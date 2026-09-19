#!/usr/bin/env python3
"""
check.py — 레포 정합성 검증. CI 는 이 파일 하나만 돌린다
===========================================================================
    python tools/check.py
    python tools/check.py --skip-python     # 알고리즘 템플릿 실행 생략 (빠름)

검사 항목
    1 링크    md·html 의 상대 링크 대상 파일이 존재하는가
    2 앵커    html 의 #앵커 대상 id 가 존재하는가
    3 씬      visualize 의 data-steps ↔ data-cap 개수, data-at/from/until 범위
    4 태그    html 태그 균형
    5 노트    notes/**/*.md frontmatter 필수 키와 값 형식
    6 규약    status: done 인 노트에 "30초 답변", "꼬리질문" 섹션이 있는가
    7 퀴즈    visualize/quiz-data.js 가 현재 노트와 일치하는가 (폰용 페이지 데이터)
    8 파이썬  algorithm/templates/*.py 자체 검증 통과

문제가 하나라도 있으면 exit 1.
다른 도구보다 길지만, 레포가 썩는 걸 막는 유일한 장치라 한 파일에 모아둔다.
===========================================================================
"""

import argparse
import re
import subprocess
import sys
from html.parser import HTMLParser

from _common import (DATE_RE, INTERVALS, LEVELS, REQUIRED, ROOT, STATUSES,
                     TOPICS, iter_notes, read_text, rel)

SKIP_DIRS = {".git", "node_modules", ".github"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}

MD_LINK = re.compile(r"\]\(\s*([^)\s]+?)\s*\)")
HTML_LINK = re.compile(r'(?:href|src)="([^"]+)"')


def walk(pattern):
    for path in sorted(ROOT.rglob(pattern)):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "mailto:", "data:", "#", "//"))


# ---------------------------------------------------------------------------
# 1, 2 링크와 앵커
# ---------------------------------------------------------------------------

def check_links_and_anchors():
    problems = []
    targets = [(p, MD_LINK) for p in walk("*.md")] + \
              [(p, HTML_LINK) for p in walk("*.html")]

    for path, pattern in targets:
        text = read_text(path)
        for link in pattern.findall(text):
            if is_external(link):
                continue
            path_part, _, anchor = link.partition("#")
            if not path_part:
                continue
            target = (path.parent / path_part).resolve()
            if not target.exists():
                problems.append(f"링크 끊김  {rel(path)} -> {link}")
                continue
            if anchor and target.suffix == ".html":
                if f'id="{anchor}"' not in read_text(target):
                    problems.append(f"앵커 없음  {rel(path)} -> {link}")
    return problems


# ---------------------------------------------------------------------------
# 3 씬 정합성 (scene.js 규약)
# ---------------------------------------------------------------------------

SCENE_HEAD = re.compile(
    r'<section class="scene"[^>]*data-scene="([^"]+)"[^>]*data-steps="(\d+)"')


def check_scenes():
    problems = []
    for path in walk("*.html"):
        text = read_text(path)
        for m in SCENE_HEAD.finditer(text):
            name, steps = m.group(1), int(m.group(2))
            nxt = text.find('<section class="scene"', m.end())
            block = text[m.end():nxt if nxt != -1 else len(text)]

            caps = sorted(int(c) for c in re.findall(r'data-cap="(\d+)"', block))
            if caps != list(range(1, steps + 1)):
                problems.append(
                    f"캡션 불일치  {rel(path)} scene={name} "
                    f"steps={steps} caps={caps}")

            for attr in ("data-at", "data-from", "data-until"):
                for value in re.findall(attr + r'="([^"]+)"', block):
                    for num in re.findall(r"\d+", value):
                        if int(num) > steps:
                            problems.append(
                                f"단계 초과  {rel(path)} scene={name} "
                                f"{attr}={value} > {steps}")
    return problems


# ---------------------------------------------------------------------------
# 4 html 태그 균형
# ---------------------------------------------------------------------------

class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> 짝 없음")
            return
        top, line = self.stack.pop()
        if top != tag:
            self.errors.append(
                f"line {self.getpos()[0]}: </{tag}> 인데 <{top}> 가 열려 있다 "
                f"(line {line})")


def check_html_balance():
    problems = []
    for path in walk("*.html"):
        parser = Balance()
        parser.feed(read_text(path))
        for err in parser.errors[:5]:
            problems.append(f"태그 불균형  {rel(path)} {err}")
        if parser.stack:
            left = ", ".join(t for t, _ in parser.stack)
            problems.append(f"태그 미닫힘  {rel(path)} [{left}]")
    return problems


