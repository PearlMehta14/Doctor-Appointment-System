import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictRow
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Detect if we are on Render (PostgreSQL) or Local (SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # PostgreSQL for Render
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # SQLite for Local Development
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
        DB_PATH = os.path.join(app.instance_path, 'doctor_appointment.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = get_db_connection()
    if DATABASE_URL:
        # Postgres uses %s
        query = query.replace('?', '%s').replace('AUTOINCREMENT', '')
        cur = conn.cursor(cursor_factory=RealDictRow)
    else:
        # SQLite uses ?
        cur = conn.cursor()
    
    cur.execute(query, params)
    
    result = None
    if fetchone:
        result = cur.fetchone()
    elif fetchall:
        result = cur.fetchall()
    
    if not (fetchone or fetchall):
        conn.commit()
    
    conn.close()
    return result

def init_db():
    # usertable
    execute_query('''
        CREATE TABLE IF NOT EXISTS usertable (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # doctorlogin
    execute_query('''
        CREATE TABLE IF NOT EXISTS doctorlogin (
            id SERIAL PRIMARY KEY,
            Email TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL
        )
    ''')
    # contact
    execute_query('''
        CREATE TABLE IF NOT EXISTS contact (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    # app (appointments)
    execute_query('''
        CREATE TABLE IF NOT EXISTS app (
            Sno SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            address TEXT,
            phone TEXT,
            time TEXT,
            date TEXT,
            msg TEXT,
            status TEXT DEFAULT 'Confirmed'
        )
    ''')
    
    # Check if status column exists (only for SQLite migration, Postgres will have it from CREATE)
    if not DATABASE_URL:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(app)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute("ALTER TABLE app ADD COLUMN status TEXT DEFAULT 'Confirmed'")
        conn.commit()
        conn.close()

    # Default Doctor
    doctor = execute_query('SELECT * FROM doctorlogin WHERE Email = ?', ('doctor@example.com',), fetchone=True)
    if not doctor:
        hashed_password = generate_password_hash('password123')
        execute_query('INSERT INTO doctorlogin (Email, Password) VALUES (?, ?)', ('doctor@example.com', hashed_password))
    
    # Test Patient
    patient = execute_query('SELECT * FROM usertable WHERE email = ?', ('patient@example.com',), fetchone=True)
    if not patient:
        hashed_password = generate_password_hash('patient123')
        execute_query('INSERT INTO usertable (email, password) VALUES (?, ?)', ('patient@example.com', hashed_password))
        today = datetime.now().strftime('%Y-%m-%d')
        execute_query("INSERT INTO app (name, age, address, phone, time, date, msg, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       ('John Doe', 30, '123 Test St', '555-0199', '10:00', today, 'patient@example.com', 'Confirmed'))

init_db()

@app.route("/")
def main():
    if 'loggedin' in session:
        return redirect(url_for('m'))
    return render_template('index.html')

@app.route("/home.html")
def m():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route("/api/upcoming_appointments")
def upcoming_appointments():
    if 'loggedin' not in session or 'email' not in session:
        return {"appointments": []}
    
    today = datetime.now().strftime('%Y-%m-%d')
    appointments = execute_query("SELECT Sno, time, date, status FROM app WHERE msg = ? AND date = ? AND status = 'Confirmed'", 
                                 (session['email'], today), fetchall=True)
    
    upcoming = []
    now = datetime.now()
    for appt in appointments:
        try:
            appt_time = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
            diff = (appt_time - now).total_seconds() / 60
            if 0 < diff <= 15:
                upcoming.append({"time": appt['time'], "id": appt['Sno'] if DATABASE_URL else appt['Sno']})
        except:
            continue
            
    return {"appointments": upcoming}

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route("/contactus.html", methods=['GET','POST'])
def submit_review():
    if request.method == 'POST':
        email = request.form['email']
        rating = request.form['message']
        execute_query("INSERT INTO contact (email, message) VALUES (?, ?)", (email, rating))
        return render_template('contactus.html', msg="Feedback received!")
    return render_template('contactus.html')

@app.route("/login.html", methods=['GET', 'POST'])
def logindr():
    if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        email = request.form['Email']
        password = request.form['Password']
        account = execute_query('SELECT * FROM doctorlogin WHERE Email = ?', (email,), fetchone=True)
        if account and check_password_hash(account['Password' if DATABASE_URL else 'Password'], password):
            session['loggedin'] = True
            session['Email'] = account['Email' if DATABASE_URL else 'Email']
            session['role'] = 'doctor'
            return redirect(url_for('doctor_dashboard'))
        else:
            msg = 'Incorrect email/password!'
            return render_template('login.html', msg=msg)
    return render_template('login.html')

@app.route('/singup.html', methods=['GET', 'POST'])
def signupdr():
    if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        email = request.form['Email']
        password = generate_password_hash(request.form['Password'])
        account = execute_query('SELECT * FROM doctorlogin WHERE Email = ?', (email,), fetchone=True)
        if account:
            msg = 'Account already exists!'
            return render_template('singup.html', msg=msg)
        else:
            execute_query('INSERT INTO doctorlogin (Email, Password) VALUES (?, ?)', (email, password))
            return redirect(url_for('logindr'))
    return render_template('singup.html')

@app.route('/confirmation.html')
def confirmation():
    if 'loggedin' not in session: return redirect(url_for('login'))
    try:
        appointments = execute_query("SELECT * FROM app WHERE msg = ? ORDER BY date DESC, time DESC", (session.get('email'),), fetchall=True)
        return render_template('confirmation.html', appointments=appointments)
    except Exception as e:
        return str(e)

@app.route('/cancel_appointment/<int:sno>')
def cancel_appointment(sno):
    if 'loggedin' not in session: return redirect(url_for('login'))
    execute_query("UPDATE app SET status = 'Cancelled' WHERE Sno = ? AND msg = ?", (sno, session.get('email')))
    return redirect(url_for('confirmation'))

@app.route('/drdash.html')
def doctor_dashboard():
    if session.get('role') != 'doctor': return redirect(url_for('logindr'))
    try:
        appointments = execute_query("SELECT * FROM app WHERE status = 'Confirmed' ORDER BY date, time", fetchall=True)
        return render_template('drdash.html', appointments=appointments)
    except Exception as e:
        return str(e)

@app.route('/patients.html')
def patients():
    if session.get('role') != 'doctor': return redirect(url_for('logindr'))
    search_query = request.args.get('search', '')
    try:
        if search_query:
            query = "SELECT Sno, name, phone, status FROM app WHERE (name LIKE ? OR phone LIKE ?) ORDER BY name"
            appointments = execute_query(query, (f'%{search_query}%', f'%{search_query}%'), fetchall=True)
        else:
            appointments = execute_query("SELECT Sno, name, phone, status FROM app ORDER BY name", fetchall=True)
        return render_template('patients.html', appointments=appointments, search_query=search_query)
    except Exception as e:
        return render_template('patients.html', appointments=[], error=str(e))

@app.route("/consultation.html", methods=['GET', 'POST'])
def consultation():
    if 'loggedin' not in session: return redirect(url_for('login'))
    today_str = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        name = request.form.get('Name')
        age = request.form.get('Age')
        address = request.form.get('Address')
        phone = request.form.get('Phone')
        time = request.form.get('time')
        date = request.form.get('date')
        message = request.form.get('msg')
        
        now = datetime.now()
        selected_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        if selected_datetime < now:
            return "<script>alert('Invalid Date/Time. Please select a future slot.'); window.history.back();</script>"

        result = execute_query("SELECT * FROM app WHERE date = ? AND time = ? AND status = 'Confirmed'", (date, time), fetchone=True)
        if result:
            return "<script>alert('Sorry, this time slot is already reserved.'); window.history.back();</script>"
        else:
            execute_query("INSERT INTO app (name, age, address, phone, time, date, msg, status) VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed')",
                           (name, age, address, phone, time, date, message))
            return redirect(url_for('confirmation'))
    return render_template('consultation.html', today=today_str)

@app.route("/timeslot.html")
def ts():
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    is_sunday = datetime.strptime(selected_date, '%Y-%m-%d').weekday() == 6
    rows = execute_query("SELECT time FROM app WHERE date = ? AND status = 'Confirmed'", (selected_date,), fetchall=True)
    booked_slots = [row['time'] for row in rows]
    return render_template("timeslot.html", booked_slots=booked_slots, selected_date=selected_date, is_sunday=is_sunday)

@app.route("/loginp.html", methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        account = execute_query('SELECT * FROM usertable WHERE email = ?', (email,), fetchone=True)
        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['email'] = account['email']
            return redirect(url_for('m'))
        else:
            msg = 'Incorrect email/password!'
            return render_template('loginp.html', msg=msg)
    return render_template('loginp.html')

@app.route('/singuppt.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        account = execute_query('SELECT * FROM usertable WHERE email = ?', (email,), fetchone=True)
        if account:
            msg = 'Account already exists!'
            return render_template('singuppt.html', msg=msg)
        else:
            execute_query('INSERT INTO usertable (email, password) VALUES (?, ?)', (email, password))
            return redirect(url_for('login'))
    return render_template('singuppt.html')

@app.route("/about.html")
def abt(): return render_template("about.html")

@app.route("/index.html")
def i(): return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)


