# Generated by Django 5.0.2 on 2024-05-14 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AuthGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, unique=True)),
            ],
            options={
                "db_table": "auth_group",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthGroupPermissions",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                "db_table": "auth_group_permissions",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("codename", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "auth_permission",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128)),
                ("last_login", models.DateTimeField(blank=True, null=True)),
                ("is_superuser", models.BooleanField()),
                ("username", models.CharField(max_length=150, unique=True)),
                ("first_name", models.CharField(max_length=150)),
                ("last_name", models.CharField(max_length=150)),
                ("email", models.CharField(max_length=254)),
                ("is_staff", models.BooleanField()),
                ("is_active", models.BooleanField()),
                ("date_joined", models.DateTimeField()),
            ],
            options={
                "db_table": "auth_user",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthUserGroups",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                "db_table": "auth_user_groups",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AuthUserUserPermissions",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                "db_table": "auth_user_user_permissions",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoAdminLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("action_time", models.DateTimeField()),
                ("object_id", models.TextField(blank=True, null=True)),
                ("object_repr", models.CharField(max_length=200)),
                ("action_flag", models.SmallIntegerField()),
                ("change_message", models.TextField()),
            ],
            options={
                "db_table": "django_admin_log",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoContentType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("app_label", models.CharField(max_length=100)),
                ("model", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "django_content_type",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoMigrations",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("app", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("applied", models.DateTimeField()),
            ],
            options={
                "db_table": "django_migrations",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DjangoSession",
            fields=[
                (
                    "session_key",
                    models.CharField(max_length=40, primary_key=True, serialize=False),
                ),
                ("session_data", models.TextField()),
                ("expire_date", models.DateTimeField()),
            ],
            options={
                "db_table": "django_session",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="ExecutionTimes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("function_name", models.TextField(blank=True, null=True)),
                ("execution_time", models.FloatField(blank=True, null=True)),
            ],
            options={
                "db_table": "execution_times",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="ExternalLink",
            fields=[
                (
                    "ext_link_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                ("ext_link_link", models.URLField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Внешняя ссылка",
                "verbose_name_plural": "Внешние ссылки",
                "db_table": "external_link",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="File",
            fields=[
                ("file_id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("file_extension", models.TextField(blank=True, null=True)),
                ("file_link", models.URLField(blank=True, null=True)),
                ("file_saved", models.BooleanField(default=False)),
                ("file_path", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Файл",
                "verbose_name_plural": "Файлы",
                "db_table": "file",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="FileMetaInfo",
            fields=[
                (
                    "file_meta_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                ("size", models.BigIntegerField(blank=True, null=True)),
                ("size_h", models.TextField(blank=True, null=True)),
                ("modification_date", models.TextField(blank=True, null=True)),
                ("html_code", models.TextField(blank=True, null=True)),
                ("title", models.TextField(blank=True, null=True)),
                ("author", models.TextField(blank=True, null=True)),
                ("page_count", models.BigIntegerField(blank=True, null=True)),
                ("text_layer", models.BooleanField(default=False)),
                ("text", models.TextField(blank=True, null=True)),
                ("char_count", models.BigIntegerField(blank=True, null=True)),
                ("word_count", models.BigIntegerField(blank=True, null=True)),
                ("rows", models.BigIntegerField(blank=True, null=True)),
                ("columns", models.BigIntegerField(blank=True, null=True)),
                ("slides_count", models.BigIntegerField(blank=True, null=True)),
                ("image_height", models.BigIntegerField(blank=True, null=True)),
                ("image_width", models.BigIntegerField(blank=True, null=True)),
                ("image_format", models.TextField(blank=True, null=True)),
                ("image_mode", models.TextField(blank=True, null=True)),
                ("exif", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Метаинформация файла",
                "verbose_name_plural": "Метаинформация файлов",
                "db_table": "file_meta_info",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="MainPageScreenshot",
            fields=[
                (
                    "screenshot_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                ("screenshot_path", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Скриншот",
                "verbose_name_plural": "Скриншоты",
                "db_table": "main_page_screenshot",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Page",
            fields=[
                ("page_id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("page_link", models.URLField(blank=True, null=True)),
                ("page_title", models.TextField(blank=True, null=True)),
                ("page_html", models.TextField(blank=True, null=True)),
                ("page_text", models.TextField(blank=True, null=True)),
                ("page_file_saved", models.BooleanField(default=False)),
                ("page_file", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Страница",
                "verbose_name_plural": "Страницы",
                "db_table": "page",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="PageScreenshot",
            fields=[
                (
                    "screenshot_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                ("screenshot_path", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "page_screenshot",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                ("site_id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("site_link", models.URLField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Сайт",
                "verbose_name_plural": "Сайты",
                "db_table": "site",
                "managed": False,
            },
        ),
    ]
