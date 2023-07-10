import json
import logging
import uuid
from datetime import datetime

from cieloApi3.paymentreturn import PaymentReturn
from cieloApi3.recurrentpaymentreturn import RecurrentPaymentReturn
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField
from creditcards.types import get_type
from creditcards.validators import CCNumberValidator, ExpiryDateValidator, CSCValidator
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from bot.management.commands.bot import enviar_notificacao, envia_convite, convite_unico, banir_membro, \
    enviar_mensagem_ao_assinante
from cieloApi3 import (
    CreditCard,
    Merchant,
    Sale,
    Payment,
    Environment,
    CieloEcommerce,
    Customer,
    RecurrentPayment,
    INTERVAL_MONTHLY, INTERVAL_ANNUAL, INTERVAL_BIMONTHLY, INTERVAL_QUARTERLY, INTERVAL_SEMIANNUAL
)
from financeiro.models import Pagamento, Ordem, Assinatura
from mundstock import settings


def validate_brand(value):
    brand = get_type(value)
    if brand not in range(1, 8):
        raise ValidationError('Desculpe. Esta bandeira não é aceita.')


def bandeira(value):
    if value == 1:
        return 'Visa'
    elif value == 2:
        return 'Amex'
    elif value == 3:
        return 'Diners'
    elif value == 4:
        return 'Discover'
    elif value == 5:
        return 'Master'
    elif value == 6:
        return 'Elo'
    elif value == 7:
        return 'JCB'
    return 'Generic'


def valida_cartao(cartao: CreditCard, id_ordem: str) -> bool:
    logging.info(f'Validando cartão para pagamento de ordem "{id_ordem}"')

    environment = Environment(sandbox=settings.SANDBOX)
    merchant = Merchant(settings.CIELO_MERCHANT_ID, settings.CIELO_MERCHANT_KEY)
    cielo_ecommerce = CieloEcommerce(merchant, environment)

    sale = Sale(id_ordem)
    sale.payment = Payment(50)
    sale.payment.capture = False
    sale.payment.soft_descriptor = 'MundstockEduc'
    sale.payment.credit_card = cartao
    try:
        cielo_ecommerce.create_sale(sale)
        if sale.payment.status == 1:
            cielo_ecommerce.cancel_sale(sale.payment.payment_id, 50)
            return True
        return False
    except Exception as ex:
        logging.exception(ex)
        raise ValidationError('Ocorreu um erro ao solicitar a transação. Verifique os dados preenchidos.')


