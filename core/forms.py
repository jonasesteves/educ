from django import forms
from django.core.mail.message import EmailMessage


class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=50)
    email = forms.CharField(label='E-mail', max_length=50)
    assunto = forms.CharField(label='Assunto', max_length=50)
    mensagem = forms.CharField(label='Mensagem', widget=forms.Textarea())

    def envia_email(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        assunto = self.cleaned_data['assunto']
        mensagem = self.cleaned_data['mensagem']

        conteudo = f'Mensagem do site enviada por {nome}:\n{mensagem}'

        mail = EmailMessage(
            subject='Mensagem do Site: ' + assunto,
            body=conteudo,
            from_email='Mensagem do Site <contato@mundstockeducacional.com.br>',
            to=('contato@mundstockeducacional.com.br',),
            headers={'Reply-To': email}
        )
        mail.send()


# class NewsletterForm(forms.Form):
#     email = forms.EmailField(label='E-mail')
#     captcha = ''


