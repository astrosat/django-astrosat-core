# django-astrosat-core

## quick start

 1. in the project you want to use it type:
`pipenv install -e git+https://github.com/astrosat/django-astrosat-core.git@master#egg=django-astrosat`

 2. add "astrosat" to your INSTALLED_APPS settings like this:
```
     INSTALLED_APPS = [
         ...
         'astrosat',
         ...
    ]
```
 2. include the astrosat URLconf in your project "urls.py" like this:
 ```
	 path("", include("astrosat.urls")
 ```

 3. run `python manage.py migrate` to create the astrosat models.

 4. profit!

## developing

django-astrosat-core comes w/ an example project to help w/ developing/testing

1. `git clone <repo> django-astrosat-core`
2. `cd django-astrosat-core/example`
3. activate virtual environments as desired
4. `pipenv install`
5. `python manage.py makemigrations && python manage.py migrate` as needed
6. `python manage.py collectstatic --noinput` as needed
7. `python manage.py runserver` goto "http://localhost:8000" and enjoy

note that "django-astrosat-core/examples/Pipfile" was created using `pipenv install -e ..`; this uses a pointer to "django-astrosat-core/setup.py" in the virtual environment and creates a entry like [packages.ed0a5ba]; if the distribution changes just run `pipenv update ed0a5ba`, otherwise code changes should just be picked up b/c  of the `-e` flag.

note note that when things go wrong, I tend to get this error: "LookupError: No installed app with label 'admin'."
