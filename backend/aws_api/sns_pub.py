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
                'notification': {'text': 'We have something to be delivered from some table to someone!',
                                 'title': 'New Order Update'}}

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
                'notification': {'text': 'Someone asked for '+request_dict['assistance_type']+' from '+request_dict['table'],
                                 'title': 'Assistance Request from ' + request_dict['table']}}

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
