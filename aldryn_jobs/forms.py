# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, get_language

from hvad.forms import TranslatableModelForm
from unidecode import unidecode


class AutoSlugForm(TranslatableModelForm):

    slug_field = 'slug'
    slugified_field = None

    def clean(self):
        super(AutoSlugForm, self).clean()
        if not self.data.get(self.slug_field):
            slug = self.generate_slug()
            # add to self.data in order to show generated slug in the form in case of an error
            self.data[self.slug_field] = self.cleaned_data[self.slug_field] = slug
        else:
            slug = self.cleaned_data[self.slug_field]

        conflict = self.get_slug_conflict(slug=slug)
        if conflict:
            self.report_error(conflict=conflict)

        return self.cleaned_data

    def generate_slug(self):
        return slugify(unidecode(self.cleaned_data[self.slugified_field]))

    def get_slug_conflict(self, slug):
        translations_model = self.instance._meta.translations_model

        try:
            language_code = self.instance.language_code
        except translations_model.DoesNotExist:
            language_code = get_language()

        qs = translations_model.objects.filter(slug=slug, language_code=language_code)
        if self.instance.pk:
            qs = qs.exclude(master=self.instance)

        try:
            return qs.get()
        except translations_model.DoesNotExist:
            return None

    def report_error(self, conflict):
        address = '<a href="%(url)s">%(label)s</a>' % {
            'url': conflict.master.get_absolute_url(),
            'label': ugettext('the conflicting object')}
        error_message = ugettext('Conflicting slug. See %(address)s.') % {'address': address}
        self.append_to_errors(field='slug', message=mark_safe(error_message))

    def append_to_errors(self, field, message):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])


class JobCategoryForm(AutoSlugForm):

    slugified_field = 'name'

    class Meta:

        fields = ['name', 'slug']


class JobOfferForm(AutoSlugForm):

    slugified_field = 'title'

    class Meta:

        fields = ['title', 'slug', 'category', 'is_active', 'content', 'publication_start', 'publication_end']
