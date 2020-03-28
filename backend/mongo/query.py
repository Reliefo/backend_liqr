from backend.mongo.mongodb import *
from backend.mongo.utils import *
import time

li = [(i, j) for i, j in zip(range(10), [k for k in range(10)])]
np.random.shuffle(li)

def fetch_order(n):
    return TableOrder.objects[n].to_json()

def user_scan(table_id, unique_id, email_id='dud'):
    scanned_table = Table.objects.get(id=table_id)
    if (email_id == 'dud'):
        tempuser = TempUser.objects.filter(unique_id=unique_id)
        if (len(tempuser) > 0):
            tempuser[0].update(set__current_table_id=str(scanned_table.id))
            scanned_table.update(push__users=tempuser[0].to_dbref())
        else:
            tempuser = TempUser(unique_id=unique_id, current_table_id=str(scanned_table.id)).save()
            scanned_table.update(push__users=tempuser.to_dbref())
        scanned_table.update(inc__nofusers=1)
    else:
        reg_user = RegisteredUser.objects.filter(email_id=email_id)[0]
        scanned_table.update(push__users=reg_user)
        reg_user.update(set__current_table_id=str(scanned_table.id))
        scanned_table.update(inc__nofusers=1)


def generate_order():
    input_order = {}
    input_order['table'] = random_table()
    input_order['orders'] = []
    for n in range(np.random.randint(1, 5)):
        input_order['orders'].append({})
        input_order['orders'][n]['placedby'] = random_user()
        input_order['orders'][n]['foodlist'] = random_food_list()
    return input_order


def order_placement(input_order):
    ordered_table = Table.objects.get(id=input_order['table'])
    tableorder = TableOrder(table=ordered_table.name, timestamp=datetime.datetime.now())
    for order in input_order['orders']:
        foodlist = {str(key): FoodItemMod.from_json(FoodItem.objects(id=foodid).exclude('id')[0].to_json()) for
                    key, foodid in enumerate(order['foodlist'])}
        tableorder.orders.append(Order(placedby=User.objects.get(id=order['placedby']).to_dbref(), foodlist=foodlist))
        tableorder.save()
    ordered_table.update(push__tableorders=tableorder.to_dbref())


def generate_asstype():
    assist_input = {'table': random_table(), 'user': random_user(),
                    'assistancetype': Assistance.types[np.random.randint(len(Assistance.types))]}
    return assist_input


def assistance_req(assist_input):
    curr_table = Table.objects.get(id=assist_input['table'])
    curr_ass = Assistance(user=User.objects.get(id=assist_input['user']).to_dbref())
    curr_ass.assistance_type = assist_input['assistancetype']
    curr_ass.timestamp = datetime.datetime.now()
    curr_ass.save()
    curr_table.update(push__assistance_reqs=curr_ass.to_dbref())
    return curr_ass


def send_assistance_req(assist_id):
    table=Table.objects(assistance_reqs__in=[assist_id])[0]
    for server in table.servers:
        if(np.random.randint(3)):
            time.sleep(1)
            Assistance.objects.get(id=assist_id).update(set__accepted_by=server.to_dbref())
            return server.name
    time.sleep(3)
    for server in Server.objects:
        if(np.random.randint(3)):
            time.sleep(1)
            Assistance.objects.get(id=assist_id).update(set__accepted_by=server.to_dbref())
            return server.name