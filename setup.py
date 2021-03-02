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
    raise RuntimeError('Unable to find version string.')


version = get_version("django_webix", "__init__.py")

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
changelog = open('CHANGELOG.rst').read().replace('.. :changelog:', '')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-webix',
    version=version,
    packages=find_packages(exclude=('tests')),
    include_package_data=True,
    license='GNU GPLv3 License',
    description='',
    long_description=readme,
    url='https://github.com/MPASolutions/django-webix',
    author='MPA Solutions',
    author_email='info@mpasol.it',
    install_requires=[
        'Django>=1.11',
        'sorl-thumbnail>=12.4.1',
        'django-extra-views>=0.11.0',
        'django-mptt>=0.11.0',
        'django-two-factor-auth>=1.12.1',
        'django-user-agents>=0.4.0',
        'python-dateutil>=2.8.1',
        'six>=1.15.0',
        'django-dal>=1.0.0',
        'django-filtersmerger>=1.0.0',
        # FIXME: feincms admin_webix
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
