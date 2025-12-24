from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    JobViewSet,
    PortfolioViewSet,
    ProjectViewSet,
    CreateJobPostingCheckoutView,
    CreateSubscriptionCheckoutView,
    JobCreditWebhookView,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"jobs", JobViewSet, basename="jobs")
router.register(r"portfolios", PortfolioViewSet, basename="portfolios")
router.register(r"projects", ProjectViewSet, basename="projects")

urlpatterns = [
    path("", include(router.urls)),

    # Nested routes for portfolio projects
    path("portfolios/<int:portfolio_pk>/projects/", ProjectViewSet.as_view({"get": "list", "post": "create"}), name="portfolio-projects"),

    # Stripe: one-time job posting credit
    path(
        "stripe/checkout/job/",
        CreateJobPostingCheckoutView.as_view(),
        name="stripe-job-checkout",
    ),

    # Stripe: subscription for unlimited posting
    path(
        "stripe/checkout/subscription/",
        CreateSubscriptionCheckoutView.as_view(),
        name="stripe-subscription-checkout",
    ),

    # Stripe webhook for one-time job credits
    path(
        "stripe/webhook/job-credit/",
        JobCreditWebhookView.as_view(),
        name="stripe-job-credit-webhook",
    ),
]
