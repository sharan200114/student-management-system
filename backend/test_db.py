
import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Checking database configuration...")

config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "student_management"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

print("Host:", config["host"])
print("User:", config["user"])
print("Database:", config["database"])
print("Port:", config["port"])

try:
    connection = mysql.connector.connect(**config)

    if connection.is_connected():
        print("\nSUCCESS: Database connected!")

    connection.close()

except mysql.connector.Error as error:
    print("\nDATABASE CONNECTION ERROR:")
    print(error)
