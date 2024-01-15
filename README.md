
# ckanext-embeddings

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

1. Similar datasets

By computing all datasets embeddings and rank them against a particular dataset one, we can get the most
similar datasets to the one provided according to the model. This similarity won't just take text-based similarity
into account but also but the meaning and context of the dataset metadata. So for instance when looking for similar
datasets to a "Bathing Water Quality" one, besides other datasets explicitly mentioning "water quality" in their
metadata you'll get others that might include things like "Wastewater Treatment", "Aquaculture Sites" or "Lakes".

The plugin adds a `package_similar_show` action that will return the closest datasets to the one provided with
the `id` parameter (id or name). 5 are returned by default, which can be changed using the `limit` paramater.


2. Semantic search

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

## Implementation

TODO

## Customizing

TODO

## Requirements

Tested on CKAN 2.10/master

As of January 2024 this plugin requires a patch in CKAN core to allow the use of
local fields in Solr queries (an upstream patch will be submitted to handle this 
via configuration instead):

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
CKAN Solr images that you can use (you might need to adjust it to the model you use, see TODO):

```
cd solr
docker build -t ckan/ckan-solr:2.10-solr9-vector .
docker run --name ckan-solr-9-vector -d ckan/ckan-solr:2.10-solr9-vector
```


## Installation

To install ckanext-embeddings:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-embeddings.git
    cd ckanext-embeddings
    pip install -e .
	pip install -r requirements.txt

3. Add `embeddings` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Config settings

None at present

**TODO:** Document any optional config settings here. For example:

	# The minimum number of hours to wait before re-checking a resource
	# (optional, default: 24).
	ckanext.embedding.some_setting = some_default_value


## Developer installation

To install ckanext-embeddings for development, activate your CKAN virtualenv and
do:

    git clone https://github.com//ckanext-embeddings.git
    cd ckanext-embeddings
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
