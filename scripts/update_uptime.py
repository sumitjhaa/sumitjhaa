"""
Computes time-since-birth-date "uptime" and updates README.md in place.
Replaces text between <!--UPTIME--> and <!--/UPTIME--> markers.
"""
import re
from datetime import date
from pathlib import Path

# --- EDIT THIS to your actual birth date ---
BIRTH_DATE = date(2000, 7, 24)  # 24 July 2000
# --------------------------------------------

README_PATH = Path("README.md")
START_MARKER = "<!--UPTIME-->"
END_MARKER = "<!--/UPTIME-->"


def calculate_uptime(birth: date, today: date) -> str:
    years = today.year - birth.year
    months = today.month - birth.month
    days = today.day - birth.day

    if days < 0:
        months -= 1
        # days in previous month
        prev_month = today.month - 1 or 12
        prev_year = today.year if today.month != 1 else today.year - 1
        days_in_prev_month = (date(prev_year, prev_month % 12 + 1, 1) - date(prev_year, prev_month, 1)).days
        days += days_in_prev_month

    if months < 0:
        years -= 1
        months += 12

    return f"{years} years, {months} months, {days} days"


def update_readme():
    text = README_PATH.read_text(encoding="utf-8")
    uptime_str = calculate_uptime(BIRTH_DATE, date.today())

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    replacement = f"{START_MARKER}{uptime_str}{END_MARKER}"

    if not pattern.search(text):
        raise ValueError(
            f"Markers {START_MARKER} / {END_MARKER} not found in README.md"
        )

    new_text = pattern.sub(replacement, text)

    if new_text != text:
        README_PATH.write_text(new_text, encoding="utf-8")
        print(f"Updated uptime to: {uptime_str}")
    else:
        print("Uptime unchanged, no write needed.")


if __name__ == "__main__":
    update_readme()