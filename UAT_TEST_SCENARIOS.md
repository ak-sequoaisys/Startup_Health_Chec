# User Acceptance Testing (UAT) Scenarios

## Overview
This document outlines comprehensive UAT scenarios for the Startup Compliance Health Check Tool. These scenarios should be executed manually to validate the complete user experience across different business contexts.

## Test Environment Setup
- **Frontend URL**: http://localhost:5173
- **Backend URL**: http://localhost:8000
- **Test Data**: Use realistic company information for each scenario
- **Browsers**: Test on Chrome, Firefox, Safari, and Edge

---

## Scenario 1: Small Tech Startup (High Risk)

### Company Profile
- **Company Name**: TechStart Innovations
- **Industry**: Technology
- **Employee Range**: 1-10 employees
- **Operating States**: NSW, VIC
- **Business Age**: 0-1 year
- **Email**: uat-techstart@example.com

### Expected Behavior
1. Navigate to application homepage
2. Click "Start Assessment"
3. Fill in company details with above information
4. Select consent checkbox
5. Answer all 15 questions selecting options that indicate minimal compliance (lowest scores)
6. Submit assessment

### Expected Results
- **Overall Risk Level**: HIGH_RISK or CRITICAL
- **Score**: Below 40%
- **Priority Actions**: Should include multiple critical items
- **Category Breakdown**: Multiple categories showing high risk
- **Recommendations**: Comprehensive list of compliance improvements needed

### Validation Points
- [ ] Assessment completes without errors
- [ ] Results display correctly
- [ ] Risk level accurately reflects poor compliance
- [ ] Priority actions are specific and actionable
- [ ] PDF report can be generated
- [ ] Results can be shared via link

---

## Scenario 2: Medium-Sized Healthcare Company (Moderate Risk)

### Company Profile
- **Company Name**: HealthCare Plus Pty Ltd
- **Industry**: Healthcare
- **Employee Range**: 51-200 employees
- **Operating States**: QLD, NSW, VIC
- **Business Age**: 3-5 years
- **Email**: uat-healthcare@example.com

### Expected Behavior
1. Complete assessment with mixed answers (some compliant, some non-compliant)
2. Focus on having good documentation but weak workplace policies
3. Strong payroll compliance but weak termination procedures

### Expected Results
- **Overall Risk Level**: MODERATE
- **Score**: 60-70%
- **Category Breakdown**: 
  - Registration: HEALTHY
  - Employee Docs: HEALTHY
  - Payroll/Statutory: HEALTHY
  - Workplace Policies: HIGH_RISK
  - Labour Filings: MODERATE
  - Governance: MODERATE
- **Priority Actions**: Focus on workplace policies and governance

### Validation Points
- [ ] Mixed risk levels display correctly across categories
- [ ] Recommendations are category-specific
- [ ] Progress bar updates correctly during assessment
- [ ] Can navigate back and forth between questions
- [ ] Previous answers are retained when navigating back

---

## Scenario 3: Established Retail Business (Low Risk)

