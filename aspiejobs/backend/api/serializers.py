from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Company, Job


class CompanySerializer(TaggitSerializer, serializers.ModelSerializer):
    industry = TagListSerializerField(required=False)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "website",
            "description",
            "logo",
            "industry",
            "created_at",
        ]


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
            "posted_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["posted_by", "company", "created_at", "updated_at"]

    def validate(self, attrs):
        # Combine incoming data with instance data for PATCH
        instance = self.instance

        is_autism_friendly = attrs.get(
            "is_autism_friendly",
            getattr(instance, "is_autism_friendly", False)
        )
        work_mode = attrs.get(
            "work_mode",
            getattr(instance, "work_mode", None)
        )

        if is_autism_friendly and work_mode == "ONSITE":
            raise serializers.ValidationError(
                {"work_mode": "Autism-friendly jobs must be Remote or Hybrid."}
            )
        return attrs
