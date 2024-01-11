from ckan.authz import is_authorized


def package_similar_show(context, data_dict):
    return is_authorized("package_show", context, data_dict)
