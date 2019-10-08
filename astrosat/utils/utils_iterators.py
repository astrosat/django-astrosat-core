from itertools import filterfalse, tee, zip_longest


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    from: https://docs.python.org/3/library/itertools.html#itertools-recipes
    """
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def partition(pred, iterable):
    """
    Use a predicate to partition entries into false entries and true entries
    from: https://docs.python.org/dev/library/itertools.html#itertools-recipes
    """
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)
