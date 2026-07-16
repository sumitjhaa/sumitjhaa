"""
Estimates Lines of Code using GitHub Languages API (bytes per language).
Much faster than cloning repos — runs in seconds.
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

# Average bytes per line of code (varies by language, ~50 is reasonable)
BYTES_PER_LINE = 50


def get_json(url):
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def list_repos():
    repos, page = [], 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}",
            headers=HEADERS,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_repo_languages(repo_name):
    data = get_json(f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages")
    return data


def format_bytes(n):
    if n < 1024:
        return f"{n} B"
    elif n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    else:
        return f"{n / (1024 * 1024):.1f} MB"


def format_lines(n):
    if n < 1000:
        return str(n)
    elif n < 1_000_000:
        return f"{n / 1000:.1f}K"
    else:
        return f"{n / 1_000_000:.1f}M"


def replace_between(text, start_marker, end_marker, new_value):
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)
    if not pattern.search(text):
        raise ValueError(f"Markers {start_marker}/{end_marker} not found")
    return pattern.sub(f"{start_marker}{new_value}{end_marker}", text)


def main():
    repos = list_repos()
    total_bytes = 0
    non_fork_count = 0

    for repo in repos:
        if repo.get("fork"):
            continue
        non_fork_count += 1
        try:
            langs = get_repo_languages(repo["name"])
            for lang, bytes_count in langs.items():
                total_bytes += bytes_count
                print(f"  {repo['name']}/{lang}: {format_bytes(bytes_count)}")
        except Exception as e:
            print(f"  {repo['name']}: skipped ({e})")

    total_lines = total_bytes // BYTES_PER_LINE

    loc_line = f"{format_lines(total_lines)} lines ({format_bytes(total_bytes)})"

    text = README_PATH.read_text(encoding="utf-8")
    text = replace_between(text, "<!--LOC_START-->", "<!--LOC_END-->", loc_line)
    README_PATH.write_text(text, encoding="utf-8")
    print(f"\nTotal: {format_bytes(total_bytes)} -> ~{format_lines(total_lines)} lines")
    print(f"LOC -> {loc_line}")


if __name__ == "__main__":
    main()
