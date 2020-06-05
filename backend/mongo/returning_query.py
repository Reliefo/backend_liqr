from backend.mongo.utils import *


def return_staff_details(staff_id):
    return Staff.objects.get(id=staff_id).to_json()


def fetch_requests_queue(staff_id, rest_id):
    staff = Staff.objects.get(id=staff_id)
    requests_queue = []
    for table in Restaurant.objects(restaurant_id=rest_id).first().tables:
        if staff in table.staff:
            for request in table.requests_queue:
                if not requests_queue:
                    requests_queue.append(request)
                    continue
                new_datetime = datetime.strptime(request['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                for n in range(len(requests_queue) - 1, -1, -1):
                    this_datetime = datetime.strptime(requests_queue[n]['timestamp'], "%Y-%m-%d %H:%M:%S.%f")
                    if new_datetime > this_datetime:
                        requests_queue.insert(n + 1, request)
                        break
    return json_util.dumps({'requests_queue': requests_queue})


def return_user_details(user_id):
    return User.objects.get(id=user_id).to_json()


def return_table_details(user_id):
    current_table_id = User.objects.get(id=user_id).current_table_id
    try:
        return Table.objects.get(id=current_table_id).to_cust_json()
    except ValidationError:
        return Table.objects(name='Not a table', seats=420)[0].to_json()


def return_restaurant(rest_id):
    return Restaurant.objects(restaurant_id=rest_id)[0].to_json()


def home_screen_lists(rest_id):
    home_screen = {'navigate_better': {}}
    for tag in Restaurant.objects(restaurant_id=rest_id).first().home_screen_tags:
        home_screen[tag] = [str(food.id) for food in
                            FoodItem.objects.filter(restaurant_id=rest_id).filter(tags__in=[tag])]
    for tag in Restaurant.objects(restaurant_id=rest_id).first().navigate_better_tags:
        home_screen['navigate_better'][tag] = [str(food.id) for food in
                                               FoodItem.objects.filter(restaurant_id=rest_id).filter(tags__in=[tag])]
    return json_util.dumps(home_screen)


def return_restaurant_customer(rest_id):
    return Restaurant.objects(restaurant_id=rest_id) \
        .exclude('staff') \
        .exclude('tables') \
        .exclude("table_orders").first().to_json()


def return_restaurant_kitchen(rest_id):
    return Restaurant.objects(restaurant_id=rest_id) \
        .only('id') \
        .only('name') \
        .only("restaurant_id").first().to_json()