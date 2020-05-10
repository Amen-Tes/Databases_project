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
                       db='databases_project_part3',
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
    rows = []
    tuplerow=tuple(rows)
    count=0
    dicty={}
    content_saver=()
    if data:
        for i in range(len(data)):
            var=data[count]
            dicty[count] = "flight number {},  departs from {},  departure_time {},  arrives to {},  arrival time {},  flight number = {}, ticket_id = {}, customer email is {}".format(count + 1,  data[count]['departure_airport'],  data[count]['departure_time'], data[count]['arrival_airport'], data[count]['arrival_time'], data[count]['flight_num'], data[count]['ticket_id'], data[count]['customer_email'] )
            count+=1
            print('\n')
        return dicty

    else:
        return "please purchase a ticket first"
        return render_template("login_success_agent.html")

    return rows

@app.route('/agent_purchase', methods = ['GET', 'POST'])
def agent_purchase():
    return render_template("purchase_portal_agent.html")

@app.route('/agent_search_to_purchase', methods = ['GET', 'POST'])
def agent_search_to_get():
    airportsource = request.form['airportsource']
    airportdestination = request.form['airportdestination']
    flightnumber = request.form['flightnumber']
    customeremail = request.form['customeremail']
    status = 'upcoming'
    cursor = conn.cursor()
    q1 = 'SELECT ticket_id, email FROM ticket NATURAL JOIN flight NATURAL JOIN customer WHERE email = %s AND departure_airport = %s AND arrival_airport = %s AND flight_num = %s AND status = %s'
    cursor.execute(q1, (customeremail.lower(), airportsource.lower(), airportdestination.lower(), flightnumber, status))
    data1 = cursor.fetchone()
    if data1:
        session_key = session.get('email')
        q2 = 'SELECT NOW()'
        cursor.execute(q2)
        data2 = cursor.fetchone()
        main_query = 'INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date) VALUES (%s, %s, %s, %s)'
        cursor.execute(main_query,(data1["ticket_id"], data1["email"], session_key, data2["NOW()"]))
        return render_template("purchase_portal_agent.html", success = "You have successfully purchased your flight, congrats")
    else:
        error = "This flight does not exist or is not upcoming"
        return render_template('purchase_portal_agent.html', error = error)

'''*********************************************************************************************************************************'''

"""Airline Staff Cases"""
'''*********************************************************************************************************************************'''
@app.route('/staff_view_flights', methods=['GET', 'POST'])
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
            dicty[count] = "flight number {},  departs from {},  departure_time {},  arrives to {},  arrival time {},  flight number = {}, status = {}".format(count + 1,  data[count]['departure_airport'],  data[count]['departure_time'], data[count]['arrival_airport'], data[count]['arrival_time'], data[count]['flight_num'], data[count]['status'])
            count+=1
            print('\n')
        return dicty

    else:
        return "there are no flights in this system, please add one first"
        return render_template("login_success_staff.html")

    return rows
@app.route('/create_flights', methods=['GET', 'POST'])
def create_flights():
    return render_template("airline_staff_createflights.html")

@app.route('/create flights', methods=['GET', 'POST'])
def creation():
    airline = request.form['airline_name']
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
    query = 'SELECT * FROM flight where flight_num = %s;'
    try:
        cursor.execute(query, (flight_num))
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
        ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (airline.lower(), flight_num, departure_airport.lower(), departure_time, arrival_airport.lower(), arrival_time, price, status.lower(), airplane_id))
        conn.commit()
        cursor.close()
        success = "you have successfully created a new flight"
        return render_template('airline_staff_createflights.html', success = success)

@app.route('/change_flight_status', methods=['GET', 'POST'])
def change():
    return render_template("change_status.html")
