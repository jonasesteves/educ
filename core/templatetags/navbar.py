from django import template
from core.models import Servico, Curso

register = template.Library()


@register.simple_tag
def consultoria_menu():
    try:
        Servico.objects.get(id=1, ativo=True)
        return True
    except Servico.DoesNotExist:
        return False


@register.simple_tag
def cursos_menu():
    try:
        Curso.objects.get(pk=1, ativo=True)
        return True
    except Curso.DoesNotExist:
        return False
