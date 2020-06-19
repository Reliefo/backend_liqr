from io import BytesIO
from functools import partial
from backend.mongo.mongodb import *
from backend.mongo.utils import *
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle
from reportlab.platypus import Table as TablePDF
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import math
import boto3
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('New Times Bo', 'Times New Roman Gras 700.ttf'))
styles = getSampleStyleSheet()

client = boto3.client(
    "s3",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def upload_pdf_bill(pdf_file, restaurant_id, invoice_no):
    key_location = restaurant_id + '/bills/' + invoice_no + '.pdf'
    bucket_name = 'liqr-restaurants'
    client.upload_fileobj(Fileobj=pdf_file,
                          Bucket=bucket_name,
                          Key=key_location,
                          ExtraArgs={'ACL': 'public-read'})
    image_link = 'https://' + bucket_name + '.s3.ap-south-1.amazonaws.com/' + key_location
    return image_link


def myFirstPage(canvas, doc, restaurant, table_ob):
    address_split = restaurant.address.split()
    first_half = math.ceil(0.4 * len(address_split))
    address1 = ' '.join(address_split[:first_half])
    address2 = ' '.join(address_split[first_half:])
    phone1 = restaurant.phone_nos[0]
    phone2 = None
    if len(restaurant.phone_nos) > 1:
        phone2 = restaurant.phone_nos[1]
    invoice_no = str_n(restaurant.invoice_no + 1, 7)
    users = [user.name for user in table_ob.users]
    date = str(datetime.now()).split()[0]
    time = str(datetime.now()).split()[1].split('.')[0]

    canvas.saveState()
    canvas.setLineWidth(.3)
    canvas.setFont('Times-Bold', 24)
    canvas.drawString(30, 780, restaurant.name)
    canvas.setFont('Times-Roman', 12)
    canvas.drawString(33, 760, address1)
    canvas.drawString(33, 745, address2)
    canvas.drawString(33, 730, 'Phone No.: ')
    canvas.drawString(90, 730, phone1)
    if phone2:
        canvas.drawString(33, 715, 'Phone No.: ')
        canvas.drawString(90, 715, phone2)
    canvas.setFont('Times-Bold', 14)
    canvas.drawString(400, 782, "Invoice No.: " + invoice_no)
    canvas.drawString(33, 680, "Bill To: " + str(len(users)) + " People")
    canvas.setFont('Times-Roman', 12)
    canvas.drawString(33, 660, ", ".join(users))
    canvas.drawString(400, 760, "Date: " + date)
    canvas.drawString(400, 745, "Time: " + time)
    canvas.drawString(400, 730, "Billing Table: " + table_ob.name)
    canvas.line(33, 640, 580, 640)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, restaurant.name))
    canvas.restoreState()


def myLaterPages(canvas, doc, restaurant):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, restaurant.name))
    canvas.restoreState()


def customization(food):
    cust = ''
    for key in food['food_options'].keys():
        if food['food_options'][key]:
            if key == 'options':
                cust += key + ": " + food['food_options'][key][0]['option_name'] + ' '
            elif key == 'choices':
                cust += food['food_options'][key][0] + ' '
    return cust


