from django.shortcuts import render
from django.views import View
from django.db.models import Q, F, Prefetch, Value, FloatField, TextField
from narod.models import Page, Site, File, MainPageScreenshot, FileMetaInfo
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchHeadline, TrigramSimilarity
from django.db.models.functions import Coalesce
from django.core.cache import cache
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

        cache_key = f'queryset_{hash(f"search_query={search_query}_search_type={search_type}")}'
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
        ).order_by("-rank").distinct()
        return search_result

    def search_url(self, q):
        search_result = self.page_model.annotate(
            similarity=TrigramSimilarity("page_link", q)
        ).filter(
            similarity__gt=0.05
        ).order_by("-similarity").distinct()
        return search_result
    

class AdvancedSearchView(View):
    file_model = File.objects.all()
    file_meta_model = FileMetaInfo.objects.all()

    def get(self, request):
        file_extensions = self.file_model.values_list('file_extension', flat=True).distinct().order_by("file_extension")
        file_extensions = [fext for fext in file_extensions if fext]
        exif_makes = self.file_meta_model.values_list('exif_make', flat=True).distinct().order_by("exif_make")
        exif_makes = [make for make in exif_makes if make]
        exif_models = self.file_meta_model.values_list('exif_model', flat=True).distinct().order_by("exif_model")
        exif_models = [model for model in exif_models if model]
        return render(request, 'search/advanced_search.html', {
            "file_extensions": file_extensions,
            "exif_makes": exif_makes,
            "exif_models": exif_models
        })
    

