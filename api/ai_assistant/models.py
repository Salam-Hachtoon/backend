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


class Summary(models.Model):
    """
    Summary Model
    Represents a summary created by a user. Each summary is associated with a user and optionally 
    an attachment. It contains the content of the summary and the timestamp of when it was created.
    Attributes:
        user (ForeignKey): A reference to the user who created the summary. Deletes the summary if 
            the user is deleted.
        attachment (ForeignKey): An optional reference to an attachment associated with the summary. 
            If the attachment is deleted, the reference is set to NULL.
        content (TextField): The main content of the summary.
        created_at (DateTimeField): The timestamp when the summary was created. Automatically set 
            when the summary is created.
    Methods:
        __str__(): Returns a string representation of the summary in the format "user - created_at".
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='summaries')
    attachment = models.ForeignKey(Attachment, on_delete=models.SET_NULL, null=True, blank=True, related_name='summaries')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{} - {}".format(self.user, self.created_at)


class FlashCard(models.Model):
    """
    FlashCard model represents a flashcard entity that is associated with a Summary.
    Each flashcard contains a term and its corresponding definition.
    Attributes:
        summary (ForeignKey): A reference to the associated Summary object. Deleting
            the Summary will cascade and delete the related flashcards.
        term (CharField): The term or keyword of the flashcard, limited to 255 characters.
        definition (TextField): The detailed explanation or definition of the term.
    Methods:
        __str__(): Returns the string representation of the flashcard, which is the term.
    """

    summary = models.ForeignKey(Summary, on_delete=models.CASCADE, related_name='flashcards')
    term = models.CharField(max_length=255)
    definition = models.TextField()
    
    def __str__(self):
        return self.term


class Quiz(models.Model):
    """
    Represents a Quiz model associated with a user and a summary.
    Attributes:
        DIFFICULTY_CHOICES (list of tuple): Choices for the difficulty level of the quiz.
            - 'easy': Easy difficulty.
            - 'medium': Medium difficulty.
            - 'hard': Hard difficulty.
        user (ForeignKey): A foreign key to the user who owns the quiz.
        summary (ForeignKey): A foreign key to the summary associated with the quiz.
        difficulty (CharField): The difficulty level of the quiz. Must be one of the DIFFICULTY_CHOICES.
        created_at (DateTimeField): The timestamp when the quiz was created.
    Methods:
        __str__(): Returns a string representation of the quiz, including its ID and difficulty level.
    """

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quizzes')
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE, related_name='quizzes')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "{} - {}".format(self.id, self.difficulty)
