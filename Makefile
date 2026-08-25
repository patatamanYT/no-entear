.PHONY: run backend frontend install install-backend install-frontend mock test build clean

run: ## Run backend + frontend together (installs deps on first run)
	./run.sh

install: install-backend install-frontend ## Install all dependencies

install-backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -q --upgrade pip && pip install -q -r requirements.txt

install-frontend:
	cd frontend && npm install

backend: ## Run only the FastAPI backend
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend: ## Run only the Next.js frontend
	cd frontend && npm run dev

mock: ## Regenerate the synthetic match dataset
	cd backend && . .venv/bin/activate && python -m app.mock_data

test: ## Run backend test suite
	cd backend && . .venv/bin/activate && pytest -q

build: ## Production build of the frontend
	cd frontend && npm run build

clean:
	rm -rf backend/.venv frontend/node_modules frontend/.next
