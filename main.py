# Blog Flask application

import psycopg2
import psycopg2.extras
from flask import (
    Flask,
    current_app,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

DBPASS = "group1"
DBUSER = "group1"

DEBUG = True

# initialize Flask
### Make the flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key'


### Routes
@app.route("/")
def index():
  return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    pwd = request.form['password']
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name, password from Users where name = %s",
                (username, ))
    user = cur.fetchone()
    cur.close()

    if user and pwd == user[1]:
      session['username'] = user[0]
      return redirect(url_for('home'))
    else:
      return render_template('login.html',
                             error='Invalid username or password')

  return render_template('login.html')


@app.route("/ingredients", methods=['GET', 'POST'])
def ingredients():
  conn = get_db()
  cur = conn.cursor()
  if request.method == 'POST' and request.form.get(
      "step") == "view_ingredient":
    postid = int(request.form["postid"])
    query = '''select * from ingredients where ingredient_id = %s'''
    cur.execute(query, [postid])
    row = cur.fetchone()
    return render_template("ingredients.html",
                           step="view_ingredient",
                           ingredient=row,
                           ingredients=[])
  else:
    search_query = request.form.get('search', '')
    if search_query:
      query = '''select * from ingredients where ingredient_name ilike %s'''
      cur.execute(query, [f'%{search_query}%'])
      ingredients = cur.fetchall()
    else:
      query = '''select * from ingredients'''
      cur.execute(query)
      ingredients = cur.fetchall()

  if request.method == 'POST' and request.form.get('ajax'):
    return render_template('ingredients_results.html',
                           ingredients=ingredients,
                           step="display_ingredients")
  else:
    return render_template('ingredients.html',
                           ingredients=ingredients,
                           step="display_ingredients")


