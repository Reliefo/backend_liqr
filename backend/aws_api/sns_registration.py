import boto3


def update_staff_endpoint(device_token, staff):
    sns = boto3.resource(
        "sns",
        aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
        aws_secret_access_key="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",
        region_name="ap-south-1"
    )

    platform_application_arn = "arn:aws:sns:ap-south-1:020452232211:app/GCM/liqr_staff"
    if staff.endpoint_arn:
        platform_endpoint = sns.PlatformEndpoint(staff.endpoint_arn)
        if platform_endpoint.attributes['Enabled'] == 'true':
            return
        else:
            platform_endpoint.delete()
            platform_application = sns.PlatformApplication(platform_application_arn)
            platform_endpoint = platform_application.create_platform_endpoint(Token=device_token,
                                                                              CustomUserData=str(staff.id))
            staff.endpoint_arn = platform_endpoint.arn
            staff.save()
            return
    else:
        platform_application = sns.PlatformApplication(platform_application_arn)
        platform_endpoint = platform_application.create_platform_endpoint(Token=device_token,
                                                                          CustomUserData=str(staff.id))
        staff.endpoint_arn = platform_endpoint.arn
        staff.save()
        return