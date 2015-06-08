# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from aldryn_jobs import __version__

py26 = sys.version_info < (2, 7, 0) and sys.version_info >= (2, 6, 5)
py27 = sys.version_info < (2, 8, 0) and sys.version_info >= (2, 7, 0)

if not py26 and not py27:
    raise ValueError(
        "Aldryn Events currently support only python >= 2.6.5"
    )


REQUIREMENTS = [
    'South<1.1,>=1.0.2',
    'aldryn-apphooks-config>=0.1.3',
    'django-emailit',
    'django-parler',
    'django-standard-form',
    'djangocms-text-ckeditor>= 1.0.10',
    'aldryn-boilerplates',
    'aldryn-common>=0.0.4',
    'aldryn-reversion>=0.0.2',
    'unidecode',
    'django-multiupload>=0.3',
    'django-sortedm2m'
]

if py26:
    REQUIREMENTS += [
        'Django<1.7,>1.5',
        'ordereddict',
    ]

if py27:
    REQUIREMENTS += [
        'Django<1.8,>1.5',
    ]

DEPENDENCY_LINKS = [
    'https://github.com/aldryn/aldryn-apphooks-config/archive/master.zip#egg=aldryn-apphooks-config-0.1.3'  # NOQA
]

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='aldryn-jobs',
    version=__version__,
    description='Publish job offers on your site',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-jobs',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    dependency_links=DEPENDENCY_LINKS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
)
