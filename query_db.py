import random
import mysql.connector
import logging
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# --------- LOAD ENVIRONMENT VARIABLES ------------
load_dotenv()

# --------- LOGGING SETUP ------------
logging.basicConfig(level=logging.ERROR, filename="errors.log",
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --------- SECURE DATABASE CREDENTIALS ------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "KphiL2022*"),
    "database": os.getenv("DB_NAME", "bus_ticketing_system")
}

# --------- DATABASE CONNECTION CONTEXT MANAGER ------------
@contextmanager
def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        yield conn, cursor
    except mysql.connector.Error as err:
        logging.error(f"Database operation failed: {err}")
        raise Exception("Database error. Please try again later.") from err
    finally:
        if conn:
            conn.close()

# --------- ID GENERATION ------------
def generate_id():
    return random.randint(11111, 99999)

# --------- INPUT VALIDATION ------------
def validate_input(input_data, data_type=str, max_length=255):
    if not isinstance(input_data, data_type):
        raise ValueError(f"Invalid input type. Expected {data_type.__name__}.")
    if isinstance(input_data, str) and len(input_data) > max_length:
        raise ValueError(f"Input exceeds maximum allowed length of {max_length}.")
    return input_data

# --------- BUS MANAGEMENT ------------
class BusManager:
    @staticmethod
    def get_bus_seats(bus_id):
        try:
            validate_input(bus_id, int)
            with db_connection() as (conn, cursor):
                query = "SELECT capacity FROM bus WHERE busid = %s"
                cursor.execute(query, (bus_id,))
                result = cursor.fetchone()
                return result["capacity"] if result else 0
        except Exception as e:
            logging.error(f"Error retrieving bus seats: {e}")
            raise Exception("Unable to retrieve bus seat details.") from e

    @staticmethod
    def update_bus_passengers(bus_id, new_passengers):
        try:
            validate_input(bus_id, int)
            validate_input(new_passengers, int)
            with db_connection() as (conn, cursor):
                query = "UPDATE bus SET capacity = capacity - %s WHERE busid = %s"
                cursor.execute(query, (new_passengers, bus_id))
                conn.commit()
        except Exception as e:
            logging.error(f"Error updating bus passengers: {e}")
            raise Exception("Unable to update bus passenger details.") from e

    @staticmethod
    def all_bus(origin, destination):
        try:
            validate_input(origin)
            validate_input(destination)
            with db_connection() as (conn, cursor):
                query = "SELECT * FROM bus WHERE origin = %s AND destination = %s"
                cursor.execute(query, (origin, destination))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching all buses: {e}")
            raise Exception("Unable to fetch bus information.") from e

    @staticmethod
    def bus_details(bus_id):
        try:
            validate_input(bus_id, int)
            with db_connection() as (conn, cursor):
                query = "SELECT * FROM bus WHERE busid = %s"
                cursor.execute(query, (bus_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching bus details: {e}")
            raise Exception("Unable to fetch bus details.") from e

# --------- USER MANAGEMENT ------------
class UserManager:
    @staticmethod
    def user_insert(details):
        try:
            for detail in details:
                validate_input(detail)
            with db_connection() as (conn, cursor):
                query = "INSERT INTO user (userid, username, phone, email, bookid) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, tuple(details))
                conn.commit()
        except Exception as e:
            logging.error(f"Error inserting user: {e}")
            raise Exception("Unable to insert user details.") from e

# --------- BOOKING MANAGEMENT ------------
class BookingManager:
    @staticmethod
    def booking_insert(details):
        try:
            for detail in details:
                validate_input(detail)
            with db_connection() as (conn, cursor):
                query = "INSERT INTO booking (booking_id, userid, busid, passengers) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, tuple(details))
                conn.commit()
        except Exception as e:
            logging.error(f"Error inserting booking: {e}")
            raise Exception("Unable to create booking.") from e

    @staticmethod
    def booking_details(booking_id):
        try:
            validate_input(booking_id, str)
            with db_connection() as (conn, cursor):
                query1 = "SELECT * FROM booking WHERE booking_id = %s"
                cursor.execute(query1, (booking_id,))
                booking_info = cursor.fetchall()

                query2 = "SELECT * FROM user WHERE userid IN (SELECT userid FROM booking WHERE booking_id = %s)"
                cursor.execute(query2, (booking_id,))
                user_info = cursor.fetchall()

                query3 = "SELECT * FROM bus WHERE busid IN (SELECT busid FROM booking WHERE booking_id = %s)"
                cursor.execute(query3, (booking_id,))
                bus_info = cursor.fetchall()

                return booking_info, user_info, bus_info
        except Exception as e:
            logging.error(f"Error fetching booking details: {e}")
            raise Exception("Unable to fetch booking details.") from e

    @staticmethod
    def delete(booking_id):
        try:
            validate_input(booking_id, int)
            with db_connection() as (conn, cursor):
                query1 = "DELETE FROM booking WHERE booking_id = %s"
                cursor.execute(query1, (booking_id,))
                conn.commit()

                # Optionally delete the associated user if no bookings exist
                query2 = "DELETE FROM user WHERE userid NOT IN (SELECT userid FROM booking)"
                cursor.execute(query2)
                conn.commit()
        except Exception as e:
            logging.error(f"Error deleting booking: {e}")
            raise Exception("Unable to delete booking.") from e

    @staticmethod
    def update_booking_user(user, booking, booking_id):
        try:
            for detail in user:
                validate_input(detail)
            validate_input(booking_id, int)
            with db_connection() as (conn, cursor):
                query = "SELECT userid FROM booking WHERE booking_id = %s"
                cursor.execute(query, (booking_id,))
                user_id = cursor.fetchone()["userid"]

                BookingManager.update_booking_passengers(booking_id, booking)

                name, phone, email = user
                update_user_query = "UPDATE user SET username = %s, phone = %s, email = %s WHERE userid = %s"
                cursor.execute(update_user_query, (name, phone, email, user_id))
                conn.commit()
        except Exception as e:
            logging.error(f"Error updating booking user: {e}")
            raise Exception("Unable to update user for the booking.") from e

    @staticmethod
    def update_booking_passengers(booking_id, passengers):
        try:
            validate_input(passengers[0], int)
            validate_input(booking_id, int)
            with db_connection() as (conn, cursor):
                query = "UPDATE booking SET passengers = %s WHERE booking_id = %s"
                cursor.execute(query, (passengers[0], booking_id))
                conn.commit()
        except Exception as e:
            logging.error(f"Error updating booking passengers: {e}")
            raise Exception("Unable to update passenger details.") from e
