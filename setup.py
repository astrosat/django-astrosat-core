import os
from setuptools import find_packages, find_namespace_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# dynamically compute the version, etc....
author = __import__("astrosat").__author__
title = __import__("astrosat").__title__
version = __import__("astrosat").__version__

install_requires = [
    # django, duh
    "django~=3.0",
    # api
    "djangorestframework~=3.0",
    # easier json validation
    "jsonschema>=3.0",
    # S3 access
    "boto3>=1.12",
    # provides logging handler for logstash (analytics)
    "python-logstash~=0.4.6",
    # profiling
    "pympler>=0.8",
]  # yapf: disable

setup(
    name=title,
    version=version,
    author=author,
    url="https://github.com/astrosat/django-astrosat-core",
    description="Behold Django-Astrosat-Core!",
    long_description=README,
    install_requires=install_requires,
    packages=find_packages(exclude=["example"]),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
