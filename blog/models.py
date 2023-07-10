from django.contrib.auth import get_user_model
from django.db import models
from django.utils.safestring import mark_safe
from stdimage import StdImageField
from tinymce.models import HTMLField

from core.models import get_file_path
from mundstock import settings


class CategoriaArtigo(models.Model):
    nome = models.CharField('Nome da categoria', max_length=50)
    slug = models.SlugField(null=True, unique=True, help_text='Nome "amigável" para a URL.')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Artigos (Categorias)'


class Artigo(models.Model):
    autor = models.ForeignKey(get_user_model(), verbose_name='Autor', on_delete=models.RESTRICT)
    categoria = models.ForeignKey(CategoriaArtigo, on_delete=models.RESTRICT)
    titulo = models.CharField('Título', max_length=100, help_text='Máx 100 Caracteres')
    publicado = models.BooleanField('Publicado', default=False)
    texto = HTMLField('Texto')
    criado = models.DateField('Criado', auto_now_add=True)
    slug = models.SlugField(unique=True, help_text='Título "amigável" para a URL.')
    imagem = StdImageField(
        'Foto de Capa', upload_to=get_file_path,
        help_text='Tamanho ideal recomendado: 370x280',
        variations={'thumb': {'width': 370, 'height': 250, 'crop': True}},
        delete_orphans=True
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Artigo'
        verbose_name_plural = 'Artigos'


class Imagem(models.Model):
    imagem = StdImageField(
        'Foto de Capa', upload_to=get_file_path, default='http://via.placeholder.com/370x250',
        help_text='Tamanho ideal recomendado: 850x500',
        variations={'thumb': {'width': 370, 'height': 250, 'crop': True}},
        delete_orphans=True
    )

    def image_tag(self):
        return mark_safe('<img src="/media/%s" style="max-width: 100px;" />' % self.imagem)

    def url(self):
        return f'{settings.URL}media/{self.imagem}'

    image_tag.sort_description = 'Image'

    class Meta:
        verbose_name = 'Imagem'
        verbose_name_plural = 'Imagens'
