import re
from db_config import get_connection
from person import Person
import mysql.connector
from mysql.connector import IntegrityError, Error
from tabulate import tabulate


def auto_doctor_id():
    from db_config import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id FROM doctors WHERE doctor_id LIKE 'D%'")
    ids = [int(row[0][1:]) for row in cursor.fetchall() if row[0][1:].isdigit()]
    cursor.close()
    conn.close()
    next_num = max(ids) + 1 if ids else 1
    return f"D{next_num:02d}"

class Doctor(Person):
    def __init__(self, doctor_id, name, specialization, contact_no):
        super().__init__(doctor_id, name, contact_no)
        self.doctor_id = doctor_id
        self.specialization = specialization
        self.name = self._format_name(name)

    def _format_name(self, name):
        name = name.strip()
        if not name.lower().startswith("dr."):
            return "Dr. " + name
        return name

    def doctor_menu():
        while True:
            print("\n=== Doctor Records ===")
            print("1. Find Doctor Details")
            print("2. Register New Doctor")
            print("3. Display All Doctors")
            print("4. Modify Doctor Record")
            print("5. Delete Doctor Record")
            print("6. Return to Main Menu")
     
            choice = input("Choose an option: ")
     
            if choice == "1":
                name = input("Enter Doctor name to find: ")
                Doctor.search_by_name(name)
            
            elif choice == '2':
                doctor_id = auto_doctor_id()
                print(f"Doctor ID: {doctor_id}")
                name = input("Enter Name: ")
                specialization = input("Enter Specialization: ")
                contact_no = input("Enter contact number: ")
                doctor = Doctor(doctor_id, name, specialization, contact_no)
                result = doctor.add()
                if result:
                    print("Doctor added successfully.")
                else:
                    print("Doctor was not added.")
     
            elif choice == '3':
                Doctor.view()
     
            elif choice == '4':
                doctor_id = input("Enter Doctor ID to update: ")
                existing = Doctor.get_by_id(doctor_id)
                if not existing:
                    print("Doctor not found.")
                    continue

                print(f"Leave blank to keep existing value.\n")

                name = input(f"Enter Name [{existing['name']}]: ") or existing['name']
                specialization = input(f"Enter Specialization [{existing['specialization']}]: ") or existing['specialization']
                contact_no = input(f"Enter Contact No [{existing['contact_no']}]: ") or existing['contact_no']

                Doctor(doctor_id, name, specialization, contact_no).update()

            elif choice == '5':
                doctor_id = input("Enter Doctor ID to delete: ")
                Doctor.delete(doctor_id)
     
            elif choice == '6':
                break
     
            else:
                print("Invalid Choice. Please try again.")

    def add(self):
        if not self.name or not re.match(r'^[A-Za-z. ]+$', self.name):
            print("Invalid Name.")
            return False
        if len(self.name) > 50:
            print("Name is too long. Maximum 50 characters allowed.")
            return False
        if not self.specialization or not all(x.isalpha() or x.isspace() for x in self.specialization):
            print("Invalid Specialization.")
            return False
        if len(self.specialization) > 100:
            print("Specialization is too long. Maximum 100 characters allowed.")
            return False
        if not self.contact_no.isdigit() or len(self.contact_no) != 10 or self.contact_no.startswith('0'):
            print("Invalid Contact Number.Must be exactly 10 digits and not start with 0.")
            return False
        if len(set(self.contact_no)) == 1:
            print("Contact Number cannot have all digits the same.")
            return False

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM doctors WHERE contact_no = %s", (self.contact_no,))
            if cursor.fetchone():
                print(f"Contact number '{self.contact_no}' is already in use. Please provide a unique number.")
                return False
            
            sql = "INSERT INTO doctors (doctor_id, name, specialization, contact_no) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.doctor_id, self.name, self.specialization, self.contact_no))
            conn.commit()
            return True
        except mysql.connector.errors.IntegrityError as e:
            if "unique_contact_no" in str(e):
                print(f"Error: Contact number '{self.contact_no}' already exists. Please use a unique contact number.")
            elif "PRIMARY" in str(e):
                print(f"Error: Duplicate Doctor ID '{self.doctor_id}'. Please use a unique ID.")
            else:
                print("Database integrity error: ", e)
            return False
        
        except Exception as e:
            print("Error while adding doctor:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def update(self):
        self.name = self.name.strip()
        self.specialization = self.specialization.strip()
        self.contact_no = self.contact_no.strip()
        
        if not self.name or not re.match(r'^[A-Za-z. ]+$', self.name):
            print("Invalid Name.")
            return False
        if len(self.name) > 50:
            print("Name is too long. Maximum 50 characters allowed.")
            return False
        if not self.specialization or not all(x.isalpha() or x.isspace() for x in self.specialization):
            print("Invalid Specialization.")
            return False
        if len(self.specialization) > 100:
            print("Specialization is too long. Maximum 100 characters allowed.")
            return False
        if not self.contact_no.isdigit() or len(self.contact_no) != 10 or self.contact_no.startswith('0'):
            print("Invalid Contact Number.Must be exactly 10 digits and not start with 0.")
            return False
        if len(set(self.contact_no)) == 1:
            print("Contact Number cannot have all digits the same.")
            return False
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "UPDATE doctors SET name=%s, specialization=%s, contact_no=%s WHERE doctor_id=%s"
            cursor.execute(sql, (self.name, self.specialization, self.contact_no, self.doctor_id))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"No updates found.")
                return False
            else:
                print("Doctor updated successfully.")
                return True
        except Error as e:
            print("Database error while updating doctor:", e)
            return False
        except Exception as e:
            print("Error while updating doctor:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    @staticmethod
    def get_by_id(doctor_id):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM doctors WHERE doctor_id = %s", (doctor_id,))
            record = cursor.fetchone()
            return record
        except Exception as e:
            print("Error fetching doctor:", e)
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def delete(doctor_id):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM doctors WHERE doctor_id=%s"
            cursor.execute(sql, (doctor_id,))
            conn.commit()
            if cursor.rowcount == 0:
                print(f"Doctor ID '{doctor_id}' not found.")
                return False
            else:
                print("Doctor deleted successfully.")
                return True
        except Error as e:
            print("Database error while deleting doctor:", e)
            return False
        except Exception as e:
            print("Error while deleting doctor:", e)
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def view():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctors")
            rows = cursor.fetchall()
            headers = ["Doctor ID", "Name", "Specialization", "Contact Number"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            
        except Error as e:
            print("Database error while viewing doctors:", e)
        except Exception as e:
            print("Error while viewing doctors:", e)
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @staticmethod
    def search_by_name(name_substring):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            search_pattern = f"%{name_substring}%"
            cursor.execute("SELECT * FROM doctors WHERE name LIKE %s", (search_pattern,))
            rows = cursor.fetchall()
            if rows:
                headers = ["Doctor ID", "Name", "Specialization", "Contact Number"]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
            else:
                print("No doctors found matching that name.")
        except Exception as e:
            print("Error searching doctors:", e)
        finally:
            cursor.close()
            conn.close()


