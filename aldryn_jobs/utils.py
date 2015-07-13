# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os.path import splitext
from django.core.urlresolvers import reverse, NoReverseMatch

from django.utils.text import get_valid_filename as get_valid_filename_django
from django.template.defaultfilters import slugify


def get_valid_filename(s):
    """
    like the regular get_valid_filename, but also slugifies away umlauts and
    stuff. Copied from django-filer
    """
    s = get_valid_filename_django(s)
    filename, ext = splitext(s)
    filename = slugify(filename)
    ext = slugify(ext)
    if ext:
        return "%s.%s" % (filename, ext)
    else:
        return "%s" % (filename,)


def namespace_is_apphooked(namespace):
    # avoid circular import
    from .urls import DEFAULT_VIEW
    """
    Check if provided namespace has an app-hooked page.
    Returns True or False.
    """
    try:
        reverse('{0}:{1}'.format(namespace, DEFAULT_VIEW))
    except NoReverseMatch:
        return False
    return True
