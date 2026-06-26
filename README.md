# TaskTracker

TaskTracker is a single-user task and time tracking application. It features a fast Python (FastAPI) backend storing data in a local SQLite database, and a highly interactive, responsive React + TypeScript Single-Page Application (SPA) styled with Tailwind CSS v4.

---

## Features

1. **Project Management**: Create, view, and delete projects.
2. **Task Checklist**: Create tasks with custom priority levels (`High`, `Medium`, `Low`) and optional due dates. Instantly toggle task completion status.
3. **Time Tracker**: Real-time play, pause, and stop controls. Log tracked time automatically with an optional description upon stopping.
4. **Time Log History**: List past time logs for the project or manually log historical entries.
5. **Dashboard Statistics**: Dynamic text-based metrics tracking total logged hours, project counts, and visual animated progress bars for task completion rates.

---

## Technology Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0, SQLite (built-in database file)
- **Backend Manager**: `uv` (Fast Python dependency installer and manager)
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React (icons)
- **Node Environment**: Managed via `fnm`

---

## Development Setup & Running Locally

Both the backend and frontend development servers have been launched and are running on your system.

### Running Backend (FastAPI)

To check or run the backend from the `backend/` directory:
```bash
# 1. Enter backend directory
cd backend

# 2. Run the DB seed script (creates tables & adds demo data)
PYTHONPATH=. uv run python app/seed.py

# 3. Start development server
PYTHONPATH=. uv run uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```
- Interactive API Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- API endpoint base: [http://localhost:8000/api](http://localhost:8000/api)

### Running Frontend (React + Vite)

To check or run the frontend from the `frontend/` directory:
```bash
# 1. Enter frontend directory
cd frontend

# 2. Load Node environment and install packages (if running fresh)
eval "$(fnm env)"
npm install

# 3. Run frontend development server
npm run dev -- --host 0.0.0.0
```
- Frontend application: [http://localhost:5173](http://localhost:5173) (Proxies `/api` calls directly to the FastAPI server running on port 8000)

---

## Project Structure

```text
tasktracker_server/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py      # SQLAlchemy connection
│   │   ├── models.py        # Project, Task, TimeLog SQLite schemas
│   │   ├── schemas.py       # Pydantic validation rules
│   │   ├── crud.py          # Queries and database commands
│   │   ├── seed.py          # Database initializer script
│   │   └── main.py          # FastAPI application server
│   ├── pyproject.toml
│   └── tracker.db           # Local SQLite database (created on run)
├── frontend/
│   ├── src/
│   │   ├── components/      
│   │   │   ├── DashboardStats.tsx   # Dashboard statistics cards
│   │   │   ├── ProjectSidebar.tsx   # Project selector/creation list
│   │   │   ├── Timer.tsx            # Play/pause/stop tracker widget
│   │   │   ├── TodoList.tsx         # Prioritized task checklist
│   │   │   └── TimeLogList.tsx      # Time records history lists
│   │   ├── App.tsx          # Main application view and tracking state
│   │   ├── api.ts           # Fetch API network client
│   │   ├── types.ts         # Shared TypeScript interfaces
│   │   ├── index.css        # Tailwind directive & theme layer
│   │   └── main.tsx
│   ├── index.html           # Document metadata and fonts
│   ├── vite.config.ts       # Vite bundler, proxy configuration & Tailwind plugin
│   └── package.json
└── desktop-linux/
    ├── app/
    │   ├── api_client.py    # Native HTTP API wrapper
    │   ├── ipc.py           # Wayland socket communicator
    │   ├── styles.py        # Dark-theme QSS stylesheet
    │   ├── widgets.py       # Custom animated widgets (SwitchButton)
    │   └── window.py        # MainWindow GUI layout and timer thread
    ├── run.py               # Main desktop runner
    ├── test_client.py       # GUI & API integration test script
    ├── pyproject.toml
    └── tasktracker-client.sh # Desktop shortcut trigger script
```

---

## Running the Linux Desktop Client

The desktop client is built on **Python 3** and **PyQt6**. It operates as a background system tray app that can be toggled using a global hotkey shortcut.

To run the desktop client manually:
```bash
cd desktop-linux
./tasktracker-client.sh
```

### Global Keyboard Toggle Shortcut on Wayland
To bind a keyboard shortcut to toggle the client open or closed (e.g. `Super+Alt+T`):
1. Navigate to **Settings** -> **Keyboard** -> **Keyboard Shortcuts** -> **View and Customise Shortcuts** -> **Custom Shortcuts** -> **Add Shortcut**.
2. Name: `Toggle TaskTracker`
3. Command: `/home/bgarcia/tasktracker_server/desktop-linux/tasktracker-client.sh --toggle`
4. Key: (your choice of key combination)
5. Click **Add**.

### Running Integration Tests
A complete automated GUI and API connectivity integration test script is included. To run it:
```bash
cd desktop-linux
uv run python test_client.py
```
This test script starts a local `QApplication` instance, connects to your running backend API, loads project details, programmatically adds a test task via button triggers, verifies it rendered inside the GUI layout, and closes cleanly.


