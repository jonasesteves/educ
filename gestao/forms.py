import logging
import uuid
from datetime import datetime, timedelta

from cieloApi3 import CreditCard
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField
from creditcards.types import get_type
from creditcards.validators import CCNumberValidator, ExpiryDateValidator, CSCValidator
from django import forms
from django.core.mail import EmailMessage
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator
from django.db.models import Q
from localflavor.br.forms import BRCPFField

from bot.management.commands import bot
from bot.management.commands.bot import convite_unico, envia_convite
from financeiro.forms import validate_brand, bandeira, cria_pagamento
from financeiro.models import Ordem
from gestao.exceptions import RefusedPaymentError
from gestao.models import Pessoa, AssinanteClub, ClienteConsultoria, FormularioConsultoria, ESTADO, Matricula
from mundstock import settings


class PessoaModelForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ['nome', 'cpf', 'email', 'telefone']


# class AlunoModelForm(forms.ModelForm):
#     nome = forms.CharField(
#         label='Nome', max_length=100, min_length=8,
#         validators=[MinLengthValidator, MaxLengthValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Nome Completo',
#             'class': 'form-control',
#         }),
#     )
#     cpf = BRCPFField(
#         label='CPF',
#         widget=forms.TextInput(attrs={
#             'placeholder': 'CPF', 'class': 'form-control',
#             'data-mask': '000.000.000-00'
#         }),
#         error_messages={'invalid': 'CPF inválido.'}
#     )
#     email = forms.CharField(
#         label='E-mail', max_length=50,
#         validators=[EmailValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'E-mail',
#             'class': 'form-control',
#         }),
#     )
#     telefone = forms.CharField(
#         label='Telefone',
#         max_length=15,
#         min_length=14,
#         validators=[MinLengthValidator, MaxLengthValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Telefone',
#             'class': 'form-control telefone',
#         }),
#     )
#     rg = forms.CharField(
#         label='RG',
#         max_length=20,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'RG',
#             'class': 'form-control',
#             'data-mask': '00000000000000000000',
#         }),
#     )
#     nacionalidade = forms.CharField(
#         label='Nacionalidade',
#         max_length=20,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Nacionalidade',
#             'class': 'form-control',
#         }),
#     )
#     estado_civil = forms.ChoiceField(
#         label='Estado Civil',
#         choices=ESTADO_CIVIL,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#     )
#     profissao = forms.CharField(
#         label='Profissão',
#         max_length=50,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Profissão',
#             'class': 'form-control',
#         }),
#     )
#     logradouro = forms.CharField(
#         label='Logradouro',
#         max_length=50,
#         min_length=5,
#         validators=[MinLengthValidator, MaxLengthValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Logradouro',
#             'class': 'form-control',
#         }),
#     )
#     numero = forms.IntegerField(
#         label='Número',
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Número',
#             'class': 'form-control',
#             'data-mask': '000000',
#         }),
#     )
#     complemento = forms.CharField(
#         label='Complemento',
#         max_length=50,
#         required=False,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Complemento',
#             'class': 'form-control',
#         }),
#     )
#     bairro = forms.CharField(
#         label='Bairro',
#         max_length=50,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Bairro',
#             'class': 'form-control',
#         }),
#     )
#     cidade = forms.CharField(
#         label='Cidade',
#         max_length=50,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Cidade',
#             'class': 'form-control',
#         }),
#     )
#     uf = forms.ChoiceField(
#         label='Estado',
#         choices=ESTADO,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#     )
#     cep = forms.CharField(
#         label='CEP',
#         max_length=9,
#         widget=forms.TextInput(attrs={
#             'placeholder': 'CEP',
#             'class': 'form-control cep',
#             'onblur': 'pesquisacep(this.value);',
#             'data-mask': '00000-000',
#         }),
#     )
#     aceito = forms.CheckboxInput()
#
#     def cria_aluno(self):
#         try:
#             pessoa = Pessoa.objects.get(cpf=self.cleaned_data['cpf'])
#             pessoa.estado_civil = self.cleaned_data['estado_civil']
#             pessoa.nacionalidade = self.cleaned_data['nacionalidade']
#             pessoa.cep = self.cleaned_data['cep']
#             pessoa.logradouro = self.cleaned_data['logradouro']
#             pessoa.numero = self.cleaned_data['numero']
#             pessoa.complemento = self.cleaned_data['complemento']
#             pessoa.bairro = self.cleaned_data['bairro']
#             pessoa.cidade = self.cleaned_data['cidade']
#             pessoa.uf = self.cleaned_data['uf']
#             pessoa.telefone = self.cleaned_data['telefone']
#             pessoa.email = self.cleaned_data['email']
#             pessoa.save()
#         except Pessoa.DoesNotExist:
#             pessoa = Pessoa(
#                 nome=self.cleaned_data['nome'],
#                 cpf=self.cleaned_data['cpf'],
#                 rg=self.cleaned_data['rg'],
#                 nacionalidade=self.cleaned_data['nacionalidade'],
#                 estado_civil=self.cleaned_data['estado_civil'],
#                 profissao=self.cleaned_data['profissao'],
#                 email=self.cleaned_data['email'],
#                 logradouro=self.cleaned_data['logradouro'],
#                 numero=self.cleaned_data['numero'],
#                 complemento=self.cleaned_data['complemento'],
#                 bairro=self.cleaned_data['bairro'],
#                 cidade=self.cleaned_data['cidade'],
#                 cep=self.cleaned_data['cep'],
#                 uf=self.cleaned_data['uf'],
#                 telefone=self.cleaned_data['telefone'],
#             )
#             pessoa.save()
#
#         try:
#             aluno = Aluno.objects.get(pessoa_id=pessoa.id)
#         except Aluno.DoesNotExist:
#             aluno = Aluno(pessoa=pessoa)
#             aluno.save()
#
#         return aluno
#
#     @staticmethod
#     def cria_ordem_pagamento(curso, matricula):
#         id_ordem = str(uuid.uuid4())
#         link_pagamento = settings.URL + 'pagamento/' + id_ordem
#         ordem = Ordem(id=id_ordem, matricula=matricula, link=link_pagamento, valor=curso.valor)
#         ordem.nome_comprador = matricula.aluno.pessoa.nome
#         ordem.save()
#         return ordem
#
#     def envia_email(self, link_pagamento):
#         email = self.cleaned_data['email']
#         conteudo = email_curso(link_pagamento)
#
#         mail = EmailMessage(
#             subject='Sua matrícula foi realizada',
#             body=conteudo,
#             from_email='Mundstock Educacional <contato@mundstockeducacional.com.br>',
#             to=[email, ],
#             headers={'Reply-To': 'contato@mundstockeducacional.com.br'}
#         )
#         mail.content_subtype = 'html'
#         mail.send()
#
#     def clean_cc_numero(self):
#         return self.cleaned_data['cc_numero'].replace(' ', '')
#
#     class Meta:
#         model = Matricula
#         fields = ['nome', 'cpf', 'rg', 'nacionalidade', 'estado_civil', 'profissao', 'cep', 'logradouro', 'numero',
#                   'complemento', 'bairro', 'cidade', 'uf', 'telefone', 'email', 'aceito', ]


