# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify

from hvad.forms import TranslatableModelForm
from unidecode import unidecode


class AutoSlugForm(TranslatableModelForm):

    slugified_field = None

    def clean(self):
        super(AutoSlugForm, self).clean()
        if not self.data.get('slug'):
            slug = slugify(unidecode(self.cleaned_data[self.slugified_field]))
            # show in form in case of error
            self.data['slug'] = slug
            # it is already clean
            self.cleaned_data['slug'] = slug
        return self.cleaned_data


class JobCategoryForm(AutoSlugForm):

    slugified_field = 'name'

    class Meta:

        fields = ['name', 'slug']


class JobOfferForm(AutoSlugForm):

    slugified_field = 'title'

    class Meta:

        fields = ['title', 'slug', 'category', 'is_active', 'content', 'publication_start', 'publication_end']
