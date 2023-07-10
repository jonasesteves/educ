from django.urls import path

from gestao.views import *

app_name = 'gestao'

urlpatterns = [
    path('club/', ClubView.as_view(), name='club'),
    path('club/termos-e-condicoes', TermosClubView.as_view(), name='club/termos-e-condicoes'),
    # path('cursos/<int:id>/formulario/', MatriculaAlunoView.as_view(), name='formulario'),
    path('pagamento-club/<str:id>', PreCadastroClubView.as_view(), name='pagamento-club'),
    path('consultoria/', ConsultoriaView.as_view(), name='consultoria'),
    path('consultoria/termos-e-condicoes', TermosConsultoriaView.as_view(), name='termos-consultoria'),
    # path('consultoria/formulario/<str:id>', FormularioConsultoriaView.as_view(), name='consultoria-formulario'),
    path('consultoria/formulario/<str:pk>', FormularioConsultoriaUpdateView.as_view(), name='consultoria-formulario'),
    path('consultoria/agendamento/<str:pk>', AgendamentoConsultoriaView.as_view(), name='consultoria-agendamento'),
    path('consultoria/agendamento/confirmacao/', ConfirmAgendamentoConsultoriaView.as_view(), name='confirmacao'),
    path('curso/<int:pk>/matricula', MatriculaView.as_view(), name='matricula'),
]
