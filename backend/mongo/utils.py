from backend.mongo.mongodb import *
import numpy as np
import re


def str_n(number, n=2):
    string = str(number)
    diff = n - len(string)
    return '0' * diff + string


def np_rand(a, b=-1):
    if b == -1:
        return np.random.randint(a)
    else:
        return np.random.randint(a, b)


# RANDOM Functions
def random_table():
    all_table_list = []
    for obj in Table.objects:
        all_table_list.append(str(obj.id))
    return all_table_list[np.random.randint(len(all_table_list))]


def random_user():
    user_list = []
    for obj in User.objects:
        user_list.append(str(obj.id))
    return user_list[np.random.randint(len(user_list))]


def random_food():
    all_food_list = []
    for obj in FoodItem.objects:
        all_food_list.append(str(obj.id))
    return all_food_list[np.random.randint(len(all_food_list))]


def random_food_list():
    random_fl = []
    for i in range(np.random.randint(2, 9)):
        random_fl.append(random_food())
    return list(set(random_fl))


# Generating orders and asstypes
def food_embed(food_dict, fooditem_fields_to_capture):
    json_dict = {key: food_dict[key] for key in food_dict.keys() if key in fooditem_fields_to_capture}
    json_dict['status'] = 'queued'
    option_id = choice_id = ''
    if 'food_options' in json_dict:
        if 'options' in json_dict['food_options'].keys():
            option_id = json_dict['food_options']['options'][0]['option_name']
        if 'choices' in json_dict['food_options'].keys():
            choice_id = json_dict['food_options']['choices'][0]
    if option_id != '':
        if choice_id != '':
            json_dict['food_id'] = food_dict['food_id'] + "#" + option_id + "_" + choice_id
        else:
            json_dict['food_id'] = food_dict['food_id'] + "#" + option_id
    return json_util.dumps(json_dict)


def c_food_dict(food_id):
    f_dict = {'food_id': food_id, 'quantity': int(np.random.choice([1, 1, 1, 1, 2, 2, 3])),
              'instructions': ['Cook with love' if np.random.randint(2) else 'no'][0]}
    return f_dict


def generate_order():
    input_order = {'table': random_table(), 'orders': []}
    for n in range(np.random.randint(1, 5)):
        input_order['orders'].append({})
        input_order['orders'][n]['placed_by'] = random_user()
        input_order['orders'][n]['food_list'] = [food_embed(c_food_dict(v)) for v in random_food_list()]
    return input_order


def generate_asstype():
    assist_input = {'table': random_table(), 'user': random_user(),
                    'assistance_type': Assistance.types[np.random.randint(len(Assistance.types))]}
    return assist_input


# Randomizing order status


def non_completed(class_objects, cooking, skip=0):
    if cooking:
        for obj in class_objects:
            if obj.status == 'queued':
                if skip == 0:
                    return obj
                else:
                    skip = 0
                    continue
        return 'all_cooking'
    else:
        for obj in class_objects:
            if obj.status == 'cooking':
                if skip == 0:
                    return obj
                else:
                    skip = 0
                    continue
        return 'all_completed'


def food_status_check(class_objects, skip=0):
    for obj in class_objects:
        if obj.status == 'queued':
            if skip == 0:
                return obj
            else:
                skip = 0
                continue
    return 'all_cooking'


def food_status_check_cook(class_objects, skip=0):
    for obj in class_objects:
        if obj.status == 'cooking':
            if skip == 0:
                return obj
            else:
                skip = 0
                continue
    return 'all_completed'


def pick_order():
    if True:
        table_order = non_completed(TableOrder.objects, True)
        order = non_completed(table_order.orders, True)
        if not isinstance(order, Order):
            TableOrder.objects.get(id=table_order.id).update(set__status='cooking')
            print('changing table order status')
            return pick_order()

        food_ob = food_status_check(order.food_list)
        if isinstance(food_ob, FoodItemMod):
            food_id = food_ob.food_id
            return (str(table_order.id), str(order.id), food_id)
        elif food_ob == 'all_cooking':
            Order.objects.get(id=order.id).update(set__status='cooking')
            print('changing order status')
            return pick_order()


def pick_order2():
    if True:
        table_order = non_completed(TableOrder.objects, False)
        order = non_completed(table_order.orders, False)
        if not isinstance(order, Order):
            TableOrder.objects.get(id=table_order.id).update(set__status='completed')
            return pick_order()

        food_ob = food_status_check_cook(order.food_list)
        if isinstance(food_ob, FoodItemMod):
            food_id = food_ob.food_id
            return (str(table_order.id), str(order.id), food_id)
        elif food_ob == 'all_completed':
            Order.objects.get(id=order.id).update(set__status='completed')
            return pick_order()


def custom_splitter(text):
    types = []
    full_splits = re.split('[/]', text)
    for n, spl in enumerate(full_splits):
        if n == 0:
            types.append(re.search('[a-zA-Z]+', spl.strip().split()[-1]).group())
        elif n == len(full_splits) - 1:
            types.append(re.search('[a-zA-Z]+', spl.strip().split()[0]).group())
        else:
            types.append(re.search('[a-zA-Z]+', spl).group())
    return types
