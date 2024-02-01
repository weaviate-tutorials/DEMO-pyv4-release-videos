import weaviate
import os
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Property, DataType, Configure, VectorDistances, ReferenceProperty

client = weaviate.connect_to_wcs(
    cluster_url=os.getenv("JP_WCS_URL"),
    auth_credentials=AuthApiKey(os.getenv("JP_WCS_ADMIN_KEY")),
    headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    }
)

try:
    client.collections.delete(["Movie", "Review"])

    # Add ["title", "tagline", "overview", "vote_average", "release_date", "runtime", "imdb_id"]
    movies = client.collections.create(
        name="Movie",
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="tagline", data_type=DataType.TEXT),
            Property(name="overview", data_type=DataType.TEXT),
            Property(name="vote_average", data_type=DataType.NUMBER),
            Property(name="release_date", data_type=DataType.DATE),
            Property(name="runtime", data_type=DataType.INT),
            Property(name="imdb_id", data_type=DataType.TEXT, skip_vectorization=True),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_openai(),
        generative_config=Configure.Generative.openai(),
        vector_index_config=Configure.VectorIndex.hnsw(distance_metric=VectorDistances.COSINE),
        inverted_index_config=Configure.inverted_index(index_timestamps=True)
    )

    # Import ["username", "content", "id"]
    reviews = client.collections.create(
        name="Review",
        vectorizer_config=Configure.Vectorizer.text2vec_openai(),
        generative_config=Configure.Generative.openai(),
        properties=[
            Property(name="username", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="content", data_type=DataType.TEXT),
            Property(name="tmdb_id", data_type=DataType.TEXT)
        ],
        inverted_index_config=Configure.inverted_index(
            index_property_length=True
        )
    )

    movies.config.add_reference(
        ReferenceProperty(name="hasReview", target_collection="Review")
    )

finally:
    client.close()
