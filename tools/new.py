#!/usr/bin/env python3
"""
new.py — 정해진 포맷으로 새 노트를 만든다
===========================================================================
    python tools/new.py network http
    python tools/new.py database lock --title "락과 데드락" --level plus
    python tools/new.py --topics                 # 사용할 수 있는 분류 보기

왜 필요한가
    포맷이 흔들리면 check.py 가 실패하고 quiz.py 가 파싱을 못 한다.
    그리고 빈 파일 앞에서 막막해지는 것도 없앤다. 저녁에 노트 하나 쓰기가 가벼워진다.

규약 (check.py 가 검사한다)
    frontmatter 필수 키  topic title level status confidence last_reviewed
    섹션                 "30초 답변" 과 "꼬리질문" 은 status: done 일 때 필수
===========================================================================
"""

import argparse
import datetime
import sys

from _common import LEVELS, NOTES, TOPICS, write_text

TEMPLATE = """---
topic: {topic}
title: {title}
level: {level}
status: todo
confidence: 1
last_reviewed: {today}
tags: []
asked_at: []
---

# {title}

> 기준:
> 한 줄 정의:

---

## 0. 30초 답변

> ""

---

## 1.

---

## 꼬리질문 체크리스트

> 아래 형식으로 채우면 터미널(tools/quiz.py)과 폰(visualize/quiz.html) 양쪽에서 출제된다.
> 빈 항목은 두지 않는다. 쓰레기 문항이 그대로 출제된다.
>
>     - [ ] 질문 내용? (→ 답 힌트)

---

## 자주 하는 실수

-
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="새 노트 생성")
    ap.add_argument("topic", nargs="?", help=f"분류 {TOPICS}")
    ap.add_argument("slug", nargs="?", help="파일명 (확장자 없이, 영문 소문자-하이픈)")
    ap.add_argument("--title", default="", help="노트 제목 (기본값: slug)")
    ap.add_argument("--level", default="core", choices=LEVELS)
    ap.add_argument("--topics", action="store_true", help="분류 목록만 출력")
    args = ap.parse_args()

    if args.topics:
        print("사용할 수 있는 분류:")
        for t in TOPICS:
            count = len(list((NOTES / t).glob("*.md"))) if (NOTES / t).exists() else 0
            print(f"  {t:<12} 노트 {count}개")
        return 0

    if not args.topic or not args.slug:
        ap.print_help()
        return 1

    if args.topic not in TOPICS:
        print(f"'{args.topic}' 는 등록되지 않은 분류입니다.")
        print(f"사용 가능: {', '.join(TOPICS)}")
        print("새 분류를 쓰려면 tools/_common.py 의 TOPICS 에 먼저 추가하세요.")
        return 1

    path = NOTES / args.topic / f"{args.slug}.md"
    if path.exists():
        print(f"이미 있습니다: {path.relative_to(NOTES.parent).as_posix()}")
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, TEMPLATE.format(
        topic=args.topic,
        title=args.title or args.slug,
        level=args.level,
        today=datetime.date.today().isoformat(),
    ))

    print(f"생성: {path.relative_to(NOTES.parent).as_posix()}")
    print("다 쓰면 frontmatter 의 status 를 done 으로 바꾸고 python tools/check.py 를 돌리세요.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
