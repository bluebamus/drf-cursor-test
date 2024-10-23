from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Study
from .serializers import StudySerializer
from book.views import IsOwnerOrReadOnly
from datetime import timezone
import logging
from rest_framework.exceptions import NotFound, ValidationError
from django.db import models
from datetime import timedelta
from django.db.models import ExpressionWrapper, F, DurationField

logger = logging.getLogger(__name__)

@extend_schema(tags=['Studies'])
class StudyViewSet(viewsets.ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['start_date', 'end_date', 'deleted']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'updated_at']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='is_active', description='Filter active studies', required=False, type=bool),
        ]
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        logger.info(f"Accessed {self.__class__.__name__}.active, URL: {request.get_full_path()}")
        active_studies = Study.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date(),
            deleted=False
        )
        if not active_studies.exists():
            raise NotFound("No active studies found", code='no_active_studies')
        serializer = self.get_serializer(active_studies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        ongoing_studies = Study.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())
        serializer = self.get_serializer(ongoing_studies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_duration(self, request):
        min_duration = request.query_params.get('min_duration')
        max_duration = request.query_params.get('max_duration')
        if min_duration and max_duration:
            studies = Study.objects.annotate(
                duration=ExpressionWrapper(F('end_date') - F('start_date'), output_field=DurationField())
            ).filter(duration__gte=timedelta(days=int(min_duration)), duration__lte=timedelta(days=int(max_duration)))
            serializer = self.get_serializer(studies, many=True)
            return Response(serializer.data)
        return Response({"error": "Please provide both min_duration and max_duration"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        logger.info(f"Accessed {self.__class__.__name__}.perform_destroy, URL: {self.request.get_full_path()}")
        if instance.deleted:
            raise ValidationError({"detail": "This study is already deleted"}, code='already_deleted')
        instance.delete()
