from django.urls import path
from . import views

app_name = 'items'
urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('hot/', views.hot_items, name='hot_items'),
    path('create/', views.item_create, name='item_create'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/review/', views.leave_review, name='leave_review'),
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/reply/', views.reply_message, name='message_reply'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/buy/', views.buy_item, name='buy_item'),
    path('order/<int:pk>/ship/', views.order_ship, name='order_ship'),
    path('order/<int:pk>/offline/', views.order_offline, name='order_offline'),
    path('order/<int:pk>/confirm/', views.order_confirm, name='order_confirm'),
    path('order/<int:pk>/cancel/', views.order_cancel, name='order_cancel'),
    path('order/<int:pk>/refund/', views.order_refund_request, name='order_refund_request'),
    path('order/<int:pk>/refund-approve/', views.order_refund_approve, name='order_refund_approve'),
]
