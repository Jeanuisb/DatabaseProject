import pandas as pd
import psycopg2
import psycopg2.extras
import re
import json


##note, before running populate, run createtables to get fresh tables
DBUSER = "group1"
DBPASS = "group1"
##todo: populate users and cookbooks



def int_or_float(attribute):
  if re.findall("\d+\.\d+", str(attribute).strip()):
    return float(re.findall("\d+\.\d+", str(attribute).strip())[0])
  else:
    return int(''.join(filter(str.isdigit, str(attribute).strip())))


def connect_db():
  conn = psycopg2.connect(host="dbclass.rhodescs.org",
                          user=DBUSER,
                          password=DBPASS,
                          dbname="group1",
                          cursor_factory=psycopg2.extras.DictCursor)
  return conn

def populate_users():
  users = ["Arnab Das", "Joshua Davis", "Joshua Holland", "Joshua Kim"]
  conn = connect_db()
  cursor = conn.cursor()

  for item in users:
    cursor.execute("INSERT INTO Users (name) VALUES (%s)", (item, ))
  conn.commit()
  print("Populated User DB")

def populate_cuisines():
  cuisines = [
      "American", "Thai", "Japanese", "Mexican", "Indian", "Chinese",
      "Italian", "French", "Greek", "Spanish", "Mediterranean", "Moroccan",
      "Brazilian", "Vietnamese", "Korean", "Turkish"
  ]

  conn = connect_db()
  cursor = conn.cursor()

  for item in cuisines:
    cursor.execute("INSERT INTO cuisine (cuisine_name) VALUES (%s)", (item, ))

  conn.commit()
  print("Populated Cuisine DB.")


def populate_cookware():
  cookware = [
      "oven", "pan", "fry pan", "pot", "sauce pan", "skillet", "bowl",
      "spatula", "spoon", "fork", "knife", "cast iron skillet", "grill",
      "grill pan", "grill skillet", "grill pot", "grill sauce pan",
      "grill fork", "grill knife", "wok", "roasting pan", "paella pan",
      "paella pot", "paella sauce pan", "paella fork", "paella knife",
      "dutch oven", "sheet pan", "cake pan", "muffin tin", "muffin pan",
      "pie pan", "tart pan", "baking sheet", "baking tray", "slow cooker"
  ]

  conn = connect_db()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM cooking_gear")

  for item in cookware:
    cursor.execute("INSERT INTO cooking_gear (gear_name) VALUES (%s)",
                   (item, ))

  conn.commit()
  print("Populated Cookware DB.")


def populate_ingredients():
  data = pd.read_csv(
      "nutrition.csv"
  )
  df = pd.DataFrame(data)

  conn = connect_db()
  cursor = conn.cursor()

  for row in df.itertuples():
    servingsize = int_or_float(row.serving_size)
    calories = int_or_float(row.calories)
    totalfat = int_or_float(row.total_fat)
    saturatedfat = int_or_float(row.saturated_fat)
    cholesterol = int_or_float(row.cholesterol)
    sodium = int_or_float(row.sodium)
    carbohydrate = int_or_float(row.carbohydrate)
    fiber = int_or_float(row.fiber)
    sugars = int_or_float(row.sugars)
    protein = int_or_float(row.protein)

    cursor.execute(
        "INSERT INTO ingredients (ingredient_name, serving_size_g, calories, total_fat_g, "
        "saturated_fat_g, cholesterol_mg, sodium_mg, carbs_g, fiber_g, sugars_g, protein_g) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (str(row.name), int(servingsize), int(calories), float(totalfat),
         float(saturatedfat), int(cholesterol), float(sodium),
         float(carbohydrate), float(fiber), float(sugars), float(protein)))
  conn.commit()
  print("Populated ingredient db.")


def populate_recipes():
  json_data = open('recipes_raw_nosource_ar.json', "r")
  parsed_json = json.loads(json_data.read())
  conn = connect_db()
  cursor = conn.cursor()

  for item in parsed_json.items():
    title = item[1]["title"]
    instructions = item[1]["instructions"]
    ingredients = item[1]["ingredients"]
    cursor.execute(
        "INSERT INTO recipes (name, instructions)"
        "VALUES (%s, %s)", (title, instructions))
    conn.commit()
    for ingredient in ingredients:
      if ingredient == '':
        pass
      else:
        cursor.execute("Select recipe_id from recipes where name = %s",
                         (title, ))
        recipe_id = cursor.fetchone()[0]
        cursor.execute(
              "INSERT INTO list_ingredients_recipe (recipe_id, ingredient) VALUES (%s, %s)",
              (recipe_id, ingredient))
        conn.commit()
  print("Populated recipes db")


##plan to remove below function if populate recipes works
def populate_recipes_ingredients():
  json_data = open('recipes_raw_nosource_ar.json', "r")
  parsed_json = json.loads(json_data.read())
  conn = connect_db()
  cursor = conn.cursor()

  for item in parsed_json.items():
    title = item[1]["title"]
    ingredients = item[1]["ingredients"]
    for ingredient in ingredients:
      if ingredient == '':
        pass
      else:
        cursor.execute("Select recipe_id from recipes where name = %s",
                         (title, ))
        recipe_id = cursor.fetchone()[0]
        cursor.execute(
              "INSERT INTO list_ingredients_recipe (recipe_id, ingredient) VALUES (%s, %s)",
              (recipe_id, ingredient))
        conn.commit()
  print("Populated recipes_ingredients db")


def populate_recipes_cuisines():
  conn = connect_db()
  cursor = conn.cursor()

  query = '''select recipe_id from recipes'''
  cursor.execute(query)
  recipe_ids = cursor.fetchall()

  for recipe_id in recipe_ids:
    query = '''INSERT INTO recipe_to_cuisine (recipe_id, cuisine_name) VALUES (%s, %s)'''
    cursor.execute(query, (recipe_id[0], "American"))
  conn.commit()
  print("Populated recipes_cuisines db")

def populate_recipes_cookware():
  conn = connect_db()
  cursor = conn.cursor()

  query = '''select gear_name from cooking_gear'''
  cursor.execute(query)
  gear_arrays = cursor.fetchall()
  gear = []

  for l in gear_arrays:
    gear += l

  instruction_query = '''select recipe_id, instructions from recipes'''
  cursor.execute(instruction_query)
  rows = cursor.fetchall()

  for row in rows:
    instruction = row[1]
    for item in gear:
      if item in instruction:
        query = '''INSERT INTO recipe_uses_cookware (recipe_id, gear_name) VALUES (%s, %s)'''
        cursor.execute(query, (row[0], item))
  conn.commit()
  print("Populated recipes_cookware db")

def main():
  populate_recipes_cookware()


main()
