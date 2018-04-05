# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_jobs import __version__

REQUIREMENTS = [
    'aldryn-apphooks-config>=0.4.0',
    'django-appdata>=0.1.4',
    'django-bootstrap3',
    'django-cms>=3.4',
    'django-emailit',
    'django-parler',
    'django-standard-form',
    'djangocms-text-ckeditor>=1.0.10',
    'aldryn-boilerplates',
    'aldryn-common>=0.1.3',
    'aldryn-translation-tools>=0.2.1',
    # Although we don't actually yet use Aldryn Categories, it has been added
    # because of a migration dependency that sneaked in somehow. In any case we
    # plan to adopt Aldryn Categories for this project in a release in
    # the very near future.
    'aldryn-categories',
    'django-multiupload>=0.5.1',
    'django-sortedm2m>=1.2.2',
    'django-admin-sortable2>=0.5.2',
    'lxml',
    'pytz',
    'cssutils',
    'html5lib<=0.9999999',
    'Django>=1.8,<2.0',
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.11',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='aldryn-jobs',
    version=__version__,
    description='Publish job openings on your site',
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
    test_suite="test_settings.run",
)