@app.route('/changestatus', methods=['GET', 'POST'])
def change_status():
    flight_num = request.form['flight_num']
    status = request.form['status']
    cursor = conn.cursor()
    query = 'SELECT flight_num FROM flight where flight_num = %s'
    cursor.execute(query, (flight_num))
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
    airline = request.form['airline_name']
    airplane_id = request.form['airplane_id']
    seats = request.form['number_of_seats']
    cursor = conn.cursor()
    #executes query
    try:
        query = 'SELECT * FROM airplane where airline_name = %s;'
        cursor.execute(query, (airline.lower()))
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
        cursor.execute(ins, (airline.lower(), airplane_id, seats))
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

    query2 = 'SELECT customer_email, COUNT(*) as c FROM purchases natural join ticket natural join flight where airline_name = %s GROUP BY customer_email ORDER BY c DESC LIMIT 1;'
    cursor.execute(query2, (airlinename))
    data2 = cursor.fetchone()
    #stores the results in a variable
    #use fetchall() if you are expecting more than 1 data row
    f = data2['customer_email']
    return render_template('view_customer.html', customer=f)

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
        dicty[i+1] = 'Airline name: {}, Flight number: {}, Departure airport: {}, Departure time: {}, Arrival airport: {}, Arrival time: {}, Price: {}, Airplane id: {}'.format(data[i]['airline_name'], data[i]['flight_num'], data[i]['departure_airport'], data[i]['departure_time'], data[i]['arrival_airport'], data[i]['arrival_time'], data[i]['price'], data[i]['airplane_id'])
    return dicty;

@app.route('/view_dest', methods=['GET', 'POST'])
def viewdest():
    return render_template('viewdest.html')

@app.route('/view_dest_1yr', methods=['GET', 'POST'])
def viewdest1yr():
    session_key = session.get('username')
    cursor = conn.cursor()
    #executes query
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query2 = 'SELECT airport_city, COUNT(*) as c FROM airport natural join flight natural join ticket NATURAL JOIN purchases where airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 YEAR) GROUP BY airport_city ORDER BY c DESC LIMIT 3;'
    cursor.execute(query2, (airlinename))
    data2 = cursor.fetchall()
    dicty = {}
    for i in range(len(data2)):
        dicty[i] = "most popular destination number {} is {}".format(i+1, data2[i]['airport_city'])
    return dicty

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
        dicty[i] = "most popular destination number {} is {}".format(i+1, data2[i]['airport_city'])
    return dicty

@app.route('/revenue_comparison', methods = ['GET', 'POST'])
def revenue_c():
    return render_template("revenue_choice.html")

@app.route('/one_year', methods = ['GET', 'POST'])
def monthly():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 3 MONTH);'
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
    return render_template('report_piechart.html', title='Revenue earned within the past year', max=17000, set=zip(values, labels, colors))

@app.route('/month_bar', methods = ['GET', 'POST'])
def yearly():
    session_key = session.get('username')
    cursor = conn.cursor()
    query1 = 'SELECT distinct(airline_name) FROM airline_staff WHERE username = %s;'
    cursor.execute(query1, (session_key.lower()))
    data = cursor.fetchone()
    airlinename = data['airline_name']
    query = 'SELECT MONTH(purchase_date) AS month, price FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE MONTH(purchase_date) = %s AND airline_name = %s AND purchase_date > DATE_SUB(NOW(), INTERVAL 1 MONTH);'
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
    return render_template('report_piechart.html', title='Revenue earned within the past year', max=17000, set=zip(values, labels, colors))

@app.route('/staff_view_reports', methods = ['GET', 'POST'])
def viewreptyp():
    return render_template('reporttyp.html')
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
def monthie():
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
    for i in range(1, 12):
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

@app.route('/searchFlight', methods=['GET', 'POST'])
def search_flights():
    return render_template('search_flight.html')

@app.route('/viewFlights', methods=['GET', 'POST'])
def view_flights():
    cursor = conn.cursor()
    query = 'SELECT flight_num, departure_time, arrival_time, status FROM flight'
    cursor.execute(query)
    data=cursor.fetchall()
    dicty = {}
    if (data):
        for i in range(len(data)):
            dicty[i] = 'flight_num = {}  ,   departure_time = {}    ,   arrival_time = {},    status = {}'.format(data[i]['flight_num'], data[i]['departure_time'], data[i]['arrival_time'], data[i]['status'])
    return dicty

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
        for i in data:
            return 'flight number {}, upcoming,  departs on {},  departs from {}  arrive on {}, arrives at {} '.format(data['flight_num'], data['departure_time'], airportsource, data['arrival_time'], airportdestination)
    else:
        error = "please enter proper source and destination values"
        return render_template('login_success_customer.html', error = error)

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
            dicty[count] = "flight number {},  departs from {},  departure_time {},  arrives to {},  arrival time {},  flight number = {}, ticket_id = {}".format(count + 1,  data[count]['departure_airport'],  data[count]['departure_time'], data[count]['arrival_airport'], data[count]['arrival_time'], data[count]['flight_num'], data[count]['ticket_id'] )
            count+=1
            print('\n')
        return dicty

    else:
        return "please purchase a ticket first"
        return render_template("login_success_customer.html")

    return rows

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
