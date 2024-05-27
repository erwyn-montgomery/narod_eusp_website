from django.shortcuts import render
from django.views import View
from django.db.models import Q, F, Prefetch, Value, FloatField, TextField
from narod.models import Page, Site, File, MainPageScreenshot
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchHeadline, TrigramSimilarity
from django.db.models.functions import Coalesce
from django.core.cache import cache


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

        cache_key = f'queryset_{(hash(f"search_query={search_query}_search_type={search_type}"))}'
        search_result = cache.get(cache_key)
        
        if not search_result:
            if search_type == "url":
                search_result = self.search_url(search_query)
            else:
                search_result = self.search_text(search_query)
            cache.set(cache_key, search_result, timeout=60*10)

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
        search_fts_query = SearchQuery(q, config="russian")
        search_rank = SearchRank(F("page_fts_text"), search_fts_query)
        search_headline = SearchHeadline("page_text", search_fts_query, config="russian")
        search_result = self.page_model.annotate(
            rank=search_rank,
            headline=search_headline 
        ).filter(
            page_fts_text=search_fts_query,
            rank__gt=0.05
        ).order_by("-rank").select_related("site").prefetch_related(
            Prefetch("site__screenshots", queryset=self.screens_model)
        ).distinct()
        return search_result

    def search_url(self, q):
        search_result = self.page_model.annotate(
            similarity=TrigramSimilarity("page_link", q)
        ).filter(
            similarity__gt=0.05
        ).order_by("-similarity").select_related("site").prefetch_related(
            Prefetch("site__screenshots", queryset=self.screens_model)
        ).distinct()
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
        page_text_query = request.GET.get('page_text', '').strip()
        file_link_query = request.GET.get('file_link', '').strip()
        file_extension_query = request.GET.get('file_extension', '')
        search_type = request.GET.get('search_type')
        search_page = request.GET.get("page", 1)
        entries_per_page = request.GET.get('entries', 20)

        cache_key = f'queryset_{hash(f"slquery={site_link_query}_ptquery={page_text_query}_flquery={file_link_query}_fequery={file_extension_query}_stype={search_type}")}'
        search_results = cache.get(cache_key)

        if not search_results:
            if search_type == "site":
                search_results = self.search_site(
                    site_link_query = site_link_query,
                    page_text_query = page_text_query,
                    file_link_query = file_link_query,
                    file_extension_query = file_extension_query
                )
            elif search_type == "page":
                search_results = self.search_page(
                    site_link_query = site_link_query,
                    page_text_query = page_text_query,
                    file_link_query = file_link_query,
                    file_extension_query = file_extension_query
                )
            elif search_type == "file":
                search_results = self.search_file(
                    site_link_query = site_link_query,
                    page_text_query = page_text_query,
                    file_link_query = file_link_query,
                    file_extension_query = file_extension_query
                )
            else:
                search_results = None
            cache.set(cache_key, search_results, timeout=60*10)  

        search_result_paged = Paginator(search_results, entries_per_page)
        page_obj = search_result_paged.get_page(search_page)

        file_extensions = self.file_model.values_list('file_extension', flat=True).distinct()

        return render(request, 'search/advanced_search_results.html', {
            "page_obj": page_obj,
            "file_extensions": file_extensions,
            "entries_per_page": entries_per_page,
            "site_link_query": site_link_query,
            "page_text_query": page_text_query,
            "file_link_query": file_link_query,
            "file_extension_query": file_extension_query,
            "search_type": search_type
        })
    
    def search_site(self, *args, **kwargs):
        fts_query = None
        if kwargs.get("site_link_query"):
            site_link_filter = Q(site_link_similarity__gt=0.05)
        else:
            site_link_filter = Q()        
        if kwargs.get("page_text_query"):
            fts_query = SearchQuery(kwargs["page_text_query"], config="russian")
            page_text_filter = Q(search_rank__gt=0.05)
        else:
            page_text_filter = Q()
        if kwargs.get("file_link_query"):
            file_link_filter = Q(file_link_similarity__gt=0.05)
        else:
            file_link_filter = Q()
        if kwargs.get("file_extension_query"):
            file_extension_filter = Q(pages__files_on_page__file_extension__exact=kwargs["file_extension_query"])
        else:
            file_extension_filter = Q()
        qs = self.site_model.prefetch_related(
            Prefetch("screenshots", queryset=self.screens_model),
            Prefetch("pages", queryset=self.page_model.prefetch_related(
                Prefetch("files_on_page", queryset=self.file_model)
            ))
        )
        qs_annotated = qs.annotate(
            site_link_similarity=TrigramSimilarity('site_link', kwargs.get("site_link_query", '')),
            file_link_similarity=TrigramSimilarity('pages__files_on_page__file_link', kwargs.get("file_link_query", '')),
            search_rank=Coalesce(SearchRank(F('pages__page_fts_text'), fts_query), Value(0.0), output_field=FloatField()),
            search_headline=Coalesce(SearchHeadline('pages__page_text', fts_query, config="russian"), Value(''), output_field=TextField())
        )
        qs_filtered = qs_annotated.filter(
            site_link_filter &
            page_text_filter &
            file_link_filter &
            file_extension_filter
        ).distinct().order_by(
            "-site_link_similarity", "-search_rank", "-file_link_similarity"
        )
        qs_final_set = set()
        qs_final = []
        for qs_obj in qs_filtered:
            site_pk = qs_obj.site_id
            if site_pk not in qs_final_set:
                qs_final.append(qs_obj)
                qs_final_set.add(site_pk)
        return qs_final

    def search_page(self, *args, **kwargs):
        fts_query = None
        if kwargs.get("site_link_query"):
            site_link_filter = Q(site_link_similarity__gt=0.05)
        else:
            site_link_filter = Q()        
        if kwargs.get("page_text_query"):
            fts_query = SearchQuery(kwargs["page_text_query"], config="russian")
            page_text_filter = Q(search_rank__gt=0.05)
        else:
            page_text_filter = Q()
        if kwargs.get("file_link_query"):
            file_link_filter = Q(file_link_similarity__gt=0.05)
        else:
            file_link_filter = Q()
        if kwargs.get("file_extension_query"):
            file_extension_filter = Q(files_on_page__file_extension__exact=kwargs["file_extension_query"])
        else:
            file_extension_filter = Q()
        qs = self.page_model.select_related("site").prefetch_related(
                Prefetch("files_on_page", queryset=self.file_model),
                Prefetch("site__screenshots", queryset=self.screens_model)
        )
        qs_annotated = qs.annotate(
            site_link_similarity=TrigramSimilarity('site__site_link', kwargs.get("site_link_query", '')),
            file_link_similarity=TrigramSimilarity('files_on_page__file_link', kwargs.get("file_link_query", '')),
            search_rank=Coalesce(SearchRank(F('page_fts_text'), fts_query), Value(0.0), output_field=FloatField()),
            search_headline=Coalesce(SearchHeadline('page_text', fts_query, config="russian"), Value(''), output_field=TextField())
        )
        qs_filtered = qs_annotated.filter(
            site_link_filter &
            page_text_filter &
            file_link_filter &
            file_extension_filter
        ).distinct().order_by(
            "-search_rank", "-site_link_similarity", "-file_link_similarity"
        )
        return qs_filtered

    def search_file(self, *args, **kwargs):
        fts_query = None
        if kwargs.get("site_link_query"):
            site_link_filter = Q(site_link_similarity__gt=0.05)
        else:
            site_link_filter = Q()        
        if kwargs.get("page_text_query"):
            fts_query = SearchQuery(kwargs["page_text_query"], config="russian")
            page_text_filter = Q(search_rank__gt=0.05)
        else:
            page_text_filter = Q()
        if kwargs.get("file_link_query"):
            file_link_filter = Q(file_link_similarity__gt=0.05)
        else:
            file_link_filter = Q()
        if kwargs.get("file_extension_query"):
            file_extension_filter = Q(file_extension__exact=kwargs["file_extension_query"])
        else:
            file_extension_filter = Q()
        qs = self.file_model.select_related("page").select_related("page__site")
        qs_annotated = qs.annotate(
            site_link_similarity=TrigramSimilarity('page__site__site_link', kwargs.get("site_link_query", '')),
            file_link_similarity=TrigramSimilarity('file_link', kwargs.get("file_link_query", '')),
            search_rank=Coalesce(SearchRank(F('page__page_fts_text'), fts_query), Value(0.0), output_field=FloatField()),
            search_headline=Coalesce(SearchHeadline('page__page_text', fts_query, config="russian"), Value(''), output_field=TextField())
        )
        qs_filtered = qs_annotated.filter(
            site_link_filter &
            page_text_filter &
            file_link_filter &
            file_extension_filter
        ).distinct().order_by(
            "-file_link_similarity", "-search_rank", "-site_link_similarity"
        ) 
        return qs_filtered
    