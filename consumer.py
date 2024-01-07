import os 
from pyspark import SparkConf 
from pyspark import SparkContext 
from pyspark.sql import SparkSession
from pyspark.sql.avro.functions import from_avro 
from pyspark.sql.types import StructType, StructField,LongType, DoubleType, StringType 
from pyspark.sql.functions import expr, from_json, col, concat, col, struct, to_timestamp 
import json 
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, LongType, DoubleType
from elasticsearch import Elasticsearch 
from elasticsearch.helpers import bulk 
from os.path import abspath 

es = Elasticsearch(
    [ {'host': 'localhost', 'port': 9200, "scheme": "http"}],
    
)

# Define the index settings and mappings
index_name = 'velo'  # Replace with your desired index name
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)



create_index = {
    "settings": {
        "analysis": {
            "analyzer": {
                "payload_analyzer": {
                    "type": "custom",
                    "tokenizer":"whitespace",
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "number": {"type": "integer"},
            "contractName": {"type": "keyword"},
            "name": {"type": "text"},
            "address": {"type": "text"},
            "last_update": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss||epoch_millis"},
            "position": {
                "type": "geo_point",
                "fields": {
                    "latitude": {"type": "text"},
                    "longitude": {"type": "text"}
                }
            },
            "bikes": {"type": "integer"},
            "stands": {"type": "integer"},
            "capacity": {"type": "integer"}
            # Add more fields as needed
        }
    }
}

# create index with the settings & mappings above
es.indices.create(index="velo", body=create_index)

def index_to_elasticsearch(batch_df, batch_id):

    # Get the schema of the DataFrame
    schema = batch_df.schema
    flattened_df = batch_df.select(
        "number",
        "contractName",
        "name",
        "address",
        "last_update",
        "position.latitude",
        "position.longitude",
        "bikes",
        "stands",
        "capacity"
    )
    # Extract actions from the DataFrame using the schema
    actions = [
        {
            "_index": "velo",
            "_source": {
                field.name: row[field.name] if row[field.name] is not None else None
                for field in schema.fields
            }
        }
        for row in batch_df.collect()
    ]

    print(f"Number of actions: {len(actions)}", "*=*==*=*=*=*=*=*=*=*=*=*=*=*==**=*==*=*=*=*=*=*=*=*=")

    # Index the documents into Elasticsearch
    success, failed = bulk(es, actions, raise_on_error=False)

    if failed:
        print(f"Failed to index {len(failed)} documents.")
        for failure in failed:
            print(f"Failed document: {failure}")
    else:
        print(f"Indexed {success} documents successfully.")
    flattened_df = flattened_df.withColumn("last_update", to_timestamp(col("last_update"), "yyyy-MM-dd HH:mm:ss"))

    flattened_df.write \
        .mode("append") \
        .insertInto("cycling_stations", overwrite=True)

spark = SparkSession.builder \
    .appName("KafkaConsumerExample") \
    .config("spark.es.nodes", "localhost") \
    .config("spark.es.port", "9200") \
    .config("spark.es.nodes.wan.only", "true") \
    .getOrCreate()
print(0)

# Create the streaming_df to read from kafka
streaming_df = spark.readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "velib-stations") \
    .option("startingOffsets", "earliest") \
    .load()
print(2)

# Define the schema for your Kafka messages
schema = StructType([
    StructField("number", IntegerType(), True),
    StructField("contractName", StringType(), True),
    StructField("name", StringType(), True),
    StructField("address", StringType(), True),
    StructField("last_update", StringType(), True),
    StructField("position", StructType([
        StructField("latitude", FloatType(), True),
        StructField("longitude", FloatType(), True)
    ]), True),
    StructField("totalStands", StructType([
        StructField("availabilities", StructType([
            StructField("bikes", IntegerType(), True),
            StructField("stands", IntegerType(), True)
        ]), True),
        StructField("capacity", IntegerType(), True)
    ]), True),
])
print(3)
# Parse the JSON data from the Kafka message
velib_df = streaming_df \
    .selectExpr("CAST(value AS STRING) as value") \
    .select(from_json("value", schema).alias("data")) \
    .select(
        col("data.number"),
        col("data.contractName"),
        col("data.name"),
        col("data.address"),
        col("data.last_update"),
        struct(
            col("data.position.latitude").cast(FloatType()).alias("latitude"),
            col("data.position.longitude").cast(FloatType()).alias("longitude")
        ).alias("position"),
        col("data.totalStands.availabilities.bikes").cast(IntegerType()).alias("bikes"),
        col("data.totalStands.availabilities.stands").cast(IntegerType()).alias("stands"),
        col("data.totalStands.capacity").cast(IntegerType()).alias("capacity")
    )

print(4)

# Print the data to the console
query = streaming_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()
print(5)
es_query = velib_df \
    .writeStream \
    .foreachBatch(index_to_elasticsearch) \
    .start()
# creating an index mapping in elasticsearch 
print(6)
es_query.awaitTermination()
# Wait for the streaming queries to terminate
console_query.awaitTermination()

spark.stop()
