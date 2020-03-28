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


class Assistance(Document):
    types = ['water', 'help', 'cutlery', 'tissue', 'cleaning', 'menu', 'ketchup']
    table = StringField()
    user = ReferenceField(User)
    assistance_type = StringField(choices=types)
    timestamp = DateTimeField()
    accepted_by = ReferenceField(Server, default=None)
    meta = {'strict': False}

    def to_json(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        data['table'] = Table.objects(assistance_reqs__in=[self.id])[0].name
        return json_util.dumps(data)


class FoodOptionsMod(EmbeddedDocument):
    size_field = DictField()


class FoodItemMod(EmbeddedDocument):
    name = StringField()
    description = StringField()
    price = StringField()
    instructions = StringField()
    foodoptions = EmbeddedDocumentField(FoodOptionsMod)


class Order(EmbeddedDocument):
    placedby = ReferenceField(User)
    foodlist = MapField(EmbeddedDocumentField(FoodItemMod))


class TableOrder(Document):
    table =StringField()
    orders = ListField(EmbeddedDocumentField(Order))
    timestamp = DateTimeField(default=datetime.datetime.now())

    def to_json(self):
        data = self.to_mongo()
        data['timestamp'] = str(data['timestamp'])
        return json_util.dumps(data)


class Table(Document):
    name = StringField(required=True)
    seats = IntField(required=True)
    servers = ListField(ReferenceField(Server))
    users = ListField(ReferenceField(User))
    nofusers = IntField()
    tableorders = ListField(ReferenceField(TableOrder))
    assistance_reqs = ListField(ReferenceField(Assistance))
    meta = {'strict': False}


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

        return json_util.dumps(data)
