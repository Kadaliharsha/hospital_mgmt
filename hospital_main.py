from db_config import get_connection
from patient import Patient
from doctor import Doctor
from service import Service, ServiceUsageDB
from appointment import Appointment
from billing import Bill
from tabulate import tabulate

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
            Patient.patient_menu()              #calls from patient.py
        elif choice == '2':
            Doctor.doctor_menu()                #calls from doctor.py
        elif choice == '3':
            Service.service_menu()              #calls from service.py
        elif choice == '4':
            Appointment.appointment_menu()      #calls from appointment.py
        elif choice == '5':
            Bill.billing_menu()                 #calls from billing.py
        elif choice == '6':
            export_menu()                       # function call of the export
        elif choice == '7':
            print("Exiting Hospital Management CLI. Bye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
