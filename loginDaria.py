#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                      # port=8889,
                       user='root',
                       password='',
                       db='db3',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/search')
def search():
        #cursor used to send queries
        return render_template('search.html')
#Authenticates the login

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    type = request.form['type']
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    #query = 'CREATE VIEW person '
    if type.lower() == 'staff':
        query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
        cursor.execute(query, (username, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(data):
            #creates a session for the the user
            #session is a built in
            session['username'] = username
            return redirect(url_for('home'))
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    elif type.lower() == 'customer':
        query = 'SELECT * FROM customer WHERE username = %s and password = %s'
        cursor.execute(query, (username, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(data):
            #creates a session for the the user
            #session is a built in
            session['username'] = username
            return redirect(url_for('home'))
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    elif type.lower() == 'booking agent':
        query = 'SELECT * FROM booking_agent WHERE username = %s and password = %s'
        cursor.execute(query, (username, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(data):
            #creates a session for the the user
            #session is a built in
            session['username'] = username
            return redirect(url_for('home'))
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    else:
        error = "This user type does not exist, reenter"
        return render_template('register.html', error = error)


    # query = 'SELECT * FROM type WHERE username = %s and password = %s'
    # cursor.execute(query, (username, password))
    # #stores the results in a variable
    # data = cursor.fetchone()
    # #use fetchall() if you are expecting more than 1 data row
    # cursor.close()
    # error = None
    # if(data):
    #     #creates a session for the the user
    #     #session is a built in
    #     session['username'] = username
    #     return redirect(url_for('home'))
    # else:
    #     #returns an error message to the html page
    #     error = 'Invalid login or username'
    #     return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    type = request.form['type']
    if type.lower() == 'staff':
        return render_template('staff.html')
    elif type.lower() == 'customer':
        return render_template('customer.html')
    elif type.lower() == 'booking agent':
        return render_template('booking agent.html')
    else:
        error = "This user type does not exist, reenter"
        return render_template('register.html', error = error)
@app.route('/staffRegister', methods=['GET', 'POST'])
def staffRegister():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    dateofbirth = request.form['dateofbirth']
    airlinename = request.form['airlinename']
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstname, lastname, dateofbirth, airlinename))
        conn.commit()
        cursor.close()
        return render_template('staff.html')
@app.route('/customerRegister', methods=['GET', 'POST'])
def customerRegister():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['building_number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phonenumber = request.form['phonenumber']
    passportnumber = request.form['passportnumber']
    passportexpiration = request.form['passportexpiration']
    passportcountry = request.form['passportcountry']
    dateofbirth = request.form['dateofbirth']
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, name, password, building_number, street, city, state, phonenumber, passportnumber, passportexpiration, passportcountry, dateofbirth))
        conn.commit()
        cursor.close()
        return render_template('customer.html')

@app.route('/booking_agentRegister', methods=['GET', 'POST'])
def booking_agentRegister():
    email = request.form['email']
    password = request.form['password']
    bookingagentid = request.form['bookingagentid']

    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
        cursor.execute(ins, (email, password, bookingagentid))
        conn.commit()
        cursor.close()
        return render_template('booking agent.html')

@app.route('/searchFlight', methods=['GET'])
def search_flights():
    return render_template('search_flight.html')

@app.route('/viewFlights', methods=['Get'])
def view_flights():
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, arrival_time, status FROM flight'
    cursor.execute(query)
    data=cursor.fetchall()
    if (data):
        for i in range(len(data)):
            return 'flight_num = {}  ,   departure_time = {}    ,   arrival_time = {},    status = {}'.format(data[i]['flight_num'], data[i]['departure_time'], data[i]['arrival_time'], data[i]['status'])
            return '\n'


@app.route('/search_using_info', methods=['GET', 'POST'])
def search_flight_using_info():
    airportsource = request.form['airportsource']
    airportdestination = request.form['airportdestination']
    status = 'upcoming'
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, arrival_time FROM flight natural join airport WHERE status= %s AND (departure_airport = %s or airport_city = %s) and (arrival_airport = %s or airport_city = %s)'
    cursor.execute(query, (status.lower(),airportsource.lower(), airportsource.lower(), airportdestination.lower(), airportdestination.lower()))
    data = cursor.fetchone()
    error = None
    if(data):
        return 'flight with flight number {} is upcoming and will depart on {} from {}. Flight {} will arrive on {} at {} '.format(data['flight_num'], data['departure_time'], airportsource, data['flight_num'], data['arrival_time'], airportdestination)
    else:
        return 'doesnt work'


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
