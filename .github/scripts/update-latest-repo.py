import os
import re
import requests

USERNAME = "Yaroslav-Repos"
README_PATH = "README.md"

START_MARKER = "<!-- LATEST_REPOS:START -->"
END_MARKER = "<!-- LATEST_REPOS:END -->"

token = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Отримуємо всі репозиторії користувача/організації
repos = []
page = 1

while True:
    response = requests.get(
        f"https://api.github.com/users/{USERNAME}/repos",
        headers=headers,
        params={
            "per_page": 100,
            "page": page,
            "type": "owner",
        },
    )
    response.raise_for_status()

    data = response.json()

    if not data:
        break

    repos.extend(data)
    page += 1

# ВАЖЛИВО:
# created_at = дата створення репозиторію
# НЕ pushed_at = дата останнього push
repos.sort(
    key=lambda repo: repo["created_at"],
    reverse=True,
)

# За потреби виключаємо спеціальний .github repository
repos = [
    repo for repo in repos
    if repo["name"] != ".github"
]

if not repos:
    raise RuntimeError("No repositories found.")

latest = repos[0]

latest_block = f"""<!-- LATEST_REPOS:START -->
**[{latest["name"]}]({latest["html_url"]})**
<!-- LATEST_REPOS:END -->"""

with open(README_PATH, "r", encoding="utf-8") as file:
    readme = file.read()

pattern = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)

if not pattern.search(readme):
    raise RuntimeError(
        "Could not find LATEST_REPOS markers in README.md"
    )

updated_readme = pattern.sub(latest_block, readme, count=1)

if updated_readme == readme:
    print("README is already up to date.")
    exit(0)

with open(README_PATH, "w", encoding="utf-8") as file:
    file.write(updated_readme)

print(f"Latest project: {latest['name']}")
print(f"Created at: {latest['created_at']}")
