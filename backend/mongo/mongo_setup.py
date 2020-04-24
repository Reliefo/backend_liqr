import pickle
import math
from backend.mongo.query import *


def setup_mongo():
    final_list_json = pickle.load(open('pkls/final_usable_json.pkl', 'rb'))
    bar_final_json = pickle.load(open('pkls/bar_final_json.pkl', 'rb'))

    FoodItem.drop_collection()
    Category.drop_collection()
    Restaurant.drop_collection()
    Table.drop_collection()
    TempUser.drop_collection()
    RegisteredUser.drop_collection()
    Staff.drop_collection()
    Assistance.drop_collection()
    TableOrder.drop_collection()
    Order.drop_collection()
    User.drop_collection()
    house_of_commons = Restaurant(name='House of Commons', restaurant_id='BNGHSR0001').save()

    cat_list = []
    for p, category in enumerate(final_list_json):
        food_list = []
        for r, food in enumerate(category['food_list']):
            food_list.append(FoodItem(name=food['name'], description=food['description'], price=food['price'],
                                      restaurant=str(house_of_commons.id)).save())
        cat_list.append(
            Category(name=category['name'], description=category['description'], food_list=food_list).save())

    bar_cat_list = []
    for p, category in enumerate(bar_final_json):
        food_list = []
        for r, food in enumerate(category['food_list']):
            food_list.append(FoodItem(name=food['name'], description=food['description'], price=food['price'],
                                      restaurant=str(house_of_commons.id)).save())
        bar_cat_list.append(
            Category(name=category['name'], description=category['description'], food_list=food_list).save())

    house_of_commons.update(set__food_menu=cat_list)
    house_of_commons.update(set__bar_menu=bar_cat_list)

    home_screen_tags = ['most_popular', 'chefs_special', 'eat_with_drinks', 'eat_with_beer', 'healty_bites',
                        'fill_stomach']
    house_of_commons.update(set__home_screen_tags=home_screen_tags)

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

    names = pickle.load(open('pkls/indian_names.pkl', 'rb'))
    girls_name = names[0]
    boys_name = names[1]

    total = {}
    sers = []
    tabs = []
    for n, table in enumerate(Table.objects):
        #     print(math.floor(n/1.5))
        sers.append(math.floor(n / 1.5))
        tabs.append(n)
        if (n + 1) % 3 == 0:
            total[tuple(set(sers))] = tabs
            sers = []
            tabs = []

    # assigning tables to servers
    for i in range(10):
        if i < 5:
            staff = Staff(name=girls_name[np.random.randint(len(girls_name))]).save()
            Restaurant.objects[0].update(push__staff=staff.to_dbref())
        else:
            staff = Staff(name=boys_name[np.random.randint(len(boys_name))]).save()
            Restaurant.objects[0].update(push__staff=staff.to_dbref())

    for key in total.keys():
        for tab in total[key]:
            Table.objects[tab].update(push__staff=Staff.objects[key[0]].to_dbref())

        for tab in total[key]:
            Table.objects[tab].update(push__staff=Staff.objects[key[1]].to_dbref())
