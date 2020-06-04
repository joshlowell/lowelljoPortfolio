import json
import boto3
import io
import zipfile
from botocore.client import Config
import mimetypes

def lambda_handler(event, context):


    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    
    portfolio_bucket = s3.Bucket('portfolio.joshlowell.info')
    build_bucket = s3.Bucket('portfoliobuilder.joshlowell.info')
    
    portfolio_zip = io.BytesIO()
    build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
    
    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            mimetype = mimetypes.guess_type(nm)[0]
            portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': str(mimetype)})
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
