from datetime import datetime, timezone
import sys
import uuid


import click


from ckan import model
from ckan.plugins import toolkit

from ckanext.embeddings.model import DatasetEmbedding
from ckanext.embeddings.lib import get_embeddings_backend


def get_commands():
    return [embeddings]


@click.group()
def embeddings():
    """"""
    pass


# TODO: token count function


@embeddings.command()
def create():
    """Creates"""
    i = 0
    backend = get_embeddings_backend()
    for dataset in (
        model.Session.query(model.Package).filter(model.Package.state == "active").all()
    ):

        computed_embedding = backend.get_embedding_for_dataset(dataset)

        dataset_embedding = (
            model.Session.query(DatasetEmbedding)
            .filter(DatasetEmbedding.package_id == dataset.id)
            .one_or_none()
        )

        if not dataset_embedding:
            dataset_embedding = DatasetEmbedding(package_id=dataset.id)

        dataset_embedding.updated = datetime.now(timezone.utc)
        dataset_embedding.embedding = computed_embedding

        model.Session.add(dataset_embedding)
        print(f"Computed embedding for dataset {dataset.title}")
        i = i + 1

    #        if i > 1:
    #            break

    model.Session.commit()


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


@embeddings.command()
@click.argument("dataset_id", type=str)
@click.option("-l", "--limit", type=int, default=5)
def related(dataset_id: str, limit: int):
    """Shows the closest neighbours to the provided dataset"""

    dataset = model.Package.get(dataset_id)
    if not dataset:
        toolkit.error_shout(f"Dataset not found: {dataset_id}")
        sys.exit()

    dataset_id = dataset.id

    dataset_embedding = (
        model.Session.query(DatasetEmbedding, model.Package.title)
        .join(model.Package)
        .filter(DatasetEmbedding.package_id == dataset_id)
        .one_or_none()
    )

    if not dataset_embedding:
        toolkit.error_shout(f"No embedding for dataset {dataset_id} found")
        sys.exit()

    r = (
        model.Session.query(DatasetEmbedding, model.Package.title)
        .join(model.Package)
        .filter(DatasetEmbedding.package_id != dataset_id)
        .order_by(
            DatasetEmbedding.embedding.cosine_distance(dataset_embedding[0].embedding)
        )
        .limit(limit)
        .all()
    )

    print(f"Related datasets to {dataset_embedding[1]}")
    print("---------------")
    for record in r:

        print(record[1])
