from django.db import models
from django.conf import settings


class Attachment(models.Model):
    """
    Attachment model represents a file uploaded by a user.
    Attributes:
        user (ForeignKey): A reference to the user who uploaded the file. 
            It is linked to the AUTH_USER_MODEL and deletes the attachment 
            if the user is deleted.
        file (FileField): The uploaded file stored in the 'attachments/' directory.
        uploaded_at (DateTimeField): The timestamp indicating when the file was uploaded.
    Methods:
        __str__(): Returns a string representation of the attachment in the 
            format "user - file name".
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {}".format(self.user, self.file.name)

