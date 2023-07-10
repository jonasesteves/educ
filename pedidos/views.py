from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from mundstock import settings
from pedidos.forms import EntregaModelForm


class ProdutosView(TemplateView):
    template_name = 'produtos/produtos.html'


class OrdemView(FormView):
    template_name = 'produtos/ordem.html'
    form_class = EntregaModelForm
    url = settings.URL

    def get_context_data(self, **kwargs):
        context = super(OrdemView, self).get_context_data(**kwargs)
        produto = self.kwargs['produto']
        if produto not in ('caneca', 'camiseta_P', 'camiseta_M', 'camiseta_G'):
            raise Http404('Página não encontrada.')
        context['produto'] = produto
        if produto == 'caneca':
            context['valor'] = '35.00'
        else:
            context['valor'] = '50.00'
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        produto = self.get_context_data()['produto']
        try:
            with transaction.atomic():
                entrega = form.save(commit=False)
                ordem = form.cria_ordem_pedido(self.get_context_data()['produto'])
                entrega.ordem = ordem
                entrega.produto = produto
                entrega.save()
                status_pagamento = form.realiza_pagamento_pedido(ordem)
        except ValidationError as err:
            messages.error(self.request, err.message, extra_tags='danger')
            return super(OrdemView, self).form_invalid(form)

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
        return super(OrdemView, self).form_invalid(form)
