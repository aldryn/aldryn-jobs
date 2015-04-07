# -*- coding: utf-8 -*-
from aldryn_categories.models import Category
from django.contrib.sitemaps import Sitemap
from ..models import JobOffer


class JobOfferCategoriesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Category.objects.all()


class JobOfferSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return JobOffer.objects.active()

    def lastmod(self, obj):
        return obj.publication_start
