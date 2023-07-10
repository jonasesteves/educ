from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from financeiro.forms import AssinaturaModelForm
from financeiro.models import Pagamento, Ordem, Assinatura, Pix
from mundstock import settings


class PixInline(admin.TabularInline):
    model = Pix
    fields = ('data_pix', 'data_proximo_pagamento', 'valor', 'periodo_contratado', 'comprovante',)
    extra = 0
    can_delete = False
    ordering = ('-criado',)

    def has_change_permission(self, request, obj=None):
        return False


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    fields = ('id_link', '_pago', 'data_pagamento', 'valor', '_status',)
    readonly_fields = ('id_link', '_status', '_pago')
    extra = 0
    can_delete = False
    ordering = ('-data_pagamento',)

    @admin.display(description='Status')
    def _status(self, obj):
        if obj.status == 1:
            return 'Autorizado'
        elif obj.status == 2:
            return 'Finalizado'
        elif obj.status == 3:
            return 'Não autorizado'
        elif obj.status in (10, 11):
            return 'Cancelado'
        elif obj.status == 12:
            return 'Aguardando instituição financeira'
        elif obj.status == 13:
            return 'Falha no processamento'
        elif obj.status == 20:
            return 'Agendado'

    @admin.display(description='Id')
    def id_link(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (reverse('admin:financeiro_pagamento_change', args=(obj.id,)), obj.id))

    @admin.display(boolean=True, description='Pago')
    def _pago(self, obj):
        return obj.pago

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class OrdemInline(admin.TabularInline):
    model = Ordem
    fields = ('nome_comprador', 'valor', 'recorrente', 'periodo', 'authorize_now', 'pago', 'link', 'criado',)
    readonly_fields = ('pago', 'link', 'criado',)
    extra = 0
    can_delete = False
    show_change_link = True

    @admin.display(boolean=True)
    def pago(self, obj):
        if obj.pago:
            return True
        return False

    # @admin.display(description='Id')
    # def id_link(self, obj):
    #     return mark_safe('<a href="%s">%s</a>' % (reverse('admin:financeiro_ordem_change', args=(obj.id,)), obj.id))

    def has_change_permission(self, request, obj=None):
        return False

    # def has_add_permission(self, request, obj):
    #     return False


class AssinaturaInline(admin.StackedInline):
    model = Assinatura
    fields = ('id_link', 'ativo', 'pago', 'proxima_recorrencia')
    readonly_fields = ('id_link', 'pago')
    extra = 0
    can_delete = False

    @admin.display(description='Id')
    def id_link(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (reverse('admin:financeiro_assinatura_change', args=(obj.id,)), obj.id))

    @admin.display(description='Pago', boolean=True)
    def pago(self, obj):
        return obj.pago

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(Ordem)
class OrdemAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'id', 'nome_comprador', 'assinante', 'consultoria', 'matricula', 'valor', 'link', 'criado',
            )
        }),
        ('Recorrência', {
            'fields': (
                'recorrente', 'periodo', 'authorize_now', 'start_date', 'end_date',
            )
        }),
    )
    list_display = ('id', 'criado', 'valor', 'nome', 'sem_pagamento', '_pago')
    list_filter = ('recorrente',)
    ordering = ('-criado',)
    readonly_fields = ('id', 'link', 'criado')
    search_fields = ('id', 'nome_comprador')
    inlines = [AssinaturaInline, PagamentoInline, PixInline]

    @admin.display(description='')
    def sem_pagamento(self, obj):
        pagamentos = Pagamento.objects.filter(ordem=obj.id)
        assinaturas = Assinatura.objects.filter(ordem=obj.id)
        if not pagamentos and not assinaturas:
            return mark_safe('<img src="/static/admin/img/icon-alert.svg" title="Ordem sem pagamento associado">')
        return ''

    @admin.display(boolean=True)
    def _pago(self, obj):
        return obj.pago

    @admin.display(description='Nome')
    def nome(self, obj):
        if obj.nome_comprador:
            return obj.nome_comprador
        if obj.assinante:
            return obj.assinante.pessoa.nome
        # if obj.matricula:
        #     return obj.matricula.aluno.pessoa.nome

    def has_change_permission(self, request, obj=None):
        if settings.DEBUG:
            return True
        assinaturas = Assinatura.objects.filter(ordem=obj)
        pagamentos = Pagamento.objects.filter(ordem=obj)
        if not pagamentos and not assinaturas:
            return True
        return False


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'ordem', 'valor', '_pago', '_capturado', 'parcelas', 'tid', 'data_pagamento', 'observacoes',
            )
        }),
        ('Outros Dados', {
            'fields': ('status', 'criado',)
        })
    )
    list_display = ('id', 'tid', 'valor', '_pago', '_capturado', 'status', 'criado',)
    ordering = ('-criado',)
    readonly_fields = ('criado',)
    search_fields = ('id', 'tid', 'status', 'ordem__nome_comprador',)

    @admin.display(description='Pago', boolean=True)
    def _pago(self, obj):
        return obj.pago

    @admin.display(description='Capturado', boolean=True)
    def _capturado(self, obj):
        return obj.capturado

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     if settings.DEBUG:
    #         return True
    #     return False


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    form = AssinaturaModelForm
    fields = ('id', 'ordem', 'ativo', 'status', 'proxima_recorrencia', 'start_date', 'end_date', 'interval', 'criado')
    list_display = ('id', 'nome_assinante', 'pago')
    inlines = [PagamentoInline]
    readonly_fields = ('id', 'ordem', 'status', 'proxima_recorrencia', 'start_date', 'end_date', 'interval', 'criado')

    @admin.display(description='Assinante')
    def nome_assinante(self, obj):
        return obj.ordem.assinante.pessoa.nome

    @admin.display(description='Pago', boolean=True)
    def pago(self, obj):
        return obj.pago

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     if obj and obj.ativo:
    #         return True
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     if settings.DEBUG:
    #         return True
    #     return False


@admin.register(Pix)
class PixAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'data_pix', 'valor', 'data_proximo_pagamento', 'periodo_contratado',)
    search_fields = ('ordem__nome_comprador', 'data_pix', 'data_proximo_pagamento', 'valor',)
