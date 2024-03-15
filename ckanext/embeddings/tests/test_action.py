import pytest

from ckan.plugins import toolkit
from ckan.tests import factories, helpers

pytestmark = pytest.mark.usefixtures("with_plugins")


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_package_similar_show():
    dataset1 = factories.Dataset(title="A dataset about chickens")

    dataset2 = factories.Dataset(title="A dataset about government budget")
    dataset3 = factories.Dataset(title="A dataset about cats")
    dataset4 = factories.Dataset(title="A dataset about ducks")

    similar = helpers.call_action("package_similar_show", id=dataset1["id"])

    assert [d["title"] for d in similar] == [
        dataset4["title"],
        dataset3["title"],
        dataset2["title"],
    ]


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_package_similar_show_limit():
    dataset1 = factories.Dataset(title="A dataset about chickens")

    dataset2 = factories.Dataset(title="A dataset about government budget")
    dataset3 = factories.Dataset(title="A dataset about cats")
    dataset4 = factories.Dataset(title="A dataset about ducks")

    similar = helpers.call_action("package_similar_show", id=dataset1["id"], limit=1)

    assert [d["title"] for d in similar] == [
        dataset4["title"],
    ]


def test_package_similar_show_wrong_limit():
    with pytest.raises(toolkit.ValidationError):
        helpers.call_action("package_similar_show", id="xxx", limit="a")


def test_package_similar_show_dataset_not_found():
    with pytest.raises(toolkit.ObjectNotFound):
        helpers.call_action("package_similar_show", id="xxx")


def test_package_similar_show_auth():
    user = factories.User()
    org = factories.Organization()
    dataset = factories.Dataset(owner_org=org["id"], private=True)

    with pytest.raises(toolkit.NotAuthorized):
        helpers.call_action(
            "package_similar_show",
            context={"user": user["name"], "ignore_auth": False},
            id=dataset["id"],
        )
