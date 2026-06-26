export interface Task {
  id: number;
  project_id: number;
  title: string;
  is_completed: boolean;
  priority: 'High' | 'Medium' | 'Low';
  due_date: string | null;
  created_at: string;
}

export interface TimeLog {
  id: number;
  project_id: number;
  description: string | null;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  tasks?: Task[];
  time_logs?: TimeLog[];
}

export interface ProjectSummary {
  project_id: number;
  project_name: string;
  total_work_seconds: number;
  total_billed_seconds: number;
  total_unbilled_seconds: number;
  total_tasks: number;
  completed_tasks: number;
}

export interface DashboardSummary {
  total_projects: number;
  total_work_seconds: number;
  total_billed_seconds: number;
  total_unbilled_seconds: number;
  total_tasks: number;
  completed_tasks: number;
  project_summaries: ProjectSummary[];
}

export interface ActiveTimer {
  id: number;
  project_id: number;
  description: string | null;
  start_time: string;
  server_time: string;
  is_paused: boolean;
  accumulated_seconds: number;
}

export interface DailyChecklist {
  date: string;
  morning_meds: boolean;
  morning_meds_taken_at: string | null;
  evening_meds: boolean;
  evening_meds_taken_at: string | null;
  morning_inject: boolean;
  morning_inject_taken_at: string | null;
}

export interface MealInjectionLog {
  id: number;
  date: string;
  timestamp: string;
  note: string | null;
}

export interface MedsStatus {
  checklist: DailyChecklist;
  meal_injections: MealInjectionLog[];
}

export interface ComplianceDay {
  date: string;
  checklist: {
    morning_meds: boolean;
    morning_meds_taken_at: string | null;
    evening_meds: boolean;
    evening_meds_taken_at: string | null;
    morning_inject: boolean;
    morning_inject_taken_at: string | null;
  };
  meal_injections_count: number;
  meal_injections: MealInjectionLog[];
}


