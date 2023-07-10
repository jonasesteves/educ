from django.urls import path
from financeiro.views import PagamentoView, payment_webhook

app_name = 'financeiro'

urlpatterns = [
    path('pagamento-cielo', payment_webhook, name='pagamento-cielo'),
    path('pagamento/<str:id>', PagamentoView.as_view(), name='pagamento'),
]
