// Shared API contract types — kept in sync with backend/app/schemas/api.py
// Auto-regenerate: npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts

export interface HealthResponse {
  status: string
}
