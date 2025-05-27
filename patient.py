from db_config import get_connection
from datetime import datetime, date
from person import Person
from service import Service, ServiceUsageDB, service_usage_menu
import re
import mysql.connector
from mysql.connector import IntegrityError, Error
from tabulate import tabulate

def auto_patient_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(patient_id) FROM patients")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    max_id = row[0]
    if max_id is None:
        return 1001
    return int(max_id) + 1

class Patient(Person):
    def __init__(self, patient_id, name, age, gender, admission_date, contact_no):
        super().__init__(patient_id, name, contact_no)
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
        self.admission_date = admission_date

    @staticmethod
    def patient_menu():
        while True:
            print("\n=== Patient Records ===")
            print("1. Find Patient Details")
            print("2. Register New Patient")
            print("3. Display all Patients")
            print("4. Modify Patient Record")
            print("5. Delete Patient Record")
            print("6. View Patient Services")
            print("7. Check Patient Admission Days")
            print("8. Return to Main Menu")
        
            choice = input("Choose an option: ")

            if choice == '1':
                name = input("Enter part or full patient name: ")
                Patient.search_by_name(name)
                
            elif choice == '2':
                patient_id = auto_patient_id()
                print(f"Patient ID: {patient_id}")
                name = input("Enter Name: ")
                age = input("Enter Age: ")
                gender = input("Enter Gender: ")
                admission_date = input("Enter Admission Date (YYYY-MM-DD): ")
                contact_no = input("Enter Contact Number: ")
                patient = Patient(patient_id, name, age, gender, admission_date, contact_no)
                result = patient.add()
                if result:
                    print("Patient added successfully.")
                else:
                    print("Patient was not added.")
                    
            elif choice == '3':
                Patient.view()

            elif choice == '4':
                patient_id = input("Enter Patient ID to update: ")
                existing = Patient.get_by_id(patient_id)
        
                if not existing:
                    print("Patient not found.")
                else:
                    print("Leave field blank to keep existing value.\n")

                    name = input(f"Enter Name [{existing.name}]: ") or existing.name
                    age = input(f"Enter Age [{existing.age}]: ") or existing.age
                    gender = input(f"Enter Gender (M/F/Other) [{existing.gender}]: ") or existing.gender
                    admission_date = input(f"Enter Admission Date (YYYY-MM-DD) [{existing.admission_date}]: ") or existing.admission_date
                    contact_no = input(f"Enter Contact Number [{existing.contact_no}]: ") or existing.contact_no

                    Patient(patient_id, name, age, gender, admission_date, contact_no).update()

            elif choice == '5':
                patient_id = input("Enter Patient ID to delete: ")
                Patient.delete(patient_id)

            elif choice == "6":
                patient_id = input("Enter Patient ID: ")
                service_usage_menu(patient_id)
            
            elif choice == "7":
                patient_id = input("Enter Patient ID: ")
                Patient.days_admitted(patient_id)

            elif choice == '8':
                break

            else:
                print("Invalid Choice. Please try again.")
    
    # CRUD Operations
    
    def add(self):
        self.name = self.name.strip()
        self.contact_no = self.contact_no.strip()
        self.gender = self.gender.capitalize()
        
        if not self.name or not re.match(r'^(?!.*[.]{2,})(?!.*[ ]{2,})[A-Za-z. ]+$', self.name):             
            print("Invalid Name.Only letters, dots, and spaces are allowed. No multiple dots or spaces.")
            return False
        if len(self.name) > 50:
            print("Name too long. Maximum 50 characters allowed.")
            return False
        try:
            age = int(self.age)
            if age < 0 or age > 120:
                print("Invalid Age. Must be between 0 and 120.")
                return False
        except ValueError:
            print("Invalid Age. Must be a number.")
            return False
        if self.gender not in ['M', 'F', 'Other']:
            print("Invalid Gender. Choose from M, F, Other.")
            return False
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.admission_date):
            print("Invalid Admission Date. Use YYYY-MM-DD format.")
            return False
        if not self.contact_no.isdigit() or len(self.contact_no) != 10 or self.contact_no.startswith('0'):
            print("Invalid Contact Number. Must be at least 10 digits and not start with 0")
            return False
        if self.contact_no == self.contact_no[0] * len(self.contact_no):
            print("Invalid Contact Number. Cannot have all same digits.")
            return False
        if self.contact_no in ['1234567890', '0123456789']:
            print("Invalid Contact Number. Cannot be a sequential number.")
            return False
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO patients (patient_id, name, age, gender, admission_date, contact_no) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.patient_id, self.name, age, self.gender, self.admission_date, self.contact_no))
            conn.commit()
            return True
        except mysql.connector.errors.IntegrityError as e:
            if "PRIMARY" in str(e):
                print(f"Error: Duplicate Patient ID '{self.patient_id}'. Please use a unique ID.")
            else:
                print("Database integrity error: ", e)
            return False
        except Exception as e:
            print("Error while adding patient:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        self.name = self.name.strip()
        self.contact_no = self.contact_no.strip()
        self.gender = self.gender.capitalize()
        
        if not self.name or not re.match(r'^(?!.*[.]{2,})(?!.*[ ]{2,})[A-Za-z. ]+$', self.name):
            print("Invalid Name.Only letters, dots, and spaces are allowed. No multiple dots or spaces.")
            return False
        if len(self.name) > 50:
            print("Name too long. Maximum 50 characters allowed.")
            return False
        
        try:
            age = int(self.age)
            if age < 0 or age > 120:
                print("Invalid Age. Must be between 0 and 120.")
                return False
        except ValueError:
            print("Invalid Age.")
            return False
        
        if self.gender not in ['M', 'F', 'Other']:
            print("Invalid Gender. Choose from M, F, Other.")
            return False
        try:
            if isinstance(self.admission_date, date):
                self.admission_date = self.admission_date.strftime("%Y-%m-%d")
            else:
                datetime.strptime(self.admission_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid Admission Date. Use YYYY-MM-DD format.")
            return False
        if not self.contact_no.isdigit() or len(self.contact_no) != 10 or self.contact_no.startswith('0'):
            print("Invalid Contact Number. Must be at least 10 digits and not start with '0'.")
            return False
        if self.contact_no == self.contact_no[0] * len(self.contact_no):
            print("Invalid Contact Number. Cannot have all same digits.")
            return False
        if self.contact_no in ['1234567890', '0123456789']:
            print("Invalid Contact Number. Cannot be a sequential number.")
            return False
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE patients SET name=%s, age=%s, gender=%s, admission_date=%s, contact_no=%s WHERE patient_id=%s"
            cursor.execute(sql, (self.name, age, self.gender, self.admission_date, self.contact_no, self.patient_id))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"No updates found in ID '{self.patient_id}'.")
                return False
            else:
                print("Sucessfully updated the patient details.")
                return True
        except mysql.connector.errors.IntegrityError as e:
            print("Integrity error in database: ", e)
            return False
        except Exception as e:
            print("Error while updating patient:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    @staticmethod
    def get_by_id(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
            row = cursor.fetchone()
            if row:
                return Patient(**row)
            else:
                return None
        except Exception as e:
            print("Error retrieving patient record:", e)
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()


    @staticmethod
    def delete(patient_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = """DELETE FROM patients WHERE patient_id=%s"""
            cursor.execute(sql, (patient_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"No patient found with ID '{patient_id}'.")
                return False
            else:
                print("Successfully deleted the patient")
                return True
        except Error as e:
            print("Error while deleting patient:", e)
            return False
        except Exception as e:
            print("Error while deleting patient:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            headers = ["Patient ID", "Name", "Age", "Gender", "Admission Date", "Contact Number"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Error as e:
            print("Error while viewing patients:", e)
        except Exception as e:
            print("Error while viewing patients:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def days_admitted(patient_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT admission_date FROM patients WHERE patient_id=%s", (patient_id,))
            row = cursor.fetchone()
            if row and row[0]:
                admission_date = row[0]
                today = date.today()
                days = (today - admission_date).days
                print(f"Patient {patient_id} has been admitted for {days} days.")
                return days
            else:
                print("Patient not found or admission date missing.")
                return None
        except Exception as e:
            print("Error calculating days admitted:", e)
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def search_by_name(name_substring):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            search_pattern = f"%{name_substring}%"
            cursor.execute("SELECT * FROM patients WHERE name LIKE %s", (search_pattern,))
            rows = cursor.fetchall()
            if rows:
                headers = ["Patient ID", "Name", "Age", "Gender", "Admission Date", "Contact Number"]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
            else:
                print("No patients found")
        except Exception as e:
            print("Error searching patients:", e)
        finally:
            cursor.close()
            conn.close()

