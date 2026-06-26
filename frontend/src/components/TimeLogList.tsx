import React, { useState } from 'react';
import type { TimeLog } from '../types';
import { Trash2, History, Plus, Clock, Calendar, MessageSquare, DollarSign } from 'lucide-react';
import { formatDuration } from './DashboardStats';

interface TimeLogListProps {
  timeLogs: TimeLog[];
  onAddManualLog: (description: string, startTime: string, endTime: string) => Promise<void>;
  onDeleteLog: (id: number) => Promise<void>;
}

export const TimeLogList: React.FC<TimeLogListProps> = ({
  timeLogs,
  onAddManualLog,
  onDeleteLog,
}) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [logType, setLogType] = useState<'work' | 'billing'>('work');
  const [description, setDescription] = useState('');
  const [logDate, setLogDate] = useState(new Date().toISOString().split('T')[0]);
  const [hours, setHours] = useState('0');
  const [minutes, setMinutes] = useState('30');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const h = parseInt(hours) || 0;
    const m = parseInt(minutes) || 0;
    let totalMinutes = h * 60 + m;

    if (totalMinutes <= 0) {
      alert('Duration must be greater than 0 minutes');
      return;
    }

    if (logType === 'billing') {
      totalMinutes = -totalMinutes;
    }

    setIsSubmitting(true);
    try {
      // Create synthetic start and end times based on selected date
      // Start time: 12:00 PM on selected date (local time)
      const baseDate = new Date(logDate);
      baseDate.setHours(12, 0, 0, 0);
      
      const startTimeISO = baseDate.toISOString();
      
      // End time: baseDate + totalMinutes (could be negative)
      const endDate = new Date(baseDate.getTime() + totalMinutes * 60000);
      const endTimeISO = endDate.toISOString();

      await onAddManualLog(description, startTimeISO, endTimeISO);
      
      setDescription('');
      setHours('0');
      setMinutes('30');
      setLogType('work');
      setShowAddForm(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-5 shadow-xl flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-md font-semibold text-zinc-300 flex items-center gap-2">
          <History className="w-5 h-5 text-violet-400" />
          Time Log History
        </h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-md bg-zinc-850 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-[10px] font-semibold transition-all"
        >
          <Plus className="w-3.5 h-3.5" />
          Add Manual Log
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleSubmit} className="space-y-3 mb-6 bg-zinc-900/20 p-4 rounded-lg border border-white/5 animate-fadeIn">
          <div>
            <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
              Log Type
            </label>
            <div className="grid grid-cols-2 gap-2 bg-zinc-950 p-1 rounded-lg border border-white/5">
              <button
                type="button"
                onClick={() => setLogType('work')}
                className={`py-1 text-xs font-semibold rounded-md transition-all ${
                  logType === 'work'
                    ? 'bg-zinc-800 text-violet-400 border border-zinc-700/50 shadow'
                    : 'text-zinc-400 hover:text-zinc-300 border border-transparent'
                }`}
              >
                Work Entry
              </button>
              <button
                type="button"
                onClick={() => setLogType('billing')}
                className={`py-1 text-xs font-semibold rounded-md transition-all ${
                  logType === 'billing'
                    ? 'bg-zinc-800 text-rose-400 border border-zinc-700/50 shadow'
                    : 'text-zinc-400 hover:text-zinc-300 border border-transparent'
                }`}
              >
                Billing Entry
              </button>
            </div>
          </div>

          <div>
            <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
              Description
            </label>
            <input
              type="text"
              placeholder={logType === 'work' ? "What did you work on?" : "Invoice reference / billing detail"}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              className="w-full bg-zinc-950 border border-white/10 rounded-md px-3.5 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500 transition-colors"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
                Date
              </label>
              <input
                type="date"
                value={logDate}
                onChange={(e) => setLogDate(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-white/10 rounded-md px-2.5 py-1 text-xs text-zinc-350 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
                Hours
              </label>
              <input
                type="number"
                min="0"
                max="24"
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-white/10 rounded-md px-2.5 py-1 text-xs text-zinc-350 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[9px] text-zinc-500 font-semibold uppercase tracking-wider mb-1">
                Minutes
              </label>
              <input
                type="number"
                min="0"
                max="59"
                value={minutes}
                onChange={(e) => setMinutes(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-white/10 rounded-md px-2.5 py-1 text-xs text-zinc-350 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-1">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-3 py-1.5 rounded-md bg-zinc-850 hover:bg-zinc-800 text-zinc-400 text-xs font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-3 py-1.5 rounded-md bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-xs font-semibold hover:opacity-90 disabled:opacity-50"
            >
              {isSubmitting ? 'Logging...' : 'Save Log'}
            </button>
          </div>
        </form>
      )}

      {/* Logs list */}
      <div className="flex-1 overflow-y-auto space-y-2 max-h-[350px] pr-1 scrollbar-thin">
        {timeLogs.length === 0 ? (
          <div className="text-center py-12 text-zinc-500 text-xs">
            No time logged yet for this project.
          </div>
        ) : (
          timeLogs.map((log) => (
            <div
              key={log.id}
              className={`group flex items-center justify-between p-3.5 bg-zinc-900/20 border rounded-lg hover:bg-zinc-900/40 transition-all duration-300 ${
                log.duration_seconds < 0
                  ? 'border-rose-950/40 hover:border-rose-800/40 bg-rose-500/[0.02]'
                  : 'border-white/5 hover:border-white/10'
              }`}
            >
              <div className="flex-1 min-w-0 pr-4">
                <div className="flex items-center gap-2 text-[10px] text-zinc-400 font-medium">
                  <span className="flex items-center gap-1 text-indigo-400">
                    <Calendar className="w-3 h-3" />
                    {formatDate(log.start_time)}
                  </span>
                  {log.duration_seconds < 0 ? (
                    <span className="flex items-center gap-1 text-rose-400 font-semibold">
                      <DollarSign className="w-3 h-3" />
                      {formatDuration(log.duration_seconds)} (Billing)
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-violet-400">
                      <Clock className="w-3 h-3" />
                      {formatDuration(log.duration_seconds)}
                    </span>
                  )}
                </div>

                <div className="flex items-start gap-1.5 mt-1.5">
                  <MessageSquare className="w-3.5 h-3.5 text-zinc-650 shrink-0 mt-0.5" />
                  <p className="text-xs text-zinc-200 leading-relaxed break-words font-medium">
                    {log.description || <span className="italic text-zinc-600">No details provided</span>}
                  </p>
                </div>
              </div>

              <button
                onClick={() => {
                  if (confirm('Delete this time log entry?')) {
                    onDeleteLog(log.id);
                  }
                }}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-red-500/10 text-zinc-500 hover:text-red-400 transition-all"
                title="Delete Time Log"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

