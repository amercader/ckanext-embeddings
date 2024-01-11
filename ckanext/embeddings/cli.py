from datetime import datetime, timezone
import sys
import uuid


import click


from ckan import model
from ckan.plugins import toolkit



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

    print(f"Similar datasets to {dataset_id}")
    print("---------------")
    for r in result:

        print(f"{r['id']} - {r['title']}")
