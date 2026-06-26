import React from 'react';
import type { DashboardSummary } from '../types';
import { Clock, Briefcase, CheckSquare, DollarSign, TrendingUp } from 'lucide-react';


interface DashboardStatsProps {
  summary: DashboardSummary | null;
}

export const formatDuration = (totalSeconds: number): string => {
  const isNegative = totalSeconds < 0;
  const absSeconds = Math.abs(totalSeconds);
  const hours = Math.floor(absSeconds / 3600);
  const minutes = Math.floor((absSeconds % 3600) / 60);
  const seconds = absSeconds % 60;
  
  const hDisplay = hours > 0 ? `${hours}h ` : '0h ';
  const mDisplay = minutes > 0 ? `${minutes}m ` : '0m ';
  const sDisplay = seconds > 0 ? `${seconds}s` : '0s';
  
  return (isNegative ? '-' : '') + (hDisplay + mDisplay + sDisplay).trim();
};

export const DashboardStats: React.FC<DashboardStatsProps> = ({ summary }) => {
  if (!summary) return null;

  const taskCompletionRate = summary.total_tasks > 0 
    ? Math.round((summary.completed_tasks / summary.total_tasks) * 100) 
    : 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {/* Total Tracked card */}
      <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-4 flex items-center gap-3 transition-all duration-300 hover:border-violet-500/30 hover:bg-zinc-900/60 shadow-lg min-w-0">
        <div className="p-2.5 rounded-lg bg-violet-500/10 text-violet-400 shrink-0">
          <Clock className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider truncate" title="Total Tracked">Total Tracked</p>
          <p className="text-sm sm:text-base font-bold text-zinc-100 mt-0.5 truncate whitespace-nowrap">{formatDuration(summary.total_work_seconds)}</p>
        </div>
      </div>

      {/* Billed card */}
      <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-4 flex items-center gap-3 transition-all duration-300 hover:border-rose-500/30 hover:bg-zinc-900/60 shadow-lg min-w-0">
        <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-400 shrink-0">
          <DollarSign className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider truncate" title="Total Billed">Billed</p>
          <p className="text-sm sm:text-base font-bold text-zinc-100 mt-0.5 truncate whitespace-nowrap">{formatDuration(summary.total_billed_seconds)}</p>
        </div>
      </div>

      {/* Unbilled card */}
      <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-4 flex items-center gap-3 transition-all duration-300 hover:border-indigo-500/30 hover:bg-zinc-900/60 shadow-lg min-w-0">
        <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0">
          <TrendingUp className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider truncate" title="Unbilled Balance">Unbilled</p>
          <p className={`text-sm sm:text-base font-bold mt-0.5 truncate whitespace-nowrap ${summary.total_unbilled_seconds < 0 ? 'text-rose-400' : 'text-zinc-100'}`}>
            {formatDuration(summary.total_unbilled_seconds)}
          </p>
        </div>
      </div>

      {/* Projects count card */}
      <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-4 flex items-center gap-3 transition-all duration-300 hover:border-emerald-500/30 hover:bg-zinc-900/60 shadow-lg min-w-0">
        <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
          <Briefcase className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider truncate" title="Total Projects">Total Projects</p>
          <p className="text-sm sm:text-base font-bold text-zinc-100 mt-0.5 truncate whitespace-nowrap">{summary.total_projects}</p>
        </div>
      </div>

      {/* Tasks completion card */}
      <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-4 flex items-center gap-3 transition-all duration-300 hover:border-amber-500/30 hover:bg-zinc-900/60 shadow-lg col-span-2 md:col-span-1 lg:col-span-1 min-w-0">
        <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 shrink-0">
          <CheckSquare className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-center gap-1">
            <p className="text-[9px] text-zinc-400 font-bold uppercase tracking-wider truncate" title="Task Progress">Progress</p>
            <span className="text-[9px] text-amber-400 font-semibold shrink-0">{summary.completed_tasks}/{summary.total_tasks} ({taskCompletionRate}%)</span>
          </div>
          <div className="w-full bg-zinc-800 rounded-full h-1 overflow-hidden mt-2">
            <div 
              className="bg-gradient-to-r from-amber-500 to-orange-500 h-1 rounded-full transition-all duration-500 ease-out" 
              style={{ width: `${taskCompletionRate}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

