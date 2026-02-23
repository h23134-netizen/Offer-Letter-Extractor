import re

text = """
Compensation & Benefits

a) You will be entitled to be paid an all-inclusive aggregate compensation of INR 14,00,000 per annum. Your employment will be governed by the Company's standard employment agreement which is to be executed by you on the date of joining.
"""

def _extract_compensation(compensation_text: str, global_text: str):
    pattern = r'(?:total annual|aggregate)\s+compensation of\s*(?:INR|Rs\.?|₹|Rs)\s*([\d,]+)\s*per annum'
    if compensation_text:
        match = re.search(pattern, compensation_text, re.IGNORECASE)
        if match:
            raw = match.group(0).strip()
            num = int(match.group(1).replace(',', ''))
            return raw, num, 1.0, "compensation_section"
            
    if global_text:
        match = re.search(pattern, global_text, re.IGNORECASE)
        if match:
            raw = match.group(0).strip()
            num = int(match.group(1).replace(',', ''))
            return raw, num, 0.7, "regex_fallback"
        
    return None, None, 0.0, "missing"

print("CTC:")
print(_extract_compensation(text, text))

sch_text = """
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

# Let's see how our _extract_schedule_a_fields works on this
def _extract_schedule_a_fields(schedule_text: str):
    dept, comp, band, grade = None, None, None, None
    if not schedule_text:
        return None, None, None, None, 0.0, "missing"
        
    lines = [l.strip() for l in schedule_text.split('\n') if l.strip()]
    
    for i, line in enumerate(lines):
        # Department
        match0 = re.search(r'^Department\s*[:\-]*\s*(.+)', line, re.IGNORECASE)
        if match0 and not dept:
            dept = match0.group(1).strip()
        elif re.search(r'^Department\s*[:\-]*$', line, re.IGNORECASE) and not dept:
            if i + 1 < len(lines):
                dept = lines[i+1].strip()

        # 1. Competency
        match1 = re.search(r'Competency\s*[:\-]*\s*(.+?)(?=\s+(?:Band|Grade)|$)', line, re.IGNORECASE)
        if not match1:
             match1 = re.search(r'^Competency\s+(.+)', line, re.IGNORECASE)
             
        if match1 and not comp:
            comp = match1.group(1).strip()
            if comp == "": comp = None
        elif re.search(r'^Competency\s*[:\-]*$', line, re.IGNORECASE) and not comp:
            if i + 1 < len(lines):
                comp = lines[i+1].strip()
            
        # 2. Band
        match2 = re.search(r'^Band\s*[:\-]*\s*([A-Za-z0-9\-\.]+)', line, re.IGNORECASE)
        if match2 and not band:
            band = match2.group(1).strip()
        elif re.search(r'^Band\s*[:\-]*$', line, re.IGNORECASE) and not band:
            if i + 1 < len(lines):
                band = lines[i+1].strip()
            
        # 3. Grade
        match3 = re.search(r'^Grade\s*[:\-]*\s*([A-Za-z0-9\-\.]+)', line, re.IGNORECASE)
        if match3 and not grade:
            grade = match3.group(1).strip()
        elif re.search(r'^Grade\s*[:\-]*$', line, re.IGNORECASE) and not grade:
            if i + 1 < len(lines):
                grade = lines[i+1].strip()
            
    if dept or comp or band or grade:
        # Override
        if grade:
            band = str(grade).split('.')[0]
            
        return dept, comp, band, grade, 1.0, "scheduleA"
    return None, None, None, None, 0.0, "missing"

print("Schedule A Table Format:")
print(_extract_schedule_a_fields(sch_text))

sch_text2 = """
Department Human Resources
Competency Shared (HR - Generalist)
Band 2
Grade 2.2
"""
print("Schedule A Line Format:")
print(_extract_schedule_a_fields(sch_text2))
