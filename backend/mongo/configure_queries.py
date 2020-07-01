from backend.mongo.utils import *
import sys
import random
import string


def random_alphaNumeric_string(lettersCount, digitsCount):
    sampleStr = ''.join((random.choice(string.ascii_letters) for i in range(lettersCount)))
    sampleStr += ''.join((random.choice(string.digits) for i in range(digitsCount)))

    # Convert string to list and shuffle it to mix letters and digits
    sampleList = list(sampleStr)
    random.shuffle(sampleList)
    finalString = ''.join(sampleList)
    return finalString


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
    elif element_type == 'add_ons':
        return configuring_add_ons(request_type, message)
    elif element_type == 'food_item':
        return configuring_food_item(request_type, message)
    elif element_type == 'home_screen_tags':
        return configuring_home_screen(request_type, message)
    elif element_type == 'taxes':
        return configuring_taxes(request_type, message)
    elif element_type == 'kitchen':
        return configuring_kitchen(request_type, message)
    elif element_type == 'manage':
        return configuring_manage(request_type, message)
    else:
        return {'status': 'element not recognized'}


def configuring_tables(request_type, message):
    if request_type == 'add':
        table_pair = message['table']
        flag = True
        while flag:
            try:
                gen_tid = random_alphaNumeric_string(4, 3)
                new_table = Table(name=table_pair['name'], seats=table_pair['seats'], tid=gen_tid).save()
                flag = False
            except NotUniqueError:
                pass
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__tables=new_table.to_dbref())
        message['table_object'] = json_util.loads(new_table.to_json())
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
        staff_pair = message['staff']
        new_staff = Staff(name=staff_pair['name']).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__staff=new_staff.to_dbref())
        message['staff'] = json_util.loads(new_staff.to_json())
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


