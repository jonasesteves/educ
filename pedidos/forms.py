import uuid

from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField
from creditcards.types import get_type
from creditcards.validators import CCNumberValidator, ExpiryDateValidator, CSCValidator
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from cieloApi3 import CreditCard
from financeiro.forms import bandeira, cria_pagamento, validate_brand
from financeiro.models import Ordem
from gestao.models import ESTADO
from mundstock import settings
from pedidos.models import Entrega
from automacao import bot


class EntregaModelForm(forms.ModelForm):
    PARCELAS = [
        ('1', '1x (à vista)'),
        ('2', '2 vezes'),
    ]
    comprador = forms.CharField(
        label='Nome', max_length=100, min_length=8,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome Completo',
            'class': 'form-control',
        }),
    )
    telefone = forms.CharField(
        label='Telefone',
        max_length=15,
        min_length=14,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Telefone',
            'class': 'form-control telefone',
        }),
    )
    logradouro = forms.CharField(
        label='Logradouro',
        max_length=50,
        min_length=5,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Logradouro',
            'class': 'form-control',
        }),
    )
    numero = forms.IntegerField(
        label='Número',
        widget=forms.TextInput(attrs={
            'placeholder': 'Número',
            'class': 'form-control',
            'data-mask': '000000',
        }),
    )
    complemento = forms.CharField(
        label='Complemento',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Complemento',
            'class': 'form-control',
        }),
    )
    bairro = forms.CharField(
        label='Bairro',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Bairro',
            'class': 'form-control',
        }),
    )
    cidade = forms.CharField(
        label='Cidade',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Cidade',
            'class': 'form-control',
        }),
    )
    uf = forms.ChoiceField(
        label='Estado',
        choices=ESTADO,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    cep = forms.CharField(
        label='CEP',
        max_length=9,
        widget=forms.TextInput(attrs={
            'placeholder': 'CEP',
            'class': 'form-control cep',
            'onblur': 'pesquisacep(this.value);',
            'data-mask': '00000-000',
        }),
    )
    cc_nome = forms.CharField(
        label='Nome do Cartão',
        max_length=50,
        min_length=8,
        validators=[MinLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome (Idêntico ao Cartão)',
            'class': 'form-control',
        }),
    )
    cc_numero = CardNumberField(
        label='Número do Cartão',
        widget=forms.TextInput(attrs={
            'placeholder': 'Número do Cartão de Crédito',
            'data-mask': '0000 0000 0000 0000',
        }),
        validators=[CCNumberValidator, validate_brand],
        error_messages={'invalid': 'Por favor, digite um número válido.'}
    )
    cc_validade = CardExpiryField(
        label='Validade',
        widget=forms.TextInput(attrs={'data-mask': '00/00'}),
        validators=[ExpiryDateValidator],
        error_messages={'date_passed': 'Ops! Esta data já passou!'}
    )
    cc_codigo = SecurityCodeField(
        label='CVV',
        widget=forms.TextInput(attrs={'placeholder': 'CVV', 'data-mask': '0000'}),
        validators=[CSCValidator],
        error_messages={'invalid': 'Por favor, digite um código válido.'}
    )
    parcelas = forms.ChoiceField(
        label='Parcelas',
        choices=PARCELAS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def clean_cc_numero(self):
        return self.cleaned_data['cc_numero'].replace(' ', '')

    def cria_ordem_pedido(self, produto):
        valor = 0
        if produto == 'caneca':
            valor = 35.0
        elif produto in ('camiseta_P', 'camiseta_M', 'camiseta_G'):
            valor = 50.0

        id_ordem = str(uuid.uuid4())
        link_pagamento = settings.URL + 'pagamento/' + id_ordem
        ordem = Ordem(id=id_ordem, nome_comprador=self.cleaned_data['comprador'], link=link_pagamento, valor=valor)
        ordem.recorrente = False
        ordem.authorize_now = True
        ordem.save()

        return ordem

    def realiza_pagamento_pedido(self, ordem):
        brand = bandeira(get_type(self.clean_cc_numero()))

        cartao = CreditCard(self.cleaned_data['cc_codigo'], brand)
        cartao.expiration_date = self.cleaned_data['cc_validade'].strftime('%m/%Y')
        cartao.card_number = self.clean_cc_numero()
        cartao.holder = self.cleaned_data['cc_nome'].strip()
        parcelas = self.cleaned_data['parcelas']

        status = cria_pagamento(ordem, cartao, parcelas)

        if status in (1, 2):
            mensagem = 'Um novo produto foi vendido no site. Verifique o Painel Administrativo.'
            bot.enviar_notificacao(mensagem)

        return status

    class Meta:
        model = Entrega
        fields = ['comprador', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', 'telefone']



