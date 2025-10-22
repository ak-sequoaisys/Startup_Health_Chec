declare global {
  interface Window {
    dataLayer: any[];
    __GTM_ID__?: string;
  }
}

const GTM_ID = import.meta.env.VITE_GTM_ID;

if (GTM_ID) {
  window.__GTM_ID__ = GTM_ID;
}

export const initializeGTM = () => {
  if (!GTM_ID) {
    console.warn('GTM ID not configured. Analytics events will not be tracked.');
    return;
  }
  
  window.dataLayer = window.dataLayer || [];
};

export const trackEvent = (eventName: string, eventData?: Record<string, any>) => {
  if (typeof window === 'undefined' || !window.dataLayer) {
    return;
  }

  window.dataLayer.push({
    event: eventName,
    ...eventData,
  });

  console.log('GTM Event:', eventName, eventData);
};

export const trackStartAssessment = (contactInfo: {
  company_name: string;
  industry?: string;
  employee_range: string;
}) => {
  trackEvent('start_assessment', {
    company_name: contactInfo.company_name,
    industry: contactInfo.industry || 'Not specified',
    employee_range: contactInfo.employee_range,
    timestamp: new Date().toISOString(),
  });
};

export const trackAnswerQuestion = (questionData: {
  question_id: string;
  question_number: number;
  category: string;
  answer_value: string;
  score: number;
}) => {
  trackEvent('answer_question', {
    question_id: questionData.question_id,
    question_number: questionData.question_number,
    category: questionData.category,
    answer_value: questionData.answer_value,
    score: questionData.score,
    timestamp: new Date().toISOString(),
  });
};

export const trackViewResults = (resultData: {
  assessment_id: string;
  overall_score: number;
  overall_percentage: number;
  risk_level: string;
  company_name: string;
}) => {
  trackEvent('view_results', {
    assessment_id: resultData.assessment_id,
    overall_score: resultData.overall_score,
    overall_percentage: resultData.overall_percentage,
    risk_level: resultData.risk_level,
    company_name: resultData.company_name,
    timestamp: new Date().toISOString(),
  });
};

export const trackReportDownload = (reportData: {
  assessment_id: string;
  company_name: string;
  overall_percentage: number;
  risk_level: string;
}) => {
  trackEvent('report_download', {
    assessment_id: reportData.assessment_id,
    company_name: reportData.company_name,
    overall_percentage: reportData.overall_percentage,
    risk_level: reportData.risk_level,
    timestamp: new Date().toISOString(),
  });
};
