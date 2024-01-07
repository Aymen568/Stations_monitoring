from elasticsearch import  Elasticsearch

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
