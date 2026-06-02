.PHONY: clean-locks dev-frontend dev-backend

## Remove stale git lock files left by the FUSE/virtiofs sandbox.
## Run this from your Mac terminal if `git commit` complains about locks.
clean-locks:
	@echo "🧹 Removing stale git lock files..."
	@find .git -name "*.lock" -delete 2>/dev/null && echo "✅  Done" || echo "✅  Nothing to clean"
	@rm -rf .git/stale-locks

## Start the frontend dev server
dev-frontend:
	cd frontend && npm run dev

## Start the backend dev server
dev-backend:
	cd backend && source venv/bin/activate && python main.py
