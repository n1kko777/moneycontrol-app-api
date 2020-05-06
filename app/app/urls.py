from django.conf import settings
from django.conf.urls.static import static
from rest_auth.registration.views import VerifyEmailView, RegisterView

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='MoneyControl API')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('rest-auth/registration/',
         RegisterView.as_view(), name='account_signup'),
    re_path(r'^rest-auth/registration/account-confirm-email/',
            VerifyEmailView.as_view(),
            name='account_email_verification_sent'),
    re_path(
        r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        VerifyEmailView.as_view(),
        name='account_confirm_email'),
    path('', include('django.contrib.auth.urls')),
    path('api/v1/', include('core.urls', namespace='api')),
    path('', schema_view),
    path('api-auth/', include('rest_framework.urls',
                              namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
