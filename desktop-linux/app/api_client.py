import requests
from typing import List, Optional

class LifeTrackerApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')

    def check_connection(self) -> bool:
        """Checks if the LifeTracker server is reachable."""
        try:
            response = requests.get(f"{self.base_url}/api", timeout=2.0)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_projects(self) -> Optional[List[dict]]:
        """Retrieves list of all projects."""
        try:
            response = requests.get(f"{self.base_url}/api/projects", timeout=3.0)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def get_tasks(self, project_id: int) -> Optional[List[dict]]:
        """Retrieves tasks for a project."""
        try:
            response = requests.get(f"{self.base_url}/api/projects/{project_id}/tasks", timeout=3.0)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def create_task(self, project_id: int, title: str) -> Optional[dict]:
        """Creates a new task for a project (default Medium priority)."""
        try:
            response = requests.post(
                f"{self.base_url}/api/projects/{project_id}/tasks",
                json={"title": title, "priority": "Medium", "is_completed": False},
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def update_task(self, task_id: int, updates: dict) -> Optional[dict]:
        """Updates a task (e.g. toggles completed state)."""
        try:
            response = requests.put(
                f"{self.base_url}/api/tasks/{task_id}",
                json=updates,
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def delete_task(self, task_id: int) -> bool:
        """Deletes a task by ID."""
        try:
            response = requests.delete(f"{self.base_url}/api/tasks/{task_id}", timeout=3.0)
            return response.status_code == 200
        except requests.RequestException:
            pass
        return False

    def create_time_log(self, project_id: int, description: str, start_time: str, end_time: str) -> Optional[dict]:
        """Creates a time log entry."""
        try:
            response = requests.post(
                f"{self.base_url}/api/projects/{project_id}/timelogs",
                json={
                    "description": description,
                    "start_time": start_time,
                    "end_time": end_time
                },
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def get_active_timer(self) -> Optional[dict]:
        """Gets current active timer from server."""
        try:
            response = requests.get(f"{self.base_url}/api/timer", timeout=2.0)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def start_active_timer(self, project_id: int, description: Optional[str] = None) -> Optional[dict]:
        """Starts a server-side active timer."""
        try:
            response = requests.post(
                f"{self.base_url}/api/timer/start",
                json={"project_id": project_id, "description": description},
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def pause_active_timer(self) -> Optional[dict]:
        """Pauses the active server-side timer."""
        try:
            response = requests.post(f"{self.base_url}/api/timer/pause", timeout=3.0)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def stop_active_timer(self, description: Optional[str] = None) -> Optional[dict]:
        """Stops the active server-side timer and commits it to a time log."""
        try:
            response = requests.post(
                f"{self.base_url}/api/timer/stop",
                json={"description": description},
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def discard_active_timer(self) -> bool:
        """Discards (cancels) the current active server-side timer."""
        try:
            response = requests.delete(f"{self.base_url}/api/timer", timeout=3.0)
            return response.status_code == 200
        except requests.RequestException:
            pass
        return False

    # MedTracker Endpoints
    def get_status(self, date_str: str) -> Optional[dict]:
        """Retrieves status (checklist & meal injections) for a specific date."""
        try:
            response = requests.get(
                f"{self.base_url}/api/status",
                params={"date": date_str},
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def toggle_item(self, date_str: str, item: str) -> Optional[dict]:
        """Toggles a checklist item's state."""
        try:
            response = requests.post(
                f"{self.base_url}/api/checklist/toggle",
                json={"date": date_str, "item": item},
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def add_meal_injection(self, date_str: str, note: str) -> Optional[dict]:
        """Logs a new mealtime injection with the current timestamp and a note."""
        try:
            response = requests.post(
                f"{self.base_url}/api/meal-injections",
                json={"date": date_str, "note": note},
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def delete_meal_injection(self, injection_id: int) -> bool:
        """Deletes a logged mealtime injection by its unique database ID."""
        try:
            response = requests.delete(
                f"{self.base_url}/api/meal-injections/{injection_id}",
                timeout=3.0
            )
            if response.status_code == 200:
                return response.json().get("success", False)
        except requests.RequestException:
            pass
        return False


