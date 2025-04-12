from django.urls import path, include

from . import views


urlpatterns = [
    path('api/v1/wallets/', views.WalletCreateView.as_view(), name="wallets"),
    path('api/v1/transactions/', views.WalletTransactionsView.as_view(), name="transactions"),
]
