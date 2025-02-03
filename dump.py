from connectdb import connect_db
##note, before running populate, run createtables to get fresh tables
DBUSER = "group1"
DBPASS = "group1"
##todo: populate users and cookbooks


def dump_table_cuisine_gear(table_name):
  conn = connect_db()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM " + table_name)
  rows = cursor.fetchall()
  print("Here is info from " + table_name)
  for row in rows:
    print("name:", row[0])
  conn.close()


def dump_users():
  conn = connect_db()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM Users")
  rows = cursor.fetchall()
  print("Here is info from Users")
  for row in rows:
    print("id:", row[0], "name:", row[1])
  conn.close()
