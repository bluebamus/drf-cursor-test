import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Person
from .serializers import PersonSerializer
from book.views import IsOwnerOrReadOnly
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin

logger = logging.getLogger(__name__)


@extend_schema(tags=["People"])
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["gender", "deleted"]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = [
        "last_name",
        "first_name",
        "birth_date",
        "created_at",
        "updated_at",
    ]

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="min_age", description="Minimum age", required=False, type=int
            ),
        ]
    )
    @action(detail=False, methods=["get"])
    def adults(self, request):
        logger.info(
            f"Accessed {self.__class__.__name__}.adults, URL: {request.get_full_path()}"
        )
        min_age = int(request.query_params.get("min_age", 18))
        adults = Person.objects.filter(age__gte=min_age, deleted=False)
        if not adults.exists():
            raise NotFound("No adults found matching the criteria", code="no_adults")
        serializer = self.get_serializer(adults, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if instance.deleted:
            raise ValidationError(
                {"detail": "This person is already deleted"}, code="already_deleted"
            )
        instance.delete()  # This will call the soft delete method


# class PersonListView(LoginRequiredMixin, ListView):
#     model = Person
#     template_name = "people/person_list.html"
#     context_object_name = "people"


# class PersonDetailView(LoginRequiredMixin, DetailView):
#     model = Person
#     template_name = "people/person_detail.html"
#     context_object_name = "person"


# class PersonCreateView(LoginRequiredMixin, CreateView):
#     model = Person
#     form_class = PersonForm
#     template_name = "people/person_form.html"
#     success_url = reverse_lazy("person-list")


# class PersonUpdateView(LoginRequiredMixin, UpdateView):
#     model = Person
#     form_class = PersonForm
#     template_name = "people/person_form.html"
#     success_url = reverse_lazy("person-list")


# class PersonDeleteView(LoginRequiredMixin, DeleteView):
#     model = Person
#     template_name = "people/person_confirm_delete.html"
#     success_url = reverse_lazy("person-list")


# class AdultsListView(LoginRequiredMixin, ListView):
#     template_name = "people/adults_list.html"
#     context_object_name = "adults"

#     def get_queryset(self):
#         return Person.objects.filter(age__gte=18)
