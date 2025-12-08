import stripe
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from djstripe.models import Customer

from .models import User, Company, Job
from .serializers import CompanySerializer, JobSerializer
from .permissions import ensure_user_can_post_job


# Use test/live secret key depending on mode
stripe.api_key = (
    settings.STRIPE_LIVE_SECRET_KEY
    if getattr(settings, "STRIPE_LIVE_MODE", False)
    else settings.STRIPE_TEST_SECRET_KEY
)


# ===========================
#      COMPANY VIEWSET
# ===========================

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("-created_at")
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts may create companies.")

        serializer.save(owner=user)


# ===========================
#        JOB VIEWSET
# ===========================

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        # Centralized business rules
        ensure_user_can_post_job(user)

        # If they don't have an active subscription and DO have a credit,
        # consume the one-time job credit.
        if not user.has_active_subscription and user.has_active_job_posting_plan:
            user.has_active_job_posting_plan = False
            user.save()

        serializer.save(
            posted_by=user,
            company=user.company_account
        )

    def perform_update(self, serializer):
        user = self.request.user
        job = self.get_object()

        if user.role != "ADMIN":
            if not hasattr(user, "company_account") or job.company != user.company_account:
                raise PermissionDenied("You can only edit jobs for your own company.")

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role != "ADMIN":
            if not hasattr(user, "company_account") or instance.company != user.company_account:
                raise PermissionDenied("You can only delete jobs for your own company.")

        return super().perform_destroy(instance)


# ===========================
#  STRIPE: ONE-TIME JOB CREDIT
# ===========================

class CreateJobPostingCheckoutView(APIView):
    """
    Creates a Stripe Checkout Session (one-time payment) for a job posting credit.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts can purchase job credits.")

        # dj-stripe customer
        customer, _ = Customer.get_or_create(subscriber=user)

        try:
            checkout_session = stripe.checkout.Session.create(
                mode="payment",
                customer=customer.id,
                line_items=[{
                    "price": settings.STRIPE_JOB_POSTING_PRICE_ID,
                    "quantity": 1,
                }],
                client_reference_id=user.id,
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"url": checkout_session.url}, status=status.HTTP_201_CREATED)


# ===========================
#  STRIPE: SUBSCRIPTION (UNLIMITED)
# ===========================

class CreateSubscriptionCheckoutView(APIView):
    """
    Creates a Stripe Checkout Session for an unlimited job posting subscription.
    The actual subscription lifecycle is managed by dj-stripe via its webhook.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts can subscribe.")

        customer, _ = Customer.get_or_create(subscriber=user)

        try:
            checkout_session = stripe.checkout.Session.create(
                mode="subscription",
                customer=customer.id,
                line_items=[{
                    "price": settings.STRIPE_UNLIMITED_POSTING_PRICE_ID,
                    "quantity": 1,
                }],
                client_reference_id=user.id,
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"url": checkout_session.url}, status=status.HTTP_201_CREATED)


# ===========================
#  STRIPE: JOB CREDIT WEBHOOK
#  (ONLY for one-time job credits)
#  Subscriptions handled by dj-stripe.
# ===========================

class JobCreditWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        endpoint_secret = settings.STRIPE_JOB_CREDIT_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Dedupe events by event.id
        event_id = event["id"]
        if StripeEvent.objects.filter(event_id=event_id).exists():
            return Response(status=status.HTTP_200_OK)
        StripeEvent.objects.create(event_id=event_id)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            if session.get("mode") == "payment":
                user_id = session.get("client_reference_id")
                if user_id is not None:
                    try:
                        user = User.objects.get(id=user_id)
                        user.has_active_job_posting_plan = True
                        user.save()
                    except User.DoesNotExist:
                        pass

        return Response(status=status.HTTP_200_OK)

