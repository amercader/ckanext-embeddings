
# ckanext-embeddings

[![Tests](https://github.com/amercader/ckanext-embeddings/workflows/Tests/badge.svg?branch=main)](https://github.com/amercader/ckanext-embeddings/actions)

An extension that uses Machine Learning Embeddings to provide similarity-based features for CKAN portals. Currently there are two features explored:

* Returning similar datasets
* Performing Semantic Search in Solr integrated with the usual CKAN search


|                              :warning: Note :warning:                              |
| ---------------------------------------------------------------------------------- |
| This is just an alpha version and has not been tested in any real world deployment |

## What this does

Embeddings are a Machine Learning technique that allows to encode complex pieces of information
like text or images as numerical vectors (lists of numbers) that encode the relationships and
similarities between these pieces of information. The closer the vectors are, the more similar
these objects are according to the underlying model used to create the embeddings. There are many
introductory resources to learn more about embeddings, here are some I found useful:

* [Embeddings: What they are and why they matter](https://simonwillison.net/2023/Oct/23/embeddings/)
* [What are embeddings in machine learning?](https://www.cloudflare.com/en-gb/learning/ai/what-are-embeddings/)
* [Getting Started With Embeddings](https://huggingface.co/blog/getting-started-with-embeddings)

In the context of CKAN, this plugin computes embeddings for all datasets, using their metadata
(their title or description, but also any other relevant metadata field can be used). Being able to
compare datasets allows us to build features that increase discoverability of relevant data for users.

Right now there are two features implemented:

#### 1. Similar datasets

By computing all datasets embeddings and rank them against a particular dataset one, we can get the most
similar datasets to the one provided according to the model. This similarity won't just take text-based similarity
into account but also but the meaning and context of the dataset metadata. So for instance when looking for similar
datasets to a "Bathing Water Quality" one, besides other datasets explicitly mentioning "water quality" in their
metadata you'll get others that might include things like "Wastewater Treatment", "Aquaculture Sites" or "Lakes".

The plugin adds a `package_similar_show` action that will return the closest datasets to the one provided with
the `id` parameter (id or name). 5 are returned by default, which can be changed using the `limit` parameter.


#### 2. Semantic search

Following the same approach as above, we can rank the embeddings of the portal datasets not against another dataset
title but against an arbitrary query term. That will give us the most similar datasets to the provided search term,
and as it is Solr what is performing the query, we can include any additional filters like in the normal CKAN search.

There's one important distinction though, and that is that the Semantic or Vector search always returns a fixed number
of results, regardless of relevance. The standard search UI hasn't been modified to account for this fact, but it
probably should.

With the plugin activated, you can pass an extra parameter to the `package_search` action to perform a semantic search
instead of the default Solr one (Solr calls this [Dense Vector Search](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)).
Consider the following standard search calls from the command line:

```
ckanapi action package_search q=boats | jq ".results[].title"

"Inshore boat-based cetacean Survey 2011"
"Inshore boat-based cetacean Survey 2012"
"Inshore boat-based cetacean Survey 2010"
"Boat-based Visual Surveys for Bottlenose Dolphins in the West Connacht Coast SAC in 2021"
"Bottlenose dolphins in the Lower River Shannon SAC, 2022"
```

And this time using the semantic search:

```
ckanapi action package_search q=boats extras='{"ext_vector_search":"true"}' | jq ".results[].title"

"Marinas"
"Estuary"
"Fishing Port"
"Sailing Density"
"Surfing"
"Ship Wrecks in Irish Waters - Recorded Year of Loss"
"Sea Cliff"
"Seascape Coastal Type"
"Midwater Trawl FIshing"
"Net Fishing"
```

Remember that the Semantic Search will always return a fixed number of datasets (the default in this case is 10).

## Requirements

Tested on CKAN 2.10/master

This plugin requires at least CKAN 2.10.4 and 2.9.11, as it needs [ckan/ckan#8053](https://github.com/ckan/ckan/pull/8053).

If for some reason you can't upgrade to a newer version, you'll need the following patch
in CKAN core to allow the use of local fields in Solr queries:

```diff
diff --git a/ckan/lib/search/query.py b/ckan/lib/search/query.py
index 70869ae3f..fb56016c0 100644
--- a/ckan/lib/search/query.py
+++ b/ckan/lib/search/query.py
@@ -397,8 +397,10 @@ class PackageSearchQuery(SearchQuery):

         query.setdefault("df", "text")
         query.setdefault("q.op", "AND")
+
+
         try:
-            if query['q'].startswith('{!'):
+            if query['q'].startswith('{!') and not query['q'].startswith('{!knn'):
                 raise SearchError('Local parameters are not supported.')
         except KeyError:
             pass

```

The Semantic Search feature requires a custom Solr schema, with a [Dense Vector Search](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html) field. Included in the plugin there is a Dockerfile based on the official
CKAN Solr images that you can use (you might need to adjust it to the model you use, see [Customizing](/#customizing)):

```
cd solr
docker build -t ckan/ckan-solr:2.10-solr9-vector .
docker run --name ckan-solr-9-vector -d ckan/ckan-solr:2.10-solr9-vector
```

## Customizing

You can choose the backend used to generate the embeddings by settings the `ckanext.embeddings.backend` config option.
Right now the plugin includes two backends, one that runs locally using  [Sentence Transformers](https://www.sbert.net/)'s `all-MiniLM-L6-v2` model (`sentence_transformers`, the default one) and one that uses OpenAI's Embeddings API (`openai`). You will need
to provide an API key for this one, either via the `ckanext.embeddings.openai.api_key` config option or a `OPENAI_API_KEY` env var.

Additionally, it's really easy to provide your own backends. You can write your own class that inherits from
`ckanext.embeddings.backends.BaseEmbeddingsBackend` and provide the following methods:

```python
from ckanext.embeddings.backends import BaseEmbeddingsBackend

class MyBackend(BaseEmbeddingsBackend):
    def get_dataset_values(self, dataset_dict):
        """ Return the text value that should be used to create the embedding
            for a particular dataset. This can include any custom fields in
            addition to the standard title or notes
        """
        return dataset_dict["title"]

    def create_embedding(self, values):
        """ Return the actual embeddings vector for the provided values"
        """
        pass
```

Once implemented, register your backend by adding it to the `ckanext.embeddings.backends` entry point
in your extension `setup.cfg` file:

```
[options.entry_points]
ckan.plugins =
             my_plugin = ckanext.my_ext.plugin:MyPlugin

babel.extractors =
                 ckan = ckan.lib.extract:extract_ckan

ckanext.embeddings.backends =
        my_embeddings_backend = ckanext.my_ext.embeddings:MyBackend
```

You can then start using by setting `ckanext.embeddings.backend = my_embeddings_backend` in your ini file.

Remember that the dimensions set in the Solr vector field need to match the ones used in the embeddings model you use.
When trying out different models it might be handy to define different vector fields and switch from one
to the other to test the returned values using the `ckanext.embeddings.solr_vector_field_name` config, e.g:

```dockerfile
FROM ckan/ckan-solr:2.10-solr9

USER root

# Sentence Transformers all-MiniLM-L6-v2 (Default)
ENV SOLR_VECTOR_FIELD_DEFINITION '<fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="384" similarityFunction="cosine"/>'
ENV SOLR_VECTOR_FIELD '<field name="vector" type="knn_vector" indexed="true" stored="true"/>'

RUN sed -i "/<types>/a $SOLR_VECTOR_FIELD_DEFINITION" $SOLR_SCHEMA_FILE
RUN sed -i "/<fields>/a $SOLR_VECTOR_FIELD" $SOLR_SCHEMA_FILE

# Sentence Transformers all-mpnet-base-v2
ENV SOLR_VECTOR_FIELD_DEFINITION '<fieldType name="knn_vector_2" class="solr.DenseVectorField" vectorDimension="768" similarityFunction="cosine"/>'
ENV SOLR_VECTOR_FIELD '<field name="vector_st_mpnet" type="knn_vector_2" indexed="true" stored="true"/>'

RUN sed -i "/<types>/a $SOLR_VECTOR_FIELD_DEFINITION" $SOLR_SCHEMA_FILE
RUN sed -i "/<fields>/a $SOLR_VECTOR_FIELD" $SOLR_SCHEMA_FILE

# OpenAI
ENV SOLR_VECTOR_FIELD_DEFINITION '<fieldType name="knn_vector_3" class="solr.DenseVectorField" vectorDimension="1536" similarityFunction="cosine"/>'
ENV SOLR_VECTOR_FIELD '<field name="vector_openai" type="knn_vector_3" indexed="true" stored="true"/>'

RUN sed -i "/<types>/a $SOLR_VECTOR_FIELD_DEFINITION" $SOLR_SCHEMA_FILE
RUN sed -i "/<fields>/a $SOLR_VECTOR_FIELD" $SOLR_SCHEMA_FILE

USER solr

```

And then in the ini file you can choose the Solr field used to when indexing/querying:

```ini
ckanext.embeddings.solr_vector_field_name = vector
#ckanext.embeddings.solr_vector_field_name = vector_st_mpnet
#ckanext.embeddings.solr_vector_field_name = vector_openai
```



## Installation

To install ckanext-embeddings:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-embeddings.git
    cd ckanext-embeddings
    pip install .
	pip install -r requirements.txt

3. Add `embeddings` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Add the following configuration option to allow the use of a custom query parser
   in Solr:

         ckan.search.solr_allowed_query_parsers = knn

5. Restart the CKAN process.

## Config settings

See [Customizing](#customizing).


## Developer installation

To install ckanext-embeddings for development, activate your CKAN virtualenv and
do:

    git clone https://github.com//ckanext-embeddings.git
    cd ckanext-embeddings
    pip install -e .
    pip install -r requirements.txt
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
