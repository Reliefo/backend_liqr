import boto3
from bson import json_util

client = boto3.client(
    "sns",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def push_order_complete_notification(update_dict):
    pub_data_dict = {'table_order_id': update_dict['table_order_id'], 'type': update_dict['type'],
                     'order_id': update_dict['order_id'], 'food_id': update_dict['food_id'],
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
