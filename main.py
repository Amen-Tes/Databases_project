#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                        port=8889,
                       user='root',
                       password='password',
                       db='dbp_3',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_success_agent')
def login_success_agent():
	return render_template('login_success_agent.html')

@app.route('/login_success_customer')
def login_success_customer():
	return render_template('login_success_customer.html')

@app.route('/login_success_staff')
def login_success_staff():
	return render_template('login_success_staff.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/search')
def search():
        #cursor used to send queries
        return render_template('search.html')

##In Progress
# @app.route('/agent_view_commission')
# def agent_view_commission():
#     return render_template('agent_view_commission.html')

# @app.route('/agent_view_cust')
# def agent_view_cust():
#         #cursor used to send queries
#         return render_template('agent_view_cust.html')

"""Booking agent cases"""
'''*********************************************************************************************************************************'''
@app.route('/agent_view_flights', methods=['GET', 'POST'])
def search_agent_flight():
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, departure_airport, arrival_time, arrival_airport, ticket_id, customer_email FROM flight natural join ticket NATURAL JOIN purchases NATURAL JOIN booking_agent WHERE status =%s AND booking_agent.email = %s'
    session_key = session.get('email')
    cursor.execute(query, ("upcoming",session_key))
    data = cursor.fetchall()
    error = None
    count = 0
    dicty={}
    if data:
        for i in range(len(data)):
            dicty[i] = (data[i]['flight_num'], data[i]['departure_airport'], data[i]['departure_time'], data[i]['arrival_time'], data[i]['flight_num'], data[i]['ticket_id'], data[i]['customer_email'])
    else:
        return "please purchase a ticket first"
        return render_template("login_success_agent.html")

    headers = ['flight_num', 'departure_airport', 'departure_time', 'arrival_airport', 'arrival_time', 'ticket_id', 'customer_email']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/agent_purchase', methods = ['GET', 'POST'])
def agent_purchase():
    return render_template("purchase_portal_agent.html")

@app.route('/agent_search_to_purchase', methods = ['GET', 'POST'])
def agent_search_to_get():
    flight_number = request.form['flight_number']
    customer_email = request.form['customer_email']
    session_key = session.get('email')
    status = 'upcoming'
    cursor = conn.cursor()
    q6 = 'select flight_num, count(*) AS c from ticket WHERE flight_num = %s group by flight_num;'
    cursor.execute(q6, (flight_number))
    data6= cursor.fetchone()
    check_if_flight_full_2 = 'SELECT seats FROM airplane NATURAL JOIN flight WHERE flight_num = %s'
    cursor.execute(check_if_flight_full_2, (flight_number))
    data7 = cursor.fetchone()
    if data6['c'] >= data7['seats']:
        return 'AIRPLANE IS FULL'
    q5 = 'SELECT distinct(airline_name) FROM flight WHERE flight_num = %s'
    cursor.execute(q5, (flight_number))
    data5 = cursor.fetchone()
    q4 = 'SELECT MAX(ticket_id) as m FROM ticket'
    cursor.execute(q4)
    data4 = cursor.fetchone()
    increase_by_one = data4['m']+1
    query = 'INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES (%s,%s,%s);'
    cursor.execute(query,(increase_by_one, data5['airline_name'], flight_number))
    q3 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
    cursor.execute(q3, (session_key))
    data3 = cursor.fetchone()
    if data5:
        q2 = 'SELECT NOW()'
        cursor.execute(q2)
        data2 = cursor.fetchone()
        main_query = 'INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES (%s,%s,%s,%s);'
        cursor.execute(main_query,(increase_by_one, customer_email, data3['booking_agent_id'], data2["NOW()"]))
        conn.commit()
        return render_template("purchase_portal_agent.html", success = "You have successfully purchased your flight, congrats")
    else:
        error = "This flight does not exist or is not upcoming"
        return render_template('purchase_portal.html', error = error)

@app.route('/searchit', methods = ['GET', 'POST'])
def searchf():
    airportsource = request.form['airportsource']
    airportdestination = request.form['airportdestination']
    status = 'upcoming'
    cursor = conn.cursor()
    query = 'SELECT distinct(flight_num), departure_time, arrival_time FROM flight natural join airport WHERE status= %s AND (departure_airport = %s or airport_city = %s) and (arrival_airport = %s or airport_city = %s)'
    cursor.execute(query, (status.lower(),airportsource.lower(), airportsource.lower(), airportdestination.lower(), airportdestination.lower()))
    data = cursor.fetchall()
    error = None
    dicty={}
    if(data):
        for i in range(len(data)):
            dicty[i] = (data[i]['flight_num'], status, data[i]['departure_time'], airportsource, data[i]['arrival_time'], airportdestination)
    else:
        error = "please enter proper source and destination values"
        return render_template('login_success_customer.html', error = error)

    headers = ['flight_num', 'status', 'departs on', 'departs from', 'arrives on', 'arrives at']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)



@app.route('/view_my_total_commission', methods = ['GET', 'POST'])
def agent_view_commission():
    session_key = session.get('email')
    cursor = conn.cursor()
    q3 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
    cursor.execute(q3, (session_key))
    data3 = cursor.fetchone()
    agents_id = data3['booking_agent_id']
    query = 'SELECT distinct(booking_agent_id), sum(price*0.1) AS s FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 MONTH)  GROUP BY booking_agent_id;'
    cursor.execute(query, (int(agents_id)))
    data2 = cursor.fetchone()
    dicty={}
    if(data2):
        dicty[0] = (agents_id, str(data2['s']))
    else:
        error = "You have not sold anything"
        return render_template('login_success_customer.html', error = error)

    headers = ['agent id', 'sum of commission received']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/view_my_average_commission', methods = ['GET', 'POST'])
