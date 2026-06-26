import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { MedsStatus, ComplianceDay } from '../types';
import { 
  Pill, ChevronLeft, ChevronRight, Calendar, Plus, 
  Trash2, Clock, Activity, Utensils, Award
} from 'lucide-react';

export function MedTracker() {
  const getTodayStr = () => {
    const tzoffset = (new Date()).getTimezoneOffset() * 60000; //offset in milliseconds
    const localISOTime = (new Date(Date.now() - tzoffset)).toISOString().slice(0, 10);
    return localISOTime;
  };

  const [currentDate, setCurrentDate] = useState<string>(getTodayStr());
  const [status, setStatus] = useState<MedsStatus | null>(null);
  const [history, setHistory] = useState<ComplianceDay[]>([]);
  const [customNote, setCustomNote] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch meds status and history
  const fetchData = async (dateStr: string) => {
    try {
      setLoading(true);
      const medsStatus = await api.getMedsStatus(dateStr);
      setStatus(medsStatus);

      // Get 7-day history (from 6 days ago to today)
      const end = new Date(dateStr);
      const start = new Date(dateStr);
      start.setDate(start.getDate() - 6);

      const startStr = start.toISOString().slice(0, 10);
      const endStr = end.toISOString().slice(0, 10);

      const compHistory = await api.getComplianceHistory(startStr, endStr);
      setHistory(compHistory);
      setError(null);
    } catch (err) {
      console.error('Failed to load MedTracker data:', err);
      setError('Could not connect to MedTracker API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(currentDate);
  }, [currentDate]);

  // Real-time sync via WebSocket
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWS = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws';
      const wsUrl = `${protocol}//${window.location.host}/api/ws`;
      
      ws = new WebSocket(wsUrl);

      ws.onmessage = async (event) => {
        if (event.data === 'refresh') {
          try {
            const medsStatus = await api.getMedsStatus(currentDate);
            setStatus(medsStatus);

            const end = new Date(currentDate);
            const start = new Date(currentDate);
            start.setDate(start.getDate() - 6);
            const startStr = start.toISOString().slice(0, 10);
            const endStr = end.toISOString().slice(0, 10);

            const compHistory = await api.getComplianceHistory(startStr, endStr);
            setHistory(compHistory);
          } catch (err) {
            console.error('WS Refresh Error in MedTracker:', err);
          }
        }
      };

      ws.onclose = () => {
        reconnectTimeout = setTimeout(connectWS, 3000);
      };

      ws.onerror = () => {
        ws?.close();
      };
    };

    connectWS();

    return () => {
      ws?.close();
      clearTimeout(reconnectTimeout);
    };
  }, [currentDate]);

  // Handlers
  const handlePrevDay = () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() - 1);
    setCurrentDate(d.toISOString().slice(0, 10));
  };

  const handleNextDay = () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() + 1);
    setCurrentDate(d.toISOString().slice(0, 10));
  };

  const handleToday = () => {
    setCurrentDate(getTodayStr());
  };

  const handleToggleChecklist = async (item: string) => {
    if (!status) return;
    try {
      await api.toggleChecklistItem(currentDate, item);
      // Let WS handle the refresh
    } catch (err) {
      console.error('Failed to toggle item:', err);
    }
  };

  const handleQuickLog = async (note: string) => {
    try {
      await api.addMealInjection(currentDate, note);
      // Let WS handle the refresh
    } catch (err) {
      console.error('Failed to quick log injection:', err);
    }
  };

  const handleCustomLog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customNote.trim()) return;
    try {
      await api.addMealInjection(currentDate, customNote.trim());
      setCustomNote('');
      // Let WS handle the refresh
    } catch (err) {
      console.error('Failed to log custom injection:', err);
    }
  };

  const handleDeleteLog = async (id: number) => {
    try {
      await api.deleteMealInjection(id);
      // Let WS handle the refresh
    } catch (err) {
      console.error('Failed to delete injection:', err);
    }
  };

  // Helper formatting functions
  const formatDateDisplay = (dateStr: string) => {
    const today = getTodayStr();
    if (dateStr === today) return 'Today';
    
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (dateStr === tomorrow.toISOString().slice(0, 10)) return 'Tomorrow';

    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    if (dateStr === yesterday.toISOString().slice(0, 10)) return 'Yesterday';

    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  };

  // Compute checklist counts
  const checklistCompletion = status ? [
    status.checklist.morning_meds,
    status.checklist.evening_meds,
    status.checklist.morning_inject
  ].filter(Boolean).length : 0;

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-xs font-medium">
          {error}
        </div>
      )}

      {/* Header Date Control Card */}
      <div className="p-4 bg-zinc-900/40 border border-white/5 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4 shadow-lg backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-gradient-to-tr from-rose-500 to-pink-500 text-white shadow-md shadow-rose-500/10 animate-pulse">
            <Pill className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-zinc-200">Daily Health Tracker</h2>
            <p className="text-[10px] text-zinc-400 font-medium">Track medication schedules & mealtime injections</p>
          </div>
        </div>

        {/* Date Navigator */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handlePrevDay}
            className="p-2 bg-zinc-800/80 hover:bg-zinc-700 rounded-lg text-zinc-400 hover:text-zinc-100 transition-colors border border-white/5 cursor-pointer"
            title="Previous Day"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-zinc-950/40 border border-white/5 rounded-lg">
            <Calendar className="w-3.5 h-3.5 text-rose-400" />
            <input
              type="date"
              value={currentDate}
              onChange={(e) => setCurrentDate(e.target.value)}
              className="bg-transparent border-none text-xs font-semibold text-zinc-200 focus:outline-none w-28 text-center cursor-pointer"
            />
            <span className="text-[10px] bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded-full font-bold">
              {formatDateDisplay(currentDate)}
            </span>
          </div>

          <button
            onClick={handleNextDay}
            className="p-2 bg-zinc-800/80 hover:bg-zinc-700 rounded-lg text-zinc-400 hover:text-zinc-100 transition-colors border border-white/5 cursor-pointer"
            title="Next Day"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          <button
            onClick={handleToday}
            className="px-3 py-2 bg-zinc-800/80 hover:bg-zinc-700 border border-white/5 rounded-lg text-xs font-bold text-zinc-300 transition-all hover:text-zinc-100 cursor-pointer"
          >
            Today
          </button>
        </div>
      </div>

      {loading && !status ? (
        <div className="flex flex-col items-center justify-center p-12 bg-zinc-900/10 border border-white/5 rounded-xl min-h-[300px]">
          <div className="w-10 h-10 rounded-full border-4 border-rose-500/20 border-t-rose-500 animate-spin mb-4"></div>
          <p className="text-xs text-zinc-400 font-semibold tracking-wide">Loading health tracker state...</p>
        </div>
      ) : status ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Daily Checklist Card */}
          <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl flex flex-col space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between border-b border-zinc-850 pb-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-4.5 h-4.5 text-rose-450 animate-pulse" />
                <h3 className="text-sm font-bold text-zinc-200">Daily Checklist</h3>
              </div>
              <span className="px-2.5 py-0.5 text-[10px] font-bold bg-rose-550/10 text-rose-400 border border-rose-500/20 rounded-full">
                {checklistCompletion} / 3 Completed
              </span>
            </div>

            {/* Checklist items list */}
            <div className="space-y-4 pt-2">
              
              {/* Morning Meds */}
              <div className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                status.checklist.morning_meds 
                  ? 'bg-emerald-500/5 border-emerald-500/20 shadow-inner' 
                  : 'bg-zinc-950/20 border-white/5 hover:border-zinc-800'
              }`}>
                <div className="flex items-center space-x-4">
                  <div className={`p-2.5 rounded-lg ${
                    status.checklist.morning_meds 
                      ? 'bg-emerald-500/10 text-emerald-400' 
                      : 'bg-amber-500/10 text-amber-400'
                  }`}>
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-zinc-200">Morning Meds</h4>
                    <p className="text-[10px] text-zinc-500 mt-0.5">Taken once daily after breakfast</p>
                    {status.checklist.morning_meds && status.checklist.morning_meds_taken_at && (
                      <span className="text-[9px] text-emerald-400 font-semibold block mt-1">
                        Checked at {formatTime(status.checklist.morning_meds_taken_at)}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleToggleChecklist('morning_meds')}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all shadow-sm cursor-pointer ${
                    status.checklist.morning_meds
                      ? 'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/35'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-white/5'
                  }`}
                >
                  {status.checklist.morning_meds ? '✓ Taken' : 'Mark Taken'}
                </button>
              </div>

              {/* Evening Meds */}
              <div className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                status.checklist.evening_meds 
                  ? 'bg-emerald-500/5 border-emerald-500/20 shadow-inner' 
                  : 'bg-zinc-950/20 border-white/5 hover:border-zinc-800'
              }`}>
                <div className="flex items-center space-x-4">
                  <div className={`p-2.5 rounded-lg ${
                    status.checklist.evening_meds 
                      ? 'bg-emerald-500/10 text-emerald-400' 
                      : 'bg-indigo-500/10 text-indigo-400'
                  }`}>
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-zinc-200">Evening Meds</h4>
                    <p className="text-[10px] text-zinc-500 mt-0.5">Taken once daily before sleep</p>
                    {status.checklist.evening_meds && status.checklist.evening_meds_taken_at && (
                      <span className="text-[9px] text-emerald-400 font-semibold block mt-1">
                        Checked at {formatTime(status.checklist.evening_meds_taken_at)}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleToggleChecklist('evening_meds')}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all shadow-sm cursor-pointer ${
                    status.checklist.evening_meds
                      ? 'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/35'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-white/5'
                  }`}
                >
                  {status.checklist.evening_meds ? '✓ Taken' : 'Mark Taken'}
                </button>
              </div>

              {/* Morning Inject */}
              <div className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                status.checklist.morning_inject 
                  ? 'bg-emerald-500/5 border-emerald-500/20 shadow-inner' 
                  : 'bg-zinc-950/20 border-white/5 hover:border-zinc-800'
              }`}>
                <div className="flex items-center space-x-4">
                  <div className={`p-2.5 rounded-lg ${
                    status.checklist.morning_inject 
                      ? 'bg-emerald-500/10 text-emerald-400' 
                      : 'bg-rose-500/10 text-rose-455'
                  }`}>
                    <Activity className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-zinc-200">Morning Inject</h4>
                    <p className="text-[10px] text-zinc-500 mt-0.5">Daily insulin/morning shot log</p>
                    {status.checklist.morning_inject && status.checklist.morning_inject_taken_at && (
                      <span className="text-[9px] text-emerald-400 font-semibold block mt-1">
                        Checked at {formatTime(status.checklist.morning_inject_taken_at)}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleToggleChecklist('morning_inject')}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all shadow-sm cursor-pointer ${
                    status.checklist.morning_inject
                      ? 'bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/35'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-white/5'
                  }`}
                >
                  {status.checklist.morning_inject ? '✓ Taken' : 'Mark Taken'}
                </button>
              </div>

            </div>
          </div>

          {/* Meal Injections Card */}
          <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl flex flex-col space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between border-b border-zinc-850 pb-4">
              <div className="flex items-center space-x-2">
                <Utensils className="w-4.5 h-4.5 text-rose-400" />
                <h3 className="text-sm font-bold text-zinc-200">Mealtime Injections</h3>
              </div>
              <span className="px-2.5 py-0.5 text-[10px] font-bold bg-violet-500/10 text-violet-400 border border-violet-500/20 rounded-full">
                {status.meal_injections.length} Logged
              </span>
            </div>

            {/* Quick Log Buttons */}
            <div className="space-y-3 pt-2">
              <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">Quick Log meal:</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {['Breakfast', 'Lunch', 'Dinner', 'Snack'].map((meal) => (
                  <button
                    key={meal}
                    onClick={() => handleQuickLog(meal)}
                    className="py-2 px-3 bg-zinc-800/80 hover:bg-zinc-700 border border-white/5 hover:border-zinc-700 rounded-lg text-xs font-bold text-zinc-300 transition-all hover:text-zinc-100 flex items-center justify-center space-x-1.5 shadow-sm cursor-pointer"
                  >
                    <span>{meal === 'Breakfast' ? '🍳' : meal === 'Lunch' ? '🥪' : meal === 'Dinner' ? '🍽️' : '🍪'}</span>
                    <span>{meal}</span>
                  </button>
                ))}
              </div>

              {/* Custom log note form */}
              <form onSubmit={handleCustomLog} className="flex gap-2 pt-2">
                <input
                  type="text"
                  placeholder="Custom note (e.g. Afternoon Tea, Dessert)..."
                  value={customNote}
                  onChange={(e) => setCustomNote(e.target.value)}
                  maxLength={50}
                  className="flex-1 bg-zinc-950/60 border border-white/5 focus:border-rose-500/50 hover:border-zinc-850 px-3 py-2 rounded-lg text-xs font-medium text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
                />
                <button
                  type="submit"
                  className="px-4 bg-gradient-to-tr from-rose-500 to-pink-500 hover:from-rose-600 hover:to-pink-600 text-white rounded-lg text-xs font-bold shadow-md shadow-rose-500/10 hover:shadow-rose-600/20 transition-all flex items-center justify-center space-x-1 cursor-pointer"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Log</span>
                </button>
              </form>

              {/* Today's Injection Logs list */}
              <div className="pt-3 flex-1 flex flex-col min-h-[160px]">
                <h4 className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider mb-2">Logs for this day:</h4>
                <div className="bg-zinc-950/40 rounded-xl border border-white/5 p-3 flex-1 overflow-y-auto max-h-[180px] divide-y divide-zinc-900">
                  {status.meal_injections.length === 0 ? (
                    <div className="h-full flex items-center justify-center text-center text-xs text-zinc-600 italic py-8">
                      No injection logs recorded for this date.
                    </div>
                  ) : (
                    status.meal_injections.map((log) => (
                      <div key={log.id} className="py-2.5 flex items-center justify-between first:pt-0 last:pb-0 group">
                        <div className="flex items-center space-x-3">
                          <span className="text-xs">💉</span>
                          <div>
                            <span className="text-xs font-bold text-zinc-200">{log.note || 'Injection'}</span>
                            <span className="text-[9px] text-zinc-500 block mt-0.5">
                              Logged at {formatTime(log.timestamp)}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteLog(log.id)}
                          className="p-1 text-zinc-600 hover:text-rose-455 hover:bg-rose-500/10 rounded transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 cursor-pointer"
                          title="Delete Log"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>

            </div>
          </div>

          {/* 7-Day Compliance History Section */}
          <div className="col-span-12 bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl flex flex-col space-y-4 animate-fadeIn">
            <div className="flex items-center space-x-2 border-b border-zinc-850 pb-3">
              <Award className="w-4.5 h-4.5 text-rose-400" />
              <h3 className="text-sm font-bold text-zinc-200">7-Day Compliance History</h3>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-7 gap-3 pt-1">
              {history.map((day) => {
                const d = new Date(day.date + 'T00:00:00');
                const isCurrent = day.date === currentDate;
                const completedCount = [
                  day.checklist.morning_meds,
                  day.checklist.evening_meds,
                  day.checklist.morning_inject
                ].filter(Boolean).length;

                return (
                  <div 
                    key={day.date}
                    onClick={() => setCurrentDate(day.date)}
                    className={`p-3.5 rounded-xl border transition-all text-center flex flex-col space-y-2.5 cursor-pointer hover:scale-[1.02] ${
                      isCurrent 
                        ? 'bg-rose-500/5 border-rose-500/30 shadow-md shadow-rose-500/5' 
                        : 'bg-zinc-950/20 border-white/5 hover:border-zinc-800'
                    }`}
                  >
                    <div className="text-[10px] font-bold text-zinc-400">
                      {d.toLocaleDateString(undefined, { weekday: 'short' })}
                    </div>
                    <div className={`text-xs font-bold leading-none ${isCurrent ? 'text-rose-400' : 'text-zinc-200'}`}>
                      {d.toLocaleDateString(undefined, { day: 'numeric' })}
                    </div>
                    
                    {/* Visual checklist indicators */}
                    <div className="flex items-center justify-center space-x-1">
                      <div 
                        className={`w-2.5 h-2.5 rounded-full border ${
                          day.checklist.morning_meds 
                            ? 'bg-emerald-500 border-emerald-400' 
                            : 'bg-zinc-900 border-white/10'
                        }`} 
                        title="Morning Meds"
                      />
                      <div 
                        className={`w-2.5 h-2.5 rounded-full border ${
                          day.checklist.evening_meds 
                            ? 'bg-emerald-500 border-emerald-400' 
                            : 'bg-zinc-900 border-white/10'
                        }`} 
                        title="Evening Meds"
                      />
                      <div 
                        className={`w-2.5 h-2.5 rounded-full border ${
                          day.checklist.morning_inject 
                            ? 'bg-rose-500 border-rose-400' 
                            : 'bg-zinc-900 border-white/10'
                        }`} 
                        title="Morning Inject"
                      />
                    </div>
                    
                    <div className="text-[9px] font-medium text-zinc-500 flex flex-col space-y-0.5">
                      <span className="text-zinc-400">{completedCount} / 3 Check</span>
                      <span>💉 {day.meal_injections_count} Logged</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      ) : null}
    </div>
  );
}
