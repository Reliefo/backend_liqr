import traceback
from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
import boto3

s3_res = boto3.resource(
    "s3",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def configure_justmenu(input_dict):
    [request_type, element_type] = input_dict['type'].split('_', 1)
    if request_type == 'add':
        name = input_dict['name']
        just = JustMenu(name=name, created=datetime.now()).save()
    elif request_type == 'image':
        object_key = input_dict['image_url'].split('/', 3)[-1]
        image = s3_res.ObjectAcl('liqr-justmenu', object_key)
        image.put(ACL='public-read')
        just = JustMenu.objects.get(id=input_dict['justmenu_id'])
        just.menu.append(input_dict['image_url'])
        just.save()
    elif request_type == 'delimage':
        object_key = input_dict['image_url'].split('/', 3)[-1]
        image = s3_res.Object('liqr-justmenu', object_key)
        image.delete()
        just = JustMenu.objects.get(id=input_dict['justmenu_id'])
        just.menu.remove(input_dict['image_url'])
        just.save()
    elif request_type == 'delete':
        just = JustMenu.objects.get(id=input_dict['justmenu_id'])
        for image_url in just.menu:
            object_key = image_url.split('/', 3)[-1]
            image = s3_res.Object('liqr-justmenu', object_key)
            image.delete()
        just.delete()
        input_dict['status'] = 'delete'
    input_dict['justmenu_config'] = json_util.loads(just.to_json())
    return json_util.dumps(input_dict)


@socket_io.on('justmenu_configuration', namespace=our_namespace)
def justmenu_configuration(message):
    input_dict = json_util.loads(message)

    emit('justmenu', configure_justmenu(input_dict))


@socket_io.on('fetch_justmenu', namespace=our_namespace)
def fetch_justmenu(message):
    just_list = []
    for just in JustMenu.objects:
        just_list.append(json_util.loads(just.to_json()))
    emit('here_justmenu', json_util.dumps(just_list))
