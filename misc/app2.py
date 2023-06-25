from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import config
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
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

if __name__ == "__main__":
    app.run(debug=True)
