from django.contrib import admin
from .models import Site, Page, File, FileMetaInfo, MainPageScreenshot, ExternalLink

# Register your models here.


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('site_link',)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('page_title', 'site', 'page_parent')
    list_filter = ('site',)
    search_fields = ('page_title', 'page_link')

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('file_link', 'page', 'file_extension')
    search_fields = ('file_link', 'file_extension')

@admin.register(FileMetaInfo)
class FileMetaInfoAdmin(admin.ModelAdmin):
    list_display = ('file',)
    search_fields = ('file',)

@admin.register(MainPageScreenshot)
class MainPageScreenshotAdmin(admin.ModelAdmin):
    list_display = ('screenshot_path', 'site')
    search_fields = ('screenshot_path',)

@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ('ext_link_link', 'page')
    search_fields = ('ext_link_link',)
