from flask import Flask, abort, render_template, request, redirect, url_for
#from query_db import *

app = Flask(__name__)

# Search Page
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print(request.form)
        '''
        origin = request.form.get('origin')
        destination = request.form['destination']

        cursor = mysql.connection.cursor()
        query = ' SELECT busid, origin, destination, departure, arrival, passengers, date_
        FROM bus
        WHERE origin = %s AND destination = %s '
        buses = cursor.fetchall()
        
        if origin == destination:
                return render_template('index.html-')
        if buses:
            return("List of Buses")
        '''
    else:
        return ('skipped') 
    return render_template('index.html')
    


'''@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404 '''


# Search bar for updating
@app.route('/update', methods=["GET", "POST"])
def update():
    if request.method == "POST":
        record_id = request.form['id']  
        
        if not record_id.isdigit():  # validate
            return "Invalid ID format", 400 
        
        return redirect(f"/change/{record_id}")
    
    return render_template('update.html')


# Update Page
@app.route('/change/<int:id>')
def change(id):
    # Assuming `booking_details(id)` is a function that returns booking details
    busd = booking_details(id)
    
    if not busd:  # If no data found (empty list or None)
        return render_template('error.html') 
    
    # Render the change page with the booking details
    return render_template('change.html', busd=busd)


# Booking details page, here we got an option for update or delete
@app.route('/updel/<int:bookid>', methods=["GET", "POST"])
def updel(bookid):
    if request.method == "POST":
        req = request.form.get('op')  # Use .get() to avoid key errors if 'op' doesn't exist

        # If 'update' is selected
        if req == "update":
            busd = booking_details(bookid)
            
            if not busd:  # Check if no data was found for the booking ID
                return render_template('error.html', error_message=f"Booking ID {bookid} not found.")
            
            seat = busd[2][7]  # Assuming seat data is in busd[2][7]
            
            seats = [i for i in range(1, seat + 1)]
            return render_template("updateBooking.html", busd=busd, seats=seats)

        # If 'delete' is selected
        else:
            busd = booking_details(bookid)
            
            if not busd:  # If no booking found, show error page
                return render_template('error.html', error_message=f"Booking ID {bookid} not found.")
            
            busid = busd[0][2]  # Assuming busid is in busd[0][2]
            passengers = book_passengers(bookid)  # Assuming this fetches the passenger count
            
            update_bus_passengers(busid, -passengers)  # Update the bus passenger count
            delete(bookid)  # Delete the booking

            return render_template("deleted.html")

    return render_template('error.html', error_message="Invalid request method.")


# Booking update page
@app.route('/updatebook/<int:bookid>', methods=["GET", "POST"])
def updatebook(bookid):
    if request.method == "POST":
        # Retrieve data from the form
        name = request.form['name']
        phno = request.form['phno']
        email = request.form['email']
        passengers = request.form['passengers']

        # Simple form validation
        if not name or not phno or not email or not passengers.isdigit():
            return render_template("error.html", message="All fields are required and 'Passengers' must be a number.")

        # Parse passengers as an integer
        passengers = int(passengers)

        # Get current booking details
        busd = booking_details(bookid)
        if not busd:
            return render_template('error.html', error_message="Booking ID not found.")
        
        busid = busd[0][2]  # Assuming the bus ID is stored here
        oldpassengers = book_passengers(bookid)  # Get the number of passengers in the original booking
        
        # Update user and booking details
        user_new_details = [name, phno, email]
        booking_new_details = [passengers]
        updatebookuser(user_new_details, booking_new_details, bookid)
        
        # Calculate the difference in passenger numbers
        new_passengers = passengers - oldpassengers
        update_bus_passengers(busid, new_passengers)  # Update the bus with the new number of passengers
        
        # Provide feedback to the user
        return render_template("updated.html", message="Booking updated successfully.")

    # Handle GET request
    return render_template("error.html", error_message="Invalid request method.")


# Returns all bus details
@app.route('/search/<from_location>/<to_location>')
def search(from_location, to_location):
    # Ensure valid data is being passed (e.g., no empty strings or invalid values)
    if not from_location or not to_location:
        return render_template('error.html', message="Both 'from' and 'to' locations are required.")
    
    # Retrieve bus details
    try:
        details = all_bus(to_location, from_location)
    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {e}")
    
    # If no buses are found, show a message to the user
    if not details:
        return render_template('search.html', det=details, message="No buses found for this route.")
    
    # If buses are found, render the search results
    return render_template('search.html', det=details)


# Page for booking
@app.route('/book/<int:busid>')
def book(busid):
    busd = busdetails(busid)
    
    # Check if bus details are valid
    if not busd:
        return render_template('error.html')  # Bus not found
    
    seat = busd[0][7]  # Assuming seat count is at index 7
    if seat <= 0:
        return render_template('no_seats.html')  # No seats available for booking
    
    # Generate a list of available seats
    seats = [i for i in range(1, seat + 1)]
    
    # Pass bus details and seats to the template
    return render_template('book.html', busd=busd, seats=seats)

# Booking a ticket
@app.route('/booked/<int:busid>', methods=["GET", "POST"])
def booked(busid):
    if request.method == "POST":
        # Get form data
        name = request.form['name']
        phno = request.form['phno']
        email = request.form['email']
        passengers = request.form['passengers']
        
        # Validate the form data
        if not name or not phno or not email or not passengers:
            return render_template('error.html', message="All fields are required.")
        
        # Ensure passengers is a positive integer and within the available seat limit
        try:
            passengers = int(passengers)
        except ValueError:
            return render_template('error.html', message="Invalid number of passengers.")
        
        busd = busdetails(busid)
        available_seats = busd[0][7]  # Assuming seat count is at index 7
        
        if passengers > available_seats:
            return render_template('error.html', message="Not enough seats available.")
        
        # Generate unique ids for the user and booking
        userid = generateid()
        bookingid = generateid()

        # Update bus passengers and insert new user and booking details
        update_bus_passengers(busid, passengers)
        user_details = [userid, name, phno, email, bookingid]
        booking_details = [bookingid, userid, busid, passengers]
        
        # Insert user and booking into the database
        try:
            userinsert(user_details)
            bookinginsert(booking_details)
        except Exception as e:
            return render_template('error.html', message="Error booking the ticket. Please try again.")

        # Return the booked ticket confirmation page with the booking ID
        return render_template('booked.html', id=bookingid)
    
    return render_template('book.html', busid=busid)


if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=8080)
