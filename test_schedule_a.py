from backend.extractor.field_parser import FieldParser

test_string = """
Name Debayan Debnath
Designation Management Trainee
Entity GFPL
Business Unit Enabling Functions
Department Human Resources
Sub-Department Generalist
Competency Shared (HR - Generalist)
Band 2
Grade 2.2
"""

parser = FieldParser()
print(parser._extract_schedule_a_fields(test_string))
