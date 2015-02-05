# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_jobs import __version__

REQUIREMENTS = [
    'django-emailit',
    'django-hvad',
    'django-standard-form',
    # This might cause issues because the 2.x release of djangocms-text-ckeditor is not cms 2.x compatible.
    'djangocms-text-ckeditor>= 1.0.10',
    'aldryn-common>=0.0.4',
    'unidecode',
    'django-multiupload>=0.3',
    'django<1.8,>1.5',
    'South>=1.0.2',
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
    zip_safe=False
)
