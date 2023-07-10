from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.views.generic import ListView, TemplateView
from django.template.defaultfilters import register
from blog.models import Artigo, CategoriaArtigo
from core.models import Curso


class BlogView(ListView):
    template_name = 'blog/blog.html'
    model = Artigo
    paginate_by = 6
    queryset = Artigo.objects.order_by('-criado').filter(publicado=True)

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data()
        context['cursos'] = Curso.objects.filter(ativo=True)
        context['total'] = Artigo.objects.filter(publicado=True).count()
        context['ultimos'] = Artigo.objects.order_by('-criado').filter(publicado=True)[:6]
        context['categorias'] = CategoriaArtigo.objects.all()
        return context

    @register.filter
    def preview(self):
        return strip_tags(self)[:150] + '...'

    @register.filter
    def quantidade(self, categoria):
        return categoria.artigo_set.filter(publicado=True).count()


class ArtigoView(TemplateView):
    template_name = 'blog/blog-single.html'

    def get_context_data(self, **kwargs):
        context = super(ArtigoView, self).get_context_data()
        context['artigo'] = get_object_or_404(Artigo, slug=kwargs['slug'])
        context['cursos'] = Curso.objects.filter(ativo=True)
        context['total'] = Artigo.objects.filter(publicado=True).count()
        context['ultimos'] = Artigo.objects.order_by('-criado').filter(publicado=True)[:6]
        context['categorias'] = CategoriaArtigo.objects.all()
        return context


class BlogCategoriaView(ListView):
    template_name = 'blog/blog-categoria.html'
    model = Artigo
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(BlogCategoriaView, self).get_context_data()
        context['categoria'] = get_object_or_404(CategoriaArtigo, slug=self.kwargs['slug'])
        context['cursos'] = Curso.objects.filter(ativo=True)
        context['total'] = Artigo.objects.filter(publicado=True).count()
        context['ultimos'] = Artigo.objects.order_by('-criado').filter(publicado=True)[:6]
        context['categorias'] = CategoriaArtigo.objects.all()
        return context

    def get_queryset(self, **kwargs):
        categoria = get_object_or_404(CategoriaArtigo, slug=self.kwargs['slug'])
        return Artigo.objects.order_by('-criado').filter(categoria=categoria, publicado=True)


class SearchView(ListView):
    model = Artigo
    template_name = 'blog/search.html'
    paginate_by = 99999

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data()
        context['cursos'] = Curso.objects.filter(ativo=True)
        context['total'] = Artigo.objects.filter(publicado=True).count()
        context['ultimos'] = Artigo.objects.order_by('-criado').filter(publicado=True)[:6]
        context['categorias'] = CategoriaArtigo.objects.all()
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        artigos = Artigo.objects.order_by('-criado').filter(
            Q(titulo__startswith=query) |
            Q(titulo__icontains=query) |
            Q(titulo__endswith=query)
        )
        return artigos