def cria_pagamento(ordem, cartao, parcelas):
    logging.info('Preparando solicitação de pagamento...')
    valor = str(ordem.valor)
    if valor[::-1].find('.') == 1:
        valor += '0'
    valor = valor.replace('.', '')

    environment = Environment(sandbox=settings.SANDBOX)
    merchant = Merchant(settings.CIELO_MERCHANT_ID, settings.CIELO_MERCHANT_KEY)

    sale = Sale(ordem.id)
    sale.customer = Customer(ordem.nome_comprador)
    sale.payment = Payment(valor)
    sale.payment.capture = False
    sale.payment.soft_descriptor = 'MundstockEduc'
    sale.payment.credit_card = cartao
    sale.payment.installments = parcelas

    if ordem.recorrente:
        recurrent_payment = RecurrentPayment()

        if ordem.periodo == '1':
            recurrent_payment.interval = INTERVAL_MONTHLY
        elif ordem.periodo == '2':
            recurrent_payment.interval = INTERVAL_BIMONTHLY
        elif ordem.periodo == '4':
            recurrent_payment.interval = INTERVAL_QUARTERLY
        elif ordem.periodo == '6':
            recurrent_payment.interval = INTERVAL_SEMIANNUAL
        elif ordem.periodo == '12':
            recurrent_payment.interval = INTERVAL_ANNUAL

        if not ordem.start_date or (ordem.start_date and ordem.start_date < datetime.now().date()):
            recurrent_payment.start_date = ''
            recurrent_payment.authorize_now = True
        else:
            recurrent_payment.start_date = ordem.start_date.strftime('%Y-%m-%d')
            recurrent_payment.authorize_now = ordem.authorize_now

        if ordem.end_date:
            recurrent_payment.end_date = ordem.end_date.strftime('%Y-%m-%d')

        sale.payment.recurrent_payment = recurrent_payment

    cielo_ecommerce = CieloEcommerce(merchant, environment)
    logging.info('Solicitação preparada.')

    if ordem.authorize_now:
        cartao_valido = True
    else:
        cartao_valido = valida_cartao(cartao, ordem.id)

    if cartao_valido:
        logging.info('Cartão válido. Enviando solicitação...')
        pagamento = Pagamento()
        try:
            dados_pagamento = cielo_ecommerce.create_sale(sale)
            logging.info('Recebendo dados da solicitação:')
            logging.info(dados_pagamento)
        except Exception as ex:
            logging.exception(ex)
            raise ValidationError('Ocorreu um erro ao solicitar a transação. Verifique os dados preenchidos.')

        if type(dados_pagamento) == list:
            motivo = dados_pagamento[0]['Message']
            mensagem = f'Desculpe. Não conseguimos validar a transação. Motivo: {motivo}'
            logging.warning(mensagem)
            raise ValidationError(mensagem)

        if sale.payment.payment_id:
            pagamento.id = sale.payment.payment_id
            pagamento.tid = sale.payment.tid
            pagamento.parcelas = sale.payment.installments
            pagamento.status = sale.payment.status
            pagamento.data_pagamento = sale.payment.received_date
            pagamento.valor = ordem.valor

        if sale.payment.recurrent_payment:
            assinatura = Assinatura(id=sale.payment.recurrent_payment.recurrent_payment_id)
            assinatura.ordem = ordem
            assinatura.status = sale.payment.status
            assinatura.proxima_recorrencia = sale.payment.recurrent_payment.next_recurrency
            assinatura.interval = sale.payment.recurrent_payment.interval

            if sale.payment.status == 20:
                assinatura.start_date = sale.payment.recurrent_payment.start_date

            if sale.payment.recurrent_payment.end_date:
                assinatura.end_date = sale.payment.recurrent_payment.end_date

            assinatura.save()

            if sale.payment.payment_id:
                pagamento.assinatura = assinatura
                pagamento.save()

        else:
            pagamento.ordem = ordem
            pagamento.save()

        if sale.payment.status == 3:
            motivo = sale.payment.return_message
            mensagem = f'Desculpe. Não conseguimos validar a transação. Motivo: {motivo}'
            logging.warning(mensagem)
            raise ValidationError(mensagem)

        if sale.payment.status == 0:
            motivo = sale.payment.return_message
            mensagem = f'{motivo}. O servidor de pagamentos demorou a responder. ' \
                       f'Por favor, entre em contato para saber a situação do seu pagamento.'
            logging.warning(mensagem)
            raise ValidationError(mensagem)

        # if sale.payment.status == 1:
        #     logging.info('Solicitando captura do pagamento...')
        #     dados_captura = cielo_ecommerce.capture_sale(sale.payment.payment_id)
        #     logging.info(json.dumps(dados_captura, indent=4))
        #     if isinstance(dados_captura, dict):
        #         if dados_captura['Status'] == 2:
        #             pagamento.status = 2
        #             pagamento.save()
        #     else:
        #         mensagem = 'Ocorreu um erro ao tentar capturar um pagamento, na função Webhook. Verifique os logs.'
        #         enviar_notificacao(mensagem)

    else:
        mensagem = 'Não foi possível validar o cartão de crédito informado.'
        logging.warning(mensagem)
        raise ValidationError(mensagem)

    return sale.payment.status


