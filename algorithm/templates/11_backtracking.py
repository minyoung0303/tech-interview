"""
11_backtracking.py — 백트래킹 / 순열·조합 / 완전 탐색
===========================================================================
Day 14. "모든 경우를 살펴봐야 한다"는 문제.

먼저 확인할 것 — N 이 작은지
    N <= 8 정도면 itertools 로 완전 탐색하는 게 가장 빠르고 안전하다.
    직접 백트래킹을 짜는 건 **가지치기(pruning)가 필요할 때**다.

백트래킹 4요소
    1) 상태(path)      지금까지 고른 것
    2) 선택            다음에 고를 수 있는 것들
    3) 가지치기        이 방향은 답이 될 수 없다고 판단해 되돌린다  <- 이게 핵심
    4) 되돌리기        path.pop() / used[i] = False

가장 흔한 버그
    result.append(path)      -> 나중에 path 가 바뀌면 결과도 바뀐다 (같은 객체 참조)
    result.append(path[:])   -> 반드시 복사해서 넣는다

실행:  python 11_backtracking.py
===========================================================================
"""

from itertools import combinations, permutations, product

# ---------------------------------------------------------------------------
# 1. itertools 로 끝나는 경우 — 먼저 이걸 고려한다
# ---------------------------------------------------------------------------

def all_permutations(items: list, k: int) -> list:
    """순열: 순서가 다르면 다른 경우."""
    return [list(p) for p in permutations(items, k)]


def all_combinations(items: list, k: int) -> list:
    """조합: 순서 무시."""
    return [list(c) for c in combinations(items, k)]


def all_repeat_permutations(items: list, k: int) -> list:
    """중복 순열: 같은 것을 여러 번 골라도 된다. 완전 탐색에 자주 쓴다."""
    return [list(p) for p in product(items, repeat=k)]


def all_subsets(items: list) -> list:
    """부분집합 전체 (2^N). 비트마스크로도 같은 걸 만들 수 있다."""
    result = []
    n = len(items)
    for mask in range(1 << n):
        subset = [items[i] for i in range(n) if mask & (1 << i)]
        result.append(subset)
    return result


# ---------------------------------------------------------------------------
# 2. 직접 백트래킹 — N과 M (백준 15649 계열)
# ---------------------------------------------------------------------------

def n_and_m_permutation(n: int, m: int) -> list:
    """1..n 에서 중복 없이 m 개를 고른 수열 (순서 있음). 백준 15649.
    백트래킹의 가장 기본 형태. 이 틀을 외운다.
    """
    result = []
    path = []
    used = [False] * (n + 1)

    def go():
        if len(path) == m:
            result.append(path[:])          # 반드시 복사
            return
        for v in range(1, n + 1):
            if used[v]:
                continue
            used[v] = True
            path.append(v)
            go()
            path.pop()                      # 되돌리기
            used[v] = False

    go()
    return result


def n_and_m_combination(n: int, m: int) -> list:
    """오름차순 (조합). 백준 15650.
    시작 인덱스를 넘겨서 "이전보다 큰 것만" 고르게 하면 중복이 사라진다.
    """
    result = []
    path = []

    def go(start):
        if len(path) == m:
            result.append(path[:])
            return
        for v in range(start, n + 1):
            path.append(v)
            go(v + 1)
            path.pop()

    go(1)
    return result


def n_and_m_repeat(n: int, m: int) -> list:
    """중복 허용 수열. 백준 15651. used 배열이 없어진다."""
    result = []
    path = []

    def go():
        if len(path) == m:
            result.append(path[:])
            return
        for v in range(1, n + 1):
            path.append(v)
            go()
            path.pop()

    go()
    return result


# ---------------------------------------------------------------------------
# 3. 가지치기가 필요한 문제 — N-Queen (백준 9663)
# ---------------------------------------------------------------------------

def n_queens(n: int) -> int:
    """N-Queen 배치 가능한 경우의 수.

    가지치기가 없으면 N=8 에서도 느리다.
    같은 열 / 같은 대각선 두 방향을 집합으로 관리해 O(1) 로 판정한다.
      대각선 1: r - c 가 같으면 같은 대각선 (↘)
      대각선 2: r + c 가 같으면 같은 대각선 (↙)
    이 두 식이 N-Queen 의 핵심이다.
    """
    cols = set()
    diag1 = set()
    diag2 = set()
    count = 0

    def go(row):
        nonlocal count
        if row == n:
            count += 1
            return
        for c in range(n):
            if c in cols or (row - c) in diag1 or (row + c) in diag2:
                continue                     # 가지치기
            cols.add(c)
            diag1.add(row - c)
            diag2.add(row + c)
            go(row + 1)
            cols.remove(c)
            diag1.remove(row - c)
            diag2.remove(row + c)

    go(0)
    return count


# ---------------------------------------------------------------------------
# 4. 연산자 끼워넣기 (백준 14888) — 남은 개수를 상태로 들고 간다
# ---------------------------------------------------------------------------

