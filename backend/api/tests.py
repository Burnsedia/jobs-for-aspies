from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from api.models import User, Company, Job


def authenticate(client, username, password):
    """Helper: logs in via JWT and sets Authorization header."""
    res = client.post("/auth/jwt/create/", {
        "username": username,
        "password": password
    })
    token = res.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class BaseAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Users
        self.user_company = User.objects.create_user(
            username="companyuser",
            password="testpass",
            role="COMPANY",
        )

        self.user_regular = User.objects.create_user(
            username="regular",
            password="testpass",
            role="USER",
        )

        # Company
        self.company = Company.objects.create(
            name="TestCo",
            description="Test company",
            owner=self.user_company,
            industry=["tech"],
        )

        self.user_company.company_account = self.company
        self.user_company.save()

        self.job = Job.objects.create(
            title="Software Engineer",
            description="Dev work",
            company=self.company,
            posted_by=self.user_company,
            min_salary=100000,
            max_salary=150000,
            job_type="FULL_TIME",
            work_mode="REMOTE",
            requirements="Python",
            responsibilities="Build features",
            is_autism_friendly=True,
        )

class AuthTests(BaseAPITest):

    def test_register_user(self):
        response = self.client.post("/auth/users/", {
            "username": "newuser",
            "password": "mypass123",
            "password_retype": "mypass123"
        })
        self.assertEqual(response.status_code, 201)

    def test_login_user(self):
        response = self.client.post("/auth/jwt/create/", {
            "username": "regular",
            "password": "testpass"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

class CompanyAPITests(BaseAPITest):

    def test_list_companies(self):
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_company_requires_auth(self):
        response = self.client.post("/api/companies/", {
            "name": "FailCo",
            "description": "Should fail"
        })
        self.assertEqual(response.status_code, 401)

    def test_create_company_success(self):
        authenticate(self.client, "companyuser", "testpass")

        payload = {
            "name": "New Co",
            "description": "Desc",
            "industry": ["tech"],
        }

        response = self.client.post("/api/companies/", payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "New Co")

class JobAPITests(BaseAPITest):

    def test_list_jobs(self):
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, 200)

    def test_filter_jobs_by_company(self):
        response = self.client.get(f"/api/jobs/?company={self.company.id}")
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_cannot_create_job(self):
        response = self.client.post("/api/jobs/", {
            "title": "Nope"
        })
        self.assertEqual(response.status_code, 401)

    def test_company_can_create_job(self):
        authenticate(self.client, "companyuser", "testpass")

        payload = {
            "title": "Backend Engineer",
            "description": "Eng job",
            "company": self.company.id,
            "min_salary": 50000,
            "max_salary": 90000,
            "job_type": "FULL_TIME",
            "work_mode": "REMOTE",
        }

        response = self.client.post("/api/jobs/", payload)
        self.assertEqual(response.status_code, 201)

class StripeTests(BaseAPITest):

    @patch("stripe.checkout.Session.create")
    def test_job_credit_checkout(self, mock_create):
        mock_create.return_value = type("obj", (object,), {"url": "https://stripe-job"})

        authenticate(self.client, "companyuser", "testpass")

        response = self.client.post("/api/stripe/checkout/job-credit/")
        self.assertEqual(response.status_code, 201)
        self.assertIn("url", response.data)

    @patch("stripe.checkout.Session.create")
    def test_subscription_checkout(self, mock_create):
        mock_create.return_value = type("obj", (object,), {"url": "https://stripe-sub"})

        authenticate(self.client, "companyuser", "testpass")

        response = self.client.post("/api/stripe/checkout/subscription/")
        self.assertEqual(response.status_code, 201)

class WebhookTests(BaseAPITest):

    @patch("stripe.Webhook.construct_event")
    def test_webhook_updates_user(self, mock_event):

        mock_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {
                "mode": "payment",
                "client_reference_id": self.user_company.id
            }}
        }

        response = self.client.post("/api/stripe/webhook/", data="{}", content_type="application/json")

        self.assertEqual(response.status_code, 200)

        self.user_company.refresh_from_db()
        self.assertTrue(self.user_company.has_active_job_posting_plan)
