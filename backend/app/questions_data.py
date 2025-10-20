from app.models import Question, QuestionOption, QuestionType, ComplianceCategory, RiskLevel

QUESTIONS = [
    Question(
        id="q1",
        category=ComplianceCategory.EMPLOYEE_DOCS,
        question_text="Do all your employees have written employment contracts?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q1_yes", text="Yes, all employees", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q1_partial", text="Some employees", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q1_no", text="No written contracts", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Written employment contracts are essential for legal protection and clarity.",
        weight=1
    ),
    Question(
        id="q2",
        category=ComplianceCategory.EMPLOYEE_DOCS,
        question_text="Do your employment contracts include all mandatory clauses (job description, compensation, working hours, leave entitlements)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q2_yes", text="Yes, all clauses included", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q2_partial", text="Some clauses missing", score=5, risk_level=RiskLevel.HIGH_RISK),
            QuestionOption(id="q2_no", text="No, many clauses missing", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Employment contracts must include specific mandatory clauses to be legally compliant.",
        weight=1
    ),
    Question(
        id="q3",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have a documented workplace health and safety policy?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q3_yes", text="Yes, documented and communicated", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q3_partial", text="Partially documented", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q3_no", text="No policy", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="A documented WHS policy is required by law for most businesses.",
        weight=1
    ),
    Question(
        id="q4",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you conduct regular workplace safety inspections and risk assessments?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q4_yes", text="Yes, regularly (quarterly or more)", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q4_partial", text="Occasionally (annually)", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q4_no", text="No regular inspections", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Regular safety inspections help identify and mitigate workplace hazards.",
        weight=1
    ),
    Question(
        id="q5",
        category=ComplianceCategory.PAYROLL_STATUTORY,
        question_text="Are you registered for PAYG withholding and remitting tax correctly?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q5_yes", text="Yes, fully compliant", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q5_partial", text="Registered but unsure of compliance", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q5_no", text="Not registered or not withholding", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="PAYG withholding is mandatory for employers. Non-compliance can result in significant penalties.",
        weight=1
    ),
    Question(
        id="q6",
        category=ComplianceCategory.PAYROLL_STATUTORY,
        question_text="Do you provide employees with payment summaries and comply with Single Touch Payroll (STP)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q6_yes", text="Yes, using STP", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q6_partial", text="Provide summaries but not using STP", score=3, risk_level=RiskLevel.HIGH_RISK),
            QuestionOption(id="q6_no", text="No payment summaries", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="STP is mandatory for most employers to report payroll information to the ATO.",
        weight=1
    ),
    Question(
        id="q7",
        category=ComplianceCategory.PAYROLL_STATUTORY,
        question_text="Are you making superannuation contributions for all eligible employees?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q7_yes", text="Yes, all eligible employees", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q7_partial", text="Some employees", score=3, risk_level=RiskLevel.HIGH_RISK),
            QuestionOption(id="q7_no", text="No contributions", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Superannuation contributions are mandatory for eligible employees. Non-compliance results in penalties.",
        weight=1
    ),
    Question(
        id="q8",
        category=ComplianceCategory.EMPLOYEE_DOCS,
        question_text="Do you provide all mandatory leave entitlements (annual leave, sick leave, parental leave)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q8_yes", text="Yes, all entitlements", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q8_partial", text="Some entitlements", score=5, risk_level=RiskLevel.HIGH_RISK),
            QuestionOption(id="q8_no", text="No formal leave policy", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Leave entitlements are mandated by the National Employment Standards (NES).",
        weight=1
    ),
    Question(
        id="q9",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have anti-discrimination and harassment policies in place?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q9_yes", text="Yes, documented and communicated", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q9_partial", text="Partially documented", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q9_no", text="No policies", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Anti-discrimination and harassment policies are essential for legal compliance and workplace culture.",
        weight=1
    ),
    Question(
        id="q10",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have a documented code of conduct for employees?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q10_yes", text="Yes, documented and communicated", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q10_partial", text="Informal guidelines only", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q10_no", text="No code of conduct", score=0, risk_level=RiskLevel.MODERATE),
        ],
        help_text="A code of conduct sets expectations and helps prevent workplace issues.",
        weight=1
    ),
    Question(
        id="q11",
        category=ComplianceCategory.GOVERNANCE,
        question_text="Do you maintain proper employee records (personal details, employment terms, pay records)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q11_yes", text="Yes, comprehensive records", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q11_partial", text="Some records maintained", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q11_no", text="Minimal or no records", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Employers must keep employee records for at least 7 years.",
        weight=1
    ),
    Question(
        id="q12",
        category=ComplianceCategory.GOVERNANCE,
        question_text="Do you keep records of working hours, overtime, and leave taken?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q12_yes", text="Yes, detailed records", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q12_partial", text="Basic records only", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q12_no", text="No time records", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Time and attendance records are required to demonstrate compliance with employment laws.",
        weight=1
    ),
    Question(
        id="q13",
        category=ComplianceCategory.LABOUR_FILINGS,
        question_text="Do you have documented termination and redundancy procedures?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q13_yes", text="Yes, documented procedures", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q13_partial", text="Informal procedures", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q13_no", text="No procedures", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Proper termination procedures help avoid unfair dismissal claims.",
        weight=1
    ),
    Question(
        id="q14",
        category=ComplianceCategory.LABOUR_FILINGS,
        question_text="Do you provide proper notice periods and final pay entitlements when terminating employment?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q14_yes", text="Yes, always", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q14_partial", text="Usually", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q14_no", text="Not consistently", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Failure to provide proper notice and final entitlements can result in legal claims.",
        weight=1
    ),
    Question(
        id="q15",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have a privacy policy for handling employee personal information?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q15_yes", text="Yes, documented policy", score=10, risk_level=RiskLevel.HEALTHY),
            QuestionOption(id="q15_partial", text="Informal practices", score=5, risk_level=RiskLevel.MODERATE),
            QuestionOption(id="q15_no", text="No privacy policy", score=0, risk_level=RiskLevel.HIGH_RISK),
        ],
        help_text="Privacy laws require proper handling and protection of employee personal information.",
        weight=1
    ),
]


def get_all_questions():
    return QUESTIONS


def get_question_by_id(question_id: str):
    for question in QUESTIONS:
        if question.id == question_id:
            return question
    return None


def get_questions_by_category(category: ComplianceCategory):
    return [q for q in QUESTIONS if q.category == category]
