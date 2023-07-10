import json

from django.test import TestCase
from pytz import timezone
import datetime
# Create your tests here.



# print(datetime.datetime.now(tz=timezone('America/Sao_Paulo')).strftime("%Y-%m-%d %H:%M:%S"))
# print(datetime.datetime.now(tz=timezone('America/Sao_Paulo')).strftime('%Y'))
#
# print(datetime.datetime.strptime('2021-04-15T10:35:36.000-04:00', "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S"))
# print(datetime.datetime.strptime('2021-04-15T10:35:36.000-04:00', "%Y-%m-%dT%H:%M:%S.000%z").isoformat())
# print(datetime.datetime.strptime('2021-04-15T10:35:36.000-04:00', "%Y-%m-%dT%H:%M:%S.%f%z"))

# data = (datetime.datetime.now(tz=timezone('America/Sao_Paulo')) + datetime.timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S.000%z')
# print(datetime.datetime.now().strftime('%Y-%m-%d'))

# data = datetime.datetime.strptime('01/25', '%m/%y').date()
# print(data.strftime('%m/%Y'))

# valor = '39990'
# # print(float(valor[:-2] + '.' + valor[-2::]))
# print(valor[:-2] + '.' + valor[-2::])
# if len(valor) < 3:
#    print('0' + (valor[:-2] + '.' + valor[-2::]))

# valor = 39.9
# valor_str = str(valor).replace('.', '')
# if str(valor)[::-1].find('.') == 1:
#     valor_str += '0'
# print(valor_str)

# d = {
#     'k1': 'v1',
#     'k2': 'v2',
#     'k3': {
#         'k3k1': 'k3v1',
#     },
# }
# x = '{ "name":"John", "age":30, "city":{"nome": "cidade", "estado":"est"} }'
# j = json.loads(x)
# print(j.json())
# print(json.dumps(j, indent=4))
#
# # print(d[1])
# if 'nome' in j['city']:
#     print(j['city'])

# print(x.json())

# frase = 'Uma frase qualquer escrita por Jonas Esteves'
# print(frase[:30])


# from financeiro.models import (Ordem, Pagamento)
# pagamentos = Pagamento.objects.filter(ordem='bd500025-784d-49bc-8ccc-76315439f9ab', pago=True)
# pagamentos
# ordem = Ordem.objects.filter(pagamentos__in=pagamentos)

# valor = '@123'
#
# print(f'num: {valor.isnumeric()}')
# print(f'alfanum:  {valor.isalnum()}')
# print(f'alfabetic: {valor.isalpha()}')
# print(f'digit: {valor.isdigit()}')

