import logging
from rest_framework import status # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from .serializers import MultiFileUploadSerializer, AttachmentSerializer
from .models import Attachment

#  Create the looger instance for the requests module
loger = logging.getLogger('requests')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_attachments(request):
    """
    Handles the upload of multiple file attachments.
    This view allows authenticated users to upload up to three files at a time.
    It validates the uploaded files using a serializer, creates attachment
    instances for each file, and associates them with the authenticated user.
    Args:
        request (HttpRequest): The HTTP request object containing the uploaded
        files and user information.
    Returns:
        Response: A DRF Response object containing a success message and the
        serialized data of the uploaded attachments if the operation is
        successful. If the file limit is exceeded or the data is invalid, it
        returns an error message with a 400 status code.
    Raises:
        None
    Notes:
        - The maximum number of files allowed per request is 3.
        - Each file is associated with the authenticated user and given a
          default status of 'pending'.
    """

    files = request.FILES.getlist("files")

    if len(files) > 3:
        return Response(
            {
                "message": "Maximum file limit exceeded. Only 3 files are allowed."
            }
            , status=status.HTTP_400_BAD_REQUEST
        )

    serializer = MultiFileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        loger.error("Invalid file upload data.")
        return Response(
            {
                'message': 'Invalid file upload data.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    files = serializer.validated_data['files']  # Get the list of validated files from the serializer
    user = request.user  # Get the authenticated user
    attachments = []

    for file in files: # Iterate over the list of files
        # Create an attachment instance for each file
        attachment_instance = Attachment.objects.create(
            user=user,  # Associate the attachment with the authenticated user
            file=file,
            status='pending'  # Default status
        )
        attachments.append(attachment_instance)

    # Serialize the list of attachment instances
    response_serializer = AttachmentSerializer(attachments, many=True)
    return Response(
        {
            'message': 'Files uploaded successfully.',
            'data': response_serializer.data
        },
        status=status.HTTP_201_CREATED
    )
