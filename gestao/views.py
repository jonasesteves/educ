import logging
from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView

from core.models import Servico, Curso
from gestao.exceptions import RefusedPaymentError
from gestao.forms import ConsultoriaModelForm, FormularioConsultoriaForm, PreCadastroClubModelForm, MatriculaForm
from gestao.models import FormularioConsultoria, PreCadastroClub


class TermosClubView(TemplateView):
    template_name = 'club-termos-e-condicoes.html'


# class MatriculaAlunoView(FormView):
#     template_name = 'cursos/formulario-aluno.html'
#     form_class = AlunoModelForm
#     id_ordem = None
#
#     def get_context_data(self, **kwargs):
#         context = super(MatriculaAlunoView, self).get_context_data(**kwargs)
#         context['curso'] = get_object_or_404(Curso, id=self.kwargs['id'], ativo=True)
#         return context
#
#     @transaction.atomic
#     def form_valid(self, form, *args, **kwargs):
#
#         curso = Curso.objects.get(id=self.kwargs['id'])
#         try:
#             with transaction.atomic():
#                 aluno = form.cria_aluno()
#                 matricula = form.save(commit=False)
#                 matricula.aluno = aluno
#                 matricula.curso = curso
#                 matricula.save()
#             ordem = form.cria_ordem_pagamento(curso, matricula)
#             self.id_ordem = ordem.id
#             form.envia_email(ordem.link)
#         except IntegrityError:
#             messages.error(self.request, 'Você já está matriculado neste curso.', extra_tags='danger')
#             return super(MatriculaAlunoView, self).form_invalid(form)
#
#         return super(MatriculaAlunoView, self).form_valid(form)
#
#     def form_invalid(self, form, *args, **kwargs):
#         messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
#         return super(MatriculaAlunoView, self).form_invalid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('financeiro:pagamento', kwargs={'id': self.id_ordem})


class ClubView(TemplateView):
    template_name = 'club.html'
    # form_class = AssinanteClubModelForm
    # id_ordem = None

    # def get_context_data(self, **kwargs):
    #     context = super(ClubView, self).get_context_data(**kwargs)
    #     return context
    #
    # @transaction.atomic
    # def form_valid(self, form):
    #     pessoa = form.salva_pessoa()
    #     assinante = form.save(commit=False)
    #     assinante.pessoa = pessoa
    #     try:
    #         assinante.save()
    #         ordem = form.cria_ordem_assinatura(assinante)
    #         self.id_ordem = ordem.id
    #         form.envia_email(ordem.link)
    #     except IntegrityError:
    #         transaction.set_rollback(True)
    #         messages.error(self.request, 'Você já possui um cadastro no Club.', extra_tags='danger')
    #         return super(ClubView, self).form_invalid(form)
    #     except ValidationError as err:
    #         transaction.set_rollback(True)
    #         messages.error(self.request, err.message, extra_tags='danger')
    #         return super(ClubView, self).form_invalid(form)
    #
    #     # messages.error(self.request, f'Ocorreu um erro ao tentar realizar o cadastro.')
    #     # return super(ClubView, self).form_invalid(form)
    #     # context = self.get_context_data()
    #     # context['link_mp'] = assinatura.link
    #     # return render(self.request, '_____club-_____cadastro-realizado.html', context)
    #
    #     return super(ClubView, self).form_valid(form)
    #
    # def form_invalid(self, form):
    #     messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
    #     return super(ClubView, self).form_invalid(form)
    #
    # def get_success_url(self):
    #     return reverse_lazy('financeiro:pagamento', kwargs={'id': self.id_ordem})


