from os.path import splitext

from django.utils.text import get_valid_filename as get_valid_filename_django
from django.template.defaultfilters import slugify


def get_valid_filename(s):
    """
    like the regular get_valid_filename, but also slugifies away
    umlauts and stuff.
    Copied from django-filer
    """
    s = get_valid_filename_django(s)
    filename, ext = splitext(s)
    filename = slugify(filename)
    ext = slugify(ext)
    if ext:
        return u"%s.%s" % (filename, ext)
    else:
        return u"%s" % (filename,)
