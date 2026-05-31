# API Testing System - Implementation Guide

## Quick Start: Testing Local APIs

### Step 1: Verify System Running

```bash
# Check if Flask app is running
curl http://localhost:8000/api/status

# Expected response:
# {
#   "status": "ok",
#   "timestamp": "2024-XX-XX..."
# }
```

### Step 2: Open Chat Interface

Navigate to: `http://localhost:8000/chat`

### Step 3: Scan Repository

1. Enter repository path: `/app/src`
2. Click "🚀 Scan Repository"
3. Wait for scan to complete

### Step 4: View Discovered APIs

Scan results will show:

- **🧪 Testable Endpoints (Local)** - These can be tested immediately
  - Source: `/app/src` code
  - Base URL: `http://localhost:8000`
  - Test buttons: Enabled ✅

- **📖 Documentation Only (External)** - These are for reference
  - Source: External repositories
  - Status: Requires deployment + configuration

### Step 5: Test APIs

Click individual "Test" button or "🧪 Test All APIs" to run tests.

Results show:
```
✅ GET /api/orders — Status: 200 | Time: 45ms
❌ POST /api/users — Status: 404 | Time: 12ms (endpoint not found)
```

## Advanced: Testing External Repository APIs

### Scenario: You discovered APIs from Gaslite repo, now it's deployed

#### Step 1: Configure the Endpoint

```bash
curl -X POST http://localhost:8000/api/test/configure-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "api_path": "/api/orders",
    "base_url": "https://gaslite-api.example.com",
    "environment": "production"
  }'
```

#### Step 2: Now Test Uses New Base URL

```bash
curl -X POST http://localhost:8000/api/test/run \
  -H "Content-Type: application/json" \
  -d '{
    "api_path": "/api/orders",
    "method": "GET"
  }'

# Will test against: https://gaslite-api.example.com/api/orders
```

#### Step 3: In UI, Tests Show Results

Tests should now succeed if the endpoint exists at the configured URL.

## Understanding the Architecture

### Why Are APIs Marked as Testable or Not?

**Testable APIs** (`testable: true`):
- Found in code being scanned locally
- Running on localhost:8000 (or configured URL)
- Ready to test immediately
- Example: Flask routes in `/app/src/app.py`

**External APIs** (`testable: false`):
- Found in external GitHub repos via scanning
- NOT running locally
- Cannot test without:
  1. Deploying that service
  2. Configuring its URL
  3. Possibly setting up authentication
- Example: APIs in Gaslite repo that aren't deployed

### The Three Testing Scenarios

```
Scenario 1: Enterprise Platform Only (MVP)
  Input: /app/src
  APIs Found: 28 local endpoints
  Testable: All 28 ✅
  Test Result: Tests against localhost:8000
  
Scenario 2: Local + External Documentation
  Input: /app/src + GitHub Gaslite repo scanned
  APIs Found: 28 local + 28 external
  Testable: 28 local ✅, 28 external 📖
  Test Result: Only 28 local tested, external shown as reference
  
Scenario 3: Multi-Environment Testing
  Input: Same as Scenario 2, but Gaslite deployed at staging URL
  Configuration: POST /api/test/configure-endpoint (Gaslite URL)
  Testable: 28 local + 28 external ✅
  Test Result: All 56 tested (28 at localhost, 28 at staging)
```

## API Endpoints Reference

### Discovery & Analysis

**GET /api/chat/artifacts/{session_id}**

Returns all discovered artifacts with metadata:

```json
{
  "apis": [
    {
      "path": "/api/orders",
      "methods": ["GET", "POST"],
      "file": "routes/orders.py",
      "testable": true,
      "base_url": "http://localhost:8000",
      "source": "local"
    }
  ],
  "functions": [...],
  "dependencies": [...]
}
```

### Testing

**POST /api/test/run**

Test a single endpoint:

```json
{
  "api_path": "/api/orders",
  "method": "GET",
  "base_url": "http://localhost:8000",  // Optional, uses default if not provided
  "timeout": 5
}
```

**POST /api/test/batch**

Test multiple endpoints at once.

**POST /api/test/validate-endpoints**

Check which endpoints actually exist (with testability filtering):

