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


class Server(Document):
    name = StringField()
    assistance_history = MapField(ListField(ReferenceField(Assistance)))
    order_history = MapField(ListField(ReferenceField(TableOrder)))
    def to_mymongo(self):
        data = self.to_mongo()

        return data

class Assistance(Document):
    types = ['water', 'help', 'cutlery', 'tissue', 'cleaning', 'menu', 'ketchup']
    table = StringField()
    user = ReferenceField(User)
    assistance_type = StringField(choices=types)
    timestamp = DateTimeField()
    accepted_by = ReferenceField(Server, default=None)
    meta = {'strict': False}

    def to_mymongo(self):
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
    size_field = DictField()


class FoodItemMod(EmbeddedDocument):
    food_id = StringField()
    name = StringField()
    description = StringField()
    price = StringField()
    instructions = StringField()
    quantity = IntField()
    status = StringField(choices=['queued', 'cooking', 'completed'])
    foodoptions = EmbeddedDocumentField(FoodOptionsMod)


class Order(Document):
    placedby = ReferenceField(User)
    foodlist = ListField(EmbeddedDocumentField(FoodItemMod))
    status = StringField(choices=['queued', 'juststarted', 'cooking', 'almostdone', 'completed'], default='queued')

    def fetch_fooditem(self, food_id):
        for fooditem in self.foodlist:
            if (fooditem.food_id == food_id):
                return fooditem.to_json()
        return "Food item not found"


class TableOrder(Document):
    table = StringField()
    orders = ListField(ReferenceField(Order))
    status = StringField(choices=['queued', 'juststarted', 'cooking', 'almostdone', 'completed'], default='queued')
    timestamp = DateTimeField(default=datetime.datetime.now())

    def to_mymongo(self):
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
    servers = ListField(ReferenceField(Server))
    users = ListField(ReferenceField(User))
    nofusers = IntField()
    qd_tableorders = ListField(ReferenceField(TableOrder))
    cook_tableorders = ListField(ReferenceField(TableOrder))
    com_tableorders = ListField(ReferenceField(TableOrder))
    assistance_reqs = ListField(ReferenceField(Assistance))
    meta = {'strict': False}

    def to_mymongo(self):
        data = self.to_mongo()
        for key, tableorder in enumerate(self.qd_tableorders):
            data['qd_tableorders'][key] = self.qd_tableorders[key].to_mymongo()
        for key, tableorder in enumerate(self.cook_tableorders):
            data['cook_tableorders'][key] = self.cook_tableorders[key].to_mymongo()
        for key, tableorder in enumerate(self.com_tableorders):
            data['com_tableorders'][key] = self.com_tableorders[key].to_mymongo()
        for key, ass_req in enumerate(self.assistance_reqs):
            data['assistance_reqs'][key] = self.assistance_reqs[key].to_mymongo()

        return data


class FoodOptions(DynamicDocument):
    size_field = DictField()
    best_paired_with = ListField(StringField())


class FoodItem(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    price = StringField(required=True)
    foodoptions = ReferenceField(FoodOptions)

    def to_mymongo(self):
        data = self.to_mongo()
        if (self.foodoptions):
            data['foodoptions'] = self.foodoptions.to_mongo()

        return data

    def to_json(self):
        data = self.to_mongo()
        if (self.foodoptions):
            data['foodoptions'] = self.foodoptions.to_mongo()

        return json_util.dumps(data)


class SubCategory(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    foodlist = ListField(ReferenceField(FoodItem), required=True)

    def to_mymongo(self):
        data = self.to_mongo()
        for key, fooditem in enumerate(self.foodlist):
            data['foodlist'][key] = self.foodlist[key].to_mymongo()

        return data


class MainCategory(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    sub_category = ListField(ReferenceField(SubCategory), required=True)

    def to_mymongo(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.sub_category):
            data['sub_category'][key] = self.sub_category[key].to_mymongo()

        return data


class Restaurant(Document):
    name = StringField(required=True)
    restaurant_id = StringField(required=True)
    menu = ListField(ReferenceField(MainCategory), required=True)
    address = StringField()
    tables = ListField(ReferenceField(Table))
    servers = ListField(ReferenceField(Server))

    def to_json(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.menu):
            data['menu'][key] = self.menu[key].to_mymongo()
        for key, server in enumerate(self.servers):
            data['servers'][key] = self.servers[key].to_mymongo()
        for key, table in enumerate(self.tables):
            data['tables'][key] = self.tables[key].to_mymongo()

        return json_util.dumps(data)
