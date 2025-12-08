from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField
from .models import User, Company, Job

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
        # stops role escalation via API
        read_only_fields = ["role"]  

class CompanySerializer(TaggitSerializer, serializers.ModelSerializer):
    industry = TagListSerializerField(required=False)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "slug",
            "website",
            "description",
            "logo",
            "industry",
            "created_at",
        ]
        read_only_fields = ["slug", "created_at"]

class JobSerializer(TaggitSerializer, serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "apply_url",
            "location",
            "job_type",
            "work_mode",
            "description",
            "responsibilities",
            "requirements",
            "min_salary",
            "max_salary",
            "tags",
            "sensory_warnings",
            "interview_accommodations",
            "is_autism_friendly",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_tags(self, value):
        value = [t.lower() for t in value]
        if len(value) > 10:
            raise serializers.ValidationError("You can assign at most 10 tags.")
        return value

    def validate(self, attrs):
        instance = self.instance
        is_autism_friendly = attrs.get(
            "is_autism_friendly",
            getattr(instance, "is_autism_friendly", False) if instance else False,
        )
        work_mode = attrs.get(
            "work_mode",
            getattr(instance, "work_mode", None) if instance else None,
        )

        if is_autism_friendly and work_mode == "ONSITE":
            raise serializers.ValidationError(
                {"work_mode": "Autism-friendly jobs must be Remote or Hybrid."}
            )
        return attrs
