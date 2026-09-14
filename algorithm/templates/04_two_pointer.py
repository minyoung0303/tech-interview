"""
04_two_pointer.py — 투 포인터 / 슬라이딩 윈도우 / 누적합
===========================================================================
Day 5. "연속된 구간" 이라는 말이 나오면 이 세 개 중 하나다.

세 개의 구분
    투 포인터        정렬된 배열에서 양 끝에서 좁혀 온다 (합이 target 인 쌍)
    슬라이딩 윈도우  왼쪽/오른쪽이 같은 방향으로 이동한다 (연속 부분 배열)
    누적합           구간 합을 O(1) 로 얻기 위한 전처리 (질의가 여러 번일 때)

전부 O(N) 이고, 2중 루프 O(N²) 를 대체하는 게 목적이다.
"연속"이 아니면 이 유형이 아니다. (부분집합이면 DP 나 백트래킹)

실행:  python 04_two_pointer.py
===========================================================================
"""

from itertools import accumulate

# ---------------------------------------------------------------------------
# 1. 누적합 (Prefix Sum)
# ---------------------------------------------------------------------------

def prefix_sum(arr: list) -> list:
    """앞에 0 을 붙인 누적합. 길이 N+1.
    구간 [l, r] (0-based, 양끝 포함) 합 = ps[r+1] - ps[l]
    앞에 0 을 두면 l=0 인 경우를 특별 처리하지 않아도 된다. 반드시 이렇게 만든다.
    """
    ps = [0] * (len(arr) + 1)
    for i, v in enumerate(arr):
        ps[i + 1] = ps[i] + v
    return ps


def range_sum(ps: list, left: int, right: int) -> int:
    """0-based 양끝 포함 구간 합. ps 는 prefix_sum 결과."""
    return ps[right + 1] - ps[left]


def sliding_window_fixed(arr: list, k: int) -> int:
    """수열 (백준 2559). 연속된 k 개의 합 중 최대.

    매번 k 개를 더하면 O(NK). 창을 한 칸 밀 때 들어온 것 더하고 나간 것 빼면 O(N).
    """
    if k > len(arr):
        raise ValueError("k 가 배열보다 크다")
    window = sum(arr[:k])
    best = window
    for i in range(k, len(arr)):
        window += arr[i] - arr[i - k]
        best = max(best, window)
    return best


def prefix_sum_2d(grid: list) -> list:
    """2차원 누적합. ps[r][c] = (0,0) ~ (r-1,c-1) 직사각형 합.
    구간 합 = ps[r2+1][c2+1] - ps[r1][c2+1] - ps[r2+1][c1] + ps[r1][c1]
    """
    n, m = len(grid), len(grid[0])
    ps = [[0] * (m + 1) for _ in range(n + 1)]
    for r in range(n):
        for c in range(m):
            ps[r + 1][c + 1] = grid[r][c] + ps[r][c + 1] + ps[r + 1][c] - ps[r][c]
    return ps


def range_sum_2d(ps: list, r1: int, c1: int, r2: int, c2: int) -> int:
    return ps[r2 + 1][c2 + 1] - ps[r1][c2 + 1] - ps[r2 + 1][c1] + ps[r1][c1]


# ---------------------------------------------------------------------------
# 2. 투 포인터 — 정렬된 배열, 양 끝에서 좁힌다
# ---------------------------------------------------------------------------

def two_solutions(arr: list, target: int = 0):
    """두 용액 (백준 2470). 합이 target 에 가장 가까운 두 값.

    정렬 후 양 끝. 합이 target 보다 크면 right--, 작으면 left++.
    "정렬하면 한 방향으로만 움직여도 된다"가 투 포인터의 근거다.
    """
    arr = sorted(arr)
    left, right = 0, len(arr) - 1
    best = None
    best_diff = float("inf")
    while left < right:
        total = arr[left] + arr[right]
        diff = abs(total - target)
        if diff < best_diff:
            best_diff = diff
            best = (arr[left], arr[right])
        if total < target:
            left += 1
        else:
            right -= 1
    return best


def count_pairs_with_sum(arr: list, target: int) -> int:
    """합이 정확히 target 인 쌍의 개수 (중복 값 있음).

    중복 값 묶음 처리가 이 유형의 함정이다.
    같은 값이 여러 개면 개수를 세서 곱하고, 양쪽 값이 같으면 조합 nC2 로 계산한다.
    """
    arr = sorted(arr)
    left, right = 0, len(arr) - 1
    count = 0
    while left < right:
        total = arr[left] + arr[right]
        if total < target:
            left += 1
        elif total > target:
            right -= 1
        else:
            lv, rv = arr[left], arr[right]
            if lv == rv:                       # 남은 구간이 전부 같은 값 -> nC2
                k = right - left + 1
                count += k * (k - 1) // 2
                break
            lc = 0
            while left <= right and arr[left] == lv:
                left += 1
                lc += 1
            rc = 0
            while right >= left and arr[right] == rv:
                right -= 1
                rc += 1
            count += lc * rc
    return count


# ---------------------------------------------------------------------------
# 3. 슬라이딩 윈도우 — 왼쪽/오른쪽이 같은 방향
# ---------------------------------------------------------------------------

