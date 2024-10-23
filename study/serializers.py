from rest_framework import serializers
from .models import Study
from .validators import validate_date_not_in_past, validate_end_date_after_start_date
from django.utils import timezone

class StudySerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Study
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'is_active', 'duration', 'progress_percentage', 'owner', 'created_at', 'updated_at', 'deleted']
        read_only_fields = ['created_at', 'updated_at', 'deleted']

    def get_is_active(self, obj):
        now = timezone.now().date()
        return obj.start_date <= now <= obj.end_date

    def get_duration(self, obj):
        return (obj.end_date - obj.start_date).days

    def get_progress_percentage(self, obj):
        now = timezone.now().date()
        if now < obj.start_date:
            return 0
        elif now > obj.end_date:
            return 100
        else:
            total_days = (obj.end_date - obj.start_date).days
            days_passed = (now - obj.start_date).days
            return min(100, int((days_passed / total_days) * 100))

    def __init__(self, *args, **kwargs):
        super(StudySerializer, self).__init__(*args, **kwargs)
        self.fields['start_date'].validators.append(validate_date_not_in_past)

    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            validate_end_date_after_start_date(data['start_date'], data['end_date'])
        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
