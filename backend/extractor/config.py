import re

SECTION_HEADERS = [
    "OFFER LETTER",
    "Compensation & Benefits",
    "Additional Terms and Conditions",
    "BYOD",
    "Schedule A",
    "SALARY COMPUTATION",
    "ACCEPTANCE OF OFFER TERMS AND CONDITIONS"
]

# More specific anchors first, then generic ones
FIELD_CONFIG = {
    "candidate_name": [
        "Name", "Employee Name", "Candidate Name", "Name of the Candidate", "Name of Employee",
        "Appointee Name", "Selected Candidate", "Offer extended to", "Dear", "To", "Mr.", "Ms.", "Mrs.",
        "Name of the Employee", "Employee", "Party of the First Part", "Personal Details", "Candidate"
    ],
    "designation": [
        "Designation", "Job Title", "Title", "Position", "Role", "Appointed as", "offered the position of",
        "Designated as", "position of", "Job Role", "Rank", "Grade", "Level", "Career Level",
        "Corporate Title", "Functional Title", "Responsibility", "Capacity", "Employment Title",
        "Job Position", "role of", "title of", "position as", "serving as", "engaged as",
        "You have been selected for the position of", "We are pleased to offer you the role of"
    ],
    "department": [
        "Department", "Dept", "Function", "Business Unit", "Vertical", "Stream", "Process",
        "Division", "Segment", "Practice", "Tower", "Tribe", "Squad", "Team", "Group",
        "Sub-Department", "Unit", "Cost Center", "Profit Center", "Service Line", "Domain",
        "Competency", "Sector", "Industry", "LOB", "Line of Business", "Strategic Unit"
    ],
    "joining_date": [
        "Date of Joining", "Joining Date", "DOJ", "Start Date", "Commencement Date", "Effective Date",
        "Reporting Date", "date of commencement", "effective from", "effective from your",
        "Appointment Date", "Date of Appointment", "Onboarding Date", "Employment Start Date",
        "Work Start Date", "Date of Commencement of Employment", "joining us on", "report for duty on",
        "employment shall be effective from", "joining on or before", "expected to join by",
        "Tentative Date of Joining", "Proposed Start Date"
    ],
    "ctc": [
        "CTC", "Total CTC", "Fixed CTC", "Annual CTC", "Cost to Company", "Total Cost to Company",
        "Remuneration", "Annual Compensation", "Gross Salary", "TCO", "Total Compensation",
        "Compensation", "Salary", "aggregate compensation of", "Annual Salary", "Monthly Salary",
        "Total Remuneration", "Cost to the Company", "Total Annual Cost to Company", "Annual Gross",
        "Fixed Pay", "Total Fixed Pay", "Annual Package", "Compensation Package", "Emoluments",
        "Gross Emoluments", "Pay Package", "Total Target Cash", "TTC", "Ote", "On Target Earnings",
        "Annual Cost", "Yearly Compensation", "Annualized CTC"
    ],
    "location": [
        "Location", "Work Location", "Base Location", "Place of Posting", "Posting", "Office Location",
        "Place of Work", "Stationed at", "at Plot No.", "Office Address", "Reporting Location",
        "Work Base", "Depot", "Branch", "Campus", "Site", "Zone", "Region", "City",
        "Territory", "Headquarters", "Registered Office", "Operating from", "Based at",
        "working from", "report to the office at", "primary work location"
    ],
    "probation_period": [
        "Probation Period", "Probationary Period", "Probation", "Period of Probation",
        "probation for a period of", "Training Period", "Trial Period", "Evaluation Period",
        "Assessment Period", "Review Period", "probationary basis", "on probation",
        "period of training", "confirmation period"
    ],
    "notice_period": [
        "Notice Period", "Notice", "Termination Notice", "Resignation Notice", "Separation Notice",
        "Notice for Termination", "Period of Notice", "Days Notice", "Months Notice", "Exit Notice",
        "Separation Period", "Notice Pay", "Notice Duration", "Termination Clause"
    ],
    "reporting_manager": [
        "Reporting Manager", "Reporting To", "Reports To", "Supervisor", "Line Manager", "Manager",
        "Team Lead", "Head of", "Director", "VP", "Vice President", "Directly reporting to",
        "Functional Manager", "Administrative Manager", "Project Manager", "Delivery Manager",
        "Reviewer", "Appraiser", "Mentor", "Guide", "Supervised by", "Accountable to"
    ]
}

REGEX_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "date": [
        r"\d{2}-\d{2}-\d{4}",  # DD-MM-YYYY (Priority for this specific file)
        r"\d{2}/\d{2}/\d{4}", 
        r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}",
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}"
    ],
    "currency": [
         r"(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?(?:\s*(?:Lakhs?|LPA|Cr|Crores?))?",
         r"[\d,]+(?:\.\d{2})?\s*(?:Lakhs?|LPA)"
    ]
}

MULTIPLIERS = {
    "lakh": 100000,
    "lakhs": 100000,
    "lpa": 100000,
    "cr": 10000000,
    "crore": 10000000,
    "crores": 10000000
}
