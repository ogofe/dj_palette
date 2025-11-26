# from django.contrib import admin
from dj_palette.palette_admin.admin import palette_admin
from .models import (
    Page,
    Element,
    YoutubeSnippet
)
from dj_palette.palette_admin.admin import PaletteModelAdmin

class PageModelAdmin(PaletteModelAdmin):
    list_display = ('title', 'url', 'published' )
    list_display_links = ('title', )
    grid_display = ('title', 'url', 'published' )
    grid_display_links = ('title', )

# Register your models here.
palette_admin.register(Page, PageModelAdmin)
palette_admin.register(Element)
palette_admin.register(YoutubeSnippet)