def generate_bill(table_ob, restaurant):
    current_list = []

    for table_ord in table_ob.table_orders:
        table_dict = json_util.loads(table_ord.to_json())
        for order in table_dict['orders']:
            for new_food in order['food_list']:
                added = False
                for food in current_list:
                    if new_food['food_id'] == food['food_id']:
                        food['quantity'] = food['quantity'] + new_food['quantity']
                        added = True
                if not added:
                    current_list.append(new_food)
    item_rows = []
    pretax = 0
    for food in current_list:
        item_rows.append(
            [Paragraph(food['name'],styles['BodyText']), customization(food) if 'food_options' in food.keys() else None, int(food['price']),
             food['quantity'], int(food['price']) * food['quantity']])
        pretax += int(food['price']) * food['quantity']
    total_tax = restaurant.taxes['Service'] + restaurant.taxes['SGST'] + restaurant.taxes['CGST']
    taxes = total_tax * pretax / 100
    total_amount = round(pretax + taxes, 2)
    taxes = round(taxes,2)

    pdf_file = BytesIO()
    doc = SimpleDocTemplate(pdf_file)

    Story = [Spacer(1, 1.7 * inch)]
    PS = ParagraphStyle(name='Welcome', parent=styles["Heading2"], alignment=1)
    welcome_message = ("Welcome to " + restaurant.name)
    p = Paragraph(welcome_message, PS)
    Story.append(p)
    Story.append(Spacer(1, 0.2 * inch))

    TitleStyle = ParagraphStyle(name='Table Title', parent=styles['Normal'], alignment=1)
    PretaxTotalStyle = ParagraphStyle(name='pretax', parent=styles['Normal'])
    TotalStyle = ParagraphStyle(name='Tatotalitle', parent=styles['Normal'], alignment=2, fontName='New Times Bo',
                                fontSize=11)
    RawTitles = ['Item Name', 'Customization', 'Price', 'Qty', 'Subtotal']
    Titles = [Paragraph('<b>{}</b>'.format(title), TitleStyle) for title in RawTitles]
    PreTotalRow = [Paragraph('<b>Pretax Total</b>', PretaxTotalStyle), '', '', '',
                   Paragraph('<b>₹ {}</b>'.format(pretax), TotalStyle)]
    TaxesRow = [Paragraph('<b>Taxes {}%</b>'.format(total_tax), PretaxTotalStyle), '', '', '',
                Paragraph('<b>₹ {}</b>'.format(taxes), TotalStyle)]
    TotalRow = [Paragraph('<b>Total</b>', PretaxTotalStyle), '', '', '',
                Paragraph('<b>₹ {}</b>'.format(total_amount), TotalStyle)]

    data = [Titles] + item_rows + [PreTotalRow] + [TaxesRow] + [TotalRow]

    columnSizes = [3 * inch, 2 * inch, 0.6 * inch, 0.4 * inch, 0.8 * inch]
    t = TablePDF(data, columnSizes)
    t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                           ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                           #                        ('VALIGN',(0,0),(-1,0),'MIDDLE'),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ]))

    Story.append(t)
    Story.append(Spacer(1, 0.2 * inch))

    RupeeStyle = ParagraphStyle(name='Tatotaitle', parent=styles['Normal'], alignment=2, fontName='New Times Bo',
                                fontSize=14)

    last_P = Paragraph('Total Bill = ₹ ' + str(total_amount), RupeeStyle)

    Story.append(last_P)
    Story.append(Spacer(1, 0.2 * inch))
    bogustext = ("Thank you, visit again")
    p = Paragraph(bogustext, PS)
    Story.append(p)

    doc.build(Story, onFirstPage=partial(myFirstPage, restaurant=restaurant, table_ob=table_ob),
              onLaterPages=myLaterPages)
    invoice_no = str_n(restaurant.invoice_no + 1, 7)
    pdf_file.seek(0)
    pdf_link = upload_pdf_bill(pdf_file, restaurant.restaurant_id, invoice_no)
    Restaurant.objects.get(id=restaurant.id).update(inc__invoice_no=1)

    return restaurant.taxes, {'Pre-Tax Amount': pretax, 'Taxes': taxes, 'Total Amount': total_amount}, pdf_link, invoice_no


def billed_cleaned(table_id):
    table_ob = Table.objects.get(id=table_id)
    restaurant = Restaurant.objects(tables__in=[table_id]).first()
    if len(table_ob.table_orders) == 0:
        table_ob.users = []
        table_ob.save()
        return False

    taxes, bill_structure, pdf_link, invoice_no = generate_bill(table_ob, restaurant)
    order_history = OrderHistory()
    order_history.table_id = table_id
    order_history.invoice_no = invoice_no
    order_history.table = table_ob.name
    order_history.restaurant_id = str(restaurant.id)
    order_history.restaurant_name = str(restaurant.name)
    order_history.pdf = pdf_link
    order_history.taxes, order_history.bill_structure = taxes, bill_structure
    for table_ord in table_ob.table_orders:
        order_history.table_orders.append(json_util.loads(table_ord.to_json()))
        table_ord.delete()
    order_history.users.extend([{"name": user.name, "user_id": str(user.id)} for user in table_ob.users])
    order_history.assistance_reqs.extend([json_util.loads(ass_req.to_json()) for ass_req in table_ob.assistance_reqs])
    for ass_req in table_ob.assistance_reqs:
        ass_req.delete()
    order_history.timestamp = datetime.now()
    order_history.save()
    for user in table_ob.users:
        user.dine_in_history.append(order_history.to_dbref())
        user.current_table_id = None
        user.save()
    Restaurant.objects(tables__in=[table_ob]).first().update(push__order_history=order_history)
    table_ob.table_orders = []
    table_ob.assistance_reqs = []
    table_ob.requests_queue = []
    table_ob.users = []
    table_ob.save()
    return order_history.to_json()
