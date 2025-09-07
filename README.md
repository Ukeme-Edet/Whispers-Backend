# Whispers Backend

Backend services for Whispers, an anonymous messaging platform.
Live app: https://whispers-gray.vercel.app

## Overview

Whispers enables people to receive anonymous messages via a shareable link while protecting recipients from abuse and spam. This repository hosts the server-side APIs, data access, and operational safeguards that power the experience.

## Core Capabilities

-   Anonymous message submission to a recipient’s public handle or link
-   Recipient inbox retrieval with pagination
-   Basic abuse protections (e.g., rate limits, content checks, IP throttling)
-   Optional moderation endpoints and message lifecycle controls (create, read, hide/delete, expire)
-   Observability hooks (logging/metrics) for safe operations

Note: Exact routes, models, and middleware may vary by implementation. Review the codebase for authoritative details.

## Quick Start

Prerequisites:

-   Node.js LTS (v18+ recommended)
-   npm or pnpm
-   A database (configure your connection string in .env)

Setup:

1. Clone the repository
2. Install dependencies: npm install
3. Create a .env file (see example below)
4. Start the dev server: npm run dev
5. Build and run production: npm run build && npm start

If your scripts differ, check package.json for available commands.

## Configuration

Create a .env file in the project root. Add the variables used by the app. Below is a common example (adjust to your stack):

```
# Server
PORT=3000
NODE_ENV=development
CORS_ORIGIN=https://whispers-gray.vercel.app

# Database
DATABASE_URL=postgres://user:pass@host:5432/whispers
# or for Mongo: mongodb+srv://user:pass@cluster/db

# Security
JWT_SECRET=change_me
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=60

# Optional
LOG_LEVEL=info
```

-   Keep secrets out of version control.
-   Align CORS_ORIGIN with the deployed frontend URL.
-   Choose a stable, managed database for production.

## Development Notes

-   Linting/formatting: npm run lint / npm run format (if configured)
-   Tests: npm test (add unit/integration tests for routes and services)
-   Migrations/seed: use your ORM/driver’s migration tool (e.g., Prisma, Knex, Sequelize) if applicable
-   Logging: prefer structured logs; avoid logging PII

## API Usage

Typical flows:

-   POST a message to a recipient’s public identifier
-   GET a recipient’s inbox (authenticated)
-   PATCH/DELETE to moderate or remove messages (authorized)

Use curl or an HTTP client to exercise routes locally:

```
# Example (adjust route names and payloads to your implementation)
curl -X POST http://localhost:3000/api/messages \
    -H "Content-Type: application/json" \
    -d '{"to":"<recipient_handle>","content":"Hello 👋"}'
```

For a definitive contract, consult:

-   Route handlers (e.g., src/routes, api/ directory)
-   Any OpenAPI/Swagger file if present
-   Integration tests as living documentation

## Deployment

-   Environment: set production variables securely (secrets manager)
-   Platform: any Node-compatible host (e.g., Vercel serverless, Render, Railway, Fly.io, AWS)
-   Build: npm ci && npm run build
-   Start: npm start (or platform adapter for serverless functions)
-   Observability: enable logs, metrics, and alerts; set LOG_LEVEL appropriately

## Security and Privacy

-   Honor anonymity: never expose sender identity or IP
-   Apply rate limiting and content validation to reduce abuse
-   Sanitize inputs to prevent injection attacks
-   Use HTTPS everywhere; rotate secrets periodically
-   Data retention: define and implement message lifecycle policies
-   Comply with regional data regulations where applicable

## Contributing

-   Open an issue for bugs or proposals
-   Create a small, focused PR with clear description and tests
-   Follow code style and commit conventions used in the repo

## License

See LICENSE file in this repository.

## Support

-   Issues: open a GitHub issue with steps to reproduce
-   Operations: include logs, environment, and versions when reporting problems

Build thoughtfully and be kind. ✨
