import { useState, useEffect } from "react";
import { Question, Answer, AssessmentResult } from "./types";
import { fetchQuestions, submitAssessment, startAssessment, generatePDFReport } from "./api";
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
import { CheckCircle2, AlertTriangle, XCircle, Info, Download, Calendar, ExternalLink, Share2 } from "lucide-react";
import { initializeGTM, trackStartAssessment, trackAnswerQuestion, trackViewResults, trackReportDownload } from "./analytics";
import { validateBusinessEmail } from "./emailValidator";

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
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);

  useEffect(() => {
    initializeGTM();
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const data = await fetchQuestions();
      setQuestions(data);
    } catch {
      setError("Failed to load questions. Please refresh the page.");
    }
  };

  const handleStartAssessment = () => {
    setStep("contact");
  };

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const emailValidationError = validateBusinessEmail(contactInfo.email);
    if (emailValidationError) {
      setEmailError(emailValidationError);
      return;
    }
    
    if (
      contactInfo.email &&
      contactInfo.company_name &&
      contactInfo.employee_range &&
      contactInfo.operating_states.length > 0 &&
      contactInfo.consent
    ) {
      setLoading(true);
      setError(null);
      setEmailError(null);
      try {
        await startAssessment(contactInfo);
        trackStartAssessment({
          company_name: contactInfo.company_name,
          industry: contactInfo.industry,
          employee_range: contactInfo.employee_range,
        });
        setStep("assessment");
      } catch (err: any) {
        if (err?.response?.data?.detail && typeof err.response.data.detail === 'string' && err.response.data.detail.includes('email')) {
          setEmailError(err.response.data.detail);
        } else {
          setError("Failed to start assessment. Please try again.");
        }
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

    const question = questions.find((q) => q.id === questionId);
    if (question) {
      trackAnswerQuestion({
        question_id: questionId,
        question_number: currentQuestionIndex + 1,
        category: question.category,
        answer_value: optionId,
        score: score,
      });
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
        company_name: contactInfo.company_name,
        contact_name: contactInfo.company_name,
        email: contactInfo.email,
        company_size: contactInfo.employee_range,
        industry: contactInfo.industry,
        answers: answers,
      };
      const assessmentResult = await submitAssessment(submission);
      setResult(assessmentResult);
      setStep("results");
      window.history.pushState({}, "", `?result=${assessmentResult.id}`);
      
      trackViewResults({
        assessment_id: assessmentResult.id,
        overall_score: assessmentResult.overall_score,
        overall_percentage: assessmentResult.overall_percentage,
        risk_level: assessmentResult.overall_risk_level,
        company_name: assessmentResult.company_name,
      });
    } catch {
      setError("Failed to submit assessment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleShareResult = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
      alert("Result link copied to clipboard!");
    });
  };

  const handleDownloadPDF = async () => {
    if (!result) return;
    
    try {
      setLoading(true);
      const pdfBlob = await generatePDFReport(result.id);
      
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `compliance_report_${result.company_name.replace(/\s+/g, "_")}_${new Date().toISOString().split("T")[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      trackReportDownload({
        assessment_id: result.id,
        company_name: result.company_name,
        overall_percentage: result.overall_percentage,
        risk_level: result.overall_risk_level,
      });
    } catch (err) {
      setError("Failed to generate PDF report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleBookCall = () => {
    window.open("https://outlook.office365.com/book/OffrdDemo@sequoiaat.com/", "_blank");
  };

  const handleExploreOffrd = () => {
    window.open("https://www.offrd.co", "_blank");
  };

  const currentQuestion = questions[currentQuestionIndex];
  const currentAnswer = answers.find((a) => a.question_id === currentQuestion?.id);
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  const getScoreColor = (percentage: number) => {
    if (percentage >= 71) return "text-success";
    if (percentage >= 41) return "text-warning";
    return "text-danger";
  };


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
        <div className="absolute top-4 left-4">
          <a href="https://www.offrd.co" target="_blank" rel="noopener noreferrer">
            <img src="/offrd-logo.png" alt="Offrd" className="h-12 w-auto" />
          </a>
        </div>
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
    const indianStates = [
      { value: "AN", label: "Andaman and Nicobar Islands" },
      { value: "AP", label: "Andhra Pradesh" },
      { value: "AR", label: "Arunachal Pradesh" },
      { value: "AS", label: "Assam" },
      { value: "BR", label: "Bihar" },
      { value: "CH", label: "Chandigarh" },
      { value: "CT", label: "Chhattisgarh" },
      { value: "DN", label: "Dadra and Nagar Haveli and Daman and Diu" },
      { value: "DL", label: "Delhi" },
      { value: "GA", label: "Goa" },
      { value: "GJ", label: "Gujarat" },
      { value: "HR", label: "Haryana" },
      { value: "HP", label: "Himachal Pradesh" },
      { value: "JK", label: "Jammu and Kashmir" },
      { value: "JH", label: "Jharkhand" },
      { value: "KA", label: "Karnataka" },
      { value: "KL", label: "Kerala" },
      { value: "LA", label: "Ladakh" },
      { value: "LD", label: "Lakshadweep" },
      { value: "MP", label: "Madhya Pradesh" },
      { value: "MH", label: "Maharashtra" },
      { value: "MN", label: "Manipur" },
      { value: "ML", label: "Meghalaya" },
      { value: "MZ", label: "Mizoram" },
      { value: "NL", label: "Nagaland" },
      { value: "OR", label: "Odisha" },
      { value: "PY", label: "Puducherry" },
      { value: "PB", label: "Punjab" },
      { value: "RJ", label: "Rajasthan" },
      { value: "SK", label: "Sikkim" },
      { value: "TN", label: "Tamil Nadu" },
      { value: "TG", label: "Telangana" },
      { value: "TR", label: "Tripura" },
      { value: "UP", label: "Uttar Pradesh" },
      { value: "UT", label: "Uttarakhand" },
      { value: "WB", label: "West Bengal" },
    ];

    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <div className="absolute top-4 left-4">
          <a href="https://www.offrd.co" target="_blank" rel="noopener noreferrer">
            <img src="/offrd-logo.png" alt="Offrd" className="h-12 w-auto" />
          </a>
        </div>
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
                  onChange={(e) => {
                    setContactInfo({ ...contactInfo, email: e.target.value });
                    setEmailError(null);
                  }}
                  required
                  className={emailError ? "border-destructive" : ""}
                />
                {emailError && (
                  <p className="text-sm text-destructive">{emailError}</p>
                )}
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
                  {indianStates.map((state) => (
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
        <div className="absolute top-4 left-4">
          <a href="https://www.offrd.co" target="_blank" rel="noopener noreferrer">
            <img src="/offrd-logo.png" alt="Offrd" className="h-12 w-auto" />
          </a>
        </div>
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
    const overallPercentage = Math.round(result.overall_percentage);
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 p-4 py-8">
        <div className="absolute top-4 left-4">
          <a href="https://www.offrd.co" target="_blank" rel="noopener noreferrer">
            <img src="/offrd-logo.png" alt="Offrd" className="h-12 w-auto" />
          </a>
        </div>
        <div className="max-w-5xl mx-auto space-y-6">
          <Card>
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-3xl font-bold">
                Your Compliance Health Check Results
              </CardTitle>
              <CardDescription className="text-lg mt-2">
                {result.company_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="relative p-8 bg-gradient-to-br from-white to-accent rounded-xl border-2 border-primary/10 shadow-lg">
                <div className="flex flex-col md:flex-row items-center justify-center gap-8">
                  <div className="text-center">
                    <div className={`text-7xl font-bold ${getScoreColor(overallPercentage)} drop-shadow-md`}>
                      {overallPercentage}%
                    </div>
                    <div className="text-sm font-medium text-muted-foreground mt-3 uppercase tracking-wide">
                      Overall Compliance Score
                    </div>
                  </div>
                  <div className="flex flex-col items-center gap-3">
                    {getRiskLevelIcon(result.overall_risk_level)}
                    <Badge
                      className={`${getRiskLevelColor(result.overall_risk_level)} text-white text-base px-6 py-2 shadow-md`}
                    >
                      {result.overall_risk_level.toUpperCase()} RISK
                    </Badge>
                  </div>
                </div>
                <div className="mt-6 flex justify-center">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleShareResult}
                    className="gap-2"
                  >
                    <Share2 className="w-4 h-4" />
                    Share Results
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button
                  onClick={handleDownloadPDF}
                  className="bg-primary hover:bg-primary-700 text-primary-foreground h-auto py-4 flex flex-col gap-2"
                  size="lg"
                >
                  <Download className="w-6 h-6" />
                  <span className="font-semibold">Download PDF Report</span>
                </Button>
                <Button
                  onClick={handleBookCall}
                  className="bg-success hover:bg-success/90 text-success-foreground h-auto py-4 flex flex-col gap-2"
                  size="lg"
                >
                  <Calendar className="w-6 h-6" />
                  <span className="font-semibold">Book a Demo</span>
                </Button>
                <Button
                  onClick={handleExploreOffrd}
                  className="bg-secondary hover:bg-secondary/90 text-secondary-foreground h-auto py-4 flex flex-col gap-2"
                  size="lg"
                >
                  <ExternalLink className="w-6 h-6" />
                  <span className="font-semibold">Explore Offrd</span>
                </Button>
              </div>

              <Separator className="my-8" />

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <AlertTriangle className="w-6 h-6 text-danger" />
                  <h3 className="text-2xl font-bold">Top Priority Actions</h3>
                </div>
                <div className="space-y-3">
                  {result.priority_actions.slice(0, 5).map((action, index) => (
                    <Alert key={index} className="border-l-4 border-l-danger bg-danger/5">
                      <AlertDescription className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-7 h-7 rounded-full bg-danger text-white font-bold flex items-center justify-center text-sm">
                          {index + 1}
                        </span>
                        <span className="text-base">{action}</span>
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              </div>

              <Separator className="my-8" />

              <div>
                <h3 className="text-2xl font-bold mb-6">Compliance Category Breakdown</h3>
                <div className="space-y-5">
                  {result.category_scores.map((category) => {
                    const categoryPercentage = Math.round(category.percentage);
                    return (
                      <Card key={category.category} className="overflow-hidden border-2">
                        <CardHeader className="pb-3">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <CardTitle className="text-xl">
                              {formatCategoryName(category.category)}
                            </CardTitle>
                            <div className="flex items-center gap-3">
                              <span className={`text-3xl font-bold ${getScoreColor(categoryPercentage)}`}>
                                {categoryPercentage}%
                              </span>
                              <Badge
                                className={`${getRiskLevelColor(category.risk_level)} text-white px-3 py-1`}
                              >
                                {category.risk_level.toUpperCase()}
                              </Badge>
                            </div>
                          </div>
                          <div className="mt-3">
                            <Progress 
                              value={category.percentage} 
                              className="h-3"
                            />
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4 pt-2">
                          {category.issues.length > 0 && (
                            <div className="bg-destructive/5 p-4 rounded-lg border border-destructive/20">
                              <h4 className="font-bold text-sm text-destructive mb-3 flex items-center gap-2">
                                <XCircle className="w-4 h-4" />
                                Gaps Identified ({category.issues.length})
                              </h4>
                              <ul className="space-y-2">
                                {category.issues.map((issue, idx) => (
                                  <li key={idx} className="flex items-start gap-2 text-sm">
                                    <span className="text-destructive mt-0.5">•</span>
                                    <span className="text-foreground">{issue}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {category.recommendations.length > 0 && (
                            <div className="bg-primary/5 p-4 rounded-lg border border-primary/20">
                              <h4 className="font-bold text-sm text-primary mb-3 flex items-center gap-2">
                                <CheckCircle2 className="w-4 h-4" />
                                Recommended Actions ({category.recommendations.length})
                              </h4>
                              <ul className="space-y-2">
                                {category.recommendations.map((rec, idx) => (
                                  <li key={idx} className="flex items-start gap-2 text-sm">
                                    <span className="text-primary mt-0.5">•</span>
                                    <span className="text-foreground">{rec}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>

              <Separator className="my-8" />

              <div className="bg-gradient-to-br from-primary/10 to-accent p-8 rounded-xl text-center border-2 border-primary/20">
                <h3 className="text-2xl font-bold mb-3">Ready to Achieve Full Compliance?</h3>
                <p className="text-foreground text-lg mb-6 max-w-2xl mx-auto">
                  Our compliance experts at Offrd can help you address these gaps and ensure
                  your business meets all Indian HR and labour compliance requirements.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Button 
                    onClick={handleBookCall}
                    className="bg-primary hover:bg-primary-700 text-primary-foreground gap-2" 
                    size="lg"
                  >
                    <Calendar className="w-5 h-5" />
                    Book a Demo
                  </Button>
                  <Button 
                    onClick={handleExploreOffrd}
                    variant="outline"
                    className="gap-2 bg-white hover:bg-accent" 
                    size="lg"
                  >
                    <ExternalLink className="w-5 h-5" />
                    Learn More About Offrd
                  </Button>
                </div>
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
