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
    

class AdvancedSearchView(View):
    file_model = File.objects.all()

    def get(self, request):
        file_extensions = self.file_model.values_list('file_extension', flat=True).distinct()
        return render(request, 'search/advanced_search.html', {
            "file_extensions": file_extensions
        })
    

class AdvancedSearchResultsView(View):
    site_model = Site.objects.all()
    page_model = Page.objects.all()
    file_model = File.objects.all()
    screens_model = MainPageScreenshot.objects.all()

    def get(self, request, *args, **kwargs):
        site_link_query = request.GET.get('site_link', '').strip()
        page_link_query = request.GET.get('page_link', '').strip()
        page_title_query = request.GET.get('page_title', '').strip()
        page_text_query = request.GET.get('page_text', '').strip()
        file_link_query = request.GET.get('file_link', '').strip()
        file_extension_query = request.GET.get('file_extension', '')
        search_types = request.GET.getlist('search_type')
        search_page = request.GET.get("page", 1)
        entries_per_page = request.GET.get('entries', 20)

        site_results = self.site_model.none()
        page_results = self.page_model.none()
        file_results = self.file_model.none()

        if 'site' in search_types:
            site_results = self.search_site(
                site_link_query = site_link_query,
                page_link_query = page_link_query,
                page_title_query = page_title_query,
                page_text_query = page_text_query,
                file_link_query = file_link_query,
                file_extension_query = file_extension_query
            )

        if 'page' in search_types:
            page_results = self.search_page(
                site_link_query = site_link_query,
                page_link_query = page_link_query,
                page_title_query = page_title_query,
                page_text_query = page_text_query,
                file_link_query = file_link_query,
                file_extension_query = file_extension_query
            )

        if 'file' in search_types:
            file_results = self.search_file(
                site_link_query = site_link_query,
                page_link_query = page_link_query,
                page_title_query = page_title_query,
                page_text_query = page_text_query,
                file_link_query = file_link_query,
                file_extension_query = file_extension_query
            )

        print("Site results count:", site_results.count())
        print("Page results count:", page_results.count())
        print("File results count:", file_results.count())

        search_results = list(chain(site_results, page_results, file_results))

        search_result_paged = Paginator(search_results, entries_per_page)
        page_obj = search_result_paged.get_page(search_page)

        file_extensions = self.file_model.values_list('file_extension', flat=True).distinct()

        return render(request, 'search/advanced_search_results.html', {
            "page_obj": page_obj,
            "file_extensions": file_extensions,
            "entries_per_page": entries_per_page,
            "site_link_query": site_link_query,
            "page_link_query": page_link_query,
            "page_title_query": page_title_query,
            "page_text_query": page_text_query,
            "file_link_query": file_link_query,
            "file_extension_query": file_extension_query,
            "search_types": search_types
        })
    
    def search_site(self, *args, **kwargs):
        if kwargs["file_extension_query"]:
            q_query = Q(pages__files_on_page__file_extension__iexact=kwargs["file_extension_query"])
        else:
            q_query = Q()
        results = self.site_model.prefetch_related(
            Prefetch("screenshots", queryset=self.screens_model),
            Prefetch("pages", queryset=self.page_model.prefetch_related(
                Prefetch("files_on_page", queryset=self.file_model)
            ))
        ).filter(
            Q(site_link__icontains=kwargs["site_link_query"]) &
            Q(pages__page_link__icontains=kwargs["page_link_query"]) &
            Q(pages__page_title__icontains=kwargs["page_title_query"]) &
            Q(pages__page_text__icontains=kwargs["page_text_query"]) &
            Q(pages__files_on_page__file_link__icontains=kwargs["file_link_query"]) &
            q_query
        )
        return results

    def search_page(self, *args, **kwargs):
        if kwargs["file_extension_query"]:
            q_query = Q(files_on_page__file_extension__iexact=kwargs["file_extension_query"])
        else:
            q_query = Q()
        results = self.page_model.select_related("site").prefetch_related(
                Prefetch("files_on_page", queryset=self.file_model),
                Prefetch("site__screenshots", queryset=self.screens_model)
        ).filter(
            Q(site__site_link__icontains=kwargs["site_link_query"]) &
            Q(page_link__icontains=kwargs["page_link_query"]) &
            Q(page_title__icontains=kwargs["page_title_query"]) &
            Q(page_text__icontains=kwargs["page_text_query"]) &
            Q(files_on_page__file_link__icontains=kwargs["file_link_query"]) &
            q_query
        )
        return results

    def search_file(self, *args, **kwargs):
        if kwargs["file_extension_query"]:
            q_query = Q(file_extension__iexact=kwargs["file_extension_query"])
        else:
            q_query = Q()
        results = self.file_model.select_related("page").select_related("page__site").filter(
            Q(page__site__site_link__icontains=kwargs["site_link_query"]) &
            Q(page__page_link__icontains=kwargs["page_link_query"]) &
            Q(page__page_title__icontains=kwargs["page_title_query"]) &
            Q(page__page_text__icontains=kwargs["page_text_query"]) &
            Q(file_link__icontains=kwargs["file_link_query"]) &
            Q()
        )
        return results
