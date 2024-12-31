def setup_database(connection):
    """Set up the database by creating tables and inserting initial data."""
    cursor = connection.cursor()

    # Create tables
    tables = {
        "user": """CREATE TABLE IF NOT EXISTS user (
            userid VARCHAR(20) PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(50) NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );""",
        "bus": """CREATE TABLE IF NOT EXISTS bus (
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
        );""",
        "booking": """CREATE TABLE IF NOT EXISTS booking (
            booking_id VARCHAR(20) PRIMARY KEY,
            userid VARCHAR(20) NOT NULL,
            busid VARCHAR(20) NOT NULL,
            passengers INT NOT NULL,
            date_ DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (busid) REFERENCES bus(busid) ON DELETE CASCADE
        );"""
    }
    for name, query in tables.items():
        cursor.execute(query)

    # Insert initial data
    data = [
        """INSERT INTO bus (busid, origin, destination, cost, rating, departure, arrival) 
        VALUES
        ('12345', 'Nairobi', 'Migori', 1299, 4.3, '2023-08-01 08:00:00', '2023-08-01 12:00:00'),
        ('12346', 'Nairobi', 'Kitale', 1999, 3.3, '2023-08-02 08:00:00', '2023-08-02 16:00:00'),
        ('12348', 'Nairobi', 'Kisumu', 1289, 4.8, '2023-08-03 08:00:00', '2023-08-03 12:00:00');""",
        """INSERT INTO user (userid, username, phone, email) 
        VALUES
        ('U001', 'John Doe', '0712345678', 'john.doe@example.com'),
        ('U002', 'Jane Smith', '0723456789', 'jane.smith@example.com');""",
        """INSERT INTO booking (booking_id, userid, busid, passengers, date_) 
        VALUES
        ('B001', 'U001', '12345', 3, '2023-08-01'),
        ('B002', 'U002', '12346', 2, '2023-08-02');"""
    ]
    for query in data:
        cursor.execute(query)
    connection.commit()
    print("Database setup completed.")
