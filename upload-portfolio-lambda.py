import json
import boto3
import io
import zipfile
from botocore.client import Config
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:537150882958:deployPortfolioTopic')
    try:
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

        topic.publish(Subject="Portfolio Deployed", Message="Portfolio deployed successfulyl")
    except:
        topic.publish(Subject="Portfolio Deploy failed", Message="Portfolio NOT deployed successfulyl")
        raise
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