class PagamentoForm(forms.Form):
    TIPO_PLANO = [
        ('Mensal', 'Mensal (R$ 39,90)'),
        ('Anual', 'Anual (R$ 399,90)'),
    ]
    PARCELAS = [
        ('1', '1x (à vista)'),
        ('2', '2 vezes (sem juros)'),
        ('3', '3 vezes (sem juros)'),
        ('4', '4 vezes (sem juros)'),
        ('5', '5 vezes (sem juros)'),
        ('6', '6 vezes (sem juros)'),
    ]
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
    pagamento = forms.ChoiceField(
        label='Pagamento',
        choices=TIPO_PLANO,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'takip();'}),
    )

    def clean_cc_numero(self):
        return self.cleaned_data['cc_numero'].replace(' ', '')

    def cria_novo_pagamento(self, ordem):
        environment = Environment(sandbox=settings.SANDBOX)
        merchant = Merchant(settings.CIELO_MERCHANT_ID, settings.CIELO_MERCHANT_KEY)

        brand = bandeira(get_type(self.clean_cc_numero()))

        cartao = CreditCard(self.cleaned_data['cc_codigo'], brand)
        cartao.expiration_date = self.cleaned_data['cc_validade'].strftime('%m/%Y')
        cartao.card_number = self.clean_cc_numero()
        cartao.holder = self.cleaned_data['cc_nome'].strip()

        sale = Sale(ordem.id)
        sale.customer = Customer(ordem.nome_comprador)
        sale.payment = Payment(str(ordem.valor).replace('.', ''))
        sale.payment.capture = True
        sale.payment.soft_descriptor = 'MundstockEduc'
        sale.payment.credit_card = cartao

        if ordem.recorrente and ordem.periodo == '1':
            parcelas = 1
        else:
            parcelas = self.cleaned_data['parcelas']

        status = cria_pagamento(ordem, cartao, parcelas)

        if status in (1, 2):
            if ordem.assinante.id_telegram:
                convite_grupo = convite_unico(settings.TELEGRAM_GRUPO_CLUB)
                convite_canal = convite_unico(settings.TELEGRAM_CANAL_CLUB)
                convite_app = ''
                envia_convite(ordem.assinante.id_telegram, convite_grupo, convite_canal, convite_app)

        return status


class AssinaturaModelForm(forms.ModelForm):
    class Meta:
        model = Assinatura
        fields = '__all__'

    def clean(self):
        environment = Environment(sandbox=settings.SANDBOX)
        merchant = Merchant(settings.CIELO_MERCHANT_ID, settings.CIELO_MERCHANT_KEY)
        cielo_ecommerce = CieloEcommerce(merchant, environment)
        try:
            if self.cleaned_data['ativo']:
                cielo_ecommerce.reactivate_recurrent_payment(self.instance.pk)
            else:
                cielo_ecommerce.deactivate_recurrent_payment(self.instance.pk)
        except Exception as ex:
            logging.error(ex)
            raise ValidationError('Erro ao tentar solicitar alteração da recorrência na Cielo.')

        return self.cleaned_data


