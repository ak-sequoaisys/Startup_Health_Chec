import { useState, useEffect } from "react";
import { Question, Answer, AssessmentResult, Lead } from "./types";
import { fetchQuestions, submitAssessment, startAssessment } from "./api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CheckCircle2, AlertTriangle, XCircle, Info } from "lucide-react";

type Step = "intro" | "contact" | "assessment" | "results";

interface ContactInfo {
  email: string;
  company_name: string;
  industry: string;
  employee_range: string;
  operating_states: string[];
  business_age: string;
  consent: boolean;
}

function App() {
  const [step, setStep] = useState<Step>("intro");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [contactInfo, setContactInfo] = useState<ContactInfo>({
    email: "",
    company_name: "",
    industry: "",
    employee_range: "",
    operating_states: [],
    business_age: "",
    consent: false,
  });
  const [leadId, setLeadId] = useState<string | null>(null);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const data = await fetchQuestions();
      setQuestions(data);
    } catch (err) {
      setError("Failed to load questions. Please refresh the page.");
    }
  };

  const handleStartAssessment = () => {
    setStep("contact");
  };

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (
      contactInfo.email &&
      contactInfo.company_name &&
      contactInfo.employee_range &&
      contactInfo.operating_states.length > 0 &&
      contactInfo.consent
    ) {
      setLoading(true);
      setError(null);
      try {
        const lead = await startAssessment(contactInfo);
        setLeadId(lead.id);
        setStep("assessment");
      } catch (err) {
        setError("Failed to start assessment. Please try again.");
      } finally {
        setLoading(false);
      }
    }
  };

  const handleAnswerSelect = (questionId: string, optionId: string, score: number) => {
    const existingAnswerIndex = answers.findIndex((a) => a.question_id === questionId);
    const newAnswer: Answer = {
      question_id: questionId,
      answer_value: optionId,
      score: score,
    };

    if (existingAnswerIndex >= 0) {
      const newAnswers = [...answers];
      newAnswers[existingAnswerIndex] = newAnswer;
      setAnswers(newAnswers);
    } else {
      setAnswers([...answers, newAnswer]);
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const submission = {
        ...contactInfo,
        answers: answers,
      };
      const assessmentResult = await submitAssessment(submission);
      setResult(assessmentResult);
      setStep("results");
    } catch (err) {
      setError("Failed to submit assessment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const currentAnswer = answers.find((a) => a.question_id === currentQuestion?.id);
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-success";
      case "medium":
        return "bg-warning";
      case "high":
        return "bg-danger";
      case "critical":
        return "bg-destructive";
      default:
        return "bg-muted";
    }
  };

  const getRiskLevelIcon = (level: string) => {
    switch (level) {
      case "low":
        return <CheckCircle2 className="w-6 h-6 text-success" />;
      case "medium":
        return <Info className="w-6 h-6 text-warning" />;
      case "high":
        return <AlertTriangle className="w-6 h-6 text-danger" />;
      case "critical":
        return <XCircle className="w-6 h-6 text-destructive" />;
      default:
        return null;
    }
  };

  const formatCategoryName = (category: string) => {
    return category
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  if (step === "intro") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl font-bold text-foreground">
              Startup Compliance Health Check
            </CardTitle>
            <CardDescription className="text-lg mt-4">
              Evaluate your HR & labour compliance in just 15 minutes
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-success mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold">Comprehensive Assessment</h3>
                  <p className="text-sm text-muted-foreground">
                    15 questions covering all key compliance areas
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-success mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold">Instant Results</h3>
                  <p className="text-sm text-muted-foreground">
                    Get your compliance score and personalized recommendations
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-success mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold">Actionable Insights</h3>
                  <p className="text-sm text-muted-foreground">
                    Identify priority areas and get expert guidance
                  </p>
                </div>
              </div>
            </div>
            <Button
              onClick={handleStartAssessment}
              className="w-full bg-primary hover:bg-primary-700 text-primary-foreground"
              size="lg"
            >
              Start Assessment
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (step === "contact") {
    const australianStates = [
      { value: "NSW", label: "New South Wales" },
      { value: "VIC", label: "Victoria" },
      { value: "QLD", label: "Queensland" },
      { value: "WA", label: "Western Australia" },
      { value: "SA", label: "South Australia" },
      { value: "TAS", label: "Tasmania" },
      { value: "ACT", label: "Australian Capital Territory" },
      { value: "NT", label: "Northern Territory" },
    ];

    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full">
          <CardHeader>
            <CardTitle className="text-2xl">Start Your Compliance Assessment</CardTitle>
            <CardDescription>
              Tell us about your business to begin
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleContactSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={contactInfo.email}
                  onChange={(e) =>
                    setContactInfo({ ...contactInfo, email: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="company_name">Company Name *</Label>
                <Input
                  id="company_name"
                  value={contactInfo.company_name}
                  onChange={(e) =>
                    setContactInfo({ ...contactInfo, company_name: e.target.value })
                  }
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="industry">Industry</Label>
                <Input
                  id="industry"
                  value={contactInfo.industry}
                  onChange={(e) =>
                    setContactInfo({ ...contactInfo, industry: e.target.value })
                  }
                  placeholder="e.g., Technology, Healthcare, Retail"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="employee_range">Employee Range *</Label>
                <Select
                  value={contactInfo.employee_range}
                  onValueChange={(value) =>
                    setContactInfo({ ...contactInfo, employee_range: value })
                  }
                  required
                >
                  <SelectTrigger id="employee_range">
                    <SelectValue placeholder="Select employee range" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1-10">1-10 employees</SelectItem>
                    <SelectItem value="11-50">11-50 employees</SelectItem>
                    <SelectItem value="51-200">51-200 employees</SelectItem>
                    <SelectItem value="201+">201+ employees</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Operating States *</Label>
                <div className="grid grid-cols-2 gap-3">
                  {australianStates.map((state) => (
                    <div key={state.value} className="flex items-center space-x-2">
                      <Checkbox
                        id={state.value}
                        checked={contactInfo.operating_states.includes(state.value)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setContactInfo({
                              ...contactInfo,
                              operating_states: [...contactInfo.operating_states, state.value],
                            });
                          } else {
                            setContactInfo({
                              ...contactInfo,
                              operating_states: contactInfo.operating_states.filter(
                                (s) => s !== state.value
                              ),
                            });
                          }
                        }}
                      />
                      <Label htmlFor={state.value} className="font-normal cursor-pointer">
                        {state.label}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="business_age">Business Age</Label>
                <Select
                  value={contactInfo.business_age}
                  onValueChange={(value) =>
                    setContactInfo({ ...contactInfo, business_age: value })
                  }
                >
                  <SelectTrigger id="business_age">
                    <SelectValue placeholder="Select business age" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0-1">Less than 1 year</SelectItem>
                    <SelectItem value="1-3">1-3 years</SelectItem>
                    <SelectItem value="3-5">3-5 years</SelectItem>
                    <SelectItem value="5+">5+ years</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-start space-x-2 pt-2">
                <Checkbox
                  id="consent"
                  checked={contactInfo.consent}
                  onCheckedChange={(checked) =>
                    setContactInfo({ ...contactInfo, consent: checked === true })
                  }
                  required
                />
                <Label htmlFor="consent" className="font-normal text-sm cursor-pointer">
                  I consent to receiving information about compliance services and agree to the
                  collection of my information for assessment purposes. *
                </Label>
              </div>
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="flex gap-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep("intro")}
                  className="flex-1"
                  disabled={loading}
                >
                  Back
                </Button>
                <Button 
                  type="submit" 
                  className="flex-1 bg-primary hover:bg-primary-700 text-primary-foreground"
                  disabled={loading}
                >
                  {loading ? "Starting..." : "Start Assessment"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (step === "assessment" && currentQuestion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-foreground">
                Question {currentQuestionIndex + 1} of {questions.length}
              </span>
              <span className="text-sm font-medium text-foreground">
                {Math.round(progress)}% Complete
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          <Card>
            <CardHeader>
              <Badge className="w-fit mb-2">
                {formatCategoryName(currentQuestion.category)}
              </Badge>
              <CardTitle className="text-xl">{currentQuestion.question_text}</CardTitle>
              {currentQuestion.help_text && (
                <CardDescription className="text-base mt-2">
                  {currentQuestion.help_text}
                </CardDescription>
              )}
              {currentQuestion.government_sources && currentQuestion.government_sources.length > 0 && (
                <div className="mt-4 p-3 bg-accent rounded-lg">
                  <h4 className="text-sm font-semibold mb-2">Government Sources:</h4>
                  <div className="space-y-1">
                    {currentQuestion.government_sources.map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary hover:underline flex items-center gap-1"
                      >
                        <span>{source.name}</span>
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              <RadioGroup
                value={currentAnswer?.answer_value || ""}
                onValueChange={(value) => {
                  const option = currentQuestion.options?.find((o) => o.id === value);
                  if (option) {
                    handleAnswerSelect(currentQuestion.id, value, option.score);
                  }
                }}
              >
                {currentQuestion.options?.map((option) => (
                  <div
                    key={option.id}
                    className="flex items-center space-x-3 border rounded-lg p-4 hover:bg-accent cursor-pointer"
                  >
                    <RadioGroupItem value={option.id} id={option.id} />
                    <Label
                      htmlFor={option.id}
                      className="flex-1 cursor-pointer font-normal"
                    >
                      {option.text}
                    </Label>
                    <Badge
                      variant="outline"
                      className={`${getRiskLevelColor(option.risk_level)} text-white border-0`}
                    >
                      {option.risk_level}
                    </Badge>
                  </div>
                ))}
              </RadioGroup>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={currentQuestionIndex === 0}
                  className="flex-1"
                >
                  Previous
                </Button>
                <Button
                  onClick={handleNext}
                  disabled={!currentAnswer || loading}
                  className="flex-1 bg-primary hover:bg-primary-700 text-primary-foreground"
                >
                  {currentQuestionIndex === questions.length - 1
                    ? loading
                      ? "Submitting..."
                      : "Submit Assessment"
                    : "Next"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (step === "results" && result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-bold">
                Your Compliance Health Check Results
              </CardTitle>
              <CardDescription className="text-lg mt-2">
                {result.company_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-center gap-4 p-6 bg-gradient-to-r from-primary-50 to-accent rounded-lg">
                <div className="text-center">
                  <div className="text-5xl font-bold text-primary">
                    {Math.round(result.overall_percentage)}%
                  </div>
                  <div className="text-sm text-muted-foreground mt-2">Overall Score</div>
                </div>
                <div className="flex items-center gap-2">
                  {getRiskLevelIcon(result.overall_risk_level)}
                  <Badge
                    className={`${getRiskLevelColor(result.overall_risk_level)} text-white text-lg px-4 py-2`}
                  >
                    {result.overall_risk_level.toUpperCase()}
                  </Badge>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-xl font-semibold mb-4">Priority Actions</h3>
                <div className="space-y-3">
                  {result.priority_actions.map((action, index) => (
                    <Alert key={index}>
                      <AlertDescription className="flex items-start gap-2">
                        <span className="font-semibold text-primary">
                          {index + 1}.
                        </span>
                        <span>{action}</span>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="text-xl font-semibold mb-4">Category Breakdown</h3>
                <div className="space-y-4">
                  {result.category_scores.map((category) => (
                    <Card key={category.category}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">
                            {formatCategoryName(category.category)}
                          </CardTitle>
                          <div className="flex items-center gap-2">
                            <span className="text-2xl font-bold">
                              {Math.round(category.percentage)}%
                            </span>
                            <Badge
                              className={`${getRiskLevelColor(category.risk_level)} text-white`}
                            >
                              {category.risk_level}
                            </Badge>
                          </div>
                        </div>
                        <Progress value={category.percentage} className="h-2 mt-2" />
                      </CardHeader>
                      <CardContent className="space-y-3">
                        {category.issues.length > 0 && (
                          <div>
                            <h4 className="font-semibold text-sm text-destructive mb-2">
                              Issues Identified:
                            </h4>
                            <ul className="list-disc list-inside space-y-1 text-sm">
                              {category.issues.map((issue, idx) => (
                                <li key={idx} className="text-foreground">
                                  {issue}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {category.recommendations.length > 0 && (
                          <div>
                            <h4 className="font-semibold text-sm text-primary mb-2">
                              Recommendations:
                            </h4>
                            <ul className="list-disc list-inside space-y-1 text-sm">
                              {category.recommendations.map((rec, idx) => (
                                <li key={idx} className="text-foreground">
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              <div className="bg-accent p-6 rounded-lg text-center">
                <h3 className="text-xl font-semibold mb-2">Need Help?</h3>
                <p className="text-foreground mb-4">
                  Our compliance experts can help you address these issues and ensure
                  your business is fully compliant.
                </p>
                <Button className="bg-primary hover:bg-primary-700 text-primary-foreground" size="lg">
                  Schedule a Consultation
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

export default App;
