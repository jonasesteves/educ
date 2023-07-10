from django.db import models

from financeiro.models import Ordem
from gestao.models import ESTADO


class Entrega(models.Model):
    ordem = models.OneToOneField(Ordem, on_delete=models.RESTRICT)
    produto = models.CharField('Produto', max_length=20)
    comprador = models.CharField('Nome do Comprador', max_length=100)
    cep = models.CharField('CEP', max_length=9)
    logradouro = models.CharField('Logradouro', max_length=50)
    numero = models.IntegerField('Número')
    complemento = models.CharField('Complemento', max_length=50, null=True, blank=True)
    bairro = models.CharField('Bairro', max_length=50)
    cidade = models.CharField('Cidade', max_length=50)
    uf = models.CharField('UF', choices=ESTADO, max_length=2)
    telefone = models.CharField('Telefone', max_length=15)
    despachado = models.BooleanField('Despachado', default=False)
    data_despacho = models.DateTimeField('Data do despacho', null=True, blank=True)
    codigo_rastreio = models.CharField('Código de rastreio', max_length=20, null=True, blank=True)
    entregue = models.BooleanField('Entregue', default=False)
    data_entrega = models.DateTimeField('Data da entrega', null=True, blank=True)
    criado = models.DateTimeField('Criado', auto_now_add=True)

    def __str__(self):
        return self.comprador
