import pickle
from backend.mongo.mongodb import Restaurant,MainCategory,SubCategory,FoodItem
from backend.mongo.utils import str_2
str_menu=pickle.load(open('half_menu_main.pkl','rb'))

restautant_id = 'BNGHSR0001'

final_list_json=[]


for n,main_cat_name in enumerate(str_menu.loc[:,'main_category'].unique()):
    final_list_json.append({})
    final_list_json[n]['name']=main_cat_name
    final_list_json[n]['description'] = ''
    final_list_json[n]['sub_category'] = []
    for p,sub_cat_name in enumerate(str_menu[str_menu['main_category'].loc[:'sub_category']==main_cat_name].loc[:,'sub_category'].unique()):
        final_list_json[n]['sub_category'].append({})
        final_list_json[n]['sub_category'][p]['name']=sub_cat_name
        final_list_json[n]['sub_category'][p]['description']=''
        final_list_json[n]['sub_category'][p]['priority']=''
        final_list_json[n]['sub_category'][p]['foodlist']=[]
        for q,food_dict in enumerate(str_menu[str_menu['main_category'].loc[:'sub_category']==main_cat_name][str_menu[str_menu['main_category'].loc[:'sub_category']==main_cat_name].loc[:,'sub_category']==sub_cat_name].iterrows()):
            final_list_json[n]['sub_category'][p]['foodlist'].append({})
            final_list_json[n]['sub_category'][p]['foodlist'][q]['name']= food_dict[1]['name']
            final_list_json[n]['sub_category'][p]['foodlist'][q]['description']=food_dict[1]['description']
            final_list_json[n]['sub_category'][p]['foodlist'][q]['price']=food_dict[1]['price']

FoodItem.drop_collection()
SubCategory.drop_collection()

MainCategory.drop_collection()
Restaurant.drop_collection()


main_cat_list = []
for p,main_cat in enumerate(final_list_json):
    sub_cat_list = []
    for q,sub_cat in enumerate(main_cat['sub_category']):
        food_list = []
        for r,food in enumerate(sub_cat['foodlist']):
            food_list.append(FoodItem(name=food['name'],description = food['description'],price=food['price'],food_id = restautant_id+str_2(p)+str_2(q)+str_2(r)).save())
        sub_cat_list.append(SubCategory(name=sub_cat['name'],description=sub_cat['description'],foodlist = food_list,sub_cat_id = restautant_id+str_2(p)+str_2(q)).save())
    main_cat_list.append(MainCategory(name=main_cat['name'],description = main_cat['description'],sub_category = sub_cat_list,main_cat_id = restautant_id+str_2(p)).save())
    
    
houseofcommons=Restaurant(name = 'House of Commons',restaurant_id='BNGHSR0001',unique_id = '0000000001',menu = main_cat_list,address='')
houseofcommons.save()

