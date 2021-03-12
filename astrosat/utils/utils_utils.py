def flatten_dictionary(dictionary, key="", separator="."):
    """
    Takes a nested dictionary and converts it to a 1D dictionary
    (keys of nested branches are concatenated together using separator)
    """

    dictionary_items = []
    for k, v in dictionary.items():
        new_key = key + separator + k if key else k
        if isinstance(v, dict):
            dictionary_items.extend(
                flatten_dictionary(v, key=new_key, separator=separator).items())
        else:
            dictionary_items.append((new_key, v))
    return dict(dictionary_items)
