from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    formatted_created_date = serializers.SerializerMethodField()
    formatted_deadline = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "formatted_created_date",
            "formatted_deadline",
            "priority",
            "status",
            
        ]

    def get_status(self, obj):
        return obj.get_status
    def get_formatted_created_date(self, obj):
        return obj.created_date.strftime("%Y-%m-%d %H:%M:%S")

    def get_formatted_deadline(self, obj):
        return obj.deadline.strftime("%Y-%m-%d %H:%M:%S")