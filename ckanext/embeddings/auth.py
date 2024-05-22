from ckan.plugins import toolkit
from ckan.authz import is_authorized

@toolkit.auth_allow_anonymous_access
def package_similar_show(context, data_dict):
    return is_authorized("package_show", context, data_dict)
