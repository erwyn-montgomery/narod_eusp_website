from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.views import View
from django.db.models import Q, Prefetch
from narod.models import Page, Site, File, MainPageScreenshot
from django.core.paginator import Paginator
import string
from django.core.cache import cache


# Create your views here.
class CatalogueView(View):
    alphabet = list(string.ascii_uppercase) + [str(digit) for digit in range(10)]
    
    def get(self, request):
        return render(request, "catalogue/alphabet.html", {"alphabet": self.alphabet})


class LetterView(View):
    site_model = Site.objects.all()
    page_model = Page.objects.all()
    screens_model = MainPageScreenshot.objects.all()

    def get(self, request, *args, **kwargs):
        letter = kwargs["letter"]
        cache_key = f"catalogue_letter={letter}"
        sites = cache.get(cache_key)
        if not sites:
            sites = get_list_or_404(self.site_model.filter(
                site_link__icontains=f'http://{letter.lower()}'
            ).order_by("site_link").prefetch_related(
                Prefetch("pages", queryset=self.page_model.order_by("page_id")),
                Prefetch("screenshots", queryset=self.screens_model)
            ))
            cache.set(cache_key, sites, timeout=60*10)
        sites_page = request.GET.get("page", 1)
        entries_per_page = request.GET.get('entries', 25)
        paginator = Paginator(sites, entries_per_page)
        page_obj = paginator.get_page(sites_page)
        return render(request, 'catalogue/letter.html', {
            "page_obj": page_obj,
            "letter": letter,
            "entries_per_page": entries_per_page
        })


class SiteView(View):
    site_model = Site.objects.all()
    page_model = Page.objects.all()
    screens_model = MainPageScreenshot.objects.all()

    def get(self, request, *args, **kwargs):
        site_id = kwargs["id"]
        cache_key = f"catalogue_site_pages={site_id}"
        cache_result = cache.get(cache_key)
        if not cache_result:
            pages = get_list_or_404(self.page_model.filter(
                site_id__exact=site_id
            ).order_by("page_id"))
            site_link = get_object_or_404(self.site_model, site_id=site_id).site_link
            cache.set(cache_key, (pages, site_link), timeout=60*10)
        else:
            pages = cache_result[0]
            site_link = cache_result[1]
        sites_page = request.GET.get("page", 1)
        entries_per_page = request.GET.get('entries', 25)
        paginator = Paginator(pages, entries_per_page)
        page_obj = paginator.get_page(sites_page)
        return render(request, 'catalogue/site.html', {
            "page_obj": page_obj,
            "site_id": site_id,
            "site_link": site_link,
            "entries_per_page": entries_per_page
        })
