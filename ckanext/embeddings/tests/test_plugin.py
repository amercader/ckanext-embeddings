import pytest
from ckan.plugins import plugin_loaded
import ckanext.embeddings.plugin as plugin


@pytest.mark.ckan_config("ckan.plugins", "embeddings")
@pytest.mark.usefixtures("with_plugins")
def test_plugin():
    assert plugin_loaded("embeddings")
