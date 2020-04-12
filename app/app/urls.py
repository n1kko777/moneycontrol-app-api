from django.contrib import admin
from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='MoneyControl API')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    # enables reset_password, you can see reset email in logs
    path('', include('django.contrib.auth.urls')),
    path('api/v1/', include('core.urls', namespace='api')),
    path('', schema_view),
    path('api-auth/', include('rest_framework.urls', \
                              namespace='rest_framework')),
]
