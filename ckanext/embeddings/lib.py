from sentence_transformers import SentenceTransformer
from openai import OpenAI


class BaseEmbeddingsBackend:
    def get_dataset_values(self, dataset):

        #TODO: only dataset_dicts when migrating to index-time

        if isinstance(dataset, dict):
            return dataset["title"]
        else:
            return dataset.title

    def get_embedding_for_dataset(self, dataset):

        return self.create_embedding(self.get_dataset_values(dataset))

    def get_embedding_for_string(self, value):

        return self.create_embedding(value)

    def create_embedding(self, values):
        raise NotImplemented


class SentenceTransformerBackend(BaseEmbeddingsBackend):

    model = None

    def __init__(self):
        # TODO: config model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        #self.model = SentenceTransformer("distiluse-base-multilingual-cased-v1")

    def create_embedding(self, values):

        return self.model.encode(values)


class OpenAIBackend(BaseEmbeddingsBackend):

    client = None

    def __init__(self):
        # TODO: config API key

        self.client = OpenAI()

    def create_embedding(self, values):

        # TODO: config model
        response = self.client.embeddings.create(
            input=values, model="text-embedding-ada-002"
        )
        embeddings = [v.embedding for v in response.data]

        return embeddings[0]


embeddings_backends = {
    "sentence_transformers": SentenceTransformerBackend,
    "openai": OpenAIBackend,
}


def get_embeddings_backend():

    #TODO: configure
    backend = "sentence_transformers"

    return embeddings_backends[backend]()

