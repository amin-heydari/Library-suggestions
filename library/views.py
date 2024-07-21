from django.db import connection
from django.db.models import Max
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from .models import Books, Reviews
from .serializers import BookSerializer, ReviewSerializer


##### WITH ORM
# class BookListView(generics.ListAPIView):
#     queryset = Books.objects.all()
#     serializer_class = BookSerializer

##### WITHOUT ORM
class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, author, genre FROM library_books")
            rows = cursor.fetchall()

        books = [
            {
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'genre': row[3],
            }
            for row in rows
        ]

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)


##### WITH ORM
# class BookListByGenreView(generics.ListAPIView):
#     serializer_class = BookSerializer
#
#     def get_queryset(self):
#         genre = self.request.query_params.get('genre', None)
#         if genre:
#             return Books.objects.filter(genre=genre)
#         return Books.objects.all()


##### WITHOUT ORM
@extend_schema(
    summary='List books filtered by genre',
    parameters=[
        OpenApiParameter(name='genre', type=str, description='The genre to filter books by', required=False)
    ],
    responses={200: BookSerializer(many=True)},
)
class BookListByGenreView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        genre = request.query_params.get('genre', None)
        with connection.cursor() as cursor:
            if genre:
                cursor.execute("SELECT id, title, author, genre FROM library_books WHERE genre = %s", [genre])
            else:
                cursor.execute("SELECT id, title, author, genre FROM library_books")
            rows = cursor.fetchall()

        books = [
            {
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'genre': row[3],
            }
            for row in rows
        ]

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)


##### WITH ORM
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Add a review for a book',
        responses={201: ReviewSerializer},
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


##### WITHOUT ORM
# class ReviewCreateView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         data = request.data
#         user_id = request.user.id
#         book_id = data.get('book')
#         rating = data.get('rating')
#
#         if not book_id or not rating:
#             return Response({'detail': 'Book ID and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT 1 FROM library_reviews WHERE book_id = %s AND user_id = %s", [book_id, user_id])
#             if cursor.fetchone():
#                 return Response({'detail': 'You have already reviewed this book.'}, status=status.HTTP_400_BAD_REQUEST)
#
#             cursor.execute(
#                 "INSERT INTO library_reviews (book_id, user_id, rating) VALUES (%s, %s, %s)",
#                 [book_id, user_id, rating]
#             )
#
#         response_data = {
#             'book': book_id,
#             'user': user_id,
#             'rating': rating
#         }
#         return Response(response_data, status=status.HTTP_201_CREATED)

##### WITH ORM
class ReviewUpdateView(generics.UpdateAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Update a review for a book',
        responses={200: ReviewSerializer},
    )
    def put(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

##### WITHOUT ORM
# class ReviewUpdateView(generics.UpdateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def put(self, request, *args, **kwargs):
#         review_id = kwargs.get('pk')
#         user_id = request.user.id
#         data = request.data
#         new_rating = data.get('rating')
#
#         if new_rating is None:
#             return Response({'detail': 'Rating is required.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT user_id FROM library_reviews WHERE id = %s", [review_id])
#             review = cursor.fetchone()
#             if not review:
#                 return Response({'detail': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)
#
#             if review[0] != user_id:
#                 return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
#
#             cursor.execute(
#                 "UPDATE library_reviews SET rating = %s WHERE id = %s",
#                 [new_rating, review_id]
#             )
#
#         response_data = {
#             'id': review_id,
#             'user': user_id,
#             'rating': new_rating
#         }
#         return Response(response_data, status=status.HTTP_200_OK)

##### WITH ORM
# class ReviewDeleteView(generics.DestroyAPIView):
#     queryset = Reviews.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#
#     @extend_schema(
#         summary='Delete a review for a book',
#         responses={204: None},
#     )
#     def delete(self, request, *args, **kwargs):
#         review = self.get_object()
#         if review.user != request.user:
#             return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)
#         super().delete(request, *args, **kwargs)
#         return Response("Review Deleted")

class ReviewDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        review_id = kwargs.get('pk')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM library_reviews WHERE id = %s", [review_id])
            review = cursor.fetchone()
            if not review:
                return Response({'detail': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

            if review[0] != user_id:
                return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)

            cursor.execute("DELETE FROM library_reviews WHERE id = %s", [review_id])

        return Response({"detail": "Review Deleted"}, status=status.HTTP_200_OK)


class BookSuggestionView(generics.GenericAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Suggest books based on genres of books the user has read',
        responses={200: BookSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        max_rating = Reviews.objects.filter(user=user).aggregate(Max('rating'))['rating__max']
        top_books_genres = Reviews.objects.filter(user=user, rating=max_rating).values_list('book__genre', flat=True).distinct()
        reviewed_books = Reviews.objects.filter(user=user).values_list('book_id', flat=True)
        suggestions = Books.objects.filter(genre__in=top_books_genres).exclude(id__in=reviewed_books)
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)
