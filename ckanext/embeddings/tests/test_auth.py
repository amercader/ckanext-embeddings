import pytest

from ckan.plugins import toolkit
from ckan.tests import factories, helpers

pytestmark = pytest.mark.usefixtures("with_plugins")


def test_package_similar_show_auth_public_dataset():

    dataset = factories.Dataset()
    context = {"user": ""}
    assert helpers.call_auth("package_similar_show", context, id=dataset["id"])

    user = factories.User()
    context = {"user": user["name"]}
    assert helpers.call_auth("package_similar_show", context, id=dataset["id"])


def test_package_similar_show_auth_private_dataset():

    user1 = factories.User()
    user2 = factories.User()
    org = factories.Organization(users=[{"name": user1["name"], "capacity": "member"}])
    dataset = factories.Dataset(private=True, owner_org=org["id"])
    context = {"user": ""}
    with pytest.raises(toolkit.NotAuthorized):
        helpers.call_auth("package_similar_show", context, id=dataset["id"])

    context = {"user": user2["name"]}
    with pytest.raises(toolkit.NotAuthorized):
        helpers.call_auth("package_similar_show", context, id=dataset["id"])

    context = {"user": user1["name"]}
    assert helpers.call_auth("package_similar_show", context, id=dataset["id"])
