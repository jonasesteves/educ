from django.core.management import BaseCommand

from bot.management.commands.bot import enviar_notificacao
from gestao.models import AssinanteClub


class Command(BaseCommand):
    help = 'Coleta assinaturas atrasadas'

    def handle(self, *args, **kwargs):
        assinaturas = AssinanteClub.objects.filter(ativo=True)
        atrasadas = [assinatura for assinatura in assinaturas if assinatura.atraso]
        if atrasadas:
            mensagem = 'O seguintes assinantes do Club estão com pagamento atrasado:\n'
            for atrasada in atrasadas:
                mensagem += f'\n@{atrasada.telegram} ({atrasada.pessoa.email})\n'
            enviar_notificacao(mensagem)
