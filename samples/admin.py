from django.contrib import admin

from .models import Sample


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "genre", "bpm", "status", "uploaded_at")
    list_filter = ("genre", "status", "author")
    search_fields = ("title", "author__username")
    autocomplete_fields = ("author",)
