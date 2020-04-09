import pickle

from backend.mongo.query import *


def setup_mongo():
    final_list_json = pickle.load(open('final_usable_json.pkl', 'rb'))

    FoodItem.drop_collection()
    SubCategory.drop_collection()
    MainCategory.drop_collection()
    Restaurant.drop_collection()
    Table.drop_collection()
    TempUser.drop_collection()
    RegisteredUser.drop_collection()
    Staff.drop_collection()
    Assistance.drop_collection()
    TableOrder.drop_collection()
    Order.drop_collection()
    User.drop_collection()

    main_cat_list = []
    for p, main_cat in enumerate(final_list_json):
        sub_cat_list = []
        for q, sub_cat in enumerate(main_cat['sub_category']):
            food_list = []
            for r, food in enumerate(sub_cat['food_list']):
                food_list.append(
                    FoodItem(name=food['name'], description=food['description'], price=food['price']).save())
            sub_cat_list.append(
                SubCategory(name=sub_cat['name'], description=sub_cat['description'], foodlist=food_list).save())
        main_cat_list.append(
            MainCategory(name=main_cat['name'], description=main_cat['description'], sub_category=sub_cat_list).save())

    house_of_commons = Restaurant(name='House of Commons', restaurant_id='BNGHSR0001', menu=main_cat_list, address='')
    house_of_commons.save()

    table_list = []
    for n in range(1, 16):
        table_list.append(Table(name='table' + str(n), seats=6, no_of_users=0).save().to_dbref())

    Restaurant.objects[0].update(set__tables=table_list)
    akshay = TempUser(unique_id="hfirnivnhhwocn34534no34n34r")

    akshay.save()

    RegisteredUser(name='Akshay', email_id='akshay.dn5@gmail.com', phone_no='8660961089').save()

    RegisteredUser.objects(name='Akshay', email_id='akshay.dn5@gmail.com', phone_no='8660961089').update(
        set__tempuser_ob=akshay.to_dbref())

    user_scan(str(table_list[2].id), 'hidnfvidfkvmsdmv')

    user_scan(str(table_list[2].id), 'hidnfvidvdff1kvmsadmv')

    user_scan(str(table_list[2].id), 'hidnfvidvdffaskvmsadmv')

    user_scan(str(table_list[2].id), 'hidnfvidvdffvf1kvmsadmv')

    user_scan(str(table_list[2].id), '', email_id='akshay.dn5@gmail.com')

    for food_ob in FoodItem.objects:
        if re.search('/', food_ob.price):
            if re.search('/', food_ob.name):
                options = custom_splitter(food_ob.name)

            elif re.search('/', food_ob.description):
                options = custom_splitter(food_ob.description)
            prices = food_ob.price.split('/')
            if len(options) == len(prices):
                options = {k: v for k, v in zip(options, prices)}
                FoodItem.objects.get(id=food_ob.id).update(set__food_options=FoodOptions(options=options))
            else:
                left_out = food_ob.id
    left_out_options = {k: v for k, v in
                        zip(custom_splitter(' Vegetables/chicken/prawns, Served'), '250/280/300'.split('/'))}
    FoodItem.objects.get(id=left_out).update(
        set__food_options=FoodOptions(options=left_out_options, choices=['Red', 'Green']))
