from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'microfinance-secret-key-2026')
DB = 'microfinance.db'


def open_db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    c = open_db()
    c.execute('CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, village TEXT, amount REAL, due_date TEXT, status TEXT, outstanding REAL, last_payment_date TEXT, days_overdue INTEGER)')

    columns = [row['name'] for row in c.execute('PRAGMA table_info(loans)').fetchall()]
    required_columns = ['id', 'name', 'phone', 'village', 'amount', 'due_date', 'status', 'outstanding', 'last_payment_date', 'days_overdue']

    if not columns or any(col not in columns for col in required_columns):
        if 'last_payment_date' not in columns:
            c.execute('ALTER TABLE loans ADD COLUMN last_payment_date TEXT')
        if 'days_overdue' not in columns:
            c.execute('ALTER TABLE loans ADD COLUMN days_overdue INTEGER')
        if any(col not in columns for col in ['id', 'name', 'phone', 'village', 'amount', 'due_date', 'status', 'outstanding']):
            c.execute('DROP TABLE IF EXISTS loans')
            c.execute('CREATE TABLE loans (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, village TEXT, amount REAL, due_date TEXT, status TEXT, outstanding REAL, last_payment_date TEXT, days_overdue INTEGER)')

    if c.execute('SELECT COUNT(*) FROM loans').fetchone()[0] == 0:
        c.executemany('INSERT INTO loans (name, phone, village, amount, due_date, status, outstanding, last_payment_date, days_overdue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', [
            ('Ravi Kumar', '9876543210', 'Karnal', 50000, '2026-09-10', 'Active', 42000, '2026-08-01', 0),
            ('Meena Devi', '9123456780', 'Panipat', 75000, '2026-10-15', 'Active', 61000, '2026-07-30', 5),
            ('Amit Singh', '9988776655', 'Hisar', 120000, '2026-08-20', 'NPA', 98000, '2026-06-25', 12),
            ('Sonia Rani', '9765432109', 'Faridabad', 90000, '2026-11-11', 'Closed', 0, '2026-08-05', 0)
        ])
    c.commit(); c.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        error = 'Invalid username or password.'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    show_details = request.args.get('show_details') == '1'
    status_filter = request.args.get('status_filter', '')
    village_filter = request.args.get('village_filter', '')

    c = open_db()
    data = {
        'total': c.execute('SELECT COUNT(*) FROM loans').fetchone()[0],
        'portfolio': c.execute('SELECT COALESCE(SUM(amount), 0) FROM loans').fetchone()[0],
        'outstanding': c.execute('SELECT COALESCE(SUM(outstanding), 0) FROM loans').fetchone()[0],
        'npa': c.execute('SELECT COUNT(*) FROM loans WHERE status = "NPA"').fetchone()[0]
    }

    query = 'SELECT * FROM loans WHERE 1=1'
    params = []
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    if village_filter:
        query += ' AND village = ?'
        params.append(village_filter)
    query += ' ORDER BY id DESC'

    loans = c.execute(query, params).fetchall()
    status_counts = c.execute('SELECT status, COUNT(*) AS total FROM loans GROUP BY status').fetchall()
    village_counts = c.execute('SELECT village, COUNT(*) AS total FROM loans WHERE village IS NOT NULL AND village != "" GROUP BY village ORDER BY total DESC LIMIT 5').fetchall()
    village_names = [row['village'] for row in c.execute('SELECT DISTINCT village FROM loans WHERE village IS NOT NULL AND village != "" ORDER BY village').fetchall()]
    c.close()

    status_list = [
        {'name': 'Active', 'value': next((row['total'] for row in status_counts if row['status'] == 'Active'), 0)},
        {'name': 'NPA', 'value': next((row['total'] for row in status_counts if row['status'] == 'NPA'), 0)},
        {'name': 'Closed', 'value': next((row['total'] for row in status_counts if row['status'] == 'Closed'), 0)}
    ]

    max_village_count = max((row['total'] for row in village_counts), default=1)
    village_chart = [
        {'name': row['village'], 'value': row['total'], 'height': max(18, int((row['total'] / max_village_count) * 100))}
        for row in village_counts
    ]

    return render_template(
        'index.html',
        data=data,
        loans=loans,
        show_details=show_details,
        status_filter=status_filter,
        village_filter=village_filter,
        villages=village_names,
        status_list=status_list,
        village_chart=village_chart,
    )


@app.route('/add', methods=['POST'])
def add():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    name = request.form['name']
    phone = request.form['phone']
    village = request.form['village']
    amount = float(request.form['amount'])
    months = int(request.form['months'])
    if name and amount > 0:
        c = open_db()
        c.execute('INSERT INTO loans (name, phone, village, amount, due_date, status, outstanding) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (name, phone, village, amount, (date.today() + timedelta(days=30 * months)).strftime('%Y-%m-%d'), 'Active', amount))
        c.commit(); c.close()
    return redirect(url_for('home', show_details='1'))


@app.route('/pay', methods=['POST'])
def pay():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    last_payment_date = request.form.get('last_payment_date')
    due_date = request.form.get('due_date')
    days_overdue = request.form.get('days_overdue')
    status = request.form.get('status')

    c = open_db()
    loan = c.execute('SELECT * FROM loans ORDER BY id DESC LIMIT 1').fetchone()
    if loan:
        updated_due_date = due_date or loan['due_date']
        updated_status = status or loan['status']
        updated_last_payment = last_payment_date or loan['last_payment_date']
        updated_overdue = int(days_overdue) if days_overdue else (loan['days_overdue'] or 0)
        c.execute(
            'UPDATE loans SET last_payment_date = ?, due_date = ?, days_overdue = ?, status = ? WHERE id = ?',
            (updated_last_payment, updated_due_date, updated_overdue, updated_status, loan['id'])
        )
    c.commit(); c.close()
    return redirect(url_for('home', show_details='1'))


@app.route('/powerbi-export')
def powerbi_export():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    csv_path = Path(__file__).resolve().parent / 'powerbi_sample_data.csv'
    return send_file(csv_path, as_attachment=True, download_name='powerbi_sample_data.csv')


if __name__ == '__main__':
    init()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