class AdvancedSearchResultsView(View):
    site_model = Site.objects.all()
    page_model = Page.objects.all()
    file_model = File.objects.all()
    meta_model = FileMetaInfo.objects.all()
    screens_model = MainPageScreenshot.objects.all()

    def get(self, request, *args, **kwargs):
        site_link_query = request.GET.get("site_link", "").strip()
        page_title_query = request.GET.get("page_title", "").strip()
        page_text_query = request.GET.get("page_text", "").strip()
        file_link_query = request.GET.get("file_link", "").strip()
        file_extension_query = request.GET.get("file_extension", "")
        pages_more_than = request.GET.get("pages_more_than", "").strip()
        pages_less_than = request.GET.get("pages_less_than", "").strip()
        doc_text_query = request.GET.get("document_text", "").strip()
        image_height_more_than = request.GET.get("image_height_more_than", "").strip()
        image_height_less_than = request.GET.get("image_height_less_than", "").strip()
        image_width_more_than = request.GET.get("image_width_more_than", "").strip()
        image_width_less_than = request.GET.get("image_width_less_than", "").strip()
        device_make = request.GET.get("device_make", "").strip()
        device_model = request.GET.get("device_model", "").strip()
        date_from = request.GET.get("date_from", "").strip()
        date_to = request.GET.get("date_to", "").strip()
        search_type = request.GET.get("search_type")
        search_page = request.GET.get("page", 1)
        entries_per_page = request.GET.get("entries", 20)

        cache_key = f'queryset_{hash(f"{site_link_query}_{page_title_query}_{page_text_query}_{file_link_query}_{file_extension_query}_{search_type}_{pages_more_than}_{pages_less_than}_{doc_text_query}_{image_height_more_than}_{image_height_less_than}_{image_width_more_than}_{image_width_less_than}_device_make={device_make}_{device_model}_{str(date_from)}_{str(date_to)}")}'
        search_results = cache.get(cache_key)

        if not search_results:
            if search_type == "site":
                search_results = self.search_site(
                    site_link_query = site_link_query,
                    pages_more_than = pages_more_than,
                    pages_less_than = pages_less_than
                )
            elif search_type == "page":
                search_results = self.search_page(
                    page_title_query = page_title_query,
                    page_text_query = page_text_query
                )
            elif search_type == "file":
                search_results = self.search_file(
                    file_link_query = file_link_query,
                    file_extension_query = file_extension_query,
                    doc_text_query = doc_text_query,
                    image_height_more_than = image_height_more_than,
                    image_height_less_than = image_height_less_than,
                    image_width_more_than = image_width_more_than,
                    image_width_less_than = image_width_less_than,
                    device_make = device_make,
                    device_model = device_model,
                    date_from = date_from,
                    date_to = date_to
                )
            else:
                search_results = None
            cache.set(cache_key, search_results, timeout=60*10)  

        search_result_paged = Paginator(search_results, entries_per_page)
        page_obj = search_result_paged.get_page(search_page)

        file_extensions = self.file_model.values_list('file_extension', flat=True).distinct()
        file_extensions = [fext for fext in file_extensions if fext]
        exif_makes = self.meta_model.values_list('exif_make', flat=True).distinct().order_by("exif_make")
        exif_makes = [make for make in exif_makes if make]
        exif_models = self.meta_model.values_list('exif_model', flat=True).distinct().order_by("exif_model")
        exif_models = [model for model in exif_models if model]

        return render(request, 'search/advanced_search_results.html', {
            "page_obj": page_obj,
            "search_type": search_type,
            "file_extensions": file_extensions,
            "exif_makes": exif_makes,
            "exif_models": exif_models,
            "entries_per_page": entries_per_page,
            "site_link_query": site_link_query,
            "page_title_query": page_title_query,
            "page_text_query": page_text_query,
            "file_link_query": file_link_query,
            "file_extension_query": file_extension_query,
            "pages_more_than": pages_more_than,
            "pages_less_than": pages_less_than,
            "doc_text_query": doc_text_query,
            "image_height_more_than": image_height_more_than,
            "image_height_less_than": image_height_less_than,
            "image_width_more_than": image_width_more_than,
            "image_width_less_than": image_width_less_than,
            "device_make": device_make,
            "device_model": device_model,
            "date_from": date_from,
            "date_to": date_to
        })
    
    def search_site(self, *args, **kwargs):
        if kwargs.get("site_link_query"):
            site_link_filter = Q(site_link_similarity__gt=0.05)
        else:
            site_link_filter = Q()
        pages_filter = Q()        
        if kwargs.get("pages_more_than") or kwargs.get("pages_less_than"):
            more = kwargs.get("pages_more_than")
            less = kwargs.get("pages_less_than")
            if more:
                pages_filter &= Q(page_count__gte=int(more))
            if less:
                pages_filter &= Q(page_count__lte=int(less))
            if more and less and (more > less):
                pages_filter = Q()
        qs_annotated = self.site_model.annotate(
            site_link_similarity=TrigramSimilarity('site_link', kwargs.get("site_link_query", '')),
        )
        qs_filtered = qs_annotated.filter(
            site_link_filter &
            pages_filter
        ).distinct().order_by("-site_link_similarity")
        return qs_filtered

    def search_page(self, *args, **kwargs):
        fts_title_results = self.page_model.none()
        fts_text_results = self.page_model.none() 
        if kwargs.get("page_title_query"):
            fts_title_query = SearchQuery(kwargs["page_title_query"], config="russian")
            fts_title_results = self.page_model.annotate(
                rank=SearchRank(F("page_fts_title"), fts_title_query)
            ).filter(
                page_fts_title=fts_title_query,
                rank__gt=0.05
            ).order_by("-rank").distinct()
        if kwargs.get("page_text_query"):
            fts_text_query = SearchQuery(kwargs["page_text_query"], config="russian")
            fts_text_results = self.page_model.annotate(
                rank=SearchRank(F("page_fts_text"), fts_text_query),
                headline=SearchHeadline("page_text", fts_text_query, config="russian")
            ).filter(
                page_fts_text=fts_text_query,
                rank__gt=0.05
            ).order_by("-rank").distinct()
        combined_results = sorted(
            chain(fts_title_results, fts_text_results),
            key=lambda instance: instance.rank,
            reverse=True
        )
        return combined_results

    def search_file(self, *args, **kwargs):
        fts_query = None    
        if kwargs.get("doc_text_query"):
            fts_query = SearchQuery(kwargs["doc_text_query"], config="russian")
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
        img_h_filter = Q()
        if kwargs.get("image_height_more_than") or kwargs.get("image_height_less_than"):
            more = kwargs.get("image_height_more_than")
            less = kwargs.get("image_height_less_than")
            if more:
                img_h_filter &= Q(files__image_height__gte=int(more))
            if less:
                img_h_filter &= Q(files__image_height__lte=int(less))
            if more and less and (more > less):
                img_h_filter = Q()
        img_w_filter = Q()
        if kwargs.get("image_width_more_than") or kwargs.get("image_width_less_than"):
            more = kwargs.get("image_width_more_than")
            less = kwargs.get("image_width_less_than")
            if more:
                img_w_filter &= Q(files__image_width__gte=int(more))
            if less:
                img_w_filter &= Q(files__image_width__lte=int(less))
            if more and less and (more > less):
                img_w_filter = Q()
        if kwargs.get("device_make"):
            make_filter = Q(files__exif_make__exact=kwargs["device_make"])
        else:
            make_filter = Q()
        if kwargs.get("device_model"):
            model_filter = Q(files__exif_model__exact=kwargs["device_model"])
        else:
            model_filter = Q()
        date_filter = Q()
        if kwargs.get("date_from") or kwargs.get("date_to"):
            more = kwargs.get("date_from")
            less = kwargs.get("date_to")
            if more:
                date_filter &= Q(files__exif_datetime__gte=more)
            if less:
                date_filter &= Q(files__exif_datetime__lte=less)
            if more and less and (more > less):
                date_filter = Q()
        qs = self.file_model.prefetch_related(
            Prefetch("files", queryset=self.meta_model)
        )
        qs_annotated = qs.annotate(
            file_link_similarity=TrigramSimilarity('file_link', kwargs.get("file_link_query", '')),
            search_rank=Coalesce(SearchRank(F('files__file_fts_text'), fts_query), Value(0.0), output_field=FloatField()),
            search_headline=Coalesce(SearchHeadline('files__text', fts_query, config="russian"), Value(''), output_field=TextField())
        )
        qs_filtered = qs_annotated.filter(
            page_text_filter &
            file_link_filter &
            file_extension_filter &
            img_h_filter &
            img_w_filter &
            make_filter &
            model_filter &
            date_filter
        ).distinct().order_by(
            "-file_link_similarity", "-search_rank"
        ) 
        return qs_filtered
    