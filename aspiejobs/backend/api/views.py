import stripe
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Company, Job, User
from .serializers import CompanySerializer, JobSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("-created_at")
    serializer_class = CompanySerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a company.")

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts can create a company profile.")

        serializer.save(owner=user)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer

    def get_permissions(self):
        # Anyone can view, only authed users can create/update/delete
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts may post jobs.")

        if not user.has_active_job_posting_plan:
            raise PermissionDenied("You must purchase a job posting plan to post jobs.")

        if not hasattr(user, "company_account") or user.company_account is None:
            raise PermissionDenied("You must create a company profile before posting jobs.")

        serializer.save(
            posted_by=user,
            company=user.company_account
        )

    def perform_update(self, serializer):
        user = self.request.user
        job = self.get_object()

        if user != job.posted_by and user.role != "ADMIN":
            raise PermissionDenied("You can only edit jobs you posted.")

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        user = self.request.user

        if user != instance.posted_by and user.role != "ADMIN":
            raise PermissionDenied("You can only delete jobs you posted.")

        return super().perform_destroy(instance)


class CreateCheckoutSessionView(APIView):
    """
    Creates a Stripe Checkout session for a job posting plan.
    Frontend should redirect to the 'url' returned here.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts can purchase job posting plans.")

        try:
            checkout_session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price": settings.STRIPE_JOB_POSTING_PRICE_ID,
                        "quantity": 1,
                    }
                ],
                client_reference_id=user.id,
                customer_email=user.email,
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"id": checkout_session.id, "url": checkout_session.url},
            status=status.HTTP_201_CREATED
        )


class StripeWebhookView(APIView):
    """
    Handles Stripe webhook events.
    On checkout.session.completed, marks user as having an active job posting plan.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=endpoint_secret,
            )
        except ValueError:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session.get("client_reference_id")

            if user_id is not None:
                try:
                    user = User.objects.get(id=user_id)
                    user.has_active_job_posting_plan = True
                    user.save()
                except User.DoesNotExist:
                    pass  # ignore silently or log

        return Response(status=status.HTTP_200_OK)

