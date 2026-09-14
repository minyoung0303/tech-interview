"""
run_all.py — 모든 템플릿의 자체 검증을 한 번에 돌린다
===========================================================================
템플릿을 고쳐가며 공부할 때, 뭔가 깨졌는지 바로 확인하는 용도.

    python algorithm/templates/run_all.py

각 파일은 단독 실행도 된다.

    python algorithm/templates/08_graph.py
===========================================================================
"""

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent


def main() -> int:
    files = sorted(
        p for p in HERE.glob("*.py")
        if p.name != "run_all.py" and p.name[0].isdigit()
    )
    failed = []
    for path in files:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
        )
        mark = "OK  " if proc.returncode == 0 else "FAIL"
        print(f"[{mark}] {path.name}")
        if proc.returncode != 0:
            failed.append(path.name)
            print(proc.stdout)
            print(proc.stderr)

    print()
    if failed:
        print(f"실패 {len(failed)}개: {', '.join(failed)}")
        return 1
    print(f"전체 {len(files)}개 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
