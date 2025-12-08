from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet,
    JobViewSet,
    CreateJobPostingCheckoutView,
    CreateSubscriptionCheckoutView,
    JobCreditWebhookView,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")
router.register(r"jobs", JobViewSet, basename="jobs")

urlpatterns = [
    path("", include(router.urls)),

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
