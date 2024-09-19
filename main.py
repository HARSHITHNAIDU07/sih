import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import pywhatkit as kit

# Database connection parameters
DB_HOST = 'your_host'
DB_DATABASE = 'your_database'
DB_USER = 'your_username'
DB_PASSWORD = 'your_password'

# Alert settings
TIME_THRESHOLD = timedelta(hours=6)
WATER_READING_THRESHOLD = 50
BATTERY_THRESHOLD = 20

def fetch_sensor_data():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Get current time
            now = datetime.now()

            # Check for sensors that haven't uploaded in the last 6 hours
            cursor.execute("""
                SELECT s.id, s.name_of_officer, s.phone_number_of_officer, 
                       s.name_of_vendor, s.phone_number_of_vendor, 
                       MAX(CONCAT(s.date_of_upload, ' ', s.time_of_upload)) AS last_upload
                FROM table2 AS s
                LEFT JOIN table1 AS r ON s.id = r.id_of_sensor
                GROUP BY s.id
            """)
            sensors = cursor.fetchall()

            for sensor in sensors:
                last_upload = datetime.strptime(sensor['last_upload'], '%Y-%m-%d %H:%M:%S')
                if now - last_upload > TIME_THRESHOLD:
                    send_alert(sensor, "No data uploaded in the last 6 hours.")

                # Check for water readings and battery percentage
                cursor.execute("""
                    SELECT water_readings, battery_percentage 
                    FROM table1 
                    WHERE id_of_sensor = %s 
                    ORDER BY date_of_upload DESC, time_of_upload DESC 
                    LIMIT 1
                """, (sensor['id'],))
                last_reading = cursor.fetchone()

                if last_reading:
                    # Calculate average water reading for the sensor
                    cursor.execute("""
                        SELECT AVG(water_readings) AS avg_water_reading 
                        FROM table1 
                        WHERE id_of_sensor = %s
                    """, (sensor['id'],))
                    avg_reading = cursor.fetchone()['avg_water_reading']

                    # Check conditions
                    if abs(last_reading['water_readings'] - avg_reading) > WATER_READING_THRESHOLD:
                        send_alert(sensor, "Water reading difference exceeds 50% from average.")
                    
                    if last_reading['battery_percentage'] < BATTERY_THRESHOLD:
                        send_alert(sensor, "Battery percentage is below 20%.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def send_alert(sensor, message):
    # Create the WhatsApp message
    officer_contact = sensor['phone_number_of_officer']
    alert_message = f"Alert for Sensor ID: {sensor['id']}\n{message}\nContact Vendor: {sensor['name_of_vendor']} ({sensor['phone_number_of_vendor']})"

    # Send the message via WhatsApp
    try:
        kit.sendwhatmsg(officer_contact, alert_message, datetime.now().hour, datetime.now().minute + 2)
        print(f"Alert sent to {officer_contact}: {alert_message}")
    except Exception as e:
        print(f"Failed to send message: {e}")

if __name__ == "__main__":
    fetch_sensor_data()

