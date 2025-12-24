import stripe
from django.conf import settings
from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from djstripe.models import Customer
from .models import User, Company, Job, Portfolio, Project
from .serializers import CompanySerializer, JobSerializer, PortfolioSerializer, ProjectSerializer
from .filters import JobFilter, CompanyFilter, PortfolioFilter
from .permissions import ensure_user_can_post_job
from .filters import JobFilter, CompanyFilter
from rest_framework.pagination import PageNumberPagination

stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("-created_at")
    serializer_class = CompanySerializer
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CompanyFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts may create companies.")

        serializer.save(owner=user)

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ["title", "description", "requirements", "responsibilities"]
    ordering_fields = ["created_at", "min_salary", "max_salary"]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        ensure_user_can_post_job(user)

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
                raise PermissionDenied("You can only edit jobs from your own company.")

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role != "ADMIN":
            if not hasattr(user, "company_account") or instance.company != user.company_account:
                raise PermissionDenied("You can only delete jobs for your own company.")

        return super().perform_destroy(instance)


class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PortfolioFilter
    search_fields = ["bio", "user__username"]
    ordering_fields = ["created_at", "years_experience"]

    def get_queryset(self):
        return Portfolio.objects.all().order_by("-created_at").prefetch_related("projects", "skills")

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != "JOB_SEEKER":
            raise PermissionDenied("Only job seekers may create portfolios.")

        # Check if user already has a portfolio
        if hasattr(user, 'portfolio'):
            raise PermissionDenied("You already have a portfolio. Use PATCH to update it.")

        serializer.save(user=user)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all().order_by("-created_at").prefetch_related("tech_stack")

        # Filter by portfolio if portfolio_pk is in URL
        portfolio_pk = self.kwargs.get('portfolio_pk')
        if portfolio_pk:
            queryset = queryset.filter(portfolio_id=portfolio_pk)

        return queryset

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        portfolio_pk = self.kwargs.get('portfolio_pk')

        if portfolio_pk:
            # Nested route - portfolio from URL
            try:
                portfolio = Portfolio.objects.get(id=portfolio_pk, user=user)
            except Portfolio.DoesNotExist:
                raise PermissionDenied("Portfolio not found or you don't own it.")
        else:
            # Direct route - portfolio from request data
            portfolio_id = self.request.data.get('portfolio')
            if not portfolio_id:
                raise PermissionDenied("Portfolio ID is required.")
            try:
                portfolio = Portfolio.objects.get(id=portfolio_id, user=user)
            except Portfolio.DoesNotExist:
                raise PermissionDenied("You can only create projects for your own portfolio.")

        serializer.save(portfolio=portfolio)

    def perform_update(self, serializer):
        user = self.request.user
        project = self.get_object()

        if project.portfolio.user != user:
            raise PermissionDenied("You can only edit projects in your own portfolio.")

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        user = self.request.user

        if instance.portfolio.user != user:
            raise PermissionDenied("You can only delete projects from your own portfolio.")

        return super().perform_destroy(instance)


class CreateJobPostingCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role != "COMPANY":
            raise PermissionDenied("Only company accounts can purchase job credits.")

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

class CreateSubscriptionCheckoutView(APIView):
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

class JobCreditWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        endpoint_secret = settings.STRIPE_JOB_CREDIT_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event.get("type") == "checkout.session.completed":
            session = event["data"]["object"]

            if session.get("mode") == "payment":
                user_id = session.get("client_reference_id")

                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        user.has_active_job_posting_plan = True
                        user.save()
                    except User.DoesNotExist:
                        pass

        return Response(status=status.HTTP_200_OK)
