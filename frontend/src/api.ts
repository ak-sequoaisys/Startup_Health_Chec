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
