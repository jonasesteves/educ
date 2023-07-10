from datetime import datetime

from django.contrib import admin
from django.utils.safestring import mark_safe

from financeiro.admin import OrdemInline, PagamentoInline
from gestao.models import Pessoa, AssinanteClub, ClienteConsultoria, FormularioConsultoria, Matricula


# class MatriculaInline(admin.TabularInline):
#     model = Matricula
#     # model = Curso.alunos.through
#     extra = 0
#     # readonly_fields = ('aluno', 'aceito',)
#     # raw_id_fields = ['aluno']
#     can_delete = False
#
#     def has_add_permission(self, request, obj):
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         return False


class FormularioConsultoriaInline(admin.StackedInline):
    model = FormularioConsultoria
    extra = 0
    fields = (
        'idade',
        'conhecimento_investimento',
        'conhecimento_economia',
        'investimentos',
        'tipo_gestao',
        'expectativa',
        'benchmark',
        'objetivo',
        'tempo',
        'recursos',
        'tolerancia',
        'acoes_caindo',
        'opiniao_diversificacao',
        'reserva_emergencia',
        'corretora',
    )


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Dados Pessoais', {
            'fields': (
                'nome',
                'cpf',
                'rg',
                'estado_civil',
                'nacionalidade',
                'profissao',
            )
        }),
        ('Informações de Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Endereço Completo', {
            'fields': (
                'cep',
                'logradouro',
                'numero',
                'complemento',
                'bairro',
                'cidade',
                'uf',
            )
        }),
        ('Outros Dados', {'fields': ('data_cadastro',)}),
    )
    list_display = ('cpf', 'nome', 'email',)
    readonly_fields = ('data_cadastro',)
    search_fields = ('nome', 'cpf', 'email',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('pessoa', 'cpf',)
        return self.readonly_fields


# @admin.register(Aluno)
# class AlunoAdmin(admin.ModelAdmin):
#     inlines = (MatriculaInline,)
#     list_display = ('nome', )
#     search_fields = ('pessoa__nome',)
#
#     @admin.display(description='Nome')
#     def nome(self, obj):
#         return obj.pessoa.nome
#
#     def has_add_permission(self, request):
#         return False
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:
#             return self.readonly_fields + ('pessoa',)
#         return self.readonly_fields


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    fields = ('pessoa', 'curso', 'aceito')
    readonly_fields = ('aceito',)
    list_display = ('nome', 'curso', 'valor_ordem', 'ordem_paga')
    list_filter = ('curso', )
    search_fields = ('pessoa__nome', 'curso__nome',)
    inlines = [OrdemInline]

    @admin.display(description='Nome')
    def nome(self, obj):
        return obj.pessoa.nome

    @admin.display(description='Pago', boolean=True)
    def ordem_paga(self, obj):
        if len(obj.ordem_set.all()) > 0:
            ordem = obj.ordem_set.all()[0]
            if ordem.pago:
                return True

        return False

    @admin.display(description='Valor da ordem')
    def valor_ordem(self, obj):
        if len(obj.ordem_set.all()) > 0:
            return obj.ordem_set.all()[0].valor
        return '-'

    # def has_add_permission(self, request):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('pessoa', 'curso')
        return self.readonly_fields


@admin.register(AssinanteClub)
class AssinanteAdmin(admin.ModelAdmin):
    indice = 0
    fields = ('pessoa', 'telegram', 'data_entrada_grupo', 'aceito', 'id_telegram', 'ativo', 'observacoes', 'criado',)
    list_display = ('nome', 'telegram', 'atraso', 'ativo', 'cielo_ativa', 'criado',)
    list_filter = ('ativo',)
    ordering = ('-ativo', 'pessoa__nome')
    readonly_fields = ('pessoa', 'data_entrada_grupo', 'aceito', 'id_telegram', 'criado',)
    search_fields = ('pessoa__nome', 'telegram',)
    inlines = [OrdemInline]

    @admin.display(description='Cobrança Ativa', boolean=True)
    def cielo_ativa(self, obj):
        if obj.assinatura_ativa:
            return True
        return False

    @admin.display(description='')
    def atraso(self, obj):
        if obj.atraso:
            return mark_safe('<img src="/static/admin/img/icon-alert.svg" title="Em atraso">')
        return ''

    @admin.display(description='Nome')
    def nome(self, obj):
        return obj.pessoa.nome

    def has_add_permission(self, request):
        return False


@admin.register(ClienteConsultoria)
class ClienteConsultoriaAdmin(admin.ModelAdmin):
    fields = ('pessoa', 'link_formulario', 'link_agendamento', 'mensagem', )
    list_display = ('pessoa',)
    inlines = [FormularioConsultoriaInline, OrdemInline]

    def has_change_permission(self, request, obj=None):
        return False
