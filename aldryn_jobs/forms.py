# -*- coding: utf-8 -*-
from hvad.forms import TranslatableModelForm


class JobOfferForm(TranslatableModelForm):

    class Meta:

        fields = ['title', 'slug', 'category', 'is_active', 'content', 'publication_start', 'publication_end']
