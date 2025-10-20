from weasyprint import HTML, CSS
from typing import Optional
import os
from datetime import datetime
from app.models import AssessmentResult, RiskLevel, ComplianceCategory


CATEGORY_DISPLAY_NAMES = {
    ComplianceCategory.REGISTRATION: "Business Registration & Licenses",
    ComplianceCategory.EMPLOYEE_DOCS: "Employee Documentation",
    ComplianceCategory.PAYROLL_STATUTORY: "Payroll & Statutory Compliance",
    ComplianceCategory.WORKPLACE_POLICIES: "Workplace Policies",
    ComplianceCategory.LABOUR_FILINGS: "Labour Law Filings",
    ComplianceCategory.GOVERNANCE: "Corporate Governance",
}


RISK_LEVEL_COLORS = {
    RiskLevel.HEALTHY: "#10b981",
    RiskLevel.MODERATE: "#f59e0b",
    RiskLevel.HIGH_RISK: "#ef4444",
}


RISK_LEVEL_DISPLAY = {
    RiskLevel.HEALTHY: "Healthy",
    RiskLevel.MODERATE: "Moderate Risk",
    RiskLevel.HIGH_RISK: "High Risk",
}


STATE_ANNEXURE = """
<div class="annexure-section">
    <h2>State-Specific Compliance References</h2>
    
    <h3>All States - Central Government Compliance</h3>
    <ul>
        <li><strong>Employees' Provident Fund (EPF)</strong>: Applicable to establishments with 20+ employees. 
            <a href="https://www.epfindia.gov.in/">EPFO Official Website</a></li>
        <li><strong>Employees' State Insurance (ESI)</strong>: Applicable to establishments with 10+ employees earning up to ₹21,000/month. 
            <a href="https://www.esic.gov.in/">ESIC Official Website</a></li>
        <li><strong>Income Tax (TDS)</strong>: Mandatory for all employers. 
            <a href="https://www.incometax.gov.in/">Income Tax Department</a></li>
        <li><strong>Goods and Services Tax (GST)</strong>: Registration required if turnover exceeds ₹40 lakhs (₹20 lakhs for special category states). 
            <a href="https://www.gst.gov.in/">GST Portal</a></li>
        <li><strong>Prevention of Sexual Harassment (POSH)</strong>: Mandatory for all organizations with 10+ employees. 
            <a href="https://wcd.nic.in/">Ministry of Women and Child Development</a></li>
    </ul>
    
    <h3>State-Specific Compliance</h3>
    
    <h4>Karnataka</h4>
    <ul>
        <li><strong>Karnataka Shops and Commercial Establishments Act</strong>: Registration required within 30 days of commencement. 
            <a href="https://labour.karnataka.gov.in/">Karnataka Labour Department</a></li>
        <li><strong>Professional Tax</strong>: Applicable to all employees and employers. Maximum ₹2,500/year. 
            <a href="https://karnatakaone.gov.in/">Karnataka One Portal</a></li>
    </ul>
    
    <h4>Maharashtra</h4>
    <ul>
        <li><strong>Maharashtra Shops and Establishments Act</strong>: Registration required within 30 days. 
            <a href="https://mahakamgar.maharashtra.gov.in/">Maharashtra Labour Department</a></li>
        <li><strong>Professional Tax</strong>: Applicable to all employees and employers. Maximum ₹2,500/year. 
            <a href="https://mahavat.gov.in/">MahaVAT Portal</a></li>
    </ul>
    
    <h4>Tamil Nadu</h4>
    <ul>
        <li><strong>Tamil Nadu Shops and Establishments Act</strong>: Registration required within 30 days. 
            <a href="https://www.tn.gov.in/labour">Tamil Nadu Labour Department</a></li>
        <li><strong>Professional Tax</strong>: Applicable to all employees and employers. Maximum ₹2,500/year. 
            <a href="https://www.tnprofessionaltax.com/">TN Professional Tax</a></li>
    </ul>
    
    <h4>Delhi</h4>
    <ul>
        <li><strong>Delhi Shops and Establishments Act</strong>: Registration required within 30 days. 
            <a href="https://labour.delhi.gov.in/">Delhi Labour Department</a></li>
        <li><strong>No Professional Tax</strong>: Delhi does not levy professional tax.</li>
    </ul>
    
    <h4>Gujarat</h4>
    <ul>
        <li><strong>Gujarat Shops and Establishments Act</strong>: Registration required within 30 days. 
            <a href="https://labour.gujarat.gov.in/">Gujarat Labour Department</a></li>
        <li><strong>Professional Tax</strong>: Applicable to all employees and employers. Maximum ₹2,500/year. 
            <a href="https://www.ptax.gujarat.gov.in/">Gujarat Professional Tax</a></li>
    </ul>
    
    <h4>West Bengal</h4>
    <ul>
        <li><strong>West Bengal Shops and Establishments Act</strong>: Registration required within 60 days. 
            <a href="https://wblabour.gov.in/">West Bengal Labour Department</a></li>
        <li><strong>Professional Tax</strong>: Applicable to all employees and employers. Maximum ₹2,500/year. 
            <a href="https://wbcomtax.gov.in/">WB Commercial Tax</a></li>
    </ul>
</div>
"""