def avgcommission():
    session_key = session.get('email')
    cursor = conn.cursor()
    q3 = 'SELECT booking_agent_id FROM booking_agent WHERE email = %s'
    cursor.execute(q3, (session_key))
    data3 = cursor.fetchone()
    agents_id = data3['booking_agent_id']
    query5 = 'SELECT distinct(booking_agent_id), avg(price*0.1) AS s FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 MONTH)  GROUP BY booking_agent_id;'
    cursor.execute(query5, (int(agents_id)))
    data2 = cursor.fetchone()
    dicty={}
    if(data2):
        dicty[0] = (agents_id, str(data2['s']))
    else:
        error = "You have not sold anything"
        return render_template('login_success_customer.html', error = error)

    headers = ['agent id', 'average commission received']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)



@app.route('/agent_view_cust')
def agent_view_cust():
    session_key = session.get('email')
    if session_key == "Booking@agent.com":
        keykey = 1
    else:
        keykey = 2
    cursor = conn.cursor()
    #executes query
    query = 'SELECT customer_email, COUNT(*) as c FROM flight NATURAL JOIN booking_agent NATURAL JOIN purchases NATURAL JOIN ticket WHERE booking_agent_id = %s AND flight.flight_num = ticket.flight_num AND ticket.ticket_id = purchases.ticket_id GROUP BY customer_email ORDER BY c DESC LIMIT 5;'
    cursor.execute(query, (keykey))
    data = cursor.fetchone()
    example = data["customer_email"]
    diction = {}
    for i in range(1):
        diction[i] = "Best customer based on the number of tickets is {}".format(example)
        print('\n')

    query1 = 'SELECT SUM(price), COUNT(booking_agent_id) AS tics_sold, MAX(price) as calc FROM flight NATURAL JOIN booking_agent NATURAL JOIN purchases NATURAL JOIN ticket WHERE booking_agent_id = %s AND flight.flight_num = ticket.flight_num AND ticket.ticket_id = purchases.ticket_id'
    cursor.execute(query1, (keykey))
    data1 = cursor.fetchone()
    commission = (float(data1['SUM(price)']))*0.1
    max_comm = (float(data1["calc"]))*0.1
    dicti = {}
    for i in range(1):
        dicti[i] = "Highest commission is {:.2f}".format(max_comm)
    return '{}{}'.format(diction, dicti)


'''*********************************************************************************************************************************'''

"""Airline Staff Cases"""
'''*********************************************************************************************************************************'''
@app.route('/staff_view_flights', methods=['GET', 'POST'])
def flightss():
    return render_template("staffvflights.html")
@app.route('/view all available flights', methods=['GET', 'POST'])
def search_staff_flight():
    session_key = session.get('username')
    cursor = conn.cursor()
    #executes query
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT flight_num, departure_time, departure_airport, arrival_time, arrival_airport, status FROM flight WHERE airline_name = %s'
    session_key = session.get('username')
    cursor.execute(query, (airlinename))
    data = cursor.fetchall()
    error = None
    rows = []
    tuplerow=tuple(rows)
    count=0
    dicty={}
    if data:
        for i in range(len(data)):
            var=data[count]
            dicty[count] = (data[count]['flight_num'],  data[count]['departure_airport'],  data[count]['departure_time'], data[count]['arrival_airport'], data[count]['arrival_time'], data[count]['flight_num'], data[count]['status'])
            count+=1

    else:
        return "there are no flights in this system, please add one first"
        return render_template("login_success_staff.html")

    headers = ['flight_num', 'departs from', 'departure time', 'arrives to', 'arrival time', 'flight number', 'status']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)
@app.route('/view customers purchases', methods=['GET', 'POST'])
def custpur():
    session_key = session.get('username')
    cursor = conn.cursor()
    #executes query
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT * from purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE airline_name = %s'
    cursor.execute(query, (airlinename))
    data = cursor.fetchall()
    error = None
    rows = []
    tuplerow=tuple(rows)
    count=0
    dicty={}
    if data:
        for i in range(len(data)):
            var=data[count]
            dicty[count] = (data[count]['ticket_id'],  data[count]['customer_email'], data[count]['booking_agent_id'], data[count]['purchase_date'])
            count+=1

    else:
        return "there are no customers with purchases"
        return render_template("login_success_staff.html")

    headers = ['ticket id', 'customer email', 'booking agent id', 'purchase date']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)


@app.route('/create_flights', methods=['GET', 'POST'])
def create_flights():
    return render_template("airline_staff_createflights.html")

@app.route('/create flights', methods=['GET', 'POST'])
def creation():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    flight_num = request.form['flight_num']
    departure_airport = request.form['departure_airport']
    departure_time = request.form['departure_time']
    arrival_airport = request.form['arrival_airport']
    arrival_time = request.form['arrival_time']
    price = request.form['price']
    status = request.form['status']
    airplane_id = request.form['airplane_id']
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM flight where flight_num = %s AND airline_name = %s;'
    try:
        cursor.execute(query, (flight_num, airlinename))
        data = cursor.fetchall()
    except:
        error = "enter proper info"
        return render_template('airline_staff_createflights.html', error = error)
    #stores the results in a variable
    #use fetchall() if you are expecting more than 1 data row
    error = None
    for i in range(len(data)):
        if data[i]['flight_num'] == flight_num:
            error = "This flight already exists"
            return render_template('airline_staff_createflights.html', error = error)
    else:
        flight_insert = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(flight_insert, (airlinename.lower(), flight_num, departure_airport.lower(), departure_time, arrival_airport.lower(), arrival_time, price, status.lower(), airplane_id))
        ticket_insert = 'INSERT INTO ticket VALUES(%s,%s,%s)'
        cursor.execute(ticket_insert, (ticket_id, airlinename, flight_num))
        conn.commit()
        cursor.close()
        success = "you have successfully created a new flight"
        return render_template('airline_staff_createflights.html', success = success)

@app.route('/change_flight_status', methods=['GET', 'POST'])
def change():
    return render_template("change_status.html")
