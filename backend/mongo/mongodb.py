from mongoengine import *

from backend.config import MONGO_DB, MONGO_HOST
from bson import json_util

conn = connect(MONGO_DB, host = MONGO_HOST,alias='default')


class FoodItem(Document):
    pass


class Table(Document):
    pass


class FoodOptions(DynamicDocument):
    size_field = DictField()
    best_paired_with = ListField(FoodItem)


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
    servers = StringField()

    def to_json(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.menu):
            data['menu'][key] = self.menu[key].to_mymongo()

        return json_util.dumps(data)


class User(Document):
    dine_in_history = DynamicField()
    current_table = ReferenceField(Table)

    meta = {'allow_inheritance': True}


class TempUser(User):
    pass

class Order(Document):
    pass

class RegisteredUser(User):
    name = StringField(required=True)
    email_id = StringField(required=True)
    phone_no = StringField()
    tempuser_ob = ReferenceField(TempUser)


class TempUser(User):
    unique_id = StringField(required=True)
    reguser_ob = ReferenceField(RegisteredUser)


class Table(Document):
    name = StringField(required=True)
    seats = IntField(required=True)
    servers = StringField()
    users = ListField(ReferenceField(User))
    nofusers = IntField()
    orders = ListField(ReferenceField(Order))


class FoodOptionsMod(EmbeddedDocument):
    size_field = DictField()


class FoodItemMod(EmbeddedDocument):
    name = StringField()
    description = StringField()
    price = StringField()
    instructions = StringField()
    foodoptions = EmbeddedDocumentField(FoodOptionsMod)


class Order(Document):
    placedby = ListField(ReferenceField(User))
    table = ReferenceField(Table)
    foodlist = MapField(EmbeddedDocumentField(FoodItemMod))
    customer_type = StringField()
