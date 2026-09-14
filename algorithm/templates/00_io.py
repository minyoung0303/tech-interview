"""
00_io.py — 입출력과 기본 골격
===========================================================================
Day 1. 여기서 시간을 잃는 사람이 정말 많다. 첫날에 손에 붙여둔다.

핵심 3줄
    1) input = sys.stdin.readline  을 안 쓰면 입력 많은 문제에서 시간 초과가 난다
    2) readline 은 개행(\\n)을 포함한다 → 문자열은 .strip() 필수
    3) 출력이 많으면 모아서 한 번에 출력한다 (print 를 10만 번 호출하지 않는다)

실행:  python 00_io.py
===========================================================================
"""

import io
import sys

# ---------------------------------------------------------------------------
# 1. 그대로 복사해서 쓰는 골격
# ---------------------------------------------------------------------------

SKELETON = r'''
import sys
input = sys.stdin.readline
sys.setrecursionlimit(10 ** 6)      # 재귀 DFS 를 쓸 때만


def solve():
    n, m = map(int, input().split())
    grid = [list(map(int, input().split())) for _ in range(n)]
    # ...
    print(0)


if __name__ == "__main__":
    solve()
'''


# ---------------------------------------------------------------------------
# 2. 입력 파싱 패턴 — 문자열을 받는 형태로 만들어 테스트가 가능하게 했다
#    실제 문제에서는 text 대신 sys.stdin 을 읽는다
# ---------------------------------------------------------------------------

def parse_one_int(text: str) -> int:
    """정수 하나.   입력: "5\\n" """
    return int(text.strip())


def parse_ints_line(text: str) -> list:
    """한 줄에 여러 정수.   입력: "1 2 3\\n" """
    return list(map(int, text.split()))


def parse_grid_spaced(lines: list) -> list:
    """공백으로 구분된 2차원 배열.
    3 1 2
    4 5 6
    """
    return [list(map(int, ln.split())) for ln in lines]


def parse_grid_chars(lines: list) -> list:
    """붙어 있는 문자 격자. 미로 문제의 기본 형태.
    #..#
    .##.
    """
    return [list(ln.strip()) for ln in lines]


def parse_grid_digits(lines: list) -> list:
    """붙어 있는 숫자 격자. "1011" -> [1, 0, 1, 1]"""
    return [[int(ch) for ch in ln.strip()] for ln in lines]


def parse_edges(lines: list) -> list:
    """간선 목록 -> 튜플 리스트"""
    return [tuple(map(int, ln.split())) for ln in lines]


def read_all_tokens(stream) -> list:
    """가장 빠른 입력. 전체를 한 번에 읽어 토큰으로 쪼갠다.
    입력량이 아주 많은 문제(수십만 줄)에서 확실한 차이가 난다.
    """
    return stream.read().split()


class TokenReader:
    """read_all_tokens 를 순서대로 꺼내 쓰는 헬퍼.
    입력 형식이 복잡한 문제에서 편하다.
    """

    def __init__(self, text: str):
        self._tokens = text.split()
        self._i = 0

    def int(self) -> int:
        v = int(self._tokens[self._i])
        self._i += 1
        return v

    def ints(self, k: int) -> list:
        vs = [int(t) for t in self._tokens[self._i:self._i + k]]
        self._i += k
        return vs

    def word(self) -> str:
        v = self._tokens[self._i]
        self._i += 1
        return v


# ---------------------------------------------------------------------------
# 3. 출력 패턴
# ---------------------------------------------------------------------------

def out_space(arr: list) -> str:
    """공백 구분:  1 2 3"""
    return " ".join(map(str, arr))


def out_lines(arr: list) -> str:
    """줄바꿈 구분. 반복 print 보다 훨씬 빠르다."""
    return "\n".join(map(str, arr))


def demo_bulk_output(arr: list) -> None:
    """출력이 수만 줄일 때. 한 번의 write 로 끝낸다."""
    sys.stdout.write("\n".join(map(str, arr)) + "\n")


# ---------------------------------------------------------------------------
# 4. EOF 까지 읽기 (줄 수를 안 알려주는 문제. 예: 백준 10951)
# ---------------------------------------------------------------------------

def sum_until_eof(text: str) -> list:
    """각 줄의 "a b" 를 더해서 리스트로 돌려준다."""
    results = []
    for line in io.StringIO(text):
        line = line.strip()
        if not line:            # 빈 줄 방어 — 실전에서 이거 없으면 터진다
            continue
        a, b = map(int, line.split())
        results.append(a + b)
    return results


# ---------------------------------------------------------------------------
# 5. 실전에서 stdin 을 바꿔 끼워 로컬 테스트하는 방법
#    문제를 풀 때 예제 입력을 파일에 저장해두면 매번 손으로 안 쳐도 된다
# ---------------------------------------------------------------------------

def with_stdin(text: str, fn):
    """sys.stdin 을 text 로 갈아끼우고 fn() 을 실행한다."""
    original = sys.stdin
    sys.stdin = io.StringIO(text)
    try:
        return fn()
    finally:
        sys.stdin = original


def example_solve():
    """with_stdin 으로 테스트되는 실제 풀이 형태.
    백준식 문제: 첫 줄에 N, 둘째 줄에 N개의 수 -> 최대-최소 출력
    """
    read = sys.stdin.readline
    n = int(read())
    arr = list(map(int, read().split()))
    assert len(arr) == n
    return max(arr) - min(arr)


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert parse_one_int("5\n") == 5
    assert parse_ints_line("1 2 3\n") == [1, 2, 3]

    assert parse_grid_spaced(["3 1 2", "4 5 6"]) == [[3, 1, 2], [4, 5, 6]]
    assert parse_grid_chars(["#..#", ".##."]) == [
        ["#", ".", ".", "#"],
        [".", "#", "#", "."],
    ]
    assert parse_grid_digits(["1011", "0110"]) == [[1, 0, 1, 1], [0, 1, 1, 0]]
    assert parse_edges(["1 2", "2 3"]) == [(1, 2), (2, 3)]

    tr = TokenReader("3 10 20 30 hello")
    assert tr.int() == 3
    assert tr.ints(3) == [10, 20, 30]
    assert tr.word() == "hello"

    assert out_space([1, 2, 3]) == "1 2 3"
    assert out_lines([1, 2]) == "1\n2"

    assert sum_until_eof("1 2\n3 4\n\n5 6\n") == [3, 7, 11]
    assert read_all_tokens(io.StringIO("1 2\n3")) == ["1", "2", "3"]

    assert with_stdin("5\n1 2 3 4 9\n", example_solve) == 8

    print("00_io.py  OK")
    print()
    print("=== 문제 풀이 시작 골격 (외워서 타이핑한다) ===")
    print(SKELETON.strip())
