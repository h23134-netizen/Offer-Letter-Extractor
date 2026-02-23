from backend.extractor.field_parser import FieldParser

test_string = """
Name Debayan Debnath
Designation Management Trainee
Entity GFPL
Business Unit Enabling Functions
Department B2B
Sub-Department Generalist
Competency Field (B2B - M&H) 1
Band 1
Grade 1.4
"""

parser = FieldParser()
print(parser._extract_schedule_a_fields(test_string))
