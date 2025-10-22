import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import * as api from '../api';

vi.mock('../api');
vi.mock('../analytics', () => ({
  initializeGTM: vi.fn(),
  trackStartAssessment: vi.fn(),
  trackAnswerQuestion: vi.fn(),
  trackViewResults: vi.fn(),
  trackReportDownload: vi.fn(),
}));

const mockQuestions = [
  {
    id: 'q1',
    category: 'registration',
    question_text: 'Test Question 1',
    question_type: 'multiple_choice',
    options: [
      { id: 'opt1', text: 'Option 1', score: 10, risk_level: 'healthy' },
      { id: 'opt2', text: 'Option 2', score: 5, risk_level: 'moderate' },
    ],
    help_text: 'Help text for question 1',
    weight: 1,
  },
  {
    id: 'q2',
    category: 'employee_docs',
    question_text: 'Test Question 2',
    question_type: 'multiple_choice',
    options: [
      { id: 'opt3', text: 'Option 3', score: 10, risk_level: 'healthy' },
      { id: 'opt4', text: 'Option 4', score: 0, risk_level: 'high_risk' },
    ],
    help_text: 'Help text for question 2',
    weight: 2,
  },
];

const mockAssessmentResult = {
  id: 'assessment-123',
  submission_date: '2024-01-01T00:00:00Z',
  company_name: 'Test Company',
  contact_name: 'Test User',
  email: 'test@example.com',
  overall_score: 80,
  max_score: 100,
  overall_percentage: 80,
  overall_risk_level: 'healthy',
  category_scores: [
    {
      category: 'registration',
      score: 10,
      max_score: 10,
      percentage: 100,
      risk_level: 'healthy',
      issues: [],
      recommendations: ['Keep up the good work'],
    },
  ],
  priority_actions: ['Action 1', 'Action 2'],
};

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.fetchQuestions).mockResolvedValue(mockQuestions);
    vi.mocked(api.startAssessment).mockResolvedValue({
      id: 'lead-123',
      company_name: 'Test Company',
      contact_name: '',
      email: 'test@example.com',
      company_size: '10-50',
      status: 'started',
      submission_date: '2024-01-01T00:00:00Z',
      consent: true,
    });
    vi.mocked(api.submitAssessment).mockResolvedValue(mockAssessmentResult);
  });

  describe('Intro Screen', () => {
    it('renders intro screen with start button', () => {
      render(<App />);
      
      expect(screen.getByText('Startup Compliance Health Check')).toBeInTheDocument();
      expect(screen.getByText(/Evaluate your HR & labour compliance/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /start assessment/i })).toBeInTheDocument();
    });

    it('shows key features on intro screen', () => {
      render(<App />);
      
      expect(screen.getByText('Comprehensive Assessment')).toBeInTheDocument();
      expect(screen.getByText('Instant Results')).toBeInTheDocument();
      expect(screen.getByText('Actionable Insights')).toBeInTheDocument();
    });

    it('navigates to contact form when start button is clicked', () => {
      render(<App />);
      
      const startButton = screen.getByRole('button', { name: /start assessment/i });
      fireEvent.click(startButton);
      
      expect(screen.getByText('Start Your Compliance Assessment')).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    });
  });

  describe('Contact Form', () => {
    beforeEach(() => {
      render(<App />);
      const startButton = screen.getByRole('button', { name: /start assessment/i });
      fireEvent.click(startButton);
    });

    it('renders all required form fields', () => {
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/company name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/employee range/i)).toBeInTheDocument();
      expect(screen.getByText(/operating states/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/consent/i)).toBeInTheDocument();
    });

    it('allows user to fill out contact form', () => {
      const emailInput = screen.getByLabelText(/email/i);
      const companyInput = screen.getByLabelText(/company name/i);
      
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(companyInput, { target: { value: 'Test Company' } });
      
      expect(emailInput).toHaveValue('test@example.com');
      expect(companyInput).toHaveValue('Test Company');
    });

    it('allows selecting operating states', () => {
      const nswCheckbox = screen.getByRole('checkbox', { name: /new south wales/i });
      
      fireEvent.click(nswCheckbox);
      
      expect(nswCheckbox).toBeChecked();
    });

    it('requires consent checkbox to be checked', () => {
      const consentCheckbox = screen.getByLabelText(/consent/i);
      
      expect(consentCheckbox).not.toBeChecked();
      
      fireEvent.click(consentCheckbox);
      
      expect(consentCheckbox).toBeChecked();
    });

    it('navigates back to intro when back button is clicked', () => {
      const backButton = screen.getByRole('button', { name: /back/i });
      fireEvent.click(backButton);
      
      expect(screen.getByText('Startup Compliance Health Check')).toBeInTheDocument();
    });
  });

  describe('Assessment Flow', () => {
    beforeEach(async () => {
      render(<App />);
      
      fireEvent.click(screen.getByRole('button', { name: /start assessment/i }));
      
      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });
      
      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'Test Company' } });
      
      const selectTrigger = screen.getByRole('combobox', { name: /employee range/i });
      fireEvent.click(selectTrigger);
      
      await waitFor(() => {
        const option = screen.getByRole('option', { name: /11-50 employees/i });
        fireEvent.click(option);
      });
      
      const nswCheckbox = screen.getByRole('checkbox', { name: /new south wales/i });
      fireEvent.click(nswCheckbox);
      
      const consentCheckbox = screen.getByLabelText(/consent/i);
      fireEvent.click(consentCheckbox);
      
      const submitButton = screen.getByRole('button', { name: /start assessment/i });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(api.startAssessment).toHaveBeenCalled();
      });
    });

    it('displays questions after contact form submission', async () => {
      await waitFor(() => {
        expect(screen.getByText('Test Question 1')).toBeInTheDocument();
      });
    });

    it('shows progress indicator', async () => {
      await waitFor(() => {
        expect(screen.getByText(/question 1 of 2/i)).toBeInTheDocument();
        expect(screen.getByText(/50% complete/i)).toBeInTheDocument();
      });
    });

    it('allows selecting an answer', async () => {
      await waitFor(() => {
        expect(screen.getByText('Test Question 1')).toBeInTheDocument();
      });
      
      const option1 = screen.getByLabelText('Option 1');
      fireEvent.click(option1);
      
      expect(option1).toBeChecked();
    });
  });

  describe('Error Handling', () => {
    it('displays error when questions fail to load', async () => {
      vi.mocked(api.fetchQuestions).mockRejectedValue(new Error('Failed to load'));
      
      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load questions/i)).toBeInTheDocument();
      });
    });

    it('displays error when assessment submission fails', async () => {
      vi.mocked(api.submitAssessment).mockRejectedValue(new Error('Submission failed'));
      
      render(<App />);
      
      fireEvent.click(screen.getByRole('button', { name: /start assessment/i }));
      
      await waitFor(() => {
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      });
      
      fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
      fireEvent.change(screen.getByLabelText(/company name/i), { target: { value: 'Test Company' } });
    });
  });
});
