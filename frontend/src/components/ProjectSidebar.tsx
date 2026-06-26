import React, { useState } from 'react';
import type { Project, ProjectSummary } from '../types';
import { formatDuration } from './DashboardStats';
import { Plus, Trash2, Folder, Briefcase } from 'lucide-react';


interface ProjectSidebarProps {
  projects: Project[];
  selectedProjectId: number | null;
  onSelectProject: (id: number) => void;
  onCreateProject: (name: string, description: string) => Promise<void>;
  onDeleteProject: (id: number) => Promise<void>;
  summaries: ProjectSummary[];
}

export const ProjectSidebar: React.FC<ProjectSidebarProps> = ({
  projects,
  selectedProjectId,
  onSelectProject,
  onCreateProject,
  onDeleteProject,
  summaries,
}) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      await onCreateProject(name, description);
      setName('');
      setDescription('');
      setShowAddForm(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getProjStats = (id: number) => {
    const summary = summaries.find((s) => s.project_id === id);
    if (!summary) return { tasks: 0, completed: 0, time: 0 };
    return {
      tasks: summary.total_tasks,
      completed: summary.completed_tasks,
      time: summary.total_unbilled_seconds,
    };
  };

  return (
    <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-4 flex flex-col h-full shadow-xl">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-md font-semibold text-zinc-300 flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-violet-400" />
          Projects
        </h2>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="p-1.5 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-all hover:scale-105"
          title="Create New Project"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="mb-4 p-3 bg-zinc-900/60 rounded-lg border border-zinc-800 animate-fadeIn">
          <input
            type="text"
            placeholder="Project Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500 mb-2"
          />
          <textarea
            placeholder="Project Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500 mb-2 resize-none h-16"
          />
          <div className="flex space-x-2 justify-end">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-3 py-1 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-400 text-[10px] font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3 py-1 rounded-md bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-[10px] font-medium hover:opacity-90 disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      )}

      <div className="flex-1 overflow-y-auto space-y-2 max-h-[450px] pr-1 scrollbar-thin">
        {projects.length === 0 ? (
          <div className="text-center py-8 text-zinc-500 text-xs">
            No projects yet. Create one to get started!
          </div>
        ) : (
          projects.map((project) => {
            const isSelected = project.id === selectedProjectId;
            const stats = getProjStats(project.id);
            const completionRate = stats.tasks > 0 ? Math.round((stats.completed / stats.tasks) * 100) : 0;

            return (
              <div
                key={project.id}
                onClick={() => onSelectProject(project.id)}
                className={`group relative flex flex-col p-3 rounded-lg cursor-pointer border transition-all duration-300 ${
                  isSelected
                    ? 'bg-gradient-to-r from-violet-500/10 to-indigo-500/10 border-violet-500/50 shadow-md shadow-violet-500/5'
                    : 'bg-zinc-900/10 border-white/5 hover:bg-zinc-900/30 hover:border-white/10'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-2.5 min-w-0">
                    <Folder className={`w-4 h-4 shrink-0 ${isSelected ? 'text-violet-400' : 'text-zinc-500'}`} />
                    <span className="text-xs font-semibold text-zinc-200 truncate pr-4">{project.name}</span>
                  </div>
                  <button
                    onClick={async (e) => {
                      e.stopPropagation();
                      if (confirm(`Are you sure you want to delete "${project.name}"? This will delete all tasks and logs.`)) {
                        await onDeleteProject(project.id);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/10 text-zinc-500 hover:text-red-400 transition-all absolute right-2 top-2.5"
                    title="Delete Project"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {project.description && (
                  <p className="text-[10px] text-zinc-400 mt-1 line-clamp-1 truncate max-w-[90%]">
                    {project.description}
                  </p>
                )}

                <div className="flex items-center justify-between mt-2.5 text-[9px] text-zinc-500">
                  <span className="flex items-center gap-1 font-medium text-zinc-400">
                    {stats.tasks} tasks • {stats.completed} done • <span className={`${stats.time < 0 ? 'text-rose-400' : 'text-violet-400'} font-semibold`} title="Unbilled Balance">Unbilled: {formatDuration(stats.time)}</span>
                  </span>
                  <div className="flex items-center space-x-1.5">
                    <div className="w-12 bg-zinc-800 rounded-full h-1">
                      <div
                        className="bg-violet-500 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${completionRate}%` }}
                      />
                    </div>
                    <span className="font-semibold text-violet-400">{completionRate}%</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
