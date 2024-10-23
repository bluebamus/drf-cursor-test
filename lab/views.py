import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Experiment
from .serializers import ExperimentSerializer
from book.views import IsOwnerOrReadOnly
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


@extend_schema(tags=["Experiments"])
class ExperimentViewSet(viewsets.ModelViewSet):
    queryset = Experiment.objects.all()
    serializer_class = ExperimentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "start_date", "end_date", "deleted"]
    search_fields = ["name", "description"]
    ordering_fields = ["start_date", "end_date", "created_at", "updated_at"]

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
                name="status",
                description="Filter by experiment status",
                required=False,
                type=str,
            ),
        ]
    )
    @action(detail=False, methods=["get"])
    def by_status(self, request):
        logger.info(
            f"Accessed {self.__class__.__name__}.by_status, URL: {request.get_full_path()}"
        )
        status = request.query_params.get("status", "IN_PROGRESS")
        experiments = Experiment.objects.filter(status=status, deleted=False)
        if not experiments.exists():
            raise NotFound(
                "No experiments found with the given status", code="no_experiments"
            )
        serializer = self.get_serializer(experiments, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(researcher=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if instance.deleted:
            raise ValidationError(
                {"detail": "This experiment is already deleted"}, code="already_deleted"
            )
        instance.delete()  # This will call the soft delete method


# class ExperimentListView(ListView):
#     model = Experiment
#     template_name = "lab/experiment_list.html"
#     context_object_name = "experiments"


# class ExperimentDetailView(DetailView):
#     model = Experiment
#     template_name = "lab/experiment_detail.html"
#     context_object_name = "experiment"


# class ExperimentCreateView(CreateView):
#     model = Experiment
#     form_class = ExperimentForm
#     template_name = "lab/experiment_form.html"
#     success_url = reverse_lazy("experiment-list")


# class ExperimentUpdateView(UpdateView):
#     model = Experiment
#     form_class = ExperimentForm
#     template_name = "lab/experiment_form.html"
#     success_url = reverse_lazy("experiment-list")


# class ExperimentDeleteView(DeleteView):
#     model = Experiment
#     template_name = "lab/experiment_confirm_delete.html"
#     success_url = reverse_lazy("experiment-list")
