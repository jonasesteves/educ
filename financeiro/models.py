import uuid
from datetime import datetime
from django.core.validators import URLValidator
from django.db import models
from stdimage import StdImageField

from core.models import get_file_path
from gestao.models import AssinanteClub, ClienteConsultoria, Matricula
from mundstock import settings


class Ordem(models.Model):
    PERIODO = [
        ('1', 'Mensal'),
        ('12', 'Anual'),
    ]
    id = models.CharField(primary_key=True, max_length=50, blank=True, help_text='Criado automaticamente.')
    # code...
    criado = models.DateTimeField('Criado', auto_now_add=True)

    @property
    def pago(self):
        assinaturas = Assinatura.objects.filter(ordem=self.id)
        pagamentos = Pagamento.objects.filter(ordem=self.id)
        pixes = Pix.objects.filter(ordem=self.id)

        if not pagamentos and not assinaturas and not pixes:
            return False

        if not self.recorrente:
            if pagamentos:
                for pagamento in pagamentos:
                    if pagamento.pago:
                        return True

            if pixes:
                for p in pixes:
                    if p.data_proximo_pagamento > datetime.now().date():
                        return True

        else:
            if assinaturas and assinaturas[0].pago:
                return True

        return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id == '':
            self.id = str(uuid.uuid4())
            self.link = f'{settings.URL}pagamento/{self.id}'
        super(Ordem, self).save()

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = 'Ordem'
        verbose_name_plural = 'Ordens'


class Assinatura(models.Model):
    id = models.CharField('Id', primary_key=True, max_length=50)
    # code...
    criado = models.DateTimeField('Criado', auto_now_add=True)

    @property
    def pago(self):
        if self.proxima_recorrencia > datetime.now().date():
            return True
        return False

    def __str__(self):
        return self.id


class Pagamento(models.Model):
    id = models.CharField(primary_key=True, max_length=50, help_text='Criado automaticamente.')
    # code...
    criado = models.DateTimeField('Criado', auto_now_add=True)

    @property
    def pago(self):
        return self.status in (1, 2)

    @property
    def capturado(self):
        return self.status == 2

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id == '':
            self.id = str(uuid.uuid4())
        super(Pagamento, self).save()

    def __str__(self):
        return self.id


class Pix(models.Model):
    # code...
    criado = models.DateTimeField('Criado', auto_now_add=True)

    def __str__(self):
        return self.ordem.nome_comprador

    class Meta:
        verbose_name = 'PIX'
        verbose_name_plural = 'PIX'