DISCLAIMER = """
<div class="disclaimer-section">
    <h2>Important Disclaimer</h2>
    <p><strong>This compliance health check report is provided for informational purposes only and does not constitute legal advice.</strong></p>
    
    <p>The assessment and recommendations contained in this report are based on the information you provided and general compliance requirements 
    applicable to startups in India. Compliance requirements may vary based on:</p>
    <ul>
        <li>Your specific business structure and operations</li>
        <li>The states in which you operate</li>
        <li>Your industry sector</li>
        <li>The number and classification of your employees</li>
        <li>Your annual turnover and revenue</li>
        <li>Recent changes in legislation</li>
    </ul>
    
    <p><strong>We strongly recommend that you:</strong></p>
    <ul>
        <li>Consult with qualified legal and compliance professionals to understand your specific obligations</li>
        <li>Verify all compliance requirements with the relevant government authorities</li>
        <li>Conduct regular compliance audits to ensure ongoing adherence to all applicable laws</li>
        <li>Stay updated on changes to labor laws, tax regulations, and other compliance requirements</li>
    </ul>
    
    <p>This report is generated as of <strong>{report_date}</strong> and may not reflect recent legislative changes or updates to compliance requirements.</p>
    
    <p><strong>Limitation of Liability:</strong> The creators and providers of this compliance health check tool shall not be held liable for any 
    actions taken or not taken based on the information provided in this report. Users are solely responsible for ensuring their compliance with 
    all applicable laws and regulations.</p>
    
    <p>For personalized compliance guidance and support, please contact our team of experts.</p>
</div>
"""


