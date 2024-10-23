from rest_framework import serializers
from .models import Person
from django.utils import timezone

class PersonSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    is_adult = serializers.SerializerMethodField()
    zodiac_sign = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'birth_date', 'age', 'is_adult', 'zodiac_sign', 'gender', 'created_at', 'updated_at', 'deleted']
        read_only_fields = ['created_at', 'updated_at', 'deleted']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_age(self, obj):
        today = timezone.now().date()
        return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))

    def get_is_adult(self, obj):
        return self.get_age(obj) >= 18

    def get_zodiac_sign(self, obj):
        month = obj.birth_date.month
        day = obj.birth_date.day
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Aquarius"
        else:
            return "Pisces"

    # ... (기존 메서드 유지)
