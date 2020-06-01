import boto3
from bson import json_util
from backend.aws_api.sns_registration import verify_endpoint

sns_client = boto3.client(
    "sns",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def push_order_complete_notification(request_dict, staff_endpoint_arn):
    pub_data_dict = {**request_dict, **{'click_action': "FLUTTER_NOTIFICATION_CLICK"}}

    gcm_dict = {'data': pub_data_dict,
                'notification': {'text': 'We have ' + request_dict['food_name'] + ' to be delivered to ' + request_dict['table'] + ' to ' + request_dict['user'],
                                 'title': 'Order Pickup: ' + request_dict['food_name'] + ' to ' + request_dict['table']}}

    final_message_dict = {"default": "Sample fallback message", "GCM": json_util.dumps(gcm_dict)}

    try:
        sns_client.publish(
            TargetArn=staff_endpoint_arn,
            Message=json_util.dumps(final_message_dict),
            Subject='Thsi is subejct',
            MessageStructure="json"
        )
    except sns_client.exceptions.EndpointDisabledException:
        verify_endpoint(request_dict['staff_id'])
    return


def push_assistance_request_notification(request_dict, staff_endpoint_arn):
    pub_data_dict = {**request_dict, **{'click_action': "FLUTTER_NOTIFICATION_CLICK"}}

    gcm_dict = {'data': pub_data_dict,
                'notification': {
                    'text': request_dict['user'] + ' from ' + request_dict['table']+' asked for ' + request_dict['assistance_type'],
                    'title': 'Assistance: ' + request_dict['assistance_type']+' for '+ request_dict['table']}}

    final_message_dict = {"default": "Sample fallback message", "GCM": json_util.dumps(gcm_dict)}

    try:
        sns_client.publish(
            TargetArn=staff_endpoint_arn,
            Message=json_util.dumps(final_message_dict),
            Subject='Thsi is subejct',
            MessageStructure="json"
        )
    except sns_client.exceptions.EndpointDisabledException:
        verify_endpoint(request_dict['staff_id'])
    return
