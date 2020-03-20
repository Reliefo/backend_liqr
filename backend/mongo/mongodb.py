from mongoengine import *

from backend.config import MONGO_DB, MONGO_HOST

conn = connect(MONGO_DB, host = MONGO_HOST,alias='default')

class FoodItem(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    price = StringField(required=True)
    food_id = StringField(required=True)


class SubCategory(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    sub_cat_id = StringField(required=True)
    foodlist = ListField(ReferenceField(FoodItem), required=True)

    def to_mymongo(self):
        data = self.to_mongo()
        for key, fooditem in enumerate(self.foodlist):
            data['foodlist'][key] = self.foodlist[key].to_mongo()
        #             reply["to_users"] = {"User": {"username": user.username} }

        return data

    meta = {'allow_inheritance': True}


class MainCategory(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    main_cat_id = StringField(required=True)
    sub_category = ListField(ReferenceField(SubCategory), required=True)

    def to_mymongo(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.sub_category):
            data['sub_category'][key] = self.sub_category[key].to_mymongo()
        #             reply["to_users"] = {"User": {"username": user.username} }

        return data


class Restaurant(Document):
    name = StringField(required=True)
    restaurant_id = StringField(required=True)
    unique_id = StringField(required=True)
    menu = ListField(ReferenceField(MainCategory), required=True)
    address = StringField()
    tables = StringField()
    servers = StringField()

    def to_json(self):
        data = self.to_mongo()
        for key, sub_cat in enumerate(self.menu):
            data['menu'][key] = self.menu[key].to_mymongo()
        #             reply["to_users"] = {"User": {"username": user.username} }

        return json_util.dumps(data)

    meta = {'allow_inheritance': True}