def configuring_food_category(request_type, message):
    if request_type == 'add':
        category_object = Category.from_json(json_util.dumps(message['category'])).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__food_menu=category_object.to_dbref())
        message['category']['category_id'] = str(category_object.id)
        return message
    elif request_type == 'delete':
        for food in Category.objects.get(id=message['category_id']).food_list:
            food.delete()
        Category.objects.get(id=message['category_id']).delete()
        message['status'] = "Food category deleted!"
        return message
    elif request_type == 'edit':
        this_object = Category.objects.get(id=message['category_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    elif request_type == 'reorder':
        cat_objs = [Category.objects.get(id=this_id) for this_id in message['category_id_list']]
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(unset__food_menu=[])
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__food_menu=cat_objs)
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
        for food in Category.objects.get(id=message['category_id']).food_list:
            food.delete()
        Category.objects.get(id=message['category_id']).delete()
        message['status'] = "Bar category deleted!"
        return message
    elif request_type == 'edit':
        this_object = Category.objects.get(id=message['category_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    elif request_type == 'reorder':
        cat_objs = [Category.objects.get(id=this_id) for this_id in message['category_id_list']]
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(unset__food_menu=[])
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push_all__food_menu=cat_objs)
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_add_ons(request_type, message):
    if request_type == 'add':
        food_object = FoodItem.from_json(json_util.dumps(message['food_dict'])).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__add_ons=food_object.to_dbref())
        message.pop('food_dict')
        message['food_obj'] = json_util.loads(food_object.to_json())
        return message
    elif request_type == 'delete':
        FoodItem.objects.get(id=message['food_id']).delete()
        message['status'] = "Food Item Deleted"
        return message
    elif request_type == 'visibility':
        FoodItem.objects.get(id=message['food_id']).update(set__visibility=message['visibility'])
        return message
    elif request_type == 'edit':
        this_object = FoodItem.objects.get(id=message['food_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_food_item(request_type, message):
    if request_type == 'add':
        food_object = FoodItem.from_json(json_util.dumps(message['food_dict'])).save()
        Category.objects(id=message['category_id'])[0].update(push__food_list=food_object.to_dbref())
        message.pop('food_dict')
        message['food_obj'] = json_util.loads(food_object.to_json())
        return message
    elif request_type == 'delete':
        FoodItem.objects.get(id=message['food_id']).delete()
        message['status'] = "Food Item Deleted"
        return message
    elif request_type == 'visibility':
        FoodItem.objects.get(id=message['food_id']).update(set__visibility=message['visibility'])
        return message
    elif request_type == 'edit':
        this_object = FoodItem.objects.get(id=message['food_id'])
        sys.stderr.write("LiQR_Error: " + str(message) + " who is a connected\n")
        for field in message['editing_fields'].keys():
            if field == 'customization':
                this_object[field] = [FoodCustomization.from_json(json_util.dumps(customization)) for customization in
                                      message['editing_fields'][field]]
            else:
                this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    elif request_type == 'reorder':
        food_objs = [FoodItem.objects.get(id=this_id) for this_id in message['food_id_list']]
        Category.objects.get(id=message['category_id']).update(unset__food_list=[])
        Category.objects.get(id=message['category_id']).update(push_all__food_list=food_objs)
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_home_screen(request_type, message):
    if request_type == 'add':
        restaurant_ob = Restaurant.objects(restaurant_id=message['restaurant_id']).first()
        if message['add_to'] == "navigate_better":
            lists_obj = HomeScreenLists(name=message['tag_name'],
                                        image="https://liqr-restaurants.s3.ap-south-1.amazonaws.com/default_need_help.jpg").save()
            restaurant_ob.navigate_better_lists.append(lists_obj.to_dbref())
            message['home_screen_lists'] = json_util.loads(lists_obj.to_json())
            message['status'] = "added"
        elif message['add_to'] == "home_screen":
            lists_obj = HomeScreenLists(name=message['tag_name']).save()
            restaurant_ob.home_screen_lists.append(lists_obj.to_dbref())
            message['home_screen_lists'] = json_util.loads(lists_obj.to_json())
            message['status'] = "added"
        else:
            message['status'] = "wrong add to"
        restaurant_ob.save()
        return message
    elif request_type == 'attach':
        HomeScreenLists.objects.get(id=message['home_screen_lists_id']).update(
            push__food_list=FoodItem.objects.get(id=message['food_id']))
        return message
    elif request_type == 'remove':
        HomeScreenLists.objects.get(id=message['home_screen_lists_id']).update(
            pull__food_list=FoodItem.objects.get(id=message['food_id']))
        return message
    elif request_type == 'delete':
        HomeScreenLists.objects.get(id=message['home_screen_lists_id']).delete()
        return message
    elif request_type == 'reorder':
        food_objs = [FoodItem.objects.get(id=this_id) for this_id in message['food_id_list']]
        HomeScreenLists.objects.get(id=message['home_screen_lists_id']).update(unset__food_list=[])
        HomeScreenLists.objects.get(id=message['home_screen_lists_id']).update(push_all__food_list=food_objs)
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_taxes(request_type, message):
    if request_type == 'set':
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(set__taxes=message['taxes'])
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_kitchen(request_type, message):
    if request_type == 'add':
        kitchen = Kitchen(name=message['name']).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__kitchens=kitchen.to_dbref())
        message['kitchen_id'] = str(kitchen.id)
        return message
    elif request_type == 'edit':
        """Requires kitchen_id, name, type=edit_kitchen"""
        this_object = Kitchen.objects.get(id=message['kitchen_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    elif request_type == 'delete':
        kitchen = Kitchen.objects.get(id=message['kitchen_id'])
        for kitchen_staff in kitchen.kitchen_staff:
            kitchen_staff.delete()
        for category in kitchen.categories:
            for food in category.food_list:
                food.kitchen = None
                food.save()
            category.kitchen = None
            category.save()
        kitchen.delete()
        return message
    elif request_type == 'category':
        categories = Category.objects(id__in=message['categories'])
        kitchen = Kitchen.objects.get(id=message['kitchen_id'])
        kitchen.categories.extend(categories)
        kitchen.save()
        for category in kitchen.categories:
            for food in category.food_list:
                food.kitchen = message['kitchen_id']
                food.save()
            category.kitchen = message['kitchen_id']
            category.save()
        return message
    elif request_type == 'decategory':
        category = Category.objects.get(id=message['category_id'])
        kitchen = Kitchen.objects.get(id=message['kitchen_id'])
        kitchen.categories.remove(category)
        kitchen.save()
        category.kitchen = None
        category.save()
        for food in category.food_list:
            food.kitchen = None
            food.save()
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_kitchen_staff(request_type, message):
    if request_type == 'add':
        new_staff = KitchenStaff(name=message['name'], kitchen=message['kitchen_id']).save()
        Kitchen.objects.get(id=message['kitchen_id']).update(push__kitchen_staff=new_staff.to_dbref())
        message['kitchen_staff'] = json_util.loads(new_staff.to_json())
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


def configuring_inventory(request_type, message):
    if request_type == 'add':
        inventory_item = InventoryItem(name=message['name'], units=message['units'], quantity=message['quantity'],
                                       default_unit=message['default_unit']).save()
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(push__inventory=inventory_item)
        message['inventory_item_id'] = str(inventory_item.id)
        return message
    elif request_type == 'delete':
        InventoryItem.objects.get(id=message['inventory_item_id']).delete()
        message['status'] = "Staff Deleted"
        return message
    elif request_type == 'edit':
        this_object = InventoryItem.objects.get(id=message['kitchen_staff_id'])
        for field in message['editing_fields'].keys():
            this_object[field] = message['editing_fields'][field]
        this_object.save()
        return message
    else:
        return {'status': 'command type not recognized'}


def configuring_manage(request_type, message):
    if request_type == 'ordering-ability':
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(set__ordering_ability=message['status'])
        if message['status']:
            message['status'] = not message['status']
            configuring_manage('hide-ordering', message)
            message['status'] = not message['status']
        return message
    elif request_type == 'hide-ordering':
        Restaurant.objects(restaurant_id=message['restaurant_id'])[0].update(set__hide_ordering=message['status'])
        return message