@app.route('/changestatus', methods=['GET', 'POST'])
def change_status():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    flight_num = request.form['flight_num']
    status = request.form['status']
    cursor = conn.cursor()
    query = 'SELECT flight_num FROM flight where flight_num = %s AND airline_name = %s'
    cursor.execute(query, (flight_num, airlinename))
    data = cursor.fetchone()
    if data:
        query2 = 'UPDATE flight SET status = %s WHERE flight_num = %s'
        cursor.execute(query2, (status, flight_num))
        conn.commit()
        cursor.close()
        success = "you have successfully updated a flight status"
        return render_template('change_status.html', success = success)
    else:
        error = "enter proper info"
        return render_template('login_success_staff.html', error = error)
@app.route('/add_airplane', methods=['GET', 'POST'])
def addairplane():
    return render_template("addairplane.html")
@app.route('/addairplane', methods=['GET', 'POST'])
def create_airplane():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    airplane_id = request.form['airplane_id']
    seats = request.form['number_of_seats']
    #executes query
    try:
        query = 'SELECT * FROM airplane where airline_name = %s;'
        cursor.execute(query, (airlinename))
        data = cursor.fetchall()
    except:
        error = "enter proper info"
        return render_template('addairplane.html', error = error)
    #stores the results in a variable
    #use fetchall() if you are expecting more than 1 data row
    error = None
    for i in range(len(data)):
        if data[i]['airplane_id'] == airplane_id:
            error = "This airplane already exists"
            return render_template('addairplane.html', error = error)
    else:
        ins = 'INSERT INTO airplane VALUES(%s, %s, %s)'
        cursor.execute(ins, (airlinename, airplane_id, seats))
        conn.commit()
        cursor.close()
        success = "you have successfully created a new airplane"
        return render_template('addairplane.html', success = success)

@app.route('/add_airport', methods=['GET', 'POST'])
def addairport():
    return render_template("addairport.html")
@app.route('/addairport', methods=['GET', 'POST'])
def create_airport():
    airport = request.form['airport_name']
    airport_city = request.form['airport_city']
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airport;'
    cursor.execute(query)
    data = cursor.fetchall()
    #stores the results in a variable
    #use fetchall() if you are expecting more than 1 data row
    error = None
    for i in range(len(data)):
        if data[i]['airport_name'] == airport:
            error = "This airport already exists"
            return render_template('addairport.html', error = error)
    else:
        ins = 'INSERT INTO airport VALUES(%s, %s)'
        cursor.execute(ins, (airport.lower(), airport_city))
        conn.commit()
        cursor.close()
        success = "you have successfully added a new airport"
        return render_template('addairport.html', success = success)

@app.route('/staff_view_customers', methods=['GET', 'POST'])
def viewcust():
    session_key = session.get('username')
    cursor = conn.cursor()
    #executes query
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']

    query2 = 'SELECT customer_email, COUNT(*) as c FROM purchases NATURAL JOIN ticket natural join flight where airline_name = %s GROUP BY customer_email ORDER BY c DESC LIMIT 1;'
    cursor.execute(query2, (airlinename))
    data2 = cursor.fetchone()
    customersinfo = data2['customer_email']
    query3 = 'SELECT name FROM customer WHERE email = %s'
    cursor.execute(query3, (customersinfo))
    data3 = cursor.fetchone()
    customersname = data3['name']
    #stores the results in a variable
    #use fetchall() if you are expecting more than 1 data row
    return render_template('view_customer.html', customer=customersname)

@app.route('/viewhist', methods=['GET', 'POST'])
def viewhist():
    session_key = session.get('username')
    cursor = conn.cursor()
    #executes query
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']

    query2 = 'SELECT customer_email, COUNT(*) as c FROM purchases natural join ticket natural join flight where airline_name = %s GROUP BY customer_email ORDER BY c DESC LIMIT 1;'
    cursor.execute(query2, (airlinename))
    data2 = cursor.fetchone()
    #stores the results in a variable
    #use fetchall() if you are expecting more than 1 data row
    f = data2['customer_email']
    query3 = 'SELECT airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, airplane_id from flight natural join ticket natural join purchases where customer_email = %s'
    cursor.execute(query3, (f))
    data = cursor.fetchall()
    dicty = {}
    for i in range(len(data)):
        dicty[i+1] = (data[i]['airline_name'], data[i]['flight_num'], data[i]['departure_airport'], data[i]['departure_time'], data[i]['arrival_airport'], data[i]['arrival_time'], data[i]['price'], data[i]['airplane_id'])

    headers = ['airline name', 'flight number', 'departure airport', 'departure time', 'arrival airport', 'arrival time', 'price', 'airplane id']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/view_dest', methods=['GET', 'POST'])
def viewdest():
    return render_template('viewdest.html')

@app.route('/view_dest_1yr', methods=['GET', 'POST'])
def viewdest1yr():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query2 = 'SELECT airport_city, COUNT(*) as c FROM airport natural join flight natural join ticket NATURAL JOIN purchases where airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) GROUP BY airport_city ORDER BY c DESC LIMIT 3;'
    cursor.execute(query2, (airlinename))
    data2 = cursor.fetchall()
    dicty = {}
    for i in range(len(data2)):
        dicty[i] = (i+1, data2[i]['airport_city'])

    headers = ['destination popularity', 'location']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/view_dest_3month', methods=['GET', 'POST'])
def viewdest3month():
    session_key = session.get('username')
    cursor = conn.cursor()
    #executes query
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query2 = 'SELECT airport_city, COUNT(*) as c FROM airport natural join flight natural join ticket NATURAL JOIN purchases where airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 3 MONTH) GROUP BY airport_city ORDER BY c DESC LIMIT 3;'
    cursor.execute(query2, (airlinename))
    data2 = cursor.fetchall()
    dicty = {}
    for i in range(len(data2)):
        dicty[i] = (i+1, data2[i]['airport_city'])

    headers = ['destination popularity', 'location']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/view_reports', methods = ['GET', 'POST'])
