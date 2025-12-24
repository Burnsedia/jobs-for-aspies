from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify
from taggit.managers import TaggableManager
from urllib.parse import urlparse

def validate_https_url(value):
    parsed = urlparse(value)
    if parsed.scheme not in ["http", "https"]:
        raise ValidationError("URL must start with http:// or https://")


def validate_logo_file_size(image):
    max_mb = 2
    if image.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Logo file size must be under {max_mb}MB.")


def validate_logo_extension(image):
    valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    name = image.name.lower()

    if "." not in name:
        raise ValidationError("Logo file must have an extension.")

    ext = "." + name.rsplit(".", 1)[-1]
    if ext not in valid_extensions:
        raise ValidationError("Unsupported file type for logo.")

class User(AbstractUser):
    ROLE_CHOICES = [
        ("JOB_SEEKER", "Job Seeker"),
        ("COMPANY", "Company"),
        ("ADMIN", "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="JOB_SEEKER",
        db_index=True,
    )

    # One-time credit for posting a job (Stripe checkout payment)
    has_active_job_posting_plan = models.BooleanField(default=False)

    # Portfolio/GitHub integration for job seekers
    github_username = models.CharField(max_length=100, blank=True, null=True)
    github_access_token = models.CharField(max_length=255, blank=True, null=True)  # Encrypted in production
    portfolio_website = models.URLField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)

    # Skills and preferences for job seekers
    preferred_work_mode = models.CharField(
        max_length=10,
        choices=[("REMOTE", "Remote"), ("ONSITE", "On-Site"), ("HYBRID", "Hybrid")],
        default="REMOTE",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username

    # ---- dj-stripe integration helpers ----

    @property
    def stripe_customer(self):
        """
        Returns or creates the dj-stripe Customer linked to this user.
        """
        from djstripe.models import Customer
        customer, _ = Customer.get_or_create(subscriber=self)
        return customer

    @property
    def has_active_subscription(self):
        """
        Checks if this user has an active unlimited job posting subscription.
        dj-stripe updates subscription statuses automatically via webhook.
        """
        from djstripe.models import Customer
        try:
            customer = Customer.objects.get(subscriber=self)
        except Customer.DoesNotExist:
            return False

        sub = customer.subscriptions.filter(status="active").first()
        return bool(sub)


class Portfolio(models.Model):
    """
    Portfolio model for job seekers to showcase their skills and projects.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio'
    )

    bio = models.TextField(blank=True, null=True, help_text="Short professional bio")
    years_experience = models.PositiveIntegerField(default=0)

    # Skills - using django-taggit for flexible tagging
    skills = TaggableManager(blank=True, help_text="Technical skills, frameworks, tools")

    # Featured projects
    featured_project_1 = models.JSONField(blank=True, null=True, help_text="Featured project data")
    featured_project_2 = models.JSONField(blank=True, null=True, help_text="Featured project data")
    featured_project_3 = models.JSONField(blank=True, null=True, help_text="Featured project data")

    # GitHub stats (cached)
    github_repos_count = models.PositiveIntegerField(default=0)
    github_stars_count = models.PositiveIntegerField(default=0)
    github_followers_count = models.PositiveIntegerField(default=0)

    # Work preferences
    open_to_remote = models.BooleanField(default=True)
    open_to_contract = models.BooleanField(default=False)
    available_for_hire = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portfolio of {self.user.username}"


class Project(models.Model):
    """
    Individual projects within a portfolio.
    """
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    github_url = models.URLField(blank=True, null=True)
    live_url = models.URLField(blank=True, null=True)
    tech_stack = TaggableManager(blank=True, help_text="Technologies used")

    # Project metadata
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.portfolio.user.username}"


class StripeEvent(models.Model):
    """
    Stores Stripe event IDs to guarantee webhook events
    are processed only once.

    This protects the job board from Stripe retrying events
    and accidentally granting multiple job credits.
    """
    event_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id

class Company(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
        null=True,   # temporarily allow null so migration succeeds
        blank=True,
    )
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    website = models.URLField(
        blank=True,
        null=True,
        validators=[validate_https_url],
    )

    description = models.TextField(blank=True, null=True)

    logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True,
        validators=[validate_logo_file_size, validate_logo_extension],
    )

    # Example tags: "tech", "finance", "remote-first", etc.
    industry = TaggableManager(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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

    ASYNC_LEVEL_CHOICES = [
        ("FULL_ASYNC", "Fully Asynchronous"),
        ("MOSTLY_ASYNC", "Mostly Asynchronous"),
        ("SOME_SYNC", "Some Synchronous Work"),
        ("TRADITIONAL", "Traditional Schedule"),
    ]

    REMOTE_POLICY_CHOICES = [
        ("FULL_REMOTE", "Fully Remote"),
        ("HYBRID_OPTIONAL", "Hybrid Optional"),
        ("HYBRID_REQUIRED", "Hybrid Required"),
        ("ONSITE", "On-site Required"),
    ]

    title = models.CharField(max_length=255)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="jobs"
    )

    apply_url = models.URLField(
        help_text="Direct link to apply on the company's website.",
        validators=[validate_https_url],
    )

    atlanta_neighborhood = models.CharField(
        max_length=20,
        choices=ATLANTA_NEIGHBORHOOD_CHOICES,
        blank=True,
        null=True,
        db_index=True,
        help_text="Specific Atlanta neighborhood or metro area location",
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text="Additional location details (building, floor, etc.)",
    )

    job_type = models.CharField(
        max_length=2,
        choices=JOB_TYPE_CHOICES,
        default="FT",
        db_index=True,
    )

    work_mode = models.CharField(
        max_length=10,
        choices=WORK_MODE_CHOICES,
        default="REMOTE",
        db_index=True,
    )

    description = models.TextField()
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)

    min_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    max_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )

    # Tech-focused tags: "frontend", "backend", "devops", "data-science", etc.
    tech_tags = TaggableManager(blank=True)

    benefits = models.TextField(blank=True, null=True, help_text="Company benefits and perks")
    interview_process = models.TextField(blank=True, null=True, help_text="Description of interview process")

    is_remote_friendly = models.BooleanField(default=False, help_text="Company has strong remote work culture")

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs_posted",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.is_remote_friendly and self.work_mode == "ONSITE":
            raise ValidationError(
                {"work_mode": "Remote-friendly jobs should be Remote or Hybrid."}
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company.name}"
