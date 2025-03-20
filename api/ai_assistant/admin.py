from django.contrib import admin
from .models import Attachment, Summary, FlashCard, Quiz, Question, Choice, Bookmark


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file', 'status', 'uploaded_at', 'extracted_text', 'batch_id')
    list_filter = ('status', 'uploaded_at')
    search_fields = ('user__username', 'file')

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'content')
    search_fields = ('user__username', 'content')

class FlashCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'summary', 'term', 'created_at')
    search_fields = ('term', 'summary__content')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'summary', 'difficulty', 'created_at')
    list_filter = ('difficulty', 'created_at')
    search_fields = ('user__username', 'summary__content')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'question_text', 'created_at')
    search_fields = ('question_text', 'quiz__summary__content')

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice_text', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('choice_text', 'question__question_text')

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username',)

# Register the models with custom admin classes
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(FlashCard, FlashCardAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
