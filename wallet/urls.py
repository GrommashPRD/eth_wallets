from django.urls import path

from . import views


urlpatterns = [
    path('api/v1/wallets/', views.WalletViewSet.as_view(), name="wallets"),
    path('api/v1/transactions/', views.TransactionView.as_view(), name="transactions"),
]
