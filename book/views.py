import logging
import datetime
import asyncio
from asgiref.sync import sync_to_async
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Book, Author, UserProfile, BookRecommendation
from .serializers import (
    BookSerializer,
    AuthorSerializer,
    UserProfileSerializer,
    UserRecommendationsSerializer,
)
from .filters import BookFilter, AuthorFilter
from django.db.models import Count, Avg
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination,
)
from blog_project.exceptions import CustomAPIException
from django.http import FileResponse, Http404
from django.db import models
from django.utils import timezone
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


# 소유자 또는 읽기 전용 권한
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


# class LimitOffsetPagination(LimitOffsetPagination):
#     default_limit = 10
#     max_limit = 100
#     limit_query_param = 'limit'
#     offset_query_param = 'offset'

# class CursorPagination(CursorPagination):
#     page_size = 10
#     ordering = '-created_at'
#     cursor_query_param = 'cursor'


@extend_schema(tags=["Books"])  # Swagger 문서화를 위한 데코레이터
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = BookFilter
    search_fields = ["title", "author__name", "isbn"]
    ordering_fields = ["title", "publication_date", "price", "rating"]
    pagination_class = StandardResultsSetPagination
    # pagination_class = LimitOffsetPagination
    # pagination_class = CursorPagination

    # 인기 있는 책 목록 반환
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="min_rating",
                description="Minimum rating",
                required=False,
                type=float,
            ),
        ]
    )
    @action(detail=False, methods=["get"])
    def popular(self, request):
        logger.info(
            f"Accessed {self.__class__.__name__}.popular, URL: {request.get_full_path()}"
        )
        min_rating = request.query_params.get("min_rating", 4.0)
        try:
            min_rating = float(min_rating)
        except ValueError:
            raise ValidationError(
                {"min_rating": "Must be a valid number"}, code="invalid"
            )

        books = Book.objects.filter(rating__gte=min_rating, deleted=False)
        if not books.exists():
            raise NotFound("No books found matching the criteria", code="not_found")

        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)

    # 삭제 시 소프트 삭제 수행
    def perform_destroy(self, instance):
        logger.info(
            f"Accessed {self.__class__.__name__}.perform_destroy, URL: {self.request.get_full_path()}"
        )
        if instance.deleted:
            raise ValidationError(
                {"detail": "This book is already deleted"}, code="already_deleted"
            )
        instance.delete()  # 소프트 삭제 메서드 호출

    @action(detail=False, methods=["get"])
    def recent(self, request):
        recent_books = Book.objects.filter(
            publication_date__gte=timezone.now() - datetime.timedelta(days=30)
        )
        page = self.paginate_queryset(recent_books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(recent_books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_price_range(self, request):
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        if min_price and max_price:
            books = Book.objects.filter(price__gte=min_price, price__lte=max_price)
            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Please provide both min_price and max_price"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def partial_update(self, request, *args, **kwargs):
        logger.info(
            f"Accessed {self.__class__.__name__}.partial_update, URL: {request.get_full_path()}"
        )
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def download_attachment(self, request, pk=None):
        book = self.get_object()
        if book.attachment:
            return FileResponse(book.attachment, as_attachment=True)
        return Response(
            {"error": "No attachment found"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=["get"])
    def download_cover_image(self, request, pk=None):
        book = self.get_object()
        if book.cover_image:
            return FileResponse(book.cover_image, as_attachment=True)
        return Response(
            {"error": "No cover image found"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["get"])
    def top_rated(self, request):
        top_books = Book.objects.order_by("-average_rating")[:10]
        serializer = self.get_serializer(top_books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_genre(self, request):
        genre_name = request.query_params.get("genre", None)
        if genre_name:
            books = Book.objects.filter(genres__name=genre_name)
            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Genre parameter is required"}, status=status.HTTP_400_BAD_REQUEST
        )


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        book = self.get_object(pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        book = self.get_object(pk)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PopularBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.order_by("-rating")[:10]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Authors"])
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = AuthorFilter
    search_fields = ["name"]
    ordering_fields = ["name"]
    pagination_class = StandardResultsSetPagination
    # pagination_class = LimitOffsetPagination
    # pagination_class = CursorPagination

    def list(self, request, *args, **kwargs):
        logger.info(
            f"Accessed {self.__class__.__name__}.list, URL: {request.get_full_path()}"
        )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.info(
            f"Accessed {self.__class__.__name__}.create, URL: {request.get_full_path()}"
        )
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        logger.info(
            f"Accessed {self.__class__.__name__}.retrieve, URL: {request.get_full_path()}"
        )
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(
            f"Accessed {self.__class__.__name__}.update, URL: {request.get_full_path()}"
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info(
            f"Accessed {self.__class__.__name__}.destroy, URL: {request.get_full_path()}"
        )
        return super().destroy(request, *args, **kwargs)

    # 특정 저자의 책 목록 반환
    @extend_schema(responses=BookSerializer(many=True))
    @action(detail=True, methods=["get"])
    def books(self, request, pk=None):
        logger.info(
            f"Accessed {self.__class__.__name__}.books, URL: {request.get_full_path()}"
        )
        try:
            author = self.get_object()
        except Author.DoesNotExist:
            raise NotFound("Author not found", code="not_found")

        books = author.books.filter(deleted=False)
        if not books.exists():
            raise NotFound("No books found for this author", code="no_books")

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    # 삭제 시 소프트 삭제 수행
    def perform_destroy(self, instance):
        logger.info(
            f"Accessed {self.__class__.__name__}.perform_destroy, URL: {self.request.get_full_path()}"
        )
        if instance.deleted:
            raise ValidationError(
                {"detail": "This author is already deleted"}, code="already_deleted"
            )
        instance.delete()  # 소프트 삭제 메서드 호출

    @action(detail=False, methods=["get"])
    def prolific(self, request):
        book_count = request.query_params.get("book_count", 5)
        authors = Author.objects.annotate(book_count=Count("books")).filter(
            book_count__gte=book_count
        )
        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def complex_book_analysis(request):
    """
    복잡한 비동기 뷰 함수

    이 함수는 다음과 같은 작업을 수행합니다:
    1. 모든 책의 평균 평점을 계산
    2. 가장 많은 책을 쓴 작가를 찾음
    3. 최근 30일 내에 출판된 책들을 조회
    4. 각 장르별 책 수를 계산

    모든 작업은 비동기적으로 수행되며, 결과는 하나의 응답으로 합쳐집니다.
    """

    @sync_to_async
    def get_average_rating():
        return Book.objects.aggregate(Avg("rating"))["rating__avg"]

    @sync_to_async
    def get_most_prolific_author():
        return (
            Author.objects.annotate(book_count=models.Count("books"))
            .order_by("-book_count")
            .first()
        )

    @sync_to_async
    def get_recent_books():
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return list(Book.objects.filter(publication_date__gte=thirty_days_ago))

    @sync_to_async
    def get_genre_counts():
        return dict(
            Book.objects.values("genre")
            .annotate(count=models.Count("id"))
            .values_list("genre", "count")
        )

    # 모든 비동기 작업을 동시에 실행
    avg_rating, prolific_author, recent_books, genre_counts = await asyncio.gather(
        get_average_rating(),
        get_most_prolific_author(),
        get_recent_books(),
        get_genre_counts(),
    )

    # 결과 직렬화
    prolific_author_serializer = AuthorSerializer(prolific_author)
    recent_books_serializer = BookSerializer(recent_books, many=True)

    # 응답 데이터 구성
    response_data = {
        "average_rating": avg_rating,
        "most_prolific_author": prolific_author_serializer.data,
        "recent_books": recent_books_serializer.data,
        "genre_counts": genre_counts,
    }

    return Response(response_data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=True, methods=["get"])
    def recommendations(self, request, pk=None):
        profile = self.get_object()
        serializer = UserRecommendationsSerializer(profile)
        return Response(serializer.data)
