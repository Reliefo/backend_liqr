import boto3
from backend.mongo.mongodb import Staff
from backend.aws_api.sns_pub import sns_client

sns = boto3.resource(
    "sns",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def update_staff_endpoint(device_token, staff):
    platform_application_arn = "arn:aws:sns:ap-south-1:020452232211:app/GCM/liqr_staff"
    if staff.endpoint_arn:
        platform_endpoint = sns.PlatformEndpoint(staff.endpoint_arn)
        if platform_endpoint.attributes['Enabled'] == 'true':
            return
        else:
            platform_endpoint.delete()
            platform_application = sns.PlatformApplication(platform_application_arn)
            platform_endpoint = platform_application.create_platform_endpoint(Token=device_token,
                                                                              CustomUserData=staff.name + "$" + str(
                                                                                  staff.id))
            staff.endpoint_arn = platform_endpoint.arn
            staff.device_token = device_token
            staff.save()
            return
    else:
        platform_application = sns.PlatformApplication(platform_application_arn)
        try:
            platform_endpoint = platform_application.create_platform_endpoint(Token=device_token,
                                                                              CustomUserData=staff.name + "$" + str(
                                                                                  staff.id))
            arn_to_be_assigned = platform_endpoint.arn
        except sns_client.exceptions.InvalidParameterException as e:
            text = e.response['Error']['Message']
            arn_to_be_assigned = text.split()[5]
        staff.endpoint_arn = arn_to_be_assigned
        staff.device_token = device_token
        staff.save()
        return


def verify_endpoint(staff_id):
    staff = Staff.objects.get(id=staff_id)
    if not staff.endpoint_arn:
        return False
    platform_endpoint = sns.PlatformEndpoint(staff.endpoint_arn)
    enabled = platform_endpoint.attributes['Enabled']
    if enabled == 'false':
        staff.endpoint_arn = None
        platform_endpoint.delete()
        staff.save()
        return False
    else:
        return True
