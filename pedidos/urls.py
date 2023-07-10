from django.urls import path

from pedidos.views import OrdemView, ProdutosView

app_name = 'pedidos'

urlpatterns = [
    path('produtos/<str:produto>/', OrdemView.as_view(), name='ordem'),
    path('produtos/', ProdutosView.as_view(), name='produtos'),
]