# class AssinanteClubModelForm(forms.ModelForm):
#     mensal = '3990'
#     anual = '39990'
#     TIPO_PLANO = [
#         ('1', f'Mensal (R$ {mensal[:-2]},{mensal[-2::]})'),
#         ('12', f'Anual (R$ {anual[:-2]},{anual[-2::]})'),
#     ]
#
#     nome = forms.CharField(
#         label='Nome', max_length=100, min_length=8,
#         validators=[MinLengthValidator, MaxLengthValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Nome Completo',
#             'class': 'form-control',
#         }),
#     )
#     cpf = BRCPFField(
#         label='CPF',
#         widget=forms.TextInput(attrs={
#             'placeholder': 'CPF', 'class': 'form-control',
#             'data-mask': '000.000.000-00'
#         }),
#         error_messages={'invalid': 'CPF inválido.'}
#     )
#     email = forms.CharField(
#         label='E-mail', max_length=50, validators=[EmailValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'E-mail',
#             'class': 'form-control',
#         }),
#     )
#     telefone = forms.CharField(
#         label='Telefone',
#         max_length=15,
#         min_length=14,
#         validators=[MinLengthValidator, MaxLengthValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': 'Telefone',
#             'class': 'form-control telefone',
#         }),
#     )
#     telegram = forms.CharField(
#         label='Telegram',
#         min_length=5,
#         max_length=32,
#         validators=[MinLengthValidator, MaxLengthValidator],
#         widget=forms.TextInput(attrs={
#             'placeholder': '@seu_usuario_do_telegram',
#             'class': 'form-control',
#         }),
#     )
#     pagamento = forms.ChoiceField(
#         label='Pagamento',
#         choices=TIPO_PLANO,
#         widget=forms.Select(attrs={'class': 'form-control'}),
#     )
#
#     def salva_pessoa(self):
#         try:
#             pessoa = Pessoa.objects.get(cpf=self.cleaned_data['cpf'])
#             pessoa.telefone = (self.cleaned_data['telefone'])
#             pessoa.email = (self.cleaned_data['email'])
#         except Pessoa.DoesNotExist:
#             pessoa = Pessoa(
#                 nome=self.cleaned_data['nome'],
#                 cpf=self.cleaned_data['cpf'],
#                 telefone=self.cleaned_data['telefone'],
#                 email=self.cleaned_data['email'],
#             )
#         pessoa.save()
#         return pessoa
#
#     def cria_ordem_assinatura(self, assinante):
#         id_ordem = str(uuid.uuid4())
#         link_pagamento = settings.URL + 'pagamento/' + id_ordem
#         ordem = Ordem(id=id_ordem, assinante=assinante, link=link_pagamento, recorrente=True)
#         ordem.nome_comprador = assinante.pessoa.nome
#         ordem.start_date = datetime.now() + timedelta(days=8)
#         if self.cleaned_data['pagamento'] == '1':
#             ordem.periodo = '1'
#             ordem.valor = float(self.mensal[:-2] + '.' + self.mensal[-2::])
#         else:
#             ordem.periodo = '12'
#             ordem.valor = float(self.anual[:-2] + '.' + self.anual[-2::])
#
#         ordem.save()
#         return ordem
#
#     def envia_email(self, link_pagamento):
#         email = self.cleaned_data['email']
#         telegram = self.cleaned_data['telegram']
#         convite_grupo = bot.convite_unico(settings.TELEGRAM_GRUPO_CLUB)
#         convite_canal = bot.convite_unico(settings.TELEGRAM_CANAL_CLUB)
#         convite_app = 'https://mundstock-club.mn.co/share/EuQZZG6gks621J1I?utm_source=manual'
#         conteudo = email_club(telegram, convite_grupo, convite_canal, convite_app, link_pagamento)
#
#         mail = EmailMessage(
#             subject='Convite Mundstock Club',
#             body=conteudo,
#             from_email='Mundstock Educacional <no-reply@mundstockeducacional.com.br>',
#             to=[email, ],
#             headers={'Reply-To': 'contato@mundstockeducacional.com.br'}
#         )
#         mail.content_subtype = 'html'
#         mail.send()
#
#     def clean_telegram(self):
#         telegram = self.cleaned_data['telegram'].replace('@', '')
#         if telegram.isnumeric():
#             raise ValidationError('Por favor, utilize um nome de usuário.')
#         elif AssinanteClub.objects.filter(telegram=telegram).exists():
#             raise ValidationError('Telegram já cadastrado.')
#         return telegram
#
#     def clean_email(self):
#         email = self.cleaned_data['email']
#         try:
#             pessoa = Pessoa.objects.get(email=email)
#             if pessoa.cpf != self.cleaned_data['cpf']:
#                 raise ValidationError('E-mail já cadastrado.')
#         except Pessoa.DoesNotExist:
#             pass
#         return email
#
#     class Meta:
#         model = AssinanteClub
#         fields = ['telegram', 'aceito']


