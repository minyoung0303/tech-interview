#!/usr/bin/env python3
"""
build_quiz.py — 노트의 꼬리질문을 폰용 퀴즈 페이지 데이터로 굽는다
===========================================================================
    python tools/build_quiz.py

노트를 고쳤으면 이걸 한 번 돌린다. 안 돌리면 tools/check.py 가 잡아준다.

왜 JSON 이 아니라 .js 인가
    fetch() 는 file:// 에서 CORS 로 막힌다. <script src> 는 막히지 않는다.
    그래서 window.QUIZ_DATA 를 담은 js 로 굽는다 →
    GitHub Pages 에서도, 로컬에서 html 을 그냥 열어도, 비행기 모드에서도 동작한다.

출력: visualize/quiz-data.js  (자동 생성. 직접 고치지 않는다)
===========================================================================
"""

import datetime
import json
import re
import subprocess
import sys

from _common import ROOT, extract_questions, iter_notes, rel, write_text

OUT = ROOT / "visualize" / "quiz-data.js"

HEADER = ("/* 자동 생성 파일입니다. 직접 고치지 마세요.\n"
          "   노트를 고친 뒤:  python tools/build_quiz.py  */\n")


def blob_base() -> str:
    """출처 링크를 GitHub blob 으로 건다. 폰에서 md 가 예쁘게 렌더링된다.
    git remote 가 없으면 상대 경로로 떨어진다(원문 그대로 보임).
    """
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"],
                             cwd=ROOT, capture_output=True, text=True,
                             timeout=5).stdout.strip()
    except Exception:
        return ""
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    if not m:
        return ""
    return f"https://github.com/{m.group(1)}/blob/main/"


def build() -> dict:
    notes = []
    items = []
    for path, meta, body in iter_notes():
        if meta is None:
            continue
        src = rel(path)
        entry = {
            "path": src,
            "topic": meta.get("topic", "?"),
            "title": meta.get("title", src),
            "level": meta.get("level", "core"),
            "status": meta.get("status", "todo"),
            "confidence": meta.get("confidence", 1),
        }
        found = extract_questions(body)
        entry["count"] = len(found)
        notes.append(entry)
        for question, hint in found:
            items.append({
                "q": question,
                "hint": hint,
                "topic": entry["topic"],
                "title": entry["title"],
                "confidence": entry["confidence"],
                "src": src,
            })
    return {"notes": notes, "items": items}


def render(generated: str) -> str:
    data = build()
    data = {"generated": generated, "blob": blob_base(), **data}
    body = json.dumps(data, ensure_ascii=False, indent=1)
    return f"{HEADER}window.QUIZ_DATA = {body};\n"


def current_generated() -> str:
    """기존 파일의 generated 값을 읽는다. 없으면 오늘 날짜."""
    if OUT.exists():
        m = re.search(r'"generated"\s*:\s*"([^"]+)"',
                      OUT.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return datetime.date.today().isoformat()


def main() -> int:
    data = build()
    text = render(datetime.date.today().isoformat())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_text(OUT, text)

    by_topic = {}
    for item in data["items"]:
        by_topic[item["topic"]] = by_topic.get(item["topic"], 0) + 1

    print(f"생성: {rel(OUT)}")
    print(f"  노트 {len(data['notes'])}개 / 문항 {len(data['items'])}개")
    for topic in sorted(by_topic):
        print(f"    {topic:<10} {by_topic[topic]}문항")
    empty = [n["path"] for n in data["notes"] if n["count"] == 0]
    if empty:
        print("  꼬리질문이 없는 노트:")
        for path in empty:
            print(f"    {path}")
    print("\n폰에서:  <Pages URL>/visualize/quiz.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
