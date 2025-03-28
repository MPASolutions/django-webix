import os
import re
import sys

from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from django_dandelion/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version("django_webix", "__init__.py")

if sys.argv[-1] == "publish":
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    sys.exit()

if sys.argv[-1] == "tag":
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open("README.rst").read()
changelog = open("CHANGELOG.rst").read().replace(".. :changelog:", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-webix",
    version=version,
    packages=find_packages(exclude=("tests")),
    include_package_data=True,
    license="GNU GPLv3 License",
    description="",
    long_description=readme,
    url="https://github.com/MPASolutions/django-webix",
    author="MPA Solutions soc.coop., Enogis srl",
    author_email="info@mpasol.it",
    install_requires=[
        "Django>=4",
        "django-extra-views>=0.11.0",
        "six>=1.15.0",
        "django-user-agents>=0.4.0",  # limit use webix on old browsers
        "python-dateutil>=2.8.1",  # for date parsing
    ],
    extras_require={
        "kora": [
            "django==5.1.5",
            "django-extra-views==0.15.0",
            "six==1.16.0",
            "django-user-agents==0.4.0",
            "python-dateutil==2.9.0.post0",
            "sorl-thumbnail==12.11.0",
            "pillow==11.0.0",
            "django-two-factor-auth==1.17.0",
            "django-modeltranslation==0.19.9",
            "django-hijack==3.6.1",
            "django-mptt==0.16.0",
            "celery==5.4.0",
            "requests==2.32.3",
            "amqp==5.2.0",
            "billiard==4.2.1",
            "kombu==5.4.2",
            "vine==5.1.0",
            "phonenumbers==8.13.47",
            "python-telegram-bot>=13.1,<=13.1.5",
            "python-magic==0.4.27",
            "numpy==2.1.2",
            "pandas==2.2.3",
            "geopandas==1.0.1",
            "xlrd==2.0.1",
        ],
        "addones": [
            "sorl-thumbnail>=12.4.1",
            "pillow",
            "django-two-factor-auth>=1.12.1",
            "django-filtersmerger>=1.0.0",
            "django-modeltranslation",
            "django-hijack",
            # "flexport",
            # "gdpr",
        ],
        "admin": [
            "django-mptt>=0.11.0",
            "django-dal>=1.0.0",  # for filter
        ],
        "auth": [],
        "commands_manager": [
            "celery>=4.4.0",
        ],
        "filter": [
            "django-dal>=1.0.0",  # for filter
            "django-filtersmerger>=1.0.0",
        ],
        "sender": [
            "django-dal>=1.0.0",  # for filter
            "requests>=2.23.0",
            "celery>=4.4.0",
            "amqp>=2.3.2",
            "billiard>=3.5.0.4",
            "kombu>=4.2.1",
            "vine>=1.1.4",
            "phonenumbers>=8.12.13",
            "python-telegram-bot>=13.1,<=13.1.5",
        ],
        "validator": [
            "python-magic==0.4.27",  # ==0.4.27
            "numpy==1.21.5",  # 1.21.6
            "pandas>=1.3.5",
            "geopandas<=0.14.3",  # 0.14.4 bug
            "xlrd>=2.0.1",
        ],
    },
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
