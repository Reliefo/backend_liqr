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
    return Restaurant.objects[0].to_json()


def str_2(number):
    string = str(number)
    if len(string) == 1:
        return '0' + string
    else:
        return string


def nprand(a, b=-1):
    if (b == -1):
        return np.random.randint(a)
    else:
        return np.random.randint(a, b)


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
    return list(set(randomfl))


# Generating orders and asstypes

def food_embed(food_dict):
    json_dict = json_util.loads(FoodItem.objects(id=food_dict['food_id']).exclude('id')[0].to_json())
    json_dict['food_id'] = food_dict['food_id']
    json_dict['quantity'] = food_dict['quantity']
    json_dict['instructions'] = food_dict['instructions']
    json_dict['status'] = 'queued'
    return json_util.dumps(json_dict)


def c_food_dict(food_id):
    f_dict = {}
    f_dict['food_id'] = food_id
    f_dict['quantity'] = int(np.random.choice([1, 1, 1, 1, 2, 2, 3]))
    f_dict['instructions'] = ['Cook with love' if np.random.randint(2) else 'no'][0]
    return f_dict


def generate_order():
    input_order = {}
    input_order['table'] = random_table()
    input_order['orders'] = []
    for n in range(np.random.randint(1, 5)):
        input_order['orders'].append({})
        input_order['orders'][n]['placedby'] = random_user()
        input_order['orders'][n]['foodlist'] = [c_food_dict(v) for v in random_food_list()]
    return input_order


def generate_asstype():
    assist_input = {'table': random_table(), 'user': random_user(),
                    'assistancetype': Assistance.types[np.random.randint(len(Assistance.types))]}
    return assist_input


# Randomizing order status


def non_completed(clas_objects, cooking, skip=0):
    if (cooking):
        for obj in clas_objects:
            if (obj.status == 'queued'):
                if (skip == 0):
                    return obj
                else:
                    skip = 0
                    continue
        return 'all_cooking'
    else:
        for obj in clas_objects:
            if (obj.status == 'cooking'):
                if (skip == 0):
                    return obj
                else:
                    skip = 0
                    continue
        return 'all_completed'


def food_status_check(clas_objects, skip=0):
    for obj in clas_objects:
        if (obj.status == 'queued'):
            if (skip == 0):
                return obj
            else:
                skip = 0
                continue
    return 'all_cooking'


def food_status_check_cook(clas_objects, skip=0):
    for obj in clas_objects:
        if (obj.status == 'cooking'):
            if (skip == 0):
                return obj
            else:
                skip = 0
                continue
    return 'all_completed'


def pick_order():
    if (True):
        tableorder = non_completed(TableOrder.objects, True)
        order = non_completed(tableorder.orders, True)
        if (not isinstance(order, Order)):
            TableOrder.objects.get(id=tableorder.id).update(set__status='cooking')
            return pick_order()

        food_ob = food_status_check(order.foodlist)
        if (isinstance(food_ob, FoodItemMod)):
            food_id = food_ob.food_id
            return (tableorder.id, order.id, food_id)
        elif (food_ob == 'all_cooking'):
            Order.objects.get(id=order.id).update(set__status='cooking')
            return pick_order()
    else:
        tableorder = non_completed(TableOrder.objects, 1)
        order = non_completed(tableorder.orders)
        food_id = food_status_check_cook(order.foodlist).food_id

        return (tableorder.id, order.id, food_id)


def pick_order2():
    if (True):
        tableorder = non_completed(TableOrder.objects, False)
        order = non_completed(tableorder.orders, False)
        if (not isinstance(order, Order)):
            TableOrder.objects.get(id=tableorder.id).update(set__status='completed')
            return pick_order()

        food_ob = food_status_check_cook(order.foodlist)
        if (isinstance(food_ob, FoodItemMod)):
            food_id = food_ob.food_id
            return (tableorder.id, order.id, food_id)
        elif (food_ob == 'all_completed'):
            Order.objects.get(id=order.id).update(set__status='completed')
            return pick_order()


    else:
        tableorder = non_completed(TableOrder.objects, 1)
        order = non_completed(tableorder.orders)
        food_id = food_status_check(order.foodlist).food_id

        return (tableorder.id, order.id, food_id)