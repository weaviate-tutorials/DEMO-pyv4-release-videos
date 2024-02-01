import weaviate
import os
from weaviate.auth import AuthApiKey

client = weaviate.connect_to_wcs(
    cluster_url=os.getenv("JP_WCS_URL"),
    auth_credentials=AuthApiKey(os.getenv("JP_WCS_ADMIN_KEY")),
    headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    }
)

movies = client.collections.get("Movie")
reviews = client.collections.get("Review")

response = movies.query.near_text(
    query="romantic comedy set in europe",
    limit=2
)

for o in response.objects:
    print(o.properties["title"])
    print(o.properties["overview"][:100])

client.close()
