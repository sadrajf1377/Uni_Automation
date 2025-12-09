from django.urls import path

from .views import My_Tickets_List,Create_New_Ticket,Ticket_Messages,Mark_Response_As_Read,Write_Message,Users_Tickets,UnResponded_Messages,Responde_To_A_Message

urlpatterns=[
    path('my_tickets',My_Tickets_List.as_view(),name='my_tickets'),
    path('create_ticket',Create_New_Ticket.as_view(),name='create_new_ticket'),
    path('ticket_message/<ticket_id>',Ticket_Messages.as_view(),name='ticket_messages'),
    path('write_ticket_message',Write_Message.as_view(),name='write_ticket_message'),
    path('mark_as_read/',Mark_Response_As_Read.as_view(),name='mark_response_as_read'),
    path('users_tickets',Users_Tickets.as_view(),name='users_tickets'),
    path('unresponed_messages',UnResponded_Messages.as_view(),name='unresponded_messages'),
    path('respond_to_a_message',Responde_To_A_Message.as_view(),name='respond_to_messages')
]