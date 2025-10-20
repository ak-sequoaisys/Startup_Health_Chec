export type QuestionType = "multiple_choice" | "yes_no" | "text" | "number";

export type ComplianceCategory =
  | "employment_contracts"
  | "workplace_safety"
  | "payroll_tax"
  | "employee_benefits"
  | "workplace_policies"
  | "record_keeping"
  | "termination_procedures";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface QuestionOption {
  id: string;
  text: string;
  score: number;
  risk_level: RiskLevel;
}

export interface Question {
  id: string;
  category: ComplianceCategory;
  question_text: string;
  question_type: QuestionType;
  options?: QuestionOption[];
  help_text?: string;
  weight: number;
}

export interface Answer {
  question_id: string;
  answer_value: string;
  score: number;
}

export interface AssessmentSubmission {
  company_name: string;
  contact_name: string;
  email: string;
  phone?: string;
  company_size: string;
  industry?: string;
  answers: Answer[];
}

export interface CategoryScore {
  category: ComplianceCategory;
  score: number;
  max_score: number;
  percentage: number;
  risk_level: RiskLevel;
  issues: string[];
  recommendations: string[];
}

export interface AssessmentResult {
  id: string;
  submission_date: string;
  company_name: string;
  contact_name: string;
  email: string;
  overall_score: number;
  max_score: number;
  overall_percentage: number;
  overall_risk_level: RiskLevel;
  category_scores: CategoryScore[];
  priority_actions: string[];
}

export interface StartAssessmentRequest {
  email: string;
  company_name: string;
  industry?: string;
  employee_range: string;
  operating_states: string[];
  business_age?: string;
  consent: boolean;
}

export interface Lead {
  id: string;
  company_name: string;
  contact_name: string;
  email: string;
  phone?: string;
  company_size: string;
  industry?: string;
  employee_range?: string;
  operating_states?: string[];
  business_age?: string;
  consent: boolean;
  status: string;
  ip_hash?: string;
  user_agent?: string;
  submission_date: string;
  overall_score?: number;
  overall_risk_level?: RiskLevel;
  high_risk_categories?: string[];
}
