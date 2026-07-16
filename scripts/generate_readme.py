"""
Updates the README with fresh data markers.
"""
import re
from pathlib import Path
from datetime import date

README_PATH = Path("README.md")
BIRTH_DATE = date(2000, 7, 24)


def calculate_uptime(birth, today):
    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day
    if days < 0:
        months -= 1
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month != 1 else today.year - 1
        days_in_prev = (date(prev_year, prev_month % 12 + 1, 1) - date(prev_year, prev_month, 1)).days
        days += days_in_prev
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months, {days} days"


def main():
    text = README_PATH.read_text(encoding="utf-8")

    # Update uptime
    uptime = calculate_uptime(BIRTH_DATE, date.today())
    text = re.sub(
        r'(<!--UPTIME-->)(.*?)(<!--/UPTIME-->)',
        rf'\g<1>{uptime}\3',
        text
    )

    README_PATH.write_text(text, encoding="utf-8")
    print(f"Updated uptime: {uptime}")


if __name__ == "__main__":
    main()
