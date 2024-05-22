import mysql.connector

# Establish a connection to the MySQL server
cnx = mysql.connector.connect(user='root', password='', host='localhost')

# Create a cursor object
cursor = cnx.cursor()

# Create a new database
cursor.execute("CREATE DATABASE IF NOT EXISTS face_attendance_db")

# Use the new database
cursor.execute("USE face_attendance_db")

# Create a new table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS people_data (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        First_name VARCHAR(255),
        Last_name VARCHAR(255),
        Occupations VARCHAR(255),
        laste_time_attendance TIMESTAMP,
        image BLOB
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS account_details (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        Username VARCHAR(255),
        Password VARCHAR(255)
    )
""")



# Close the cursor and connection
cursor.close()
cnx.close()

# Print a success message
print("The 'face_attendance_db' database and 'people_data' table were successfully created.")

