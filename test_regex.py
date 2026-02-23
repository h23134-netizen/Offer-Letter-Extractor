import re

text = """
Retention Bonus:
" In addition to the above, you will be entitled to an INR 100000 as a Retention Bonus, which will be paid upon completing 12 months of employment in the following month's payroll.
Furthermore, an additional amount of INR 150000 as a Retention Bonus will be paid upon completion of 24 months of employment in the following month's payroll."
Each payment will have a clawback of 12 months from the date of disbursement.

ESOP:

"You are also entitled to the ESOP program at InsuranceDekho and will be offered ESOPs and ESARs worth total of INR 500000 at Fair Market Value as on the date of the grant. The Vesting schedule shall be over a period of 4 years in the ratio of 10:30:30:30 from the date of grant.

The exercise price per option will be equal to the fair market value per share as on the grant date, as determined by the company's Board of Directors in good faith. All the other terms and conditions will be subsequently shared with you.

Note: You shall receive a grant letter post joining as per the forthcoming grant cycle. The terms and conditions of the grant shall be governed by the respective ESOP/ESAR plan."
"""

clean_text = text.replace('\n', ' ')

print("Testing Retention Bonus:")
bonus_type = "Retention"
pattern1 = rf'{bonus_type}\s*Bonus[^\d]+(?:INR|Rs\.?)\s*([\d,]+)'
pattern2 = rf'(?:INR|Rs\.?)\s*([\d,]+)[^\d]+?{bonus_type}\s*Bonus'

match = re.search(pattern1, clean_text, re.IGNORECASE)
if match: print("Pattern 1 matched:", match.group(1))
else: print("Pattern 1 failed")

match2 = re.search(pattern2, clean_text, re.IGNORECASE)
if match2: print("Pattern 2 matched:", match2.group(1))
else: print("Pattern 2 failed")

print("\nTesting ESOP:")
match_esop = re.search(r'ESOP[^\d]{1,100}?(?:INR|Rs\.?)\s*([\d,]+)', clean_text, re.IGNORECASE)
if match_esop: print("ESOP matched:", match_esop.group(1))
else: print("ESOP failed")

match_esop2 = re.search(r'ESOP.*?(?:INR|Rs\.?)\s*([\d,]+)', clean_text, re.IGNORECASE)
if match_esop2: print("ESOP fallback matched:", match_esop2.group(1))
