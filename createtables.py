import psycopg2

DBUSER = "group1"
DBPASS = "group1"

conn = psycopg2.connect(host="dbclass.rhodescs.org",
                        user=DBUSER,
                        password=DBPASS,
                        dbname="group1")
cur = conn.cursor()
with open("schema.sql", "r") as file:
    alltext = file.read()  # read all the text
cur.execute(alltext)  # execute all the SQL in the file
conn.commit()  # Actually make the changes to the db

cur.close()
conn.close()  # close everything
