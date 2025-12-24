# AsyncSkills

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-AGPLv3-blue)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange)

**A skills-first job board for remote/async work, connecting talent through portfolios and demonstrable abilities instead of traditional interviews.**

## Our Mission

Traditional job interviews often focus on "tell me about yourself" questions that disadvantage skilled professionals who struggle with social communication. AsyncSkills revolutionizes hiring by emphasizing demonstrable skills, portfolios, and take-home projects. We connect talented individuals with companies offering remote and asynchronous work arrangements, creating opportunities for everyone to showcase their abilities on their own terms.

## Key Features

*   **Skills-First Matching:** Showcase your portfolio and GitHub projects instead of traditional resumes and interviews.
*   **Remote/Async Focus:** Jobs specifically designed for remote work and asynchronous communication.
*   **Take-Home Projects:** Companies can create coding challenges and skill assessments for candidates.
*   **Portfolio Integration:** Direct GitHub OAuth integration to display your repositories and contributions.
*   **Inclusive Hiring:** Designed to reduce bias by focusing on demonstrable skills over social interviews.

## Tech Stack

*   **Backend:** Python, Django, Django REST Framework
*   **Frontend:** Astro, Vue.js
*   **Database:** SQLite (development) / PostgreSQL (production)
*   **Libraries:** `django-taggit` for tagging, `Scrapy` for data scraping, `dj-stripe` for payments

## Getting Started

This project is a decoupled application with a Django backend and an Astro/Vue frontend, specifically designed for Atlanta's tech job market.

### Prerequisites

*   Python 3.10+
*   Node.js 18+
*   Poetry for Python package management
*   `npm` or `yarn` for Node.js package management

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/asyncskills.git
cd asyncskills/backend

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver
```

### Frontend Setup

```bash
# In a new terminal, navigate to the frontend directory
cd asyncskills/frontend

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

The AGPLv3 ensures that AsyncSkills remains free and open source. If you deploy this software as a service, you must also make your modifications available under AGPLv3. This protects the community's access to the codebase while allowing commercial use.
