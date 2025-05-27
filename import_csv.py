from db_config import get_connection
import pandas as pd
import mysql.connector
import os
print("Current working directory:", os.getcwd())

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root@39',
    database='hospitalmanagementsystem'
)
cursor = conn.cursor()

def import_csv_to_table(csv_file, table_name, columns, date_columns=None):
    try:
        df = pd.read_csv(csv_file)

        df = df.where(pd.notnull(df), None)

        if date_columns:
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

        placeholders = ','.join(['%s'] * len(columns))
        cols = ','.join(columns)
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

        for index, row in df.iterrows():
            try:
                cursor.execute(sql, tuple(row[col] for col in columns))
            except Exception as row_err:
                print(f"Row {index + 1} skipped due to error: {row_err}")
                print("Row data:", row.to_dict())

        conn.commit()
        print(f"✅ Imported {len(df)} rows into '{table_name}' from '{os.path.basename(csv_file)}'")

    except Exception as e:
        print(f"❌ Error importing '{csv_file}' into table '{table_name}': {e}")


import_csv_to_table(
    csv_file=r'C:/Users/kadali.harshavardhan/Desktop/hospital_mgmt/CSV reports/patients_dataset.csv',
    table_name='patients',
    columns=['patient_id', 'name', 'age', 'gender', 'admission_date', 'contact_no'],
    date_columns=['admission_date']
)

import_csv_to_table(
    csv_file=r'C:/Users/kadali.harshavardhan/Desktop/hospital_mgmt/CSV reports/doctors_dataset.csv',
    table_name='doctors',
    columns=['doctor_id', 'name', 'specialization', 'contact_no']
)

import_csv_to_table(
    csv_file=r'C:/Users/kadali.harshavardhan/Desktop/hospital_mgmt/CSV reports/services_dataset.csv',
    table_name='services',
    columns=['service_id', 'service_name', 'cost']
)

import_csv_to_table(
    csv_file=r'C:/Users/kadali.harshavardhan/Desktop/hospital_mgmt/CSV reports/appointments_dataset.csv',
    table_name='appointments',
    columns=['appt_id', 'patient_id', 'doctor_id', 'date', 'diagnosis', 'consulting_charge'],
    date_columns=['date']
)

import_csv_to_table(
    csv_file=r'C:/Users/kadali.harshavardhan/Desktop/hospital_mgmt/CSV reports/billing_dataset.csv',
    table_name='billing',
    columns=['bill_id', 'patient_id', 'total_amount', 'billing_date'],
    date_columns=['billing_date']
)

# Close connection
cursor.close()
conn.close()
print("✅ All CSVs imported successfully and DB connection closed.")
