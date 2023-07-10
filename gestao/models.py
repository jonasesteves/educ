import logging
import uuid
from datetime import datetime
from django.db import models
from core.models import Curso
from mundstock import settings

ESTADO = [
    ('', 'Estado'),
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]


class Pessoa(models.Model):
    ESTADO_CIVIL = [
        ('Solteiro', 'Solteiro(a)'),
        ('Casado', 'Casado(a)'),
        ('Separado', 'Separado(a)'),
        ('Divorciado', 'Divorciado(a)'),
        ('Viúvo', 'Viúvo(a)'),
    ]
    nome = models.CharField('Nome', max_length=100)
    cpf = models.CharField('CPF', max_length=14, unique=True, null=True, blank=True)
    rg = models.CharField('RG', max_length=20, unique=True, null=True, blank=True)
    estado_civil = models.CharField('Estado Civil', choices=ESTADO_CIVIL, max_length=20, null=True, blank=True)
    nacionalidade = models.CharField('Nacionalidade', max_length=20, null=True, blank=True)
    profissao = models.CharField('Profissão', max_length=50, null=True, blank=True)
    cep = models.CharField('CEP', max_length=9, null=True, blank=True)
    logradouro = models.CharField('Logradouro', max_length=50, null=True, blank=True)
    numero = models.IntegerField('Número', null=True, blank=True)
    complemento = models.CharField('Complemento', max_length=50, null=True, blank=True)
    bairro = models.CharField('Bairro', max_length=50, null=True, blank=True)
    cidade = models.CharField('Cidade', max_length=50, null=True, blank=True)
    uf = models.CharField('UF', choices=ESTADO, max_length=2, null=True, blank=True)
    telefone = models.CharField('Telefone', max_length=15, null=True, blank=True)
    email = models.EmailField('E-mail', max_length=50, unique=True)
    data_cadastro = models.DateTimeField('Data de cadastro', auto_now_add=True)

    def __str__(self):
        return self.nome


class AssinanteClub(models.Model):
    pessoa = models.OneToOneField(Pessoa, models.CASCADE)
    id_telegram = models.BigIntegerField('Id Telegram', unique=True, null=True, blank=True)
    telegram = models.CharField('Telegram', max_length=32, unique=True, null=True, blank=True)
    data_entrada_grupo = models.DateTimeField('Data Entrada Grupo', null=True)
    ativo = models.BooleanField('Ativo', default=False, null=False)
    aceito = models.BooleanField('Contrato aceito', default=False, null=False)
    observacoes = models.TextField('Observações', max_length=500, null=True, blank=True)
    criado = models.DateTimeField('Criado', auto_now_add=True)

    @property
    def atraso(self):
        if self.ativo:
            try:
                ordem = self.ordem_set.order_by('-criado')[0:1].get()
                if not ordem.start_date:
                    if not ordem.pago:
                        return True
                else:
                    if ordem.start_date < datetime.now().date():
                        if not ordem.pago:
                            return True
            except Exception as ex:
                logging.exception(f"{self.pessoa}: {ex}")
        return False

    @property
    def assinatura_ativa(self):
        ordens = self.ordem_set.filter(assinatura__ativo=True)
        try:
            return ordens[0].assinatura
        except IndexError:
            pass
        return None

    def __str__(self):
        return self.pessoa.nome

    class Meta:
        verbose_name = 'Assinante Club'
        verbose_name_plural = 'Assinantes Club'


class Matricula(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    aceito = models.BooleanField('Contrato aceito', default=False)

    class Meta:
        unique_together = [['pessoa_id', 'curso_id']]
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'

    def __str__(self):
        return f"{self.pessoa} - {self.curso}"


class ClienteConsultoria(models.Model):
    pessoa = models.OneToOneField(Pessoa, models.CASCADE)
    aceito = models.BooleanField('Contrato aceito', default=False)
    link_formulario = models.CharField('Link do formulário', max_length=200, null=True, blank=True)
    link_agendamento = models.CharField('Link de agendamento', max_length=200, null=True, blank=True)
    mensagem = models.TextField('Mensagem', max_length=500, null=True, blank=True)
    criado = models.DateTimeField('Criado', auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente Consultoria'
        verbose_name_plural = 'Clientes Consultoria'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(ClienteConsultoria, self).save()
        if self.link_formulario is None:
            formulario = FormularioConsultoria()
            id_formulario = str(uuid.uuid4())
            formulario.id = id_formulario
            formulario.cliente = self
            formulario.save()
            self.link_formulario = f'{settings.URL}consultoria/formulario/{id_formulario}'
            self.link_agendamento = f'{settings.URL}consultoria/agendamento/{id_formulario}'
            super(ClienteConsultoria, self).save()

    def __str__(self):
        return self.pessoa.nome


class FormularioConsultoria(models.Model):
    id = models.CharField('Id', primary_key=True, max_length=50)
    cliente = models.OneToOneField(ClienteConsultoria, models.CASCADE, related_name='formulario')
    respondido = models.BooleanField('Respondido', default=False)
    # link = models.CharField('Link', max_length=200)
    formacao_academica = models.CharField('Formação acadêmica', max_length=200, null=True)
    idade = models.CharField('Idade', max_length=200, null=True)
    conhecimento_investimento = models.CharField('Conhecimento sobre investimento', max_length=200, null=True)
    conhecimento_economia = models.CharField('Conhecimento sobre economia', max_length=200, null=True)
    investimentos = models.CharField('Investimentos que tem ou já teve:', max_length=200, null=True)
    tipo_gestao = models.CharField('Tipo de gestão ideal', max_length=200, null=True)
    expectativa = models.CharField('Expectativa de rentabilidade a.a.', max_length=200, null=True)
    benchmark = models.CharField('Referência de rentabilidade (Benchmark)', max_length=200, null=True)
    objetivo = models.CharField('Objetivo ao investir', max_length=200, null=True)
    tempo = models.CharField('Tempo dos investimentos', max_length=200, null=True)
    recursos = models.CharField('Quando pretende utilizar recursos', max_length=200, null=True)
    tolerancia = models.CharField('Tolerância ao risco', max_length=200, null=True)
    acoes_caindo = models.CharField('O que faria se ações caíssem 30%', max_length=200, null=True)
    opiniao_diversificacao = models.CharField('Opinião sobre diversificação', max_length=200, null=True)
    reserva_emergencia = models.CharField('Tem reserva de emergencia', max_length=200, null=True)
    corretora = models.CharField('Corretora de preferência', max_length=50, null=True)
    criado = models.DateTimeField('Criado', auto_now_add=True)

    class Meta:
        verbose_name = 'Formulário'

    def __str__(self):
        return self.cliente.link_formulario


class PreCadastroClub(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    id_telegram = models.BigIntegerField('Id Telegram')
    telegram = models.CharField('Telegram', max_length=35, null=True)
    nome = models.CharField('Nome', max_length=50)
    plano = models.CharField('Plano', max_length=10)
    valor = models.DecimalField('Valor', max_digits=7, decimal_places=2)
    link = models.URLField('Link', max_length=100)
    criado = models.DateTimeField('Criado', auto_now_add=True)


