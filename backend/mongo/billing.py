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
from backend.aws_api.s3_interaction import upload_fileobj, fetch_file_object, fetch_file_object_acl, copy_fileobj

pdfmetrics.registerFont(TTFont('New Times Bo', 'Times New Roman Gras 700.ttf'))
styles = getSampleStyleSheet()


def my_first_page(canvas, doc, restaurant, table_ob):
    address1 = address2 = phone2 = phone1 = ''
    if restaurant.address:
        address_split = restaurant.address.split()
        first_half = math.ceil(0.4 * len(address_split))
        address1 = ' '.join(address_split[:first_half])
        address2 = ' '.join(address_split[first_half:])
    if len(restaurant.phone_nos) > 0:
        phone1 = restaurant.phone_nos[0]
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
    canvas.line(33, 640, 560, 640)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, restaurant.name))
    canvas.restoreState()


def my_later_pages(canvas, doc, restaurant):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, restaurant.name))
    canvas.restoreState()


def get_customization(food):
    cust = ''
    for customization in food['customization']:
        if len(customization['list_of_options']):
            cust = cust + customization['name'] + ": ["
            for option in customization['list_of_options']:
                if customization['customization_type'] == "choices":
                    cust += option + ", "
                elif customization['customization_type'] == "options":
                    cust += option['option_name'] + ": " + str(option['option_price']) + ", "
                elif customization['customization_type'] == "add_ons":
                    cust += option['name'] + ": " + str(option['price']) + ", "
            cust = cust[0:-2]
            cust += "]; "
    return cust


def generate_bill(table_ob, restaurant):
    current_list = []

    for table_ord in table_ob.table_orders:
        table_dict = json_util.loads(table_ord.to_json())
        for order in table_dict['orders']:
            for new_food in order['food_list']:
                food_id = new_food['food_id'].split('#')[0]
                FoodItem.objects.get(id=food_id).update(inc__ordered_times=new_food['quantity'])
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
            [Paragraph(food['name'], styles['BodyText']),
             Paragraph(get_customization(food), styles['BodyText']) if 'customization' in food.keys() else None,
             float(food['price']),
             food['quantity'], round(float(food['price']) * food['quantity'])])
        pretax += float(food['price']) * food['quantity']
    cgst = restaurant.taxes['CGST']
    sgst = restaurant.taxes['SGST']
    service_tax = restaurant.taxes['Service']
    currency = restaurant.currency
    total_tax = cgst + sgst + service_tax
    taxes = total_tax * pretax / 100
    total_amount = round(pretax + taxes, 2)
    taxes = round(taxes, 2)

    pdf_file = BytesIO()
    doc = SimpleDocTemplate(pdf_file)

    story = [Spacer(1, 1.7 * inch)]
    ps = ParagraphStyle(name='Welcome', parent=styles["Heading2"], alignment=1)
    welcome_message = ("Welcome to " + restaurant.name)
    p = Paragraph(welcome_message, ps)
    story.append(p)
    story.append(Spacer(1, 0.2 * inch))

    title_style = ParagraphStyle(name='Table Title', parent=styles['Normal'], alignment=1)
    pretax_total_style = ParagraphStyle(name='pretax', parent=styles['Normal'])
    total_style = ParagraphStyle(name='Tatotalitle', parent=styles['Normal'], alignment=2, fontName='New Times Bo',
                                 fontSize=11)
    raw_titles = ['Item Name', 'Customization', 'Price', 'Qty', 'Subtotal']
    titles = [Paragraph('<b>{}</b>'.format(title), title_style) for title in raw_titles]
    pre_total_row = [Paragraph('<b>Pretax Total</b>', pretax_total_style), '', '', '',
                     Paragraph('<b>{} {}</b>'.format(currency, pretax), total_style)]
    taxes_row = [Paragraph('<b>Taxes {}%</b>'.format(total_tax), pretax_total_style),
                 Paragraph('<b>CGST: {}%, SGST: {}%, Service Tax: {}%</b>'.format(cgst, sgst, service_tax),
                           pretax_total_style), '', '',
                 Paragraph('<b>{} {}</b>'.format(currency, taxes), total_style)]
    total_row = [Paragraph('<b>Total</b>', pretax_total_style), '', '', '',
                 Paragraph('<b>{} {}</b>'.format(currency, total_amount), total_style)]

    data = [titles] + item_rows + [pre_total_row] + [taxes_row] + [total_row]

    column_sizes = [3 * inch, 2.5 * inch, 0.6 * inch, 0.4 * inch, 0.8 * inch]
    t = TablePDF(data, column_sizes)
    t.setStyle(TableStyle([('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                           ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                           #                        ('VALIGN',(0,0),(-1,0),'MIDDLE'),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                           ('SPAN', (-4, -1), (-2, -1)),
                           ('SPAN', (-4, -2), (-2, -2)),
                           ('SPAN', (-4, -3), (-2, -3))
                           ]))

    story.append(t)
    story.append(Spacer(1, 0.2 * inch))

    rupee_style = ParagraphStyle(name='Tatotaitle', parent=styles['Normal'], alignment=2, fontName='New Times Bo',
                                 fontSize=14)

    last_p = Paragraph('Total Bill to be Paid: {} '.format(currency) + str(total_amount), rupee_style)

    story.append(last_p)
    story.append(Spacer(1, 0.2 * inch))
    bogustext = "Thank you, visit again"
    p = Paragraph(bogustext, ps)
    story.append(p)

    doc.build(story, onFirstPage=partial(my_first_page, restaurant=restaurant, table_ob=table_ob),
              onLaterPages=partial(my_later_pages, restaurant=restaurant))
    invoice_no = restaurant.restaurant_id + "_" + str_n(restaurant.invoice_no + 1, 7)
    pdf_file.seek(0)
    pdf_file_path = restaurant.restaurant_id + '/bills/' + invoice_no + '.pdf'
    pdf_link = upload_fileobj(pdf_file, 'liqr-restaurants', pdf_file_path)
    Restaurant.objects.get(id=restaurant.id).update(inc__invoice_no=1)

    return restaurant.taxes, {'Pre-Tax Amount': pretax, 'Taxes': taxes,
                              'Total Amount': total_amount}, pdf_link, invoice_no


def clear_table(table_id):
    table_ob = Table.objects.get(id=table_id)
    table_ob.users = []
    for user in table_ob.users:
        user.current_table_id = None
        user.save()
    table_ob.save()
    return "done"


def billed_cleaned(table_id):
    table_ob = Table.objects.get(id=table_id)
    restaurant = Restaurant.objects(tables__in=[table_id]).first()
    if len(table_ob.table_orders) == 0:
        table_ob.save()
        return {'status': 'failed', 'message': 'There are no orders to bill', 'order_history': {}}

    taxes, bill_structure, pdf_link, invoice_no = generate_bill(table_ob, restaurant)
    order_history = OrderHistory()
    order_history.table_id = table_id
    order_history.invoice_no = invoice_no
    order_history.table = table_ob.name
    order_history.restaurant_id = str(restaurant.restaurant_id)
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
        user_bill_path = user.aws_id + "/bills/" + invoice_no
        copy_fileobj(pdf_link, "liqr-users", user_bill_path)
        # user.current_table_id = None
        user.save()
    Restaurant.objects(tables__in=[table_ob]).first().update(push__order_history=order_history)
    table_ob.table_orders = []
    table_ob.assistance_reqs = []
    table_ob.requests_queue = []
    table_ob.save()
    clear_table(table_id)
    return {"status": "billed", "order_history": order_history.to_json()}
