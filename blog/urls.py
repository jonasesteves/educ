from django.urls import path
from blog.views import BlogView, ArtigoView, BlogCategoriaView, SearchView

app_name = 'blog'

urlpatterns = [
    path('blog/', BlogView.as_view(), name='blog'),
    path('blog/artigo/<slug:slug>', ArtigoView.as_view(), name='artigo'),
    # path('blog/categorias/', BlogCategoriasView.as_view(), name='blog-categorias'),
    path('blog/categorias/<slug:slug>', BlogCategoriaView.as_view(), name='blog-categoria'),
    path('blog/search', SearchView.as_view(), name='search'),
]
