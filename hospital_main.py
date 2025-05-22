from db_config import get_connection
from patient import Patient, auto_patient_id
from doctor import Doctor, auto_doctor_id
from service import Service, service_usage_menu, auto_service_id
from appointment import Appointment, auto_appt_id
from billing import Bill, calculate_total_charge, auto_bill_id
from tabulate import tabulate

# --- Patients ---
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

# --- Doctors ---
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

# --- Services ---
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
            cost = input("Enter Cost: ")
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
          
# --- Appointments ---
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

# --- Billing ---
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

# -- Export --
def export_menu():
    while True:
        print("\n=== Export ===")
        print("1. Export Billing Summary")
        print("2. Export Appointment Summary")
        print("3. Return to Main Menu")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            filename = input("Enter filename for billing summary (default: billing_summary.csv): ").strip() or "billing_summary.csv"
            if not filename.lower().endswith(".csv"):
                filename += ".csv"
            Bill.export_billing_summary_to_csv(filename)
            
        elif choice == '2':
            filename = input("Enter filename for appointment summary (default: appointment_summary.csv): ").strip() or "appointment_summary.csv"
            if not filename.lower().endswith(".csv"):
                filename += ".csv"
            Appointment.export_appointment_summary_to_csv(filename)
            
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

# --- Main CLI ---
def main_menu():
    while True:
        print("\n=== Hospital Management System ===")
        print("1. Patient Records")
        print("2. Doctor Records")
        print("3. Service Records")
        print("4. Appointment Records")
        print("5. Billing Records")
        print("6. Export Records")
        print("7. Exit System")
        
        choice = input("Select an option: ")

        if choice == '1':
            patient_menu()
        elif choice == '2':
            doctor_menu()
        elif choice == '3':
            service_menu()
        elif choice == '4':
            appointment_menu()
        elif choice == '5':
            billing_menu()
        elif choice == '6':
            export_menu()
        elif choice == '7':
            print("Exiting Hospital Management CLI. Bye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
