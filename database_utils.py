import mysql.connector

# Function to retrieve data from OpenDCIM database
def fetchData(query):
    try:
        connection = mysql.connector.connect(
            user='your_username', 
            password='your_password', 
            database='dcim', 
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except mysql.connector.Error as error:
        print(f"Database error: {error}")
        return []
