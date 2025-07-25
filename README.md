# DynamoDB to S3 via EventBridge/Lambda
CloudFormationTemplate for creating a lambda function/permissions that exports DynamoDB data to S3. Code and identifiers have been anonymized from original to display my work in CloudFormation. You will not be able to directly run this.

Once a Day at 8:00PM EST
## What this Creates
  1. Lambda Role with following Permissions
       - DynamoDB Table amplify-CHAT-USAGE-TABLE-NAME
           - dynamodb:ExportTableToPointInTime
       - Basic Lambda Execution Role
       - S3 Bucket
           - S3:PutObjectAcl
           - S3:PutObject
           - s3:AbortMultipartUpload
        
  2. Lambda Function: Prod-Chat-Usage-DB-Export-S3
     - Python Runtime 3.12
     - Timeout : 6 minutes
     - Code Stored as a zip file in : BUCKET-WHERE-ZIP-FILE-IS-UPLOADED/weeklyreporting.zip
     - **Environment Variables**:
        - `BUCKET_NAME`
        - `TABLE_ARN`
        - `SNS_TOPIC`
    
  3. EventBridge Rule
     - Will Execute Lambda Function Every Day at 8PM EST `0 1 * * ? *` (1:00 AM UTC, equivalent to 8:00 PM EST)

  4. S3 Bucket: amplify-weeklyreportingparquets
     - S3 Default Encryption
     - Access Control : Private
     - Stack Deletion: all items will be retained

  5. SNS Topic: DynamoDBExportToS3NotificationSNS
     - Will notify email/distro list (customizable) with notifications of failures/successes
     