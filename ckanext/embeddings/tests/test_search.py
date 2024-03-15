from unittest import mock
import pytest

from ckan.plugins import toolkit
from ckan.tests import factories, helpers

from ckan.lib.search.query import PackageSearchQuery


pytestmark = pytest.mark.usefixtures("with_plugins")


@pytest.mark.usefixtures("clean_index")
def test_embedding_gets_indexed():

    dataset = factories.Dataset()

    index = PackageSearchQuery().get_index(dataset["id"])

    assert "vector" in index
    assert index["vector"] and isinstance(index["vector"], list)


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_semantic_search():

    dataset1 = factories.Dataset(title="A dataset about government budgets")
    dataset2 = factories.Dataset(title="A dataset about a duck")
    dataset3 = factories.Dataset(title="A dataset about a cat")

    results = helpers.call_action(
        "package_search", q="a furry animal", extras={"ext_vector_search": True}
    )

    assert [r["title"] for r in results["results"]] == [
        dataset3["title"],
        dataset2["title"],
        dataset1["title"],
    ]


def test_semantic_search_query_syntax():

    with mock.patch("ckan.lib.search.query.make_connection") as m:
        results = helpers.call_action(
            "package_search", q="a furry animal", extras={"ext_vector_search": True}
        )
        local_params = "{!knn f=vector topK=10}"
        q = m.mock_calls[1].kwargs["q"]
        assert q.startswith(local_params)


def test_semantic_search_needs_param():

    with mock.patch("ckan.lib.search.query.make_connection") as m:
        results = helpers.call_action("package_search", q="a furry animal")
        local_params = "{!knn f=vector topK=10}"
        q = m.mock_calls[1].kwargs["q"]
        assert not q.startswith(local_params)


def test_semantic_search_needs_q():

    with mock.patch("ckan.lib.search.query.make_connection") as m:
        results = helpers.call_action(
            "package_search", extras={"ext_vector_search": True}
        )
        local_params = "{!knn f=vector topK=10}"
        q = m.mock_calls[1].kwargs["q"]
        assert not q.startswith(local_params)


def test_semantic_search_wrong_extras():

    with pytest.raises(toolkit.ValidationError):
        results = helpers.call_action("package_search", extras="wrong")


@pytest.mark.ckan_config("ckanext.embeddings.solr_vector_field_name", "my_vector_field")
def test_semantic_search_query_syntax_custom_field():

    with mock.patch("ckan.lib.search.query.make_connection") as m:
        results = helpers.call_action(
            "package_search", q="a furry animal", extras={"ext_vector_search": True}
        )
        local_params = "{!knn f=my_vector_field topK=10}"
        q = m.mock_calls[1].kwargs["q"]
        assert q.startswith(local_params)
