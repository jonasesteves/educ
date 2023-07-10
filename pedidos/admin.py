from django.contrib import admin
from mundstock import settings
from pedidos.models import Entrega


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Produto', {'fields': ('produto', 'criado', 'ordem',)}),
        ('Dados da Entrega', {
            'fields': (
                'comprador',
                'telefone',
                'cep',
                'logradouro',
                'numero',
                'complemento',
                'bairro',
                'cidade',
                'uf',
            )
        }),
        ('Despacho', {
            'fields': (
                'despachado',
                'data_despacho',
                'codigo_rastreio',
                'entregue',
                'data_entrega',
            )
        })
    )
    list_display = ('comprador', 'produto', 'pago', 'despachado', 'entregue')
    readonly_fields = ('ordem', 'produto', 'criado')
    search_fields = ('comprador', 'produto',)

    @admin.display(description='Pago', boolean=True)
    def pago(self, obj):
        return obj.ordem.pago

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        if settings.DEBUG:
            return True
        if obj and not obj.ordem.pago:
            return True
        return False
