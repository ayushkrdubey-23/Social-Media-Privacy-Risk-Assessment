# API Reference — Current Project Checkpoint

Base URL during local development:

```text
http://127.0.0.1:5000
```

## Health

### GET `/api/health`

Returns backend health status.

### GET `/api/info`

Returns project and privacy-mode information.

## Questionnaire

### GET `/api/questionnaire`

Returns the complete 50-question questionnaire.

### GET `/api/questionnaire/summary`

Returns questionnaire metadata and category counts.

### GET `/api/questionnaire/question/<question_id>`

Returns one question by its stable ID, such as `Q001`.

### GET `/api/questionnaire/category/<category>`

Returns all questions in one category.

## Assessment

### POST `/api/assessment`

Expected JSON:

```json
{
  "responses": {
    "Q001": "PRIVATE",
    "Q002": "FRIENDS",
    "Q003": "PRIVATE"
  }
}
```

A complete assessment requires all 50 questionnaire answers.

Successful processing returns derived information including:

- assessment ID,
- overall score,
- risk level,
- category scores,
- findings,
- recommendations.

Raw responses are not included in the successful API result.

### GET `/api/assessment/<assessment_id>`

Returns the persisted derived assessment record.

### GET `/api/assessment/<assessment_id>/recommendations`

Returns recommendations associated with the saved assessment's findings.

### DELETE `/api/assessment/<assessment_id>`

Deletes the assessment and its associated derived records.

## Dashboard

### GET `/api/dashboard/stats`

Returns aggregate statistics including:

- total assessments,
- average/minimum/maximum score,
- risk distribution,
- category averages,
- finding severity distribution,
- recommendation priority distribution.

### GET `/api/dashboard/summary`

Returns a compact version of the dashboard statistics.

## Privacy Checklist

### GET `/api/privacy-checklist`

Returns the awareness checklist.

### GET `/api/privacy-checklist/summary`

Returns checklist metadata.

### GET `/api/privacy-checklist/category/<category>`

Returns checklist items for a specific privacy category.

## Error Handling

The API uses structured JSON errors with an error code and message where appropriate. Examples include:

- `VALIDATION_FAILED`
- `QUESTION_NOT_FOUND`
- `CATEGORY_NOT_FOUND`
- `ASSESSMENT_NOT_FOUND`
- `JSON_REQUIRED`
- `REQUEST_TOO_LARGE`

## Privacy Note

These APIs are intentionally designed around self-reported responses and derived results. They do not provide a mechanism for social-media scraping or private-account inspection.
