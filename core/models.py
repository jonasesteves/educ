import uuid
from django.db import models
from stdimage import StdImageField
from tinymce import HTMLField


def get_file_path(_instance, filename):
    extensao = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{extensao}'
    return filename


ESTADO_CIVIL = [
    ('', 'Estado Civil'),
    ('Solteiro', 'Solteiro(a)'),
    ('Casado', 'Casado(a)'),
    ('Separado', 'Separado(a)'),
    ('Divorciado', 'Divorciado(a)'),
    ('Viúvo', 'Viúvo(a)'),
]
NIVEL = [
    ('Iniciante', 'Iniciante'),
    ('Intermediário', 'Intermediário'),
    ('Avançado', 'Avançado'),
]
BOOLEAN = [
    ('Sim', 'Sim'),
    ('Não', 'Não'),
]


class CategoriaLivro(models.Model):
    nome = models.CharField('Nome', max_length=50)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Livros (Categorias)'


class Livro(models.Model):
    categoria = models.ForeignKey(CategoriaLivro, on_delete=models.CASCADE)
    titulo = models.CharField('Título', max_length=100)
    link = models.TextField('Link', max_length=1000)

    def __str__(self):
        return self.titulo


class Curso(models.Model):
    nome = models.CharField('Nome do curso', max_length=50, help_text='Máx 50 caracteres.')
    categoria = models.CharField('Categoria', max_length=20, default='Finanças')
    descricao_breve = models.CharField('Descrição breve', max_length=150, help_text='Máx 150 caracteres', null=True, blank=True)
    descricao_completa = HTMLField('Descrição completa', max_length=2000, help_text='Máx 2000 caracteres', null=True, blank=True)
    valor = models.DecimalField('Valor', decimal_places=2, max_digits=7)
    desconto = models.DecimalField('Desconto em reais', decimal_places=2, max_digits=7, default=0)
    prazo_desconto = models.DateField('Prazo do desconto', null=True, blank=True, help_text='Data limite para dar o desconto')
    duracao = models.IntegerField('Duração (Meses)')
    inicio = models.DateField('Data de Início', null=True, blank=True, help_text='Data de início das matrículas')
    vagas = models.IntegerField('Vagas', null=True, blank=True)
    nivel = models.CharField('Nível', choices=NIVEL, max_length=13)
    certificado = models.CharField('Certificado', choices=BOOLEAN, default=BOOLEAN[1], max_length=3)
    ativo = models.BooleanField('Ativo?', default=True)
    imagem = StdImageField(
        'Imagem', upload_to=get_file_path,
        help_text='Tamanho ideal recomendado: 850x500',
        variations={'thumb': {'width': 370, 'height': 250, 'crop': True}},
        delete_orphans=True, null=True, blank=True
    )

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.nome


class Depoimento(models.Model):
    nome = models.CharField('Depoente', max_length=20)
    texto = models.TextField('Texto', max_length=280)
    imagem = StdImageField(
        'Imagem', upload_to=get_file_path, default='http://via.placeholder.com/150x150',
        help_text='Tamanho ideal recomendado: 150x150',
        variations={'thumb': {'width': 150, 'height': 150, 'crop': True}},
        delete_orphans=True
    )

    def __str__(self):
        return self.nome


class Servico(models.Model):
    nome = models.CharField('Nome', max_length=100)
    valor = models.DecimalField('Valor', max_digits=7, decimal_places=2)
    descricao_breve = models.CharField(
        'Descrição breve',
        max_length=150,
        null=True, blank=True,
        help_text='Máx 150 caracteres')
    descricao_completa = models.TextField('Descrição completa', max_length=2000, help_text='Máx 2000 caracteres')
    ativo = models.BooleanField('Ativo', default=False)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return self.nome
