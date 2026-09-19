#!/usr/bin/env python3
"""
quiz.py — 노트의 꼬리질문 체크리스트를 랜덤 출제한다
===========================================================================
    python tools/quiz.py                    전체에서 5문제
    python tools/quiz.py -n 10              10문제
    python tools/quiz.py --topic infra      분류 지정
    python tools/quiz.py --weak             confidence 2 이하인 노트만
    python tools/quiz.py --list             출제 없이 목록만
    python tools/quiz.py --auto             Enter 안 기다리고 답까지 바로 출력

읽는 것과 답하는 것은 효과가 다르다. 노트를 다시 읽지 말고 이걸 돌린다.

출제 소스
    `## ... 꼬리질문 ...` 제목 아래의  `- [ ] 질문 (→ 답 힌트)`  항목.
    `(→ ...)` 부분은 힌트로 분리해서 Enter 를 누를 때 보여준다.
===========================================================================
"""

import argparse
import random
import re
import sys

from _common import iter_notes, rel

HEADING = re.compile(r"^(#{1,6})[^\n]*꼬리질문[^\n]*$", re.MULTILINE)
ANY_HEADING = re.compile(r"^#{1,6} ", re.MULTILINE)
ITEM = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+?)\s*$", re.MULTILINE)
CLEAN = re.compile(r"[*`]")


def extract(body: str, source: str):
    """꼬리질문 섹션에서 (질문, 힌트, 출처) 를 뽑는다."""
    out = []
    for head in HEADING.finditer(body):
        start = head.end()
        nxt = ANY_HEADING.search(body, start)
        section = body[start:nxt.start() if nxt else len(body)]
        for raw in ITEM.findall(section):
            line = CLEAN.sub("", raw).strip()
            if not line:
                continue
            question, hint = line, ""
            m = re.search(r"\(\s*→\s*(.+?)\)\s*$", line)
            if m:
                question = line[:m.start()].strip()
                hint = m.group(1).strip()
            if question:
                out.append((question, hint, source))
    return out


def collect(topic=None, weak=False):
    pool = []
    for path, meta, body in iter_notes():
        if meta is None:
            continue
        if topic and meta.get("topic") != topic:
            continue
        if weak and meta.get("confidence", 1) > 2:
            continue
        pool.extend(extract(body, rel(path)))
    return pool


def main() -> int:
    ap = argparse.ArgumentParser(description="꼬리질문 랜덤 출제")
    ap.add_argument("-n", "--count", type=int, default=5)
    ap.add_argument("--topic")
    ap.add_argument("--weak", action="store_true",
                    help="confidence 2 이하인 노트만")
    ap.add_argument("--list", action="store_true", help="출제 없이 목록만")
    ap.add_argument("--auto", action="store_true",
                    help="Enter 를 기다리지 않고 힌트까지 바로 출력")
    ap.add_argument("--seed", type=int, help="같은 문제를 다시 뽑을 때")
    args = ap.parse_args()

    pool = collect(args.topic, args.weak)
    if not pool:
        print("출제할 꼬리질문이 없습니다.")
        print("노트의 '꼬리질문 체크리스트' 에 `- [ ] 질문 (→ 힌트)` 형식으로 채우세요.")
        return 0

    if args.seed is not None:
        random.seed(args.seed)

    if args.list:
        for question, hint, source in pool:
            suffix = f"  (→ {hint})" if hint else ""
            print(f"- {question}{suffix}   [{source}]")
        print(f"\n총 {len(pool)}문항")
        return 0

    picked = random.sample(pool, min(args.count, len(pool)))
    interactive = sys.stdin.isatty() and not args.auto

    print(f"전체 {len(pool)}문항 중 {len(picked)}문항\n"
          + ("소리 내어 답하고 Enter 를 누르세요.\n" if interactive else ""))

    for i, (question, hint, source) in enumerate(picked, start=1):
        print(f"Q{i}. {question}")
        if interactive:
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print("\n중단")
                return 0
        if hint:
            print(f"    → {hint}")
        print(f"    출처: {source}\n")

    print("막힌 문항이 있으면 그 노트의 confidence 를 낮추세요.")
    print("  python tools/review.py <노트경로> -c 2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
