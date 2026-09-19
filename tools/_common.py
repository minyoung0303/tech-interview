"""
_common.py — tools 전체가 공유하는 최소 유틸
===========================================================================
frontmatter 규약을 한 곳에만 둔다. 스키마를 바꿀 때 이 파일만 고치면 된다.
표준 라이브러리만 쓴다 (PyYAML 없이 `key: value` 와 `[a, b]` 만 지원).
===========================================================================
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"

# notes/ 하위에 허용하는 분류. 새로 추가하려면 여기에 적는다.
TOPICS = [
    "database",
    "network",
    "os",
    "ds-algo",
    "infra",
    "backend",
    "language",
    "etc",
]

# frontmatter 필수 키
REQUIRED = ["topic", "title", "level", "status", "confidence", "last_reviewed"]

LEVELS = ["core", "plus", "deep"]
STATUSES = ["todo", "drafting", "done"]

# confidence -> 복습 주기(일). 낮게 평가한 것을 자주 본다.
INTERVALS = {1: 2, 2: 2, 3: 5, 4: 12, 5: 30}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def read_text(path) -> str:
    """줄바꿈을 그대로 보존해서 읽는다 (CRLF/LF 섞임 방지)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write_text(path, text: str) -> None:
    """읽은 그대로 되돌려 쓴다. 줄바꿈을 변환하지 않는다."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def parse_frontmatter(text: str):
    """맨 앞 `---` 블록을 dict 로 돌려준다. 없으면 (None, text).

    지원 형식
        key: value
        key: [a, b, c]
    그 이상은 지원하지 않는다. 필요해지면 그때 늘린다.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text

    meta = {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        raw = lines[i].strip()
        if not raw or raw.startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, _, value = raw.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            meta[key] = [v.strip() for v in inner.split(",") if v.strip()]
        elif value.isdigit():
            meta[key] = int(value)
        else:
            meta[key] = value

    if end is None:
        return None, text
    return meta, "\n".join(lines[end + 1:])


def iter_notes():
    """notes/**/*.md 를 (경로, meta, 본문) 으로 순회한다. meta 는 None 일 수 있다."""
    if not NOTES.exists():
        return
    for path in sorted(NOTES.rglob("*.md")):
        text = read_text(path)
        meta, body = parse_frontmatter(text)
        yield path, meta, body


def rel(path) -> str:
    """레포 기준 상대 경로를 슬래시로 출력한다."""
    return pathlib.Path(path).resolve().relative_to(ROOT).as_posix()