@app.route("/register", methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    pwd = request.form['password']
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE name = %s", (username, ))
    existing_user = cur.fetchone()
    if existing_user:
      # User already exists, render register.html with error message
      return render_template('register.html', error='User already exists')

    cur.execute(
        f"insert into Users (name, password) values ('{username}', '{pwd}')")
    conn.commit()
    cur.close()

    return redirect(url_for('login'))

  return render_template('register.html')


@app.route("/add_recipe", methods=['GET', 'POST'])
def add_recipe():

  if "step" not in request.form:
    return render_template('add_recipe.html', step="compose_entry")

  elif request.form["step"] == "add_entry":
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into recipes (name, instructions) values (%s, %s) RETURNING recipe_id",
        [request.form['name'], request.form['instructions']])
    conn.commit()
    recipe_id = cursor.fetchone()[0]

    cuisine_name = request.form['cuisine']
    cursor.execute("SELECT 1 FROM cuisine WHERE cuisine_name = %s", (cuisine_name,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO cuisine (cuisine_name) VALUES (%s)", (cuisine_name,))
    cursor.execute(
        "insert into recipe_to_cuisine (recipe_id, cuisine_name) values (%s, %s)",
        [recipe_id, request.form['cuisine']])
    conn.commit()

    cursor.execute("select gear_name from cooking_gear")
    gear = cursor.fetchall()
    for cookgear in request.form["cookware"].split(","):
      if cookgear not in [gear[i][0] for i in range(len(gear))]:
        cookware_query = '''insert into cooking_gear (gear_name) values (%s)'''
        cursor.execute(cookware_query, (cookgear, ))
        conn.commit()
      else:
        pass

      query = '''insert into recipe_uses_cookware (recipe_id, gear_name) values (%s,%s)'''
      cursor.execute(query, [recipe_id, cookgear])
      conn.commit()

    for ingredient in request.form["ingredients"].split(","):
      query = '''insert into list_ingredients_recipe (recipe_id, ingredient) values (%s, %s)'''
      cursor.execute(query, [recipe_id, ingredient])
      conn.commit()

    return render_template("add_recipe.html", step="add_entry")


@app.route("/logout")
def logout():
  session.pop('username', None)
  return redirect(url_for('index'))


@app.route("/home")
def home():
  if 'username' in session:
    return render_template('home.html', username=session['username'])
  else:
    return redirect(url_for('index'))


@app.route("/recipes", methods=['get', 'post'])
def recipes():
  #get recipes to pass into template
  if "step" not in request.form:
    conn = connect_db()
    cur = conn.cursor()
    search_query = request.args.get('search', '')

    if search_query:
      query = '''select * from main_list where name ilike %s'''
      cur.execute(query, ['%' + search_query + '%'])
    else:
      query = '''select * from main_list'''
      cur.execute(query)

    recipes = cur.fetchall()

    if request.method == 'GET' and request.args.get('ajax'):
      return render_template('recipes_results.html',
                             recipes=recipes,
                             step="display_recipes")
    else:
      return render_template('recipes.html',
                             recipes=recipes,
                             step="display_recipes",
                             search_query=search_query)

  elif request.form["step"] == "view_recipe":
    conn = get_db()
    cursor = conn.cursor()
    # get the postID from the form
    postid = int(request.form["postid"])
    debug("Using postid=" + str(postid))

    # query the DB to retrieve that post by ID.  We use fetchone()
    # to retrieve the only row (there can be only one!)
    query = '''select * from main_list where recipe_id = %s'''
    cursor.execute(query, [postid])
    row = cursor.fetchone()

    return render_template("recipes.html", step="view_recipe", recipe=row)

  elif request.form["step"] == "choose_cookbook":
    conn = get_db()
    cur = conn.cursor()

    recipe_id = int(request.form["postid"])
    debug("Using postid=" + str(recipe_id))

    query = '''select * from viewable_recipes where recipe_id = %s'''
    cur.execute(query, [recipe_id])
    row = cur.fetchone()

    find_user_query = '''select user_id from users where name = %s'''
    cur.execute(find_user_query, [session['username']])
    find_user_id = cur.fetchone()[0]

    cookbook_query = '''select * from cookbooks 
    where cookbook_id in 
    (select cookbook_id from cookbooks_usedby_user 
     where user_id = %s)'''
    cur.execute(cookbook_query, [find_user_id])
    cookbooks = cur.fetchall()

    return render_template("recipes.html",
                           step="choose_cookbook",
                           cookbooks=cookbooks,
                           recipe=row)

  elif request.form["step"] == 'add_recipe':
    conn = get_db()
    cur = conn.cursor()

    cookbook_id = int(request.form["cookbook_id"])
    recipe_id = int(request.form["postid"])

    debug("Using cookbook_id=" + str(cookbook_id) + " and recipe_id=" +
          str(recipe_id))

    query = '''insert into cookbook_to_recipe (cookbook_id, recipe_id) values (%s, %s)'''
    cur.execute(query, [cookbook_id, recipe_id])
    conn.commit()
    conn.close()

    return render_template("recipes.html", step="add_recipe")


@app.route("/cookbook", methods=['get', 'post'])
def cookbook():

  if "step" not in request.form:

    conn = connect_db()
    cur = conn.cursor()

    find_user_query = '''select user_id from users where name = %s'''
    cur.execute(find_user_query, [session['username']])
    find_user_id = cur.fetchone()[0]

    cookbook_query = '''select * from cookbooks 
    where cookbook_id in 
    (select cookbook_id from cookbooks_usedby_user 
     where user_id = %s)'''
    cur.execute(cookbook_query, [find_user_id])
    cookbooks = cur.fetchall()

    return render_template('cookbook.html', cookbooks=cookbooks)

  elif request.form["step"] == "view_cookbook":
    conn = connect_db()
    cur = conn.cursor()

    cookbook_id = int(request.form["postid"])

    query = '''select * from cookbooks where cookbook_id = %s'''
    cur.execute(query, (cookbook_id, ))
    cookbook = cur.fetchone()

    recipe_query = '''select recipe_id from cookbook_to_recipe where cookbook_id = %s'''
    cur.execute(recipe_query, (cookbook_id, ))
    recipe_ids = cur.fetchall()
    entries = []

    for id in recipe_ids:
      query_recipe_name = '''select recipe_id, name from recipes where recipe_id = %s'''
      cur.execute(query_recipe_name, [id[0]])
      entries += cur.fetchall()
    return render_template('cookbook.html',
                           step="view_cookbook",
                           cookbook=cookbook,
                           entries=entries)

  elif request.form["step"] == "view_recipe":
    conn = get_db()
    cursor = conn.cursor()
    # get the postID from the form
    postid = int(request.form["postid"])
    debug("Using postid=" + str(postid))

    # query the DB to retrieve that post by ID.  We use fetchone()
    # to retrieve the only row (there can be only one!)
    query = '''select * from main_list where recipe_id = %s'''
    cursor.execute(query, [postid])
    row = cursor.fetchone()
    return render_template("recipes.html", step="view_recipe", recipe=row)


@app.route("/create_cookbook", methods=['get', 'post'])
def create_cookbook():
  # Step 1, display form
  if "step" not in request.form:
    return render_template('create_cookbook.html', step="compose_entry")

  # Step 2, add blog post to database.
  elif request.form["step"] == "add_entry":
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "insert into cookbooks (cookbook_name) values (%s) RETURNING cookbook_id",
        [request.form['title']])
    conn.commit()
    user_cookbook_id = cursor.fetchone()[0]

    user_query = '''select user_id from users where name = %s'''
    cursor.execute(user_query, [session['username']])
    insert_user_id = cursor.fetchone()[0]

    cookbook_query = '''select cookbook_id from cookbooks where cookbook_id = %s'''
    cursor.execute(cookbook_query, (user_cookbook_id, ))

    cursor.execute(
        '''
      insert into cookbooks_usedby_user (cookbook_id, user_id)
      values (%s, %s)''', (user_cookbook_id, insert_user_id))
    conn.commit()

    return render_template("create_cookbook.html", step="add_entry")


@app.route("/settings")
def settings():
  return render_template('settings.html')


@app.route("/change_password", methods=['POST'])
def change_password():
  if 'username' not in session:
    return redirect(url_for('login'))

  username = session['username']
  current_password = request.form['current_password']
  new_password = request.form['new_password']

  # Verify current password
  conn = connect_db()
  cur = conn.cursor()
  cur.execute("SELECT password FROM Users WHERE name = %s", (username, ))
  stored_password = cur.fetchone()[0]
  cur.close()

  if current_password != stored_password:
    return render_template('settings.html',
                           error='Current password is incorrect')

  # Update password
  conn = connect_db()
  cur = conn.cursor()
  cur.execute("UPDATE Users SET password = %s WHERE name = %s",
              (new_password, username))
  conn.commit()
  cur.close()

  return render_template('settings.html',
                         success='Password updated successfully')


@app.route("/delete_account", methods=['POST'])
def delete_account():
  if 'username' not in session:
    return redirect(url_for('login'))

  username = session['username']
  password = request.form['password']

  # Verify password
  conn = connect_db()
  cur = conn.cursor()
  cur.execute("SELECT password FROM Users WHERE name = %s", (username, ))
  stored_password = cur.fetchone()[0]
  cur.close()

  if password != stored_password:
    return render_template('settings.html', error2='Password is incorrect')

  # Delete account
  conn = connect_db()
  cur = conn.cursor()
  cur.execute("DELETE FROM Users WHERE name = %s", (username, ))
  conn.commit()
  cur.close()

  session.pop('username', None)
  return redirect(url_for('index'))

@app.route("/delete_cookbook", methods=['POST'])
def delete_cookbook():
    if 'username' not in session:
        return redirect(url_for('login'))

    cookbook_id = request.form['cookbook_id']
    conn = get_db()
    cur = conn.cursor()

    # Deleting the cookbook
    cur.execute("DELETE FROM cookbooks_usedby_user WHERE cookbook_id = %s", (cookbook_id,))
    cur.execute("DELETE FROM cookbook_to_recipe WHERE cookbook_id = %s", (cookbook_id,))
    cur.execute("DELETE FROM cookbooks WHERE cookbook_id = %s", (cookbook_id,))
    conn.commit()
    cur.close()

    return redirect(url_for('cookbook'))

@app.route("/delete_recipe_from_cookbook", methods=['POST'])
def delete_recipe_from_cookbook():
    if 'username' not in session:
        return redirect(url_for('login'))

    recipe_id = request.form['recipe_id']
    cookbook_id = request.form['cookbook_id']
    conn = get_db()
    cur = conn.cursor()

    # Deleting the recipe from the cookbook
    cur.execute("DELETE FROM cookbook_to_recipe WHERE recipe_id = %s AND cookbook_id = %s", (recipe_id, cookbook_id))
    conn.commit()
    cur.close()

    return redirect(url_for('cookbook'))

def connect_db():
  """Connects to the database."""
  debug("Connecting to DB.")
  conn = psycopg2.connect(host="dbclass.rhodescs.org",
                          user=DBUSER,
                          password=DBPASS,
                          dbname="group1",
                          cursor_factory=psycopg2.extras.DictCursor)
  return conn


def get_db():
  """Retrieve the database connection or initialize it. The connection
    is unique for each request and will be reused if this is called again.
    """
  if "db" not in g:
    g.db = connect_db()

  return g.db


@app.teardown_appcontext
def close_db(e=None):
  """If this request connected to the database, close the
    connection.
    """
  db = g.pop("db", None)

  if db is not None:
    db.close()
    debug("Closing DB")


@app.cli.command("init")
def init_db():
  """Clear existing data and create new tables."""
  conn = get_db()
  cur = conn.cursor()
  with current_app.open_resource("schema.sql") as file:  # open the file
    alltext = file.read()  # read all the text
    cur.execute(alltext)  # execute all the SQL in the file
  conn.commit()
  print("Initialized the database and cleared tables.")


#####################################################
# Debugging


def debug(s):
  """Prints a message to the console/shell (not web browser) 
    if debugging is turned on."""
  if DEBUG:  # set to False to turn off
    print("DEBUG:", s)


#####################################################
# App begins running here:

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080,
          debug=True)  # can turn off debugging with False
