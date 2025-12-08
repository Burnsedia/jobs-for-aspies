from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from taggit.managers import TaggableManager

class User(AbstractUser):
    ROLE_CHOICES = [
        ("JOB_SEEKER", "Job Seeker"),
        ("COMPANY", "Company"),
        ("ADMIN", "Admin"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="JOB_SEEKER"
    )
    # Set to True after successful Stripe checkout
    has_active_job_posting_plan = models.BooleanField(
        default=False,
        help_text="True if this user has paid via Stripe and can post jobs."
    )

    def __str__(self):
        return self.username


class Company(models.Model):
    # The account that owns this company profile
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_account",
        null=True,
        blank=True,
        help_text="The user who owns this company account."
    )

    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True
    )

    # Industry tags, "neurodivergent-friendly", "remote-first", etc.
    industry = TaggableManager(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ("FT", "Full-Time"),
        ("PT", "Part-Time"),
        ("CT", "Contract"),
        ("IN", "Internship"),
        ("TP", "Temporary"),
    ]

    WORK_MODE_CHOICES = [
        ("REMOTE", "Remote"),
        ("ONSITE", "On-Site"),
        ("HYBRID", "Hybrid"),
    ]

    title = models.CharField(max_length=255)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    # Direct link to apply for the job externally
    apply_url = models.URLField(
        help_text="Direct link to apply on the company's website."
    )

    location = models.CharField(max_length=255, blank=True, null=True)

    job_type = models.CharField(
        max_length=2,
        choices=JOB_TYPE_CHOICES,
        default="FT"
    )

    work_mode = models.CharField(
        max_length=10,
        choices=WORK_MODE_CHOICES,
        default="REMOTE"
    )

    description = models.TextField()
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)

    min_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    max_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Taggit for job skills, roles, metadata
    tags = TaggableManager(blank=True)

    sensory_warnings = models.TextField(
        blank=True,
        null=True,
        help_text="Noise level, lighting, customer interaction, etc."
    )

    interview_accommodations = models.TextField(
        blank=True,
        null=True,
        help_text="Clear instructions, written questions, alternative formats."
    )

    # Must be remote or hybrid (rule enforced below)
    is_autism_friendly = models.BooleanField(default=False)

    # Track who posted the job
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs_posted"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Autism-friendly jobs must be Remote or Hybrid
        if self.is_autism_friendly and self.work_mode not in ["REMOTE", "HYBRID"]:
            raise ValidationError({
                "work_mode": "Autism-friendly jobs must be Remote or Hybrid, not On-Site."
            })

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation everywhere (forms, DRF, admin, scripts)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company.name}"

