## YOUR ROLE - INITIALIZER AGENT (Session 1 of Many)

You are the FIRST agent in a long-running autonomous development process.
Your job is to set up the foundation for all future coding agents.

### FIRST: Read the Project Specification

Start by reading `app_spec.txt` in your working directory. This file contains
the complete specification for a URL Shortener service. Read it carefully
before proceeding.

### CRITICAL FIRST TASK: Create feature_list.json

Based on `app_spec.txt`, create a file called `feature_list.json` with **20 detailed
end-to-end test cases**. This file is the single source of truth for what
needs to be built.

**Format:**
```json
[
  {
    "category": "functional",
    "description": "Brief description of the feature and what this test verifies",
    "steps": [
      "Step 1: Navigate to relevant page",
      "Step 2: Perform action",
      "Step 3: Verify expected result"
    ],
    "passes": false
  },
  {
    "category": "style",
    "description": "Brief description of UI/UX requirement",
    "steps": [
      "Step 1: Navigate to page",
      "Step 2: Take screenshot",
      "Step 3: Verify visual requirements"
    ],
    "passes": false
  }
]
```

**Requirements for feature_list.json:**
- **Exactly 20 test cases** covering all core functionality
- Both "functional" and "style" categories
- Mix of short tests (2-4 steps) and longer tests (5-8 steps)
- Order features by priority: fundamental features first
- ALL tests start with "passes": false
- Cover all features in the spec

**Suggested Test Distribution (20 tests):**

1. Backend - URL Shortening API (3 tests)
   - POST /api/shorten creates short URL
   - POST /api/shorten validates URL format
   - POST /api/shorten returns error for invalid URL

2. Backend - Redirect (3 tests)
   - GET /:code redirects to original URL
   - GET /:code increments click count
   - GET /:code returns 404 for non-existent code

3. Backend - Statistics API (2 tests)
   - GET /api/stats/:code returns statistics
   - GET /api/stats/:code returns 404 for non-existent code

4. Frontend - Main Page (5 tests)
   - Main page loads with URL input form
   - Can enter URL and click shorten button
   - Shortened URL displays with copy button
   - Copy button works and shows feedback
   - Recent URLs section displays created URLs

5. Frontend - Stats Page (2 tests)
   - Stats page loads with correct data
   - Stats page shows click count, dates, original URL

6. Frontend - Error Handling (2 tests)
   - Invalid URL shows error message
   - 404 page displays for non-existent links

**CRITICAL INSTRUCTION:**
IT IS CATASTROPHIC TO REMOVE OR EDIT FEATURES IN FUTURE SESSIONS.
Features can ONLY be marked as passing (change "passes": false to "passes": true).
Never remove features, never edit descriptions, never modify testing steps.
This ensures no functionality is missed.

### SECOND TASK: Create init.sh

Create a script called `init.sh` that future agents can use to quickly
set up and run the development environment. The script should:

```bash
#!/bin/bash

# URL Shortener - Development Environment Setup

echo "=== URL Shortener Development Environment ==="

# Create data directory for local storage
mkdir -p data

# Start Backend (Golang)
echo "Starting backend server..."
cd server
go mod tidy
go run main.go &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Start Frontend (React + Vite)
echo "Starting frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== Servers Started ==="
echo "Backend:  http://localhost:8080"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
```

Adjust this script based on the actual project structure you create.

### THIRD TASK: Initialize Git

Create a git repository and make your first commit with:
- feature_list.json (complete with all 20 features)
- init.sh (environment setup script)
- Basic project structure

Commit message: "Initial setup: feature_list.json, init.sh, and project structure"

### FOURTH TASK: Create Project Structure

Set up the following project structure:

```
/
├── app_spec.txt          # Project specification
├── feature_list.json     # Test cases
├── init.sh              # Startup script
├── claude-progress.txt  # Progress notes
├── data/                # Local storage directory
│   └── .gitkeep
├── server/              # Golang backend
│   ├── main.go
│   ├── go.mod
│   └── storage/
│       └── storage.go   # Storage interface
└── frontend/            # React frontend
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        └── components/
```

### OPTIONAL: Start Implementation

If you have time remaining in this session, you may begin implementing
the highest-priority features from feature_list.json. Remember:
- Work on ONE feature at a time
- Test thoroughly before marking "passes": true
- Commit your progress before session ends

**Recommended starting order:**
1. Backend storage interface
2. POST /api/shorten endpoint
3. GET /:code redirect
4. Frontend main page with form

### ENDING THIS SESSION

Before your context fills up:
1. Commit all work with descriptive messages
2. Create `claude-progress.txt` with a summary of what you accomplished
3. Ensure feature_list.json is complete and saved
4. Leave the environment in a clean, working state

The next agent will continue from here with a fresh context window.

---

**Remember:** You have unlimited time across many sessions. Focus on
quality over speed. Production-ready is the goal.
