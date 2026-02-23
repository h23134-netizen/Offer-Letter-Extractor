import pytest
from extractor.text_extractor import TextExtractor
from extractor.field_parser import FieldParser

# Fixtures
SUPPORT_TEMPLATE_TEXT = """
OFFER LETTER

Dear John Doe,
We are pleased to offer you the position of Customer Support Executive at Gurugram, Haryana, India.
Your employment will be effective from your 15-05-2025 and you will be on probation for a period of 6 months.

Compensation & Benefits
Your total annual compensation of INR 4,50,000 per annum.

Schedule A
Designation: Customer Support Executive
Sub-Department: Customer Excellence - CX
Band: 2
Grade: 2.1

SALARY COMPUTATION
Basic               150000 12500
HRA                 75000  6250
(A) Gross Salary    225000 18750
Provident Fund      18000  1500
(B) Long Term Benefits 18000 1500
Total CTC           450000 37500

ACCEPTANCE OF OFFER TERMS AND CONDITIONS
Date of Joining: 15/05/2025
"""

SALES_FIELD_TEMPLATE_TEXT = """
OFFER LETTER

Dear Jane Smith,
We are pleased to offer you the position of Field Sales Manager at Rajkot, Gujarat, India.
Your employment will be effective from your 01-06-2025.

Compensation & Benefits
Your total annual compensation of Rs. 6,00,000 per annum.

BYOD
You are required to bring your own device.

Schedule A
Designation: Field Sales Manager
Sub-Department: Sales
Band: S1
Grade: G3

SALARY COMPUTATION
Basic               200000 16666
HRA                 100000 8333
(A) Gross Salary    300000 24999
Total CTC           600000 50000
"""

def test_support_template():
    extractor = TextExtractor()
    parser = FieldParser()
    
    sections = extractor.split_sections(SUPPORT_TEMPLATE_TEXT)
    parsed = parser.parse(sections)
    
    fields = parsed["fields"]
    
    assert fields["designation"] == "Customer Support Executive"
    assert fields["location_city"] == "Gurugram"
    assert fields["location_state"] == "Haryana"
    assert fields["date_of_joining_norm"] == "2025-05-15"
    assert fields["comp_total_annual_inr"] == 450000
    assert fields["byod_clause"] == "No"
    assert fields["scheduleA_sub_department"] == "Customer Excellence - CX"
    assert fields["scheduleA_band"] == "2"
    assert fields["scheduleA_grade"] == "2.1"
    
    assert len(fields["salary_table_rows"]) == 6
    assert fields["salary_table_totals"]["gross_salary"] == 225000
    assert fields["salary_table_totals"]["total_ctc"] == 450000

def test_sales_field_template():
    extractor = TextExtractor()
    parser = FieldParser()
    
    sections = extractor.split_sections(SALES_FIELD_TEMPLATE_TEXT)
    parsed = parser.parse(sections)
    
    fields = parsed["fields"]
    
    assert fields["designation"] == "Field Sales Manager"
    assert fields["location_city"] == "Rajkot"
    assert fields["location_state"] == "Gujarat"
    assert fields["date_of_joining_norm"] == "2025-06-01"
    assert fields["comp_total_annual_inr"] == 600000
    assert fields["byod_clause"] == "Yes"
    
    assert fields["salary_table_totals"]["gross_salary"] == 300000

BONUS_TEMPLATE_TEXT = """
OFFER LETTER
Dear Sam Smith,
We are pleased to offer you the position of Customer Support Executive at Gurugram, Haryana, India.

Compensation & Benefits
Your total annual compensation of INR 4,50,000 per annum.

Retention Bonus:
In addition to the above, you will be entitled to an INR 100000 as a Retention Bonus, which will be paid upon completing 12 months.

ESOP:
You are also entitled to the ESOP program and will be offered ESOPs worth total of INR 500000 at Fair Market Value.

Joining Bonus:
You will receive Rs 50,000 as a Joining Bonus in your first paycheck.
"""
def test_bonus_extraction():
    extractor = TextExtractor()
    parser = FieldParser()
    sections = extractor.split_sections(BONUS_TEMPLATE_TEXT)
    parsed = parser.parse(sections)
    fields = parsed["fields"]
    
    assert fields["bonus_retention_inr"] == 100000
    assert fields["esop_amount_inr"] == 500000
    assert fields["bonus_joining_inr"] == 50000

NEW_LAYOUT_TEXT = """
OFFER LETTER
Dear Debayan Debnath,
We are pleased to offer you the position.

Compensation & Benefits
a) You will be entitled to be paid an all-inclusive aggregate compensation of INR 14,00,000 per annum.

Schedule A
Name
Debayan Debnath
Designation
Management Trainee
Entity
GFPL
Business Unit
Enabling Functions
Department
Human Resources
Sub-Department
Generalist
Competency
Shared (HR - Generalist)
Band
2
Grade
2.2
"""
def test_new_layout_extraction():
    extractor = TextExtractor()
    parser = FieldParser()
    sections = extractor.split_sections(NEW_LAYOUT_TEXT)
    parsed = parser.parse(sections)
    fields = parsed["fields"]
    
    assert fields["comp_total_annual_inr"] == 1400000
    assert fields["scheduleA_department"] == "Human Resources"
    assert fields["scheduleA_sub_department"] == "Generalist"
    assert fields["scheduleA_band"] == "2"
    assert fields["scheduleA_grade"] == "2.2"

