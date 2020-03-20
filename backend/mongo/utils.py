from backend.mongo.mongodb import Restaurant,MainCategory, SubCategory,FoodItem
import json

def return_restaurant():
    return json.loads(Restaurant.objects[0].to_json())

def str_2(number):
    string = str(number)
    if(len(string)==1):
        return '0'+string
    else:
        return string
