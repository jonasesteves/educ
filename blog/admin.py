from django.contrib import admin

from blog.models import CategoriaArtigo, Artigo, Imagem


@admin.register(CategoriaArtigo)
class CategoriaArtigoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Artigo)
class ArtigoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria')
    prepopulated_fields = {'slug': ('titulo',)}


@admin.register(Imagem)
class ImagemAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'url',)
