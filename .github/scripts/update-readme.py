#!/usr/bin/env python3
import os
import requests
from datetime import datetime

README_TPL = """# CBNG Trained Datasets

This repo contains datasets generated from the latest reviewed edits.

## Datasets

| Name | Assets | Comparator Results |
| ---- | ------ | ------------------ |
"""


def get_releases(org, repo):
    page = 1
    results = []

    while True:
        gh_token = os.environ.get("GITHUB_TOKEN", "")
        r = requests.get(
            f"https://api.github.com/repos/{org}/{repo}/releases",
            headers={"Authorization": f"token {gh_token}"},
            params={"per_page": 100, "page": page},
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break

        results.extend(data)
        page += 1

    return results


def build_assests_string(release):
    return " ".join([
        f'[{asset["name"]}]({asset["browser_download_url"]})'
        for asset in sorted(release["assets"], key=lambda a: (a["name"].split("/")[0],
                                                              a["name"]))
        if not asset["name"].endswith("-comparator.md")
    ])


def build_comparator_string(release):
    return " ".join([
        f'[{asset["name"].split("/")[0]}]({asset["browser_download_url"]})'
        for asset in sorted(release["assets"], key=lambda a: a["name"].split("/")[0])
        if asset["name"].endswith("-comparator.md")
    ])


def main():
    readme_str = README_TPL

    for release in sorted(
        get_releases("cluebotng", "trained-datasets"),
        key=lambda r: datetime.strptime(r["published_at"], "%Y-%m-%dT%H:%M:%SZ"),
        reverse=True,
    ):
        readme_str += f'| [{release["tag_name"]}]({release["html_url"]}) '
        readme_str += f"| {build_assests_string(release)} "
        readme_str += f"| {build_comparator_string(release)} |\n"

    with open("README.md", "w") as fh:
        fh.write(readme_str)


if __name__ == "__main__":
    main()
