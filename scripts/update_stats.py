"""
Fetches GitHub stats and writes them into README.md between markers.
Requires env var GITHUB_TOKEN.
"""
import os
import re
import requests
from pathlib import Path

USERNAME = "sumitjhaa"
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}
README_PATH = Path("README.md")


def get_json(url, headers=None):
    r = requests.get(url, headers=headers or HEADERS)
    r.raise_for_status()
    return r.json()


def get_user_summary():
    data = get_json(f"https://api.github.com/users/{USERNAME}")
    return {
        "public_repos": data["public_repos"],
        "followers": data["followers"],
    }


def get_total_stars():
    stars = 0
    page = 1
    while True:
        repos = get_json(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
        )
        if not repos:
            break
        stars += sum(r["stargazers_count"] for r in repos)
        page += 1
    return stars


def get_commit_count_approx():
    url = f"https://api.github.com/search/commits?q=author:{USERNAME}"
    search_headers = {**HEADERS, "Accept": "application/vnd.github.cloak-preview+json"}
    data = get_json(url, headers=search_headers)
    return data.get("total_count", 0)


def get_pr_count():
    data = get_json(
        f"https://api.github.com/search/issues?q=author:{USERNAME}+type:pr"
    )
    return data.get("total_count", 0)


def get_issue_count():
    data = get_json(
        f"https://api.github.com/search/issues?q=author:{USERNAME}+type:issue"
    )
    return data.get("total_count", 0)


def get_top_languages():
    lang_count = {}
    page = 1
    while True:
        repos = get_json(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
        )
        if not repos:
            break
        for r in repos:
            if r.get("fork"):
                continue
            lang = r.get("language")
            if lang:
                lang_count[lang] = lang_count.get(lang, 0) + 1
        page += 1
    sorted_langs = sorted(lang_count.items(), key=lambda x: -x[1])[:5]
    return ", ".join(l[0] for l in sorted_langs) if sorted_langs else "N/A"


def replace_between(text, start_marker, end_marker, new_value):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"Markers {start_marker}/{end_marker} not found")
    return pattern.sub(f"{start_marker}{new_value}{end_marker}", text)


def main():
    text = README_PATH.read_text(encoding="utf-8")

    summary = get_user_summary()
    stars = get_total_stars()
    commits = get_commit_count_approx()
    prs = get_pr_count()
    issues = get_issue_count()
    langs = get_top_languages()

    text = replace_between(text, "<!--REPOS-->", "<!--/REPOS-->", str(summary['public_repos']))
    text = replace_between(text, "<!--STARS-->", "<!--/STARS-->", str(stars))
    text = replace_between(text, "<!--COMMITS-->", "<!--/COMMITS-->", f"{commits:,}")
    text = replace_between(text, "<!--FOLLOWERS-->", "<!--/FOLLOWERS-->", str(summary['followers']))
    text = replace_between(text, "<!--PR_ISSUES-->", "<!--/PR_ISSUES-->", f"{prs:,}")
    text = replace_between(text, "<!--ISSUES-->", "<!--/ISSUES-->", f"{issues:,}")
    text = replace_between(text, "<!--LANGUAGES-->", "<!--/LANGUAGES-->", langs)

    README_PATH.write_text(text, encoding="utf-8")
    print(f"Repos -> {summary['public_repos']}")
    print(f"Stars -> {stars}")
    print(f"Commits -> {commits:,}")
    print(f"Followers -> {summary['followers']}")
    print(f"PRs -> {prs:,}")
    print(f"Issues -> {issues:,}")
    print(f"Languages -> {langs}")


if __name__ == "__main__":
    main()
