drop table if exists Users cascade;
drop table if exists cooking_gear cascade;
drop table if exists cookbooks cascade;
drop table if exists ingredients cascade;
drop table if exists recipes cascade;
drop table if exists cuisine cascade;
drop table if exists cookbooks_usedby_user;
drop table if exists recipe_uses_cookware;
drop table if exists cookbook_to_recipe;
drop table if exists ingredients_in_recipe;
drop table if exists recipe_to_cuisine;
drop table if exists list_ingredients_recipe;


create table Users (
  user_id serial PRIMARY KEY,
  name varchar(250),
  password text,
  email text
);


create table cooking_gear (
  gear_name varchar(250) PRIMARY KEY
);

-- will populate this table on user input
create table cookbooks (
  cookbook_id serial PRIMARY KEY,
  cookbook_name varchar(250)
);


create table ingredients (
  ingredient_id serial PRIMARY KEY, 
  ingredient_name varchar(250),
  serving_size_g int,
  calories int,
  total_fat_g float,
  saturated_fat_g float,
  cholesterol_mg int,
  sodium_mg float,
  carbs_g float,
  fiber_g float,
  sugars_g float,
  protein_g float
);


create table recipes (
  recipe_id serial PRIMARY KEY,
  name varchar(250), 
  instructions TEXT
);


create table cuisine (
  cuisine_name varchar(250) PRIMARY KEY
);


-- tables below are weak tables, will be used when we parse enough info to link information together or on user input
create table cookbooks_usedby_user (
  user_id serial,
  cookbook_id serial,
  foreign key (user_id) references Users(user_id),
  foreign key (cookbook_id) references cookbooks(cookbook_id)
);


create table recipe_uses_cookware (
  recipe_id serial,
  gear_name varchar(250),
  foreign key (recipe_id) references recipes(recipe_id),
  foreign key (gear_name) references  cooking_gear(gear_name)
);


create table cookbook_to_recipe (
  cookbook_id serial,
  recipe_id serial,
  foreign key (cookbook_id) references cookbooks(cookbook_id),
  foreign key (recipe_id) references recipes(recipe_id),
  PRIMARY KEY (cookbook_id, recipe_id) 
);


create table list_ingredients_recipe (
  recipe_id serial, 
  ingredient text,
  foreign key (recipe_id) references recipes(recipe_id)
);


create table recipe_to_cuisine (
  cuisine_name varchar(250),
  recipe_id serial,
  foreign key (cuisine_name) references cuisine(cuisine_name),
  foreign key (recipe_id) references recipes(recipe_id)
);
