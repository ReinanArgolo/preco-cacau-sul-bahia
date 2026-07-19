from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx


def issue_title(source: str) -> str:
    return f"Falha de coleta: {source}"


class GitHubIssues:
    def __init__(self, repository: str, token: str) -> None:
        self.base = f"https://api.github.com/repos/{repository}"
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30,
        )

    def find(self, title: str, state: str = "all") -> dict | None:
        response = self.client.get(f"{self.base}/issues", params={"state": state, "per_page": 100})
        response.raise_for_status()
        return next((item for item in response.json() if item["title"] == title), None)

    def report_failure(self, source: str, message: str, run_url: str) -> None:
        title = issue_title(source)
        body = f"A coleta de **{source}** falhou.\n\nMensagem sanitizada: `{message[:500]}`\n\nExecução: {run_url}"
        existing = self.find(title)
        if existing:
            self.client.patch(
                f"{self.base}/issues/{existing['number']}",
                json={"state": "open", "body": body},
            ).raise_for_status()
        else:
            self.client.post(f"{self.base}/issues", json={"title": title, "body": body}).raise_for_status()

    def close_recovered(self, source: str) -> None:
        existing = self.find(issue_title(source), state="open")
        if existing:
            self.client.post(
                f"{self.base}/issues/{existing['number']}/comments",
                json={"body": "A fonte voltou a responder nesta execução. Fechamento automático."},
            ).raise_for_status()
            self.client.patch(
                f"{self.base}/issues/{existing['number']}", json={"state": "closed"}
            ).raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("status_file", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.status_file.read_text(encoding="utf-8"))
    failures = {item["source"]: item["message"] for item in payload.get("failures", [])}
    github = GitHubIssues(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])
    run_url = (
        f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/"
        f"{os.environ['GITHUB_RUN_ID']}"
    )
    for source, message in failures.items():
        github.report_failure(source, message, run_url)
    for source in payload.get("sources", {}):
        if source not in failures:
            github.close_recovered(source)


if __name__ == "__main__":
    main()
