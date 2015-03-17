# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap

from ..models import JobCategory, JobOffer


class JobOfferCategoriesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return JobCategory.objects.all()


class JobOfferSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return JobOffer.objects.active()

    def lastmod(self, obj):
        return obj.publication_start
