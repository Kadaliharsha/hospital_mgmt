# Hospital Patient Record & Billing System

A real-world Python-based solution for managing hospital appointments and billing, designed for use by hospital front desks, administrators, and medical office staff. This system integrates with a MySQL database and streamlines the process of scheduling appointments and generating patient bills.

---

## Table of Contents

- [Folder Structure](#folder-structure)
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Typical Use Cases](#typical-use-cases)
- [Setup Instructions](#setup-instructions)
- [Database Requirements](#database-requirements)
- [Getting Started](#getting-started)
- [Export & Reporting](#export--reporting)
- [Support & Contribution](#support--contribution)

---

## Folder Structure

```
hospital_mgmt/
├── db_config.py            # DB connection logic
├── patient.py              # Patient class
├── doctor.py               # Doctor class
├── service.py              # Services logic
├── billing.py              # Billing logic
├── appointment.py          # Appointment logic
├── person.py               # Base Person class
├── hospital_main.py        # Main menu & CLI
├── requirements.txt        # List of required libraries
├── output/
│   └── invoices/
│       └── bill_1001.txt   # Sample invoice
└── README.md               # Project documentation
```
---


## Project Overview

This system is built to address the everyday needs of hospitals and clinics:
- **Appointment Scheduling**: Book, update, view, and cancel patient appointments with doctors.
- **Billing**: Generate, update, and manage patient bills, including itemized invoices for consultations and hospital services.
- **Data Export**: Export appointment summaries for administrative and reporting purposes.

---

## Key Features

- **Unique ID Generation**: Automatically generates unique IDs for appointments and bills, reducing manual errors.
- **Validation & Error Handling**: Ensures all data (dates, IDs, charges) is validated and user-friendly error messages are provided.
- **Comprehensive CRUD Operations**: Add, update, view, and delete both appointments and bills.
- **Invoice Generation**: Produces detailed invoices with patient, doctor, and service details.
- **CSV Export**: Export appointment summaries to CSV for reporting or backup.
- **Service Tracking**: Tracks all services used by patients and ensures accurate billing.
- **Secure Database Interaction**: Uses parameterized queries and robust error handling to maintain data integrity.

---

## How It Works

1. **Appointment Management**  
   - Staff can add new appointments by entering patient and doctor IDs, date, diagnosis, and consulting charges.
   - Appointments can be updated, viewed, filtered by date range, or deleted (cancelled).

2. **Billing Management**  
   - When a patient is ready to be billed, all services used are fetched and included in the bill.
   - Bills are generated with a unique bill ID, and invoices can be printed or saved.
   - After billing, temporary service usage records are cleared to prevent duplicate billing.

3. **Reporting**  
   - Administrators can export appointment summaries to CSV for analysis or compliance.

---

## Typical Use Cases

- **Front Desk Operations**: Quickly schedule or update appointments for walk-in or returning patients.
- **Billing Desk**: Generate bills and print invoices for patients at discharge or after outpatient procedures.
- **Hospital Administration**: Export appointment data for monthly or quarterly reporting.
- **Doctors & Nurses**: View patient appointment histories and service usage.

---

## Setup Instructions

### Prerequisites

- Python 3.7+
- MySQL Server or MySQL
- Required Python packages:

  ```bash
  pip install -r requirements.txt
  ```

---
## Database Requirements

- **MySQL** database with the following tables:
  - `appointments`
  - `patients`
  - `doctors`
  - `billing`
  - `services`
  - `billed_services`
  - `temp_service_usage`
- A `db_config.py` file is required to provide the `get_connection()` function for secure database access.

---

## Getting Started

1. **Clone the Repository**
   ```bash
   + git clone https://github.com/your-username/hospital-mgmt.git
   + cd hospital-mgmt
   ```

2. **Set Up Database**
   - Ensure your MySQL server is running.
   - Create the required tables as per the schema.

3. **Configure Database Connection**
   - Edit `db_config.py` to include your MySQL credentials and connection logic.

4. **Run Appointment or Billing Operations**
   - Use the `Appointment` and `Bill` classes in your Python scripts or integrate them into your hospital management workflow.

---

## Export & Reporting

- **Export Appointments**: Use the export function to save appointment summaries as CSV files for record-keeping or further analysis.
- **Invoice Generation**: Generate and print invoices for patients, including all services and consultation charges.

---

## Support & Contribution

- **Issues**: If you encounter bugs or need help, please open an issue in this repository.
- **Contributions**: Pull requests are welcome! Please fork the repository and submit your changes for review.

---

