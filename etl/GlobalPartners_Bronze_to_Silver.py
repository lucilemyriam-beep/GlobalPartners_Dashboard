import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Bronze_Order_Item_Options
Bronze_Order_Item_Options_node1792625407825 = glueContext.create_dynamic_frame.from_catalog(database="globalpartners_bronze_db", table_name="order_item_options", transformation_ctx="Bronze_Order_Item_Options_node1792625407825")

# Script generated for node Bronze_Order_Items
Bronze_Order_Items_node1792616981276 = glueContext.create_dynamic_frame.from_catalog(database="globalpartners_bronze_db", table_name="order_items", transformation_ctx="Bronze_Order_Items_node1792616981276")

# Script generated for node Bronze_Date_Dim
Bronze_Date_Dim_node1792627053660 = glueContext.create_dynamic_frame.from_catalog(database="globalpartners_bronze_db", table_name="date_dim", transformation_ctx="Bronze_Date_Dim_node1792627053660")

# Script generated for node Change_Schema_Order_Options
Change_Schema_Order_Options_node1792625549661 = ApplyMapping.apply(frame=Bronze_Order_Item_Options_node1792625407825, mappings=[("order_id", "string", "order_id", "string"), ("lineitem_id", "string", "lineitem_id", "string"), ("option_group_name", "string", "option_group_name", "string"), ("option_name", "string", "option_name", "string"), ("option_price", "decimal", "option_price", "decimal"), ("option_quantity", "int", "option_quantity", "int")], transformation_ctx="Change_Schema_Order_Options_node1792625549661")

# Script generated for node Change Schema
ChangeSchema_node1792617427415 = ApplyMapping.apply(frame=Bronze_Order_Items_node1792616981276, mappings=[("app_name", "string", "app_name", "string"), ("restaurant_id", "string", "restaurant_id", "string"), ("creation_time_utc", "string", "creation_time_utc", "string"), ("order_id", "string", "order_id", "string"), ("user_id", "string", "user_id", "string"), ("printed_card_number", "string", "printed_card_number", "string"), ("is_loyalty", "boolean", "is_loyalty", "boolean"), ("currency", "string", "currency", "string"), ("lineitem_id", "string", "lineitem_id", "string"), ("item_category", "string", "item_category", "string"), ("item_name", "string", "item_name", "string"), ("item_price", "decimal", "item_price", "decimal"), ("item_quantity", "int", "item_quantity", "int")], transformation_ctx="ChangeSchema_node1792617427415")

# Script generated for node Change_Schema_Date_Dim
Change_Schema_Date_Dim_node1792627326797 = ApplyMapping.apply(frame=Bronze_Date_Dim_node1792627053660, mappings=[("date_key", "string", "date_key", "string"), ("year", "int", "year", "int"), ("month", "string", "month", "string"), ("week", "string", "week", "string"), ("day_of_week", "string", "day_of_week", "string"), ("is_weekend", "boolean", "is_weekend", "boolean"), ("is_holiday", "boolean", "is_holiday", "boolean"), ("holiday_name", "string", "holiday_name", "string")], transformation_ctx="Change_Schema_Date_Dim_node1792627326797")

# Script generated for node Clean_Validate_Order_Options
SqlQuery19 = '''
SELECT
    order_id,
    lineitem_id,
    TRIM(option_group_name) AS option_group_name,
    TRIM(option_name) AS option_name,
    CAST(option_price AS DECIMAL(18,2)) AS option_price,
    CAST(option_quantity AS INT) AS option_quantity
FROM myDataSource
WHERE order_id IS NOT NULL
  AND lineitem_id IS NOT NULL
  AND TRY_CAST(option_price AS DECIMAL(18,2)) >= 0
  AND TRY_CAST(option_quantity AS INT) > 0
'''
Clean_Validate_Order_Options_node1792626018576 = sparkSqlQuery(glueContext, query = SqlQuery19, mapping = {"myDataSource":Change_Schema_Order_Options_node1792625549661}, transformation_ctx = "Clean_Validate_Order_Options_node1792626018576")

# Script generated for node Clean_Validate_Order_Items
SqlQuery20 = '''
SELECT
    app_name,
    restaurant_id,
    TRY_CAST(creation_time_utc AS TIMESTAMP)
        AS creation_time_utc,
    order_id,
    user_id,
    is_loyalty,
    currency,
    lineitem_id,
    item_category,
    item_name,
    CAST(item_price AS DECIMAL(18,2))
        AS item_price,
    CAST(item_quantity AS INT)
        AS item_quantity
FROM myDataSource
WHERE order_id IS NOT NULL
  AND lineitem_id IS NOT NULL
  AND TRY_CAST(item_price AS DECIMAL(18,2)) >= 0
  AND TRY_CAST(item_quantity AS INT) > 0
  AND TRY_CAST(creation_time_utc AS TIMESTAMP) IS NOT NULL
'''
Clean_Validate_Order_Items_node1792618426205 = sparkSqlQuery(glueContext, query = SqlQuery20, mapping = {"myDataSource":ChangeSchema_node1792617427415}, transformation_ctx = "Clean_Validate_Order_Items_node1792618426205")

# Script generated for node Clean_Validate_Date_Dim
SqlQuery18 = '''
SELECT
    TO_DATE(date_key, 'dd-MM-yyyy') AS date_key,
    year,
    month,
    week,
    day_of_week,
    is_weekend,
    is_holiday,
    holiday_name
FROM myDataSource
WHERE date_key IS NOT NULL
  AND TRIM(date_key) <> ''
  AND TRY_TO_TIMESTAMP(date_key, 'dd-MM-yyyy') IS NOT NULL
'''
Clean_Validate_Date_Dim_node1792627868347 = sparkSqlQuery(glueContext, query = SqlQuery18, mapping = {"myDataSource":Change_Schema_Date_Dim_node1792627326797}, transformation_ctx = "Clean_Validate_Date_Dim_node1792627868347")

# Script generated for node Silver_Order_Item_Options
Silver_Order_Item_Options_node1792626442892 = glueContext.write_dynamic_frame.from_options(frame=Clean_Validate_Order_Options_node1792626018576, connection_type="s3", format="glueparquet", connection_options={"path": "s3://globalpartners-medallion-593271843946/silver/order_item_options/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="Silver_Order_Item_Options_node1792626442892")

# Script generated for node Silver_Order_Items
Silver_Order_Items_node1792619142483 = glueContext.write_dynamic_frame.from_options(frame=Clean_Validate_Order_Items_node1792618426205, connection_type="s3", format="glueparquet", connection_options={"path": "s3://globalpartners-medallion-593271843946/silver/order_items/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="Silver_Order_Items_node1792619142483")

# Script generated for node Silver_Date_Dim
Silver_Date_Dim_node1792628636131 = glueContext.write_dynamic_frame.from_options(frame=Clean_Validate_Date_Dim_node1792627868347, connection_type="s3", format="glueparquet", connection_options={"path": "s3://globalpartners-medallion-593271843946/silver/date_dim/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="Silver_Date_Dim_node1792628636131")

job.commit()