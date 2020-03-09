from django.urls import path, include
from rest_framework import routers

from . import views


app_name = 'core'

router = routers.DefaultRouter()
router.register("Tag", views.TagViewSet)
router.register("Action", views.ActionViewSet)
router.register("Category", views.CategoryViewSet)
router.register("Transfer", views.TransferViewSet)
router.register("Profile", views.ProfileViewSet)
router.register("Account", views.AccountViewSet)
router.register("Company", views.CompanyViewSet)
router.register("Transaction", views.TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
