import cProfile
import functools
import io
import operator
import pstats
import sys

from django.apps import apps
from django.conf import settings
from django.template import Context, Template

from pympler.classtracker import ClassTracker
from pympler.process import ProcessMemoryInfo
from pympler.util.stringutils import pp

from astrosat.conf import app_settings

#################
# debug_toolbar #
#################


def show_toolbar(request):
    """
    adds an extra check to the default SHOW_TOOLBAR_CALLBACK
    to allow me to toggle django-debug-toolbar via a DynamicSetting
    """
    from debug_toolbar.middleware import show_toolbar as _show_toolbar
    return _show_toolbar(request) and app_settings.ASTROSAT_ENABLE_DEBUG_TOOLBAR


#############
# profiling #
#############


def profile(n_calls=100, sort_key="cumulative", path=""):
    """A decorator that profiles a function
    Parameters
    ----------
    n_calls : int
        the number of calls to include in the profile.
    sort_key: str
        the profiling statistic to order calls by.
        valid options can be found at: https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats
    path : str
        A filename to output profiling statistics to (default is to print to stdout)
    """

    # there are multiple values for each SortKey; this clever code reduces them into a single list
    valid_sort_keys = functools.reduce(
        operator.add, [key._all_values for key in pstats.SortKey]
    )
    assert sort_key in valid_sort_keys, f"Invalid sort_key: '{sort_key}'."

    def profile_decorator(fn):
        @functools.wraps(fn)
        def profile_wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            try:
                profiler.enable()
                result = fn(*args, **kwargs)
                profiler.disable()
                return result
            finally:
                stream = io.StringIO()
                stats = pstats.Stats(profiler,
                                     stream=stream).sort_stats(sort_key)
                stats.print_stats(n_calls)
                stats_value = stream.getvalue()

                if not path:
                    print(stats_value)  # print to stdout
                else:
                    with open(path, "w") as fp:
                        fp.write(stats_value)  # print to path

        return profile_wrapper

    return profile_decorator


def track_memory(path=""):
    """
    A decorator that reports the memory usage of a function.
    This simulates the django-debug-toolbar panel that pympler provides.
    (note: b/c this decorator takes arguments, it must be called as a fn)
    Parameters
    ----------
    path : str
        A filename to output memory tracking statistics to (default is to print to stdout)
    """
    def track_memory_decorator(fn):
        @functools.wraps(fn)
        def track_memory_wrapper(*args, **kwargs):

            memory_info = {}
            tracker = ClassTracker()
            for cls in apps.get_models() + [Context, Template]:
                # track all models from registered apps, plus some standard Django ones
                tracker.track_class(cls)

            try:
                tracker.create_snapshot("before")
                memory_info["before"] = ProcessMemoryInfo()
                result = fn(*args, **kwargs)
                memory_info["after"] = ProcessMemoryInfo()
                tracker.create_snapshot("after")
                memory_info["stats"] = tracker.stats
                memory_info["stats"].annotate()
                return result

            finally:

                # record a whole bunch of memory statistics...
                resources = [
                    ("resident set size", memory_info["after"].rss),
                    ("virtual size", memory_info["after"].vsz),
                ]
                resources.extend(memory_info["after"] - memory_info["before"])
                resources = [(k, pp(v)) for k, v in resources]
                resources.extend(memory_info["after"].os_specific)

                # record each tracked class as of the final snapshot...
                classes_stats = []
                snapshot = memory_info["stats"].snapshots[-1]
                for class_name in memory_info["stats"].tracked_classes:
                    # history is a list of tuples that is updated on every creation/deletions: (timestamp, n_instances)
                    history = [
                        n for _, n in memory_info["stats"].history[class_name]
                    ]
                    if history:
                        classes_stats.append({
                            "name":
                                class_name,
                            "n_instances":
                                len(history),
                            "min_instances":
                                min(history),
                            "max_instances":
                                max(history),
                            "size":
                                pp(
                                    snapshot.classes.get(class_name,
                                                         {}).get("sum", 0)
                                ),
                        })

                if not path:
                    stream = sys.stdout
                else:
                    stream = open(path, "w")

                print("\nRESOURCES", file=stream)
                for k, v in resources:
                    print(f"{k:<26}: {v:>10}", file=stream)
                print("\nCLASSES", file=stream)
                for class_stats in classes_stats:
                    print(
                        "{name}: created/deleted {n_instances} times for a min/max of {min_instances}/{max_instances} instances: {size:>10}"
                        .format(**class_stats),
                        file=stream,
                    )

                stream.closed
                tracker.detach_all_classes()

        return track_memory_wrapper

    return track_memory_decorator