# ---------------------------------------------------------------------------
# 5, 6 노트 frontmatter 와 섹션 규약
# ---------------------------------------------------------------------------

HAS_SCRIPT = re.compile(r"^#{1,3}[^\n]*30초 답변", re.MULTILINE)
HAS_FOLLOWUP = re.compile(r"^#{1,3}[^\n]*꼬리질문", re.MULTILINE)


def check_notes():
    problems = []
    for path, meta, body in iter_notes():
        name = rel(path)
        if meta is None:
            problems.append(f"frontmatter 없음  {name}  (tools/new.py 로 생성하세요)")
            continue

        for key in REQUIRED:
            if key not in meta:
                problems.append(f"필수 키 누락  {name}  '{key}'")

        topic = meta.get("topic")
        expected = path.parent.name
        if topic and topic != expected:
            problems.append(f"topic 불일치  {name}  topic={topic} 인데 폴더는 {expected}")
        if expected not in TOPICS:
            problems.append(f"미등록 분류  {name}  '{expected}' (tools/_common.py TOPICS)")

        level = meta.get("level")
        if level and level not in LEVELS:
            problems.append(f"level 값 오류  {name}  '{level}' not in {LEVELS}")

        status = meta.get("status")
        if status and status not in STATUSES:
            problems.append(f"status 값 오류  {name}  '{status}' not in {STATUSES}")

        conf = meta.get("confidence")
        if conf is not None and conf not in INTERVALS:
            problems.append(f"confidence 범위  {name}  {conf} (1~5)")

        date = meta.get("last_reviewed")
        if date and not DATE_RE.match(str(date)):
            problems.append(f"날짜 형식  {name}  '{date}' (YYYY-MM-DD)")

        if not str(meta.get("title", "")).strip():
            problems.append(f"title 비어 있음  {name}")

        # 규약: 완성된 노트는 암기용 30초 답변과 퀴즈용 꼬리질문을 갖는다
        if status == "done":
            if not HAS_SCRIPT.search(body):
                problems.append(f"섹션 누락  {name}  '30초 답변'")
            if not HAS_FOLLOWUP.search(body):
                problems.append(f"섹션 누락  {name}  '꼬리질문'")
    return problems


# ---------------------------------------------------------------------------
# 7 알고리즘 템플릿 자체 검증
# ---------------------------------------------------------------------------

def check_quiz_data():
    """visualize/quiz-data.js 가 현재 노트와 일치하는지.

    폰용 퀴즈 페이지는 이 파일을 읽는다. 노트를 고치고 다시 굽지 않으면
    폰에서는 옛 문항이 나온다. 조용히 어긋나는 종류라 여기서 막는다.
    """
    import build_quiz

    if not build_quiz.OUT.exists():
        return [f"퀴즈 데이터 없음  {rel(build_quiz.OUT)}  "
                f"(python tools/build_quiz.py)"]
    expected = build_quiz.render(build_quiz.current_generated())
    if read_text(build_quiz.OUT) != expected:
        return ["퀴즈 데이터 낡음  노트와 quiz-data.js 가 다릅니다  "
                "(python tools/build_quiz.py)"]
    return []


def check_python():
    problems = []
    templates = ROOT / "algorithm" / "templates"
    if not templates.exists():
        return problems
    for path in sorted(templates.glob("*.py")):
        if not path.name[0].isdigit():
            continue
        proc = subprocess.run([sys.executable, str(path)],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-1:]
            problems.append(f"템플릿 실패  {rel(path)}  {' '.join(tail)}")
    return problems


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="레포 정합성 검증")
    ap.add_argument("--skip-python", action="store_true",
                    help="algorithm/templates 실행을 생략한다")
    args = ap.parse_args()

    stages = [
        ("링크·앵커", check_links_and_anchors),
        ("씬 정합성", check_scenes),
        ("html 태그", check_html_balance),
        ("노트 규약", check_notes),
        ("퀴즈 데이터", check_quiz_data),
    ]
    if not args.skip_python:
        stages.append(("파이썬 템플릿", check_python))

    total = []
    for label, fn in stages:
        found = fn()
        mark = "FAIL" if found else " OK "
        print(f"[{mark}] {label}" + (f"  ({len(found)}건)" if found else ""))
        total.extend(found)

    if total:
        print()
        for line in total:
            print("  -", line)
        print(f"\n문제 {len(total)}건")
        return 1

    print("\n전부 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
