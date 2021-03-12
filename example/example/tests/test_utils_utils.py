import pytest

from astrosat.utils import flatten_dictionary


def test_flatten_dictionary():
    test_dictionary = {"I": {"AM": {"A": {"NESTED": "DICTIONARY"}}}}
    flattened_test_dictionary = flatten_dictionary(test_dictionary,
                                                   separator="-")
    assert flattened_test_dictionary == {"I-AM-A-NESTED": "DICTIONARY"}
