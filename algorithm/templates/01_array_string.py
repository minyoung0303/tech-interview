"""
01_array_string.py — 구현 / 시뮬레이션 / 격자
===========================================================================
Day 2. "시키는 대로 하면 되는" 문제인데 실수로 틀리는 유형.
알고리즘이 아니라 **정확도** 문제라서, 정리해둔 부품을 쓰는 게 핵심이다.

부품 3개만 챙긴다
    1) 방향 배열 (dr, dc)      — 격자 이동은 전부 이걸로 처리한다
    2) 경계 체크 함수 in_range — if 안에 부등호 4개를 매번 쓰지 않는다
    3) 회전 / 전치              — zip(*grid) 관용구

실행:  python 01_array_string.py
===========================================================================
"""

# ---------------------------------------------------------------------------
# 1. 방향 배열 — 이 네 줄이 격자 문제의 절반이다
# ---------------------------------------------------------------------------

# 상, 하, 좌, 우
DR = (-1, 1, 0, 0)
DC = (0, 0, -1, 1)

# 8방향 (대각선 포함). 단지/영역 문제에서 "대각선도 연결"이면 이걸 쓴다
D8 = ((-1, -1), (-1, 0), (-1, 1),
      (0, -1),           (0, 1),
      (1, -1),  (1, 0),  (1, 1))

# 시계 방향 회전 순서 (북 → 동 → 남 → 서). 로봇/뱀 문제에서 쓴다
#   d = (d + 1) % 4  → 시계 방향 90도
#   d = (d + 3) % 4  → 반시계 방향 90도
CW = ((-1, 0), (0, 1), (1, 0), (0, -1))


def in_range(r: int, c: int, n: int, m: int) -> bool:
    """격자 안인지 확인. 부등호를 매번 쓰다가 틀리는 걸 막는다."""
    return 0 <= r < n and 0 <= c < m


def neighbors(r: int, c: int, n: int, m: int, diagonal: bool = False):
    """인접 칸을 순회하는 제너레이터. for nr, nc in neighbors(...) 로 쓴다."""
    dirs = D8 if diagonal else tuple(zip(DR, DC))
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if in_range(nr, nc, n, m):
            yield nr, nc


# ---------------------------------------------------------------------------
# 2. 2차원 배열 생성 / 변형
# ---------------------------------------------------------------------------

def make_grid(n: int, m: int, fill=0) -> list:
    """[[0]*m]*n 은 같은 행을 n번 참조한다. 반드시 이 형태로 만든다."""
    return [[fill] * m for _ in range(n)]


def transpose(grid: list) -> list:
    """전치. 행과 열을 바꾼다."""
    return [list(row) for row in zip(*grid)]


def rotate_cw(grid: list) -> list:
    """시계 방향 90도 회전. 삼성 기출 구현 문제에서 자주 필요하다."""
    return [list(row) for row in zip(*grid[::-1])]


def rotate_ccw(grid: list) -> list:
    """반시계 방향 90도 회전."""
    return [list(row) for row in zip(*grid)][::-1]


def flatten(grid: list) -> list:
    return [v for row in grid for v in row]


# ---------------------------------------------------------------------------
# 3. 격자 순회 패턴
# ---------------------------------------------------------------------------

def spiral_order(n: int, m: int) -> list:
    """달팽이(나선) 순회 좌표 순서.
    방향 전환 조건: 다음 칸이 격자 밖이거나 이미 방문했으면 시계 방향으로 꺾는다.
    """
    visited = make_grid(n, m, False)
    order = []
    r = c = d = 0
    for _ in range(n * m):
        order.append((r, c))
        visited[r][c] = True
        nr, nc = r + CW[d][0], c + CW[d][1]
        if not in_range(nr, nc, n, m) or visited[nr][nc]:
            d = (d + 1) % 4
            nr, nc = r + CW[d][0], c + CW[d][1]
        r, c = nr, nc
    return order


def zigzag_order(n: int, m: int) -> list:
    """지그재그(보스트로페돈) 순회. 홀수 행은 역방향."""
    order = []
    for r in range(n):
        cols = range(m) if r % 2 == 0 else range(m - 1, -1, -1)
        for c in cols:
            order.append((r, c))
    return order


# ---------------------------------------------------------------------------
# 4. 시뮬레이션 예제 — 로봇 이동 (백준 14503 로봇 청소기 축소판)
#    "규칙을 코드로 그대로 옮기는" 연습. 조건 순서를 문제 그대로 따라간다
# ---------------------------------------------------------------------------

def clean_room(grid: list, sr: int, sc: int, sd: int) -> int:
    """로봇 청소기 규칙
        1. 현재 칸이 청소되지 않았으면 청소한다
        2. 네 방향 중 청소되지 않은 빈 칸이 있으면
           → 반시계 90도 회전 후, 바라보는 칸이 청소 안 된 빈 칸이면 한 칸 전진
        3. 없으면 바라보는 방향을 유지한 채 한 칸 후진. 후진 못 하면 종료

    grid: 0=빈 칸, 1=벽.  반환값: 청소한 칸 수
    """
    n, m = len(grid), len(grid[0])
    cleaned = make_grid(n, m, False)
    r, c, d = sr, sc, sd
    count = 0

    while True:
        if not cleaned[r][c]:
            cleaned[r][c] = True
            count += 1

        # 2. 주변에 청소할 곳이 남았는지
        has_dirty = any(
            grid[nr][nc] == 0 and not cleaned[nr][nc]
            for nr, nc in neighbors(r, c, n, m)
        )

        if has_dirty:
            d = (d + 3) % 4                       # 반시계 90도
            nr, nc = r + CW[d][0], c + CW[d][1]
            if in_range(nr, nc, n, m) and grid[nr][nc] == 0 and not cleaned[nr][nc]:
                r, c = nr, nc
        else:
            # 3. 후진 (바라보는 방향의 반대)
            br, bc = r - CW[d][0], c - CW[d][1]
            if not in_range(br, bc, n, m) or grid[br][bc] == 1:
                return count
            r, c = br, bc


