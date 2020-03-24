from backend.mongo.mongodb import *

def user_scan(table_id, unique_id, email_id='dud'):
    scanned_table = Table.objects.get(id=table_id)

    if (email_id == 'dud'):
        tempuser = TempUser.objects.filter(unique_id=unique_id)
        if (len(tempuser) > 0):
            tempuser[0].update(set__current_table=scanned_table.to_dbref())
            scanned_table.update(push__users=tempuser[0].to_dbref())
        else:
            tempuser = TempUser(unique_id=unique_id, current_table=scanned_table.to_dbref()).save()
            scanned_table.update(push__users=tempuser.to_dbref())
        scanned_table.update(inc__nofusers=1)
    else:
        reg_user = RegisteredUser.objects.filter(email_id=email_id)[0]
        scanned_table.update(push__users=reg_user)
        reg_user.update(set__current_table=scanned_table.to_dbref())
        scanned_table.update(inc__nofusers=1)

def order_placement(input_order):
    users_list = []
    for userid in input_order['placedby']:
        users_list.append(User.objects.get(id=userid).to_dbref())
    ordered_list = []
    for foodid in input_order['foodlist']:
        ordered_list.append(FoodItemMod.from_json(FoodItem.objects(id=foodid).exclude("id")[0].to_json()))
    ordered_table = Table.objects.get(id=input_order['table'])
    order_ob=Order(placedby = users_list,table = ordered_table.to_dbref(),foodlist={str(key):ordered_list[key] for key in range(len(ordered_list))},customer_type=input_order['order_type']).save()
    ordered_table.update(push__orders=order_ob.to_dbref())
    return True

def fetch_order():
    order = Order.objects[5].to_json()
    return order