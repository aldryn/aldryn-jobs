# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_jobs import __version__

REQUIREMENTS = [
    'Django<1.8,>=1.5',
    'South<1.1,>=1.0.2',
    'aldryn-apphooks-config>=0.1.0',
    'django-emailit',
    'django-parler',
    'django-standard-form',
    'djangocms-text-ckeditor>= 1.0.10',
    'aldryn-common>=0.0.4',
    'unidecode',
    'django-multiupload>=0.3',
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
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
    dependency_links=[
        'git+https://github.com/yakky/django-cms@future/integration#egg=django-cms-3.0.90a3',
        'git+https://github.com/aldryn/aldryn-apphooks-config#egg=aldryn-apphooks-config-0.1.0',
    ],
)