# WEBHOOK
class AtualizaPagamentoForm(forms.Form):

    @staticmethod
    def intervalo(interval):
        if interval == 'Monthly':
            return 1
        elif interval == 'Bimonthly':
            return 2
        elif interval == 'Quarterly':
            return 4
        elif interval == 'SemiAnnual':
            return 6
        elif interval == 'Annual':
            return 12
        else:
            return 0

    @staticmethod
    def _envia_notificacao_alerta(assinante):
        conteudo = f"Olá!\nGostaria de informar que não foi possível renovar sua assinatura do Club. " \
                   f"Para continuar fazendo parte do Club, certifique-se de  que seu cartão esteja desbloqueado."
        enviar_mensagem_ao_assinante(conteudo, assinante.id_telegram)
        enviar_notificacao(f"Mensagem de cobrança enviada para {assinante.pessoa.nome}")

    @staticmethod
    def identifica_pagamento(pagamento_retorno):
        try:
            pagamento = Pagamento.objects.get(id=pagamento_retorno.payment_id)
        except Pagamento.DoesNotExist:
            pagamento = Pagamento(id=pagamento_retorno.payment_id)
            pagamento.tid = pagamento_retorno.tid
            pagamento.parcelas = pagamento_retorno.installments
            pagamento.valor = pagamento_retorno.amount / 100

        pagamento.status = pagamento_retorno.status
        pagamento.data_pagamento = pagamento_retorno.received_date
        return pagamento

    @staticmethod
    def identifica_assinatura(recorrencia_retorno):
        try:
            assinatura = Assinatura.objects.get(id=recorrencia_retorno.recurrent_payment_id)
            assinatura.start_date = recorrencia_retorno.start_date
            assinatura.status = recorrencia_retorno.status
            if recorrencia_retorno.next_recurrency:
                assinatura.proxima_recorrencia = recorrencia_retorno.next_recurrency

            return assinatura

        except Assinatura.DoesNotExist:
            mensagem = """
                Assinatura não encontrada para criação de novo pagamento.\n<b>Assinatura: </b>%s\n<b>Pagamento: </b>
                """ % recorrencia_retorno.recurrent_payment_id
            enviar_notificacao(mensagem)
        return None

    def save(self):
        logging.info(f'Notificação de pagamento recebida: {self.data}')
        environment = Environment(sandbox=settings.SANDBOX)
        merchant = Merchant(settings.CIELO_MERCHANT_ID, settings.CIELO_MERCHANT_KEY)
        cielo_ecommerce = CieloEcommerce(merchant, environment)

        change = self.data['ChangeType']

        if change == 1:
            pagamento_retorno = PaymentReturn()
            pagamento_retorno.update_return(cielo_ecommerce.get_sale(self.data['PaymentId']))
            pagamento = self.identifica_pagamento(pagamento_retorno)
            if pagamento_retorno.recurrent:
                pagamento.assinatura = Assinatura.objects.get(id=pagamento_retorno.recurrent_payment_id)
            else:
                pagamento.ordem = Ordem.objects.get(id=pagamento_retorno.id_ordem)

            if pagamento.valor > 0.5:
                pagamento.save()
                logging.info(f"ChangeType 1: Pagamento salvo: {pagamento.id}")
            else:
                logging.info('Pagamento referente a validação de cartão ignorado.')

        elif change == 2:
            pagamento_retorno = PaymentReturn()
            pagamento_retorno.update_return(cielo_ecommerce.get_sale(self.data['PaymentId']))
            recorrencia_retorno = RecurrentPaymentReturn()
            recorrencia_retorno.update_return(cielo_ecommerce.get_recurrent_payment(self.data['RecurrentPaymentId']))
            pagamento = self.identifica_pagamento(pagamento_retorno)
            assinatura = self.identifica_assinatura(recorrencia_retorno)
            if 0 < recorrencia_retorno.current_recurrency_try < 3:
                if assinatura.start_date == assinatura.proxima_recorrencia and recorrencia_retorno.current_recurrency_try == 2:
                    try:
                        cielo_ecommerce.deactivate_recurrent_payment(assinatura.id)
                        assinatura.ordem.assinante.ativo = False
                        assinatura.ordem.assinante.save()
                    except Exception as ex:
                        mensagem = f"Houve um problema ao cancelar a assinatura após 7 dias: " \
                                   f"{assinatura.ordem.assinante.pessoa.email}"
                        enviar_notificacao(mensagem)
                else:
                    if assinatura.ordem.assinante.id_telegram:
                        self._envia_notificacao_assinante(assinatura.ordem.assinante)
                    # self._envia_email_alerta('jonasesteves@msn.com')

            try:
                assinatura.save()
                logging.info(f"ChangeType 2: Assinatura salva: {assinatura.id}")
                pagamento.assinatura = assinatura
                pagamento.save()
                logging.info(f"ChangeType 2: Pagamento salvo: {pagamento.id}")
            except Exception as ex:
                logging.exception(ex)

        elif change == 4:
            recorrencia_retorno = RecurrentPaymentReturn()
            recorrencia_retorno.update_return(cielo_ecommerce.get_recurrent_payment(self.data['RecurrentPaymentId']))
            assinatura = self.identifica_assinatura(recorrencia_retorno)
            if assinatura.status == 4 and recorrencia_retorno.current_recurrency_try < 3:
                assinatura.ativo = False
                mensagem = f"<b>ATENÇÃO:</b>\nO usuário {assinatura.ordem.assinante.pessoa.nome} teve uma cobrança " \
                           f"recusada com retentativa não autorizada. É necessário gerar uma nova ordem de assinatura."
                enviar_notificacao(mensagem)
            if assinatura.status == 4 and recorrencia_retorno.current_recurrency_try == 3:
                banir_membro(assinatura.ordem.assinante.id_telegram)
                enviar_notificacao(f'Usuário {assinatura.ordem.assinante.pessoa.nome} removido por atraso no pagamento')
                assinatura.ativo = False
                assinatura.ordem.assinante.ativo = False
                assinatura.ordem.assinante.save()
                logging.info(f'Cancelado por retentativas: {assinatura.ordem.assinante.pessoa.nome}')
            if assinatura.status == 5:
                mensagem = f'Cartão vencido: {assinatura.ordem.assinante.pessoa.nome}'
                enviar_notificacao(mensagem)
                logging.info(mensagem)

            assinatura.save()

        else:
            mensagem = f"Cielo enviou um POST DE NOTIFICAÇÃO com ChangeType não programado: {self.data}"
            enviar_notificacao(mensagem)


