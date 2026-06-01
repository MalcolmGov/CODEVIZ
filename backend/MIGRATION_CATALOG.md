# Business Logic Migration Catalog

## Core Modules (Fully Preserved)
- ✅ repo_chat.py → core/scanner_legacy.py (Repository scanning)
- ✅ security_bug_detector.py → core/security_detector_legacy.py (Security analysis)
- ✅ performance_analyzer.py → core/performance_analyzer_legacy.py (Performance)
- ✅ refactoring_detector.py → core/refactoring_detector_legacy.py (Refactoring detection)
- ✅ ai_refactorer.py → core/ai_refactorer_legacy.py (AI refactoring)
- ✅ automated_fix_generator.py → core/auto_fix_generator_legacy.py (Auto-fixes)
- ✅ code_smell_detector.py → core/code_smell_detector_legacy.py (Code smells)

## Service Integrations (Fully Preserved)
- ✅ github_scanner.py → services/github_legacy.py (GitHub API)
- ✅ slack_bot_integration.py → services/slack_legacy.py (Slack)

## Enterprise Features (Fully Preserved)
- ✅ enterprise_features.py → core/enterprise_legacy.py
- ✅ remediation_engine.py → core/remediation_legacy.py
- ✅ policy_engine.py → core/policy_engine_legacy.py
- ✅ risk_scoring.py → core/risk_scoring_legacy.py
- ✅ compliance_dashboard.py → core/compliance_legacy.py

## Utilities & Tools
- ✅ code_wiki.py → services/code_wiki_legacy.py
- ✅ report_generator.py → services/report_legacy.py
- ✅ agents.py → services/agents_legacy.py
- ✅ api_tester.py → services/api_tester_legacy.py

## Next Steps
1. Keep legacy files as-is (they work)
2. Create wrapper modules that import from legacy
3. Gradually refactor legacy code into new modules
4. Write tests for each migrated piece
5. Remove _legacy suffix once tested

## Nothing Lost
All 14,455 lines of Python logic is preserved in /backend/core and /backend/services
All functionality maintained
All features available
