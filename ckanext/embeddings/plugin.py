import ckan.plugins as plugins

from ckan import model
import ckan.plugins.toolkit as toolkit

from ckanext.embeddings.model import DatasetEmbedding
from ckanext.embeddings import cli
from ckanext.embeddings.lib import get_embeddings_backend


class EmbeddingPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IDatasetForm

    def before_dataset_index(self, dataset_dict):

        dataset_id = dataset_dict["id"]

        # TODO generate here

        dataset_embedding = (
            model.Session.query(DatasetEmbedding)
            .filter(DatasetEmbedding.package_id == dataset_id)
            .one_or_none()
        )

        if dataset_embedding:
            dataset_dict["vector"] = list(map(str, dataset_embedding.embedding))

        return dataset_dict

    def before_dataset_search(self, search_params):

        if not toolkit.asbool(search_params.get("extras", {}).get("ext_vector_search")):
            return search_params

        q = search_params.get("q")

        if not q or q == "*:*":
            return search_params

        search_params["defType"] = "lucene"

        # TODO: default
        rows = search_params.get("rows", 10)

        # TODO: reuse?
        backend = get_embeddings_backend()

        # {!knn f%3Dvector topK%3D10}[embedding]

        embedding = backend.get_embedding_for_string(q)

        search_params["q"] = f"{{!knn f=vector topK={rows}}}{list(embedding)}"

        return search_params
