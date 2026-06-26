import type { Project, Task, TimeLog, DashboardSummary, ActiveTimer, MedsStatus, DailyChecklist, MealInjectionLog, ComplianceDay } from './types';

export const api = {
  // Projects
  async getProjects(): Promise<Project[]> {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
  },

  async createProject(name: string, description: string): Promise<Project> {
    const res = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description }),
    });
    if (!res.ok) throw new Error('Failed to create project');
    return res.json();
  },

  async deleteProject(id: number): Promise<void> {
    const res = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete project');
  },

  // Tasks
  async getTasks(projectId: number): Promise<Task[]> {
    const res = await fetch(`/api/projects/${projectId}/tasks`);
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
  },

  async createTask(projectId: number, title: string, priority: string, dueDate: string | null): Promise<Task> {
    const res = await fetch(`/api/projects/${projectId}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, priority, due_date: dueDate || null }),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  },

  async updateTask(id: number, updates: Partial<Pick<Task, 'title' | 'is_completed' | 'priority' | 'due_date'>>): Promise<Task> {
    const res = await fetch(`/api/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
  },

  async deleteTask(id: number): Promise<void> {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete task');
  },

  // Time Logs
  async getTimeLogs(projectId: number): Promise<TimeLog[]> {
    const res = await fetch(`/api/projects/${projectId}/timelogs`);
    if (!res.ok) throw new Error('Failed to fetch time logs');
    return res.json();
  },

  async createTimeLog(projectId: number, data: { description: string; start_time: string; end_time: string }): Promise<TimeLog> {
    const res = await fetch(`/api/projects/${projectId}/timelogs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create time log');
    return res.json();
  },

  async deleteTimeLog(id: number): Promise<void> {
    const res = await fetch(`/api/timelogs/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete time log');
  },

  // Summary
  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch('/api/dashboard/summary');
    if (!res.ok) throw new Error('Failed to fetch dashboard summary');
    return res.json();
  },

  // Active Timer
  async getActiveTimer(): Promise<ActiveTimer | null> {
    const res = await fetch('/api/timer');
    if (!res.ok) throw new Error('Failed to fetch active timer');
    return res.json();
  },

  async startActiveTimer(projectId: number, description?: string): Promise<ActiveTimer> {
    const res = await fetch('/api/timer/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_id: projectId, description }),
    });
    if (!res.ok) throw new Error('Failed to start active timer');
    return res.json();
  },

  async pauseActiveTimer(): Promise<ActiveTimer> {
    const res = await fetch('/api/timer/pause', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to pause active timer');
    return res.json();
  },

  async stopActiveTimer(description?: string): Promise<TimeLog> {
    const res = await fetch('/api/timer/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    if (!res.ok) throw new Error('Failed to stop active timer');
    return res.json();
  },

  async discardActiveTimer(): Promise<void> {
    const res = await fetch('/api/timer', { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to discard active timer');
  },

  // MedTracker endpoints
  async getMedsStatus(date: string): Promise<MedsStatus> {
    const res = await fetch(`/api/status?date=${date}`);
    if (!res.ok) throw new Error('Failed to fetch meds status');
    return res.json();
  },

  async toggleChecklistItem(date: string, item: string): Promise<DailyChecklist> {
    const res = await fetch('/api/checklist/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date, item }),
    });
    if (!res.ok) throw new Error('Failed to toggle checklist item');
    return res.json();
  },

  async addMealInjection(date: string, note: string | null): Promise<MealInjectionLog> {
    const res = await fetch('/api/meal-injections', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date, note }),
    });
    if (!res.ok) throw new Error('Failed to log meal injection');
    return res.json();
  },

  async deleteMealInjection(id: number): Promise<void> {
    const res = await fetch(`/api/meal-injections/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete meal injection');
  },

  async getComplianceHistory(startDate: string, endDate: string): Promise<ComplianceDay[]> {
    const res = await fetch(`/api/history?start_date=${startDate}&end_date=${endDate}`);
    if (!res.ok) throw new Error('Failed to fetch compliance history');
    return res.json();
  },
};


