
from pyathena import connect

print("Connecting to AWS Athena...")

try:
    conn = connect(
        region_name="us-east-1",
        schema_name="globalpartners_gold_db",
        work_group="primary"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SHOW TABLES IN globalpartners_gold_db"
    )

    print("Connection successful!")
    print("Available Gold tables:")

    for row in cursor.fetchall():
        print(row[0])

    cursor.close()
    conn.close()

except Exception as e:
    print("Connection failed:")
    print(e)
