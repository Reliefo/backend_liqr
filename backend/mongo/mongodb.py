from mongoengine import *
from datetime import datetime
from backend.config import MONGO_DB, MONGO_HOST
from bson import json_util
from flask_login import UserMixin

conn = connect(MONGO_DB, host=MONGO_HOST, alias='default', username='good_blud', password='screwZomato@420',
               authentication_source='reliefo')


class FoodCustomizationMod(EmbeddedDocument):
    name = StringField()
    customization_type = StringField(choices=['options', 'choices', 'add_ons'])
    less_more = IntField(choices=[-1, 0, 1])
    that_number = IntField()
    list_of_options = ListField()


class FoodOptionsMod(EmbeddedDocument):
    options = ListField(DictField())
    choices = ListField()
    add_ons = ListField(DictField())


class FoodItemMod(EmbeddedDocument):
    food_id = StringField()
    name = StringField()
    description = StringField()
    price = StringField()
    instructions = StringField()
    quantity = IntField()
    kitchen = StringField()
    status = StringField(choices=['awaiting', 'accepted', 'rejected', 'queued', 'cooking', 'completed'])
    customization = ListField(EmbeddedDocumentField(FoodCustomizationMod))
    food_options = EmbeddedDocumentField(FoodOptionsMod)


class Order(Document):
    placed_by = DictField()
    food_list = ListField(EmbeddedDocumentField(FoodItemMod))
    status = StringField(choices=['queued', 'cooking', 'completed'], default='queued')

    def fetch_food_item(self, food_id):
        for food_item in self.food_list:
            if food_item.food_id == food_id:
                return food_item.to_json()
        return "Food item not found"