def generate_html_report(result: AssessmentResult) -> str:
    risk_color = RISK_LEVEL_COLORS.get(result.overall_risk_level, "#6b7280")
    risk_display = RISK_LEVEL_DISPLAY.get(result.overall_risk_level, result.overall_risk_level.value)
    
    category_rows = ""
    for cat_score in result.category_scores:
        cat_name = CATEGORY_DISPLAY_NAMES.get(cat_score.category, cat_score.category.value)
        cat_risk_color = RISK_LEVEL_COLORS.get(cat_score.risk_level, "#6b7280")
        cat_risk_display = RISK_LEVEL_DISPLAY.get(cat_score.risk_level, cat_score.risk_level.value)
        
        issues_html = ""
        if cat_score.issues:
            issues_html = "<ul class='issues-list'>"
            for issue in cat_score.issues:
                issues_html += f"<li>{issue}</li>"
            issues_html += "</ul>"
        else:
            issues_html = "<p class='no-issues'>No significant issues identified</p>"
        
        recommendations_html = ""
        if cat_score.recommendations:
            recommendations_html = "<ul class='recommendations-list'>"
            for rec in cat_score.recommendations:
                recommendations_html += f"<li>{rec}</li>"
            recommendations_html += "</ul>"
        
        category_rows += f"""
        <div class="category-section">
            <div class="category-header">
                <h3>{cat_name}</h3>
                <div class="category-score">
                    <span class="score-value">{cat_score.percentage:.1f}%</span>
                    <span class="risk-badge" style="background-color: {cat_risk_color};">{cat_risk_display}</span>
                </div>
            </div>
            <div class="category-details">
                <div class="score-breakdown">
                    <span>Score: {cat_score.score} / {cat_score.max_score}</span>
                </div>
                {f'<div class="issues"><h4>Issues Identified:</h4>{issues_html}</div>' if cat_score.issues else ''}
                {f'<div class="recommendations"><h4>Recommendations:</h4>{recommendations_html}</div>' if cat_score.recommendations else ''}
            </div>
        </div>
        """
    
    priority_actions_html = ""
    if result.priority_actions:
        priority_actions_html = "<ol class='priority-actions-list'>"
        for action in result.priority_actions:
            priority_actions_html += f"<li>{action}</li>"
        priority_actions_html += "</ol>"
    
    disclaimer_with_date = DISCLAIMER.format(report_date=datetime.now().strftime("%B %d, %Y"))
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Compliance Health Check Report - {result.company_name}</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                line-height: 1.6;
                color: #1f2937;
                font-size: 11pt;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #3b82f6;
            }}
            
            .header h1 {{
                color: #1e40af;
                margin: 0;
                font-size: 24pt;
            }}
            
            .header .subtitle {{
                color: #6b7280;
                font-size: 12pt;
                margin-top: 5px;
            }}
            
            .company-info {{
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            
            .company-info h2 {{
                margin-top: 0;
                color: #1e40af;
                font-size: 14pt;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }}
            
            .info-item {{
                margin: 5px 0;
            }}
            
            .info-label {{
                font-weight: bold;
                color: #4b5563;
            }}
            
            .overall-score {{
                background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
                color: white;
                padding: 25px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            
            .overall-score h2 {{
                margin: 0 0 15px 0;
                font-size: 16pt;
            }}
            
            .score-display {{
                font-size: 48pt;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .risk-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                margin-top: 10px;
            }}
            
            .category-section {{
                margin-bottom: 25px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                overflow: hidden;
                page-break-inside: avoid;
            }}
            
            .category-header {{
                background-color: #f9fafb;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            .category-header h3 {{
                margin: 0;
                color: #1f2937;
                font-size: 13pt;
            }}
            
            .category-score {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .score-value {{
                font-size: 18pt;
                font-weight: bold;
                color: #1f2937;
            }}
            
            .category-details {{
                padding: 15px;
            }}
            
            .score-breakdown {{
                color: #6b7280;
                font-size: 10pt;
                margin-bottom: 10px;
            }}
            
            .issues, .recommendations {{
                margin-top: 15px;
            }}
            
            .issues h4, .recommendations h4 {{
                color: #1e40af;
                margin: 0 0 10px 0;
                font-size: 11pt;
            }}
            
            .issues-list, .recommendations-list {{
                margin: 0;
                padding-left: 20px;
            }}
            
            .issues-list li {{
                color: #dc2626;
                margin-bottom: 5px;
            }}
            
            .recommendations-list li {{
                color: #059669;
                margin-bottom: 5px;
            }}
            
            .no-issues {{
                color: #10b981;
                font-style: italic;
                margin: 0;
            }}
            
            .priority-actions {{
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 20px;
                margin: 30px 0;
                page-break-inside: avoid;
            }}
            
            .priority-actions h2 {{
                color: #92400e;
                margin-top: 0;
                font-size: 14pt;
            }}
            
            .priority-actions-list {{
                margin: 10px 0;
                padding-left: 25px;
            }}
            
            .priority-actions-list li {{
                margin-bottom: 10px;
                color: #78350f;
            }}
            
            .annexure-section {{
                margin-top: 40px;
                page-break-before: always;
            }}
            
            .annexure-section h2 {{
                color: #1e40af;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 10px;
                font-size: 16pt;
            }}
            
            .annexure-section h3 {{
                color: #1f2937;
                margin-top: 25px;
                font-size: 13pt;
            }}
            
            .annexure-section h4 {{
                color: #4b5563;
                margin-top: 20px;
                font-size: 12pt;
            }}
            
            .annexure-section ul {{
                line-height: 1.8;
            }}
            
            .annexure-section li {{
                margin-bottom: 10px;
            }}
            
            .annexure-section a {{
                color: #2563eb;
                text-decoration: none;
            }}
            
            .disclaimer-section {{
                margin-top: 40px;
                padding: 20px;
                background-color: #fef2f2;
                border: 2px solid #ef4444;
                border-radius: 8px;
                page-break-before: always;
            }}
            
            .disclaimer-section h2 {{
                color: #991b1b;
                margin-top: 0;
                font-size: 14pt;
            }}
            
            .disclaimer-section p {{
                margin: 10px 0;
                color: #7f1d1d;
            }}
            
            .disclaimer-section ul {{
                color: #7f1d1d;
                line-height: 1.8;
            }}
            
            .disclaimer-section strong {{
                color: #991b1b;
            }}
            
            .footer {{
                margin-top: 30px;
                text-align: center;
                color: #6b7280;
                font-size: 9pt;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Compliance Health Check Report</h1>
            <div class="subtitle">Indian Startup HR & Labour Compliance Assessment</div>
        </div>
        
        <div class="company-info">
            <h2>Company Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Company Name:</span> {result.company_name}
                </div>
                <div class="info-item">
                    <span class="info-label">Contact Person:</span> {result.contact_name}
                </div>
                <div class="info-item">
                    <span class="info-label">Email:</span> {result.email}
                </div>
                <div class="info-item">
                    <span class="info-label">Assessment Date:</span> {result.submission_date.strftime("%B %d, %Y")}
                </div>
            </div>
        </div>
        
        <div class="overall-score">
            <h2>Overall Compliance Score</h2>
            <div class="score-display">{result.overall_percentage:.1f}%</div>
            <div>Score: {result.overall_score} / {result.max_score}</div>
            <span class="risk-badge" style="background-color: {risk_color};">{risk_display}</span>
        </div>
        
        <div class="priority-actions">
            <h2>Priority Actions</h2>
            {priority_actions_html}
        </div>
        
        <h2 style="color: #1e40af; margin-top: 30px; font-size: 16pt;">Category Breakdown</h2>
        {category_rows}
        
        {STATE_ANNEXURE}
        
        {disclaimer_with_date}
        
        <div class="footer">
            <p>Generated by Startup Compliance Health Check Tool</p>
            <p>Report ID: {result.id}</p>
        </div>
    </body>
    </html>
    """
    
    return html_content


def generate_pdf_report(result: AssessmentResult, output_path: Optional[str] = None) -> str:
    if output_path is None:
        os.makedirs("/tmp/compliance_reports", exist_ok=True)
        output_path = f"/tmp/compliance_reports/report_{result.id}.pdf"
    
    html_content = generate_html_report(result)
    
    HTML(string=html_content).write_pdf(output_path)
    
    return output_path
