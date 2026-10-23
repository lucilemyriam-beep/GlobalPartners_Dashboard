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

# Script generated for node Silver_Order_Items
Silver_Order_Items_node1792636009671 = glueContext.create_dynamic_frame.from_catalog(database="globalpartners_silver_db", table_name="order_items", transformation_ctx="Silver_Order_Items_node1792636009671")

# Script generated for node Gold_Restaurant_Order_Summary
SqlQuery41 = '''
SELECT
    restaurant_id,
    COUNT(DISTINCT order_id) AS total_orders
FROM order_items
GROUP BY restaurant_id
'''
Gold_Restaurant_Order_Summary_node1792637033692 = sparkSqlQuery(glueContext, query = SqlQuery41, mapping = {"order_items":Silver_Order_Items_node1792636009671}, transformation_ctx = "Gold_Restaurant_Order_Summary_node1792637033692")

# Script generated for node Gold_Restaurant_Order_Summary_Target
Gold_Restaurant_Order_Summary_Target_node1792638187176 = glueContext.getSink(path="s3://globalpartners-medallion-593271843946/gold/restaurant_order_summary/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=[], enableUpdateCatalog=True, transformation_ctx="Gold_Restaurant_Order_Summary_Target_node1792638187176")
Gold_Restaurant_Order_Summary_Target_node1792638187176.setCatalogInfo(catalogDatabase="globalpartners_gold_db",catalogTableName="restaurant_order_summary")
Gold_Restaurant_Order_Summary_Target_node1792638187176.setFormat("glueparquet", compression="snappy")
Gold_Restaurant_Order_Summary_Target_node1792638187176.writeFrame(Gold_Restaurant_Order_Summary_node1792637033692)
job.commit()