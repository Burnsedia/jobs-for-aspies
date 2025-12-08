# AspieJobs Development Roadmap

This document outlines the planned features and development phases for the AspieJobs project. Our goal is to build a comprehensive and valuable platform for the autistic community.

This project is licensed under the AGPLv3. All contributions are subject to this license.

---

## Phase 1: Core MVP (In Progress)

This phase focuses on launching a functional, public job board that delivers immediate value to job seekers.

*   **Backend API:** Develop a robust REST API with Django and Django REST Framework.
*   **Database Schema:** Define models for `Job`, `Company`, and `Tag`.
*   **Tagging System:** Implement a tagging system for job attributes using `django-taggit`.
*   **Job Scraping:** Create a cron job or management command using `Scrapy` to automatically populate the job board from various sources.
*   **Admin Job Approval:** Use the Django Admin panel for manual review and approval of all jobs.
*   **Frontend Application:** Build the user-facing website with Astro and Vue.js.
*   **Core Pages:** Develop the Job Listings page, Job Detail page, and Company Profile pages.
*   **Filtered Search:** Implement the front-end logic for filtering jobs by keywords, location, and the neurodiversity-specific tags.

---

## Phase 2: Personalization and AI

Once the core platform is stable and has an audience, we will introduce personalization features.

*   **User Accounts:** Implement a system for job seekers to sign up, log in, and create profiles.
*   **User Profiles:** Allow users to save their skills, experience, and, most importantly, their preferred workplace attributes and tags.
*   **AI Matching Engine:** Develop a system to analyze job descriptions and user profiles to generate a "match score."
*   **Personalized Job Feeds:** Display a "Recommended for You" section for logged-in users.
*   **Email Job Alerts:** Allow users to subscribe to email notifications for new jobs that match their profile.

---

## Phase 3: Monetization and Growth

This phase focuses on ensuring the long-term sustainability of the project.

*   **Employer Accounts:** Create a full dashboard for employers to log in, post jobs directly, and manage their company profile.
*   **Payment Integration:** Integrate a payment processor (e.g., Stripe) to allow for paid job postings.
*   **Featured Jobs:** Allow employers to pay to have their jobs featured on the homepage or at the top of search results.
*   **Analytics:** Provide simple analytics for employers on their job post performance.

---

## Phase 4: Mobile and Community

This phase focuses on expanding the platform's reach and building a community.

*   **Progressive Web App (PWA):** Enhance the web application with full PWA capabilities for offline access and an installable experience.
*   **App Store Submission:** Package the PWA for submission to the Google Play Store and Apple App Store (pending quality guidelines).
*   **Community Forum:** Consider adding a forum or discussion board for users to share experiences and advice.
*   **Resource Library:** Build a collection of articles, guides, and resources for both job seekers and employers on neurodiversity in the workplace.

## How to Contribute

We welcome contributors of all skill levels! If you'd like to contribute, please check our `CONTRIBUTING.md` file, and feel free to pick up an issue or a feature from this roadmap.
ake it a reality. If you're interested in contributing to any of these features, please start a discussion in the project's issue tracker.

## License

This project is licensed under the GNU Affero General Public License v3.0. All contributions to this project will be licensed under the same.
