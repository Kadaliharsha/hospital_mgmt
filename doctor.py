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

    def add(self):
        if not self.name or not re.match(r'^[A-Za-z. ]+$', self.name):
            print("Invalid Name.")
            return False
        if not self.specialization or not all(x.isalpha() or x.isspace() for x in self.specialization):
            print("Invalid Specialization.")
            return False
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number.")
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
        if not self.name or not re.match(r'^[A-Za-z. ]+$', self.name):
            print("Invalid Name.")
            return False
        if not self.specialization or not all(x.isalpha() or x.isspace() for x in self.specialization):
            print("Invalid Specialization.")
            return False
        if not self.contact_no.isdigit() or len(self.contact_no) < 10:
            print("Invalid Contact Number.")
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


