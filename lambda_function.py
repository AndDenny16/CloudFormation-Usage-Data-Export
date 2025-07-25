import json
import boto3
import datetime
import os
import logging
from datetime import datetime, timedelta, timezone

TABLE_ARN = os.environ["TABLE_ARN"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
PREFIX = os.environ["PREFIX"]
SNS_TOPIC = os.environ["SNS_TOPIC"]
dynamodb = boto3.client("dynamodb")
sns = boto3.client("sns")


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Export Started")
    export_from = datetime.now(timezone.utc) - timedelta(hours=24)
    logger.info("Exporting From %s", export_from.isoformat())
    try:
        resp = dynamodb.export_table_to_point_in_time(
            TableArn = TABLE_ARN,
            S3Bucket = BUCKET_NAME,
            S3Prefix = PREFIX,
            ExportFormat = "DYNAMODB_JSON",
            IncrementalExportSpecification = {
            "ExportFromTime": export_from.replace(tzinfo=datetime.timezone.utc)
            },
            ExportType = "INCREMENTAL_EXPORT")

        export_arn = resp["ExportDescription"]["ExportArn"]
        logger.info("Export finished successfully with ARN: %s", export_arn)
        sns.publish(
            TopicArn=SNS_TOPIC,
            Subject="DynamoDB Export Successful",
            Message=json.dumps({
                "ExportArn": export_arn,
                "StartedFrom": export_from.isoformat()
            }, indent=2)
        )
        return {
        "ExportArn": resp["ExportDescription"]["ExportArn"],
        "StartedFrom": export_from.isoformat(timespec="seconds")
        }

    except Exception as e: 
        logger.error("Export Failed Due To: %s", e)
        sns.publish(
            TopicArn=SNS_TOPIC,
            Subject="DynamoDB Export Failed",
            Message=json.dumps({
                "ExportArn": export_arn,
                "StartedFrom": export_from.isoformat()
            }, indent=2)
        )
        return {
            "statusCode": 500,
            "body": json.dumps({"Error": "Failed To Export The Table to S3"})
        }

  