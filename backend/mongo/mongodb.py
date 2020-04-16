from mongoengine import *
import datetime
from backend.config import MONGO_DB, MONGO_HOST
from bson import json_util

conn = connect(MONGO_DB, host=MONGO_HOST, alias='default')


class TableOrder(Document):
    pass


class User(Document):
    dine_in_history = DynamicField()
    current_table_id = StringField()
    personal_cart = ListField(ReferenceField(TableOrder))
    meta = {'allow_inheritance': True}


class TempUser(User):
    pass


class RegisteredUser(User):
    name = StringField(required=True)
    email_id = StringField(required=True)
    phone_no = StringField()
    tempuser_ob = ReferenceField(TempUser)


class TempUser(User):
    unique_id = StringField(required=True)
    reguser_ob = ReferenceField(RegisteredUser)


class Assistance(Document):
    pass


class Staff(Document):
    name = StringField()
    assistance_history = MapField(ListField(ReferenceField(Assistance)))
    order_history = MapField(ListField(ReferenceField(TableOrder)))

    def to_my_mongo(self):
        data = self.to_mongo()

        return data


class Assistance(Document):
    types = ['water', 'help', 'cutlery', 'tissue', 'cleaning', 'menu', 'ketchup']
    table = StringField()
    user = ReferenceField(User)
    assistance_type = StringField(choices=types)
    timestamp = DateTimeField()
    accepted_by = ReferenceField(Staff, default=None)
    meta = {'strict': False}

    def to_my_mongo(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        data['table'] = Table.objects(assistance_reqs__in=[self.id])[0].name

        return data

    def to_json(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        data['table'] = Table.objects(assistance_reqs__in=[self.id])[0].name
        return json_util.dumps(data)


class FoodOptionsMod(EmbeddedDocument):
    options = DictField()
    choices = ListField()


class FoodItemMod(EmbeddedDocument):
    food_id = StringField()
    name = StringField()
    description = StringField()
    price = StringField()
    instructions = StringField()
    quantity = IntField()
    status = StringField(choices=['queued', 'cooking', 'completed'])
    food_options = EmbeddedDocumentField(FoodOptionsMod)


class Order(Document):
    placed_by = ReferenceField(User)
    food_list = ListField(EmbeddedDocumentField(FoodItemMod))
    status = StringField(choices=['queued', 'juststarted', 'cooking', 'almostdone', 'completed'], default='queued')

    def fetch_food_item(self, food_id):
        for food_item in self.food_list:
            if food_item.food_id == food_id:
                return food_item.to_json()
        return "Food item not found"


class TableOrder(Document):
    table = StringField()
    table_id = StringField()
    orders = ListField(ReferenceField(Order))
    status = StringField(choices=['queued', 'juststarted', 'cooking', 'almostdone', 'completed'], default='queued')
    timestamp = DateTimeField(default=datetime.datetime.now())

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


class Table(Document):
    name = StringField(required=True)
    seats = IntField(required=True)
    staff = ListField(ReferenceField(Staff))
    users = ListField(ReferenceField(User))
    no_of_users = IntField()
    table_orders = ListField(ReferenceField(TableOrder))
    assistance_reqs = ListField(ReferenceField(Assistance))
    meta = {'strict': False}

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, table_order in enumerate(self.table_orders):
            data['table_orders'][key] = self.table_orders[key].to_my_mongo()
        for key, ass_req in enumerate(self.assistance_reqs):
            data['assistance_reqs'][key] = self.assistance_reqs[key].to_my_mongo()

        return data


class FoodOptions(EmbeddedDocument):
    options = DictField()
    choices = ListField()


class FoodItem(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    price = StringField(required=True)
    tags = ListField(StringField())
    food_options = EmbeddedDocumentField(FoodOptions)

    def to_my_mongo(self):
        data = self.to_mongo()
        if self.food_options:
            data['food_options'] = self.food_options.to_mongo()

        return data

    def to_json(self):
        data = self.to_mongo()
        if self.food_options:
            data['food_options'] = self.food_options.to_mongo()

        return json_util.dumps(data)


class Category(Document):
    name = StringField(required=True)
    description = StringField()
    food_list = ListField(ReferenceField(FoodItem))

    def to_my_mongo(self):
        data = self.to_mongo()
        for key, food_item in enumerate(self.food_list):
            data['food_list'][key] = self.food_list[key].to_my_mongo()

        return data


def check_exists(order_id, order_list):
    for n, order in enumerate(order_list):
        if order_id == order['_id']:
            return n
    return -1


class Restaurant(Document):
    name = StringField(required=True)
    restaurant_id = StringField(required=True)
    food_menu = ListField(ReferenceField(Category), required=True)
    bar_menu = ListField(ReferenceField(Category))
    address = StringField()
    tables = ListField(ReferenceField(Table, reverse_delete_rule=PULL))
    staff = ListField(ReferenceField(Staff, reverse_delete_rule=PULL))
    table_orders = ListField(ReferenceField(TableOrder))
    assistance_reqs = ListField(ReferenceField(Assistance))

    def to_json(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.food_menu):
            data['food_menu'][key] = self.food_menu[key].to_my_mongo()
        for key, sub_cat in enumerate(self.bar_menu):
            data['bar_menu'][key] = self.bar_menu[key].to_my_mongo()
        for key, staff in enumerate(self.staff):
            data['staff'][key] = self.staff[key].to_my_mongo()
        for key, table in enumerate(self.tables):
            data['tables'][key] = self.tables[key].to_my_mongo()

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
                            t_app_dict = {k: tabord_dict[k] for k in ['_id', 'table', 'status', 'timestamp']}
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
                            t_app_dict = {k: tabord_dict[k] for k in ['_id', 'table', 'status', 'timestamp']}
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
                            t_app_dict = {k: tabord_dict[k] for k in ['_id', 'table', 'status', 'timestamp']}
                            o_app_dict = {k: order[k] for k in ['_id', 'placed_by', 'status']}
                            o_app_dict['food_list'] = []
                            o_app_dict['food_list'].append(food_item)
                            t_app_dict['orders'] = []
                            t_app_dict['orders'].append(o_app_dict)
                            update_list.append(t_app_dict)
        return json_util.dumps({"queue": q_list, "cooking": cook_list, "completed": comp_list})
