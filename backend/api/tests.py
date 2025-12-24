from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from api.models import User, Company, Job, Portfolio, Project


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
            role="JOB_SEEKER",
        )

        # Company
        self.company = Company.objects.create(
            name="TestCo",
            description="Test company",
            owner=self.user_company,
            industry=["tech"],
        )

        self.user_company.company_account = self.company
        self.user_company.has_active_job_posting_plan = True  # Give them a job posting credit
        self.user_company.save()

        self.job = Job.objects.create(
            title="Software Engineer",
            description="Dev work",
            company=self.company,
            posted_by=self.user_company,
            min_salary=100000,
            max_salary=150000,
            job_type="FT",
            work_mode="REMOTE",
            remote_level="FULL_REMOTE",
            async_level="FULL_ASYNC",
            requirements="Python",
            responsibilities="Build features",
            is_remote_friendly=True,
        )

class AuthTests(BaseAPITest):

    def test_register_user(self):
        response = self.client.post("/auth/users/", {
            "username": "newuser",
            "password": "mypass123",
            "re_password": "mypass123"
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
            "apply_url": "https://example.com/apply",
            "min_salary": 50000,
            "max_salary": 90000,
            "job_type": "FT",
            "work_mode": "REMOTE",
            "remote_level": "FULL_REMOTE",
            "async_level": "FULL_ASYNC",
            "tech_tags": ["python", "django"],
        }

        response = self.client.post("/api/jobs/", payload)
        self.assertEqual(response.status_code, 201)

    def test_filter_jobs_by_skills(self):
        # Create a job with specific skills
        job = Job.objects.create(
            title="Frontend Developer",
            description="React development",
            company=self.company,
            posted_by=self.user_company,
            job_type="FT",
            work_mode="REMOTE",
            remote_level="FULL_REMOTE",
            async_level="FULL_ASYNC",
            requirements="JavaScript, React",
        )
        job.tech_tags.add("react", "javascript")

        # Test filtering by skills
        response = self.client.get("/api/jobs/?tech_tags__name=react")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_jobs_by_remote_level(self):
        response = self.client.get("/api/jobs/?remote_level=FULL_REMOTE")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_jobs_by_async_level(self):
        response = self.client.get("/api/jobs/?async_level=FULL_ASYNC")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

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


class PortfolioAPITests(BaseAPITest):

    def setUp(self):
        super().setUp()
        # Create portfolio for the regular user
        self.portfolio = Portfolio.objects.create(
            user=self.user_regular,
            bio="Experienced Python developer",
            years_experience=5,
            available_for_hire=True,
            open_to_remote=True,
        )
        self.portfolio.skills.add("python", "django", "react")

        # Create a project
        self.project = Project.objects.create(
            portfolio=self.portfolio,
            title="E-commerce Platform",
            description="Built a full-stack e-commerce solution",
            tech_stack=["python", "django", "react"],
            github_url="https://github.com/user/ecommerce",
            live_url="https://ecommerce-demo.com",
        )

    def test_get_portfolio_list(self):
        authenticate(self.client, "regular", "testpass")
        response = self.client.get("/api/portfolios/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_portfolio_detail(self):
        authenticate(self.client, "regular", "testpass")
        response = self.client.get(f"/api/portfolios/{self.portfolio.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["bio"], "Experienced Python developer")

    def test_create_portfolio(self):
        # Create a new user for this test
        new_user = User.objects.create_user(
            username="portfolio_user",
            password="testpass",
            role="JOB_SEEKER",
        )

        authenticate(self.client, "portfolio_user", "testpass")
        payload = {
            "bio": "Full-stack developer specializing in React and Node.js",
            "years_experience": 3,
            "skills": ["react", "nodejs", "typescript"],
            "available_for_hire": True,
            "open_to_remote": True,
        }

        response = self.client.post("/api/portfolios/", payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["bio"], payload["bio"])

    def test_update_portfolio(self):
        authenticate(self.client, "regular", "testpass")
        payload = {
            "bio": "Updated bio with more experience",
            "years_experience": 6,
        }

        response = self.client.patch(f"/api/portfolios/{self.portfolio.id}/", payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["years_experience"], 6)

    def test_get_portfolio_projects(self):
        authenticate(self.client, "regular", "testpass")
        response = self.client.get(f"/api/portfolios/{self.portfolio.id}/projects/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "E-commerce Platform")

    def test_create_project(self):
        authenticate(self.client, "regular", "testpass")
        payload = {
            "title": "Portfolio Website",
            "description": "Personal portfolio built with Next.js",
            "tech_stack": ["react", "nextjs", "tailwind"],
            "github_url": "https://github.com/user/portfolio",
            "live_url": "https://portfolio-demo.com",
        }

        response = self.client.post(f"/api/portfolios/{self.portfolio.id}/projects/", payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Portfolio Website")

    def test_portfolio_skills_filtering(self):
        authenticate(self.client, "regular", "testpass")
        response = self.client.get("/api/portfolios/?skills__name=python")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_portfolio_availability_filtering(self):
        authenticate(self.client, "regular", "testpass")
        response = self.client.get("/api/portfolios/?available_for_hire=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get("/api/portfolios/?available_for_hire=false")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    def test_portfolio_remote_preference_filtering(self):
        authenticate(self.client, "regular", "testpass")
        response = self.client.get("/api/portfolios/?open_to_remote=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