def revenue_c():
    return render_template("revenue_choice_barchart.html")

@app.route('/one_year', methods = ['GET', 'POST'])
def one_year_bar():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS m, count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE MONTH(purchase_date) = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND airline_name = %s GROUP BY m ORDER BY c;'
    my_values = []
    for i in range(1, 12):
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                my_values.append(data[k]['c'])
        else:
            my_values.append(0)


        """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""

    labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC']

    values = my_values

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    pie_labels=labels
    pie_values=values
    return render_template('bar_chart.html', title='Tickets sold within the past year', max=20, values=values, labels = labels)

@app.route('/month_bar', methods = ['GET', 'POST'])
def SIX_month_BAR():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    q2 = 'SELECT MONTH(NOW()) AS now'
    cursor.execute(q2)
    data2 = cursor.fetchone()
    query = 'SELECT MONTH(purchase_date) AS m, count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE MONTH(purchase_date) = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND airline_name = %s GROUP BY m ORDER BY c;'
    my_values = []
    for i in range(0, 12):
        cursor.execute(query, (i+1, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                my_values.append(data[k]['c'])
        else:
            my_values.append(0)



    """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""
    labels = []
    values = []
    if data2['now'] == 1:
        labels.extend(['AUG','SEP', 'OCT', 'NOV', 'DEC', 'JAN'])
        values.extend(my_values[6:12])
        values.append(my_values[0])
    elif data2['now'] == 2:
        labels.extend(['SEP','OCT', 'NOV', 'DEC', 'JAN', 'FEB'])
        values.extend(my_values[8:12])
        values.append(my_values[0])
        values.append(my_values[1])
    elif data2['now'] == 3:
        labels.extend(['OCT','NOV', 'DEC', 'JAN', 'FEB', 'MAR'])
        values.extend(my_values[9:12])
        values.append(my_values[0])
        values.append(my_values[1])
        values.append(my_values[2])
    elif data2['now'] == 4:
        labels.extend(['NOV','DEC', 'JAN', 'FEB', 'MAR', 'APR'])
        values.append(my_values[10])
        values.append(my_values[11])
        values.append(my_values[0])
        values.append(my_values[1])
        values.append(my_values[2])
        values.append(my_values[3])
    elif data2['now'] == 5:
        labels.extend(['DEC','JAN', 'FEB', 'MAR', 'APR', 'MAY'])
        values.append(my_values[11])
        values.extend(my_values[0:6])
    elif data2['now'] == 6:
        labels.extend(['JAN','FEB', 'MAR', 'APR', 'MAY', 'JUNE'])
        values.extend(my_values[0:7])
    elif data2['now'] == 7:
        labels.extend(['FEB','MAR', 'APR', 'MAY', 'JUN', 'JUL'])
        values.extend(my_values[1:8])
    elif data2['now'] == 8:
        labels.extend(['MAR','APR', 'MAY', 'JUNE', 'JUL', 'AUG'])
        values.extend(my_values[2:9])
    elif data2(['now']) == 9:
        labels.extend(['APR','MAY', 'JUN', 'JUL', 'AUG', 'SEP'])
        values.extend(my_values[3:10])
    elif data2['now'] == 10:
        labels.extend(['MAY','JUN', 'JUL', 'AUG', 'SEP', 'OCT'])
        values.extend(my_values[4:11])
    elif data2['now'] == 11:
        labels.extend(['JUN','JUL', 'AUG', 'SEP', 'AUG', 'NOV'])
        values.extend(my_values[5:12])
    elif data2['now'] == 12:
        labels.extend(['JUL','AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
        values.extend(my_values[6:13])

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='Tickets sold within the past 6 months', max=20, labels=bar_labels, values=bar_values)
@app.route('/staff_view_agents', methods = ['GET', 'POST'])
def choose():
    return render_template('staff_view_booking_agent.html')
@app.route('/pastyear', methods = ['GET', 'POST'])
def yr():
    return render_template('bestagents_year.html')
@app.route('/pastmonth', methods = ['GET', 'POST'])
def mnth():
    return render_template('bestagents_month.html')
@app.route('/tickets_sold_yr', methods = ['GET', 'POST'])
def ticketyr():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT booking_agent_id, count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND airline_name = %s AND booking_agent_id IS NOT NULL GROUP BY booking_agent_id ORDER BY c DESC LIMIT 5;'
    cursor.execute(query, (airlinename))
    data2 = cursor.fetchall()
    dicty={}
    if(data2):
        for i in range(len(data2)):
            dicty[i] = (data2[i]['booking_agent_id'], data2[i]['c'])
    else:
        error = "no data"
        return render_template('login_success_customer.html', error = error)

    headers = ['agent id', 'tickets sold']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/tickets_sold_month', methods = ['GET', 'POST'])
def ticketMTH():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT booking_agent_id, count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE purchase_date > DATE_SUB(NOW(), INTERVAL 1 MONTH) AND airline_name = %s AND booking_agent_id IS NOT NULL GROUP BY booking_agent_id ORDER BY c DESC LIMIT 5;'
    cursor.execute(query, (airlinename))
    data2 = cursor.fetchall()
    dicty={}
    if(data2):
        for i in range(len(data2)):
            dicty[i] = (data2[i]['booking_agent_id'], data2[i]['c'])
    else:
        error = "no data"
        return render_template('login_success_customer.html', error = error)

    headers = ['agent id', 'tickets sold']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)




@app.route('/compare_revenue_earned', methods = ['GET', 'POST'])
def viewreptyp():
    return render_template('report_type.html')
@app.route('/indirect_sales', methods = ['GET', 'POST'])
def yearmonth():
    return render_template('yearormonth_indirect.html')
