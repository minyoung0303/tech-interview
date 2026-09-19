#!/usr/bin/env python3
"""
review.py — 오늘 복습할 노트를 뽑고, 복습 기록을 갱신한다
===========================================================================
    python tools/review.py                                  오늘 볼 것
    python tools/review.py --all                            전체 현황
    python tools/review.py --topic network                  분류만
    python tools/review.py notes/network/http.md -c 4       복습 완료 기록

복습 주기 (frontmatter 의 confidence 로 결정)
    1~2 -> 2일    3 -> 5일    4 -> 12일    5 -> 30일

기록은 md 의 frontmatter 에만 남는다. 별도 상태 파일이나 DB 를 만들지 않는다.
두 곳에 상태가 있으면 반드시 어긋나기 때문이다.
===========================================================================
"""

import argparse
import datetime
import pathlib
import re
import sys

from _common import (INTERVALS, ROOT, iter_notes, read_text, rel, write_text)

TODAY = datetime.date.today()


def parse_date(value):
    try:
        return datetime.date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def collect(topic=None):
    """(경로, meta, 경과일, 주기, 남은일) 목록."""
    rows = []
    for path, meta, _body in iter_notes():
        if meta is None:
            continue
        if topic and meta.get("topic") != topic:
            continue
        conf = meta.get("confidence", 1)
        interval = INTERVALS.get(conf, 2)
        last = parse_date(meta.get("last_reviewed"))
        elapsed = (TODAY - last).days if last else 9999
        rows.append((path, meta, elapsed, interval, interval - elapsed))
    return rows


def show_due(rows):
    due = [r for r in rows
           if r[1].get("status") != "todo" and r[4] <= 0]
    due.sort(key=lambda r: (r[1].get("confidence", 1), -r[2]))

    todo = [r for r in rows if r[1].get("status") == "todo"]

    if due:
        print(f"오늘 복습 ({len(due)}개)")
        for path, meta, elapsed, interval, _ in due:
            print(f"  [c{meta.get('confidence')}] {rel(path):<42} "
                  f"{elapsed:>3}일 경과  (주기 {interval}일)")
    else:
        print("오늘 복습할 노트가 없습니다. 새 노트를 쓰거나 알고리즘에 시간을 쓰세요.")

    if todo:
        print(f"\n아직 안 쓴 노트 ({len(todo)}개)")
        for path, meta, *_ in todo[:8]:
            print(f"  [todo] {rel(path):<42} {meta.get('title', '')}")
        if len(todo) > 8:
            print(f"  ... 외 {len(todo) - 8}개")

    print()
    summary(rows)
    if due:
        first = rel(due[0][0])
        print(f"\n복습을 끝냈으면:  python tools/review.py {first} -c 4")


def show_all(rows):
    by_topic = {}
    for row in rows:
        by_topic.setdefault(row[1].get("topic", "?"), []).append(row)

    for topic in sorted(by_topic):
        items = sorted(by_topic[topic], key=lambda r: rel(r[0]))
        print(f"\n[{topic}]")
        for path, meta, elapsed, interval, remain in items:
            flag = "DUE" if (meta.get("status") != "todo" and remain <= 0) else "   "
            print(f"  {flag} c{meta.get('confidence')} "
                  f"{meta.get('status', ''):<9} {rel(path):<42} "
                  f"{meta.get('title', '')}")
    print()
    summary(rows)


def summary(rows):
    if not rows:
        print("노트가 없습니다. python tools/new.py <분류> <파일명> 으로 시작하세요.")
        return
    counts = {"done": 0, "drafting": 0, "todo": 0}
    confs = []
    for _p, meta, *_ in rows:
        counts[meta.get("status", "todo")] = counts.get(meta.get("status", "todo"), 0) + 1
        confs.append(meta.get("confidence", 1))
    avg = sum(confs) / len(confs)
    print(f"진도: done {counts['done']} / drafting {counts['drafting']} "
          f"/ todo {counts['todo']}    평균 confidence {avg:.1f}")


def update(target: str, confidence):
    path = (ROOT / target).resolve() if not pathlib.Path(target).is_absolute() \
        else pathlib.Path(target)
    if not path.exists():
        print(f"파일이 없습니다: {target}")
        return 1

    text = read_text(path)
    if not text.lstrip().startswith("---"):
        print(f"frontmatter 가 없습니다: {rel(path)}")
        return 1

    # 줄바꿈을 보존하기 위해 . 대신 [^\r\n] 을 쓴다
    text, n1 = re.subn(r"^(last_reviewed:)[^\r\n]*",
                       r"\1 " + TODAY.isoformat(), text, count=1, flags=re.MULTILINE)
    if n1 == 0:
        print("last_reviewed 키를 못 찾았습니다.")
        return 1

    if confidence is not None:
        if confidence not in INTERVALS:
            print(f"confidence 는 1~5 입니다: {confidence}")
            return 1
        text, n2 = re.subn(r"^(confidence:)[^\r\n]*",
                           r"\1 " + str(confidence), text, count=1, flags=re.MULTILINE)
        if n2 == 0:
            print("confidence 키를 못 찾았습니다.")
            return 1

    write_text(path, text)
    conf = confidence if confidence is not None else "변경 없음"
    nxt = INTERVALS.get(confidence, None)
    print(f"기록: {rel(path)}  last_reviewed={TODAY}  confidence={conf}")
    if nxt:
        print(f"다음 복습: {TODAY + datetime.timedelta(days=nxt)} ({nxt}일 후)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="복습 큐와 진도 확인")
    ap.add_argument("target", nargs="?", help="복습 완료를 기록할 노트 경로")
    ap.add_argument("-c", "--confidence", type=int, help="자기평가 1~5")
    ap.add_argument("--all", action="store_true", help="전체 현황")
    ap.add_argument("--topic", help="특정 분류만")
    args = ap.parse_args()

    if args.target:
        return update(args.target, args.confidence)

    rows = collect(args.topic)
    if args.all:
        show_all(rows)
    else:
        show_due(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
