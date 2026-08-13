# TofuPilot Python Client Tests

End-to-end tests for the TofuPilot Python SDK.

## Setup

1. Configure environment variables in `clients/.env.local` (shared by all client
   test suites, loaded by `tests/conftest.py`):
   ```bash
   TOFUPILOT_URL=http://localhost:3000
   TOFUPILOT_API_KEY_USER=your-user-api-key
   TOFUPILOT_API_KEY_STATION=your-station-api-key
   ```
   The session procedure is created automatically and the station is linked to it
   by the conftest (station id resolved from the station key itself).

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/v2/runs/create/test_sub_units_lifecycle.py

# Run with verbose output
python -m pytest -v
```

## Testing Against Vercel Preview Deployments

Point `TOFUPILOT_URL` at the preview:

```bash
TOFUPILOT_URL=https://your-preview-deployment.vercel.app
```

The suite only works while [Deployment Protection](https://vercel.com/docs/security/deployment-protection)
is off on that project. Nothing here injects a protection bypass header — if
protection is turned back on, every request 401s before it reaches the API, and
the bypass has to be implemented in the fixtures first.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TOFUPILOT_URL` | API base URL (e.g., `http://localhost:3000`) |
| `TOFUPILOT_API_KEY_USER` | User API key for authentication |
| `TOFUPILOT_API_KEY_STATION` | Station API key for authentication |
