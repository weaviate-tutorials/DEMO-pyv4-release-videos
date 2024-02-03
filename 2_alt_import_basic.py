# Written for the basic demo only
# Try running 2_import.py instead to actually import your data

import weaviate
from weaviate.classes.data import DataObject
import os

client = weaviate.connect_to_embedded(
    headers={"X-Cohere-Api-Key": os.getenv("COHERE_API_KEY")}
)

reviews = client.collections.get("Review")
movies = client.collections.get("Movie")

tgt_uuid = reviews.data.insert(properties={"username": "jphwang1"})
movies.data.insert(
    properties={"title": "Modern times"},
    references={"hasReview": tgt_uuid}
)

review_props = [{"username": f"user_{i}"} for i in range(5)]
reviews.data.insert_many(review_props)

movie_objs = [
    DataObject(
        properties={"title": f"Movie {i}"},
        references={"hasReview": tgt_uuid},
    ) for i in range(5)
]
movies.data.insert_many(movie_objs)

with client.batch.fixed_size(batch_size=100) as batch:
    batch.add_object(
        properties={"title": "Avatar"},
        collection="Movie",
    )

with movies.batch.dynamic() as batch:
    for i in range(100):
        batch.add_object(
            properties={"title": "When Harry met Sally"}
        )
        if batch.number_errors > 100:
            break

if len(movies.batch.failed_objects) > 0 or len(movies.batch.failed_references) > 0:
    # do soemthing
    pass


client.close()
