import traceback
from flask_socketio import emit
from .. import socket_io, our_namespace
from backend.mongo.query import *
import boto3
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode

s3_res = boto3.resource(
    "s3",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def generate_qr_image(justmenu_id, name):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data('https://order.liqr.cc/jm?rid=' + justmenu_id)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")

    qr_resize = img_qr.resize((850, 850))

    img = Image.open('default.png', 'r')
    img.paste(qr_resize, (195, 360))

    # Writeign rest name
    font = ImageFont.truetype("Roboto-Black.ttf", 96)

    W, H = img.size
    msg = name
    d = ImageDraw.Draw(img)
    w, h = d.textsize(msg, font=font)

    d.text(((W - w) / 2, 150), msg, font=font, fill="black")

    font_scan = ImageFont.truetype("Roboto-Black.ttf", 76)

    W, H = img.size
    msg = "Scan for Menu"
    d = ImageDraw.Draw(img)
    w, h = d.textsize(msg, font=font_scan)

    d.text(((W - w) / 2, 330), msg, font=font_scan, fill="black")

    imgobj = io.BytesIO()

    # format here would be something like "JPEG". See below link for more info.
    img.save(imgobj, format='png')
    imgobj.seek(0)

    filename = name.lower().replace(' ', '_') + "_qr.png"

    s3.upload_fileobj(imgobj, 'liqr-justmenu', justmenu_id + '/' + filename, ExtraArgs={'ACL': 'public-read'})
    img_url = "https://s3-ap-south-1.amazonaws.com/liqr-justmenu/" + justmenu_id + "/" + filename

    return img_url


def configure_justmenu(input_dict):
    [request_type, element_type] = input_dict['type'].split('_', 1)
    if request_type == 'add':
        name = input_dict['name']
        just = JustMenu(name=name, created=datetime.now()).save()
        qr_code_url = generate_qr_image(str(just.id), just.name)
        just.qr = qr_code_url
        just.save()
    elif request_type == 'image':
        object_key = input_dict['image_url'].split('/', 4)[-1]
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
            object_key = image_url.split('/', 4)[-1]
            image = s3_res.Object('liqr-justmenu', object_key)
            image.delete()
        just.delete()
        input_dict['status'] = 'deleted'
    input_dict['justmenu_object'] = json_util.loads(just.to_json())
    return json_util.dumps(input_dict)


@socket_io.on('justmenu_configuration', namespace=our_namespace)
def justmenu_configuration(message):
    input_dict = json_util.loads(message)

    emit('justmenu_config', configure_justmenu(input_dict))


@socket_io.on('fetch_justmenu', namespace=our_namespace)
def fetch_justmenu(message):
    just_list = []
    for just in JustMenu.objects:
        just_list.append(json_util.loads(just.to_json()))
    emit('here_justmenu', json_util.dumps(just_list))
