from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import config
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.secret_key = 'test1' 

def get_db_connection():
    conn = psycopg2.connect(
        host=config.pg_host,
        database=config.pg_database,
        user=config.pg_user,
        password=config.pg_password
    )
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form.get('id')
        username = request.form.get('username')
        password = request.form.get('password')

        if verify_credentials(id, username, password):
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials!'

    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'Add':
            return redirect(url_for('add_entry'))
        elif action == 'Edit':
            return redirect(url_for('edit_entry'))
        elif action == 'Delete':
            return redirect(url_for('delete_entry'))
        elif action == 'View':
            return redirect(url_for('view_entries'))

    return render_template('home.html') 

@app.route('/view', methods=['GET'])
def view_entries():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    entries = fetch_db()
    return render_template('view.html', entries=entries)


def fetch_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM termlog")
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return entries

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        id = request.form.get('id')
        term = request.form.get('term')
        subreddit = request.form.get('subreddit')
        post_time = datetime.now()
        insert_db(id, term, subreddit, post_time)
        return 'Entry added!'
    return render_template('add.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit_entry():
    if request.method == 'POST':
        id = request.form.get('id')
        term = request.form.get('term')
        subreddit = request.form.get('subreddit')
        update_db(id, term, subreddit)
        return 'Entry updated!'
    return render_template('edit.html')  

@app.route('/delete', methods=['GET', 'POST'])
def delete_entry():
    if request.method == 'POST':
        id = request.form.get('id')
        delete_db(id)
        return 'Entry deleted!'
    return render_template('delete.html') 
def get_db_connection():
    return psycopg2.connect(
        host=config.pg_host,
        database=config.pg_database,
        user=config.pg_user,
        password=config.pg_password
    )

def insert_db(id, term, subreddit, post_time):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO termlog (id, term, subreddit, post_time) VALUES (%s, %s, %s, %s)",
                (id, term, subreddit, post_time))
    conn.commit()
    cur.close()
    conn.close()

def update_db(id, term, subreddit):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE termlog SET term = %s, subreddit = %s WHERE id = %s",
                (term, subreddit, id))
    conn.commit()
    cur.close()
    conn.close()

def delete_db(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM termlog WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()

def verify_credentials(id, username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM login_cred WHERE id = %s AND username = %s", (id, username))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result is not None:
        hashed_password = result[0]
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    else:
        return False

def fetch_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM termlog")
    entries = cur.fetchall()
    cur.close()
    conn.close()
    return entries

if __name__ == "__main__":
    app.run(debug=True)
