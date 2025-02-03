import psycopg2
import psycopg2.extras

DBUSER = "group1"
DBPASS = "group1"

def connect_db():
  conn = psycopg2.connect(host="dbclass.rhodescs.org",
                        user=DBUSER,
                        password=DBPASS,
                        dbname="group1",
                        cursor_factory=psycopg2.extras.DictCursor)
  return conn