### Company Profile
- **Company Name**: Retail Excellence Group
- **Industry**: Retail
- **Employee Range**: 201+ employees
- **Operating States**: All states (NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
- **Business Age**: 5+ years
- **Email**: uat-retail@example.com

### Expected Behavior
1. Complete assessment selecting all best-practice options
2. Demonstrate full compliance across all categories
3. Show comprehensive documentation and policies

### Expected Results
- **Overall Risk Level**: HEALTHY
- **Score**: Above 80%
- **Category Breakdown**: All categories showing HEALTHY or MODERATE
- **Priority Actions**: Minimal or maintenance-focused actions
- **Recommendations**: Focus on continuous improvement

### Validation Points
- [ ] High scores display with appropriate positive messaging
- [ ] Healthy risk indicators show green/positive colors
- [ ] Recommendations focus on maintaining compliance
- [ ] PDF report reflects positive compliance status
- [ ] Lead information captured correctly in backend

---

## Scenario 4: Multi-State Manufacturing Company

### Company Profile
- **Company Name**: Indian Manufacturing Co
- **Industry**: Manufacturing
- **Employee Range**: 51-200 employees
- **Operating States**: NSW, VIC, QLD, WA
- **Business Age**: 3-5 years
- **Email**: uat-manufacturing@example.com

### Expected Behavior
1. Complete assessment with focus on multi-state compliance challenges
2. Test state-specific applicability rules
3. Verify questions adapt based on operating states

### Expected Results
- Questions should be relevant to multi-state operations
- Recommendations should address cross-state compliance
- Risk assessment should consider complexity of multi-state operations

### Validation Points
- [ ] State-specific questions display appropriately
- [ ] Multi-state compliance issues are highlighted
- [ ] Recommendations address jurisdictional differences
- [ ] All selected states are reflected in results

---

## Scenario 5: Startup with Incomplete Assessment (Error Handling)

### Company Profile
- **Company Name**: Incomplete Test Co
- **Industry**: Technology
- **Employee Range**: 11-50 employees
- **Operating States**: NSW
- **Business Age**: 1-3 years
- **Email**: uat-incomplete@example.com

### Expected Behavior
1. Start assessment but skip required fields
2. Attempt to proceed without answering questions
3. Test validation and error messages
4. Refresh page mid-assessment
5. Test browser back button behavior

### Expected Results
- Appropriate validation messages display
- Cannot proceed without required information
- Error messages are clear and helpful
- Application handles interruptions gracefully

### Validation Points
- [ ] Email validation works correctly
- [ ] Required field indicators are clear
- [ ] Cannot submit without consent
- [ ] Cannot proceed without selecting operating states
- [ ] Error messages are user-friendly
- [ ] Application doesn't crash on invalid input

---

## Scenario 6: Mobile User Experience

### Company Profile
- **Company Name**: Mobile Test Company
- **Industry**: Services
- **Employee Range**: 11-50 employees
- **Operating States**: VIC
- **Business Age**: 1-3 years
- **Email**: uat-mobile@example.com

### Expected Behavior
1. Complete entire assessment on mobile device (iOS and Android)
2. Test touch interactions
3. Verify responsive design
4. Test form inputs on mobile keyboards

### Expected Results
- All functionality works on mobile devices
- Layout adapts appropriately
- Touch targets are appropriately sized
- Forms are easy to complete on mobile

### Validation Points
- [ ] Intro screen displays correctly on mobile
- [ ] Contact form is usable on mobile
- [ ] Radio buttons are easy to tap
- [ ] Checkboxes work with touch
- [ ] Progress bar is visible
- [ ] Results page is readable on small screens
- [ ] PDF download works on mobile
- [ ] Share functionality works on mobile

---

## Scenario 7: Accessibility Testing

### Company Profile
- **Company Name**: Accessibility Test Co
- **Industry**: Technology
- **Employee Range**: 11-50 employees
- **Operating States**: NSW
- **Business Age**: 1-3 years
- **Email**: uat-a11y@example.com

### Expected Behavior
1. Complete assessment using only keyboard navigation
2. Test with screen reader (NVDA, JAWS, or VoiceOver)
3. Verify color contrast
4. Test with browser zoom at 200%

### Expected Results
- All interactive elements are keyboard accessible
- Screen reader announces all content correctly
- Color contrast meets WCAG AA standards
- Application remains usable at high zoom levels

### Validation Points
- [ ] Can tab through all form fields
- [ ] Can select radio buttons with keyboard
- [ ] Can check checkboxes with keyboard
- [ ] Screen reader announces form labels
- [ ] Screen reader announces validation errors
- [ ] Focus indicators are visible
- [ ] Skip links are available
- [ ] Headings are properly structured
- [ ] ARIA labels are present where needed

---

## Scenario 8: Performance Testing

### Company Profile
- **Company Name**: Performance Test Co
- **Industry**: Technology
- **Employee Range**: 11-50 employees
- **Operating States**: NSW
- **Business Age**: 1-3 years
- **Email**: uat-performance@example.com

### Expected Behavior
1. Measure page load times
2. Measure assessment submission time
3. Test with slow network connection (3G simulation)
4. Monitor browser console for errors

### Expected Results
- First Contentful Paint (FCP) < 2 seconds
- Assessment submission < 5 seconds
- No JavaScript errors in console
- Smooth animations and transitions

### Validation Points
- [ ] Homepage loads quickly
- [ ] Questions load without delay
- [ ] Navigation between questions is instant
- [ ] Results display within 5 seconds
- [ ] PDF generation completes within 10 seconds
- [ ] No memory leaks during extended use
- [ ] Application works on slow connections

---

## Scenario 9: Data Persistence and Recovery

### Company Profile
- **Company Name**: Data Test Company
- **Industry**: Technology
- **Employee Range**: 11-50 employees
- **Operating States**: NSW
- **Business Age**: 1-3 years
- **Email**: uat-data@example.com

### Expected Behavior
1. Start assessment and answer several questions
2. Close browser tab
3. Reopen application
4. Test if progress is saved (if implemented)
5. Complete assessment
6. Verify results are retrievable via URL

### Expected Results
- Assessment can be completed after interruption
- Results remain accessible via unique URL
- Lead data is captured correctly in backend

### Validation Points
- [ ] Assessment ID is generated correctly
- [ ] Results URL is shareable
- [ ] Results can be retrieved later
- [ ] Lead information is stored in database
- [ ] Assessment data is complete and accurate

---

## Scenario 10: Admin Dashboard Access

### Company Profile
- **Admin User**: admin@offrd.com.au
- **Password**: [Use configured admin password]

### Expected Behavior
1. Access admin dashboard
2. View all submitted assessments
3. Filter assessments by date, state, score
4. Export assessment data to CSV
5. Review audit logs

### Expected Results
- Admin can view all leads and assessments
- Filtering works correctly
- CSV export contains all relevant data
- Audit logs show email notification status

### Validation Points
- [ ] Admin authentication works
- [ ] Dashboard displays all assessments
- [ ] Filters apply correctly
- [ ] Date range filtering works
- [ ] State filtering works
- [ ] Score filtering works
- [ ] CSV export downloads successfully
- [ ] CSV contains all expected columns
- [ ] Audit logs are complete and accurate

---

## Test Execution Checklist

### Pre-Testing
- [ ] Backend server is running
- [ ] Frontend server is running
- [ ] Database is accessible
- [ ] Email service is configured (if applicable)
- [ ] Test data is prepared

### During Testing
- [ ] Document any bugs or issues
- [ ] Take screenshots of unexpected behavior
- [ ] Note browser console errors
- [ ] Record network request failures
- [ ] Capture performance metrics

### Post-Testing
- [ ] All scenarios completed
- [ ] Issues documented in issue tracker
- [ ] Test results summarized
- [ ] Stakeholders notified of findings
- [ ] Regression testing planned for fixes

---

## Success Criteria

### Functional Requirements
- ✅ All 15 questions display correctly
- ✅ Assessment can be completed end-to-end
- ✅ Results are calculated accurately
- ✅ Risk levels are assigned correctly
- ✅ Recommendations are relevant and helpful
- ✅ PDF reports generate successfully
- ✅ Lead data is captured correctly

### Non-Functional Requirements
- ✅ FCP < 2 seconds
- ✅ Assessment submission < 5 seconds
- ✅ No accessibility violations (WCAG AA)
- ✅ Works on all major browsers
- ✅ Responsive on mobile devices
- ✅ No JavaScript errors in console
- ✅ Secure data handling

### User Experience
- ✅ Intuitive navigation
- ✅ Clear instructions
- ✅ Helpful error messages
- ✅ Professional appearance
- ✅ Smooth interactions
- ✅ Consistent branding

---

## Issue Reporting Template

When reporting issues found during UAT, use the following template:

```
**Issue Title**: [Brief description]

**Scenario**: [Which UAT scenario]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]

**Actual Result**: [What actually happened]

**Severity**: [Critical/High/Medium/Low]

**Browser/Device**: [Browser version and device]

**Screenshots**: [Attach if applicable]

**Additional Notes**: [Any other relevant information]
```

---

## Sign-Off

### Test Execution
- **Tester Name**: ___________________
- **Date**: ___________________
- **Scenarios Completed**: _____ / 10
- **Issues Found**: _____
- **Critical Issues**: _____

### Approval
- **Product Owner**: ___________________
- **Date**: ___________________
- **Status**: [ ] Approved [ ] Rejected [ ] Conditional

### Notes
_____________________________________
_____________________________________
_____________________________________
