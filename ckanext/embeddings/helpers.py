from ckan.plugins import toolkit


def get_similar_datasets(dataset_id, limit=None):
    try:
        datasets = toolkit.get_action("package_similar_show")(
            {}, {"id": dataset_id, "limit": limit}
        )
    except toolkit.ObjectNotFound:
        datasets = []

    return datasets
