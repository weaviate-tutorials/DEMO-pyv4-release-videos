# Movie: ["title", "tagline", "overview", "vote_average", "release_date", "runtime", "imdb_id"]
# Reviews: ["username", "content", "tmdb_id"]

import weaviate
import weaviate.classes.config as wc

client = weaviate.connect_to_embedded()

reviews = client.collections.create(
    name="Review",
    properties=[
        wc.Property(name="username", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="content", data_type=wc.DataType.TEXT),
        wc.Property(name="tmdb_id", data_type=wc.DataType.TEXT, skip_vectorization=True),
    ],
    vectorizer_config=wc.Configure.Vectorizer.text2vec_cohere(),
    generative_config=wc.Configure.Generative.openai(),
    inverted_index_config=wc.Configure.inverted_index(
        index_property_length=True
    )
)

movies = client.collections.create(
    name="Movie",
    properties=[
        wc.Property(name="title", data_type=wc.DataType.TEXT),
        wc.Property(name="tagline", data_type=wc.DataType.TEXT),
        wc.Property(name="overview", data_type=wc.DataType.TEXT),
        wc.Property(name="vote_average", data_type=wc.DataType.NUMBER),
        wc.Property(name="release_date", data_type=wc.DataType.DATE),
        wc.Property(name="runtime", data_type=wc.DataType.INT),
        wc.Property(name="imdb_id", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="tmdb_id", data_type=wc.DataType.INT),
    ],
    vectorizer_config=wc.Configure.Vectorizer.text2vec_cohere(),
    generative_config=wc.Configure.Generative.openai(),
    vector_index_config=wc.Configure.VectorIndex.hnsw(
        distance_metric=wc.VectorDistances.COSINE
    ),
    references=[
        wc.ReferenceProperty(name="hasReview", target_collection="Review")
    ]
)

client.close()
