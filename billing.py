from db_config import get_connection
from service import ServiceUsageDB
import re
import datetime
import csv
import os
from tabulate import tabulate

import mysql.connector
from mysql.connector import IntegrityError, Error

def auto_bill_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bill_id FROM billing WHERE bill_id REGEXP '^B[0-9]+$'")
    bill_ids = cursor.fetchall()
    cursor.close()
    conn.close()
    max_num = 0
    for (bill_id,) in bill_ids:
        try:
            num = int(bill_id[1:])
            if num > max_num:
                max_num = num
        except:
            continue
    return f'B{max_num+1:03d}'

class Bill:
    def __init__(self, bill_id, patient_id, billing_date=None):
        self.bill_id = bill_id
        self.patient_id = patient_id
        self.billing_date = billing_date or datetime.date.today().strftime("%Y-%m-%d")

    def billing_menu():
        while True:
            print("\n=== Billing Records ===")
            print("1. Create New Bill")
            print("2. View All Billing Records")
            print("3. Modify Bill Details")
            print("4. Delete Bill Entry")
            print("5. Calculate Total Charges")
            print("6. Print/Generate Invoice")
            print("7. Return to Main Menu")
            
            choice = input("Select an option: ")
     
            if choice == "1":
                bill_id = auto_bill_id()
                print(f"Bill ID: {bill_id}")
                patient_id = input("Enter Patient ID: ")
                billing_date = input("Enter Billing Date (YYYY-MM-DD) [leave blank for today]: ")
                if not billing_date.strip():
                    bill = Bill(bill_id, patient_id)
                else:
                    bill = Bill(bill_id, patient_id, billing_date)
                result = bill.add()
                if result:
                    bill.generate_invoice()
                else:
                    print("Bill and Invoice not generated.")
     
            elif choice == "2":
                Bill.view()
     
            elif choice == "3":
                bill_id = input("Enter Bill ID to update: ")
                existing = Bill.get_by_id(bill_id)
                if not existing:
                    print("Bill not found.")
                    return

                print("Leave fields blank to keep current values.")

                patient_id = input(f"Enter Patient ID [{existing['patient_id']}]: ") or existing['patient_id']
                billing_date = input(f"Enter Billing Date (YYYY-MM-DD) [{existing['billing_date']}]: ") or str(existing['billing_date'])

                bill = Bill(bill_id, patient_id, billing_date)
                bill.update()
     
            elif choice == "4":
                bill_id = input("Enter Bill ID to delete: ")
                Bill.delete(bill_id)
     
            elif choice == "5":
                patient_id = input("Enter Patient ID to compute total billing: ")
                total = calculate_total_charge(patient_id)
                if total is not None:
                    print(f"Total bill for patient {patient_id}: {total}")
     
            elif choice == "6":
                print("Generate Invoice Using:")
                print("1. By Bill ID")
                print("2. By Patient ID")
                invoice_choice = input("Select an option: ")
                if invoice_choice == "1":
                    bill_id = input("Enter Bill ID to generate invoice: ")
                    from db_config import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT patient_id, billing_date FROM billing WHERE bill_id=%s", (bill_id,))
                    row = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    if row:
                        patient_id, billing_date = row
                        bill = Bill(bill_id, patient_id, billing_date)
                        bill.generate_invoice()
                    else:
                        print("Bill not found.")
                        
                elif invoice_choice == "2":
                    patient_id = input("Enter Patient ID to generate invoice: ")
                    from db_config import get_connection
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT bill_id, billing_date FROM billing WHERE patient_id=%s", (patient_id,))
                    bills = cursor.fetchall()
                    if not bills:
                        print("No bills found for this patient.")
                    elif len(bills) == 1:
                        bill_id = bills[0]['bill_id']
                        billing_date = bills[0]['billing_date']
                        bill = Bill(bill_id, patient_id, billing_date)
                        bill.generate_invoice()
                    else:
                        print("Multiple bills found for this patient:")
                        for idx, b in enumerate(bills):
                            print(f"{idx+1}. Bill ID: {b['bill_id']}, Date: {b['billing_date']}")
                        user_input = input("Select bill number to generate invoice: ").strip()
                        if user_input.isdigit():
                            selection = int(user_input) - 1
                            if 0 <= selection < len(bills):
                                selected_bill = bills[selection]
                                bill = Bill(selected_bill['bill_id'], patient_id, selected_bill['billing_date'])
                                bill.generate_invoice()
                                return
                            else:
                                print("Invalid selection.")
                        else:
                            print("Invalid input. Please enter a number.")
                    cursor.close()
                    conn.close()
                else:
                    print("Invalid option for invoice generation.")
     
            elif choice == "7":
                break
     
            else:
                print("Invalid Choice. Please try again.")

    def add(self):
        import datetime
        if not self.patient_id:
            print("Patient ID is required.")
            return False
        try:
            datetime.datetime.strptime(self.billing_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Billing Date. Use YYYY-MM-DD format.")
            return False

        services = ServiceUsageDB.get_services_for_patient(self.patient_id)
        print("DEBUG: Services fetched from temp_service_usage:", services)
        if not services:
            print("No services to bill for this patient.")
            return False


        total_amount = sum(float(s[2]) for s in services)  

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM patients WHERE patient_id=%s", (self.patient_id,))
            if cursor.fetchone() is None:
                print("Patient ID does not exist.")
                return False

            sql = "INSERT INTO billing (bill_id, patient_id, total_amount, billing_date) VALUES (%s, %s, %s, %s)"
            try:
                cursor.execute(sql, (self.bill_id, self.patient_id, total_amount, self.billing_date))
            except IntegrityError:
                print(f"Error: Duplicate Bill ID '{self.bill_id}'. Please use a unique ID.")
                return False

            for s in services:
                try:
                    cursor.execute(
                        "INSERT INTO billed_services (bill_id, patient_id, service_id, service_name, cost) VALUES (%s, %s, %s, %s, %s)",
                        (self.bill_id, self.patient_id, s[0], s[1], s[2])
                    )
                except IntegrityError:
                    print(f"Error: Duplicate service entry for bill {self.bill_id} and service {s[0]}. Skipping.")
            conn.commit()
            print(f"Bill added successfully. Total amount: {total_amount}")
            print("Billed services recorded.")
            try:
                ServiceUsageDB.clear_services_for_patient(self.patient_id)
            except Exception as e:
                print("Error clearing temp service usage:", e)

            return True
        except Error as e:
            print("Database error while adding bill:", e)
            return False
        except Exception as e:
            print("Error while adding bill:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        try:
            ServiceUsageDB.clear_services_for_patient(self.patient_id)
        except Exception as e:
            print("Error clearing temp service usage:", e)

    def update(self):
        import datetime
        if not self.bill_id:
            print("Bill ID is required.")
            return False
        if not self.patient_id:
            print("Patient ID is required.")
            return False
        try:
            datetime.datetime.strptime(self.billing_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Billing Date. Use YYYY-MM-DD format.")
            return False

        services = ServiceUsageDB.get_services_for_patient(self.patient_id)
        if not services:
            print("No services to bill for this patient.")
            return False

        total_amount = sum(float(s[2]) for s in services)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM patients WHERE patient_id=%s", (self.patient_id,))
            if cursor.fetchone() is None:
                print("Patient ID does not exist.")
                return False

            sql = "UPDATE billing SET patient_id=%s, total_amount=%s, billing_date=%s WHERE bill_id=%s"
            cursor.execute(sql, (self.patient_id, total_amount, self.billing_date, self.bill_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("No updates found.")
                return False
            else:
                print("Bill updated successfully. Total amount:", total_amount)
                return True
        except Error as e:
            print("Database error while updating bill:", e)
            return False
        except Exception as e:
            print("Error while updating bill:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        try:
            ServiceUsageDB.clear_services_for_patient(self.patient_id)
        except Exception as e:
            print("Error clearing temp service usage:", e)
        
    @staticmethod
    def get_by_id(bill_id):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM billing WHERE bill_id=%s", (bill_id,))
            return cursor.fetchone()
        except Error as e:
            print("Database error:", e)
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(bill_id):
        if not bill_id:
            print("Bill ID is required.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM billing WHERE bill_id=%s"
            cursor.execute(sql, (bill_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Bill ID not found.")
                return False
            else:
                print("Bill deleted successfully.")
                return True
        except Error as e:
            print("Database error while deleting bill:", e)
            return False
        except Exception as e:
            print("Error while deleting bill:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()


    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM billing")
            rows = cursor.fetchall()
            headers = ["Bill ID", "Patient ID", "Total Amount", "Billing Date"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Error as e:
            print("Database error while viewing bills:", e)
        except Exception as e:
            print("Error while viewing bills:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()


    def generate_invoice(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (self.patient_id,))
            patient = cursor.fetchone()

            cursor.execute("""
                SELECT a.date, d.name AS doctor_name, d.specialization, a.consulting_charge
                FROM appointments a
                JOIN doctors d ON a.doctor_id = d.doctor_id
                WHERE a.patient_id = %s
                ORDER BY a.date DESC LIMIT 1
            """, (self.patient_id,))
            appt = cursor.fetchone()

            cursor.execute("""
                SELECT s.service_name, bs.cost
                FROM billed_services bs
                JOIN services s ON bs.service_id = s.service_id
                WHERE bs.bill_id = %s
            """, (self.bill_id,))
            services = cursor.fetchall()

            lines = []
            lines.append("=" * 70)
            lines.append(" " * 25 + "HOSPITAL INVOICE")
            lines.append("=" * 70)
            lines.append(f"Bill No.       : {self.bill_id:<15}   Date: {self.billing_date}")
            lines.append(f"Patient ID     : {self.patient_id:<15}   Name: {patient['name'] if patient else 'N/A'}")
            lines.append("-" * 70)

            if appt:
                lines.append(f"Doctor         : {appt['doctor_name']}")
                lines.append(f"Consultation Charge : ₹{float(appt['consulting_charge']):,.2f}")
            else:
                lines.append("Doctor         : N/A")
                lines.append("Consultation Charge : ₹0.00")

            lines.append("-" * 70)
            lines.append(f"{'Service Name':<50}{'Amount (₹)':>18}")
            lines.append("-" * 70)

            service_total = 0
            if services:
                for s in services:
                    lines.append(f"{s['service_name'][:50]:<50}{float(s['cost']):>18,.2f}")
                    service_total += float(s['cost'])
            else:
                lines.append("No services billed.".ljust(70))

            lines.append("-" * 70)
            consulting_charge = float(appt['consulting_charge']) if appt else 0.0
            lines.append(f"{'Service Total':<50}{'₹' + format(service_total, ',.2f'):>18}")
            lines.append(f"{'Consultation Charge':<50}{'₹' + format(consulting_charge, ',.2f'):>18}")
            lines.append("-" * 70)
            total = service_total + consulting_charge
            lines.append(f"{'TOTAL AMOUNT DUE':<50}{'₹' + format(total, ',.2f'):>18}")
            lines.append("=" * 70)
            lines.append("Payment should be done within 5 days. For queries, call (234)-145-9081")
            lines.append("=" * 70)
            lines.append(" " * 20 + "Thank you for choosing our Hospital!")
            lines.append("=" * 70)

            
            output_dir = os.path.join("output", "invoices")
            os.makedirs(output_dir, exist_ok=True)

            filename = os.path.join(output_dir, f"bill_{self.patient_id}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write('\n'.join(lines))
            print(f"Invoice generated and saved as {filename}")

        except Error as e:
            print("Database error while generating invoice:", e)
        except Exception as e:
            print("Error while generating invoice:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def export_billing_summary_to_csv(filename="billing_summary.csv"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT bill_id, patient_id, total_amount, billing_date FROM billing")
            rows = cursor.fetchall()
            if not rows:
                print("No billing records to export.")
                return
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Bill ID", "Patient ID", "Total Amount", "Billing Date"])
                for row in rows:
                    writer.writerow(row)
            print(f"Billing summary exported to {filename}")
        except Exception as e:
            print("Error exporting billing summary:", e)
        finally:
            cursor.close()
            conn.close()

def calculate_total_charge(patient_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM temp_service_usage WHERE patient_id=%s",
            (patient_id,)
        )
        service_total = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COALESCE(SUM(consulting_charge), 0) FROM appointments WHERE patient_id=%s",
            (patient_id,)
        )
        consulting_total = cursor.fetchone()[0] or 0

        total_billing = service_total + consulting_total
        print(f"Service Total: {service_total}")
        print(f"Consulting Total: {consulting_total}")
        print(f"Total Billing: {total_billing}")
        return total_billing
    except Error as e:
        print("Database error while computing total billing:", e)
        return None
    except Exception as e:
        print("Error while computing total billing:", e)
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
 
