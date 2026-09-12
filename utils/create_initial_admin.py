import bcrypt
import os 
def create_admin(conn,cursor):
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"),salt)
    cursor.execute("""
    INSERT INTO users (name,email,password,role)
    VALUES (%s,%s,%s,%s)""", 
    ['admin', ADMIN_EMAIL, encrypted_password.decode("utf-8"), "admin"])