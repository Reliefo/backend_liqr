from backend.mongo.utils import *
import time

li = [(i, j) for i, j in zip(range(10), [k for k in range(10)])]
np.random.shuffle(li)


def return_staff_details(staff_id):
    return Staff.objects.get(id=staff_id).to_json()


def fetch_requests_queue(staff_id, rest_id):
    staff = Staff.objects.get(id=staff_id)
    requests_queue = []
    for table in Restaurant.objects(restaurant_id=rest_id).first().tables:
        if staff in table.staff:
            for request in table.requests_queue:
                if not requests_queue:
                    requests_queue.append(request)
                    continue
                new_datetime = datetime.strptime(request['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                for n in range(len(requests_queue) - 1, -1, -1):
                    this_datetime = datetime.strptime(requests_queue[n]['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                    if new_datetime > this_datetime:
                        requests_queue.insert(n + 1, request)
                        break
    return json_util.dumps({'requests_queue': requests_queue})


def return_user_details(user_id):
    return User.objects.get(id=user_id).to_json()


def return_table_details(user_id):
    current_table_id = User.objects.get(id=user_id).current_table_id
    try:
        return Table.objects.get(id=current_table_id).to_cust_json()
    except ValidationError:
        return Table.objects(name='Not a table', seats=420)[0].to_json()


def return_restaurant(rest_id):
    return Restaurant.objects(restaurant_id=rest_id)[0].to_json()


def home_screen_lists(rest_id):
    home_screen = {'navigate_better': {}}
    for tag in Restaurant.objects(restaurant_id=rest_id).first().home_screen_tags:
        home_screen[tag] = [str(food.id) for food in
                            FoodItem.objects.filter(restaurant_id=rest_id).filter(tags__in=[tag])]
    for tag in Restaurant.objects(restaurant_id=rest_id).first().navigate_better_tags:
        home_screen['navigate_better'][tag] = [str(food.id) for food in
                                               FoodItem.objects.filter(restaurant_id=rest_id).filter(tags__in=[tag])]
    return json_util.dumps(home_screen)


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
                if Table.objects(users__in=[temp_user[0].id]):
                    return temp_user[0]
                else:
                    scanned_table.users.append(temp_user[0].to_dbref())
                    scanned_table.save()
                    return temp_user[0]
            temp_user[0].update(set__current_table_id=str(scanned_table.id))
            if Table.objects(users__in=[temp_user[0].id]):
                Table.objects(users__in=[temp_user[0].id]).first().update(pull__users=temp_user[0])
            scanned_table.users.append(temp_user[0].to_dbref())
            scanned_table.save()
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
            scanned_table.users.append(temp_user.to_dbref())
            scanned_table.save()
            return temp_user
    else:
        reg_user = RegisteredUser.objects.filter(email_id=email_id)[0]
        scanned_table.users.append(reg_user.to_dbref())
        scanned_table.save()
        reg_user.current_table_id = str(scanned_table.id)
        reg_user.save()
        return reg_user


def order_placement(input_order):
    fooditem_fields_to_capture = ['name', 'description', 'price', 'quantity', 'instructions', 'food_id', 'food_options']
    ordered_table = Table.objects.get(id=input_order['table'])
    table_order = TableOrder(table=str(ordered_table.name), table_id=str(ordered_table.id), personal_order=True,
                             timestamp=datetime.now())
    for order in input_order['orders']:
        food_list = [FoodItemMod.from_json(json_util.dumps(
            {**{key: food_dict[key] for key in food_dict.keys() if key in fooditem_fields_to_capture},
             **{'status': "queued"}})) for food_dict in order['food_list']]
        user = User.objects.get(id=order['placed_by'])
        table_order.orders.append(
            Order(placed_by={"id": str(user.id), "name": user.name}, food_list=food_list).save().to_dbref())
    table_order.save()
    ordered_table.update(push__table_orders=table_order.to_dbref())
    Restaurant.objects(tables__in=[str(ordered_table.id)]).update(push__table_orders=table_order.to_dbref())
    return TableOrder.objects.get(id=table_order.id).to_json()


def push_to_table_cart(input_order):
    fooditem_fields_to_capture = ['name', 'description', 'price', 'quantity', 'instructions', 'food_id', 'food_options']
    ordered_table = Table.objects.get(id=input_order['table'])
    order = input_order['orders'][0]
    if ordered_table.table_cart:
        new_food_list = [FoodItemMod.from_json(food_embed(food_dict, fooditem_fields_to_capture)) for food_dict in
                         order['food_list']]
        user = User.objects.get(id=order['placed_by'])
        cart_order_id = None
        for cart_order in TableOrder.objects.get(id=ordered_table.table_cart.id).orders:
            if str(user.id) == cart_order.placed_by['id']:
                cart_order_id = cart_order.id
        if cart_order_id:
            order = Order.objects.get(id=cart_order_id)
            food_list = order.food_list.copy()
            for new_food_item in new_food_list:
                quantity = -1
                for food_item in food_list:
                    if food_item.food_id == new_food_item.food_id:
                        quantity = food_item.quantity + new_food_item.quantity
                        remove_food = food_item
                if quantity != -1:
                    food_list.remove(remove_food)
                    new_food_item.quantity = quantity
                food_list.append(new_food_item)
            order.food_list = food_list
            order.save()
        else:
            TableOrder.objects.get(id=ordered_table.table_cart.id).update(
                push__orders=Order(placed_by={"id": str(user.id), "name": user.name},
                                   food_list=new_food_list).save().to_dbref())
    else:
        table_order = TableOrder(table=str(ordered_table.name), table_id=str(ordered_table.id),
                                 timestamp=datetime.now())
        food_list = [FoodItemMod.from_json(food_embed(food_dict, fooditem_fields_to_capture)) for food_dict in
                     order['food_list']]
        table_order.orders.append(Order(placed_by={"id": str(User.objects.get(id=order['placed_by']).id),
                                                   "name": User.objects.get(id=order['placed_by']).name},
                                        food_list=food_list).save().to_dbref())
        table_order.save()
        Table.objects.get(id=input_order['table']).update(set__table_cart=table_order.to_dbref())


def remove_from_table_cart(input_dict):
    remove_food = None
    for food_item in Order.objects.get(id=input_dict['order_id']).food_list:
        if food_item.food_id == input_dict['food_id']:
            remove_food = food_item
    Order.objects.get(id=input_dict['order_id']).update(pull__food_list=remove_food)


def order_placement_table(table_id):
    table_order = Table.objects.get(id=table_id).table_cart
    table_order.timestamp = datetime.now()
    table_order.save()
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
    elif element_type == 'kitchen_staff':
        return configuring_kitchen_staff(request_type, message)
    elif element_type == 'food_category':
        return configuring_food_category(request_type, message)
    elif element_type == 'bar_category':
        return configuring_bar_category(request_type, message)
    elif element_type == 'food_item':
        return configuring_food_item(request_type, message)
    elif element_type == 'home_screen_tags':
        return configuring_home_screen(request_type, message)
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


def configuring_kitchen_staff(request_type, message):
    if request_type == 'add':
        staff_objects = []
        staff_dict_list = []
        for staff_pair in message['kitchen_staff']:
            new_staff = KitchenStaff(name=staff_pair['name']).save()
            staff_objects.append(new_staff.to_dbref())
            staff_dict_list.append({**{'kitchen_staff_id': str(new_staff.id)}, **staff_pair})
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__kitchen_staff=staff_objects)
        message['kitchen_staff'] = staff_dict_list
        return message
    elif request_type == 'delete':
        KitchenStaff.objects.get(id=message['kitchen_staff_id']).delete()
        message['status'] = "Staff Deleted"
        return message
    elif request_type == 'edit':
        this_object = KitchenStaff.objects.get(id=message['kitchen_staff_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
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


def configuring_home_screen(request_type, message):
    if request_type == 'add':
        restaurant_ob = Restaurant.objects(restaurant_id=message['restaurant_id']).first()
        if message['add_to'] == "navigate_better":
            restaurant_ob.navigate_better_tags.append(message['tag_name'])
            message['status'] = "added"
        elif message['add_to'] == "home_screen":
            restaurant_ob.home_screen_tags.append(message['tag_name'])
            message['status'] = "added"
        else:
            message['status'] = "wrong add to"
        restaurant_ob.save()
        return message
    elif request_type == 'attach':
        FoodItem.objects.get(id=message['food_id']).update(push__tags=message['tag_name'])
        message['status'] = "Tag " + message['tag_name'] + " attached to Food Item"
        return message
    elif request_type == 'remove':
        FoodItem.objects.get(id=message['food_id']).update(pull__tags=message['tag_name'])
        message['status'] = "Tag " + message['tag_name'] + " removed from Food Item"
        return message
    elif request_type == 'delete':
        restaurant_ob = Restaurant.objects(restaurant_id=message['restaurant_id']).first()
        if message['remove_from'] == "navigate_better":
            restaurant_ob.navigate_better_tags.remove(message['tag_name'])
            message['status'] = "deleted"
        elif message['remove_from'] == "home_screen":
            restaurant_ob.home_screen_tags.remove(message['tag_name'])
            message['status'] = "deleted"
        else:
            message['status'] = "wrong remove from"
        if message['status'] == 'deleted':
            for food in FoodItem.objects(tags__in=[message['tag_name']]):
                food.tags.remove(message['tag_name'])
                food.save()
        restaurant_ob.save()
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


def calculate_bill(table_ob, restaurant):
    pretax = 0
    for table_ord in table_ob.table_orders:
        for order in table_ord.orders:
            for food in order.food_list:
                pretax += float(food.price)
    total_tax = restaurant.taxes['Service'] + restaurant.taxes['SGST'] + restaurant.taxes['CGST']
    total_amount = pretax * (100 + total_tax) / 100
    return restaurant.taxes, {'Pre-Tax Amount': pretax, 'Total Tax': total_tax, 'Total Amount': total_amount}


def billed_cleaned(table_id):
    table_ob = Table.objects.get(id=table_id)
    if len(table_ob.table_orders) == 0:
        table_ob.users = []
        table_ob.save()
        return False
    for user in table_ob.users:
        user_history = UserHistory()
        restaurant = Restaurant.objects(tables__in=[table_id]).first()
        user_history.table_id = table_id
        user_history.table = table_ob.name
        user_history.restaurant_id = str(restaurant.id)
        user_history.restaurant_name = str(restaurant.name)
        for table_ord in table_ob.table_orders:
            if table_ord.personal_order:
                if table_ord.orders[0].placed_by['id'] == user.id:
                    user_history.personal_orders.append(json_util.loads(table_ord.to_json()))
            else:
                user_history.table_orders.append(json_util.loads(table_ord.to_json()))
        user_history.users.extend([{"name": user.name, "user_id": str(user.id)} for user in table_ob.users])
        user_history.assistance_reqs.extend(
            [json_util.loads(ass_req.to_json()) for ass_req in table_ob.assistance_reqs])
        user_history.timestamp = datetime.now()
        user_history.save()
        user.dine_in_history.append(user_history.to_dbref())
        user.current_table_id = None
        user.save()

    order_history = OrderHistory()
    order_history.table_id = table_id
    order_history.table = table_ob.name
    order_history.taxes, order_history.bill_structure = calculate_bill(table_ob, Restaurant.objects(
        tables__in=[table_ob]).first())
    for table_ord in table_ob.table_orders:
        order_history.table_orders.append(json_util.loads(table_ord.to_json()))
        table_ord.delete()
    order_history.users.extend([{"name": user.name, "user_id": str(user.id)} for user in table_ob.users])
    order_history.assistance_reqs.extend([json_util.loads(ass_req.to_json()) for ass_req in table_ob.assistance_reqs])
    for ass_req in table_ob.assistance_reqs:
        ass_req.delete()
    order_history.timestamp = datetime.now()
    order_history.save()
    Restaurant.objects(tables__in=[table_ob]).first().update(push__order_history=order_history)
    table_ob.table_orders = []
    table_ob.assistance_reqs = []
    table_ob.users = []
    table_ob.save()
    return order_history.to_json()
