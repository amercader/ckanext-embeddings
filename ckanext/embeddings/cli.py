from datetime import datetime, timezone
import sys
import uuid


import click


from ckan import model
from ckan.plugins import toolkit

from ckanext.embeddings.lib import get_embeddings_backend


def get_commands():
    return [embeddings]


@click.group()
def embeddings():
    """"""
    pass


@embeddings.command()
@click.argument("dataset_id", type=str)
@click.option("-l", "--limit", type=int, default=5)
def related(dataset_id: str, limit: int):
    """Shows the closest neighbours to the provided dataset"""

    try:
        dataset_dict = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": dataset_id}
        )
    except toolkit.ObjectNotFound:
        toolkit.error_shout(f"Dataset not found: {dataset_id}")
        sys.exit()

    backend = get_embeddings_backend()
    dataset_embedding = backend.get_embedding_for_dataset(dataset_dict)
    search_params = {}
    search_params["defType"] = "lucene"
    search_params["q"] = f"{{!knn f=vector topK={limit}}}{list(dataset_embedding)}"
    search_params["fq"] = f"-id:{dataset_dict['id']}"

    results = toolkit.get_action("package_search")({}, search_params)

    print(f"Related datasets to {dataset_dict['title']}")
    print("---------------")
    for result in results["results"]:

        print(result["title"])
