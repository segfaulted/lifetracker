import React, { useState } from 'react';
import type { Task } from '../types';
import { Check, Plus, Trash2, Calendar, AlertTriangle } from 'lucide-react';

interface TodoListProps {
  tasks: Task[];
  onAddTask: (title: string, priority: 'High' | 'Medium' | 'Low', dueDate: string | null) => Promise<void>;
  onToggleTask: (id: number, isCompleted: boolean) => Promise<void>;
  onDeleteTask: (id: number) => Promise<void>;
}

export const TodoList: React.FC<TodoListProps> = ({
  tasks,
  onAddTask,
  onToggleTask,
  onDeleteTask,
}) => {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<'High' | 'Medium' | 'Low'>('Medium');
  const [dueDate, setDueDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setIsSubmitting(true);
    try {
      await onAddTask(title, priority, dueDate || null);
      setTitle('');
      setPriority('Medium');
      setDueDate('');
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPriorityStyles = (p: 'High' | 'Medium' | 'Low') => {
    switch (p) {
      case 'High':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'Medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Low':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
      default:
        return 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30';
    }
  };

  const isOverdue = (dateStr: string | null, isCompleted: boolean) => {
    if (!dateStr || isCompleted) return false;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const taskDate = new Date(dateStr);
    taskDate.setHours(0, 0, 0, 0);
    return taskDate < today;
  };

  // Sort tasks: uncompleted first, then by priority (High -> Medium -> Low), then by created_at
  const sortedTasks = [...tasks].sort((a, b) => {
    if (a.is_completed !== b.is_completed) {
      return a.is_completed ? 1 : -1;
    }
    const priorityWeight = { High: 3, Medium: 2, Low: 1 };
    const weightDiff = priorityWeight[b.priority] - priorityWeight[a.priority];
    if (weightDiff !== 0) return weightDiff;
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  return (
    <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-5 shadow-xl flex flex-col h-full">
      <h3 className="text-md font-semibold text-zinc-300 mb-4 flex items-center gap-2">
        <Check className="w-5 h-5 text-indigo-400" />
        Tasks Checklist
      </h3>

      {/* Add Task Form */}
      <form onSubmit={handleSubmit} className="space-y-3 mb-6 bg-zinc-900/20 p-4 rounded-lg border border-white/5">
        <div>
          <input
            type="text"
            placeholder="Add a new task..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full bg-zinc-950 border border-white/10 rounded-md px-3.5 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500 transition-colors"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as any)}
              className="w-full bg-zinc-950 border border-white/10 rounded-md px-2.5 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-violet-500"
            >
              <option value="High">🔴 High</option>
              <option value="Medium">🟡 Medium</option>
              <option value="Low">🔵 Low</option>
            </select>
          </div>
          <div>
            <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
              Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full bg-zinc-950 border border-white/10 rounded-md px-2.5 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-violet-500"
            />
          </div>
        </div>
        <div className="flex justify-end pt-1">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-4 py-2 rounded-md bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-xs font-semibold hover:opacity-90 transition-all disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            {isSubmitting ? 'Adding...' : 'Add Task'}
          </button>
        </div>
      </form>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto space-y-2 max-h-[350px] pr-1 scrollbar-thin">
        {sortedTasks.length === 0 ? (
          <div className="text-center py-12 text-zinc-500 text-xs">
            No tasks listed. Add some tasks above!
          </div>
        ) : (
          sortedTasks.map((task) => {
            const overdue = isOverdue(task.due_date, task.is_completed);

            return (
              <div
                key={task.id}
                className={`group flex items-center justify-between p-3 rounded-lg border transition-all duration-300 ${
                  task.is_completed
                    ? 'bg-zinc-950/20 border-zinc-900 opacity-60'
                    : 'bg-zinc-900/10 border-white/5 hover:border-white/10 hover:bg-zinc-900/30'
                }`}
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0 pr-4">
                  {/* Custom Checkbox */}
                  <button
                    onClick={() => onToggleTask(task.id, !task.is_completed)}
                    className={`w-5 h-5 rounded-md border flex items-center justify-center shrink-0 transition-all ${
                      task.is_completed
                        ? 'bg-indigo-500 border-indigo-600 text-white'
                        : 'border-zinc-700 hover:border-violet-500 bg-zinc-950/60'
                    }`}
                  >
                    {task.is_completed && <Check className="w-3.5 h-3.5 stroke-[3px]" />}
                  </button>

                  <div className="min-w-0 flex-1">
                    <p
                      className={`text-xs font-medium text-zinc-200 truncate ${
                        task.is_completed ? 'line-through text-zinc-500' : ''
                      }`}
                    >
                      {task.title}
                    </p>
                    
                    <div className="flex flex-wrap items-center gap-2 mt-1">
                      {/* Priority Tag */}
                      <span className={`text-[8px] font-bold uppercase px-1.5 py-0.5 rounded border ${getPriorityStyles(task.priority)}`}>
                        {task.priority}
                      </span>
                      
                      {/* Due Date Indicator */}
                      {task.due_date && (
                        <span className={`text-[9px] flex items-center gap-1 font-medium ${overdue ? 'text-rose-400 font-bold' : 'text-zinc-500'}`}>
                          {overdue ? <AlertTriangle className="w-3 h-3 shrink-0" /> : <Calendar className="w-3 h-3 shrink-0" />}
                          {overdue ? 'Overdue: ' : ''}{new Date(task.due_date).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => onDeleteTask(task.id)}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-red-500/10 text-zinc-500 hover:text-red-400 transition-all"
                  title="Delete Task"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