# ---------------------------------------------------------------------------
# 5. 문자열 처리 관용구
# ---------------------------------------------------------------------------

def alpha_index(ch: str) -> int:
    """'A' -> 0, 'a' -> 0"""
    return ord(ch.upper()) - ord("A")


def is_palindrome(s: str) -> bool:
    return s == s[::-1]


def run_length_encode(s: str) -> str:
    """연속 문자 압축. "aaabb" -> "a3b2"  (문자열 압축 유형)"""
    if not s:
        return ""
    out = []
    prev, cnt = s[0], 1
    for ch in s[1:]:
        if ch == prev:
            cnt += 1
        else:
            out.append(prev + (str(cnt) if cnt > 1 else ""))
            prev, cnt = ch, 1
    out.append(prev + (str(cnt) if cnt > 1 else ""))
    return "".join(out)


def caesar(s: str, k: int) -> str:
    """알파벳만 k칸 밀기. 대소문자 유지, 나머지는 그대로."""
    out = []
    for ch in s:
        if ch.isupper():
            out.append(chr((ord(ch) - 65 + k) % 26 + 65))
        elif ch.islower():
            out.append(chr((ord(ch) - 97 + k) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def split_keep_numbers(s: str) -> list:
    """문자열에서 연속된 숫자를 정수로 묶어 뽑는다. 파싱 문제에 쓴다.
    "ab12cd3" -> ['ab', 12, 'cd', 3]
    """
    out, buf, digits = [], "", ""
    for ch in s:
        if ch.isdigit():
            if buf:
                out.append(buf)
                buf = ""
            digits += ch
        else:
            if digits:
                out.append(int(digits))
                digits = ""
            buf += ch
    if buf:
        out.append(buf)
    if digits:
        out.append(int(digits))
    return out


# ---------------------------------------------------------------------------
# 6. 색종이 넓이 (백준 2563) — 2차원 배열 스탬프 찍기 패턴
# ---------------------------------------------------------------------------

def paper_area(papers: list, size: int = 100, side: int = 10) -> int:
    """papers: [(x, y), ...] 왼쪽 아래 좌표. 겹치는 부분은 한 번만 센다."""
    board = make_grid(size, size, 0)
    for x, y in papers:
        for dx in range(side):
            for dy in range(side):
                board[x + dx][y + dy] = 1
    return sum(map(sum, board))


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 방향 / 경계
    assert in_range(0, 0, 3, 3) and not in_range(-1, 0, 3, 3)
    assert sorted(neighbors(0, 0, 3, 3)) == [(0, 1), (1, 0)]
    assert len(list(neighbors(1, 1, 3, 3))) == 4
    assert len(list(neighbors(1, 1, 3, 3, diagonal=True))) == 8

    # 2차원 생성 — 얕은 복사 함정 확인
    g = make_grid(2, 3)
    g[0][0] = 9
    assert g == [[9, 0, 0], [0, 0, 0]], "make_grid 가 행을 공유하면 안 된다"

    # 회전 / 전치
    grid = [[1, 2, 3],
            [4, 5, 6]]
    assert transpose(grid) == [[1, 4], [2, 5], [3, 6]]
    assert rotate_cw(grid) == [[4, 1], [5, 2], [6, 3]]
    assert rotate_ccw(grid) == [[3, 6], [2, 5], [1, 4]]
    assert rotate_cw(rotate_cw(rotate_cw(rotate_cw(grid)))) == grid
    assert flatten(grid) == [1, 2, 3, 4, 5, 6]

    # 순회
    assert spiral_order(3, 3) == [
        (0, 0), (0, 1), (0, 2),
        (1, 2), (2, 2),
        (2, 1), (2, 0),
        (1, 0), (1, 1),
    ]
    assert zigzag_order(2, 3) == [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0)]

    # 시뮬레이션: 벽 없는 3x3 이면 전부 청소한다
    room = make_grid(3, 3, 0)
    assert clean_room(room, 1, 1, 0) == 9

    # 사방이 벽인 1칸 방
    room2 = [[1, 1, 1],
             [1, 0, 1],
             [1, 1, 1]]
    assert clean_room(room2, 1, 1, 0) == 1

    # 문자열
    assert alpha_index("C") == 2 and alpha_index("a") == 0
    assert is_palindrome("aba") and not is_palindrome("ab")
    assert run_length_encode("aaabbc") == "a3b2c"
    assert run_length_encode("") == ""
    assert caesar("aBz", 1) == "bCa"
    assert split_keep_numbers("ab12cd3") == ["ab", 12, "cd", 3]

    # 색종이: 겹치지 않는 2장 = 200, 완전히 겹치면 100
    assert paper_area([(0, 0), (20, 20)]) == 200
    assert paper_area([(0, 0), (0, 0)]) == 100
    assert paper_area([(0, 0), (5, 5)]) == 175   # 10x10 두 장, 5x5 겹침

    print("01_array_string.py  OK")
