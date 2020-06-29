from backend.mongo.configure_queries import *
from backend.mongo.returning_query import *
from backend.mongo.billing import billed_cleaned
import time


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
            for table in Table.objects(users__in=[temp_user[0].id]):
                table.users.remove(temp_user[0])
                table.save()
            scanned_table.users.append(temp_user[0].to_dbref())
            scanned_table.save()
            return temp_user[0]
        else:
            planet = np.random.choice(TempUser.planet_choices)
            if len(TempUser.objects.filter(planet__in=[planet])) == 0:
                planet_no = 1
            else:
                planet_no = len(TempUser.objects.filter(planet__in=[planet])) + 1
            name = planet + " " + str(planet_no)
            temp_user = TempUser(unique_id=unique_id + "$" + name, current_table_id=str(scanned_table.id),
                                 planet=planet, planet_no=planet_no, name=name).save()
            scanned_table.users.append(temp_user.to_dbref())
            scanned_table.save()
            return temp_user
    else:
        reg_user = RegisteredUser.objects.filter(email_id=email_id)[0]
        if reg_user.current_table_id == str(scanned_table.id):
            if Table.objects(users__in=[reg_user.id]):
                return reg_user
            else:
                scanned_table.users.append(reg_user.to_dbref())
                scanned_table.save()
                return reg_user
        for table in Table.objects(users__in=[reg_user.id]):
            table.users.remove(reg_user)
            table.save()
        scanned_table.users.append(reg_user.to_dbref())
        scanned_table.save()
        reg_user.current_table_id = str(scanned_table.id)
        reg_user.save()
        return reg_user


# Generating orders and asstypes
def food_embed(food_dict, fooditem_fields_to_capture):
    json_dict = {key: food_dict[key] for key in food_dict.keys() if key in fooditem_fields_to_capture}
    json_dict['status'] = 'queued'
    option_id = choice_id = add_on_id = ''
    food_obj = FoodItem.objects.get(id=json_dict['food_id'])
    price = 0
    there_was_option = False
    if 'customization' in json_dict:
        for customization in json_dict['customization']:
            if customization["customization_type"] == "options":
                for option in customization['list_of_options']:
                    option_id += option['option_name']
                    price += float(option['option_price'])
                    there_was_option = True
            elif customization["customization_type"] == "choices":
                for option in customization['list_of_options']:
                    option_id += option
            elif customization["customization_type"] == "add_ons":
                for option in customization['list_of_options']:
                    option_id += option
                for n,option in enumerate(customization['list_of_options']):
                    customization["list_of_options"][n] = json_util.loads(FoodItem.objects.
                                                                          get(id=option).to_json())
                    price += float(customization["list_of_options"][n]['price'])
        food_id = food_dict['food_id']
        for thing in [option_id,choice_id,add_on_id]:
            if thing!='':
                food_id = food_id + "#" + thing
        if not there_was_option:
            price += float(food_obj.price)
        json_dict['food_id']=food_id
        json_dict['price'] = str(price)
    else:
        json_dict['price'] = food_obj.price
    return json_util.dumps(json_dict)


def order_placement(input_order):
    fooditem_fields_to_capture = ['name', 'description', 'price', 'quantity', 'instructions', 'food_id', 'customization',
                                  'kitchen']
    ordered_table = Table.objects.get(id=input_order['table'])
    table_order = TableOrder(table=str(ordered_table.name), table_id=str(ordered_table.id), personal_order=True,
                             timestamp=datetime.now())
    for order in input_order['orders']:
        food_list = [FoodItemMod.from_json(food_embed(food_dict, fooditem_fields_to_capture)) for food_dict in
                     order['food_list']]
        user = User.objects.get(id=order['placed_by'])
        table_order.orders.append(
            Order(placed_by={"id": str(user.id), "name": user.name}, food_list=food_list).save().to_dbref())
    table_order.save()
    ordered_table.update(push__table_orders=table_order.to_dbref())
    Restaurant.objects(tables__in=[str(ordered_table.id)]).update(push__table_orders=table_order.to_dbref())
    return TableOrder.objects.get(id=table_order.id).to_json()


def push_to_table_cart(input_order):
    fooditem_fields_to_capture = ['name', 'description', 'price', 'quantity', 'instructions', 'food_id', 'customization',
                                  'kitchen']
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
