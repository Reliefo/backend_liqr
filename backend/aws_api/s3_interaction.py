import boto3

s3_resource = boto3.resource(
    "s3",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)
s3_client = boto3.client(
    "s3",
    aws_access_key_id="AKIAQJQYMJQJYTMFNHEU",
    aws_secret_access_key="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",
    region_name="ap-south-1"
)


def fetch_file_object(bucket_name, object_key):
    s3_resource.Object(bucket_name, object_key)


def fetch_file_object_acl(bucket_name, object_key):
    s3_resource.ObjectAcl(bucket_name, object_key)


def upload_fileobj(fileobj, bucket_name, file_path):
    s3_client.upload_fileobj(fileobj, bucket_name, file_path, ExtraArgs={'ACL': 'public-read'})
    image_link = 'https://s3-ap-south-1.amazonaws.com/' + bucket_name + '/' + file_path
    return image_link


def copy_fileobj(s3_file_link, new_bucket_name, file_path):
    copy_source = "/" + s3_file_link.split('/', 3)[-1]
    s3_client.copy_object(
        Bucket=new_bucket_name,
        CopySource=copy_source,
        Key=file_path,
    )
