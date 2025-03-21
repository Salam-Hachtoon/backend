from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Attachment(models.Model):
    """
    Attachment model represents a file uploaded by a user along with its associated metadata.
    Attributes:
        user (ForeignKey): A reference to the user who uploaded the attachment. 
            Related to the AUTH_USER_MODEL with a cascade delete behavior.
        file (FileField): The uploaded file stored in the 'attachments/' directory.
        extracted_text (TextField): Optional field to store text extracted from the uploaded file.
        batch_id (CharField): Optional field to track batch uploads using a unique identifier.
        status (CharField): The processing status of the attachment. 
            Choices are:
                - "processing": The file is being processed.
                - "completed": The file has been successfully processed.
                - "failed": The file processing failed.
            Defaults to "processing".
        uploaded_at (DateTimeField): The timestamp when the file was uploaded. Automatically set on creation.
    Methods:
        __str__(): Returns a string representation of the attachment in the format 
            "<user> - <file name>".
    """

    CHOICE=[
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed")
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    extracted_text = models.TextField(blank=True, null=True)
    batch_id = models.CharField(max_length=50, null=True, blank=True)  # Tracks batch uploads
    status = models.CharField(
        CHOICE,
        max_length=20,
        default="processing",
    )
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
    created_at = models.DateTimeField(auto_now_add=True)

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


class Question(models.Model):
    """
    Represents a question in a quiz.
    Attributes:
        quiz (ForeignKey): A foreign key linking the question to a specific quiz. 
            Deletes associated questions when the quiz is deleted.
        question_text (TextField): The text of the question.
        correct_answer (CharField): The correct answer to the question, with a maximum length of 255 characters.
        created_at (DateTimeField): The timestamp when the question was created, automatically set at creation.
    Methods:
        __str__(): Returns the text of the question as its string representation.
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question_text



class Choice(models.Model):
    """
    Represents a choice for a question in the system.
    Attributes:
        question (ForeignKey): A foreign key to the related Question model. 
            When the related question is deleted, all associated choices are also deleted.
        choice_text (CharField): The text of the choice, limited to 255 characters.
        is_correct (BooleanField): Indicates whether this choice is the correct answer 
            for the related question. Defaults to False.
    Methods:
        __str__(): Returns the text of the choice as its string representation.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.choice_text

class Bookmark(models.Model):
    """
    Represents a bookmark created by a user for a FlashCard, Summary, or Quiz Question.
    Attributes:
        user (ForeignKey): The user who created the bookmark.
        content_type (ForeignKey): The type of the bookmarked object (FlashCard, Summary, or Question).
        object_id (PositiveIntegerField): The ID of the bookmarked object.
        content_object (GenericForeignKey): The generic relationship to the bookmarked object.
        created_at (DateTimeField): The timestamp when the bookmark was created.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Bookmark by {} on {}".format(self.user, self.created_at)