@app.route('/direct_sales', methods = ['GET', 'POST'])
def yearmonth_direct():
    return render_template('yearormonth_direct.html')
'''***********************************************************************************'''
'''**************report yearly revenues earned direct and indirect*********'''
@app.route('/year_pie_indirect', methods = ['GET', 'POST'])
def indirect_year_piechart():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND booking_agent_id IS NOT NULL'
    my_values = []
    for i in range(1, 12):
        temp = []
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                temp.append(data[k]['price'])
        my_values.append(sum(temp))
        del temp[:]

    labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC']

    values = my_values

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    pie_labels=labels
    pie_values=values
    return render_template('report_piechart.html', title='Revenue earned indirectly within the past year', max=20, set=zip(values, labels, colors))

@app.route('/year_pie_direct', methods = ['GET', 'POST'])
def direct_year_piechart():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND booking_agent_id IS NULL'
    my_values = []
    for i in range(1, 12):
        temp = []
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                temp.append(data[k]['price'])
        my_values.append(sum(temp))
        del temp[:]




    labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC']

    values = my_values

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    pie_labels=labels
    pie_values=values
    return render_template('report_piechart.html', title='Revenue earned from direct sales within the past year', max=20, set=zip(values, labels, colors))
'''***********************************************************************************'''

