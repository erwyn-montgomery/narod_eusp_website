from django.shortcuts import render
from django.views import View
from django.db.models import Q, Prefetch
from narod.models import Page, Site, File, MainPageScreenshot
from django.core.paginator import Paginator
from itertools import chain


# Create your views here.
class SearchResults(View):
    page_model = Page.objects.all()
    site_model = Site.objects.all()
    file_model = File.objects.all()
    screens_model = MainPageScreenshot.objects.all()

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get("q", "")
        search_query = search_query.strip()
        search_type = request.GET.get("search_type", "text")
        search_page = request.GET.get("page", 1)
        entries_per_page = request.GET.get('entries', 20)

        if search_type == "url":
            search_result = self.search_url(search_query)
        else:
            search_result = self.search_text(search_query)

        search_result_paged = Paginator(search_result, entries_per_page)
        page_obj = search_result_paged.get_page(search_page)

        return render(request, 'search/search_results.html', {
            "query": search_query,
            "search_type": search_type,
            "results": search_result_paged,
            "page_obj": page_obj,
            "entries_per_page": entries_per_page
        })
    
    def search_text(self, q):
        search_result = self.page_model.filter(
            Q(page_text__icontains=q) | Q(page_title__icontains=q) 
        ).select_related("site").prefetch_related(
            Prefetch("site__screenshots", queryset=self.screens_model)
        )
        return search_result

    def search_url(self, q):
        site_result = self.site_model.filter(
            site_link__icontains=q
        ).prefetch_related(
            Prefetch("screenshots", queryset=self.screens_model),
            Prefetch("pages", queryset=self.page_model.order_by("page_id"))
        )

        page_result = self.page_model.filter(
            page_link__icontains=q
        ).select_related("site").prefetch_related(
            Prefetch("site__screenshots", queryset=self.screens_model)
        )

        file_result = self.file_model.filter(
            file_link__icontains=q
        )
        
        search_result = list(chain(site_result, page_result, file_result))
        return search_result
    