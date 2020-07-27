from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
from backend.mongo.mongodb import Restaurant
from backend.aws_api.s3_interaction import upload_fileobj


def generate_qr_image(table_obj, rest_id, logo_path=''):
    rest_obj = Restaurant.objects(restaurant_id=rest_id).first()
    rest_name = rest_obj.name
    unique_table_id = table_obj.tid
    table_name = table_obj.name
    #     rest_name = "Chicago Style Restaurant In Chicago Illinois"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data('https://liqr.cc/x_' + unique_table_id)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white")

    square_length = 1019
    qr_resize = img_qr.resize((square_length, square_length))

    img = Image.open('liqr_QR_temp.png', 'r')
    left_space = int((img.size[0] - qr_resize.size[0]) / 2)
    #     print(left_space)
    img.paste(qr_resize, (left_space, 360))
    if logo_path != '':
        logo = Image.open(logo_path)
        img.paste(logo, )

    # Writeign rest name
    font_size = 96
    font = ImageFont.truetype("Roboto-Black.ttf", font_size)

    W, H = img.size
    msg = rest_name
    d = ImageDraw.Draw(img)
    w, h = d.textsize(msg, font=font)
    while (W - w) < 20:
        font_size -= 2
        font = ImageFont.truetype("Roboto-Black.ttf", font_size)
        w, h = d.textsize(msg, font=font)

    d.text(((W - w) / 2, 210), msg, font=font, fill="black")

    font_scan_size = font_size - 20
    font_scan = ImageFont.truetype("Roboto-Black.ttf", font_scan_size)

    W, H = img.size
    msg = "Scan for Menu"
    d = ImageDraw.Draw(img)
    w, h = d.textsize(msg, font=font_scan)

    d.text(((W - w) / 2, 330), msg, font=font_scan, fill="black")

    W, H = img.size
    msg = table_name
    d = ImageDraw.Draw(img)
    w, h = d.textsize(msg, font=font_scan)

    d.text(((W - w) / 2, 1320), msg, font=font_scan, fill="black")

    imgobj = io.BytesIO()

    # format here would be something like "JPEG". See below link for more info.
    img.save(imgobj, format='png')
    imgobj.seek(0)

    filename = rest_name.lower().replace(' ', '_') + "_" + table_name.lower().replace(' ', '_') + "_qr.png"

    file_path = rest_id + '/tables/' + filename
    img_url = upload_fileobj(imgobj, 'liqr-restaurants', file_path)

    return img_url
