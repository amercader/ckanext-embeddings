from datetime import datetime, timezone
import sys
import uuid

import click

from ckan import model
from ckan.plugins import toolkit

from ckanext.embeddings.backends import get_embeddings_backend


def get_commands():
    return [embeddings]


@click.group()
def embeddings():
    """"""
    pass


@embeddings.command()
@click.argument("dataset_id", type=str)
@click.option("-l", "--limit", type=int, default=5)
def similar(dataset_id: str, limit: int):
    """Shows the closest neighbours to the provided dataset"""

    try:
        result = toolkit.get_action("package_similar_show")(
            {"ignore_auth": True}, {"id": dataset_id, "limit": limit}
        )
    except toolkit.ObjectNotFound:
        toolkit.error_shout(f"Dataset not found: {dataset_id}")
        sys.exit(1)

    msg = f"Similar datasets to {dataset_id}"
    print(msg)
    print("-" * len(msg))
    for r in result:

        print(f"{r['id']} - {r['title']}")


@embeddings.command()
@click.argument("query", type=str)
@click.option("-l", "--limit", type=int, default=10)
def search(query: str, limit: int):
    """Shows the closest dataset to the provided search term"""

    backend = get_embeddings_backend()
    query_embedding = backend.get_embedding_for_string(query)
    search_params = {}
    search_params["defType"] = "lucene"

    field_name = toolkit.config.get("ckanext.embeddings.solr_vector_field_name", "vector")

    search_params["q"] = f"{{!knn f={field_name} topK={limit}}}{list(query_embedding)}"

    result = toolkit.get_action("package_search")({"ignore_auth": True}, search_params)

    msg = f"Closest datasets to '{query}'"
    print(msg)
    print("-" * len(msg))

    for r in result["results"]:

        print(f"{r['id']} - {r['title']}")
