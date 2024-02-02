from django.urls import path
from .views import IndexView, BookListView, BookDetailView,AuthorListView, AuthorDetailView, LoanedBooksByUserListView, LoanedBooksAllListView, renew_book_librarian
from .views import AuthorCreate, AuthorUpdate, AuthorDelete, BookCreate, BookUpdate, BookDelete

# app_name = 'myapp'
urlpatterns = [
  path('', IndexView.as_view(), name='index'),
  path('books/', BookListView.as_view(), name='books'),
  path('mybooks/', LoanedBooksByUserListView.as_view(), name='my-borrowed'),
  path('book/<int:pk>', BookDetailView.as_view(), name='book-detail'),
  path('authors/', AuthorListView.as_view(), name='authors'),
  path('author/<int:pk>', AuthorDetailView.as_view(), name='author-detail'),
  path('all-borrowed/', LoanedBooksAllListView.as_view(), name='all-borrowed'),
  path('book/<uuid:pk>/renew/', renew_book_librarian, name='renew-book-librarian'),

  path('author/create/', AuthorCreate.as_view(), name='author-create'),
  path('author/<int:pk>/update/', AuthorUpdate.as_view(), name='author-update'),
  path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),
  
  path('book/create/', BookCreate.as_view(), name='book-create'),
  path('book/<int:pk>/update/', BookUpdate.as_view(), name='book-update'),
  path('book/<int:pk>/delete/', BookDelete.as_view(), name='book-delete'),
]
