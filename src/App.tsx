import React, { useState, useEffect, useCallback } from 'react';
import { 
  GitHubUser, 
  GitHubRepo, 
  CommitItem, 
  CommitDetail, 
  BranchItem, 
  PullRequestItem, 
  GitHubIssue, 
  TaskItem, 
  TaskStatus 
} from './types';
import { api } from './utils/api';
import { Header } from './components/Header';
import { RepoOverview } from './components/RepoOverview';
import { CommitTracker } from './components/CommitTracker';
import { TaskManager } from './components/TaskManager';
import { BranchesAndPRs } from './components/BranchesAndPRs';
import { GitHubIssuesView } from './components/GitHubIssuesView';
import { CodeEditor } from './components/CodeEditor';
import { CommitDetailModal } from './components/CommitDetailModal';
import { TaskModal } from './components/TaskModal';
import { NewIssueModal } from './components/NewIssueModal';
import { 
  AlertCircle, 
  RefreshCw, 
  GitCommit, 
  CheckSquare, 
  Layers, 
  GitBranch, 
  Sparkles,
  Code
} from 'lucide-react';

export default function App() {
  const [lang, setLang] = useState<'fa' | 'en'>('fa');
  const [user, setUser] = useState<GitHubUser | null>(null);
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<GitHubRepo | null>(null);

  // Active view tab
  const [activeTab, setActiveTab] = useState<'overview' | 'commits' | 'tasks' | 'editor' | 'branches_prs' | 'issues'>('overview');
  const [editorFilePath, setEditorFilePath] = useState<string | null>(null);

  // Repo Data
  const [commits, setCommits] = useState<CommitItem[]>([]);
  const [branches, setBranches] = useState<BranchItem[]>([]);
  const [selectedBranch, setSelectedBranch] = useState<string>('');
  const [pullRequests, setPullRequests] = useState<PullRequestItem[]>([]);
  const [issues, setIssues] = useState<GitHubIssue[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);

  // Modals & Inspections
  const [inspectingCommit, setInspectingCommit] = useState<CommitDetail | null>(null);
  const [isCommitModalOpen, setIsCommitModalOpen] = useState(false);

  // Task Modal state
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskItem | null>(null);
  const [taskModalInitialCommit, setTaskModalInitialCommit] = useState<string | null>(null);
  const [taskModalInitialTitle, setTaskModalInitialTitle] = useState<string | null>(null);

  // New Issue Modal
  const [isNewIssueModalOpen, setIsNewIssueModalOpen] = useState(false);

  // AI Suggestions
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [suggestedTasks, setSuggestedTasks] = useState<Partial<TaskItem>[]>([]);

  // Loading & Error states
  const [isLoadingMain, setIsLoadingMain] = useState(true);
  const [isLoadingRepoData, setIsLoadingRepoData] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const isFa = lang === 'fa';

  // 1. Initial Load: User and Repositories
  const loadUserAndRepos = useCallback(async () => {
    setIsLoadingMain(true);
    setErrorMessage(null);
    try {
      const [userData, reposData] = await Promise.all([
        api.getUser().catch(() => null),
        api.getRepos().catch(() => []),
      ]);

      setUser(userData || {
        login: 'vpn-admin',
        id: 1,
        avatar_url: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop&q=80',
        html_url: 'https://github.com/4640244835a-maker/vpn-management-panel',
        name: 'VPN Admin',
        company: null,
        blog: '',
        location: null,
        email: null,
        bio: 'Marzban Xray VPN Server Administrator',
        public_repos: 1,
        followers: 0,
        following: 0,
      });

      const safeRepos = reposData && reposData.length > 0 ? reposData : [
        {
          id: 1,
          name: 'vpn-management-panel',
          full_name: '4640244835a-maker/vpn-management-panel',
          private: true,
          html_url: 'https://github.com/4640244835a-maker/vpn-management-panel',
          description: 'Marzban & Xray VPN Core Management Dashboard on Railway',
          default_branch: 'main',
          updated_at: new Date().toISOString(),
          pushed_at: new Date().toISOString(),
          stargazers_count: 0,
          forks_count: 0,
          open_issues_count: 0,
          language: 'TypeScript',
        }
      ];

      setRepos(safeRepos);
      const defaultRepo = 
        safeRepos.find((r) => r.name === 'vpn-management-panel') || 
        safeRepos[0];
      setSelectedRepo(defaultRepo);
    } catch (err: any) {
      console.warn('Silent GitHub load fallback:', err);
      // Fallback repo so dashboard never gets blocked
      const fallbackRepo: GitHubRepo = {
        id: 1,
        name: 'vpn-management-panel',
        full_name: '4640244835a-maker/vpn-management-panel',
        private: true,
        html_url: 'https://github.com/4640244835a-maker/vpn-management-panel',
        description: 'Marzban & Xray VPN Core Management Dashboard on Railway',
        default_branch: 'main',
        updated_at: new Date().toISOString(),
        pushed_at: new Date().toISOString(),
        stargazers_count: 0,
        forks_count: 0,
        open_issues_count: 0,
        language: 'TypeScript',
      };
      setRepos([fallbackRepo]);
      setSelectedRepo(fallbackRepo);
    } finally {
      setIsLoadingMain(false);
    }
  }, []);

  useEffect(() => {
    loadUserAndRepos();
  }, [loadUserAndRepos]);

  // 2. Load Selected Repository Data (Commits, Branches, PRs, Issues, Tasks)
  const loadRepoData = useCallback(async (repo: GitHubRepo, branch?: string) => {
    setIsLoadingRepoData(true);
    try {
      const [owner, repoName] = repo.full_name.split('/');
      
      const [commitsData, branchesData, pullsData, issuesData, tasksData] = await Promise.all([
        api.getCommits(owner, repoName, 1, 35, branch || undefined).catch(() => []),
        api.getBranches(owner, repoName).catch(() => []),
        api.getPullRequests(owner, repoName).catch(() => []),
        api.getIssues(owner, repoName).catch(() => []),
        api.getTasks(owner, repoName).catch(() => []),
      ]);

      setCommits(commitsData);
      setBranches(branchesData);
      setPullRequests(pullsData);
      setIssues(issuesData);

      // If this repository has no tasks yet, seed initial smart tasks based on repo content
      if (tasksData.length === 0 && commitsData.length > 0) {
        const initialTasksToSeed: Partial<TaskItem>[] = [
          {
            title: isFa ? 'بررسی معماری پنل مدیریت Marzban Xray' : 'Review Marzban Xray Panel Architecture',
            description: isFa 
              ? 'تست یکپارچگی بک‌اند، اتصالات API، و پیکربندی پروتکل‌های Xray بر اساس آخرین کامیت.' 
              : 'Test backend integration, API connections, and Xray protocol configs based on latest commit.',
            status: 'in_progress',
            priority: 'high',
            labels: ['Feature', 'Architecture'],
            linkedCommitSha: commitsData[0]?.sha || null,
            linkedBranch: repo.default_branch,
          },
          {
            title: isFa ? 'پیکربندی محیط تولید و استقرار با داکر' : 'Configure Docker Production Deployment',
            description: isFa 
              ? 'ایجاد فایل docker-compose و متغیرهای محیطی برای استقرار امن روی سرورهای ابری.' 
              : 'Create docker-compose and environment variables for cloud deployment.',
            status: 'todo',
            priority: 'medium',
            labels: ['DevOps', 'Docker'],
            linkedBranch: repo.default_branch,
          },
          {
            title: isFa ? 'پیاده‌سازی تست‌های واحد و بررسی خطاها' : 'Implement Unit Tests and Error Handling',
            description: isFa 
              ? 'نوشتن تست برای سرویس‌های اصلی پروکسی و لاگینگ جامع خطاها.' 
              : 'Write tests for core proxy services and structured logging.',
            status: 'backlog',
            priority: 'medium',
            labels: ['Testing', 'Quality'],
          },
        ];

        // Seed them sequentially
        const seeded: TaskItem[] = [];
        for (const t of initialTasksToSeed) {
          try {
            const saved = await api.createTask(owner, repoName, t);
            seeded.push(saved);
          } catch (e) {
            console.error('Seed task failed', e);
          }
        }
        setTasks(seeded);
      } else {
        setTasks(tasksData);
      }
    } catch (err: any) {
      console.error('Error fetching repo data:', err);
    } finally {
      setIsLoadingRepoData(false);
    }
  }, [isFa]);

  useEffect(() => {
    if (selectedRepo) {
      setSelectedBranch('');
      loadRepoData(selectedRepo);
    }
  }, [selectedRepo, loadRepoData]);

  // Branch filter change
  const handleBranchChange = (branchName: string) => {
    setSelectedBranch(branchName);
    if (selectedRepo) {
      loadRepoData(selectedRepo, branchName);
    }
  };

  // Inspect commit diff
  const handleInspectCommit = async (sha: string) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');
    try {
      const detail = await api.getCommitDetail(owner, repoName, sha);
      setInspectingCommit(detail);
      setIsCommitModalOpen(true);
    } catch (err) {
      console.error('Failed to inspect commit:', err);
    }
  };

  // Open task modal from commit
  const handleCreateTaskFromCommit = (sha: string, message: string) => {
    setEditingTask(null);
    setTaskModalInitialCommit(sha);
    setTaskModalInitialTitle(`${isFa ? 'پیگیری کامیت' : 'Follow up'}: ${message}`);
    setIsTaskModalOpen(true);
  };

  // Create or Update Task
  const handleSaveTask = async (taskData: Partial<TaskItem>, createAsGitHubIssue = false) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');

    let ghIssueNum: number | null = null;
    let ghIssueUrl: string | null = null;

    if (createAsGitHubIssue && taskData.title) {
      try {
        const ghIssue = await api.createIssue(
          owner, 
          repoName, 
          taskData.title, 
          taskData.description || '', 
          taskData.labels || []
        );
        ghIssueNum = ghIssue.number;
        ghIssueUrl = ghIssue.html_url;
        // Refresh issues list
        setIssues((prev) => [ghIssue, ...prev]);
      } catch (e) {
        console.error('Failed to create GitHub issue:', e);
      }
    }

    if (editingTask) {
      // Update existing task
      const updated = await api.updateTask(owner, repoName, editingTask.id, {
        ...taskData,
        githubIssueNumber: ghIssueNum || editingTask.githubIssueNumber,
        githubIssueUrl: ghIssueUrl || editingTask.githubIssueUrl,
      });
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } else {
      // Create new task
      const created = await api.createTask(owner, repoName, {
        ...taskData,
        githubIssueNumber: ghIssueNum,
        githubIssueUrl: ghIssueUrl,
      });
      setTasks((prev) => [created, ...prev]);
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId: string) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');
    await api.deleteTask(owner, repoName, taskId);
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  // Move task status
  const handleUpdateTaskStatus = async (taskId: string, newStatus: TaskStatus) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');
    // Optimistic UI update
    setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t)));
    try {
      await api.updateTask(owner, repoName, taskId, { status: newStatus });
    } catch (err) {
      console.error('Failed to update status', err);
      // Revert on failure
      loadRepoData(selectedRepo, selectedBranch);
    }
  };

  // Convert an existing GitHub Issue to a Kanban Task
  const handleConvertIssueToTask = async (issue: GitHubIssue) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');
    const newTask = await api.createTask(owner, repoName, {
      title: issue.title,
      description: issue.body || '',
      status: issue.state === 'closed' ? 'done' : 'todo',
      priority: 'medium',
      labels: issue.labels.map((l) => l.name),
      githubIssueNumber: issue.number,
      githubIssueUrl: issue.html_url,
      assignee: issue.user.login,
    });
    setTasks((prev) => [newTask, ...prev]);
    setActiveTab('tasks');
  };

  // Create GitHub Issue from Modal
  const handleCreateGitHubIssue = async (title: string, body: string, labels: string[]) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');
    const createdIssue = await api.createIssue(owner, repoName, title, body, labels);
    setIssues((prev) => [createdIssue, ...prev]);
  };

  // AI Task Suggester
  const handleSuggestTasksWithAI = async () => {
    if (!selectedRepo) return;
    setIsAiLoading(true);
    try {
      const suggestions = await api.suggestTasksWithAI(selectedRepo.name, commits);
      setSuggestedTasks(suggestions);
    } catch (err: any) {
      console.error('AI suggestion failed:', err);
      alert(isFa ? `خطا در تحلیل هوش مصنوعی: ${err.message}` : `AI Error: ${err.message}`);
    } finally {
      setIsAiLoading(false);
    }
  };

  // Add an AI suggested task directly
  const handleAddSuggestedTask = async (suggested: Partial<TaskItem>) => {
    if (!selectedRepo) return;
    const [owner, repoName] = selectedRepo.full_name.split('/');
    const newTask = await api.createTask(owner, repoName, {
      title: suggested.title,
      description: suggested.description,
      status: suggested.status || 'todo',
      priority: suggested.priority || 'medium',
      labels: suggested.labels || ['AI-Suggested'],
      linkedCommitSha: (suggested as any).suggestedCommitSha || null,
      linkedBranch: selectedRepo.default_branch,
    });
    setTasks((prev) => [newTask, ...prev]);
    setSuggestedTasks((prev) => prev.filter((s) => s.title !== suggested.title));
  };

  if (isLoadingMain) {
    return (
      <div 
        className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6"
        dir={isFa ? 'rtl' : 'ltr'}
      >
        <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 mb-4 shadow-xl">
          <GitCommit className="w-8 h-8 animate-pulse" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">
          {isFa ? 'اتصال به مخزن گیت‌هاب...' : 'Connecting to GitHub Repository...'}
        </h2>
        <p className="text-xs text-slate-400 max-w-sm text-center">
          {isFa
            ? 'در حال برقراری ارتباط امن با توکن دسترسی و بارگذاری اطلاعات پروژه‌ها و کامیت‌ها...'
            : 'Authenticating with access token and fetching repositories and commit logs...'}
        </p>
      </div>
    );
  }

  // Removed blocking error screen so user is never blocked if GitHub API fails
  return (
    <div 
      className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col antialiased transition-colors"
      dir={isFa ? 'rtl' : 'ltr'}
    >
      {/* Header */}
      <Header
        user={user}
        repos={repos}
        selectedRepo={selectedRepo}
        onSelectRepo={(r) => setSelectedRepo(r)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        lang={lang}
        setLang={setLang}
        onRefresh={() => selectedRepo && loadRepoData(selectedRepo, selectedBranch)}
        isLoading={isLoadingRepoData}
        taskCount={tasks.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {selectedRepo ? (
          <>
            {/* Overview View */}
            {activeTab === 'overview' && (
              <RepoOverview
                repo={selectedRepo}
                user={user}
                commits={commits}
                tasks={tasks}
                onNavigateTab={setActiveTab}
                onInspectCommit={handleInspectCommit}
                lang={lang}
              />
            )}

            {/* Commits & Changes Tracker View */}
            {activeTab === 'commits' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <GitCommit className="w-5 h-5 text-indigo-500" />
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                      {isFa ? 'پیگیری تغییرات، تاریخچه کامیت‌ها و کد دیف' : 'Commit History & Code Diffs'}
                    </h2>
                  </div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {commits.length} {isFa ? 'کامیت ردیابی‌شده' : 'commits tracked'}
                  </span>
                </div>

                <CommitTracker
                  commits={commits}
                  branches={branches}
                  selectedBranch={selectedBranch}
                  onSelectBranch={handleBranchChange}
                  onInspectCommit={handleInspectCommit}
                  onCreateTaskFromCommit={handleCreateTaskFromCommit}
                  lang={lang}
                  isLoading={isLoadingRepoData}
                />
              </div>
            )}

            {/* Tasks & Kanban Board View */}
            {activeTab === 'tasks' && (
              <TaskManager
                tasks={tasks}
                commits={commits}
                branches={branches}
                onAddTask={() => {
                  setEditingTask(null);
                  setTaskModalInitialCommit(null);
                  setTaskModalInitialTitle(null);
                  setIsTaskModalOpen(true);
                }}
                onEditTask={(task) => {
                  setEditingTask(task);
                  setIsTaskModalOpen(true);
                }}
                onDeleteTask={handleDeleteTask}
                onUpdateTaskStatus={handleUpdateTaskStatus}
                onInspectCommit={handleInspectCommit}
                onSuggestTasksWithAI={handleSuggestTasksWithAI}
                isAiLoading={isAiLoading}
                suggestedTasks={suggestedTasks}
                onAddSuggestedTask={handleAddSuggestedTask}
                lang={lang}
              />
            )}

            {/* Online Code Editor & Commit Updates View */}
            {activeTab === 'editor' && (
              <CodeEditor
                repo={selectedRepo}
                branches={branches}
                defaultBranch={selectedRepo.default_branch}
                lang={lang}
                initialFilePath={editorFilePath}
                onCommitCreated={async (newSha) => {
                  if (selectedRepo) {
                    await loadRepoData(selectedRepo, selectedBranch);
                  }
                }}
              />
            )}

            {/* Branches & PRs View */}
            {activeTab === 'branches_prs' && (
              <BranchesAndPRs
                repo={selectedRepo}
                branches={branches}
                pullRequests={pullRequests}
                lang={lang}
                isLoading={isLoadingRepoData}
                onSelectBranch={(bName) => {
                  setSelectedBranch(bName);
                  setActiveTab('commits');
                  loadRepoData(selectedRepo, bName);
                }}
              />
            )}

            {/* GitHub Issues View */}
            {activeTab === 'issues' && (
              <GitHubIssuesView
                issues={issues}
                lang={lang}
                onConvertIssueToTask={handleConvertIssueToTask}
                onCreateNewIssue={() => setIsNewIssueModalOpen(true)}
                isLoading={isLoadingRepoData}
              />
            )}
          </>
        ) : (
          <div className="p-12 text-center text-slate-400">
            <p>{isFa ? 'مخزنی برای نمایش انتخاب نشده است.' : 'No repository selected.'}</p>
          </div>
        )}
      </main>

      {/* Commit Detail Modal with Diff Viewer */}
      {isCommitModalOpen && (
        <CommitDetailModal
          commit={inspectingCommit}
          onClose={() => {
            setIsCommitModalOpen(false);
            setInspectingCommit(null);
          }}
          onCreateTaskFromCommit={handleCreateTaskFromCommit}
          onEditFile={(filePath) => {
            setEditorFilePath(filePath);
            setActiveTab('editor');
          }}
          lang={lang}
        />
      )}

      {/* Task Create / Edit Modal */}
      {isTaskModalOpen && (
        <TaskModal
          isOpen={isTaskModalOpen}
          onClose={() => {
            setIsTaskModalOpen(false);
            setEditingTask(null);
            setTaskModalInitialCommit(null);
            setTaskModalInitialTitle(null);
          }}
          onSave={handleSaveTask}
          initialTask={editingTask}
          initialCommitSha={taskModalInitialCommit}
          initialTitle={taskModalInitialTitle}
          commits={commits}
          branches={branches}
          lang={lang}
        />
      )}

      {/* New GitHub Issue Modal */}
      {isNewIssueModalOpen && (
        <NewIssueModal
          isOpen={isNewIssueModalOpen}
          onClose={() => setIsNewIssueModalOpen(false)}
          onCreate={handleCreateGitHubIssue}
          lang={lang}
        />
      )}
    </div>
  );
}
