from django.urls import path

from .views import *

urlpatterns = [
    path('book/list', BookListView.as_view(), name='book_list'),
    path('book/genre', BookListByGenreView.as_view(), name='book-list-by-genre'),
    path('review/add/', ReviewCreateView.as_view(), name='review-add'),
    path('review/update/<int:pk>/', ReviewUpdateView.as_view(), name='review-update'),
    path('review/delete/<int:pk>/', ReviewDeleteView.as_view(), name='review-delete'),
    path('suggest/api/', BookSuggestionView.as_view(), name='book-suggestion'),

]
