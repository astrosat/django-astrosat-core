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

    def conditional_redirect_decorator(view_fn):

        @functools.wraps(view_fn)
        def conditional_redirect_wrapper(*args, **kwargs):

            if conditional():
                return redirect(redirect_nam)  # *args, **kwargs)
            return view_fn(*args, **kwargs)

        return conditional_redirect_wrapper

    return conditional_redirect_decorator
