# API Testing System - Architectural Fix

## Problem Statement

The API testing system was discovering APIs from external GitHub repositories (e.g., Gaslite) but then attempting to test them against `localhost:8000`, causing 404 errors on all discovered endpoints.

**Root Cause**: Conflation of two different API types:
1. **Local APIs** - Defined in `/app/src`, running on localhost:8000, testable immediately
2. **Documentation APIs** - Discovered from external repositories, not running locally, not testable without deployment

## Architectural Decision

Implement a **hybrid model** that supports both local and external API testing:

### Three-Tier Classification

```
APIs
├── Local/Testable ✅
│   ├── Source: Local code repository
│   ├── Default Base URL: http://localhost:8000
│   ├── Testable: Immediately
│   └── Example: POST /api/orders (from /app/src/app.py)
│
├── External/Documentation 📖
│   ├── Source: Scanned GitHub repositories
│   ├── Default Base URL: Not set (requires configuration)
│   ├── Testable: Only when deployed and base URL configured
│   └── Example: POST /api/orders (discovered in Gaslite repo)
│
└── Configuration-Overridden 🔧
    ├── Source: Any API with user-provided base URL
    ├── Base URL: User-specified
    ├── Testable: When endpoint exists at configured URL
    └── Use Case: Testing staging/production versions
```

## Implementation Details

### 1. API Metadata Enrichment

Each discovered API now includes:

```python
api = {
    "path": "/api/orders",
    "methods": ["GET", "POST"],
    "file": "routes/orders.py",
    "type": "express_route",
    
    # NEW: Testability metadata
    "testable": True,              # Can be tested?
    "base_url": "http://localhost:8000",  # Where to test
    "source": "local",             # Origin: local | external
    "environment": "development"   # dev | staging | production
}
```

### 2. Discovery Logic Changes

**repo_chat.py** - `_extract_apis()`:
- APIs extracted from local files are marked `testable: true`
- APIs from external repos would be marked `testable: false` (future enhancement)
- Default base_url is set to `http://localhost:8000` for local APIs

### 3. UI Changes

**chat.html** - Visual Separation:

```
🧪 Testable Endpoints (Local) ← Green border, test buttons enabled
├─ ✅ GET /api/orders
├─ ✅ POST /api/users
└─ ✅ DELETE /api/driver-applications

📖 Documentation Only (External) ← Purple border, test button hidden, informational
├─ 📖 GET /api/external-endpoint
└─ ℹ️ "Deploy this service separately to test"
```

### 4. New API Endpoints

#### `/api/test/validate-endpoints` (Enhanced)

```json
POST /api/test/validate-endpoints
Request:
{
  "apis": [...],
  "base_url": "http://localhost:8000"
}

Response:
{
  "validated_endpoints": [...],      // Found and working
  "invalid_endpoints": [...],         // Not found (404)
  "skipped_external": [...]          // External repos, skipped
  "validation_summary": {
    "total_checked": 50,
    "local_apis": 28,
    "external_apis": 22,
    "valid": 28,
    "invalid": 0,
    "valid_percentage": "100%"
  }
}
```

#### `/api/test/configure-endpoint` (New)

```json
POST /api/test/configure-endpoint
Request:
{
  "api_path": "/api/orders",
  "base_url": "https://staging-api.example.com",
  "environment": "staging"
}

Response:
{
  "status": "success",
  "api_path": "/api/orders",
  "base_url": "https://staging-api.example.com",
  "environment": "staging"
}
```

Used for:
- Testing external repository APIs after they're deployed
- Testing different environments (dev/staging/prod)
- Overriding defaults for local development

### 5. Test Execution Flow

```
User clicks "Test All APIs"
    ↓
Client filters to testable APIs only (testable: true)
    ↓
Skip external/documentation APIs
    ↓
For each testable API:
    1. Retrieve configuration (if exists in Redis)
    2. Use configured base_url or default
    3. Execute test
    4. Report results
    ↓
Display:
- ✅ Passed tests
- ❌ Failed tests (with reason)
- ℹ️ Skipped tests (with explanation)
```

## Code Changes

### 1. repo_chat.py

**Change**: Enhanced `_extract_apis()` method

```python
# Before:
apis.append({
    "path": route,
    "methods": methods_list,
    "type": "flask_route"
})

# After:
apis.append({
    "path": route,
    "methods": methods_list,
    "type": "flask_route",
    "testable": True,                          # NEW
    "base_url": "http://localhost:8000",      # NEW
    "source": "local",                         # NEW
    "environment": "development"               # NEW
})
```

### 2. chat.html

**Change**: Visual separation of testable vs external APIs

