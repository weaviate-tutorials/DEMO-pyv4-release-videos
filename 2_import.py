import weaviate
import os
import pandas as pd
from datetime import datetime, timezone
from weaviate.util import generate_uuid5

client = weaviate.connect_to_embedded(
    headers={
        "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY")  # Providing the Cohere API key as `text2vec-cohere` is used for vectorization
    }
)


movies = client.collections.get("Movie")
reviews = client.collections.get("Review")

df = pd.read_json("data/movie_reviews_1990_2024_20_movies_info.json")
rdf = pd.read_json("data/movie_reviews_1990_2024_20_movie_reviews.json")

ref_id_map = dict()
with reviews.batch.fixed_size(batch_size=50, concurrent_requests=2) as batch:
    for i, row in rdf.iterrows():
        movie_id = row["id"]
        ref_ids = list()
        for review in row["results"]:
            props = {
                "username": review["author_details"]["username"],
                "content": review["content"],
                "tmdb_id": review["id"],
            }
            review_uuid = generate_uuid5(row["id"])
            batch.add_object(
                properties=props,
                uuid=review_uuid
            )
            ref_ids.append(review_uuid)
        ref_id_map[movie_id] = ref_ids


if len(reviews.batch.failed_objects) > 0 or len(reviews.batch.failed_references) > 0:
    print(reviews.batch.failed_objects[:5])
    print(reviews.batch.failed_references[:5])


# ["title", "tagline", "overview", "vote_average", "release_date", "runtime", "imdb_id", "tmdb_id"]
with movies.batch.fixed_size(batch_size=50, concurrent_requests=2) as batch:
    for i, row in df.iterrows():
        cols = ["title", "tagline", "overview", "vote_average", "runtime", "imdb_id"]
        movie_id = row["id"]
        movie_uuid = generate_uuid5(row["id"])
        props = {c: row[c] for c in cols}
        props["release_date"] = datetime.strptime(row["release_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if movie_id in ref_id_map.keys():
            refs = {"hasReview": ref_id_map[movie_id]}
        else:
            refs = None
        batch.add_object(
            properties=props,
            references=refs,
            uuid=movie_uuid
        )
        if i % 100 == 0:
            print(i)


if len(reviews.batch.failed_objects) > 0 or len(reviews.batch.failed_references) > 0:
    print(reviews.batch.failed_objects[:5])
    print(reviews.batch.failed_references[:5])


client.close()