def operator_insert(nums: list, counts: list):
    """counts = [+개수, -개수, *개수, //개수]
    반환: (최댓값, 최솟값)

    상태: (인덱스, 현재값, 남은 연산자 개수)
    나눗셈은 문제 규칙대로 **음수일 때 절댓값 몫에 음수 부호**를 붙인다.
    파이썬 // 는 내림이라 -7//2 == -4 가 되므로 그대로 쓰면 틀린다. 이게 함정이다.
    """
    best = [float("-inf"), float("inf")]
    ops = list(counts)

    def go(idx, acc):
        if idx == len(nums):
            best[0] = max(best[0], acc)
            best[1] = min(best[1], acc)
            return
        for op in range(4):
            if ops[op] == 0:
                continue
            ops[op] -= 1
            nxt = nums[idx]
            if op == 0:
                go(idx + 1, acc + nxt)
            elif op == 1:
                go(idx + 1, acc - nxt)
            elif op == 2:
                go(idx + 1, acc * nxt)
            else:
                if acc < 0:
                    go(idx + 1, -((-acc) // nxt))      # 음수 나눗셈 규칙
                else:
                    go(idx + 1, acc // nxt)
            ops[op] += 1

    go(1, nums[0])
    return best[0], best[1]


# ---------------------------------------------------------------------------
# 5. 스타트와 링크 (백준 14889) — 조합으로 절반 나누기
# ---------------------------------------------------------------------------

def start_and_link(stats: list) -> int:
    """n 명을 두 팀으로 나눌 때 능력치 차이의 최소.

    itertools.combinations 로 절반을 고르면 코드가 아주 짧아진다.
    (0번 사람을 고정하면 대칭 중복을 절반으로 줄일 수 있다 — 여기서는 명확성을 택했다)
    """
    n = len(stats)
    members = range(n)
    best = float("inf")
    for team in combinations(members, n // 2):
        if 0 not in team:
            continue                          # 대칭 제거: 0번은 항상 start 팀
        other = [m for m in members if m not in team]
        a = sum(stats[i][j] + stats[j][i] for i, j in combinations(team, 2))
        b = sum(stats[i][j] + stats[j][i] for i, j in combinations(other, 2))
        best = min(best, abs(a - b))
    return best


# ---------------------------------------------------------------------------
# 6. 타겟 넘버 (프로그래머스) — DFS 완전 탐색의 기본
# ---------------------------------------------------------------------------

def target_number(numbers: list, target: int) -> int:
    """각 수를 더하거나 빼서 target 을 만드는 방법의 수."""
    def go(idx, acc):
        if idx == len(numbers):
            return 1 if acc == target else 0
        return go(idx + 1, acc + numbers[idx]) + go(idx + 1, acc - numbers[idx])

    return go(0, 0)


# ---------------------------------------------------------------------------
# 7. 스도쿠식 제약 백트래킹 (백준 2580 축소판)
# ---------------------------------------------------------------------------

def solve_sudoku4(board: list) -> bool:
    """4x4 스도쿠 (2x2 박스). 0 은 빈 칸. board 를 제자리에서 채운다.

    빈 칸을 찾아 1..4 를 넣어보고, 유효하면 다음 빈 칸으로.
    막히면 0 으로 되돌린다 — 백트래킹의 정석 구조.
    """
    def valid(r, c, v):
        for i in range(4):
            if board[r][i] == v or board[i][c] == v:
                return False
        br, bc = (r // 2) * 2, (c // 2) * 2
        for i in range(br, br + 2):
            for j in range(bc, bc + 2):
                if board[i][j] == v:
                    return False
        return True

    def go():
        for r in range(4):
            for c in range(4):
                if board[r][c] != 0:
                    continue
                for v in range(1, 5):
                    if valid(r, c, v):
                        board[r][c] = v
                        if go():
                            return True
                        board[r][c] = 0        # 되돌리기
                return False                   # 아무 것도 못 넣으면 실패
        return True                            # 빈 칸이 없으면 완성

    return go()


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert all_permutations([1, 2, 3], 2) == [
        [1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]
    assert all_combinations([1, 2, 3], 2) == [[1, 2], [1, 3], [2, 3]]
    assert len(all_repeat_permutations([0, 1], 3)) == 8
    assert len(all_subsets([1, 2, 3])) == 8
    assert [] in all_subsets([1, 2])

    # 백준 15649 / 15650 / 15651
    assert n_and_m_permutation(3, 2) == all_permutations([1, 2, 3], 2)
    assert n_and_m_combination(4, 2) == [
        [1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    assert len(n_and_m_repeat(3, 2)) == 9

    # 결과 복사를 안 하면 터지는 케이스 — path[:] 의 중요성 확인
    res = n_and_m_permutation(3, 3)
    assert len(res) == 6 and len(set(map(tuple, res))) == 6

    # N-Queen 알려진 값
    assert n_queens(1) == 1
    assert n_queens(4) == 2
    assert n_queens(6) == 4
    assert n_queens(8) == 92

    # 백준 14888 예제
    assert operator_insert([1, 2, 3, 4, 5, 6], [2, 1, 1, 1]) == (54, -24)
    assert operator_insert([3, 4, 5], [1, 0, 1, 0]) == (35, 17)
    # 음수 나눗셈 규칙 확인
    #   "-" 먼저: 0 - 7 = -7,  -7 // 2 -> -3  (파이썬 기본 // 는 -4 가 되므로 규칙이 필요)
    #   "//" 먼저: 0 // 7 = 0,  0 - 2 = -2
    assert operator_insert([0, 7, 2], [0, 1, 0, 1]) == (-2, -3)

    # 백준 14889 예제
    stats = [
        [0, 1, 2, 3],
        [4, 0, 5, 6],
        [7, 1, 0, 2],
        [3, 4, 5, 0],
    ]
    assert start_and_link(stats) == 0

    # 프로그래머스 타겟 넘버
    assert target_number([1, 1, 1, 1, 1], 3) == 5
    assert target_number([4, 1, 2, 1], 4) == 2

    # 4x4 스도쿠
    board = [
        [1, 0, 0, 0],
        [0, 0, 3, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 2],
    ]
    assert solve_sudoku4(board)
    for row in board:
        assert sorted(row) == [1, 2, 3, 4]
    for c in range(4):
        assert sorted(board[r][c] for r in range(4)) == [1, 2, 3, 4]

    print("11_backtracking.py  OK")
