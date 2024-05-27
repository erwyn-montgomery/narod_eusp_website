# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
import re


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class ExecutionTimes(models.Model):
    function_name = models.TextField(blank=True, null=True)
    execution_time = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'execution_times'


class ExternalLink(models.Model):
    ext_link_id = models.BigIntegerField(primary_key=True)
    page = models.ForeignKey('Page', on_delete=models.CASCADE, related_name="ext_links")
    ext_link_link = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Внешняя ссылка"
        verbose_name_plural = "Внешние ссылки"
        managed = False
        db_table = 'external_link'


class File(models.Model):
    file_id = models.BigIntegerField(primary_key=True)
    page = models.ForeignKey('Page', on_delete=models.CASCADE, related_name="files_on_page")
    file_extension = models.CharField(max_length=5, blank=True, null=True)
    file_link = models.URLField(blank=True, null=True)
    file_saved = models.BooleanField(default=False)
    file_path = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        managed = False
        db_table = 'file'


class FileMetaInfo(models.Model):
    file_meta_id = models.BigIntegerField(primary_key=True)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="files")
    size = models.BigIntegerField(blank=True, null=True)
    size_h = models.CharField(max_length=100, blank=True, null=True)
    modification_date = models.DateField(blank=True, null=True)
    html_code = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    page_count = models.BigIntegerField(blank=True, null=True)
    text_layer = models.BooleanField(default=False)
    text = models.TextField(blank=True, null=True)
    char_count = models.BigIntegerField(blank=True, null=True)
    word_count = models.BigIntegerField(blank=True, null=True)
    rows = models.BigIntegerField(blank=True, null=True)
    columns = models.BigIntegerField(blank=True, null=True)
    slides_count = models.IntegerField(blank=True, null=True)
    image_height = models.IntegerField(blank=True, null=True)
    image_width = models.IntegerField(blank=True, null=True)
    image_format = models.CharField(max_length=100, blank=True, null=True)
    image_mode = models.CharField(max_length=100, blank=True, null=True)
    exif = models.TextField(blank=True, null=True)
    exif_make = models.TextField(blank=True, null=True)
    exif_model = models.TextField(blank=True, null=True)
    exif_software = models.TextField(blank=True, null=True)
    exif_orientation = models.SmallIntegerField(blank=True, null=True)
    exif_datetime = models.DateField(blank=True, null=True)
    exif_artist = models.TextField(blank=True, null=True)
    exif_copyright = models.TextField(blank=True, null=True)
    exif_hostcomputer = models.TextField(blank=True, null=True)
    file_fts_text = SearchVectorField(blank=True, null=True)
    file_fts_title = SearchVectorField(blank=True, null=True)

    class Meta:
        verbose_name = "Метаинформация файла"
        verbose_name_plural = "Метаинформация файлов"
        managed = False
        db_table = 'file_meta_info'


class MainPageScreenshot(models.Model):
    screenshot_id = models.BigIntegerField(primary_key=True)
    site = models.ForeignKey('Site', on_delete=models.CASCADE, related_name="screenshots")
    screenshot_path = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Скриншот"
        verbose_name_plural = "Скриншоты"
        managed = False
        db_table = 'main_page_screenshot'


class Page(models.Model):
    page_id = models.BigIntegerField(primary_key=True)
    site = models.ForeignKey('Site', on_delete=models.CASCADE, related_name="pages")
    page_link = models.URLField(blank=True, null=True)
    page_parent = models.ForeignKey('self', on_delete=models.CASCADE, db_column='page_parent')
    page_title = models.TextField(blank=True, null=True)
    page_html = models.TextField(blank=True, null=True)
    page_text = models.TextField(blank=True, null=True)
    page_file_saved = models.BooleanField(default=False)
    page_file = models.TextField(blank=True, null=True)
    page_fts_text = SearchVectorField(null=True)
    page_fts_title = SearchVectorField(null=True)

    def save(self, *args, **kwargs):
        self.page_fts_text = SearchVector('page_text')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        managed = False
        db_table = 'page'
        indexes = [
            models.Index(fields=['page_fts_text'], name='page_fts_text_idx')
        ]


class PageScreenshot(models.Model):
    screenshot_id = models.BigIntegerField(primary_key=True)
    page = models.ForeignKey('Page', on_delete=models.CASCADE)
    screenshot_path = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'page_screenshot'


class Site(models.Model):
    site_id = models.BigIntegerField(primary_key=True)
    site_link = models.URLField(blank=True, null=True)
    page_count = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Сайт"
        verbose_name_plural = "Сайты"
        managed = False
        db_table = 'site'

    def site_name(self):
        if self.site_link:
            match = re.search(r"http://(.*?)\.narod\.ru", self.site_link)
            if match:
                return match.group(1)
        return ""
