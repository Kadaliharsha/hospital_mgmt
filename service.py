import re
from db_config import get_connection
import mysql.connector
from mysql.connector import IntegrityError, Error
from tabulate import tabulate
from decimal import Decimal

def auto_service_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT service_id FROM services WHERE service_id LIKE 'S%'")
    ids = [int(row[0][1:]) for row in cursor.fetchall() if row[0][1:].isdigit()]
    cursor.close()
    conn.close()
    next_num = max(ids) + 1 if ids else 1
    return f"S{next_num:02d}"

def service_usage_menu(patient_id):
    while True:
        print("\nService Usage of Patient:", patient_id)
        print("1. Add Service Usage")
        print("2. View Services Used")
        print("3. Clear Services")
        print("4. Back to Patient Management")
        choice = input("Select an option: ")
     
        if choice == '1':
            service_id = input("Enter Service ID: ")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT service_id, service_name, cost FROM services WHERE service_id=%s", (service_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if not row:
                print("Service ID not found.")
            else:
                service = Service(*row)
                ServiceUsageDB.add_service_for_patient(patient_id, service)
     
        elif choice == '2':
            rows = ServiceUsageDB.get_services_for_patient(patient_id)
            if rows:
                print(f"\nServices used by Patient ID: {patient_id}")
                headers = ["Service ID", "Service Name", "Cost"]
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                print("No services recorded.")
     
        elif choice == '3':
            ServiceUsageDB.clear_services_for_patient(patient_id)
     
        elif choice == '4':
            break
     
        else:
            print("Invalid choice. Please try again.")

