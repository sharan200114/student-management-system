
import os
import mysql.connector
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

load_dotenv()

# Initialize password hashing
bcrypt = Bcrypt()

# Admin credentials
full_name = "StudentHub Administrator"
email = "admin@gmail.com"
password = "Admin@12345"

# Generate secure password hash
password_hash = bcrypt.generate_password_hash(
    password
).decode("utf-8")

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO admins (full_name, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (full_name, email, password_hash)
    )

    connection.commit()

    print("Admin account created successfully!")
    print("Email:", email)
    print("Password:", password)

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
