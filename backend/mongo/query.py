from backend.mongo.utils import *
import time

li = [(i, j) for i, j in zip(range(10), [k for k in range(10)])]
np.random.shuffle(li)


def fetch_order(n):
    return TableOrder.objects[n].to_json()


def user_scan(table_id, unique_id, email_id='dud'):
    scanned_table = Table.objects.get(id=table_id)
    if email_id == 'dud':
        temp_user = TempUser.objects.filter(unique_id=unique_id)
        if len(temp_user) > 0:
            temp_user[0].update(set__current_table_id=str(scanned_table.id))
            scanned_table.update(push__users=temp_user[0].to_dbref())
            return temp_user[0].id
        else:
            temp_user = TempUser(unique_id=unique_id, current_table_id=str(scanned_table.id)).save()
            scanned_table.update(push__users=temp_user.to_dbref())
            return temp_user.id
    else:
        reg_user = RegisteredUser.objects.filter(email_id=email_id)[0]
        scanned_table.update(push__users=reg_user)
        reg_user.update(set__current_table_id=str(scanned_table.id))
        scanned_table.update(inc__no_of_users=1)


def order_placement(input_order):
    ordered_table = Table.objects.get(id=input_order['table'])
    table_order = TableOrder(table=str(ordered_table.name), table_id=str(ordered_table.name),
                             timestamp=datetime.datetime.now())
    for order in input_order['orders']:
        food_list = [FoodItemMod.from_json(food_dict) for food_dict in order['food_list']]
        table_order.orders.append(
            Order(placed_by=User.objects.get(id=order['placed_by']).to_dbref(), food_list=food_list).save().to_dbref())
        table_order.timestamp = datetime.datetime.now()
        table_order.save()
    ordered_table.update(push__table_orders=table_order.to_dbref())
    Restaurant.objects(tables__in=[str(ordered_table.id)]).update(push__table_orders=table_order.to_dbref())
    return TableOrder.objects.get(id=table_order.id).to_json()


def assistance_req(assist_input):
    curr_table = Table.objects.get(id=assist_input['table'])
    curr_ass = Assistance(user=User.objects.get(id=assist_input['user']).to_dbref())
    curr_ass.assistance_type = assist_input['assistance_type']
    curr_ass.timestamp = datetime.datetime.now()
    curr_ass.save()
    curr_table.update(push__assistance_reqs=curr_ass.to_dbref())
    return curr_ass


def send_assistance_req(assist_id):
    table = Table.objects(assistance_reqs__in=[assist_id])[0]
    for staff in table.staff:
        if np.random.randint(3):
            time.sleep(1)
            Assistance.objects.get(id=assist_id).update(set__accepted_by=staff.to_dbref())
            return staff.name
    time.sleep(3)
    for staff in Staff.objects:
        if np.random.randint(3):
            time.sleep(1)
            Assistance.objects.get(id=assist_id).update(set__accepted_by=staff.to_dbref())
            return staff.name


def validate_for_order(order_id, cooking=True):
    if cooking:
        for food_item in Order.objects.get(id=order_id).food_list:
            if food_item.status == 'cooking':
                continue
            else:
                return False
        return True
    else:
        for food_item in Order.objects.get(id=order_id).food_list:
            if food_item.status == 'completed':
                continue
            else:
                return False
        return True


def validate_for_table_order(order_id, cooking=True):
    if cooking:
        for order in TableOrder.objects.get(id=order_id).orders:
            if order.status == 'cooking':
                continue
            else:
                return False
        return True
    else:
        for order in TableOrder.objects.get(id=order_id).orders:
            if order.status == 'completed':
                continue
            else:
                return False
        return True


def order_status_cooking(status_tuple):
    order = Order.objects.get(id=status_tuple[1])
    food_json_dict = json_util.loads(order.fetch_food_item(status_tuple[2]))
    food_json_dict['status'] = 'cooking'
    Order.objects.get(id=status_tuple[1]).update(pull__food_list__food_id=FoodItemMod(food_id=status_tuple[2]).food_id)
    Order.objects.get(id=status_tuple[1]).update(push__food_list=FoodItemMod.from_json(json_util.dumps(food_json_dict)))
    if validate_for_order(status_tuple[1], True):
        Order.objects.get(id=status_tuple[1]).update(set__status='cooking')
    if validate_for_table_order(status_tuple[0], True):
        TableOrder.objects.get(id=status_tuple[0]).update(set__status='cooking')
    return "Done"


def order_status_completed(status_tuple):
    order = Order.objects.get(id=status_tuple[1])
    food_json_dict = json_util.loads(order.fetch_food_item(status_tuple[2]))
    food_json_dict['status'] = 'completed'
    Order.objects.get(id=status_tuple[1]).update(pull__food_list__food_id=FoodItemMod(food_id=status_tuple[2]).food_id)
    Order.objects.get(id=status_tuple[1]).update(push__food_list=FoodItemMod.from_json(json_util.dumps(food_json_dict)))
    if validate_for_order(status_tuple[1], False):
        Order.objects.get(id=status_tuple[1]).update(set__status='completed')
    if validate_for_table_order(status_tuple[0], False):
        TableOrder.objects.get(id=status_tuple[0]).update(set__status='completed')
    return "Done"


def configuring_restaurant(message):
    if message['type'] == 'add_tables':
        table_objects = []
        table_dict_list = []
        for table_pair in message['tables']:
            new_table = Table(name=table_pair['table_name'], seats=table_pair['seats']).save()
            table_objects.append(new_table.to_dbref())
            table_dict_list.append({**{'table_id': str(new_table.id)}, **table_pair})
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__tables=table_objects)
        return {"restaurant_id": message['restaurant_id'], "type": "add_tables", "tables": table_dict_list}
    elif message['type'] == 'add_staff':
        staff_objects = []
        staff_dict_list = []
        for staff_pair in message['staff']:
            new_staff = Staff(name=staff_pair['staff_name']).save()
            staff_objects.append(new_staff.to_dbref())
            staff_dict_list.append({**{'staff_id': str(new_staff.id)}, **staff_pair})
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__staff=staff_objects)
        return {"restaurant_id": message['restaurant_id'], "type": "add_staff", "staff": staff_dict_list}
