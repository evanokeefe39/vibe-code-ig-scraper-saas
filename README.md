# Vibe Scraper SaaS

A lightweight B2C SaaS that curates location-based recommendations from social media profiles into personalized lists for Google Maps. Evolving towards an agentic platform where AI agents dynamically orchestrate scraping operations based on user goals and cost constraints.

## Prerequisites

### Database Setup

This project uses PostgreSQL for data storage.

1. Start PostgreSQL with Docker: `docker-compose up -d postgres`
2. Run migrations: `python manage.py migrate`
3. Create superuser (optional): `python manage.py createsuperuser`

### Development Setup

1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Activate shell: `poetry shell`
4. Run Django: `python manage.py runserver`

### Geocoding Setup

This project uses Mapbox for geocoding services. To set up:

1. Sign up for a Mapbox account at [mapbox.com](https://account.mapbox.com/)
2. Create an access token in Account > Access Tokens
3. Set the environment variable: `MAPBOX_ACCESS_TOKEN=your_token_here`
4. For development, you can use Nominatim (OpenStreetMap) as a fallback without an API key

See [geocoding-providers.md](geocoding-providers.md) for detailed provider information.

## Requirements

See [functional-requirements.md](functional-requirements.md) and [non-functional-requirements.md](non-functional-requirements.md).

## Architecture

See [architecture.md](architecture.md).

## Roadmap

See [roadmap.md](roadmap.md).