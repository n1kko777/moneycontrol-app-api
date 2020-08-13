from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404
from allauth.account.admin import EmailAddress
from allauth.account.utils import send_email_confirmation
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

User = get_user_model()


class NewEmailConfirmation(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = get_object_or_404(User, email=request.data['email'])
        emailAddress = EmailAddress.objects.filter(
            user=user, verified=True).exists()

        if emailAddress:
            return Response(
                {
                    'message': 'Это Email уже проверен'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            try:
                send_email_confirmation(request, user=user)
                return Response(
                    {
                        'message':
                        'Отправлено подтверждение по электронной почте'
                    },
                    status=status.HTTP_201_CREATED
                )
            except APIException:
                return Response(
                    {
                        'message':
                        'Этот адрес электронной почты не существует, \
                            пожалуйста, создайте новую учетную запись'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
