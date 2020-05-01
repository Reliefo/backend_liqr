from backend.mongo.utils import *
import time

li = [(i, j) for i, j in zip(range(10), [k for k in range(10)])]
np.random.shuffle(li)


def return_user_details(user_id):
    pass


def return_restaurant(rest_id):
    return Restaurant.objects(restaurant_id=rest_id)[0].to_json()


def home_screen_lists(rest_id):
    home_screen = {'available_tags': Restaurant.objects(restaurant_id=rest_id).first().home_screen_tags,
                   'navigate better': {
                       'available_tags': Restaurant.objects(restaurant_id=rest_id).first().navigate_better_tags}}

    for tag in home_screen['available_tags']:
        home_screen[tag] = [str(food.id) for food in FoodItem.objects.filter(restaurant=rest_id).filter(tags__in=[tag])]
    for tag in home_screen['navigate better']['available_tags']:
        home_screen['navigate better'][tag] = [str(food.id) for food in
                                               FoodItem.objects.filter(restaurant=rest_id).filter(tags__in=[tag])]

    return json.dumps(home_screen)


def return_restaurant_customer(rest_id):
    return Restaurant.objects(restaurant_id=rest_id) \
        .exclude('staff') \
        .exclude('tables') \
        .exclude("table_orders").first().to_json()


def fetch_order(n):
    return TableOrder.objects[n].to_json()


def user_scan(table_id, unique_id, email_id='dud'):
    scanned_table = Table.objects.get(id=table_id)
    if email_id == 'dud':
        temp_user = TempUser.objects.filter(unique_id=unique_id)
        if len(temp_user) > 0:
            if temp_user[0].current_table_id == str(scanned_table.id):
                return temp_user[0]
            temp_user[0].update(set__current_table_id=str(scanned_table.id))
            scanned_table.update(push__users=temp_user[0].to_dbref())
            return temp_user[0]
        else:
            planet = np.random.choice(TempUser.planet_choices)
            if len(TempUser.objects.filter(planet__in=[planet])) == 0:
                planet_no = 1
            else:
                planet_no = len(TempUser.objects.filter(planet__in=[planet])) + 1
            name = planet + "_" + str(planet_no)
            temp_user = TempUser(unique_id=unique_id + "$" + name, current_table_id=str(scanned_table.id),
                                 planet=planet, planet_no=planet_no, name=name).save()
            scanned_table.update(push__users=temp_user.to_dbref())
            return temp_user
    else:
        reg_user = RegisteredUser.objects.filter(email_id=email_id)[0]
        scanned_table.update(push__users=reg_user)
        reg_user.update(set__current_table_id=str(scanned_table.id))
        return reg_user


def order_placement(input_order):
    ordered_table = Table.objects.get(id=input_order['table'])
    table_order = TableOrder(table=str(ordered_table.name), table_id=str(ordered_table.id), personal_order=True,
                             timestamp=datetime.now())
    for order in input_order['orders']:
        food_list = [FoodItemMod.from_json(json_util.dumps({**food_dict, **{'status': "queued"}})) for food_dict in
                     order['food_list']]
        table_order.orders.append(
            Order(placed_by=User.objects.get(id=order['placed_by']).to_dbref(), food_list=food_list).save().to_dbref())
    table_order.save()
    ordered_table.update(push__table_orders=table_order.to_dbref())
    Restaurant.objects(tables__in=[str(ordered_table.id)]).update(push__table_orders=table_order.to_dbref())
    return TableOrder.objects.get(id=table_order.id).to_json()


def push_to_table_cart(input_order):
    ordered_table = Table.objects.get(id=input_order['table'])
    order = input_order['orders'][0]
    if ordered_table.table_cart:
        food_list = [FoodItemMod.from_json(json_util.dumps({**food_dict, **{'status': "queued"}})) for food_dict in
                     order['food_list']]
        TableOrder.objects.get(id=ordered_table.table_cart.id).update(
            push__orders=Order(placed_by=User.objects.get(id=order['placed_by']).to_dbref(),
                               food_list=food_list).save().to_dbref())
    else:
        table_order = TableOrder(table=str(ordered_table.name), table_id=str(ordered_table.id), personal_order=False,
                                 timestamp=datetime.now())
        food_list = [FoodItemMod.from_json(json_util.dumps({**food_dict, **{'status': "queued"}})) for food_dict in
                     order['food_list']]
        table_order.orders.append(
            Order(placed_by=User.objects.get(id=order['placed_by']).to_dbref(), food_list=food_list).save().to_dbref())
        table_order.save()
        Table.objects.get(id=input_order['table']).update(set__table_cart=table_order)
    return Table.objects.get(id=input_order['table']).table_cart.to_json()


