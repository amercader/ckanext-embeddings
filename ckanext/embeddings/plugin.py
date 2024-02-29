import json

import ckan.plugins as plugins

from ckan import model
import ckan.plugins.toolkit as toolkit

from ckanext.embeddings import cli, helpers
from ckanext.embeddings.actions import package_similar_show
from ckanext.embeddings.auth import package_similar_show as package_similar_show_auth
from ckanext.embeddings.backends import get_embeddings_backend


class EmbeddingPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IPackageController, inherit=True)

    _backend = None

    @property
    def backend(self):
        if self._backend is None:
            self._backend = get_embeddings_backend()
        return self._backend

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_resource("assets", "ckanext-embeddings")

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IActions

    def get_actions(self):
        return {"package_similar_show": package_similar_show}

    # IAuthFunctions

    def get_auth_functions(self):
        return {"package_similar_show": package_similar_show_auth}

    # ITemplateHelpers

    def get_helpers(self):
        return {"embeddings_get_similar_datasets": helpers.get_similar_datasets}

    # IDatasetForm

    def before_dataset_index(self, dataset_dict):

        dataset_id = dataset_dict["id"]

        dataset_embedding = self.backend.get_embedding_for_dataset(dataset_dict)

        if dataset_embedding is not None:
            field_name = toolkit.config.get(
                "ckanext.embeddings.solr_vector_field_name", "vector"
            )
            dataset_dict[field_name] = list(map(str, dataset_embedding))

        return dataset_dict

    def before_dataset_search(self, search_params):
        extras = search_params.get("extras", {})
        if isinstance(extras, str):
            try:
                extras = json.loads(extras)
            except ValueError:
                raise toolkit.ValidationError(
                    {"extras": f"Wrong JSON object: {extras}"}
                )

        if not toolkit.asbool(extras.get("ext_vector_search")):
            return search_params

        q = search_params.get("q")

        if not q or q == "*:*" or q.startswith("!{knn"):
            return search_params

        search_params["defType"] = "lucene"

        # TODO: default
        rows = search_params.get("rows", 10)

        embedding = self.backend.get_embedding_for_string(q)

        field_name = toolkit.config.get(
            "ckanext.embeddings.solr_vector_field_name", "vector"
        )

        search_params["q"] = f"{{!knn f={field_name} topK={rows}}}{list(embedding)}"

        return search_params
