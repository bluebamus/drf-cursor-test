from rest_framework import serializers
from .models import Book, Author, Genre, UserProfile, ReadingHistory, BookRecommendation

class AuthorSerializer(serializers.ModelSerializer):
    """
    Author 모델을 위한 ModelSerializer
    """
    books_count = serializers.SerializerMethodField()
    average_book_rating = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'bio', 'created_at', 'updated_at', 'deleted', 'books_count', 'average_book_rating']
        read_only_fields = ['created_at', 'updated_at', 'deleted']

    def get_books_count(self, obj):
        return obj.books.count()

    def get_average_book_rating(self, obj):
        return obj.books.aggregate(Avg('rating'))['rating__avg']

    def __init__(self, *args, **kwargs):
        """
        초기화 메서드: fields 매개변수를 통해 필드를 동적으로 제한할 수 있습니다.
        """
        super(AuthorSerializer, self).__init__(*args, **kwargs)

        fields = self.context.get('fields')
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def validate_name(self, value):
        """
        name 필드에 대한 사용자 정의 유효성 검사
        """
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value

    def create(self, validated_data):
        """
        Author 인스턴스 생성 메서드
        """
        return Author.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Author 인스턴스 업데이트 메서드
        """
        instance.name = validated_data.get('name', instance.name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genres', 'publication_date', 'isbn', 'price', 'average_rating']

class ReadingHistorySerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = ReadingHistory
        fields = ['book', 'date_read', 'rating']

class UserProfileSerializer(serializers.ModelSerializer):
    favorite_genres = GenreSerializer(many=True)
    reading_history = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'favorite_genres', 'reading_history']

    def get_reading_history(self, obj):
        history = ReadingHistory.objects.filter(user=obj).order_by('-date_read')[:10]
        return ReadingHistorySerializer(history, many=True).data

class BookRecommendationSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = BookRecommendation
        fields = ['book', 'score', 'created_at']

class UserRecommendationsSerializer(serializers.ModelSerializer):
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'recommendations']

    def get_recommendations(self, obj):
        recommendations = BookRecommendation.objects.filter(user=obj).order_by('-score')[:5]
        return BookRecommendationSerializer(recommendations, many=True).data
