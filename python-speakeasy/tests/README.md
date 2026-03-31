# TofuPilot Python Client Tests

End-to-end tests for the TofuPilot Python SDK.

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure environment variables in `.env`:
   ```bash
   TOFUPILOT_URL=http://localhost:3000
   TOFUPILOT_API_KEY_USER=your-user-api-key
   TOFUPILOT_API_KEY_STATION=your-station-api-key
   TOFUPILOT_PROCEDURE_ID=your-procedure-id
   ```

3. Install dependencies:
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

For testing against Vercel preview deployments with [Deployment Protection](https://vercel.com/docs/security/deployment-protection) enabled:

1. Get your bypass secret from Vercel Dashboard:
   - Project Settings > Deployment Protection > Protection Bypass for Automation

2. Add to your `.env`:
   ```bash
   TOFUPILOT_URL=https://your-preview-deployment.vercel.app
   VERCEL_AUTOMATION_BYPASS_SECRET=your-bypass-secret
   ```

The test fixtures automatically inject the bypass header when `VERCEL_AUTOMATION_BYPASS_SECRET` is set.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TOFUPILOT_URL` | API base URL (e.g., `http://localhost:3000`) |
| `TOFUPILOT_API_KEY_USER` | User API key for authentication |
| `TOFUPILOT_API_KEY_STATION` | Station API key for authentication |
| `TOFUPILOT_PROCEDURE_ID` | Procedure ID for V1 tests |
| `VERCEL_AUTOMATION_BYPASS_SECRET` | (Optional) Vercel deployment protection bypass |
