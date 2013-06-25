# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify

from hvad.forms import TranslatableModelForm
from unidecode import unidecode


class JobOfferForm(TranslatableModelForm):

    class Meta:

        fields = ['title', 'slug', 'category', 'is_active', 'content', 'publication_start', 'publication_end']

    def clean(self):
        super(JobOfferForm, self).clean()
        if not self.data.get('slug'):
            slug = slugify(unidecode(self.cleaned_data['title']))
            # show in form in case of error
            self.data['slug'] = slug
            # it is already clean
            self.cleaned_data['slug'] = slug
        return self.cleaned_data
