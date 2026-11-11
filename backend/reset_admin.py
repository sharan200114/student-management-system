
import os
import mysql.connector
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

load_dotenv()
bcrypt = Bcrypt()

email = "admin@gmail.com"
new_password = "Admin@12345"

password_hash = bcrypt.generate_password_hash(
    new_password
).decode("utf-8")

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
    UPDATE admins
    SET password_hash = %s
    WHERE email = %s
    """,
    (password_hash, email)
)

connection.commit()

if cursor.rowcount > 0:
    print("Admin password reset successfully!")
else:
    print("Admin account not found.")

cursor.close()
connection.close()
