from django.contrib import admin
from .models import Curso, Depoimento, CategoriaLivro, Livro, Servico


# @admin.register(Curso)
# class CursoAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'inicio',)
#     exclude = ('alunos',)


@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(CategoriaLivro)
class CategoriaLivroAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria')
    search_fields = ('titulo', 'categoria__nome')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id', 'valor', 'ativo',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'inicio')



# @admin.register(Homem)
# class HomemAdmin(admin.ModelAdmin):
#     list_display = ('tamanho_barba',)


# class MulherInline(admin.TabularInline):
#     model = Mulher


# @admin.register(Mulher)
# class MulherAdmin(admin.ModelAdmin):
#     # fields = ('nome', 'cpf', 'cor_unha',)
#     # inlines = (PessoaInline, )
#     # Colunas da tabela de mulheres.
#     list_display = ('nome', 'cor_unha',)
#
#     @admin.display(description='Nome')
#     def nome(self, obj):
#         return obj.pessoa.nome
#
#     def get_readonly_fields(self, request, obj=None):
#         if obj:
#             return self.readonly_fields + ('pessoa',)
#         return self.readonly_fields


# class FilhoInline(admin.TabularInline):
#     model = Filho
#     extra = 0
#     verbose_name = 'Filho(a)'
#     verbose_name_plural = 'Filhos'
#     # raw_id_fields = ('mae',)
#     # can_delete = False
#
#     # def has_add_permission(self, request, obj):
#     #     return False
#
#
# @admin.register(Mae)
# class MaeAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'cor_unha')
#     inlines = [FilhoInline, ]
#     list_filter = ('nome',)
#
#
# @admin.register(Filho)
# class FilhoAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'brinquedo_favorito')