'''**********************monthly revenues earned both directly and indirectly**********'''
@app.route('/month_pie_indirect', methods = ['GET', 'POST'])
def indirect_month_piechart():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND booking_agent_id IS NOT NULL'
    my_values = []
    q2 = 'SELECT MONTH(NOW()) AS now'
    cursor.execute(q2)
    data2 = cursor.fetchone()
    for i in range(1, 12):
        temp = []
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                temp.append(data[k]['price'])
        my_values.append(sum(temp))
        del temp[:]

    labels = []
    values = []
    if data2['now'] == 1:
        labels.extend(['DEC', 'JAN'])
        values.extend(my_values[12])
        values.append(my_values[0])
    elif data2['now'] == 2:
        labels.extend(['JAN', 'FEB'])
        values.append(my_values[0])
        values.append(my_values[1])
    elif data2['now'] == 3:
        labels.extend(['FEB', 'MAR'])
        values.append(my_values[1])
        values.append(my_values[2])
    elif data2['now'] == 4:
        labels.extend(['MAR', 'APR'])
        values.append(my_values[2])
        values.append(my_values[3])
    elif data2['now'] == 5:
        labels.extend(['APR', 'MAY'])
        values.append(my_values[3])
        values.append(my_values[4])
    elif data2['now'] == 6:
        labels.extend(['MAY', 'JUNE'])
        values.append(my_values[4])
        values.append(my_values[5])
    elif data2['now'] == 7:
        labels.extend(['JUN', 'JUL'])
        values.append(my_values[5])
        values.append(my_values[6])
    elif data2['now'] == 8:
        labels.extend(['JUL', 'AUG'])
        values.append(my_values[6])
        values.append(my_values[7])
    elif data2(['now']) == 9:
        labels.extend(['AUG', 'SEP'])
        values.append(my_values[7])
        values.append(my_values[8])
    elif data2['now'] == 10:
        labels.extend(['MAY','JUN', 'JUL', 'AUG', 'SEP', 'OCT'])
        values.append(my_values[8])
        values.append(my_values[9])
    elif data2['now'] == 11:
        labels.extend(['JUN','JUL', 'AUG', 'SEP', 'AUG', 'NOV'])
        values.append(my_values[9])
        values.append(my_values[10])
    elif data2['now'] == 12:
        labels.extend(['JUL','AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
        values.append(my_values[10])
        values.append(my_values[11])

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    pie_labels=labels
    pie_values=values
    return render_template('report_piechart.html', title='Revenue earned indirectly within the past month', max=20, set=zip(values, labels, colors))

@app.route('/month_pie_direct', methods = ['GET', 'POST'])
def DIRECT_month_piechart():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND booking_agent_id IS NULL'
    my_values = []
    q2 = 'SELECT MONTH(NOW()) AS now'
    cursor.execute(q2)
    data2 = cursor.fetchone()
    for i in range(1, 12):
        temp = []
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                temp.append(data[k]['price'])
        my_values.append(sum(temp))
        del temp[:]

    labels = []
    values = []
    if data2['now'] == 1:
        labels.extend(['DEC', 'JAN'])
        values.extend(my_values[12])
        values.append(my_values[0])
    elif data2['now'] == 2:
        labels.extend(['JAN', 'FEB'])
        values.append(my_values[0])
        values.append(my_values[1])
    elif data2['now'] == 3:
        labels.extend(['FEB', 'MAR'])
        values.append(my_values[1])
        values.append(my_values[2])
    elif data2['now'] == 4:
        labels.extend(['MAR', 'APR'])
        values.append(my_values[2])
        values.append(my_values[3])
    elif data2['now'] == 5:
        labels.extend(['APR', 'MAY'])
        values.append(my_values[3])
        values.append(my_values[4])
    elif data2['now'] == 6:
        labels.extend(['MAY', 'JUNE'])
        values.append(my_values[4])
        values.append(my_values[5])
    elif data2['now'] == 7:
        labels.extend(['JUN', 'JUL'])
        values.append(my_values[5])
        values.append(my_values[6])
    elif data2['now'] == 8:
        labels.extend(['JUL', 'AUG'])
        values.append(my_values[6])
        values.append(my_values[7])
    elif data2(['now']) == 9:
        labels.extend(['AUG', 'SEP'])
        values.append(my_values[7])
        values.append(my_values[8])
    elif data2['now'] == 10:
        labels.extend(['MAY','JUN', 'JUL', 'AUG', 'SEP', 'OCT'])
        values.append(my_values[8])
        values.append(my_values[9])
    elif data2['now'] == 11:
        labels.extend(['JUN','JUL', 'AUG', 'SEP', 'AUG', 'NOV'])
        values.append(my_values[9])
        values.append(my_values[10])
    elif data2['now'] == 12:
        labels.extend(['JUL','AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
        values.append(my_values[10])
        values.append(my_values[11])

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    pie_labels=labels
    pie_values=values
    return render_template('report_piechart.html', title='Revenue earned indirectly within the past month', max=20, set=zip(values, labels, colors))






@app.route('/yearonly', methods = ['GET', 'POST'])
def soldtickets():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE MONTH(purchase_date) = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) AND airline_name = %s GROUP BY customer_email ORDER BY c;'
    my_values = []
    for i in range(1, 12):
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                my_values.append(data[k]['c'])
        else:
            my_values.append(0)


        """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""

    labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC']

    values = my_values

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='tickets sold within the past year', max=5, labels=bar_labels, values=bar_values)

@app.route('/monthie', methods = ['GET', 'POST'])
def month_PIE():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE MONTH(purchase_date) = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 6 MONTH) AND airline_name = %s GROUP BY customer_email ORDER BY c;'
    my_values = []
    q2 = 'SELECT MONTH(NOW()) AS now'
    cursor.execute(q2)
    data2 = cursor.fetchone()
    for i in range(0, 12):
        cursor.execute(query, (i, airlinename))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                my_values.append(data[k]['c'])
        else:
            my_values.append(0)

    """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""
    labels = []
    values = []
    if data2['now'] == 1:
        labels.extend(['AUG','SEP', 'OCT', 'NOV', 'DEC', 'JAN'])
        values.extend(my_values[6:12])
        values.append(my_values[0])
    elif data2['now'] == 2:
        labels.extend(['SEP','OCT', 'NOV', 'DEC', 'JAN', 'FEB'])
        values.extend(my_values[8:12])
        values.append(my_values[0])
        values.append(my_values[1])
    elif data2['now'] == 3:
        labels.extend(['OCT','NOV', 'DEC', 'JAN', 'FEB', 'MAR'])
        values.extend(my_values[9:12])
        values.append(my_values[0])
        values.append(my_values[1])
        values.append(my_values[2])
    elif data2['now'] == 4:
        labels.extend(['NOV','DEC', 'JAN', 'FEB', 'MAR', 'APR'])
        values.append(my_values[10])
        values.append(my_values[11])
        values.append(my_values[0])
        values.append(my_values[1])
        values.append(my_values[2])
        values.append(my_values[3])
    elif data2['now'] == 5:
        labels.extend(['DEC','JAN', 'FEB', 'MAR', 'APR', 'MAY'])
        values.append(my_values[11])
        values.extend(my_values[0:6])
    elif data2['now'] == 6:
        labels.extend(['JAN','FEB', 'MAR', 'APR', 'MAY', 'JUNE'])
        values.extend(my_values[0:7])
    elif data2['now'] == 7:
        labels.extend(['FEB','MAR', 'APR', 'MAY', 'JUN', 'JUL'])
        values.extend(my_values[1:8])
    elif data2['now'] == 8:
        labels.extend(['MAR','APR', 'MAY', 'JUNE', 'JUL', 'AUG'])
        values.extend(my_values[2:9])
    elif data2(['now']) == 9:
        labels.extend(['APR','MAY', 'JUN', 'JUL', 'AUG', 'SEP'])
        values.extend(my_values[3:10])
    elif data2['now'] == 10:
        labels.extend(['MAY','JUN', 'JUL', 'AUG', 'SEP', 'OCT'])
        values.extend(my_values[4:11])
    elif data2['now'] == 11:
        labels.extend(['JUN','JUL', 'AUG', 'SEP', 'AUG', 'NOV'])
        values.extend(my_values[5:12])
    elif data2['now'] == 12:
        labels.extend(['JUL','AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
        values.extend(my_values[6:13])


    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='Expenditure within the past 6 months', max=10, labels=bar_labels, values=bar_values)

@app.route('/specifica', methods = ['GET', 'POST'])
def specifica():
    cursor = conn.cursor()
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    fromm = request.form['from']
    to = request.form['to']
    frommonth = int(fromm)
    tomonth = int(to)
    if frommonth<1 or frommonth>12 or tomonth<1 or tomonth>12:
        error = "please enter valid values"
        return render_template('login_success_customer.html', error = error)
    else:
        query = 'SELECT count(*) AS c FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE MONTH(purchase_date) = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 6 MONTH) AND airline_name = %s GROUP BY customer_email ORDER BY c;'
        my_values = []
        q2 = 'SELECT MONTH(NOW()) AS now'
        cursor.execute(q2)
        data2 = cursor.fetchone()
        if frommonth>tomonth:
            for i in range(frommonth, 13):
                cursor.execute(query, (i, airlinename))
                data = cursor.fetchall()
                if (data):
                    for k in range(len(data)):
                        my_values.append(data[k]['c'])
                else:
                    my_values.append(0)
            for i in range(1, tomonth+1):
                cursor.execute(query, (i, airlinename))
                data = cursor.fetchall()
                if (data):
                    for k in range(len(data)):
                        my_values.append(data[k]['c'])
                else:
                    my_values.append(0)

        else:
            for i in range(frommonth, tomonth+1):
                cursor.execute(query, (i, airlinename))
                data = cursor.fetchall()
                if (data):
                    for k in range(len(data)):
                        my_values.append(data[k]['c'])
                else:
                    my_values.append(0)
        """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""
        labels = []
        if frommonth<tomonth:
            for i in range(frommonth,(tomonth)+1):
                labels.append("month {}".format(i))
        elif tomonth<frommonth:
            for i in range(tomonth, 13):
                labels.append("month {}".format(i))
            for i in range(1,frommonth+1):
                labels.append("month {}".format(i))

        values = my_values

        colors = [
        "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
        "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
        "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

        bar_labels=labels
        bar_values=values
        return render_template('bar_chart.html', title='Expenditure between months {} and {}'.format(fromm, to), max=10, labels=bar_labels, values=bar_values)



'''***********'''
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
            return redirect(url_for('login_success_staff'))
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    elif type.lower() == 'customer':
        query = 'SELECT * FROM customer WHERE email = %s and password = %s'
        cursor.execute(query, (username, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(data):
            #creates a session for the the user
            #session is a built in
            session['email'] = username
            return redirect(url_for('login_success_customer'))
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    elif type.lower() == 'booking agent':
        query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
        cursor.execute(query, (username, password))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(data):
            #creates a session for the the user
            #session is a built in
            session['email'] = username
            return redirect(url_for('login_success_agent'))
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    else:
        error = "This user type does not exist, reenter"
        return render_template('register.html', error = error)


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
        ins = 'INSERT INTO airline_staff VALUES(%s, MD5(%s), %s, %s, %s, %s)'
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
        ins = 'INSERT INTO customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
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
        ins = 'INSERT INTO booking_agent VALUES(%s, MD5(%s), %s)'
        cursor.execute(ins, (email, password, bookingagentid))
        conn.commit()
        cursor.close()
        return render_template('booking agent.html')

@app.route('/searchFlight', methods=['GET', 'POST'])
def search_flights():
    return render_template('search_flight.html')

@app.route('/viewFlights', methods=['GET', 'POST'])
def view_flights():
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, departure_airport, arrival_airport, arrival_time, arrival_airport FROM flight'
    cursor.execute(query)
    data=cursor.fetchall()
    dicty = {}
    if (data):
        for i in range(len(data)):
            dicty[i] = (data[i]['flight_num'], data[i]['departure_time'], data[i]['departure_airport'], data[i]['arrival_time'], data[i]['arrival_airport'])

    headers = ['Flight num', 'departure time', 'departure airport', 'arrival time', 'arrival airport']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/search_using_info', methods=['GET', 'POST'])
def search_flight_using_info():
    airportsource = request.form['airportsource']
    airportdestination = request.form['airportdestination']
    status = 'upcoming'
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, arrival_time FROM flight natural join airport WHERE status= %s AND (departure_airport = %s or airport_city = %s) and (arrival_airport = %s or airport_city = %s)'
    cursor.execute(query, (status.lower(),airportsource.lower(), airportsource.lower(), airportdestination.lower(), airportdestination.lower()))
    data = cursor.fetchall()
    error = None
    dicty={}
    if(data):
        for i in range(len(data)):
            dicty[i] = (data[i]['flight_num'], status, data[i]['departure_time'], airportsource, data[i]['arrival_time'], airportdestination)
    else:
        error = "please enter proper source and destination values"
        return render_template('login_success_customer.html', error = error)
    headers = ['Flight num', 'status', 'departure time', 'airport source', 'arrival time', 'airport destination']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)


@app.route('/Logout', methods=['GET'])
def logout():
    return render_template('index.html')

"""All customer use cases """
'''*********************************************************************************************************************************'''
@app.route('/customer_view_flights', methods=['GET', 'POST'])
def search_customers_flight():
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, departure_airport, arrival_time, arrival_airport, ticket_id FROM flight natural join ticket NATURAL JOIN purchases WHERE status =%s AND customer_email = %s'
    session_key = session.get('email')
    cursor.execute(query, ("upcoming",session_key))
    data = cursor.fetchall()
    error = None
    rows = []
    tuplerow=tuple(rows)
    count=0
    dicty={}
    content_saver=()
    if data:
        for i in range(len(data)):
            var=data[count]
            dicty[count] = (data[count]['departure_airport'],  data[count]['departure_time'], data[count]['arrival_airport'], data[count]['arrival_time'], data[count]['flight_num'], data[count]['ticket_id'] )
            count+=1
            print('\n')

    else:
        return "please purchase a ticket first"
        return render_template("login_success_customer.html")

    headers = ['departure airport', 'departure time', 'departure airport', 'arrival time', 'arrival airport']
    table = []
    for key, value in dicty.iteritems():
        temp = []
        for i in value:
            temp.extend([i])
        table.append(temp)
    return render_template('printer.html', table = table, header = headers)

@app.route('/customer_purchase', methods = ['GET', 'POST'])
def purchase_my_flight():
    return render_template("purchase_portal.html")

@app.route('/search_to_purchase', methods = ['GET', 'POST'])
def search_to_get():
    airportsource = request.form['airportsource']
    airportdestination = request.form['airportdestination']
    flightnumber = request.form['flightnumber']
    status = 'upcoming'
    cursor = conn.cursor()
    q1 = 'SELECT ticket_id FROM ticket NATURAL JOIN flight WHERE departure_airport = %s AND arrival_airport = %s AND flight_num = %s AND status = %s'
    cursor.execute(q1, (airportsource.lower(), airportdestination.lower(), flightnumber, status))
    data1 = cursor.fetchone()
    if data1:
        session_key = session.get('email')
        q2 = 'SELECT NOW()'
        cursor.execute(q2)
        data2 = cursor.fetchone()
        main_query = 'INSERT INTO purchases (ticket_id, customer_email, purchase_date) VALUES (%s, %s, %s)'
        cursor.execute(main_query,(data1["ticket_id"], session_key, data2["NOW()"]))
        conn.commit()
        return render_template("purchase_portal.html", success = "You have successfully purchased your flight, congrats")
    else:
        error = "This flight does not exist or is not upcoming"
        return render_template('purchase_portal.html', error = error)

@app.route('/track_spending', methods = ['GET', 'POST'])
def track_expenditure():
    return render_template("tracker.html")

@app.route('/year_bar', methods = ['GET', 'POST'])
def year_bar_chart():
    session_key = session.get('email')
    cursor = conn.cursor()
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND customer_email = %s;'
    my_values = []
    for i in range(1, 12):
        temp = []
        cursor.execute(query, (i, session_key))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                temp.append(data[k]['price'])
        my_values.append(sum(temp))
        del temp[:]


        """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""

    labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC']

    values = my_values

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='Expenditure within the past year', max=1000, labels=bar_labels, values=bar_values)

@app.route('/6month_bar', methods = ['GET', 'POST'])
def month_chart():
    session_key = session.get('email')
    cursor = conn.cursor()
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND customer_email = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR);'
    my_values = []
    q2 = 'SELECT MONTH(NOW()) AS now'
    cursor.execute(q2)
    data2 = cursor.fetchone()
    for i in range(0, 12):
        temp = []
        cursor.execute(query, (i, session_key))
        data = cursor.fetchall()
        if (data):
            for k in range(len(data)):
                temp.append(data[k]['price'])
        my_values.append(sum(temp))
        del temp[:]


    """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""
    labels = []
    values = []
    if data2['now'] == 1:
        labels.extend(['AUG','SEP', 'OCT', 'NOV', 'DEC', 'JAN'])
        values.extend(my_values[6:12])
        values.append(my_values[0])
    elif data2['now'] == 2:
        labels.extend(['SEP','OCT', 'NOV', 'DEC', 'JAN', 'FEB'])
        values.extend(my_values[8:12])
        values.append(my_values[0])
        values.append(my_values[1])
    elif data2['now'] == 3:
        labels.extend(['OCT','NOV', 'DEC', 'JAN', 'FEB', 'MAR'])
        values.extend(my_values[9:12])
        values.append(my_values[0])
        values.append(my_values[1])
        values.append(my_values[2])
    elif data2['now'] == 4:
        labels.extend(['NOV','DEC', 'JAN', 'FEB', 'MAR', 'APR'])
        values.append(my_values[10])
        values.append(my_values[11])
        values.append(my_values[0])
        values.append(my_values[1])
        values.append(my_values[2])
        values.append(my_values[3])
    elif data2['now'] == 5:
        labels.extend(['DEC','JAN', 'FEB', 'MAR', 'APR', 'MAY'])
        values.append(my_values[11])
        values.extend(my_values[0:6])
    elif data2['now'] == 6:
        labels.extend(['JAN','FEB', 'MAR', 'APR', 'MAY', 'JUNE'])
        values.extend(my_values[0:7])
    elif data2['now'] == 7:
        labels.extend(['FEB','MAR', 'APR', 'MAY', 'JUN', 'JUL'])
        values.extend(my_values[1:8])
    elif data2['now'] == 8:
        labels.extend(['MAR','APR', 'MAY', 'JUNE', 'JUL', 'AUG'])
        values.extend(my_values[2:9])
    elif data2(['now']) == 9:
        labels.extend(['APR','MAY', 'JUN', 'JUL', 'AUG', 'SEP'])
        values.extend(my_values[3:10])
    elif data2['now'] == 10:
        labels.extend(['MAY','JUN', 'JUL', 'AUG', 'SEP', 'OCT'])
        values.extend(my_values[4:11])
    elif data2['now'] == 11:
        labels.extend(['JUN','JUL', 'AUG', 'SEP', 'AUG', 'NOV'])
        values.extend(my_values[5:12])
    elif data2['now'] == 12:
        labels.extend(['JUL','AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
        values.extend(my_values[6:13])

    colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

    bar_labels=labels
    bar_values=values
    return render_template('bar_chart.html', title='Expenditure within the past 6 months', max=1000, labels=bar_labels, values=bar_values)

@app.route('/specify_dates', methods = ['GET', 'POST'])
def specified():
    session_key = session.get('email')
    fromm = request.form['from']
    to = request.form['to']
    frommonth = int(fromm)
    tomonth = int(to)
    if frommonth<1 or frommonth>12 or tomonth<1 or tomonth>12:
        error = "please enter valid values"
        return render_template('login_success_customer.html', error = error)
    else:
        cursor = conn.cursor()
        query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND customer_email = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR);'
        my_values = []
        q2 = 'SELECT MONTH(NOW()) AS now'
        cursor.execute(q2)
        data2 = cursor.fetchone()
        if frommonth>tomonth:
            for i in range(frommonth, 13):
                temp = []
                cursor.execute(query, (i, session_key))
                data = cursor.fetchall()
                if (data):
                    for k in range(len(data)):
                        temp.append(data[k]['price'])
                my_values.append(sum(temp))
                del temp[:]
            for i in range(1, tomonth+1):
                temp = []
                cursor.execute(query, (i, session_key))
                data = cursor.fetchall()
                if (data):
                    for k in range(len(data)):
                        temp.append(data[k]['price'])
                my_values.append(sum(temp))
                del temp[:]
        else:
            for i in range(frommonth, tomonth+1):
                temp = []
                cursor.execute(query, (i, session_key))
                data = cursor.fetchall()
                if (data):
                    for k in range(len(data)):
                        temp.append(data[k]['price'])
                my_values.append(sum(temp))
                del temp[:]
        """ bar chart code source - https://blog.ruanbekker.com/blog/2017/12/14/graphing-pretty-charts-with-python-flask-and-chartjs/"""
        labels = []
        if frommonth<tomonth:
            for i in range(frommonth,(tomonth)+1):
                labels.append("month {}".format(i))
        elif tomonth<frommonth:
            for i in range(tomonth, 13):
                labels.append("month {}".format(i))
            for i in range(1,frommonth+1):
                labels.append("month {}".format(i))

        values = my_values

        colors = [
        "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
        "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
        "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

        bar_labels=labels
        bar_values=values
        return render_template('bar_chart.html', title='Expenditure between months {} and {}'.format(fromm, to), max=1000, labels=bar_labels, values=bar_values)

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 8000, debug = True)
