import React, { useState } from 'react';
import { Play, Pause, Square, X } from 'lucide-react';
import { formatDuration } from './DashboardStats';

interface TimerProps {
  projectName: string;
  isTimerRunning: boolean;
  elapsedSeconds: number;
  onStart: () => void;
  onPause: () => void;
  onStop: (description: string) => Promise<void>;
  onCancel: () => void;
}

export const Timer: React.FC<TimerProps> = ({
  projectName,
  isTimerRunning,
  elapsedSeconds,
  onStart,
  onPause,
  onStop,
  onCancel,
}) => {
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [description, setDescription] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleStopClick = () => {
    onPause();
    setShowSaveForm(true);
  };

  const handleSaveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onStop(description);
      setDescription('');
      setShowSaveForm(false);
    } catch (err) {
      console.error('Failed to save time log:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDiscard = () => {
    if (confirm('Are you sure you want to discard this tracked time?')) {
      onCancel();
      setDescription('');
      setShowSaveForm(false);
    }
  };

  return (
    <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-5 shadow-xl relative overflow-hidden transition-all duration-300 hover:border-violet-500/20">
      {/* Background glow decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/5 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none"></div>
      
      {!showSaveForm ? (
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-center md:text-left">
            <span className="text-[10px] bg-violet-500/10 text-violet-400 border border-violet-500/20 px-2 py-0.5 rounded-full font-medium tracking-wide uppercase">
              Time Tracker
            </span>
            <h3 className="text-sm font-semibold text-zinc-200 mt-1.5">
              Tracking: <span className="text-zinc-100 font-bold">{projectName}</span>
            </h3>
          </div>
 
          <div className="flex items-center gap-6">
            {/* Live Clock */}
            <div className="font-mono text-3xl font-bold tracking-wider text-zinc-100 flex items-center gap-1.5 tabular-nums">
              <span className={`w-2 h-2 rounded-full bg-violet-500 ${isTimerRunning ? 'animate-pulse' : 'opacity-40'}`}></span>
              {formatDuration(elapsedSeconds)}
            </div>
 
            {/* Controls */}
            <div className="flex items-center gap-2.5">
              {!isTimerRunning ? (
                <button
                  onClick={onStart}
                  className="p-3 rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 text-white hover:opacity-90 transition-all hover:scale-105 shadow-md shadow-violet-500/10"
                  title="Start Tracking"
                >
                  <Play className="w-5 h-5 fill-current" />
                </button>
              ) : (
                <button
                  onClick={onPause}
                  className="p-3 rounded-full bg-zinc-800 border border-zinc-700 text-zinc-300 hover:bg-zinc-750 transition-all hover:scale-105"
                  title="Pause Tracking"
                >
                  <Pause className="w-5 h-5" />
                </button>
              )}
 
              {elapsedSeconds > 0 && (
                <>
                  <button
                    onClick={handleStopClick}
                    className="p-3 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-all hover:scale-105"
                    title="Stop & Log Time"
                  >
                    <Square className="w-5 h-5 fill-current" />
                  </button>
                  <button
                    onClick={handleDiscard}
                    className="p-2 rounded-md bg-zinc-800/40 hover:bg-zinc-800 text-zinc-500 hover:text-zinc-300 transition-all"
                    title="Discard Time"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSaveSubmit} className="space-y-4 animate-fadeIn">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-zinc-200">
              Save tracked time for <span className="text-violet-400 font-bold">{projectName}</span>
            </h3>
            <span className="font-mono text-lg font-bold text-zinc-100 bg-zinc-900 border border-zinc-800 px-3 py-1 rounded-md">
              {formatDuration(elapsedSeconds)}
            </span>
          </div>
 
          <div>
            <label className="block text-[10px] text-zinc-400 font-semibold uppercase tracking-wider mb-1.5">
              What did you accomplish?
            </label>
            <input
              type="text"
              placeholder="e.g. Implement layout fixes, debug auth flow..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-violet-500 transition-colors"
            />
          </div>
 
          <div className="flex justify-end space-x-2.5">
            <button
              type="button"
              onClick={handleDiscard}
              className="px-4 py-2 rounded-md bg-zinc-850 hover:bg-zinc-800 text-zinc-400 text-xs font-semibold transition-all"
            >
              Discard
            </button>
            <button
              type="button"
              onClick={() => {
                setShowSaveForm(false);
                onStart(); // Resume
              }}
              className="px-4 py-2 rounded-md bg-zinc-800 hover:bg-zinc-750 text-zinc-200 text-xs font-semibold transition-all"
            >
              Resume Timer
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 rounded-md bg-gradient-to-r from-violet-500 to-indigo-500 text-white text-xs font-semibold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {isSaving ? 'Logging...' : 'Save Time Entry'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
