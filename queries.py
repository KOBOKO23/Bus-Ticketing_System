from flask import Flask
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

def create_connection():
    """Create a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username", 
            password="KphiL2022*",
            database="bus_ticketing_system" 
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    try:
        # Establish connection
        connection = create_connection()
        if connection is None:
            return "Failed to connect to the database."
        
        cursor = connection.cursor()

        # Create the tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            userid VARCHAR(20) PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(50) NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bus (
            busid VARCHAR(20) PRIMARY KEY,
            origin VARCHAR(50) NOT NULL,
            destination VARCHAR(50) NOT NULL,
            cost INT NOT NULL,
            rating DECIMAL(3, 2) NOT NULL,
            departure DATETIME NOT NULL,
            arrival DATETIME NOT NULL,
            capacity INT NOT NULL DEFAULT 60,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            booking_id VARCHAR(20) PRIMARY KEY,
            userid VARCHAR(20) NOT NULL,
            busid VARCHAR(20) NOT NULL,
            passengers INT NOT NULL,
            date_ DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (busid) REFERENCES bus(busid) ON DELETE CASCADE
        );
        """)
        
        # Insert sample data
        cursor.execute("""
        INSERT INTO bus (busid, origin, destination, cost, rating, departure, arrival) 
        VALUES
        ('12345', 'Nairobi', 'Migori', 1299, 4.3, '2024-12-31 12:00:00', '2025-01-01 08:00:00'),
        ('12346', 'Nairobi', 'Kitale', 1999, 3.3, '2025-01-02 12:00:00', '2025-01-03 08:00:00'),
        ('12348', 'Nairobi', 'Kisumu', 1289, 4.8, '2025-01-03 12:00:00', '2025-01-04 08:00:00');
        """)
        
        cursor.execute("""
        INSERT INTO user (userid, username, phone, email) 
        VALUES
        ('U001', 'John Doe', '0712345678', 'john.doe@example.com'),
        ('U002', 'Jane Smith', '0723456789', 'jane.smith@example.com');
        """)
        
        cursor.execute("""
        INSERT INTO booking (booking_id, userid, busid, passengers, date_) 
        VALUES
        ('B001', 'U001', '12345', 3, '2024-12-31'),
        ('B002', 'U002', '12346', 2, '2025-01-02');
        """)

        # Commit the transaction
        connection.commit()

        # Select query to verify insertion
        cursor.execute("SELECT * FROM bus WHERE busid = '12345';")
        result = cursor.fetchall()

        return f"Database operations completed successfully. Bus details: {result}"

    except Error as e:
        print(f"Error: {e}")
        return f"Error: {e}"

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
