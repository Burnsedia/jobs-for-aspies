from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Company, Job

class CompanySerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "website",
            "description",
            "logo",
            "tags",
            "created_at",
        ]

class JobSerializer(TaggitSerializer, serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source="company",
        write_only=True
    )

    tags = TagListSerializerField(required=False)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "company_id",
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

    # Re-validate the autism-friendly rule at serializer level
    def validate(self, attrs):
        is_autism_friendly = attrs.get("is_autism_friendly")
        work_mode = attrs.get("work_mode")

        if is_autism_friendly and work_mode == "ONSITE":
            raise serializers.ValidationError(
                {"work_mode": "Autism-friendly jobs must be Remote or Hybrid."}
            )
        return attrs
