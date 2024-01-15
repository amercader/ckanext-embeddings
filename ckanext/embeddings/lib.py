import os
import logging

from sentence_transformers import SentenceTransformer
from openai import OpenAI
import tiktoken

from ckan.plugins import toolkit


log = logging.getLogger(__name__)


class BaseEmbeddingsBackend:
    def get_dataset_values(self, dataset_dict):

        if dataset_dict.get("notes"):
            return dataset_dict["title"] + " " + dataset_dict["notes"]
        else:
            return dataset_dict["title"]

        #return dataset_dict["title"]

    def get_embedding_for_dataset(self, dataset_dict):

        return self.create_embedding(self.get_dataset_values(dataset_dict))

    def get_embedding_for_string(self, value):

        return self.create_embedding(value)

    def create_embedding(self, values):
        raise NotImplemented


class SentenceTransformerBackend(BaseEmbeddingsBackend):

    model = None

    def __init__(self):
        # TODO: config model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # self.model = SentenceTransformer("distiluse-base-multilingual-cased-v1")

    def _check_input_length(self, values):
        num_input = len(
            self.model[0]
            .tokenizer(values, return_attention_mask=False, return_token_type_ids=False)
            .input_ids
        )
        max_input = self.model.max_seq_length
        if num_input > max_input:
            log.info(
                f"Too many input values, input will be truncated ({num_input} vs {max_input})"
            )

    def create_embedding(self, values):
        self._check_input_length(values)

        return self.model.encode(values)


class OpenAIBackend(BaseEmbeddingsBackend):

    client = None

    def __init__(self):
        # TODO: config declaration
        api_key = toolkit.config.get(
            "ckanext.embeddings.openai.api_key", os.environ.get("OPENAI_API_KEY")
        )

        self.client = OpenAI(api_key=api_key)

    def _check_input_length(self, values):
        # TODO: configure
        encoding = tiktoken.get_encoding("cl100k_base")
        max_input = 8191
        num_tokens = len(encoding.encode(values))
        log.debug(f"[OpenAI Embeddings API] Input size: {num_tokens}")
        if num_tokens > max_input:
            log.info(
                f"Too many input values, input will be truncated ({num_tokens} vs {max_input})"
            )

    def create_embedding(self, values):

        self._check_input_length(values)

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

    # TODO: configure
    #backend = "openai"

    backend = "sentence_transformers"

    return embeddings_backends[backend]()
