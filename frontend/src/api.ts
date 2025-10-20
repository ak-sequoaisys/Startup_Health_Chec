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
  const response = await fetch(`${API_URL}/api/questions`);
  if (!response.ok) {
    throw new Error("Failed to fetch questions");
  }
  return response.json();
}

export async function submitAssessment(
  submission: AssessmentSubmission
): Promise<AssessmentResult> {
  const response = await fetch(`${API_URL}/api/assessments`, {
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
  const response = await fetch(`${API_URL}/api/assessments/${assessmentId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch assessment");
  }
  return response.json();
}
