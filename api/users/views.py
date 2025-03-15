import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User

# Create the looger instance for the celery tasks
loger = logging.getLogger('requests')


@api_view(['POST'])
def sginup(request):
    serializer = UserSerializer(data=request.data)
    if User.objects.filter(email=request.data['email']).exists():
        # Log the error message
        loger.error('User already exists.')
        return Response(
            {
                'message': 'User already exists.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                'message': 'User created successfully.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    else:
        # Log the error message
        loger.error('User creation failed: {}.'.format(serializer.errors))
        return Response(
            {
                'message': 'User creation failed.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
