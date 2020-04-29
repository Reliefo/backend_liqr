import boto3
from bson import json_util

client = boto3.client(
    "sns",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def push_order_complete_notification(request_dict):
    pub_data_dict = {'table_order_id': request_dict['table_order_id'], 'type': request_dict['type'],
                     'order_id': request_dict['order_id'], 'food_id': request_dict['food_id'],
                     'click_action': "FLUTTER_NOTIFICATION_CLICK"}

    gcm_dict = {'data': pub_data_dict,
                'notification': {'text': 'We have something to be delivered from some table to someone!',
                                 'title': 'New Order Update'}}

    final_message_dict = {"default": "Sample fallback message", "GCM": json_util.dumps(gcm_dict)}

    response = client.publish(
        TopicArn='arn:aws:sns:ap-south-1:020452232211:Reliefo-Topic',
        Message=json_util.dumps(final_message_dict),
        Subject='Thsi is subejct',
        MessageStructure="json"
    )
    return response


def push_assistance_request_notification(request_dict):
    pub_data_dict = {'assistance_req_id': str(request_dict['_id']), 'assistance_type': request_dict['assistance_type'],
                     'user_id': str(request_dict['user']), 'timestamp': request_dict['timestamp'],
                     'table_id': request_dict['table_id'],
                     'click_action': "FLUTTER_NOTIFICATION_CLICK"}

    gcm_dict = {'data': pub_data_dict,
                'notification': {'text': 'Someone asked for '+request_dict['assistance_type']+' from '+request_dict['table'],
                                 'title': 'Assistance Request from ' + request_dict['table']}}

    final_message_dict = {"default": "Sample fallback message", "GCM": json_util.dumps(gcm_dict)}

    response = client.publish(
        TopicArn='arn:aws:sns:ap-south-1:020452232211:Reliefo-Topic',
        Message=json_util.dumps(final_message_dict),
        Subject='Thsi is subejct',
        MessageStructure="json"
    )
    return response