class PreCadastroClubView(FormView):
    template_name = 'pagamento/pagamento-club.html'
    form_class = PreCadastroClubModelForm

    def get_context_data(self, **kwargs):
        context = super(PreCadastroClubView, self).get_context_data()
        context['precadastro'] = get_object_or_404(PreCadastroClub, id=self.kwargs['id'])
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        precadastro = context['precadastro']

        try:
            with transaction.atomic():
                pessoa = form.salva_pessoa()
                assinante = form.save(commit=False)
                assinante.pessoa = pessoa
                assinante.id_telegram = precadastro.id_telegram
                assinante.telegram = precadastro.telegram
                assinante.save()
                status_pagamento = form.realiza_pagamento(assinante, precadastro)
                form.envia_convite(assinante)
        except IntegrityError:
            messages.error(self.request, 'Você já possui um cadastro no Club.', extra_tags='danger')
            return super(PreCadastroClubView, self).form_invalid(form)
        except ValidationError as err:
            messages.error(self.request, err.message, extra_tags='danger')
            return super(PreCadastroClubView, self).form_invalid(form)

        if status_pagamento == 12:
            context['cabecalho'] = '<h2>Pagamento <span>Em Análise.</span></h2>'
            context['mensagem'] = '<p>Seu pagamento está sendo processado. ' \
                                  'Aguardando resposta da instituição financeira.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        if status_pagamento == 13:
            context['cabecalho'] = '<h2><span>Oops!</span></h2>'
            context['mensagem'] = '<p>Pagamento cancelado por falha no processamento ou por ação do AF.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        if status_pagamento == 20:
            context['cabecalho'] = '<h2>Pagamento <span>Agendado</span> com sucesso!</h2>'
            context['mensagem'] = '<p>Seu pagamento foi agendado. ' \
                                  'Você receberá uma mensagem do bot contendo todas as informações e links de acesso.'
            return render(self.request, 'pagamento/sucesso.html', context)

        return render(self.request, 'pagamento/sucesso.html')

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
        return super(PreCadastroClubView, self).form_invalid(form)


