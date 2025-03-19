import logging
from rest_framework import status # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import attachmentSerializer
from ..users.models import User


#  Create the looger instance for the requests module
loger = logging.getLogger('requests')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachments(request):
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        loger.error('Refresh token is required.')
        return Response(
            {
                'message': 'Refresh token is required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        token = RefreshToken(refresh_token)
        user = User.objects.get(id=token['user_id'])
    except Exception as e:
        pass