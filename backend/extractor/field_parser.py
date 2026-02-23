import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import dateparser

class FieldParser:
    def parse(self, sections: dict) -> Dict[str, Any]:
        """
        Parses strictly defined fields using section bounds.
        """
        results = {
            "designation": None,
            "location_city": None,
            "location_state": None,
            "date_of_joining_raw": None,
            "date_of_joining_norm": None,
            "comp_total_annual_raw": None,
            "comp_total_annual_inr": None,
            "bonus_joining_inr": None,
            "bonus_retention_inr": None,
            "esop_amount_inr": None,
            "byod_clause": "No",
            "scheduleA_department": None,
            "scheduleA_competency": None,
            "scheduleA_band": None,
            "scheduleA_grade": None,
            "salary_table_rows": [],
            "salary_table_totals": {}
        }
        confidence_scores = {k: 0.0 for k in results.keys()}
        extraction_methods = {k: "missing" for k in results.keys()}
        
        # We need to extract from sections
        header_text = sections.get("header", "")
        compensation_text = sections.get("compensation", "")
        scheduleA_text = sections.get("scheduleA", "")
        byod_text = sections.get("byod", "")
        table_text = sections.get("salary_table", "")
        acceptance_text = sections.get("acceptance", "")
        
        # Globally combined fallback (if needed)
        global_text = "\n".join(sections.values())
        
        # 1. Designation
        # Priority 1: Schedule A
        # Priority 2: Intro sentence in header
        designation_val, desig_conf, desig_meth = self._extract_designation(scheduleA_text, header_text)
        results["designation"] = designation_val
        confidence_scores["designation"] = desig_conf
        extraction_methods["designation"] = desig_meth

        # 2. Location (City + State)
        # Regex: at\s+(.*?),\s*(.*?),\s*India from intro sentence
        loc_city, loc_state, loc_conf, loc_meth = self._extract_location(header_text)
        results["location_city"] = loc_city
        results["location_state"] = loc_state
        confidence_scores["location_city"] = loc_conf
        confidence_scores["location_state"] = loc_conf
        extraction_methods["location_city"] = loc_meth
        extraction_methods["location_state"] = loc_meth
        
        # 3. Date of Joining
        # Labeled in acceptance -> intro sentence fallback
        doj_raw, doj_norm, doj_conf, doj_meth = self._extract_date_of_joining(acceptance_text, header_text)
        results["date_of_joining_raw"] = doj_raw
        results["date_of_joining_norm"] = doj_norm
        confidence_scores["date_of_joining_raw"] = doj_conf
        confidence_scores["date_of_joining_norm"] = doj_conf
        extraction_methods["date_of_joining_raw"] = doj_meth
        extraction_methods["date_of_joining_norm"] = doj_meth
        
        # 4. Compensation Headline
        comp_raw, comp_inr, comp_conf, comp_meth = self._extract_compensation(compensation_text, global_text)
        results["comp_total_annual_raw"] = comp_raw
        results["comp_total_annual_inr"] = comp_inr
        confidence_scores["comp_total_annual_raw"] = comp_conf
        confidence_scores["comp_total_annual_inr"] = comp_conf
        extraction_methods["comp_total_annual_raw"] = comp_meth
        extraction_methods["comp_total_annual_inr"] = comp_meth
        
        # 5. BYOD
        if byod_text and byod_text.strip():
            # If the section was found, it implies BYOD
            results["byod_clause"] = "Yes"
            confidence_scores["byod_clause"] = 1.0
            extraction_methods["byod_clause"] = "binary_presence"
        else:
            # Check globally if the exact string exists just in case
            if "BYOD" in global_text:
                results["byod_clause"] = "Yes"
                confidence_scores["byod_clause"] = 1.0
                extraction_methods["byod_clause"] = "binary_presence"
            else:
                results["byod_clause"] = "No"
                confidence_scores["byod_clause"] = 1.0
                extraction_methods["byod_clause"] = "binary_absence"
            
        # 6. Schedule A Department, Competency, Band, Grade
        dept, comp, band, grade, sch_conf, sch_meth = self._extract_schedule_a_fields(scheduleA_text)
        results["scheduleA_department"] = dept
        results["scheduleA_competency"] = comp
        results["scheduleA_band"] = band
        results["scheduleA_grade"] = grade
        confidence_scores["scheduleA_department"] = sch_conf
        confidence_scores["scheduleA_competency"] = sch_conf
        confidence_scores["scheduleA_band"] = sch_conf
        confidence_scores["scheduleA_grade"] = sch_conf
        extraction_methods["scheduleA_department"] = sch_meth
        extraction_methods["scheduleA_competency"] = sch_meth
        extraction_methods["scheduleA_band"] = sch_meth
        extraction_methods["scheduleA_grade"] = sch_meth
        
        # 7. Salary Computation Table
        rows, totals, tab_conf, tab_meth = self._extract_salary_table(table_text)
        results["salary_table_rows"] = rows
        results["salary_table_totals"] = totals
        confidence_scores["salary_table_rows"] = tab_conf
        confidence_scores["salary_table_totals"] = tab_conf
        extraction_methods["salary_table_rows"] = tab_meth
        extraction_methods["salary_table_totals"] = tab_meth

        # 8. Bonuses (Joining and Retention)
        jb_inr, jb_conf, jb_meth = self._extract_bonus(global_text, "Joining")
        results["bonus_joining_inr"] = jb_inr
        confidence_scores["bonus_joining_inr"] = jb_conf
        extraction_methods["bonus_joining_inr"] = jb_meth

        rb_inr, rb_conf, rb_meth = self._extract_bonus(global_text, "Retention")
        results["bonus_retention_inr"] = rb_inr
        confidence_scores["bonus_retention_inr"] = rb_conf
        extraction_methods["bonus_retention_inr"] = rb_meth

        # 9. ESOP Amount
        esop_inr, esop_conf, esop_meth = self._extract_esop(global_text)
        results["esop_amount_inr"] = esop_inr
        confidence_scores["esop_amount_inr"] = esop_conf
        extraction_methods["esop_amount_inr"] = esop_meth

        return {
            "fields": results,
            "confidence": confidence_scores,
            "methods": extraction_methods
        }

    def _extract_designation(self, schedule_text: str, header_text: str):
        if schedule_text:
            match = re.search(r'Designation\s*[:\-]?\s*([^\n]+)', schedule_text, re.IGNORECASE)
            if match:
                return match.group(1).strip(), 1.0, "scheduleA"
        
        if header_text:
            match = re.search(r'offer you the position of\s+([^,\.]+)', header_text, re.IGNORECASE)
            if match:
                return match.group(1).strip(), 0.9, "intro_sentence"
                
        return None, 0.0, "missing"

    def _extract_location(self, header_text: str):
        if header_text:
             # Grab the last two comma-separated words right before 'India'
            match = re.search(r'([^,]+),\s*([^,]+),\s*India', header_text, re.IGNORECASE)
            if match:
                # The city block might contain street address stuff like "Sector 20, Gurugram"
                # Splitting by space and taking the last word isolates the city cleanly
                city = match.group(1).split()[-1].strip()
                state = match.group(2).strip()
                return city, state, 0.9, "intro_sentence"
        return None, None, 0.0, "missing"

    def _extract_date_of_joining(self, acceptance_text: str, header_text: str):
        if acceptance_text:
            match = re.search(r'Date of Joining\s*[:\-]?\s*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4}|\d{1,2}\s+[a-zA-Z]+\s+\d{4})', acceptance_text, re.IGNORECASE)
            if match:
                raw = match.group(1).strip()
                return raw, self._normalize_date(raw), 1.0, "labeled_acceptance"
        
        if header_text:
            match = re.search(r'effective from your\s*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4}|\d{1,2}\s+[a-zA-Z]+\s+\d{4})', header_text, re.IGNORECASE)
            if match:
                raw = match.group(1).strip()
                return raw, self._normalize_date(raw), 0.9, "intro_sentence"
                
        return None, None, 0.0, "missing"

    def _normalize_date(self, date_str: str) -> str:
        try:
            dt = dateparser.parse(date_str, settings={'DATE_ORDER': 'DMY'})
            if dt:
                return dt.strftime("%Y-%m-%d")
        except:
            pass
        return date_str

    def _extract_compensation(self, compensation_text: str, global_text: str):
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

    def _extract_schedule_a_fields(self, schedule_text: str):
        dept, comp, band, grade = None, None, None, None
        if not schedule_text:
            return None, None, None, None, 0.0, "missing"
            
        lines = [l.strip() for l in schedule_text.split('\n') if l.strip()]
        
        for i, line in enumerate(lines):
            # Department
            match0 = re.search(r'Department\s*[:\-]*\s*(.+?)(?=\s+(?:Sub-Department|Competency|Band|Grade)|$)', line, re.IGNORECASE)
            if match0 and not dept:
                dept = match0.group(1).strip()
            elif re.search(r'Department\s*[:\-]*$', line, re.IGNORECASE) and not dept:
                if i + 1 < len(lines):
                    dept = lines[i+1].strip()

            # 1. Competency
            match1 = re.search(r'Competency\s*[:\-]*\s*(.+?)(?=\s+(?:Band|Grade)|$)', line, re.IGNORECASE)
            if match1 and not comp:
                comp = match1.group(1).strip()
                if comp == "": comp = None
            elif re.search(r'Competency\s*[:\-]*$', line, re.IGNORECASE) and not comp:
                if i + 1 < len(lines):
                    comp = lines[i+1].strip()
                
            # 2. Band
            match2 = re.search(r'Band\s*[:\-]*\s*([A-Za-z0-9\-\.]+)', line, re.IGNORECASE)
            if match2 and not band:
                band = match2.group(1).strip()
            elif re.search(r'Band\s*[:\-]*$', line, re.IGNORECASE) and not band:
                if i + 1 < len(lines):
                    band = lines[i+1].strip()
                
            # 3. Grade
            match3 = re.search(r'Grade\s*[:\-]*\s*([A-Za-z0-9\-\.]+)', line, re.IGNORECASE)
            if match3 and not grade:
                grade = match3.group(1).strip()
            elif re.search(r'Grade\s*[:\-]*$', line, re.IGNORECASE) and not grade:
                if i + 1 < len(lines):
                    grade = lines[i+1].strip()
                
        if dept or comp or band or grade:
            # User requested override: Always derive the Band explicitly from the Grade
            # e.g., Grade "2.1" -> Band "2"
            if grade:
                band = str(grade).split('.')[0]
                
            return dept, comp, band, grade, 1.0, "scheduleA"
        return None, None, None, None, 0.0, "missing"

    def _extract_salary_table(self, table_text: str):
        rows = []
        totals = {
            "gross_salary": None,
            "long_term_benefits": None,
            "fixed_ctc": None,
            "total_ctc": None
        }
        
        if not table_text:
            return [], {}, 0.0, "missing"
            
        for line in table_text.split('\n'):
            line = line.strip()
            # Handle multiple spaces and numbers
            match = re.search(r'^(.+?)\s+([\d,]+)(?:\.00)?\s+([\d,]+)(?:\.00)?$', line)
            if match:
                component = match.group(1).strip()
                try:
                    per_annum = int(match.group(2).replace(',', ''))
                    per_month = int(match.group(3).replace(',', ''))
                except ValueError:
                    continue
                    
                rows.append({
                    "component": component,
                    "per_annum": per_annum,
                    "per_month": per_month
                })
                
                lower_comp = component.lower()
                if "gross salary" in lower_comp:
                    totals["gross_salary"] = per_annum
                elif "long term benefits" in lower_comp or "long-term benefits" in lower_comp:
                    totals["long_term_benefits"] = per_annum
                elif "fixed ctc" in lower_comp:
                    totals["fixed_ctc"] = per_annum
                elif "total ctc" in lower_comp:
                    totals["total_ctc"] = per_annum
                    
        if rows:
            return rows, totals, 1.0, "salary_table"
        return [], {}, 0.0, "missing"

    def _extract_bonus(self, global_text: str, bonus_type: str):
        """
        Extracts Joining or Retention bonus amounts with highly permissive proximity scanning.
        """
        clean_text = global_text.replace('\n', ' ')
        
        # Pattern 1: [Type] Bonus ......... INR 100000
        # We allow up to 150 characters of ANYTHING between the Bonus keyword and the Currency indicator
        pattern1 = rf'{bonus_type}\s*Bonus(?:.{{0,150}}?)(?:INR|Rs\.?|₹|Rs)\s*([\d,]{{4,}})'
        
        # Pattern 2: INR 100000 ......... [Type] Bonus
        pattern2 = rf'(?:INR|Rs\.?|₹|Rs)\s*([\d,]{{4,}})(?:.{{0,150}}?){bonus_type}\s*Bonus'
        
        # Pattern 3: Fallback without Currency just in case they wrote "100000 as a Retention Bonus"
        pattern3 = rf'([\d,]{{4,}})(?:.{{0,150}}?){bonus_type}\s*Bonus'
        
        for pat in [pattern1, pattern2, pattern3]:
            match = re.search(pat, clean_text, re.IGNORECASE)
            if match:
                raw_val = match.group(1).replace(',', '').strip()
                try:
                    return float(raw_val), 0.8, "text_proximity"
                except ValueError:
                    pass
                    
        return None, 0.0, "missing"

    def _extract_esop(self, global_text: str):
        """
        Extracts ESOP program value with highly permissive proximity scanning.
        """
        clean_text = global_text.replace('\n', ' ')
        
        # Allow up to 200 characters between ESOP and the currency value
        pattern1 = r'ESOP(?:.{0,200}?)(?:INR|Rs\.?|₹|Rs)\s*([\d,]{4,})'
        pattern2 = r'ESAR(?:.{0,200}?)(?:INR|Rs\.?|₹|Rs)\s*([\d,]{4,})'
        
        for pat in [pattern1, pattern2]:
            match = re.search(pat, clean_text, re.IGNORECASE)
            if match:
                raw_val = match.group(1).replace(',', '').strip()
                try:
                    return float(raw_val), 0.8, "text_proximity"
                except ValueError:
                    pass
                    
        return None, 0.0, "missing"
