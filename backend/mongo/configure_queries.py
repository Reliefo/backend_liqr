from backend.mongo.utils import *


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
    elif element_type == 'taxes':
        return configuring_taxes(request_type, message)
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
        Table.objects.get(id=message['table_id']).update(push__staff=Staff.objects.get(id=message['assigned_staff']))
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


def configuring_taxes(request_type, message):
    if request_type == 'set':
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(set__taxes=message['taxes'])
        return message
    else:
        return {'status': 'command type not recognized'}
