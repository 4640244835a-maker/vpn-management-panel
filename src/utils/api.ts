import { GitHubUser, GitHubRepo, CommitItem, CommitDetail, BranchItem, PullRequestItem, GitHubIssue, TaskItem } from '../types';

export const api = {
  // Check health and user
  getUser: async (tokenOverride?: string): Promise<GitHubUser | null> => {
    try {
      const headers: Record<string, string> = {};
      if (tokenOverride) headers['x-github-token'] = tokenOverride;
      const res = await fetch('/api/github/user', { headers });
      if (!res.ok) {
        return null;
      }
      return await res.json();
    } catch {
      return null;
    }
  },

  // Repositories
  getRepos: async (tokenOverride?: string): Promise<GitHubRepo[]> => {
    try {
      const headers: Record<string, string> = {};
      if (tokenOverride) headers['x-github-token'] = tokenOverride;
      const res = await fetch('/api/github/repos', { headers });
      if (!res.ok) {
        return [];
      }
      return await res.json();
    } catch {
      return [];
    }
  },

  // Commits
  getCommits: async (owner: string, repo: string, page = 1, per_page = 30, sha?: string, tokenOverride?: string): Promise<CommitItem[]> => {
    const headers: Record<string, string> = {};
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    let url = `/api/github/repo/${owner}/${repo}/commits?page=${page}&per_page=${per_page}`;
    if (sha) url += `&sha=${sha}`;
    const res = await fetch(url, { headers });
    if (!res.ok) throw new Error('Failed to fetch commits');
    return res.json();
  },

  // Repository Contents (Directory or File)
  getRepoContents: async (
    owner: string, 
    repo: string, 
    path = '', 
    ref = '', 
    tokenOverride?: string
  ): Promise<{ type: 'dir'; items: any[] } | { type: 'file'; name: string; path: string; sha: string; size: number; text: string; download_url?: string }> => {
    const headers: Record<string, string> = {};
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    let url = `/api/github/repo/${owner}/${repo}/contents?path=${encodeURIComponent(path)}`;
    if (ref) url += `&ref=${encodeURIComponent(ref)}`;
    const res = await fetch(url, { headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to fetch repository contents');
    }
    return res.json();
  },

  // Update / Commit File to GitHub Repository
  updateRepoFile: async (
    owner: string,
    repo: string,
    data: { path: string; content: string; message?: string; sha?: string; branch?: string },
    tokenOverride?: string
  ): Promise<{ success: boolean; commit: { sha: string; message: string; html_url: string }; content: { name: string; path: string; sha: string } }> => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    const res = await fetch(`/api/github/repo/${owner}/${repo}/contents`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.details || err.error || 'Failed to update file in GitHub repository');
    }
    return res.json();
  },

  // Commit Details with Diff
  getCommitDetail: async (owner: string, repo: string, sha: string, tokenOverride?: string): Promise<CommitDetail> => {
    const headers: Record<string, string> = {};
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    const res = await fetch(`/api/github/repo/${owner}/${repo}/commit/${sha}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch commit details');
    return res.json();
  },

  // Branches
  getBranches: async (owner: string, repo: string, tokenOverride?: string): Promise<BranchItem[]> => {
    const headers: Record<string, string> = {};
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    const res = await fetch(`/api/github/repo/${owner}/${repo}/branches`, { headers });
    if (!res.ok) throw new Error('Failed to fetch branches');
    return res.json();
  },

  // Pull Requests
  getPullRequests: async (owner: string, repo: string, state = 'all', tokenOverride?: string): Promise<PullRequestItem[]> => {
    const headers: Record<string, string> = {};
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    const res = await fetch(`/api/github/repo/${owner}/${repo}/pulls?state=${state}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch pull requests');
    return res.json();
  },

  // GitHub Issues
  getIssues: async (owner: string, repo: string, state = 'all', tokenOverride?: string): Promise<GitHubIssue[]> => {
    const headers: Record<string, string> = {};
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    const res = await fetch(`/api/github/repo/${owner}/${repo}/issues?state=${state}`, { headers });
    if (!res.ok) throw new Error('Failed to fetch issues');
    return res.json();
  },

  createIssue: async (owner: string, repo: string, title: string, body: string, labels: string[] = [], tokenOverride?: string): Promise<GitHubIssue> => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (tokenOverride) headers['x-github-token'] = tokenOverride;
    const res = await fetch(`/api/github/repo/${owner}/${repo}/issues`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ title, body, labels }),
    });
    if (!res.ok) throw new Error('Failed to create issue');
    return res.json();
  },

  // Tasks Management
  getTasks: async (owner: string, repo: string): Promise<TaskItem[]> => {
    const res = await fetch(`/api/tasks/${owner}/${repo}`);
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
  },

  createTask: async (owner: string, repo: string, taskData: Partial<TaskItem>): Promise<TaskItem> => {
    const res = await fetch(`/api/tasks/${owner}/${repo}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  },

  updateTask: async (owner: string, repo: string, taskId: string, updates: Partial<TaskItem>): Promise<TaskItem> => {
    const res = await fetch(`/api/tasks/${owner}/${repo}/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
  },

  deleteTask: async (owner: string, repo: string, taskId: string): Promise<{ success: boolean; id: string }> => {
    const res = await fetch(`/api/tasks/${owner}/${repo}/${taskId}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete task');
    return res.json();
  },

  // AI Task Suggester
  suggestTasksWithAI: async (repoName: string, commits: CommitItem[]): Promise<Partial<TaskItem>[]> => {
    const res = await fetch('/api/ai/suggest-tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repoName, commits }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to suggest tasks');
    }
    const data = await res.json();
    return data.tasks || [];
  },
};
