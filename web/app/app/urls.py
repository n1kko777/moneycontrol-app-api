from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import include, url
from django.views.generic import TemplateView, RedirectView

from rest_framework_swagger.views import get_swagger_view

from .views import NewEmailConfirmation
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^favicon\.ico$', RedirectView.as_view(
        url='/static/images/favicon.ico'), name='favicon'),
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    url(r'^privacy/$', TemplateView.as_view(template_name="privacy.html"),
        name='privacy'),
    url(r'^user-manual/$', TemplateView.as_view(template_name="user-manual.html"),
        name='user-manual'),
    url(r'^signup/$', TemplateView.as_view(template_name="signup.html"),
        name='signup'),
    url(r'^email-verification/$',
        TemplateView.as_view(template_name="email_verification.html"),
        name='email-verification'),
    url(r'^login/$', TemplateView.as_view(template_name="login.html"),
        name='login'),
    url(r'^logout/$', TemplateView.as_view(template_name="logout.html"),
        name='logout'),

    url(
        r'^reverify-email/$',
        TemplateView.as_view(
            template_name="resend_verification_email.html"
        ),
        name='reverify-email'
    ),

    url(r'^password-reset/$',
        TemplateView.as_view(template_name="password_reset.html"),
        name='password-reset'),
    url(r'^password-reset/confirm/$',
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name='password-reset-confirm'),

    url(r'^user-details/$',
        TemplateView.as_view(template_name="user_details.html"),
        name='user-details'),
    url(r'^password-change/$',
        TemplateView.as_view(template_name="password_change.html"),
        name='password-change'),


    # this url is used to generate email content
    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        TemplateView.as_view(template_name="password_reset_confirm.html"),
        name='password_reset_confirm'),

    url(r'^api/v1/', include('core.urls', namespace='api')),
    url(r'^verify-email/$', NewEmailConfirmation.as_view(),
        name='resend-email-confirmation'),
    url(r'^dj-rest-auth/', include('dj_rest_auth.urls')),
    url(r'^dj-rest-auth/registration/',
        include('dj_rest_auth.registration.urls')),
    url(r'^account/', include('allauth.urls')),

    url(r'^accounts/login/$', RedirectView.as_view(url='/',
                                                   permanent=True),
        name='profile-login'),

    url(r'^docs/$', get_swagger_view(title='API Docs'), name='api_docs'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# to have images urls in dev. in prod we don't need this, because of nginx
