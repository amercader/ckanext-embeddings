from ckan.plugins import toolkit

import logging
log = logging.getLogger(__name__)

@toolkit.side_effect_free
def package_similar_show(context, data_dict):

    toolkit.check_access("package_similar_show", context, data_dict)

    dataset_id = toolkit.get_or_bust(data_dict, "id")
    limit = data_dict.get("limit") or 5
    try:
        limit = int(limit)
    except ValueError:
        raise toolkit.ValidationError(f"Wrong value for limit paramater: {limit}")

    field_name = toolkit.config.get("ckanext.embeddings.solr_vector_field_name", "vector")

    try:
        vectors = toolkit.get_action("package_search")(
            {"ignore_auth": True}, {"fq": f"(id:{dataset_id} OR name:{dataset_id})", 'fl':f"{field_name},id"}
        )['results']
        dataset_dict = vectors.pop()
        dataset_embedding = dataset_dict[field_name]
    except IndexError:
        raise toolkit.ObjectNotFound(f"Dataset not found: {dataset_id}")

    search_params = {}
    search_params["defType"] = "lucene"
    search_params["q"] = f"{{!knn f={field_name} topK={limit}}}{list(dataset_embedding)}"
    search_params["fq"] = f"-id:{dataset_dict['id']}"

    results = toolkit.get_action("package_search")({}, search_params)

    return results["results"]
