from flask import Flask, render_template, request
import psycopg2
import config
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        id = request.form.get('id')
        term = request.form.get('term')
        subreddit = request.form.get('subreddit')
        post_time = datetime.now()  # Automatically get current date and time
        add_entry(id, term, subreddit, post_time)
        return 'Entry added!'
    return render_template('form.html')  # You need to create form.html in templates folder

def add_entry(id, term, subreddit, post_time):
    conn = psycopg2.connect(
        host=config.pg_host,
        database=config.pg_database,
        user=config.pg_user,
        password=config.pg_password
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO termlog (id, term, subreddit, post_time) VALUES (%s, %s, %s, %s)", 
                (id, term, subreddit, post_time))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    app.run(debug=True)
