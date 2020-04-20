import functools

from django.shortcuts import redirect


def conditional_redirect(conditional, redirect_name):

    """
    A decorator for a view that redirects to "redirect_name" if "conditional" is true
    Parameters
    ----------
    conditional : fn
        the function to check if a redirect will ocurr
    redirect_name: str
        the view name to redirect to
    """

    def _decorator(view_fn):
        @functools.wraps(view_fn)
        def _wrapper(*args, **kwargs):

            if conditional():
                return redirect(redirect_name)  # *args, **kwargs)
            return view_fn(*args, **kwargs)

        return _wrapper

    return _decorator


def conditional_exception(conditional, exception):
    """
    A decorator for a view that raises an exception if conditional is true
    """
    def _decorator(view_fn):
        @functools.wraps(view_fn)
        def _wrapper(request, *args, **kwargs):

            if conditional(request):
                raise exception
            return view_fn(request, *args, **kwargs)

        return _wrapper

    return _decorator
