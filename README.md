# AspieJobs

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-AGPLv3-blue)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange)

**A job board designed with the autistic community in mind, connecting neurodivergent talent with inclusive employers.**

## Our Mission

The modern workplace can be a challenging environment to navigate for autistic individuals. AspieJobs aims to bridge this gap by creating a platform where job seekers can find roles at companies that are genuinely committed to neurodiversity and inclusion. We focus on highlighting job attributes that matter, such as sensory-friendly environments, flexible schedules, and clear communication protocols, making the job search process more transparent and accessible.

## Key Features

*   **Neurodiversity-First Filtering:** Search for jobs using tags that are critical for the autistic community (e.g., `Sensory-Friendly`, `Flexible Schedule`, `Mentorship Provided`).
*   **Curated Job Listings:** Jobs are sourced and curated to ensure they are from companies that value neurodivergent talent.
*   **In-Depth Company Profiles:** Learn about a company's culture and their commitment to inclusion before you apply.
*   **AI-Powered Matching:** (Coming Soon!) A system to match user profiles with the most suitable job openings based on skills and neurodiversity needs.

## Tech Stack

*   **Backend:** Python, Django, Django REST Framework
*   **Frontend:** Astro, Vue.js
*   **Database:** PostgreSQL
*   **Libraries:** `django-taggit` for tagging, `Scrapy` for data scraping.

## Getting Started

This project is a decoupled application with a Django backend and an Astro/Vue frontend.

### Prerequisites

*   Python 3.10+
*   Node.js 18+
*   Poetry for Python package management
*   `npm` or `yarn` for Node.js package management

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/aspiejobs.git
cd aspiejobs/backend

# Install dependencies
poetry install

# Apply migrations
poetry run python manage.py migrate

# Run the development server
poetry run python manage.py runserver
```

### Frontend Setup

```bash
# In a new terminal, navigate to the frontend directory
cd aspiejobs/frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

## How to Contribute

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. We welcome any contributions, from fixing bugs and improving documentation to implementing new features.

Please read our `CONTRIBUTING.md` file for details on our code of conduct and the process for submitting pull requests. Check out the `ROADMAP.md` to see where the project is headed and find features you'd like to work on!

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the `LICENSE` file for details.