```javascript
// Before:
apisList.innerHTML = apis.map(api => /* render all uniformly */)

// After:
const testableAPIs = apis.filter(api => api.testable !== false);
const externalAPIs = apis.filter(api => api.testable === false);

// Render testable APIs with test buttons
// Render external APIs with info message instead
```

### 3. app.py

**Changes**:
- Enhanced `/api/test/validate-endpoints` to filter testable vs external
- New `/api/test/configure-endpoint` for base URL configuration
- Updated `/api/test/run` to check Redis for configured base URLs

## Migration Path

### Phase 1: Local API Testing (MVP) ✅
- Discover APIs from local code only
- Test against localhost:8000
- **Status**: Implemented

### Phase 2: External Repository Documentation
- Discover APIs from GitHub repos
- Mark as `testable: false`
- Show in UI for reference only
- **Status**: Ready for implementation

### Phase 3: Multi-Environment Testing
- Allow users to configure base URLs
- Test against staging/production
- Store configurations in Redis
- **Status**: Endpoints ready

### Phase 4: Deployment Integration
- Auto-detect when external repos are deployed
- Update base URLs from CD/CI webhooks
- Test deployed external APIs
- **Status**: Future enhancement

## Usage Examples

### Example 1: Test Local APIs (Default Behavior)

1. User enters `/app/src` in repository input
2. System scans and finds local Flask routes
3. Marks all as `testable: true, base_url: http://localhost:8000`
4. UI shows all with test buttons
5. User clicks "Test All APIs"
6. Results show: 28/28 endpoints responding

### Example 2: Mixed Repository (Local + External References)

1. User scans repository that imports external APIs
2. Discovery finds:
   - Local routes: `/api/users` → testable ✅
   - External refs: `/api/external-service` → documentation 📖
3. UI shows:
   - Local: Testable, with test buttons
   - External: Info banner, no test buttons
4. User can configure external endpoint base URL if service is deployed
5. After configuration, test buttons become available

### Example 3: Test Staging Environment

```bash
# Configure staging API
curl -X POST http://localhost:8000/api/test/configure-endpoint \
  -H "Content-Type: application/json" \
  -d '{
    "api_path": "/api/orders",
    "base_url": "https://staging-api.example.com",
    "environment": "staging"
  }'

# Run test (will use staging URL)
curl -X POST http://localhost:8000/api/test/run \
  -H "Content-Type: application/json" \
  -d '{
    "api_path": "/api/orders",
    "method": "GET"
  }'
# → Tests against https://staging-api.example.com/api/orders
```

## Benefits

1. **Clarity**: Users instantly see which APIs can be tested locally
2. **Flexibility**: Support for external repos when deployed
3. **Scalability**: Multi-environment testing with configuration
4. **Debuggability**: Clear reasons why APIs can/cannot be tested
5. **User Experience**: No more confusing 404 errors
6. **Documentation**: Discovered external APIs serve as reference material

## Future Enhancements

1. **Webhook Integration**: Auto-update base URLs when external repos deploy
2. **API Versioning**: Track multiple versions of same endpoint
3. **Test Profiles**: Save and reuse common test configurations
4. **CI/CD Integration**: Automatic validation in PR checks
5. **API Mocking**: Mock external APIs for testing without deployment
6. **Documentation Generation**: Convert tests to OpenAPI specs

## Testing the Fix

### Test Case 1: Local APIs Show as Testable

```bash
POST /api/chat/scan/SESSION_ID
# Scan /app/src

GET /api/chat/artifacts/SESSION_ID
# Check response: all APIs have testable: true

POST /api/test/batch
# Should show all tests passing for localhost:8000 APIs
```

### Test Case 2: Configuration Persistence

```bash
POST /api/test/configure-endpoint
{
  "api_path": "/api/orders",
  "base_url": "https://external.com"
}

POST /api/test/run
{
  "api_path": "/api/orders",
  "method": "GET"
}
# Should use https://external.com (not localhost:8000)
```

### Test Case 3: Validation Filtering

```bash
POST /api/test/validate-endpoints
# skipped_external should show any non-testable APIs
# Summary should show: local_apis + external_apis = total_checked
```

## Deployment Notes

1. Update `repo_chat.py` - Add metadata to discovered APIs
2. Update `chat.html` - Separate UI display logic
3. Update `app.py` - Add validation and configuration endpoints
4. Restart Flask service
5. Clear any cached API discovery results

**No database migrations required** - metadata is in-memory or Redis-stored.

## Questions?

For implementation details or clarifications on the architectural decision, see:
- `/api/chat/artifacts/{session_id}` - Returns APIs with metadata
- `/api/test/validate-endpoints` - Shows testability status
- `/api/test/configure-endpoint` - Sets custom base URLs
