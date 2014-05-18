# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext

from aldryn_search.utils import get_index_base, strip_tags

from aldryn_jobs.models import JobOffer


class JobOffersIndex(get_index_base()):
    haystack_use_for_indexing = getattr(settings, "ALDRYN_JOBS_SEARCH", True)

    INDEX_TITLE = True

    def prepare_pub_date(self, obj):
        return obj.publication_start

    def get_title(self, obj):
        return obj.title

    def get_index_kwargs(self, language):
        return {'translations__language_code': language}

    def get_index_queryset(self, language):
        return self.get_model().active.all()

    def get_model(self):
        return JobOffer

    def get_search_data(self, obj, language, request):
        text_bits = [strip_tags(obj.lead_in)]
        plugins = obj.content.cmsplugin_set.filter(language=language)
        for base_plugin in plugins:
            instance, plugin_type = base_plugin.get_plugin_instance()
            if not instance is None:
                plugin_content = strip_tags(instance.render_plugin(context=RequestContext(request)))
                text_bits.append(plugin_content)

        return ' '.join(text_bits)
