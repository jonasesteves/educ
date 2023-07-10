from django.core.management import BaseCommand

from bot.management.commands.bot import enviar_ao_insights, enviar_foto_ao_insights


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **kwargs):

        caption = f"<b>Curso de Economia: do Básico aos Ciclos Econômicos</b>\n" \
                   f"\nAs inscrições já estão abertas para o meu curso de economia! O objetivo do curso é " \
                   f"ensinar os alunos como as economias funcionam e como os ciclos econômicos podem afetar " \
                   f"os seus investimentos. São mais de 40h de conteúdo para investidores e especuladores.\n" \
                   f"\n<b>O curso foi dividido em 4 módulos (cronograma completo no " \
                   f"<a href='https://mundstockeducacional.com.br/curso/economia-para-investidores'>site</a>):</b>\n" \
                   f"✅ Módulo 1 - Introdução à Microeconomia\n" \
                   f"✅ Módulo 2 - Dominando a Macroeconomia\n" \
                   f"✅ Módulo 3 - Macroeconomia II (Tópicos Avançados)\n" \
                   f"✅ Módulo 4 - Ciclos, Crises e Investimentos\n" \
                   f"\nSerão 14 aulas ao vivo, às terças e quintas às 19h, e todo o conteúdo ficará disponível " \
                   f"dentro da plataforma por 12 meses para os alunos assistirem quando quiserem.\n" \
                   f"\nPara mais informações acesse o nosso site: " \
                   f"https://mundstockeducacional.com.br/curso/economia-para-investidores"

        enviar_foto_ao_insights('curso.jpg', caption=caption)
