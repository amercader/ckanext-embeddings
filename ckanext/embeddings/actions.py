from ckan.plugins import toolkit

from ckanext.embeddings.lib import get_embeddings_backend


@toolkit.side_effect_free
def package_similar_show(context, data_dict):
    dataset_id = toolkit.get_or_bust(data_dict, "id")
    limit = data_dict.get("limit", 5)
    try:
        limit = int(limit)
    except ValueError:
        raise toolkit.ValidationError(f"Wrong value for limit paramater: {limit}")

    try:
        dataset_dict = toolkit.get_action("package_show")(
            {"ignore_auth": True}, {"id": dataset_id}
        )
    except toolkit.ObjectNotFound:
        raise toolkit.ObjectNotFound(f"Dataset not found: {dataset_id}")

    backend = get_embeddings_backend()
    dataset_embedding = backend.get_embedding_for_dataset(dataset_dict)

    field_name = toolkit.config.get("ckanext.embeddings.solr_vector_field_name", "vector")

    search_params = {}
    search_params["defType"] = "lucene"
    search_params["q"] = f"{{!knn f={field_name} topK={limit}}}{list(dataset_embedding)}"
    search_params["fq"] = f"-id:{dataset_dict['id']}"

    results = toolkit.get_action("package_search")({}, search_params)

    return results["results"]
