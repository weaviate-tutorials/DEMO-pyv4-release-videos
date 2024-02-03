import weaviate
import os
import weaviate.classes.query as wq

client = weaviate.connect_to_embedded(
    headers={
        "X-Cohere-Api-Key": os.getenv("COHERE_API_KEY"),  # Providing the Cohere API key as `text2vec-cohere` is used for vectorization
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY"),  # Providing the OpenAI API key as `openai` is used for RAG (generative) queries
    }
)

assert client.is_ready()

movies = client.collections.get("Movie")
reviews = client.collections.get("Review")

response = movies.generate.near_text(
    query="holiday season",
    limit=4,
    return_references=[wq.QueryReference(link_on="hasReview", return_properties=["username", "content"])],
    return_properties=["title", "tagline", "runtime"],
    filters=(wq.Filter.by_property("runtime").less_than(100) & wq.Filter.by_property("runtime").greater_than(85)),
    single_prompt="Translate this into French: {title}",
    grouped_task="What do these movies have in common?"
)


print("\n\n===== 'Grouped task' generated output: =====")
print(response.generated)
for o in response.objects:
    print("\n===== Movie =====")
    print(f"title: {o.properties['title']}")
    print(f"In French: {o.generated}")
    print(f"Runtime: {o.properties['runtime']}")
    print(f"uuid: {o.uuid}")
    print(f"Sample review by: {o.references['hasReview'].objects[0].properties['username']}")
    print(f"Review body: {o.references['hasReview'].objects[0].properties['content']}")


client.close()