def sum_equal_target_count(n: int, target: int) -> int:
    """수들의 합 5 (백준 2018). 1..n 의 연속된 자연수 합이 target 이 되는 경우의 수.

    양수만 있으므로 창을 넓히면 합이 커지고 줄이면 작아진다 → 단조성이 성립.
    이 단조성이 슬라이딩 윈도우의 전제다. 음수가 섞이면 못 쓴다.
    """
    left = 1
    total = 0
    count = 0
    for right in range(1, n + 1):
        total += right
        while total > target:
            total -= left
            left += 1
        if total == target:
            count += 1
    return count


def min_length_at_least(arr: list, target: int) -> int:
    """부분합 (백준 1806). 합이 target 이상인 가장 짧은 연속 구간의 길이.
    없으면 0.
    """
    left = 0
    total = 0
    best = float("inf")
    for right, v in enumerate(arr):
        total += v
        while total >= target:
            best = min(best, right - left + 1)
            total -= arr[left]
            left += 1
    return 0 if best == float("inf") else best


def dna_password(s: str, need: dict, window: int) -> int:
    """DNA 비밀번호 (백준 12891). 길이가 고정된 창에서 조건을 만족하는 개수.

    고정 창 + 개수 조건. 창이 움직일 때 카운트를 증감시키고,
    "조건을 만족하는 종류 수"를 따로 관리해서 매번 전체 비교를 피한다.
    """
    from collections import Counter

    cur = Counter()
    satisfied = sum(1 for ch, k in need.items() if k == 0)

    def add(ch):
        nonlocal satisfied
        if ch in need:
            cur[ch] += 1
            if cur[ch] == need[ch]:
                satisfied += 1

    def remove(ch):
        nonlocal satisfied
        if ch in need:
            if cur[ch] == need[ch]:
                satisfied -= 1
            cur[ch] -= 1

    for i in range(window):
        add(s[i])
    count = 1 if satisfied == len(need) else 0

    for i in range(window, len(s)):
        add(s[i])
        remove(s[i - window])
        if satisfied == len(need):
            count += 1
    return count


def longest_subarray_k_distinct(arr: list, k: int) -> int:
    """서로 다른 값이 최대 k 종류인 가장 긴 연속 구간. 가변 창의 전형."""
    from collections import defaultdict

    cnt = defaultdict(int)
    left = 0
    best = 0
    for right, v in enumerate(arr):
        cnt[v] += 1
        while len(cnt) > k:
            cnt[arr[left]] -= 1
            if cnt[arr[left]] == 0:
                del cnt[arr[left]]
            left += 1
        best = max(best, right - left + 1)
    return best


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    arr = [1, 2, 3, 4, 5]
    ps = prefix_sum(arr)
    assert ps == [0, 1, 3, 6, 10, 15]
    assert range_sum(ps, 0, 4) == 15
    assert range_sum(ps, 1, 3) == 9        # 2+3+4
    assert range_sum(ps, 2, 2) == 3

    assert sliding_window_fixed([3, -2, -4, -9, -1, -5, 7, 6, 3, 2], 3) == 16
    assert sliding_window_fixed([1, 2, 3], 3) == 6

    grid = [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]
    ps2 = prefix_sum_2d(grid)
    assert range_sum_2d(ps2, 0, 0, 2, 2) == 45
    assert range_sum_2d(ps2, 1, 1, 2, 2) == 28        # 5+6+8+9
    assert range_sum_2d(ps2, 0, 0, 0, 0) == 1

    # 백준 2470 예제. |합|이 같은 후보가 여러 개면 먼저 찾은 것을 남긴다
    assert two_solutions([2, -3, 5, 7, -6, 1], 0) == (-6, 7)
    assert two_solutions([-2, 4, -99, -1, 98], 0) == (-99, 98)
    assert count_pairs_with_sum([1, 2, 3, 4, 5], 6) == 2      # (1,5),(2,4)
    assert count_pairs_with_sum([1, 1, 1, 1], 2) == 6         # 4C2
    assert count_pairs_with_sum([1, 1, 2, 2], 3) == 4         # 2 x 2

    assert sum_equal_target_count(15, 15) == 4        # 15 / 7+8 / 4+5+6 / 1+..+5
    assert sum_equal_target_count(1, 1) == 1

    assert min_length_at_least([5, 1, 3, 5, 10, 7, 4, 9, 2, 8], 15) == 2
    assert min_length_at_least([1, 2], 100) == 0
    assert min_length_at_least([100], 100) == 1

    # 백준 12891 예제 1: 조건을 만족하는 창이 없다
    assert dna_password("CCTGGATTG", {"A": 2, "C": 0, "G": 1, "T": 1}, 8) == 0
    # 백준 12891 예제 2: "AT", "TA" 두 개
    assert dna_password("GATA", {"A": 1, "C": 0, "G": 0, "T": 1}, 2) == 2
    assert dna_password("AAA", {"A": 1, "C": 0, "G": 0, "T": 0}, 1) == 3

    assert longest_subarray_k_distinct([1, 2, 1, 3, 4], 2) == 3   # [1,2,1]
    assert longest_subarray_k_distinct([1, 1, 1], 1) == 3

    print("04_two_pointer.py  OK")
