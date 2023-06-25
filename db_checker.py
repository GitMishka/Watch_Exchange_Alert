import psycopg2
import config
import csv

def get_db_connection():
    conn = psycopg2.connect(
        host=config.pg_host,
        database=config.pg_database,
        user=config.pg_user,
        password=config.pg_password
    )
    return conn

def check_quality():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_newposts WHERE id IS NULL;")
    rows = cur.fetchall()

    if rows:
        with open('deleted_rows.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "post_time", "url", "price", "keyterm"])  
            writer.writerows(rows)  

        cur.execute("DELETE FROM search_newposts WHERE id IS NULL;")
        conn.commit()

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_quality()
