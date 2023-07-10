from django.urls import path
from .views import *


app_name = 'core'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('contato/', ContatoView.as_view(), name='contato'),
    path('quem-somos/', TemplateView.as_view(template_name='quem-somos.html'), name='quem-somos'),
    path('livros-recomendados/', LivrosView.as_view(), name='livros-recomendados'),
    path('curso/economia-para-investidores', CursoEPIView.as_view(), name='curso-epi'),
    path('curso/economia-para-investidores/contrato', ContratoEPIView.as_view(), name='curso-epi-contrato'),
]


