import { useState, useEffect } from 'react';
import { api } from './api';
import type { Project, Task, TimeLog, DashboardSummary } from './types';
import { DashboardStats, formatDuration } from './components/DashboardStats';
import { ProjectSidebar } from './components/ProjectSidebar';
import { Timer } from './components/Timer';
import { TodoList } from './components/TodoList';
import { TimeLogList } from './components/TimeLogList';
import { Briefcase, AlertCircle, Clock, Heart } from 'lucide-react';
import { MedTracker } from './components/MedTracker';



function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [timeLogs, setTimeLogs] = useState<TimeLog[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'tasks' | 'meds'>('tasks');

  // Global Timer State
  const [timerProjectId, setTimerProjectId] = useState<number | null>(null);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Load initial data
  useEffect(() => {
    const initData = async () => {
      try {
        setLoading(true);
        const projs = await api.getProjects();
        setProjects(projs);
        
        const sum = await api.getDashboardSummary();
        setSummary(sum);

        const active = await api.getActiveTimer();
        if (active) {
          setTimerProjectId(active.project_id);
          setIsTimerRunning(!active.is_paused);
          const elapsed = active.is_paused
            ? active.accumulated_seconds
            : active.accumulated_seconds + Math.floor((new Date(active.server_time).getTime() - new Date(active.start_time).getTime()) / 1000);
          setElapsedSeconds(elapsed >= 0 ? elapsed : 0);
        }

        if (projs.length > 0) {
          setSelectedProjectId(projs[0].id);
        }
      } catch (err) {
        setError('Failed to load application data. Is the backend server running?');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    initData();
  }, []);

  // Fetch project-specific data (tasks & logs) when selection changes
  useEffect(() => {
    if (selectedProjectId === null) {
      setTasks([]);
      setTimeLogs([]);
      return;
    }

    const fetchProjectDetails = async () => {
      try {
        const pTasks = await api.getTasks(selectedProjectId);
        const pLogs = await api.getTimeLogs(selectedProjectId);
        setTasks(pTasks);
        setTimeLogs(pLogs);
      } catch (err) {
        console.error(`Failed to load details for project ${selectedProjectId}:`, err);
      }
    };

    fetchProjectDetails();
  }, [selectedProjectId]);

  // Global timer ticking effect
  useEffect(() => {
    let interval: any = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  // Poll active timer status to keep in sync with other clients
  useEffect(() => {
    const syncTimer = async () => {
      try {
        const active = await api.getActiveTimer();
        if (active) {
          setTimerProjectId(active.project_id);
          setIsTimerRunning(!active.is_paused);
          const elapsed = active.is_paused
            ? active.accumulated_seconds
            : active.accumulated_seconds + Math.floor((new Date(active.server_time).getTime() - new Date(active.start_time).getTime()) / 1000);
          setElapsedSeconds(elapsed >= 0 ? elapsed : 0);
        } else {
          if (timerProjectId !== null) {
            setIsTimerRunning(false);
            setTimerProjectId(null);
            setElapsedSeconds(0);
            await refreshSummary();
            if (selectedProjectId) {
              const pLogs = await api.getTimeLogs(selectedProjectId);
              setTimeLogs(pLogs);
            }
          }
        }
      } catch (err) {
        console.error('Failed to sync timer:', err);
      }
    };

    const timerId = setInterval(syncTimer, 5000);
    return () => clearInterval(timerId);
  }, [isTimerRunning, selectedProjectId]);

  // Real-time Live Sync via WebSockets
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWS = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/ws`;
      
      ws = new WebSocket(wsUrl);

      ws.onmessage = async (event) => {
        if (event.data === 'refresh') {
          console.log('[LiveSync] Refresh signal received from server');
          
          try {
            const projs = await api.getProjects();
            setProjects(projs);
            
            const sum = await api.getDashboardSummary();
            setSummary(sum);

             const active = await api.getActiveTimer();
             if (active) {
               setTimerProjectId(active.project_id);
               setIsTimerRunning(!active.is_paused);
               const elapsed = active.is_paused
                 ? active.accumulated_seconds
                 : active.accumulated_seconds + Math.floor((new Date(active.server_time).getTime() - new Date(active.start_time).getTime()) / 1000);
               setElapsedSeconds(elapsed >= 0 ? elapsed : 0);
             } else {
               setIsTimerRunning(false);
               setTimerProjectId(null);
               setElapsedSeconds(0);
             }

            if (selectedProjectId) {
              const pTasks = await api.getTasks(selectedProjectId);
              const pLogs = await api.getTimeLogs(selectedProjectId);
              setTasks(pTasks);
              setTimeLogs(pLogs);
            }
          } catch (err) {
            console.error('[LiveSync] Error refreshing data:', err);
          }
        }
      };

      ws.onclose = () => {
        reconnectTimeout = setTimeout(connectWS, 3000);
      };

      ws.onerror = (err) => {
        console.error('[LiveSync] WebSocket error:', err);
        ws?.close();
      };
    };

    connectWS();

    return () => {
      ws?.close();
      clearTimeout(reconnectTimeout);
    };
  }, [selectedProjectId, isTimerRunning]);

  // Refresh dashboard summary
  const refreshSummary = async () => {
    try {
      const sum = await api.getDashboardSummary();
      setSummary(sum);
    } catch (err) {
      console.error('Failed to update summary:', err);
    }
  };

  // Handlers
  const handleSelectProject = (id: number) => {
    setSelectedProjectId(id);
  };

  const handleCreateProject = async (name: string, description: string) => {
    const newProj = await api.createProject(name, description);
    setProjects((prev) => [newProj, ...prev]);
    setSelectedProjectId(newProj.id);
    await refreshSummary();
  };

  const handleDeleteProject = async (id: number) => {
    await api.deleteProject(id);
    setProjects((prev) => prev.filter((p) => p.id !== id));
    
    // If we deleted the active project or the tracked project
    if (selectedProjectId === id) {
      const remaining = projects.filter((p) => p.id !== id);
      setSelectedProjectId(remaining.length > 0 ? remaining[0].id : null);
    }
    if (timerProjectId === id) {
      setIsTimerRunning(false);
      setTimerProjectId(null);
      setElapsedSeconds(0);
    }
    await refreshSummary();
  };

  const handleAddTask = async (title: string, priority: 'High' | 'Medium' | 'Low', dueDate: string | null) => {
    if (!selectedProjectId) return;
    const newTask = await api.createTask(selectedProjectId, title, priority, dueDate);
    setTasks((prev) => [...prev, newTask]);
    await refreshSummary();
  };

  const handleToggleTask = async (id: number, isCompleted: boolean) => {
    const updated = await api.updateTask(id, { is_completed: isCompleted });
    setTasks((prev) => prev.map((t) => (t.id === id ? updated : t)));
    await refreshSummary();
  };

  const handleDeleteTask = async (id: number) => {
    await api.deleteTask(id);
    setTasks((prev) => prev.filter((t) => t.id !== id));
    await refreshSummary();
  };

  // Timer controls
  const handleStartTimer = async () => {
    if (!selectedProjectId) return;
    try {
      const active = await api.startActiveTimer(selectedProjectId);
      setTimerProjectId(active.project_id);
      setIsTimerRunning(!active.is_paused);
      const elapsed = active.is_paused
        ? active.accumulated_seconds
        : active.accumulated_seconds + Math.floor((new Date(active.server_time).getTime() - new Date(active.start_time).getTime()) / 1000);
      setElapsedSeconds(elapsed >= 0 ? elapsed : 0);
      await refreshSummary();
    } catch (err) {
      console.error(err);
    }
  };

  const handlePauseTimer = async () => {
    try {
      await api.pauseActiveTimer();
      setIsTimerRunning(false);
      await refreshSummary();
    } catch (err) {
      console.error(err);
    }
  };

  const handleStopTimer = async (description: string) => {
    try {
      const logged = await api.stopActiveTimer(description);
      // If active view is the project we just tracked, update its log list
      if (selectedProjectId === timerProjectId) {
        setTimeLogs((prev) => [logged, ...prev]);
      }
      setIsTimerRunning(false);
      setTimerProjectId(null);
      setElapsedSeconds(0);
      await refreshSummary();
    } catch (err) {
      console.error('Failed to stop active timer:', err);
    }
  };

  const handleCancelTimer = async () => {
    try {
      await api.discardActiveTimer();
      setIsTimerRunning(false);
      setTimerProjectId(null);
      setElapsedSeconds(0);
      await refreshSummary();
    } catch (err) {
      console.error(err);
    }
  };

  // Manual Time Log
  const handleAddManualLog = async (description: string, startTime: string, endTime: string) => {
    if (!selectedProjectId) return;
    const logged = await api.createTimeLog(selectedProjectId, {
      description,
      start_time: startTime,
      end_time: endTime,
    });
    setTimeLogs((prev) => [logged, ...prev]);
    await refreshSummary();
  };

  const handleDeleteLog = async (id: number) => {
    await api.deleteTimeLog(id);
    setTimeLogs((prev) => prev.filter((log) => log.id !== id));
    await refreshSummary();
  };

  // Helpers
  const activeProject = projects.find((p) => p.id === selectedProjectId) || null;
  const trackedProject = projects.find((p) => p.id === timerProjectId) || null;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-slate-100">
        <div className="w-12 h-12 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mb-4"></div>
        <p className="text-sm font-semibold tracking-wide text-zinc-400">Loading TaskTracker Workspace...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      {/* Premium Header */}
      <header className="border-b border-zinc-900 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-gradient-to-tr from-violet-500 to-indigo-500 text-white shadow-md shadow-violet-500/10">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-zinc-100 tracking-tight leading-none">TaskTracker</h1>
            <span className="text-[10px] text-zinc-400 font-medium">Single-User Dashboard</span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 bg-zinc-900/60 p-1 rounded-lg border border-white/5">
          <button
            onClick={() => setActiveTab('tasks')}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
              activeTab === 'tasks'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Tasks & Time</span>
          </button>
          <button
            onClick={() => setActiveTab('meds')}
            className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
              activeTab === 'meds'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-450 hover:text-zinc-200'
            }`}
          >
            <Heart className="w-3.5 h-3.5 text-rose-500" />
            <span>Med Tracker</span>
          </button>
        </div>

        {/* Global Running Timer banner */}
        {timerProjectId && trackedProject && selectedProjectId !== timerProjectId && (
          <div className="hidden md:flex items-center bg-violet-950/20 border border-violet-500/30 rounded-lg px-4 py-2 space-x-4 animate-pulse">
            <span className="text-xs text-violet-400 font-medium">
              Tracking: <span className="font-bold">{trackedProject.name}</span>
            </span>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleSelectProject(timerProjectId)}
                className="px-2 py-0.5 rounded bg-violet-500/20 hover:bg-violet-500/30 text-[10px] text-violet-300 font-semibold"
              >
                View
              </button>
            </div>
          </div>
        )}

        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Local Database Connected
          </span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        {error && (
          <div className="p-4 mb-6 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center space-x-3 text-rose-400">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <p className="text-xs font-medium">{error}</p>
          </div>
        )}

        {activeTab === 'tasks' ? (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Projects Sidebar (Left) */}
            <div className="md:col-span-3 flex flex-col h-[600px] md:h-auto animate-fadeIn">
              <ProjectSidebar
                projects={projects}
                selectedProjectId={selectedProjectId}
                onSelectProject={handleSelectProject}
                onCreateProject={handleCreateProject}
                onDeleteProject={handleDeleteProject}
                summaries={summary?.project_summaries || []}
              />
            </div>

            {/* Active Dashboard & Details (Right) */}
            <div className="md:col-span-9 flex flex-col space-y-6">
              {/* Stats Bar */}
              <DashboardStats summary={summary} />

              {activeProject ? (
                <div className="space-y-6 animate-fadeIn">
                  {/* Project Title / Banner */}
                  <div className="p-6 bg-gradient-to-r from-zinc-900/15 to-zinc-900/5 border border-white/10 rounded-xl flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <h2 className="text-lg font-bold text-zinc-100 leading-tight">{activeProject.name}</h2>
                      {activeProject.description ? (
                        <p className="text-xs text-zinc-400 mt-2 leading-relaxed max-w-2xl">{activeProject.description}</p>
                      ) : (
                        <p className="text-xs italic text-zinc-650 mt-2">No description provided for this project.</p>
                      )}
                    </div>
                    {summary && (() => {
                      const projSum = summary.project_summaries.find((s) => s.project_id === activeProject.id);
                      const totalWork = projSum?.total_work_seconds || 0;
                      const totalBilled = projSum?.total_billed_seconds || 0;
                      const totalUnbilled = projSum?.total_unbilled_seconds || 0;
                      return (
                        <div className="shrink-0 flex items-center gap-3 bg-zinc-950/20 border border-white/5 rounded-lg p-3 self-start md:self-auto">
                          <div className="text-center px-2">
                            <p className="text-[8px] text-zinc-500 font-bold uppercase tracking-wider">Tracked</p>
                            <p className="text-xs font-bold text-violet-400 mt-0.5">{formatDuration(totalWork)}</p>
                          </div>
                          <div className="w-px h-6 bg-zinc-800" />
                          <div className="text-center px-2">
                            <p className="text-[8px] text-zinc-500 font-bold uppercase tracking-wider">Billed</p>
                            <p className="text-xs font-bold text-rose-400 mt-0.5">{formatDuration(totalBilled)}</p>
                          </div>
                          <div className="w-px h-6 bg-zinc-800" />
                          <div className="text-center px-2">
                            <p className="text-[8px] text-zinc-500 font-bold uppercase tracking-wider">Unbilled</p>
                            <p className={`text-xs font-bold mt-0.5 ${totalUnbilled < 0 ? 'text-rose-400' : 'text-zinc-100'}`}>
                              {formatDuration(totalUnbilled)}
                            </p>
                          </div>
                        </div>
                      );
                    })()}
                  </div>

                  {/* Timer Widget */}
                  <Timer
                    projectName={activeProject.name}
                    isTimerRunning={timerProjectId === activeProject.id && isTimerRunning}
                    elapsedSeconds={timerProjectId === activeProject.id ? elapsedSeconds : 0}
                    onStart={handleStartTimer}
                    onPause={handlePauseTimer}
                    onStop={handleStopTimer}
                    onCancel={handleCancelTimer}
                  />

                  {/* Two-Column split details */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <TodoList
                      tasks={tasks}
                      onAddTask={handleAddTask}
                      onToggleTask={handleToggleTask}
                      onDeleteTask={handleDeleteTask}
                    />
                    
                    <TimeLogList
                      timeLogs={timeLogs}
                      onAddManualLog={handleAddManualLog}
                      onDeleteLog={handleDeleteLog}
                    />
                  </div>
                </div>
              ) : projects.length > 0 ? (
                <div className="bg-zinc-900/20 border border-white/10 backdrop-blur-md rounded-xl p-6 shadow-xl flex-1 animate-fadeIn">
                  <h3 className="text-sm font-bold text-zinc-200 mb-4 flex items-center gap-2">
                    <Briefcase className="w-4 h-4 text-violet-400" />
                    Per-Project Time & Progress Summary
                  </h3>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-zinc-800 text-[10px] text-zinc-400 font-semibold uppercase tracking-wider">
                          <th className="pb-3 pl-2">Project</th>
                          <th className="pb-3 text-right">Tracked</th>
                          <th className="pb-3 text-right">Billed</th>
                          <th className="pb-3 text-right font-semibold text-zinc-300">Unbilled</th>
                          <th className="pb-3 text-center pl-4">Tasks Status</th>
                          <th className="pb-3 pl-6">Completion</th>
                          <th className="pb-3 text-right pr-2">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-850/50">
                        {projects.map((p) => {
                          const pSum = summary?.project_summaries.find((s) => s.project_id === p.id);
                          const totalWork = pSum?.total_work_seconds || 0;
                          const totalBilled = pSum?.total_billed_seconds || 0;
                          const totalUnbilled = pSum?.total_unbilled_seconds || 0;
                          const totalTasks = pSum?.total_tasks || 0;
                          const completedTasks = pSum?.completed_tasks || 0;
                          const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
                          
                          return (
                            <tr key={p.id} className="hover:bg-zinc-900/30 transition-colors">
                              <td className="py-3.5 pl-2">
                                <span className="text-xs font-semibold text-zinc-200 block">{p.name}</span>
                                {p.description && (
                                  <span className="text-[10px] text-zinc-500 block truncate max-w-xs mt-0.5">{p.description}</span>
                                )}
                              </td>
                              <td className="py-3.5 text-right font-mono text-xs text-violet-400">
                                {formatDuration(totalWork)}
                              </td>
                              <td className="py-3.5 text-right font-mono text-xs text-rose-400">
                                {formatDuration(totalBilled)}
                              </td>
                              <td className={`py-3.5 text-right font-mono text-xs font-semibold ${totalUnbilled < 0 ? 'text-rose-400' : 'text-zinc-200'}`}>
                                {formatDuration(totalUnbilled)}
                              </td>
                              <td className="py-3.5 text-center text-xs text-zinc-400 pl-4">
                                {completedTasks} / {totalTasks} Completed
                              </td>
                              <td className="py-3.5 pl-6">
                                <div className="flex items-center space-x-2">
                                  <div className="w-20 bg-zinc-800 rounded-full h-1.5 shrink-0">
                                    <div
                                      className="bg-violet-500 h-1.5 rounded-full"
                                      style={{ width: `${completionRate}%` }}
                                    />
                                  </div>
                                  <span className="text-[10px] font-bold text-zinc-300">{completionRate}%</span>
                                </div>
                              </td>
                              <td className="py-3.5 text-right pr-2">
                                <button
                                  onClick={() => handleSelectProject(p.id)}
                                  className="px-2.5 py-1 rounded-md bg-zinc-800 hover:bg-zinc-750 text-zinc-300 text-[10px] font-semibold transition-all cursor-pointer"
                                >
                                  Open
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center p-12 bg-zinc-900/10 border border-white/5 border-dashed rounded-xl text-center min-h-[400px]">
                  <div className="p-4 rounded-lg bg-zinc-900/30 text-zinc-500 mb-4 border border-white/5">
                    <Briefcase className="w-8 h-8" />
                  </div>
                  <h3 className="text-md font-bold text-zinc-300">No Active Project</h3>
                  <p className="text-xs text-zinc-500 max-w-xs mt-2 leading-relaxed">
                    Select an existing project from the sidebar, or create a new one to start tracking your tasks and time.
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="animate-fadeIn">
            <MedTracker />
          </div>
        )}
      </main>

      {/* Sleek Footer */}
      <footer className="border-t border-zinc-900 bg-zinc-950/40 py-4 px-6 text-center text-[10px] text-zinc-500">
        TaskTracker SPA &copy; {new Date().getFullYear()} &bull; Built with FastAPI & React Tailwind v4
      </footer>
    </div>
  );
}

export default App;
