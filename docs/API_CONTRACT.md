# YelpCamp Express API Contract

This document defines the read-only API contract for the YelpCamp Express
backend. The `YelpCampClient` in `app/yelpcamp_client.py` is configured to
target these endpoints.

## Base URL
All requests are prefixed with the base URL configured in the
`YELPCAMP_API_URL` environment variable (e.g. `http://localhost:3000`).

## Authentication
All requests MUST include a service-to-service authentication header.
- Header: `Authorization`
- Value: `Bearer <YELPCAMP_CHAT_SERVICE_TOKEN>`

The token is held exclusively by the Express backend (for validation) and the
MCP/FastAPI backend (for the call). It is **never** exposed to the browser.

## Query / filter parameters
Supported on the search endpoint:
- `keyword` (optional): fuzzy match on title or location.
- `location` (optional): exact match on location.
- `minPrice` / `maxPrice` (optional): non-negative numeric price bounds.
- `limit` (optional): positive integer, default `50`, capped at `100`.

## Endpoints

### 1. Search Campgrounds
`GET /api/chat/campgrounds`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Sunny Pines",
    "location": "California",
    "price": 50.0,
    "description": "Beautiful pine forest."
  }
]
```

### 2. Get Campground Details
`GET /api/chat/campgrounds/:id`

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Sunny Pines",
  "location": "California",
  "price": 50.0,
  "description": "Beautiful pine forest.",
  "reviews": ["Great place!", "Wifi was spotty."]
}
```

### 3. List Campground Reviews
`GET /api/chat/campgrounds/:id/reviews`

**Response (200 OK):**
```json
["Great place!", "Wifi was spotty."]
```

## Errors
All errors are returned as JSON with a generic message; internal details are
never leaked.
- `400` — invalid filter / id.
- `401` — missing or invalid service token.
- `404` — campground not found.
- `429` — rate limit exceeded (see `Retry-After`).
- `500` / `503` — internal / service not configured.

## Notes
- The Express `camp` table has no `features` column, so `features` is not
  part of the public response. The MCP `recommend_campgrounds` tool therefore
  only supports `location` and `budget` against real data.
- `id` is a numeric integer (the PostgreSQL `camp.id`), not a string.