class PreCadastroClubModelForm(forms.ModelForm):
    class Meta:
        model = AssinanteClub
        fields = ['aceito']

    PARCELAS = [
        ('1', '1x (à vista)'),
        ('2', '2 vezes'),
    ]

    nome = forms.CharField(
        label='Nome', max_length=100, min_length=8,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome Completo',
            'class': 'form-control',
        }),
    )
    cpf = BRCPFField(
        label='CPF',
        widget=forms.TextInput(attrs={
            'placeholder': 'CPF', 'class': 'form-control',
            'data-mask': '000.000.000-00'
        }),
        error_messages={'invalid': 'CPF inválido.'}
    )
    email = forms.EmailField(
        label='E-mail', max_length=50, validators=[EmailValidator],
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
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
    aceito = forms.BooleanField(
        error_messages={'required': 'Você precisa aceitar os Termos e Condições.'},
        label='Aceito os Termos e Condições',
        widget=forms.CheckboxInput(attrs={'id': 'chk', 'class': 'form-check-input'})
    )

    def clean_cc_numero(self):
        return self.cleaned_data['cc_numero'].replace(' ', '')

    def salva_pessoa(self):
        try:
            pessoa = Pessoa.objects.filter(
                Q(cpf=self.cleaned_data['cpf']) | Q(email=self.cleaned_data['email'])
            )[0:1].get()
            pessoa.telefone = (self.cleaned_data['telefone'])
            pessoa.email = (self.cleaned_data['email'])
        except Pessoa.DoesNotExist:
            pessoa = Pessoa(
                nome=self.cleaned_data['nome'],
                cpf=self.cleaned_data['cpf'],
                telefone=self.cleaned_data['telefone'],
                email=self.cleaned_data['email'],
            )
        pessoa.save()
        return pessoa

    def realiza_pagamento(self, assinante, precadastro):

        # CRIA A ORDEM BASEADO NO PRECADASTRO:
        logging.info('Criando a ordem...')
        id_ordem = str(uuid.uuid4())
        link_pagamento = settings.URL + 'pagamento/' + id_ordem
        ordem = Ordem(id=id_ordem, assinante=assinante, link=link_pagamento, recorrente=True)
        ordem.nome_comprador = assinante.pessoa.nome
        ordem.authorize_now = False
        ordem.start_date = datetime.now().date() + timedelta(days=8)
        ordem.periodo = precadastro.plano
        ordem.valor = precadastro.valor

        ordem.save()
        logging.info('Ordem salva.')

        # SOLICITA PAGAMENTO NA CIELO:
        brand = bandeira(get_type(self.clean_cc_numero()))

        cartao = CreditCard(self.cleaned_data['cc_codigo'], brand)
        cartao.expiration_date = self.cleaned_data['cc_validade'].strftime('%m/%Y')
        cartao.card_number = self.clean_cc_numero()
        cartao.holder = self.cleaned_data['cc_nome'].strip()

        if ordem.recorrente and ordem.periodo == '1':
            parcelas = 1
        else:
            parcelas = self.cleaned_data['parcelas']

        status = cria_pagamento(ordem, cartao, parcelas)

        # DELETA O PRECADASTRO:
        logging.info('Deletando pré-cadastro...')
        precadastro.delete()

        return status

    def envia_convite(self, assinante):
        email = self.cleaned_data['email']
        convite_grupo = convite_unico(settings.TELEGRAM_GRUPO_CLUB)
        convite_canal = convite_unico(settings.TELEGRAM_CANAL_CLUB)
        convite_app = 'https://bit.ly/3wSz9dB'
        envia_convite(assinante.id_telegram, convite_grupo, convite_canal, convite_app)

        # conteudo = email_club(assinante.telegram, convite_grupo, convite_canal, convite_app, 'link_pagamento')
        #
        # mail = EmailMessage(
        #     subject='Convite Mundstock Club',
        #     body=conteudo,
        #     from_email='Mundstock Educacional <no-reply@mundstockeducacional.com.br>',
        #     to=[email, ],
        #     headers={'Reply-To': 'contato@mundstockeducacional.com.br'}
        # )
        # mail.content_subtype = 'html'
        # mail.send()


class ConsultoriaModelForm(forms.ModelForm):

    class Meta:
        model = ClienteConsultoria
        fields = ['mensagem', ]
        # exclude = ['nome', ]

    field_order = ('nome', 'email', 'telefone', 'mensagem', )
    # PARCELAS = [
    #     ('1', '1x (à vista)'),
    #     ('2', '2 vezes'),
    #     ('3', '3 vezes'),
    # ]
    nome = forms.CharField(
        label='Nome', max_length=100, min_length=8,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome Completo',
            'class': 'form-control',
        }),
    )
    # cpf = BRCPFField(
    #     label='CPF',
    #     widget=forms.TextInput(attrs={
    #         'placeholder': 'CPF', 'class': 'form-control',
    #         'data-mask': '000.000.000-00'
    #     }),
    #     error_messages={'invalid': 'CPF inválido.'}
    # )
    email = forms.CharField(
        label='E-mail', max_length=50, validators=[EmailValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'E-mail',
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

    mensagem = forms.CharField(
        label='Mensagem', max_length=500,
        validators=[MaxLengthValidator, ],
        widget=forms.Textarea(attrs={
            'placeholder': 'Mensagem',
            'class': 'form-control',
        }),
    )

    # def clean_cc_numero(self):
    #     return self.cleaned_data['cc_numero'].replace(' ', '')

    def salva_pessoa(self):
        try:
            pessoa = Pessoa.objects.get(email=self.cleaned_data['email'])
            # pessoa.cep = self.cleaned_data['cep']
            # pessoa.logradouro = self.cleaned_data['logradouro']
            # pessoa.numero = self.cleaned_data['numero']
            # pessoa.complemento = self.cleaned_data['complemento']
            # pessoa.bairro = self.cleaned_data['bairro']
            # pessoa.cidade = self.cleaned_data['cidade']
            # pessoa.uf = self.cleaned_data['uf']
            pessoa.telefone = self.cleaned_data['telefone']
            pessoa.email = self.cleaned_data['email']
            pessoa.save()
        except Pessoa.DoesNotExist:
            pessoa = Pessoa(
                nome=self.cleaned_data['nome'],
                # cpf=self.cleaned_data['cpf'],
                email=self.cleaned_data['email'],
                # logradouro=self.cleaned_data['logradouro'],
                # numero=self.cleaned_data['numero'],
                # complemento=self.cleaned_data['complemento'],
                # bairro=self.cleaned_data['bairro'],
                # cidade=self.cleaned_data['cidade'],
                # cep=self.cleaned_data['cep'],
                # uf=self.cleaned_data['uf'],
                telefone=self.cleaned_data['telefone'],
            )
            pessoa.save()
        return pessoa

    # @staticmethod
    # def cria_formulario(cliente_consultoria):
    #     formulario = FormularioConsultoria()
    #     id_formulario = str(uuid.uuid4())
    #     formulario.id = id_formulario
    #     formulario.cliente = cliente_consultoria
    #     formulario.save()
    #
    #     cliente_consultoria.link_formulario = f'{settings.URL}consultoria/formulario/{id_formulario}'
    #     cliente_consultoria.link_agendamento = f'{settings.URL}consultoria/agendamento/{id_formulario}'
    #     cliente_consultoria.save()

    @staticmethod
    def envia_notificacao(cliente):
        contratante = cliente.pessoa.nome
        mensagem = f'📈 <b>Consultoria</b>\n\n' \
                   f'Novo interessado:\n<b>{contratante}</b>'
        bot.enviar_notificacao(mensagem)

    # @staticmethod
    # def cria_ordem_consultoria(cliente_consultoria):
    #     servico_consultoria = Servico.objects.get(id=1)
    #     id_ordem = str(uuid.uuid4())
    #     link_pagamento = settings.URL + 'pagamento/' + id_ordem
    #     ordem = Ordem(id=id_ordem, consultoria=cliente_consultoria, link=link_pagamento)
    #     ordem.nome_comprador = cliente_consultoria.pessoa.nome
    #     ordem.valor = servico_consultoria.valor
    #     ordem.authorize_now = True
    #     ordem.save()
    #
    #     cliente_consultoria.link_formulario = f'{settings.URL}consultoria/formulario/{id_ordem}'
    #     cliente_consultoria.link_agendamento = f'{settings.URL}consultoria/agendamento/{id_ordem}'
    #     cliente_consultoria.save()
    #     return ordem
    #
    # def realiza_pagamento_consultoria(self, ordem):
    #     brand = bandeira(get_type(self.clean_cc_numero()))
    #
    #     cartao = CreditCard(self.cleaned_data['cc_codigo'], brand)
    #     cartao.expiration_date = self.cleaned_data['cc_validade'].strftime('%m/%Y')
    #     cartao.card_number = self.clean_cc_numero()
    #     cartao.holder = self.cleaned_data['cc_nome'].strip()
    #     parcelas = self.cleaned_data['parcelas']
    #
    #     status = cria_pagamento(ordem, cartao, parcelas)
    #
    #     if status in (1, 2):
    #         mensagem = 'Um novo pagamento da consultoria foi realizado. Verifique o Painel Administrativo.'
    #         bot.enviar_notificacao(mensagem)
    #
    #     return status

    # @staticmethod
    # def envia_email_formulario(ordem):
    #     email = ordem.consultoria.pessoa.email
    #
    #     conteudo = email_consultoria_formulario(ordem.consultoria.link_formulario, ordem.consultoria.link_agendamento)
    #
    #     mail = EmailMessage(
    #         subject='Formulário de Avaliação de Perfil',
    #         body=conteudo,
    #         from_email='Mundstock Educacional <no-reply@mundstockeducacional.com.br>',
    #         to=[email, ],
    #         headers={'Reply-To': 'contato@mundstockeducacional.com.br'}
    #     )
    #     mail.content_subtype = 'html'
    #     mail.send()

    # def envia_email(self, link_pagamento):
    #     email = self.cleaned_data['email']
    #     conteudo = email_consultoria(link_pagamento)
    #
    #     mail = EmailMessage(
    #         subject='Seu cadastro foi realizado.',
    #         body=conteudo,
    #         from_email='Mundstock Educacional <contato@mundstockeducacional.com.br>',
    #         to=[email, ],
    #         headers={'Reply-To': 'contato@mundstockeducacional.com.br'}
    #     )
    #     mail.content_subtype = 'html'
    #     mail.send()


class FormularioConsultoriaForm(forms.ModelForm):
    class Meta:
        model = FormularioConsultoria
        exclude = ('id', 'cliente', 'respondido',)

    # field_order = ('cpf', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf', )
    nome = forms.CharField(
        label='Nome', max_length=100, min_length=8,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome Completo',
            'class': 'form-control',
        }),
    )
    # email = forms.EmailField(
    #     label='E-mail', max_length=50, validators=[EmailValidator],
    #     widget=forms.EmailInput(attrs={
    #         'placeholder': 'E-mail',
    #         'class': 'form-control',
    #     }),
    # )
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
    cpf = BRCPFField(
        label='CPF',
        widget=forms.TextInput(attrs={
            'placeholder': 'CPF', 'class': 'form-control',
            'data-mask': '000.000.000-00',
        }),
        error_messages={'invalid': 'CPF inválido.'}
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
    IDADE = [
        ('18 a 25 anos', '18 a 25 anos'),
        ('26 a 35 anos', '26 a 35 anos'),
        ('36 a 45 anos', '36 a 45 anos'),
        ('46 a 65 anos', '46 a 65 anos'),
        ('66 anos ou mais', '66 anos ou mais'),
    ]
    idade = forms.ChoiceField(
        label='Qual a sua idade?',
        choices=IDADE,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    FORMACAO_ACADEMICA = [
        ('Ensino Fundamental', 'Ensino Fundamental'),
        ('Ensino Médio', 'Ensino Médio'),
        ('Ensino Superior', 'Ensino Superior'),
        ('Pós Graduação, Mestrado ou Doutorado', 'Pós Graduação, Mestrado ou Doutorado'),
    ]
    formacao_academica = forms.ChoiceField(
        label='Qual é sua formação academica?',
        choices=FORMACAO_ACADEMICA,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'}),
    )

    CONHECIMENTO_INVESTIMENTO = [
        ('Não tenho conhecimento', 'Não tenho conhecimento'),
        ('Razoável', 'Razoável'),
        ('Bom', 'Bom'),
        ('Excelente', 'Excelente'),
    ]
    conhecimento_investimento = forms.ChoiceField(
        label='Como você avalia seu conhecimento sobre investimento?',
        choices=CONHECIMENTO_INVESTIMENTO,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    CONHECIMENTO_ECONOMIA = [
        ('Não tenho conhecimento', 'Não tenho conhecimento'),
        ('Razoável', 'Razoável'),
        ('Bom', 'Bom'),
        ('Excelente', 'Excelente'),
    ]
    conhecimento_economia = forms.ChoiceField(
        label='Como você avalia seu conhecimento sobre economia?',
        choices=CONHECIMENTO_ECONOMIA,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    INVESTIMENTOS = [
        ('Nunca investi', 'Nunca investi'),
        ('Poupança', 'Poupança'),
        ('Títulos de Renda Fixa', 'Títulos de Renda Fixa'),
        ('Tesouro Direto', 'Tesouro Direto'),
        ('Previdência Complementar', 'Previdência Complementar'),
        ('Fundos de Investimento', 'Fundos de Investimento'),
        ('Fundos Imobiliários', 'Fundos Imobiliários'),
        ('Ações', 'Ações'),
        ('Derivativos', 'Derivativos'),
        ('Investimentos no Exterior', 'Investimentos no Exterior'),
        ('Criptomoedas', 'Criptomoedas'),
    ]
    investimentos = forms.MultipleChoiceField(
        label='Selecione abaixo todos os investimentos que você já possuiu no passado ou que possui atualmente:',
        choices=INVESTIMENTOS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'radiobox'})
    )

    EXPECTATIVA = [
        ('Rentabilizar de 2% a 5%', 'Rentabilizar de 2% a 5%'),
        ('Rentabilizar de 5% a 10%', 'Rentabilizar de 5% a 10%'),
        ('Rentabilizar mais de 10%', 'Rentabilizar mais de 10%'),
    ]
    expectativa = forms.ChoiceField(
        label='Quanto você gostaria de rentabilizar seus investimentos no ano?',
        choices=EXPECTATIVA,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    BENCHMARK = [
        ('Inflação', 'Inflação'),
        ('Selic', 'Selic'),
        ('CDI', 'CDI'),
        ('Ibovespa', 'Ibovespa'),
        ('S&P 500', 'S&P 500'),
        ('Não sei', 'Não sei'),
    ]
    benchmark = forms.ChoiceField(
        label='Você deseja que seus investimentos tenham como referência de rentabilidade qual dos seguintes indicadores (benchmark)?',
        choices=BENCHMARK,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    OBJETIVO = [
        (
            'Preservação de Capital: desejo minimizar os riscos e manter o meu poder de compra ao rentabilizar meu patrimônio à mesma taxa da inflação',
            'Preservação de Capital: desejo minimizar os riscos e manter o meu poder de compra ao rentabilizar meu patrimônio à mesma taxa da inflação'
        ),
        (
            'Acumulação de Patrimônio: desejo diversificar os riscos e investir de modo a tentar rentabilizar o meu capital a uma taxa maior que a inflação',
            'Acumulação de Patrimônio: desejo diversificar os riscos e investir de modo a tentar rentabilizar o meu capital a uma taxa maior que a inflação'
        ),
        (
            'Construção de Renda: desejo que meus investimentos gerem renda futura a partir de uma carteira que receba rendimentos (por exemplo: dividendos) recorrentes',
            'Construção de Renda: desejo que meus investimentos gerem renda futura a partir de uma carteira que receba rendimentos (por exemplo: dividendos) recorrentes'
        ),
        (
            'Especulação: desejo correr maiores riscos para ter maior potencial de valorização dos meus recursos',
            'Especulação: desejo correr maiores riscos para ter maior potencial de valorização dos meus recursos'
        ),
    ]
    objetivo = forms.ChoiceField(
        label='Qual é o seu objetivo ao investir?',
        choices=OBJETIVO,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    TEMPO = [
        ('Curto Prazo: menos de 1 ano', 'Curto Prazo: menos de 1 ano'),
        ('Médio Prazo: entre 1 e 3 anos', 'Médio Prazo: entre 1 e 3 anos'),
        ('Médio-Longo Prazo: entre 3 e 5 anos', 'Médio-Longo Prazo: entre 3 e 5 anos'),
        ('Longo Prazo: acima de 5 anos', 'Longo Prazo: acima de 5 anos'),
    ]
    tempo = forms.ChoiceField(
        label='Por quanto tempo você deseja manter os seus investimentos?',
        choices=TEMPO,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    UTILIZAR_RECURSOS = [
        (
            'Posso precisar do dinheiro a qualquer momento',
            'Posso precisar do dinheiro a qualquer momento'
        ),
        (
            'Posso precisar nos próximos 6 meses',
            'Posso precisar nos próximos 6 meses'
        ),
        (
            'Posso precisar nos próximos 12 meses',
            'Posso precisar nos próximos 12 meses'
        ),
        (
            'Não tenho necessidade de utilizar os recursos',
            'Não tenho necessidade de utilizar os recursos'
        )
    ]
    recursos = forms.ChoiceField(
        label='Sobre os recursos que você pretende investir, quando você pretende utilizá-los?',
        choices=UTILIZAR_RECURSOS,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    TIPOS_GESTAO = [
        (
            'Gestão Ativa: mudar os meus investimentos frequentemente para superar a rentabilidade média do mercado',
            'Gestão Ativa: mudar os meus investimentos frequentemente para superar a rentabilidade média do mercado'
        ),
        (
            'Gestão Passiva: não pretendo mudar meus investimentos com frequência',
            'Gestão Passiva: não pretendo mudar meus investimentos com frequência'
        ),
    ]
    tipo_gestao = forms.ChoiceField(
        label='Qual o tipo de gestão de patrimônio que você considera ideal?',
        choices=TIPOS_GESTAO,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    TOLERANCIA = [
        (
            'Não gosto de correr riscos (baixa tolerância ao risco)',
            'Não gosto de correr riscos (baixa tolerância ao risco)',
        ),
        (
            'Estou disposto a correr poucos riscos (média tolerância ao risco)',
            'Estou disposto a correr poucos riscos (média tolerância ao risco)',
        ),
        (
            'Estou disposto a assumir riscos elevados (alta tolerância ao risco)',
            'Estou disposto a assumir riscos elevados (alta tolerância ao risco)',
        ),
    ]
    tolerancia = forms.ChoiceField(
        label='Qual opção melhor descreve a sua tolerância ao risco?',
        choices=TOLERANCIA,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    ACOES_CAINDO = [
        ('Venderia imediatamente', 'Venderia imediatamente'),
        ('Venderia uma parte das minhas ações', 'Venderia uma parte das minhas ações'),
        ('Não faria nada', 'Não faria nada'),
        ('Compraria mais ações', 'Compraria mais ações'),
    ]
    acoes_caindo = forms.ChoiceField(
        label='Você possui ações na sua cartira de investimentos e por algum motivo o mercado brasileiro despenca -30% e as suas ações acompanham esse movimento. Nesse caso o que você faria?',
        choices=ACOES_CAINDO,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    OPINIAO_DIVERSIFICACAO = [
        ('Acho muito importante diversificar, para reduzir riscos', 'Acho muito importante diversificar, para reduzir riscos'),
        ('Acho importante diversificar, mas nem sempre', 'Acho importante diversificar, mas nem sempre'),
        ('Acho desnecessário diversificar', 'Acho desnecessário diversificar'),
    ]
    opiniao_diversificacao = forms.ChoiceField(
        label='Qual a sua opinião em relação a diversificação de investimentos?',
        choices=OPINIAO_DIVERSIFICACAO,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    RESERVA_EMERGENCIA = [
        ('Sim', 'Sim'),
        ('Não', 'Não'),
        ('Não vejo necessidade', 'Não vejo necessidade'),
    ]
    reserva_emergencia = forms.ChoiceField(
        label='Você tem uma reserva de emergência?',
        choices=RESERVA_EMERGENCIA,
        widget=forms.RadioSelect(attrs={'class': 'radiobox'})
    )

    corretora = forms.CharField(
        label='Qual corretora de investimentos você tem preferência para investir?',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    # aceito = forms.BooleanField(
    #     error_messages={'required': 'Você precisa aceitar o Contrato, Termos e Condições.'},
    #     label='Aceito os Termos e Condições',
    #     widget=forms.CheckboxInput(attrs={'id': 'chk', 'class': 'form-check-input'})
    # )

    def salva_pessoa(self, pessoa):
        # pessoa = Pessoa.objects.get(cpf=self.cleaned_data['email'])
        pessoa.nome = self.cleaned_data['nome']
        pessoa.cpf = self.cleaned_data['cpf']
        pessoa.cep = self.cleaned_data['cep']
        pessoa.logradouro = self.cleaned_data['logradouro']
        pessoa.numero = self.cleaned_data['numero']
        pessoa.complemento = self.cleaned_data['complemento']
        pessoa.bairro = self.cleaned_data['bairro']
        pessoa.cidade = self.cleaned_data['cidade']
        pessoa.uf = self.cleaned_data['uf']
        pessoa.telefone = self.cleaned_data['telefone']
        pessoa.save()

    def aceita_contrato(self, cliente):
        cliente.aceito = self.cleaned_data['aceito']
        cliente.save()

    @staticmethod
    def envia_notificacao(cliente):
        contratante = cliente.pessoa.nome
        mensagem = f'📈 <b>Consultoria</b>\n\n' \
                   f'Novo formulário disponível para análise:\n<b>{contratante}</b>'
        bot.enviar_notificacao(mensagem)


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['aceito', ]

    PARCELAS = [
        ('1', '1x (à vista)'),
        ('2', '2 vezes (sem juros)'),
        ('3', '3 vezes (sem juros)'),
        ('4', '4 vezes (sem juros)'),
        ('5', '5 vezes (sem juros)'),
        ('6', '6 vezes (sem juros)'),
    ]
    nome = forms.CharField(
        label='Nome', max_length=100, min_length=8,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome Completo',
            'class': 'form-control',
        }),
    )
    cpf = BRCPFField(
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CPF',
            'data-mask': '000.000.000-00',
        }),
        error_messages={'invalid': 'CPF inválido.'}
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
    email = forms.EmailField(
        label='E-mail',
        max_length=50,
        min_length=5,
        validators=[MinLengthValidator, MaxLengthValidator],
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
            'class': 'form-control',
        }),
    )
    cc_nome = forms.CharField(
        label='Nome do Cartão',
        max_length=50,
        min_length=8,
        validators=[MinLengthValidator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Nome (Idêntico ao Cartão)',
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
    aceito = forms.BooleanField(
        error_messages={'required': 'Você precisa aceitar os Termos e Condições.'},
        label='Aceito os Termos e Condições',
        widget=forms.CheckboxInput(attrs={'id': 'chk', 'class': 'form-check-input'})
    )

    def clean_cc_numero(self):
        return self.cleaned_data['cc_numero'].replace(' ', '')

    def salva_pessoa(self):
        try:
            pessoa = Pessoa.objects.filter(
                Q(cpf=self.cleaned_data['cpf']) | Q(email=self.cleaned_data['email'])
            )[0:1].get()
            pessoa.telefone = (self.cleaned_data['telefone'])
            pessoa.email = (self.cleaned_data['email'])
        except Pessoa.DoesNotExist:
            pessoa = Pessoa(
                nome=self.cleaned_data['nome'],
                cpf=self.cleaned_data['cpf'],
                telefone=self.cleaned_data['telefone'],
                email=self.cleaned_data['email'],
            )
        pessoa.save()
        return pessoa

    def paga_curso(self, curso):
        id_ordem = str(uuid.uuid4())
        link_pagamento = settings.URL + 'pagamento/' + id_ordem
        ordem = Ordem(id=id_ordem, nome_comprador=self.cleaned_data['nome'], link=link_pagamento, )
        ordem.valor = curso.valor - curso.desconto
        ordem.matricula = self.instance
        ordem.recorrente = False
        ordem.authorize_now = True
        ordem.save()

        brand = bandeira(get_type(self.clean_cc_numero()))

        cartao = CreditCard(self.cleaned_data['cc_codigo'], brand)
        cartao.expiration_date = self.cleaned_data['cc_validade'].strftime('%m/%Y')
        cartao.card_number = self.clean_cc_numero()
        cartao.holder = self.cleaned_data['cc_nome'].strip()
        parcelas = self.cleaned_data['parcelas']

        status = cria_pagamento(ordem, cartao, parcelas)

        if status in (1, 2):
            mensagem = f"Um novo aluno se matriculou no curso:\n<b>{ordem.nome_comprador}</b>"
            bot.enviar_notificacao(mensagem)

        if status == 3:
            raise RefusedPaymentError()

        return status

    def enviar_email(self):
        email = self.cleaned_data['email']
        convite_canal_alunos = bot.convite_unico(settings.TELEGRAM_CANAL_ALUNOS)
        convite_app = ''
        conteudo = """
        <p><b>Bem-vindo (a) ao Curso de Economia: do Básico aos Ciclos Econômicos!</b></p>
        <p>Os links abaixo dão acesso a dois ambientes, o grupo no <b>Telegram</b> e a plataforma de aulas da 
        <b>Mighty Networks</b>. Dentro do grupo no Telegram os alunos poderão interagir com o professor 
        e é onde receberão notificações relevantes, como os links de acesso às aulas ao vivo no Zoom.</p>
        <p>Todas as aulas, após concluídas, ficarão disponíveis dentro da plataforma da Mighty Networks para 
        você assistir novamente quando quiser. Essa plataforma pode ser acessada tanto pelo computador 
        como por aplicativo no celular.</p>
        <p><b>Link Telegram:</b> <a href="%s">%s</a></p>
        <p><b>Link Mighty Networks:</b> <a href="https://curso-de-economia-para-investidores.mn.co/share/SYBzGAa33L7QCQZc?utm_source=manual">https://curso-de-economia-para-investidores.mn.co/share/SYBzGAa33L7QCQZc?utm_source=manual</a></p>
        <p><b>Link do APP Mighty Networks para Android:</b> <a href="https://play.google.com/store/apps/details?id=com.mightybell.mb&hl=pt_BR&gl=US">Clique aqui.</a></p>
        <p><b>Link do APP Mighty Networks para IOS:</b> <a href="https://apps.apple.com/us/app/mighty-networks/id1081683081">Clique aqui.</a></p>
        <p>Muito obrigado,</p>
        <p>Igor George Mazzei Mundstock</p>
        """ % (convite_canal_alunos, convite_canal_alunos)

        mail = EmailMessage(
            subject='Bem vindo ao Curso!',
            body=conteudo,
            from_email='Mundstock Educacional <no-reply@mundstockeducacional.com.br>',
            to=[email, ],
            headers={'Reply-To': 'contato@mundstockeducacional.com.br'}
        )
        mail.content_subtype = 'html'
        mail.send()


