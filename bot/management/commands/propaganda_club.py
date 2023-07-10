from django.core.management import BaseCommand

from bot.management.commands.bot import enviar_ao_insights


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):

        mensagem = f"<b>🚀 Faça parte dos Membros do YouTube!</b>\n" \
                   f"\nInscreva-se na comunidade de membros do YouTube e tenha acesso a vídeos " \
                   f"exclusivos e lives semanais.\n" \
                   f"\n<b>Estão disponíveis 2 planos de assinatura:</b>\n\n" \
                   f"🟢 <b>Análise Macro: </b>para investidores que desejam estar por dentro do que acontece " \
                   f"de relevante no cenário macroeconômico global.\n\n" \
                   f"🟢 <b>Análise Macro + Investimentos: </b>para investidores que, além de interessados em " \
                   f"macroeconomia, desejam aprender sobre investimentos em ações, " \
                   f"<i>stocks</i>, FII's, fundos de investimentos e <i>commodities</i>.\n" \
                   f"\nOs membros recebem semanalmente vídeos e notificações sobre mercados e " \
                   f"investimentos e todas as quartas-feiras, às 19h, realizamos uma live exclusiva para debater " \
                   f"cenário macro e oportunidades de investimento.\n" \
                   f"\nPara mais informações, " \
                   f"<a href='https://www.youtube.com/channel/UCSieFtb-DCmhsLhWaRssngQ/join'>clique aqui</a>"

        enviar_ao_insights(mensagem, disable_web_page_preview=True)