class TableOrder(Document):
    table = StringField()
    table_id = StringField()
    orders = ListField(ReferenceField(Order))
    personal_order = BooleanField()
    status = StringField(choices=['queued', 'cooking', 'completed'], default='queued')
    timestamp = DateTimeField(default=datetime.now())

    def to_my_mongo(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        for key, order in enumerate(self.orders):
            data['orders'][key] = json_util.loads(self.orders[key].to_json())

        return data

    def to_json(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        for key, order in enumerate(self.orders):
            data['orders'][key] = json_util.loads(self.orders[key].to_json())
        return json_util.dumps(data)


class Staff(Document):
    pass


class User(Document):
    pass


class Assistance(Document):
    types = ['water', 'help', 'cutlery', 'tissue', 'cleaning', 'menu', 'ketchup']
    table = StringField()
    table_id = StringField()
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    assistance_type = StringField()
    timestamp = DateTimeField()
    accepted_by = DictField()
    meta = {'strict': False}

    def to_my_mongo(self):
        data = self.to_mongo()
        data.pop('user')
        data.pop('_id')
        data['user_id'] = str(self.user.id)
        data['user'] = self.user.name
        data['assistance_req_id'] = str(self.id)
        data['timestamp'] = str(data['timestamp'])
        return data

    def to_json(self):
        data = self.to_mongo()
        data.pop('user')
        data.pop('_id')
        data['user_id'] = str(self.user.id)
        data['user'] = self.user.name
        data['assistance_req_id'] = str(self.id)
        data['timestamp'] = str(data['timestamp'])
        return json_util.dumps(data)


class OrderHistory(Document):
    restaurant_name = StringField()
    restaurant_id = StringField()
    table_orders = ListField(DictField())
    users = ListField(DictField())
    assistance_reqs = ListField()
    timestamp = DateTimeField(default=datetime.now())
    table_id = StringField()
    table = StringField()
    bill_structure = DictField()
    taxes = DictField()
    pdf = StringField()
    invoice_no = StringField()

    def to_my_mongo(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        return data

    def to_json(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        return json_util.dumps(data)


class User(Document):
    name = StringField(required=True)
    dine_in_history = ListField(ReferenceField(OrderHistory, reverse_delete_rule=PULL))
    current_table_id = StringField()
    personal_cart = ListField(ReferenceField(TableOrder), reverse_delete_rule=PULL)
    timestamp = DateTimeField(default=datetime.now())
    meta = {'allow_inheritance': True}

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, table_order in enumerate(self.dine_in_history):
            data['dine_in_history'][key] = self.dine_in_history[key].to_my_mongo()
        for key, ass_req in enumerate(self.personal_cart):
            data['personal_cart'][key] = self.personal_cart[key].to_my_mongo()
        return data

    def to_json(self):
        data = self.to_mongo()
        for key, table_order in enumerate(self.dine_in_history):
            data['dine_in_history'][key] = self.dine_in_history[key].to_my_mongo()
        for key, ass_req in enumerate(self.personal_cart):
            data['personal_cart'][key] = self.personal_cart[key].to_my_mongo()
        return json_util.dumps(data)

    def to_minimal(self):
        data = {"name": self.name, 'id': self.id}
        return data


class TempUser(User):
    pass


class RegisteredUser(User):
    email_id = StringField(required=True)
    phone_no = StringField()
    tempuser_ob = StringField()
    unique_id = StringField()


class TempUser(User):
    planet_choices = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Neptune']
    planet = StringField(choices=planet_choices)
    planet_no = IntField()
    unique_id = StringField(required=True)
    reguser_ob = StringField()


class Staff(Document):
    name = StringField()
    requests_history = ListField(DictField())
    rej_requests_history = ListField(DictField())
    endpoint_arn = StringField()
    device_token = StringField()

    def to_my_mongo(self):
        data = self.to_mongo()
        return data

    def to_minimal(self):
        data = {'name': self.name, 'id': self.id}
        return data


class KitchenStaff(Document):
    name = StringField()
    orders_cooked = ListField(DictField())
    kitchen = StringField()

    def to_my_mongo(self):
        data = self.to_mongo()
        return data


class AppUser(UserMixin, Document):
    username = StringField(max_length=30)
    user_type = StringField(choices=['customer', 'manager', 'staff', 'kitchen', 'admin', 'owner'])
    password = StringField()
    sid = StringField()
    timestamp = DateTimeField(default=datetime.now())
    rest_user = ReferenceField(User, reverse_delete_rule=CASCADE)
    staff_user = ReferenceField(Staff, reverse_delete_rule=CASCADE)
    kitchen_staff = ReferenceField(KitchenStaff, reverse_delete_rule=CASCADE)
    restaurant_id = StringField()
    name = StringField()
    temp_password = BooleanField()


class CustomerStats(Document):
    username = StringField()
    count = IntField()


class Table(Document):
    name = StringField(required=True)
    tid = StringField(unique=True)
    seats = IntField(required=True)
    staff = ListField(ReferenceField(Staff, reverse_delete_rule=PULL))
    users = ListField(ReferenceField(User, reverse_delete_rule=PULL))
    table_orders = ListField(ReferenceField(TableOrder, reverse_delete_rule=PULL))
    table_cart = ReferenceField(TableOrder, reverse_delete_rule=NULLIFY)
    assistance_reqs = ListField(ReferenceField(Assistance, reverse_delete_rule=PULL))
    requests_queue = ListField(DictField())

    meta = {'strict': False}

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, table_order in enumerate(self.table_orders):
            data['table_orders'][key] = self.table_orders[key].to_my_mongo()
        for key, ass_req in enumerate(self.assistance_reqs):
            data['assistance_reqs'][key] = self.assistance_reqs[key].to_my_mongo()
        for key, user in enumerate(self.users):
            data['users'][key] = self.users[key].to_my_mongo()
        return data

    def to_cust_json(self):
        data = self.to_mongo()
        for key, table_order in enumerate(self.table_orders):
            data['table_orders'][key] = self.table_orders[key].to_my_mongo()
        for key, ass_req in enumerate(self.assistance_reqs):
            data['assistance_reqs'][key] = self.assistance_reqs[key].to_my_mongo()
        for key, user in enumerate(self.users):
            data['users'][key] = self.users[key].to_minimal()
        for key, user in enumerate(self.staff):
            data['staff'][key] = self.staff[key].to_minimal()
        if (self.table_cart):
            data['table_cart'] = self.table_cart.to_my_mongo()
        return json_util.dumps(data)

    def remove_staff(self, staff_id):
        for staff_ob in self.staff:
            print(staff_ob.id)
            self.staff.pop()


class InventoryItem(Document):
    name = StringField()
    units = DictField()
    default_unit = StringField()
    quantity = FloatField()

    def to_my_mongo(self):
        data = self.to_mongo()
        return data


class InventoryItemMod(EmbeddedDocument):
    inventory_item_id = StringField()
    name = StringField()
    unit_used = StringField()
    quantity = FloatField()


class FoodCustomization(EmbeddedDocument):
    name = StringField()
    customization_type = StringField(choices=['options', 'choices', 'add_ons'])
    less_more = IntField(choices=[-1, 0, 1])
    that_number = IntField()
    list_of_options = ListField()


class FoodItem(Document):
    name = StringField(required=True)
    description = StringField()
    price = StringField()
    tags = ListField(StringField())
    customization = ListField(EmbeddedDocumentField(FoodCustomization))
    #     food_options = EmbeddedDocumentField(FoodOptions)
    restaurant_id = StringField()
    image_link = StringField()
    kitchen = StringField()
    ingredients = ListField(EmbeddedDocumentField(InventoryItemMod))
    visibility = BooleanField(default=True)
    ordered_times = IntField(default=0)

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, customization in enumerate(self.customization):
            data['customization'][key] = self.customization[key].to_mongo()
        if self.ingredients:
            data['ingredients'] = self.ingredients.to_my_mongo()
        return data

    def to_json(self):
        data = self.to_mongo()
        for key, customization in enumerate(self.customization):
            data['customization'][key] = self.customization[key].to_mongo()
        if self.ingredients:
            data['ingredients'] = self.ingredients.to_my_mongo()
        return json_util.dumps(data)


class Category(Document):
    name = StringField(required=True)
    description = StringField()
    food_list = ListField(ReferenceField(FoodItem, reverse_delete_rule=PULL))
    kitchen = StringField()

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, food_item in enumerate(self.food_list):
            data['food_list'][key] = self.food_list[key].to_my_mongo()
        return data


class Kitchen(Document):
    name = StringField()
    kitchen_staff = ListField(ReferenceField(KitchenStaff, reverse_delete_rule=PULL))
    categories = ListField(ReferenceField(Category, reverse_delete_rule=PULL))

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, staff in enumerate(self.kitchen_staff):
            data['kitchen_staff'][key] = self.kitchen_staff[key].to_my_mongo()
        for key, sub_cat in enumerate(self.categories):
            data['categories'][key] = {"category_id": str(self.categories[key].id), "name": self.categories[key].name}
        return data


def check_exists(order_id, order_list):
    for n, order in enumerate(order_list):
        if order_id == order['_id']:
            return n
    return -1


class JustMenu(Document):
    name = StringField(required=True)
    menu = ListField(StringField())
    created = DateTimeField()
    visits = ListField(DateTimeField())
    qr = StringField()

    def to_json(self):
        data = self.to_mongo()
        data['created'] = str(data['created'])
        return json_util.dumps(data)


class HomeScreenLists(Document):
    name = StringField()
    image = StringField()
    food_list = ListField(ReferenceField(FoodItem, reverse_delete_rule=PULL))

    def to_my_mongo(self):
        data = self.to_mongo()
        return data


# class NavigateBetterLists(Document):
#     name=StringField()
#     image=StringField(default="https://liqr-restaurants.s3.ap-south-1.amazonaws.com/default_need_help.jpg")
#     food_list=ListField(ReferenceField(FoodItem, reverse_delete_rule=PULL))


class Restaurant(Document):
    name = StringField(required=True)
    restaurant_id = StringField(required=True)
    food_menu = ListField(ReferenceField(Category, reverse_delete_rule=PULL))
    bar_menu = ListField(ReferenceField(Category, reverse_delete_rule=PULL))
    add_ons = ListField(ReferenceField(FoodItem, reverse_delete_rule=PULL))
    address = StringField()
    abs_address = StringField()
    logo = StringField()
    phone_nos = ListField(StringField())
    tables = ListField(ReferenceField(Table, reverse_delete_rule=PULL))
    kitchen_staff = ListField(ReferenceField(KitchenStaff, reverse_delete_rule=PULL))
    staff = ListField(ReferenceField(Staff, reverse_delete_rule=PULL))
    table_orders = ListField(ReferenceField(TableOrder, reverse_delete_rule=PULL))
    assistance_reqs = ListField(ReferenceField(Assistance, reverse_delete_rule=PULL))
    order_history = ListField(ReferenceField(OrderHistory, reverse_delete_rule=PULL))
    navigate_better_lists = ListField(ReferenceField(HomeScreenLists, reverse_delete_rule=PULL))
    home_screen_lists = ListField(ReferenceField(HomeScreenLists, reverse_delete_rule=PULL))
    manager_room = StringField()
    kitchen_room = StringField()
    taxes = DictField(default={'Service': 0, 'CGST': 0, 'SGST': 0})
    home_page_images = DictField(
        default={'0': 'https://liqr-restaurants.s3.ap-south-1.amazonaws.com/default_home_page.png'})
    invoice_no = IntField(default=0)
    kitchens = ListField(ReferenceField(Kitchen, reverse_delete_rule=PULL))
    inventory = ListField(ReferenceField(InventoryItem, reverse_delete_rule=PULL))
    ordering_ability = BooleanField(default=True)
    display_order_buttons = BooleanField(default=True)
    theme_properties = DictField(default={"theme": False})
    currency = StringField(default='$', choices=['$','₹'])

    def to_json(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.food_menu):
            data['food_menu'][key] = self.food_menu[key].to_my_mongo()
        for key, sub_cat in enumerate(self.bar_menu):
            data['bar_menu'][key] = self.bar_menu[key].to_my_mongo()
        for key, add_on in enumerate(self.add_ons):
            data['add_ons'][key] = self.add_ons[key].to_my_mongo()
        for key, staff in enumerate(self.staff):
            data['staff'][key] = self.staff[key].to_my_mongo()
        for key, table in enumerate(self.tables):
            data['tables'][key] = self.tables[key].to_my_mongo()
        for key, table_order in enumerate(self.table_orders):
            data['table_orders'][key] = self.table_orders[key].to_my_mongo()
        for key, order_his in enumerate(self.order_history):
            data['order_history'][key] = self.order_history[key].to_my_mongo()
        for key, ass_req in enumerate(self.assistance_reqs):
            data['assistance_reqs'][key] = self.assistance_reqs[key].to_my_mongo()
        for key, kitchen in enumerate(self.kitchens):
            data['kitchens'][key] = self.kitchens[key].to_my_mongo()
        for key, item in enumerate(self.inventory):
            data['inventory'][key] = self.inventory[key].to_my_mongo()
        for key, home_screen_list in enumerate(self.home_screen_lists):
            data['home_screen_lists'][key] = self.home_screen_lists[key].to_my_mongo()
        for key, navigate_better_list in enumerate(self.navigate_better_lists):
            data['navigate_better_lists'][key] = self.navigate_better_lists[key].to_my_mongo()

        return json_util.dumps(data)

    def fetch_order_lists(self):
        q_list = []
        cook_list = []
        comp_list = []
        for table_order_ob in self.table_orders:
            tabord_dict = json_util.loads(table_order_ob.to_json())
            if tabord_dict['status'] == 'completed':
                comp_list.append(tabord_dict)
                continue
            for order in tabord_dict['orders']:
                for food_item in order['food_list']:
                    if food_item['status'] == 'queued':
                        update_list = q_list
                        index = check_exists(tabord_dict['_id'], update_list)
                        if index >= 0:
                            order_index = check_exists(order['_id'], update_list[index]['orders'])
                            if order_index >= 0:
                                update_list[index]['orders'][order_index]['food_list'].append(food_item)
                            else:
                                o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                                o_app_dict['food_list'] = []
                                o_app_dict['food_list'].append(food_item)
                                update_list[index]['orders'].append(o_app_dict)

                        else:
                            t_app_dict = {k: tabord_dict[k] for k in
                                          ['_id', 'table', 'table_id', 'status', 'timestamp']}
                            o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                            o_app_dict['food_list'] = []
                            o_app_dict['food_list'].append(food_item)
                            t_app_dict['orders'] = []
                            t_app_dict['orders'].append(o_app_dict)
                            update_list.append(t_app_dict)
                    elif food_item['status'] == 'cooking':
                        update_list = cook_list
                        index = check_exists(tabord_dict['_id'], update_list)
                        if index >= 0:
                            order_index = check_exists(order['_id'], update_list[index]['orders'])
                            if order_index >= 0:
                                update_list[index]['orders'][order_index]['food_list'].append(food_item)
                            else:
                                o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                                o_app_dict['food_list'] = []
                                o_app_dict['food_list'].append(food_item)
                                update_list[index]['orders'].append(o_app_dict)

                        else:
                            t_app_dict = {k: tabord_dict[k] for k in
                                          ['_id', 'table', 'table_id', 'status', 'timestamp']}
                            o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                            o_app_dict['food_list'] = []
                            o_app_dict['food_list'].append(food_item)
                            t_app_dict['orders'] = []
                            t_app_dict['orders'].append(o_app_dict)
                            update_list.append(t_app_dict)
                    elif food_item['status'] == 'completed':
                        update_list = comp_list
                        index = check_exists(tabord_dict['_id'], update_list)
                        if index >= 0:
                            order_index = check_exists(order['_id'], update_list[index]['orders'])
                            if order_index >= 0:
                                update_list[index]['orders'][order_index]['food_list'].append(food_item)
                            else:
                                o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                                o_app_dict['food_list'] = []
                                o_app_dict['food_list'].append(food_item)
                                update_list[index]['orders'].append(o_app_dict)

                        else:
                            t_app_dict = {k: tabord_dict[k] for k in
                                          ['_id', 'table', 'table_id', 'status', 'timestamp']}
                            o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                            o_app_dict['food_list'] = []
                            o_app_dict['food_list'].append(food_item)
                            t_app_dict['orders'] = []
                            t_app_dict['orders'].append(o_app_dict)
                            update_list.append(t_app_dict)
        return json_util.dumps({"queue": q_list, "cooking": cook_list, "completed": comp_list})
