# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from aldryn_jobs import __version__

REQUIREMENTS = [
    'South<1.1,>=1.0.2',
    'aldryn-apphooks-config>=0.1.3',
    'django-bootstrap3',
    'django-emailit',
    'django-parler',
    'django-standard-form',
    'djangocms-text-ckeditor>= 1.0.10',
    'aldryn-boilerplates',
    'aldryn-common>=0.0.4',
    'aldryn-reversion>=0.0.2',
    # aldryn categories has been added because of a migration dependency
    # which sneaked somehow and we need it to be properly migrated
    # also it would be used heavily in future (after a switch to this package
    # instead of aldryn-jobs own categories).
    'aldryn-categories',
    'unidecode',
    'django-multiupload>=0.3',
    'django-sortedm2m',
]

py26 = sys.version_info < (2, 7, 0) and sys.version_info >= (2, 6, 5)
if py26:
    REQUIREMENTS += [
        'Django<1.7,>1.5',
        'ordereddict',
    ]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.6',
    'Framework :: Django :: 1.7',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
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
    classifiers=CLASSIFIERS,
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
)