class Service:
    def __init__(self, service_id, service_name, cost):
        self.service_id = service_id
        self.service_name = service_name
        self.cost = cost
        
    @staticmethod
    def service_menu():
        while True:
            print("\n=== Service Records ===")
            print("1. Register New Service")
            print("2. Display All Services")
            print("3. Modify Service")
            print("4. Remove Service")
            print("5. Return to Main Menu")
            
            choice = input("Select an option: ")

            if choice == '1':
                service_id = auto_service_id()
                print(f"Auto-generated Service ID: {service_id}")
                service_name = input("Enter Service Name: ")
                cost = float(input("Enter Cost: "))
                service = Service(service_id, service_name, cost)
                result = service.add()
                if result:
                    print("Service added successfully.")
                else:
                    print("Service was not added.")

            elif choice == '2':
                Service.view()

            elif choice == '3':
                service_id = input("Enter Service ID to update: ")
                existing = Service.get_by_id(service_id)
                if not existing:
                    print("Service not found.")
                    continue

                print("Leave input blank to keep current value.")

                name = input(f"Enter Service Name [{existing['service_name']}]: ") or existing['service_name']

                cost_input = input(f"Enter Cost [{existing['cost']}]: ")
                try:
                    cost = float(cost_input) if cost_input.strip() else float(existing['cost'])
                except ValueError:
                    print("Invalid cost input. Please try again.")
                    continue

                Service(service_id, name, cost).update()

            elif choice == '4':
                service_id = input("Enter Service ID to delete: ")
                Service.delete(service_id)

            elif choice == '5':
                break
            
            else:
                print("Invalid Choice. Please try again.")

    def add(self):
        if not self.service_name or not re.match(r'^[A-Za-z0-9\s\-_]+$', self.service_name):
            print("Invalid Service Name.")
            return False
        try:
            cost_val = float(self.cost)
            if cost_val < 0 or cost_val > 5000:
                print("Cost must be between 0 and 5000.")
                return False
            self.cost = round(cost_val, 2)
        except ValueError:
            print("Invalid Cost.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO services (service_id, service_name, cost) VALUES (%s, %s, %s)"
            cursor.execute(sql, (self.service_id, self.service_name, self.cost))
            conn.commit()
            return True
        except IntegrityError:
            print(f"Error: Duplicate Service ID '{self.service_id}'.")
            return False
        except Error as e:
            print("Database error while adding service:", e)
            return False
        except Exception as e:
            print("Error while adding service:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        if not self.service_name or not re.match(r'^[A-Za-z0-9\s\-_]+$', self.service_name):
            print("Invalid Service Name.")
            return False
        try:
            cost_val = float(self.cost)
            if cost_val < 0 or cost_val > 5000:
                print("Cost must be between 0 and 5000.")
                return False
            self.cost = round(cost_val, 2)
        except ValueError:
            print("Invalid Cost.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE services SET service_name=%s, cost=%s WHERE service_id=%s"
            cursor.execute(sql, (self.service_name, cost_val, self.service_id))
            conn.commit()
            if cursor.rowcount == 0:
                print("No updates found.")
                return False
            else:
                print("Service updated successfully.")
                return True
        except Error as e:
            print("Database error while updating service:", e)
            return False
        except Exception as e:
            print("Error while updating service:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    @staticmethod
    def get_by_id(service_id):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM services WHERE service_id = %s", (service_id,))
            return cursor.fetchone()
        except Exception as e:
            print("Error fetching service:", e)
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
        
    @staticmethod
    def delete(service_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM services WHERE service_id=%s"
            cursor.execute(sql, (service_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print("Service ID not found.")
                return False
            else:
                print("Service deleted successfully.")
                return True
        except Error as e:
            print("Database error while deleting service:", e)
            return False
        except Exception as e:
            print("Error while deleting service:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM services")
            rows = cursor.fetchall()
            headers = ["Service ID", "Service Name", "Cost"]
            formatted_rows = []
            for row in rows:
                service_id = row[0]
                service_name = row[1]
                cost = row[2]
                if isinstance(cost, Decimal):
                    cost_str = f"{float(cost):.2f}"
                else:
                    cost_str = f"{float(cost):.2f}"
                formatted_rows.append((service_id, service_name, cost_str))

            print(tabulate(formatted_rows, headers=headers, tablefmt="grid"))
        except Error as e:
            print("Database error while viewing services:", e)
        except Exception as e:
            print("Error while viewing services:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

class ServiceUsageDB:
    @staticmethod
    def add_service_for_patient(patient_id, service):
        if not re.match(r'^[A-Za-z0-9]+$', patient_id):
            print("Invalid Patient ID.")
            return
        if not re.match(r'^[A-Za-z0-9]+$', service.service_id):
            print("Invalid Service ID.")
            return
        if not re.match(r'^[A-Za-z0-9\s\-_]+$', service.service_name):
            print("Invalid Service Name.")
            return
        try:
            cost = float(service.cost)
            if cost < 0 or cost > 5000:
                print("Invalid Cost.")
                return
        except ValueError:
            print("Invalid Cost.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO temp_service_usage (patient_id, service_id, service_name, cost) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (patient_id, service.service_id, service.service_name, cost))
            conn.commit()
            print(f"Added {service.service_name} (ID: {service.service_id}, Cost: {cost}) for patient {patient_id}")
        except IntegrityError:
            print(f"Error: Duplicate service usage entry for patient {patient_id} and service {service.service_id}.")
        except Error as e:
            print("Database error while adding service usage:", e)
        except Exception as e:
            print("Error while adding service usage:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def get_services_for_patient(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "SELECT service_id, service_name, cost FROM temp_service_usage WHERE patient_id=%s"
            cursor.execute(sql, (patient_id,))
            rows = cursor.fetchall()
            return rows
        except Error as e:
            print("Database error while fetching services:", e)
            return []
        except Exception as e:
            print("Error while fetching services:", e)
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def clear_services_for_patient(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM temp_service_usage WHERE patient_id=%s"
            cursor.execute(sql, (patient_id,))
            conn.commit()
            print(f"Cleared services for patient {patient_id}")
        except Error as e:
            print("Database error while clearing services:", e)
        except Exception as e:
            print("Error while clearing services:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()




