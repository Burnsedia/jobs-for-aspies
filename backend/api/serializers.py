from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField
from .models import User, Company, Job, Portfolio, Project
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

class UserCreateSerializer(DjoserUserCreateSerializer):
    """
    Used by Djoser for registration:
        POST /auth/users/

    We inherit from Djoser's serializer so that password validation,
    user creation logic, and signals still work.
    """
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ("id", "username", "email", "password")

class UserSerializer(DjoserUserSerializer):
    """
    Used by Djoser for:
        GET /auth/users/me/
        GET /auth/users/<id>/

    We extend it to include the user's role, but we keep it read-only.
    """
    role = serializers.CharField(read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = ("id", "username", "email", "role")

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
    tech_tags = TagListSerializerField(required=False)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "apply_url",
            "remote_level",
            "async_level",
            "location",
            "job_type",
            "work_mode",
            "description",
            "responsibilities",
            "requirements",
            "min_salary",
            "max_salary",
            "tech_tags",
            "benefits",
            "interview_process",
            "is_remote_friendly",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_tech_tags(self, value):
        value = [t.lower() for t in value]
        if len(value) > 10:
            raise serializers.ValidationError("You can assign at most 10 tech tags.")
        return value

    def validate(self, attrs):
        instance = self.instance
        is_remote_friendly = attrs.get(
            "is_remote_friendly",
            getattr(instance, "is_remote_friendly", False) if instance else False,
        )
        work_mode = attrs.get(
            "work_mode",
            getattr(instance, "work_mode", None) if instance else None,
        )

        if is_remote_friendly and work_mode == "ONSITE":
            raise serializers.ValidationError(
                {"work_mode": "Remote-friendly jobs should be Remote or Hybrid."}
            )
        return attrs


class ProjectSerializer(TaggitSerializer, serializers.ModelSerializer):
    tech_stack = TagListSerializerField(required=False)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "github_url",
            "live_url",
            "tech_stack",
            "start_date",
            "end_date",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PortfolioSerializer(TaggitSerializer, serializers.ModelSerializer):
    skills = TagListSerializerField(required=False)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            "id",
            "user",
            "bio",
            "years_experience",
            "skills",
            "featured_project_1",
            "featured_project_2",
            "featured_project_3",
            "github_repos_count",
            "github_stars_count",
            "github_followers_count",
            "open_to_remote",
            "open_to_contract",
            "available_for_hire",
            "created_at",
            "updated_at",
            "projects",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
