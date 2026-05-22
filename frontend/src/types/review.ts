export interface ReviewJobItem {
  id: number;
  repository_name: string;
  pr_number: number;
  pr_title: string;
  author: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | null;
  created_at: string;
  completed_at: string | null;
}

export interface ReviewIssue {
  file: string;
  line: string;
  level: 'LOW' | 'MEDIUM' | 'HIGH';
  issue: string;
  suggestion: string;
}

export interface SuggestedTestCase {
  name: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface MergeRecommendation {
  can_merge: boolean;
  reason: string;
}

export interface ReviewDetail {
  id: number;
  review_job_id: number;
  repository_name: string;
  pr_number: number;
  pr_title: string;
  pr_author: string;
  pr_url: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  summary: string;
  potential_bugs: ReviewIssue[];
  security_issues: ReviewIssue[];
  code_smells: ReviewIssue[];
  performance_issues: ReviewIssue[];
  suggested_test_cases: SuggestedTestCase[];
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  merge_recommendation: MergeRecommendation;
  ai_raw_response: string;
  github_comment_url: string | null;
  created_at: string;
}

export interface RepositoryItem {
  id: number;
  full_name: string;
  html_url: string;
  review_count: number;
  last_reviewed_at: string | null;
}
