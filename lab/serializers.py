from rest_framework import serializers
from .models import Experiment
from django.utils import timezone

class ExperimentSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    researcher = serializers.ReadOnlyField(source='researcher.username')

    class Meta:
        model = Experiment
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'status', 'is_active', 'duration', 'time_remaining', 'researcher', 'created_at', 'updated_at', 'deleted']
        read_only_fields = ['created_at', 'updated_at', 'deleted']

    def create(self, validated_data):
        validated_data['researcher'] = self.context['request'].user
        return super().create(validated_data)

    def get_is_active(self, obj):
        return obj.status == 'IN_PROGRESS'

    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).total_seconds() / 3600  # Duration in hours

    def get_time_remaining(self, obj):
        if obj.status == 'COMPLETED' or obj.status == 'CANCELLED':
            return 0
        now = timezone.now()
        if now > obj.end_date:
            return 0
        return (obj.end_date - now).total_seconds() / 3600  # Remaining time in hours
