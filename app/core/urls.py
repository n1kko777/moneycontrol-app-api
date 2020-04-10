from django.urls import path, include
from rest_framework import routers

from . import views


app_name = 'core'

router = routers.DefaultRouter()
router.register("tag", views.TagViewSet)
router.register("action", views.ActionViewSet)
router.register("category", views.CategoryViewSet)
router.register("transfer", views.TransferViewSet)
router.register("profile", views.ProfileViewSet)
router.register("account", views.AccountViewSet)
router.register("company", views.CompanyViewSet)
router.register("transaction", views.TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