class ConsultoriaView(FormView):
    template_name = 'consultoria/consultoria.html'
    form_class = ConsultoriaModelForm
    success_url = reverse_lazy('gestao:consultoria')
    # id_ordem = None

    def get_context_data(self, **kwargs):
        context = super(ConsultoriaView, self).get_context_data()
        context['consultoria'] = get_object_or_404(Servico, id=1, ativo=True)
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        try:
            with transaction.atomic():
                pessoa = form.salva_pessoa()
                cliente_consultoria = form.save(commit=False)
                cliente_consultoria.pessoa = pessoa
                cliente_consultoria.save()
                # form.cria_formulario(cliente_consultoria)
                form.envia_notificacao(cliente_consultoria)
                # ordem = form.cria_ordem_consultoria(cliente_consultoria)
                # status_pagamento = form.realiza_pagamento_consultoria(ordem)
        except IntegrityError as err:
            logging.exception(err)
            messages.error(self.request, 'Desculpe. Ocorreu um erro ao enviar o formulário.', extra_tags='danger')
            return super(ConsultoriaView, self).form_invalid(form)
        except ValidationError as err:
            messages.error(self.request, err.message, extra_tags='danger')
            return super(ConsultoriaView, self).form_invalid(form)

        # form.envia_email_formulario(ordem)

        # if status_pagamento == 12:
        #     context['cabecalho'] = '<h2>Pagamento <span>Em Análise.</span></h2>'
        #     context['mensagem'] = '<p>Seu pagamento está sendo processado. ' \
        #                           'Aguardando resposta da instituição financeira.</p>'
        #     return render(self.request, 'pagamento/sucesso.html', context)
        #
        # if status_pagamento == 13:
        #     context['cabecalho'] = '<h2><span>Oops!</span></h2>'
        #     context['mensagem'] = '<p>Pagamento cancelado por falha no processamento ou por ação do AF.</p>'
        #     return render(self.request, 'pagamento/sucesso.html', context)

        # return render(self.request, 'pagamento/sucesso.html')
        messages.success(self.request, 'Em breve você será contatado pelo consultor por e-mail. Obrigado pela preferência.', extra_tags='success')
        return super(ConsultoriaView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
        return super(ConsultoriaView, self).form_invalid(form)

    # def get_success_url(self):
    #     return reverse_lazy('financeiro:pagamento', kwargs={'id': self.id_ordem})


class TermosConsultoriaView(TemplateView):
    template_name = 'consultoria/termos.html'


class FormularioConsultoriaUpdateView(UpdateView):
    model = FormularioConsultoria
    form_class = FormularioConsultoriaForm
    template_name = 'consultoria/consultoria-formulario.html'
    id_formulario = ''

    def get_context_data(self, **kwargs):
        context = super(FormularioConsultoriaUpdateView, self).get_context_data()
        context['formulario'] = get_object_or_404(FormularioConsultoria, id=self.kwargs['pk'], respondido=False)
        return context

    def form_valid(self, form):
        # ATUALIZA PESSOA AQUI E BLOQUEIA OS CAMPOS PREENCHIDOS, COMO  NO FORM DO PANORAMA
        formulario = form.save(commit=False)
        form.salva_pessoa(formulario.cliente.pessoa)
        # form.aceita_contrato(formulario.cliente)
        formulario.respondido = True
        self.id_formulario = formulario.id
        formulario.save()
        form.envia_notificacao(formulario.cliente)
        messages.success(self.request, 'Obrigado pela sua avaliação. Agende uma data e horário para a reunião online com o consultor.', extra_tags='api')
        return super(FormularioConsultoriaUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
        return super(FormularioConsultoriaUpdateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('gestao:consultoria-agendamento', kwargs={'pk': self.id_formulario})


# class FormularioConsultoriaView(FormView):
#     template_name = 'consultoria/consultoria-formulario.html'
#     form_class = FormularioConsultoriaForm
#     ordem = None
#
#     def get_context_data(self, **kwargs):
#         context = super(FormularioConsultoriaView, self).get_context_data()
#         context['ordem'] = get_object_or_404(Ordem, id=self.kwargs['id'])
#         try:
#             formulario = (context['ordem']).consultoria.formulario
#             raise Http404()
#         except FormularioConsultoria.DoesNotExist:
#             if not context['ordem'].pago:
#                 raise Http404()
#         return context
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         self.ordem = context['ordem']
#         formulario = form.save(commit=False)
#         formulario.cliente = self.ordem.consultoria
#         formulario.save()
#         form.notificacao(self.ordem)
#         return super(FormularioConsultoriaView, self).form_valid(form)
#
#     def form_invalid(self, form):
#         messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
#         return super(FormularioConsultoriaView, self).form_invalid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('gestao:consultoria-agendamento', kwargs={'id': self.ordem.id})


class AgendamentoConsultoriaView(TemplateView):
    template_name = 'consultoria/consultoria-agendamento.html'

    def get_context_data(self, **kwargs):
        context = super(AgendamentoConsultoriaView, self).get_context_data()
        context['formulario'] = get_object_or_404(FormularioConsultoria, id=self.kwargs['pk'], respondido=True)
        # ordem = get_object_or_404(Ordem, id=self.kwargs['id'])
        # if not ordem.pago:
        #     raise Http404()
        return context


class ConfirmAgendamentoConsultoriaView(TemplateView):
    template_name = 'consultoria/confirmacao-agendamento.html'

    def get_context_data(self, **kwargs):
        context = super(ConfirmAgendamentoConsultoriaView, self).get_context_data()
        str_inicio = self.request.GET.get('event_start_time')
        str_fim = self.request.GET.get('event_end_time')
        context['data'] = datetime.strptime(str_inicio, '%Y-%m-%dT%H:%M:%S%z')
        context['inicio'] = datetime.strptime(str_inicio, '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M')
        context['fim'] = datetime.strptime(str_fim, '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M')
        return context


class MatriculaView(FormView):
    template_name = 'cursos/matricula.html'
    form_class = MatriculaForm
    success_url = reverse_lazy('core:index')

    def get_context_data(self, **kwargs):
        context = super(MatriculaView, self).get_context_data(**kwargs)
        try:
            context['curso'] = Curso.objects.get(pk=self.kwargs['pk'], ativo=True)
        except Curso.DoesNotExist:
            raise Http404
        context['valor_com_desconto'] = context['curso'].valor - context['curso'].desconto
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()

        try:
            with transaction.atomic():
                matricula = form.save(commit=False)
                pessoa = form.salva_pessoa()
                matricula.curso = context['curso']
                matricula.pessoa = pessoa
                matricula.save()
                status_pagamento = form.paga_curso(context['curso'])
                form.enviar_email()
        except RefusedPaymentError:
            messages.error(self.request, 'Desculpe, seu pagamento não foi aprovado.', extra_tags='danger')
            return super(MatriculaView, self).form_invalid(form)
        except ValidationError as err:
            messages.error(self.request, err.message, extra_tags='danger')
            return super(MatriculaView, self).form_invalid(form)
        except IntegrityError:
            messages.error(self.request, 'Você já realizou uma matrícula neste curso.', extra_tags='danger')
            return super(MatriculaView, self).form_invalid(form)

        if status_pagamento == 12:
            context['cabecalho'] = '<h2>Pagamento <span>Em Análise.</span></h2>'
            context['mensagem'] = '<p>Seu pagamento está sendo processado. ' \
                                  'Aguardando resposta da instituição financeira.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        if status_pagamento == 13:
            context['cabecalho'] = '<h2><span>Oops!</span></h2>'
            context['mensagem'] = '<p>Pagamento cancelado por falha no processamento ou por ação do AF.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        return render(self.request, 'pagamento/sucesso.html')

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
        return super(MatriculaView, self).form_invalid(form)
