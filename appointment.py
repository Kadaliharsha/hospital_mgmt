import re
from db_config import get_connection
import mysql.connector
from mysql.connector import IntegrityError, Error
import csv
from tabulate import tabulate


def auto_appt_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT appt_id FROM appointments WHERE appt_id LIKE 'A%'")
    ids = [int(row[0][1:]) for row in cursor.fetchall() if row[0][1:].isdigit()]
    cursor.close()
    conn.close()
    next_num = max(ids) + 1 if ids else 1
    return f"A{next_num:03d}"

class Appointment:
    def __init__(self, appt_id, patient_id, doctor_id, date, diagnosis, consulting_charge):
        self.appt_id = appt_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.diagnosis = diagnosis
        self.consulting_charge = consulting_charge

    def appointment_menu():
        while True:
            print("\n=== Appointment Records ===")
            print("1. Schedule New Appointment")
            print("2. View All Appointments")
            print("3. Modify Appointment Details")
            print("4. Cancel Appointment")
            print("5. Search/Filter Appointments")
            print("6. Calculate Days Between Patient Appointments")
            print("7. Return to Main Menu")
            
            choice = input("Select an option: ")

            if choice == '1':
                appt_id = auto_appt_id()
                print(f"Registered Appointment ID: {appt_id}")
                patient_id = input("Enter Patient ID: ")
                doctor_id = input("Enter Doctor ID: ")
                date = input("Enter Appointment Date (YYYY-MM-DD): ")
                diagnosis = input("Enter Diagnosis: ")
                consulting_charge = input("Enter Consulting Charge: ")
                appointment = Appointment(appt_id, patient_id, doctor_id, date, diagnosis, consulting_charge)
                result = appointment.add()
                if result:
                    print("Appointment added successfully.")
                else:
                    print("Appointment was not added.")
                    
            elif choice == '2':
                Appointment.view()

            elif choice == '3':
                appt_id = input("Enter Appointment ID to update: ")
                existing = Appointment.get_by_id(appt_id)
                if not existing:
                    print("Appointment not found.")
                    continue

                print("Leave input blank to keep current value.")

                patient_id = input(f"Enter Patient ID [{existing['patient_id']}]: ") or existing['patient_id']
                doctor_id = input(f"Enter Doctor ID [{existing['doctor_id']}]: ") or existing['doctor_id']
                date = input(f"Enter Appointment Date (YYYY-MM-DD) [{existing['date']}]: ") or str(existing['date'])
                diagnosis = input(f"Enter Diagnosis [{existing['diagnosis']}]: ") or existing['diagnosis']
                consulting_charge = input(f"Enter Consulting Charge [{existing['consulting_charge']}]: ") or existing['consulting_charge']

                Appointment(appt_id, patient_id, doctor_id, date, diagnosis, consulting_charge).update()

            elif choice == '4':
                appt_id = input("Enter Appointment ID to delete: ")
                Appointment.delete(appt_id)

            elif choice == '5':
                Appointment.filter_appointments()

            elif choice == '6':
                patient_id = input("Enter Patient ID: ")
                Appointment.days_between_appointments(patient_id)
                
            elif choice == "7":
                break
            else:
                print("Invalid Choice. Please try again.")

    def add(self):
        if not self.patient_id or not str(self.patient_id).isdigit():
            print("Invalid Patient ID.")
            return False
        if not self.doctor_id or not isinstance(self.doctor_id, str):
            print("Invalid Doctor ID.")
            return False
        if not self.date or not re.match(r'^\d{4}-\d{2}-\d{2}$', self.date):
            print("Invalid Date. Use YYYY-MM-DD format.")
            return False
        if not self.diagnosis or not isinstance(self.diagnosis, str):
            print("Invalid Diagnosis.")
            return False
        try:
            charge = float(self.consulting_charge)
            if charge < 0:
                print("Consulting charge cannot be negative.")
                return False
        except ValueError:
            print("Invalid consulting charge. Enter a valid number.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO appointments (appt_id, patient_id, doctor_id, date, diagnosis, consulting_charge) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.appt_id, self.patient_id, self.doctor_id, self.date, self.diagnosis, charge))
            conn.commit()
            return True
        except mysql.connector.errors.IntegrityError as e:
            if "PRIMARY" in str(e):
                print(f"Error: Duplicate Appointment ID '{self.appt_id}'.")
            else:
                print("Database integrity error: ", e)
            return False
        except Exception as e:
            print("Error while adding appointment:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        if not self.patient_id or not str(self.patient_id).isdigit():
            print("Invalid Patient ID.")
            return False
        if not self.doctor_id or not isinstance(self.doctor_id, str):
            print("Invalid Doctor ID.")
            return False
        if not self.date or not re.match(r'^\d{4}-\d{2}-\d{2}$', self.date):
            print("Invalid Date. Use YYYY-MM-DD format.")
            return False
        if not self.diagnosis or not isinstance(self.diagnosis, str):
            print("Invalid Diagnosis.")
            return False
        try:
            charge = float(self.consulting_charge)
            if charge < 0 or charge > 10000:
                print("Consulting charge must be between 0 and 10000.")
                return False
        except ValueError:
            print("Invalid Consulting Charge. Enter a valid number.")
            return False
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE appointments SET patient_id=%s, doctor_id=%s, date=%s, diagnosis=%s, consulting_charge=%s WHERE appt_id=%s"
            cursor.execute(sql, (self.patient_id, self.doctor_id, self.date, self.diagnosis, charge, self.appt_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("No updates found.")
                return False
            else:
                print("Appointment updated successfully.")
                return True
        except Error as e:
            print("Database error while updating appointment:", e)
            return False
        except Exception as e:
            print("Error while updating appointment:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    @staticmethod
    def get_by_id(appt_id):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM appointments WHERE appt_id = %s", (appt_id,))
            return cursor.fetchone()
        except Exception as e:
            print("Error fetching appointment:", e)
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(appt_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM appointments WHERE appt_id=%s"
            cursor.execute(sql, (appt_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Appointment ID not found.")
                return False
            else:
                print("Appointment cancelled successfully.")
                return True
        except Error as e:
            print("Database error while deleting appointment:", e)
            return False
        except Exception as e:
            print("Error while deleting appointment:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appointments")
            rows = cursor.fetchall()
            headers = ["Appointment ID", "Patient ID", "Doctor ID", "Date", "Diagnosis", "Consulting Charge"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Error as e:
            print("Database error while viewing appointments:", e)
        except Exception as e:
            print("Error while viewing appointments:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def filter_appointments():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            start_date = input("Enter start date(YYYY-MM-DD): ")
            end_date = input("Enter end date(YYYY-MM-DD):")
            cursor.execute("SELECT * FROM appointments WHERE date BETWEEN %s and %s", (start_date, end_date))
            rows = cursor.fetchall()
            if rows:
                headers = ["Appointment ID", "Patient ID", "Doctor ID", "Date", "Diagnosis", "Consulting Charge"]
                print("\nAppointments from", start_date, "to", end_date)
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                print("No appointments found in the given date range.")
        except Error as e:
            print("Database error while fetching appointments for given dates:", e)
        except Exception as e:
            print("Error while fetching appointments for given dates:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    @staticmethod
    def days_between_appointments(patient_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT date FROM appointments WHERE patient_id=%s ORDER BY date", (patient_id,))
            rows = cursor.fetchall()
            dates = [row[0] for row in rows if row[0]]
            if len(dates) < 2:
                print("Not enough appointments to calculate days between.")
                return []
            days_between = []
            for i in range(1, len(dates)):
                days = (dates[i] - dates[i-1]).days
                days_between.append(days)
            for idx, days in enumerate(days_between, 1):
                print(f"Days between appointment {idx} and {idx+1}: {days}")
            return days_between
        except Exception as e:
            print("Error calculating days between appointments:", e)
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def export_appointment_summary_to_csv(filename="appointment_summary.csv"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT appt_id, patient_id, doctor_id, date, diagnosis, consulting_charge FROM appointments")
            rows = cursor.fetchall()
            if not rows:
                print("No appointment records to export.")
                return
            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Appointment ID", "Patient ID", "Doctor ID", "Date", "Diagnosis", "Consulting Charge"])
                for row in rows:
                    writer.writerow(row)
            print(f"Appointment summary exported to {filename}")
        except Exception as e:
            print("Error exporting appointment summary:", e)
        finally:
            cursor.close()
            conn.close()



