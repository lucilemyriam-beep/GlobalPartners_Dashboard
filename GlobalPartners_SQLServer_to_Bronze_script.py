import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node SQL Server - Date Dim
SQLServerDateDim_node1792549008380 = glueContext.create_dynamic_frame.from_options(
    connection_type = "sqlserver",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "dbo.date_dim",
        "connectionName": "globalpartners-sqlserver-connection-v4",
    },
    transformation_ctx = "SQLServerDateDim_node1792549008380"
)

# Script generated for node SQL Server - Order Options
SQLServerOrderOptions_node1792548385472 = glueContext.create_dynamic_frame.from_options(
    connection_type = "sqlserver",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "dbo.order_item_options",
        "connectionName": "globalpartners-sqlserver-connection-v4",
    },
    transformation_ctx = "SQLServerOrderOptions_node1792548385472"
)

# Script generated for node Microsoft SQL Server
MicrosoftSQLServer_node1792537520497 = glueContext.create_dynamic_frame.from_options(
    connection_type = "sqlserver",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "dbo.order_items",
        "connectionName": "globalpartners-sqlserver-connection-v4",
    },
    transformation_ctx = "MicrosoftSQLServer_node1792537520497"
)

# Script generated for node S3 Bronze - Date Dim
EvaluateDataQuality().process_rows(frame=SQLServerDateDim_node1792549008380, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1792548084468", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
S3BronzeDateDim_node1792549145618 = glueContext.write_dynamic_frame.from_options(frame=SQLServerDateDim_node1792549008380, connection_type="s3", format="glueparquet", connection_options={"path": "s3://globalpartners-medallion-593271843946/bronze/date_dim/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="S3BronzeDateDim_node1792549145618")

# Script generated for node S3 Bronze - Order Options
EvaluateDataQuality().process_rows(frame=SQLServerOrderOptions_node1792548385472, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1792548084468", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
S3BronzeOrderOptions_node1792548702307 = glueContext.write_dynamic_frame.from_options(frame=SQLServerOrderOptions_node1792548385472, connection_type="s3", format="glueparquet", connection_options={"path": "s3://globalpartners-medallion-593271843946/bronze/order_item_options/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="S3BronzeOrderOptions_node1792548702307")

# Script generated for node Amazon S3
EvaluateDataQuality().process_rows(frame=MicrosoftSQLServer_node1792537520497, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1792536879625", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
AmazonS3_node1792540117252 = glueContext.write_dynamic_frame.from_options(frame=MicrosoftSQLServer_node1792537520497, connection_type="s3", format="glueparquet", connection_options={"path": "s3://globalpartners-medallion-593271843946/bronze/order_items/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="AmazonS3_node1792540117252")

job.commit()