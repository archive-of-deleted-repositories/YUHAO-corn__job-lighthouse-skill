#!/usr/bin/env python3
"""Dependency-free client for the public Job Lighthouse API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

DEFAULT_API = "https://job-lighthouse.godcorn001.workers.dev/api"
VERSION = "0.1.0"


def config_path() -> Path:
    root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "job-lighthouse" / "config.json"


def load_config() -> dict[str, Any]:
    path = config_path()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            return value
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}


def save_config(value: dict[str, Any]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def telemetry_enabled(config: dict[str, Any]) -> bool:
    env = os.environ.get("JOB_LIGHTHOUSE_TELEMETRY", "").strip().lower()
    if env in {"0", "false", "off", "no"}:
        return False
    if env in {"1", "true", "on", "yes"}:
        return True
    return config.get("telemetry", True) is not False


class Client:
    def __init__(self) -> None:
        self.config = load_config()
        self.base_url = os.environ.get("JOB_LIGHTHOUSE_API_URL", DEFAULT_API).rstrip("/")
        self.install_id = str(self.config.get("install_id") or uuid.uuid4())
        if "install_id" not in self.config:
            self.config["install_id"] = self.install_id
            self.config.setdefault("telemetry", True)
            save_config(self.config)

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None, *, include_visitor: bool = True) -> Any:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": f"job-lighthouse-skill/{VERSION}",
            "x-job-lighthouse-client": "skill",
        }
        if include_visitor:
            headers["x-job-lighthouse-visitor"] = self.install_id
        request = urllib.request.Request(
            f"{self.base_url}/{path.lstrip('/')}",
            data=body,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(detail).get("error", detail)
            except json.JSONDecodeError:
                message = detail
            raise RuntimeError(f"Job Lighthouse API {error.code}: {message}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Cannot reach Job Lighthouse API: {error.reason}") from error

    def emit(self, event: str) -> bool:
        if not telemetry_enabled(self.config):
            return False
        try:
            self.request("POST", "telemetry", {"channel": "skill", "event": event}, include_visitor=False)
            return True
        except RuntimeError:
            return False

    def ensure_install_event(self) -> None:
        if self.config.get("install_reported") or not telemetry_enabled(self.config):
            return
        if self.emit("install"):
            self.config["install_reported"] = True
            save_config(self.config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search public jobs through Job Lighthouse")
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search with a natural-language requirement")
    search.add_argument("query", help="Complete natural-language job requirement")
    search.add_argument("--limit", type=int, default=40, choices=range(1, 101), metavar="1-100")
    search.add_argument("--no-ai", action="store_true", help="Use deterministic ranking only")
    search.add_argument("--json", action="store_true", help="Print the full JSON response")

    for command in ("health", "stats"):
        item = sub.add_parser(command, help=f"Show platform {command}")
        item.add_argument("--json", action="store_true")

    telemetry = sub.add_parser("telemetry", help="Show or change anonymous telemetry")
    telemetry.add_argument("mode", choices=("status", "on", "off"), nargs="?", default="status")
    return parser


def print_search(value: dict[str, Any]) -> None:
    ai = value.get("ai") or {}
    print(f"找到 {value.get('count', 0)} 个候选 · AI {'已使用' if ai.get('used') else '未使用'}")
    if ai.get("summary"):
        print(f"\n摘要：{ai['summary']}")
    ai_jobs = {item.get("jobId"): item for item in ai.get("jobs", []) if isinstance(item, dict)}
    for index, item in enumerate(value.get("results", []), 1):
        job = item.get("job") or {}
        analysis = ai_jobs.get(job.get("id"), {})
        print(f"\n{index}. [{item.get('score', 0)}] {job.get('title', '未命名')} · {job.get('company', '')} · {job.get('locationText', '')}")
        reason = analysis.get("matchReason") or "、".join(item.get("evidence", [])[:5])
        if reason:
            print(f"   匹配：{reason}")
        risks = list(dict.fromkeys((analysis.get("risks") or []) + (item.get("risks") or [])))
        if risks:
            print(f"   风险：{'；'.join(risks[:3])}")
        if job.get("url"):
            print(f"   原文：{job['url']}")


def main() -> int:
    args = build_parser().parse_args()
    client = Client()

    if args.command == "telemetry":
        if args.mode != "status":
            client.config["telemetry"] = args.mode == "on"
            if args.mode == "on":
                client.config.pop("install_reported", None)
            save_config(client.config)
        print("on" if telemetry_enabled(client.config) else "off")
        return 0

    client.ensure_install_event()
    client.emit("invoke")
    try:
        if args.command == "search":
            result = client.request("POST", "search", {"query": args.query, "ai": not args.no_ai, "limit": args.limit})
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print_search(result)
        else:
            result = client.request("GET", args.command)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(" · ".join(f"{key}: {value}" for key, value in result.items()))
        return 0
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
