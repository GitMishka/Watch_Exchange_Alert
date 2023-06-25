import praw
from tabulate import tabulate
from datetime import datetime
from twilio.rest import Client
import psycopg2
import time
import config
while True:
  try:
    conn = psycopg2.connect(
    host=config.pg_host,
    database=config.pg_database,
    user=config.pg_user,
    password=config.pg_password
)
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS search_newposts (id TEXT PRIMARY KEY, title TEXT, post_time TIMESTAMP, url TEXT, price FLOAT, keyterm TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS search_texted (id TEXT PRIMARY KEY, title TEXT, post_time TIMESTAMP, url TEXT, price FLOAT, keyterm TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS search_terms (id TEXT PRIMARY KEY,term TEXT,subreddit TEXT,post_time TIMESTAMP)")
    
    account_sid = config.twilio_account_sid
    auth_token = config.twilio_auth_token
    
    client = Client(account_sid, auth_token)

    user_agent = "Searchbot_01"
    reddit = praw.Reddit(username=config.reddit_username,
                        password =config.reddit_password,
                        client_id=config.reddit_client_id,
                        client_secret=config.reddit_client_secret,
                        user_agent=user_agent,
                        check_for_async=False)
    subreddit = reddit.subreddit('watchexchange')
    posts = subreddit.new(limit=10)

    cur.execute("SELECT term FROM search_terms WHERE subreddit = %s", (str(subreddit),))
    search_terms = [item[0] for item in cur.fetchall()]

    keyterm_list = ['A. Lange & Sohne', 'Alpina', 'Armani Exchange', 'Audemars Piguet', 
                    'Ball', 'Baume et Mercier', 'Bell & Ross', 'Blancpain', 'Breguet', 'Breitling', 
                    'Bremont', 'Bulova', 'Bvlgari', 'Cartier', 'Certina', 'Chanel', 'Chopard', 'Citizen', 
                    'Corum', 'Daniel Wellington', 'De Bethune', 'Doxa', 'Ebel', 'Eberhard & Co.', 
                    'F.P. Journe', 'Fossil', 'Frederique Constant', 'Girard-Perregaux', 'Glashütte Original', 
                    'G-Shock', 'Hamilton', 'Harry Winston', 'Hermes', 'Hublot', 'IWC', 'Jaeger-LeCoultre', 'Junghans', 
                    'Laco', 'Longines', 'Maurice Lacroix', 'MeisterSinger', 'Montblanc', 'Movado', 'Nomos Glashütte', 'Omega', 
                    'Oris', 'Panerai', 'Parmigiani Fleurier', 'Patek Philippe', 'Piaget', 'Rado', 'Raymond Weil', 'Richard Mille', 
                    'Rolex', 'Seiko', 'Shinola', 'Sinn', 'Tag Heuer', 'Tissot', 'Tudor', 'Ulysse Nardin', 'Vacheron Constantin', 
                    'Victorinox Swiss Army', 'Zenith']

    for post in posts:
        post_id = post.id
        post_name = post.title.lower()
        post_time = datetime.utcfromtimestamp(post.created_utc)
        url = post.url
        price_str = post_name.split("$")[-1].split()[0]
        try:
            price = float(price_str.replace("k", "000").replace("K", "000").replace(".", ""))
        except ValueError:
            price = None
        keyterm = None
        for keyterm_name in keyterm_list:
            if keyterm_name.lower() in post_name:
                keyterm = keyterm_name
                break
        
        cur.execute("SELECT id FROM search_newposts WHERE id=%s", (post_id,))
        existing_post = cur.fetchone()
        if existing_post:
            continue
        
        cur.execute("INSERT INTO search_newposts (id, title, post_time, url, price, keyterm) VALUES (%s, %s, %s, %s, %s, %s)",
                    (post_id, post_name, post_time, url, price, keyterm))
        conn.commit()
        
        if any(term in post_name for term in search_terms):
            cur.execute("SELECT id FROM search_texted WHERE id=%s", (post_id,))
            texted_post = cur.fetchone()
            
            if not texted_post:
                message_body = f"keyterm: {keyterm}\nTime: {post_time}\nLink: {url}"
                message = client.messages.create(
                    to=config.twilio_to_number,
                    from_='18334633894',
                    body=message_body
                )
                
                cur.execute("INSERT INTO search_texted (id, title, post_time, url, price, keyterm) VALUES (%s, %s, %s, %s, %s, %s)",
                            (post_id, post_name, post_time, url, price, keyterm))
                conn.commit()
  except Exception as e:
      print(f"An error occurred: {e}")

  time.sleep(10)


