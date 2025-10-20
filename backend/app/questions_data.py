from app.models import Question, QuestionOption, QuestionType, ComplianceCategory, RiskLevel, ApplicabilityRule, GovernmentSource

QUESTIONS = [
    Question(
        id="q1",
        category=ComplianceCategory.REGISTRATION,
        question_text="Is your company registered with the Registrar of Companies (ROC)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q1_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q1_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q1_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
        ],
        help_text="Company registration with ROC is mandatory for all companies operating in India.",
        weight=3,
        government_sources=[
            GovernmentSource(
                name="Ministry of Corporate Affairs",
                url="https://www.mca.gov.in/",
                description="Official portal for company registration and compliance"
            )
        ]
    ),
    Question(
        id="q2",
        category=ComplianceCategory.REGISTRATION,
        question_text="Do you have a valid GST registration?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q2_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q2_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q2_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
        ],
        help_text="GST registration is mandatory for businesses with turnover above the threshold limit.",
        weight=3,
        government_sources=[
            GovernmentSource(
                name="GST Portal",
                url="https://www.gst.gov.in/",
                description="Official GST portal for registration and filing"
            )
        ]
    ),
    Question(
        id="q3",
        category=ComplianceCategory.REGISTRATION,
        question_text="Is your company registered for Provident Fund (PF)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q3_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q3_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q3_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q3_not_applicable", text="Not applicable (less than 20 employees)", score=10, risk_level=RiskLevel.LOW),
        ],
        help_text="PF registration is mandatory for establishments with 20 or more employees.",
        weight=3,
        applicability_rules=[
            ApplicabilityRule(rule_type="employee_count", threshold=20)
        ],
        government_sources=[
            GovernmentSource(
                name="EPFO",
                url="https://www.epfindia.gov.in/",
                description="Employees' Provident Fund Organisation"
            )
        ]
    ),
    Question(
        id="q4",
        category=ComplianceCategory.EMPLOYEE_DOCS,
        question_text="Do all your employees have written employment contracts or appointment letters?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q4_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q4_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q4_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
        ],
        help_text="Written employment contracts are essential for legal protection and clarity of terms.",
        weight=2,
        government_sources=[
            GovernmentSource(
                name="Ministry of Labour & Employment",
                url="https://labour.gov.in/",
                description="Official portal for labour laws and regulations"
            )
        ]
    ),
    Question(
        id="q5",
        category=ComplianceCategory.EMPLOYEE_DOCS,
        question_text="Do you maintain proper employee records (personal details, joining date, salary details)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q5_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q5_no", text="No", score=0, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q5_not_sure", text="Not sure", score=3, risk_level=RiskLevel.MEDIUM),
        ],
        help_text="Maintaining proper employee records is mandatory under various labour laws.",
        weight=2,
        government_sources=[
            GovernmentSource(
                name="Ministry of Labour & Employment",
                url="https://labour.gov.in/",
                description="Official portal for labour laws and regulations"
            )
        ]
    ),
    Question(
        id="q6",
        category=ComplianceCategory.PAYROLL_STATUTORY,
        question_text="Are you deducting and depositing TDS on employee salaries?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q6_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q6_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q6_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
        ],
        help_text="TDS deduction on salaries is mandatory as per Income Tax Act.",
        weight=3,
        government_sources=[
            GovernmentSource(
                name="Income Tax Department",
                url="https://www.incometax.gov.in/",
                description="Official portal for income tax compliance"
            )
        ]
    ),
    Question(
        id="q7",
        category=ComplianceCategory.PAYROLL_STATUTORY,
        question_text="Are you making timely PF contributions for eligible employees?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q7_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q7_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q7_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q7_not_applicable", text="Not applicable", score=10, risk_level=RiskLevel.LOW),
        ],
        help_text="PF contributions must be made by 15th of every month for eligible employees.",
        weight=3,
        applicability_rules=[
            ApplicabilityRule(rule_type="pf_applicable")
        ],
        government_sources=[
            GovernmentSource(
                name="EPFO",
                url="https://www.epfindia.gov.in/",
                description="Employees' Provident Fund Organisation"
            )
        ]
    ),
    Question(
        id="q8",
        category=ComplianceCategory.PAYROLL_STATUTORY,
        question_text="Are you registered and compliant with ESI (Employee State Insurance)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q8_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q8_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q8_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q8_not_applicable", text="Not applicable (less than 10 employees)", score=10, risk_level=RiskLevel.LOW),
        ],
        help_text="ESI registration is mandatory for establishments with 10 or more employees earning up to Rs. 21,000 per month.",
        weight=3,
        applicability_rules=[
            ApplicabilityRule(rule_type="esi_applicable", threshold=10)
        ],
        government_sources=[
            GovernmentSource(
                name="ESIC",
                url="https://www.esic.gov.in/",
                description="Employees' State Insurance Corporation"
            )
        ]
    ),
    Question(
        id="q9",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have a documented Prevention of Sexual Harassment (POSH) policy?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q9_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q9_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q9_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q9_not_applicable", text="Not applicable (less than 10 employees)", score=10, risk_level=RiskLevel.LOW),
        ],
        help_text="POSH policy and Internal Complaints Committee (ICC) are mandatory for organizations with 10 or more employees.",
        weight=3,
        applicability_rules=[
            ApplicabilityRule(rule_type="posh_applicable", threshold=10)
        ],
        government_sources=[
            GovernmentSource(
                name="Ministry of Women and Child Development",
                url="https://wcd.nic.in/",
                description="Information on POSH Act and compliance"
            )
        ]
    ),
    Question(
        id="q10",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have documented leave policies (casual, sick, earned leave)?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q10_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q10_no", text="No", score=0, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q10_not_sure", text="Not sure", score=3, risk_level=RiskLevel.MEDIUM),
        ],
        help_text="Clear leave policies help maintain transparency and compliance with labour laws.",
        weight=2,
        government_sources=[
            GovernmentSource(
                name="Ministry of Labour & Employment",
                url="https://labour.gov.in/",
                description="Official portal for labour laws and regulations"
            )
        ]
    ),
    Question(
        id="q11",
        category=ComplianceCategory.WORKPLACE_POLICIES,
        question_text="Do you have a documented code of conduct and disciplinary policy?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q11_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q11_no", text="No", score=0, risk_level=RiskLevel.MEDIUM),
            QuestionOption(id="q11_not_sure", text="Not sure", score=3, risk_level=RiskLevel.MEDIUM),
        ],
        help_text="A code of conduct sets expectations and helps prevent workplace issues.",
        weight=1
    ),
    Question(
        id="q12",
        category=ComplianceCategory.LABOUR_FILINGS,
        question_text="Are you filing monthly/quarterly returns for PF and ESI on time?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q12_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q12_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q12_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q12_not_applicable", text="Not applicable", score=10, risk_level=RiskLevel.LOW),
        ],
        help_text="Timely filing of statutory returns is mandatory to avoid penalties.",
        weight=3,
        government_sources=[
            GovernmentSource(
                name="EPFO",
                url="https://www.epfindia.gov.in/",
                description="Employees' Provident Fund Organisation"
            ),
            GovernmentSource(
                name="ESIC",
                url="https://www.esic.gov.in/",
                description="Employees' State Insurance Corporation"
            )
        ]
    ),
    Question(
        id="q13",
        category=ComplianceCategory.LABOUR_FILINGS,
        question_text="Are you compliant with Professional Tax (PT) registration and payment?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q13_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q13_no", text="No", score=0, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q13_not_sure", text="Not sure", score=3, risk_level=RiskLevel.MEDIUM),
            QuestionOption(id="q13_not_applicable", text="Not applicable (state doesn't levy PT)", score=10, risk_level=RiskLevel.LOW),
        ],
        help_text="Professional Tax is a state-level tax applicable in certain states.",
        weight=2,
        applicability_rules=[
            ApplicabilityRule(rule_type="pt_applicable", states=["Maharashtra", "Karnataka", "West Bengal", "Tamil Nadu", "Gujarat", "Andhra Pradesh", "Telangana", "Madhya Pradesh", "Assam", "Meghalaya", "Tripura"])
        ]
    ),
    Question(
        id="q14",
        category=ComplianceCategory.GOVERNANCE,
        question_text="Do you conduct regular board meetings and maintain proper minutes?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q14_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q14_no", text="No", score=0, risk_level=RiskLevel.HIGH),
            QuestionOption(id="q14_not_sure", text="Not sure", score=3, risk_level=RiskLevel.MEDIUM),
        ],
        help_text="Regular board meetings are required under the Companies Act for proper governance.",
        weight=2,
        government_sources=[
            GovernmentSource(
                name="Ministry of Corporate Affairs",
                url="https://www.mca.gov.in/",
                description="Official portal for company registration and compliance"
            )
        ]
    ),
    Question(
        id="q15",
        category=ComplianceCategory.GOVERNANCE,
        question_text="Are you filing annual returns (Form AOC-4, MGT-7) with ROC on time?",
        question_type=QuestionType.YES_NO,
        options=[
            QuestionOption(id="q15_yes", text="Yes", score=10, risk_level=RiskLevel.LOW),
            QuestionOption(id="q15_no", text="No", score=0, risk_level=RiskLevel.CRITICAL),
            QuestionOption(id="q15_not_sure", text="Not sure", score=3, risk_level=RiskLevel.HIGH),
        ],
        help_text="Annual filing with ROC is mandatory for all registered companies.",
        weight=3,
        government_sources=[
            GovernmentSource(
                name="Ministry of Corporate Affairs",
                url="https://www.mca.gov.in/",
                description="Official portal for company registration and compliance"
            )
        ]
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
