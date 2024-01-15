import ckan.plugins as plugins

from ckan import model
import ckan.plugins.toolkit as toolkit

from ckanext.embeddings.model import DatasetEmbedding
from ckanext.embeddings import cli
from ckanext.embeddings.actions import package_similar_show
from ckanext.embeddings.auth import package_similar_show as package_similar_show_auth
from ckanext.embeddings.lib import get_embeddings_backend


class EmbeddingPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IPackageController, inherit=True)

    backend = None

    # IConfigurer

    def update_config(self, config):

        self.backend = get_embeddings_backend()

        toolkit.add_template_directory(config, "templates")

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IActions

    def get_actions(self):
        return {"package_similar_show": package_similar_show}

    # IAuthFunctions

    def get_auth_functions(self):
        return {"package_similar_show": package_similar_show_auth}

    # IDatasetForm

    def before_dataset_index(self, dataset_dict):

        dataset_id = dataset_dict["id"]

        if not self.backend:
            self.backend = get_embeddings_backend()
        dataset_embedding = self.backend.get_embedding_for_dataset(dataset_dict)

        if dataset_embedding is not None:
            field_name = toolkit.config.get(
                "ckanext.embeddings.solr_vector_field_name", "vector"
            )
            dataset_dict[field_name] = list(map(str, dataset_embedding))

        return dataset_dict

    def before_dataset_search(self, search_params):

        if not toolkit.asbool(search_params.get("extras", {}).get("ext_vector_search")):
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
