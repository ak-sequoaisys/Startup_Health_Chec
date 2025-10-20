import { Question, AssessmentSubmission, AssessmentResult, StartAssessmentRequest, Lead } from "./types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function startAssessment(data: StartAssessmentRequest): Promise<Lead> {
  const response = await fetch(`${API_URL}/api/v1/assessments/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Failed to start assessment");
  }
  return response.json();
}

export async function fetchQuestions(): Promise<Question[]> {
  const response = await fetch(`${API_URL}/api/v1/questions`);
  if (!response.ok) {
    throw new Error("Failed to fetch questions");
  }
  return response.json();
}

export async function submitAnswer(assessmentId: string, questionId: string, answerValue: string): Promise<{ status: string; answers_count: number }> {
  const response = await fetch(`${API_URL}/api/v1/assessments/answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      assessment_id: assessmentId,
      question_id: questionId,
      answer_value: answerValue,
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to submit answer");
  }
  return response.json();
}

export async function submitAssessment(
  submission: AssessmentSubmission
): Promise<AssessmentResult> {
  const response = await fetch(`${API_URL}/api/v1/assessments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(submission),
  });
  if (!response.ok) {
    throw new Error("Failed to submit assessment");
  }
  return response.json();
}

export async function fetchAssessment(
  assessmentId: string
): Promise<AssessmentResult> {
  const response = await fetch(`${API_URL}/api/v1/assessments/${assessmentId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch assessment");
  }
  return response.json();
}

export async function generatePDFReport(assessmentId: string): Promise<Blob> {
  const response = await fetch(`${API_URL}/api/v1/reports/generate?assessment_id=${assessmentId}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to generate PDF report");
  }
  return response.blob();
}

export interface TrialRecord {
  email: string;
  company: string;
  states: string[] | null;
  score: number | null;
  rating: string | null;
  started: string;
  completed: string | null;
  status: string;
}

export interface TrialFilters {
  start_date?: string;
  end_date?: string;
  states?: string;
  score_min?: number;
  score_max?: number;
  status?: string;
}

export async function fetchAdminTrials(token: string, filters?: TrialFilters): Promise<TrialRecord[]> {
  const params = new URLSearchParams();
  if (filters?.start_date) params.append("start_date", filters.start_date);
  if (filters?.end_date) params.append("end_date", filters.end_date);
  if (filters?.states) params.append("states", filters.states);
  if (filters?.score_min !== undefined) params.append("score_min", filters.score_min.toString());
  if (filters?.score_max !== undefined) params.append("score_max", filters.score_max.toString());
  if (filters?.status) params.append("status", filters.status);

  const url = `${API_URL}/api/v1/admin/trials${params.toString() ? `?${params.toString()}` : ""}`;
  const response = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Unauthorized - Invalid or expired token");
    }
    throw new Error("Failed to fetch trials");
  }
  return response.json();
}

export async function exportTrialsCSV(token: string, filters?: TrialFilters): Promise<void> {
  const params = new URLSearchParams();
  if (filters?.start_date) params.append("start_date", filters.start_date);
  if (filters?.end_date) params.append("end_date", filters.end_date);
  if (filters?.states) params.append("states", filters.states);
  if (filters?.score_min !== undefined) params.append("score_min", filters.score_min.toString());
  if (filters?.score_max !== undefined) params.append("score_max", filters.score_max.toString());
  if (filters?.status) params.append("status", filters.status);

  const url = `${API_URL}/api/v1/admin/trials/export${params.toString() ? `?${params.toString()}` : ""}`;
  const response = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Unauthorized - Invalid or expired token");
    }
    throw new Error("Failed to export CSV");
  }
  
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = `trials_export_${new Date().toISOString().split("T")[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}
