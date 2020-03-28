from backend.mongo.mongodb import *
import json
import numpy as np

user_list = []
for obj in User.objects:
    user_list.append(str(obj.id))

all_table_list = []
for obj in Table.objects:
    all_table_list.append(str(obj.id))

all_food_list = []
for obj in FoodItem.objects:
    all_food_list.append(str(obj.id))


def return_restaurant():
    return json.loads(Restaurant.objects[0].to_json())


def str_2(number):
    string = str(number)
    if len(string) == 1:
        return '0' + string
    else:
        return string


# RANDOM Functions
def random_table():
    return all_table_list[np.random.randint(len(all_table_list))]


def random_user():
    return user_list[np.random.randint(len(user_list))]


def random_food():
    return all_food_list[np.random.randint(len(all_food_list))]


def random_food_list():
    randomfl = []
    for i in range(np.random.randint(2, 9)):
        randomfl.append(random_food())
    return randomfl