```json
{
  "validated_endpoints": [..],      // Endpoints that exist
  "invalid_endpoints": [..],         // 404s
  "skipped_external": [..]          // External APIs (require config)
}
```

### Configuration

**POST /api/test/configure-endpoint**

Set base URL for testing an API:

```json
{
  "api_path": "/api/orders",
  "base_url": "https://staging-api.example.com",
  "environment": "staging"
}
```

Configuration persists for 1 hour or until cleared.

## Troubleshooting

### Problem: "All discovered APIs return 404"

**Cause**: System tried to test external repository APIs against localhost:8000

**Solution**: 
1. Check if API is marked `testable: true` or `false`
2. If `testable: false`, it's from external repo - needs configuration
3. If `testable: true` but still 404:
   - API endpoint might not exist in local code
   - Check file path in discovery results
   - Verify Flask/Express route syntax

### Problem: "Test button is greyed out"

**Cause**: API is marked as external/documentation-only

**Solution**:
1. Deploy the external service
2. Configure its URL: `POST /api/test/configure-endpoint`
3. Test button will become enabled

### Problem: "Configuration doesn't seem to work"

**Cause**: Redis cache expired (1 hour timeout) or not configured

**Solution**:
1. Reconfigure endpoint: `POST /api/test/configure-endpoint`
2. Check Redis is running: `curl http://localhost:6379/health`
3. If no Redis, configuration won't persist between requests

### Problem: "See 'connection_error' in validation results"

**Cause**: Cannot reach the base URL

**Solutions**:
- Check if service is running at configured URL
- Verify network connectivity
- Confirm base_url format (include http:// or https://)
- Check for firewall/CORS issues

## Common Workflows

### Workflow 1: Quick Local API Testing

```
1. Open http://localhost:8000/chat
2. Path: /app/src
3. "Scan Repository"
4. "Test All APIs"
5. View results
Time: ~2-3 minutes
```

### Workflow 2: Test External Repo After Deployment

```
1. Scan external repo in chat
2. Note: APIs show as "Documentation Only"
3. Deploy external service
4. Get service URL
5. POST /api/test/configure-endpoint with new URL
6. Click "Test" button (now enabled)
7. View results
Time: ~5 minutes + deployment time
```

### Workflow 3: Compare Environments

```
1. Configure API for development:
   POST /api/test/configure-endpoint
   {"api_path": "/api/orders", "base_url": "http://localhost:8000", "environment": "development"}

2. Run tests
   POST /api/test/run {"api_path": "/api/orders", "method": "GET"}

3. Reconfigure for staging:
   POST /api/test/configure-endpoint
   {"api_path": "/api/orders", "base_url": "https://staging.example.com", "environment": "staging"}

4. Run same tests again
   Compare results between environments
Time: ~5 minutes
```

## Implementation Checklist

✅ Code Changes:
- [x] repo_chat.py - Add metadata to APIs
- [x] chat.html - Separate UI display
- [x] app.py - Add endpoints & validation

Ready for:
- [ ] Testing
- [ ] Deployment
- [ ] User feedback

## Next Steps

After deploying these changes:

1. **Test locally**: Follow "Quick Start" section above
2. **Verify filtering**: Ensure external APIs are properly separated
3. **Test configuration**: Use `/api/test/configure-endpoint` endpoint
4. **Document**: Share this guide with team members

## Architecture Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    Repository Chat Interface                     │
│  http://localhost:8000/chat                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    [User enters repo path]
                             │
                    [System scans code]
                             │
                ┌────────────┴────────────┐
                │                         │
         Local APIs                  External APIs
        (from /app/src)        (from GitHub repos)
         ✅ Testable            📖 Documentation
         ∎ Test Buttons         ∎ Info Only
         ∎ Green Border         ∎ Purple Border
                │                         │
                ├─→ [User clicks Test] ←─┤
                │                         │
         [Test at                  [Requires config]
         localhost:8000]                 │
                │                  [User provides URL]
         [Results: ✅]           [Configuration stored]
                │                    │
                └────────────┬───────┘
                             │
                    [Test results shown]
                             │
                    ✅ 28/28 tests pass
                    📊 Full coverage
```

---

**Need help?** Check the full architecture document at `/app/src/API_TESTING_ARCHITECTURE.md`