def order_placement_table(table_id):
    table_order = Table.objects.get(id=table_id).table_cart
    Table.objects.get(id=table_id).update(unset__table_cart="")
    Table.objects.get(id=table_id).update(push__table_orders=table_order.to_dbref())
    Restaurant.objects(tables__in=[str(table_id)]).update(push__table_orders=table_order.to_dbref())
    return table_order.to_json()


def assistance_req(assist_input):
    curr_table = Table.objects.get(id=assist_input['table'])
    curr_ass = Assistance(user=User.objects.get(id=assist_input['user']).to_dbref())
    curr_ass.assistance_type = assist_input['assistance_type']
    curr_ass.table_id = assist_input['table']
    curr_ass.table = curr_table.name
    curr_ass.timestamp = datetime.now()
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
    [request_type, element_type] = message['type'].split('_', 1)

    if element_type == 'tables':
        return configuring_tables(request_type, message)
    elif element_type == 'staff':
        return configuring_staff(request_type, message)
    elif element_type == 'food_category':
        return configuring_food_category(request_type, message)
    elif element_type == 'bar_category':
        return configuring_bar_category(request_type, message)
    elif element_type == 'food_item':
        return configuring_food_item(request_type, message)
    else:
        return {'status': 'element not recognized'}


def configuring_tables(request_type, message):
    if request_type == 'add':
        table_objects = []
        table_dict_list = []
        for table_pair in message['tables']:
            new_table = Table(name=table_pair['name'], seats=table_pair['seats']).save()
            table_objects.append(new_table.to_dbref())
            table_dict_list.append({**{'table_id': str(new_table.id)}, **table_pair})
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__tables=table_objects)
        message['tables'] = table_dict_list
        return message
    elif request_type == 'delete':
        Table.objects.get(id=message['table_id']).delete()
        message['status'] = "Table Deleted"
        return message
    elif request_type == 'edit':
        this_object = Table.objects.get(id=message['table_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_staff(request_type, message):
    if request_type == 'add':
        staff_objects = []
        staff_dict_list = []
        for staff_pair in message['staff']:
            new_staff = Staff(name=staff_pair['name']).save()
            staff_objects.append(new_staff.to_dbref())
            staff_dict_list.append({**{'staff_id': str(new_staff.id)}, **staff_pair})
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__staff=staff_objects)
        message['staff'] = staff_dict_list
        return message
    elif request_type == 'delete':
        Staff.objects.get(id=message['staff_id']).delete()
        message['status'] = "Staff Deleted"
        return message
    elif request_type == 'edit':
        this_object = Staff.objects.get(id=message['staff_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    elif request_type == 'assign':
        for staff_id in message['assigned_staff']:
            Table.objects.get(id=message['table_id']).update(push__staff=Staff.objects.get(id=staff_id))
        return {**message, **{'status': 'Staff Assigned'}}
    elif request_type == 'withdraw':
        Table.objects.get(id=message['table_id']).update(pull__staff=Staff.objects.get(id=message['withdraw_staff_id']))
        return {**message, **{'status': 'Staff Withdrawn'}}
    else:
        return {'status': 'command type not recognized'}


def configuring_food_category(request_type, message):
    if request_type == 'add':
        category_object = Category.from_json(json_util.dumps(message['category'])).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__food_menu=category_object.to_dbref())
        message['category']['category_id'] = str(category_object.id)
        return message
    elif request_type == 'delete':
        Category.objects.get(id=message['category_id']).delete()
        message['status'] = "Food category deleted!"
        return message
    elif request_type == 'edit':
        this_object = Category.objects.get(id=message['category_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_bar_category(request_type, message):
    if request_type == 'add':
        category_object = Category.from_json(json_util.dumps(message['category'])).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__bar_menu=category_object.to_dbref())
        message['category']['category_id'] = str(category_object.id)
        return message
    elif request_type == 'delete':
        Category.objects.get(id=message['category_id']).delete()
        message['status'] = "Bar category deleted!"
        return message
    elif request_type == 'edit':
        this_object = Category.objects.get(id=message['category_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_food_item(request_type, message):
    if request_type == 'add':
        food_object = FoodItem.from_json(json_util.dumps(message['food_dict'])).save()
        print(message)
        Category.objects(id=message['category_id'])[0].update(push__food_list=food_object.to_dbref())
        message['food_dict']['food_id'] = str(food_object.id)
        return message
    elif request_type == 'delete':
        FoodItem.objects.get(id=message['food_id']).delete()
        message['status'] = "Food Item Deleted"
        return message
    elif request_type == 'edit':
        this_object = FoodItem.objects.get(id=message['food_id'])
        for field in message['editing_fields'].keys():
            if field == 'food_options':
                this_object[field] = FoodOptions.from_json(json_util.dumps(message['editing_fields'][field]))
            else:
                this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    else:
        return {'status': 'command type not recognized'}
