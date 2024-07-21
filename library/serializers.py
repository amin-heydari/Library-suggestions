from rest_framework import serializers
from .models import Books, Reviews


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'title', 'author', 'genre')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ('id', 'book', 'rating')

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        book = data['book']

        review_id = self.instance.id if self.instance else None
        if Reviews.objects.filter(book=book, user=user).exclude(id=review_id).exists():
            raise serializers.ValidationError("You have already reviewed this book.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return Reviews.objects.create(user=user, **validated_data)