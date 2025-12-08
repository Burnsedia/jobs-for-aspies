# api/filters.py
import django_filters
from taggit.models import Tag
from .models import Job, Company

class JobFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__name",
        to_field_name="name",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Job
        fields = {
            "company": ["exact"],
            "work_mode": ["exact"],
            "job_type": ["exact"],
            "is_autism_friendly": ["exact"],
        }


class CompanyFilter(django_filters.FilterSet):
    industry = django_filters.ModelMultipleChoiceFilter(
        field_name="industry__name",
        to_field_name="name",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Company
        fields = {
            "name": ["icontains"],
        }
