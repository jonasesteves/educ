import json
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.views.generic import FormView
from financeiro.forms import PagamentoForm, AtualizaPagamentoForm
from financeiro.models import Ordem, Assinatura, Pagamento


class PagamentoView(FormView):
    template_name = 'pagamento/form-pagamento.html'
    form_class = PagamentoForm

    def get_context_data(self, **kwargs):
        context = super(PagamentoView, self).get_context_data(**kwargs)
        context['ordem'] = get_object_or_404(Ordem, id=self.kwargs['id'])
        assinaturas = Assinatura.objects.filter(ordem=self.kwargs['id'])
        pagamentos = Pagamento.objects.filter(Q(ordem=self.kwargs['id']), Q(status=1) | Q(status=2) | Q(status=20))
        if pagamentos or assinaturas:
            raise Http404
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ordem = context['ordem']
        try:
            status = form.cria_novo_pagamento(ordem)
        except ValidationError as err:
            messages.error(self.request, err.message, extra_tags='danger')
            return super(PagamentoView, self).form_invalid(form)

        if status == 12:
            context['cabecalho'] = '<h2>Pagamento <span>Em Análise.</span></h2>'
            context['mensagem'] = '<p>Seu pagamento está sendo processado. ' \
                                  'Aguardando resposta da instituição financeira.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        if status == 13:
            context['cabecalho'] = '<h2><span>Oops!</span></h2>'
            context['mensagem'] = '<p>Pagamento cancelado por falha no processamento ou por ação do AF.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        if status == 20:
            context['cabecalho'] = '<h2>Pagamento <span>Agendado</span> com sucesso!</h2>'
            context['mensagem'] = '<p><strong>Obrigado pela preferência. </strong>' \
                                  'Continue explorando nosso conteúdo.</p>'
            return render(self.request, 'pagamento/sucesso.html', context)

        return render(self.request, 'pagamento/sucesso.html')

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija os erros do formulário.', extra_tags='danger')
        return super(PagamentoView, self).form_invalid(form)


@csrf_exempt
@require_POST
def payment_webhook(request):
    data = json.loads(request.body)
    form = AtualizaPagamentoForm(data)
    if form.is_valid():
        form.save()

    return JsonResponse({})
