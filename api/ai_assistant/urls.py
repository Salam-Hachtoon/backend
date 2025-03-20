from . import views
from django.urls import path, include


urlpatterns = [
    path('upload_attachments/', views.upload_attachments, name='upload_attachments'),
    path('get_summary/', views.get_summary, name='get_summary'),
    path('get_flash_cards/',  views.get_flash_cards, name='get_flash_cards'),
    path('get_quiz/', views.get_quiz, name='get_quiz'),
    path('create_bookmark/', views.create_bookmark, name='create_bookmark'),
    path('delete_bookmark/', views.delete_bookmark, name='delete_bookmark'),
    path('user/summaries/', views.get_user_summaries, name='get_user_summaries'),
    path('user/flashcards/', views.get_user_flashcards, name='get_user_flashcards'),
    path('user/quizzes/', views.get_user_quizzes, name='get_user_quizzes'),
    path('user/attachments/', views.get_user_attachments, name='get_user_attachments'),
]
