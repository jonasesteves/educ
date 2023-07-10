from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView

from blog.models import Artigo
from .forms import ContatoForm
from .models import Curso, Depoimento, CategoriaLivro


# Template home
class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['cursos'] = Curso.objects.filter(ativo=True)
        context['depoimentos'] = Depoimento.objects.order_by('?').all()
        context['artigos'] = Artigo.objects.order_by('-criado').filter(publicado=True)[:9]
        return context


class CursoEPIView(TemplateView):
    template_name = 'cursos/curso-epi.html'
    model = Curso

    def get_context_data(self, **kwargs):
        context = super(CursoEPIView, self).get_context_data(**kwargs)
        try:
            context['curso'] = Curso.objects.get(pk=1, ativo=True)
        except Curso.DoesNotExist:
            raise Http404()
        context['valor_com_desconto'] = context['curso'].valor - context['curso'].desconto
        return context


class ContratoEPIView(TemplateView):
    template_name = 'cursos/termos-epi.html'


# Template Livros
class LivrosView(ListView):
    template_name = 'livros.html'
    model = CategoriaLivro

    paginate_by = 1000
    ordering = 'id'


# Template contato
class ContatoView(FormView):
    template_name = 'contact.html'
    form_class = ContatoForm
    success_url = reverse_lazy('core:contato')

    def form_valid(self, form):
        form.envia_email()
        messages.success(self.request, 'Sua mensagem foi enviada com sucesso.')
        return super(ContatoView, self).form_valid(form)

    def form_invalid(self, form):
        mensagem = 'Desculpe. Ocorreu um erro ao tentar enviar a mensagem. Verifique os dados preenchidos.'
        messages.error(self.request, mensagem, extra_tags='danger')
        return super(ContatoView, self).form_invalid(form)


# Template página de cursos
class CursosView(ListView):
    template_name = 'cursos/cursos.html'
    model = Curso
    paginate_by = 3
    ordering = '-id'


# Template página de um único curso
class CursoView(TemplateView):
    template_name = 'cursos/curso.html'

    def get_context_data(self, **kwargs):
        context = super(CursoView, self).get_context_data(**kwargs)
        context['curso'] = get_object_or_404(Curso, id=kwargs['id'])
        return context
