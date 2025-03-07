import csv
import os
import mysql.connector

def load_csv_to_mysql(csv_filename, db_config):
    """Loads data from a CSV file into a MySQL table."""

    try:
        downloads_path = os.path.expanduser("~/Downloads")
        csv_filepath = os.path.join(downloads_path, csv_filename)

        if not os.path.exists(csv_filepath):
            print(f"Error: CSV file '{csv_filepath}' not found.")
            return

        mydb = mysql.connector.connect(**db_config)
        mycursor = mydb.cursor()

        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)

            for row in csvreader:
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['%s'] * len(row))
                values = tuple(row.values())

                sql = f"INSERT INTO orders ({columns}) VALUES ({placeholders})"
                mycursor.execute(sql, values)

        mydb.commit()
        print(f"Data from '{csv_filename}' loaded into 'orders' table.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found in Downloads directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection closed.")

db_config = {
    "host": "your_host",
    "user": "your_user",
    "password": "your_password",
    "database": "your_database",
}

csv_file = "orders.csv"

load_csv_to_mysql(csv_file, db_config)