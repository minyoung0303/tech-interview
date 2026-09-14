"""
10_dp.py — 동적 계획법 (DP)
===========================================================================
Day 13~14. BFS 와 함께 출제 비중 최상위. 그리고 가장 막막한 유형.

막막함을 없애는 절차 4단계 — **코드보다 이걸 먼저 한다**
    1) dp 의 정의를 **한국어 문장**으로 쓴다
       "dp[i] = i번째 계단까지 왔을 때의 최대 점수"
       이 문장이 안 나오면 아직 못 푼 것이다. 코드를 치지 않는다
    2) 점화식을 쓴다
       "dp[i] = max(dp[i-2], dp[i-3] + s[i-1]) + s[i]"
    3) 초기값(base case)을 정한다  <- 여기서 대부분 틀린다
    4) 순회 방향을 정한다 (작은 것부터 = bottom-up)

DP 인지 아는 신호
    - 최댓값/최솟값/개수를 구하는데 **지금 선택이 앞의 선택에 의존**한다
    - 그리디로 반례가 나온다
    - 완전 탐색을 그려보면 **같은 부분 문제가 반복**된다

실행:  python 10_dp.py
===========================================================================
"""

import sys
from functools import lru_cache

sys.setrecursionlimit(10 ** 6)


# ---------------------------------------------------------------------------
# 1. 1차원 DP
# ---------------------------------------------------------------------------

def make_one(n: int) -> int:
    """1로 만들기 (백준 1463). 연산: /3, /2, -1. 최소 연산 횟수.

    dp[i] = i 를 1로 만드는 최소 연산 횟수
    dp[i] = min(dp[i-1], dp[i//2] if i%2==0, dp[i//3] if i%3==0) + 1

    그리디(큰 나눗셈 먼저)는 틀린다. n=10 이면 그리디 /2 -> 5 -> 4 -> 2 -> 1 (4회),
    최적은 10 -> 9 -> 3 -> 1 (3회). 이 반례를 기억해두면 DP 를 떠올리기 쉽다.
    """
    dp = [0] * (n + 1)
    for i in range(2, n + 1):
        best = dp[i - 1] + 1
        if i % 2 == 0:
            best = min(best, dp[i // 2] + 1)
        if i % 3 == 0:
            best = min(best, dp[i // 3] + 1)
        dp[i] = best
    return dp[n]


def count_123(n: int) -> int:
    """1,2,3 더하기 (백준 9095). n 을 1,2,3 의 합으로 나타내는 방법의 수.

    dp[i] = i 를 만드는 방법의 수 = dp[i-1] + dp[i-2] + dp[i-3]
    (마지막에 무엇을 더했는지로 경우를 나눈다)
    """
    dp = [0] * (max(n, 3) + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for step in (1, 2, 3):
            if i >= step:
                dp[i] += dp[i - step]
    return dp[n]


def stairs(scores: list) -> int:
    """계단 오르기 (백준 2579). 연속 3칸은 밟을 수 없고, 마지막 칸은 반드시 밟는다.

    "연속 3칸 금지" 라는 제약 때문에 dp[i] 만으로는 부족하다.
    이럴 때 **상태를 하나 추가**한다 -> dp[i][연속 밟은 개수]
    이 아이디어가 DP 확장의 핵심이다.
    """
    n = len(scores)
    if n == 0:
        return 0
    if n == 1:
        return scores[0]
    if n == 2:
        return scores[0] + scores[1]

    # dp[i][0] = i번째를 밟았고 i-1은 안 밟았다
    # dp[i][1] = i번째와 i-1을 연속으로 밟았다
    dp = [[0, 0] for _ in range(n)]
    dp[0][0] = scores[0]
    dp[1][0] = scores[1]
    dp[1][1] = scores[0] + scores[1]
    for i in range(2, n):
        dp[i][0] = max(dp[i - 2][0], dp[i - 2][1]) + scores[i]
        dp[i][1] = dp[i - 1][0] + scores[i]
    return max(dp[n - 1][0], dp[n - 1][1])


def tiling_2xn(n: int, mod: int = 10007) -> int:
    """2xn 타일링 (백준 11726). dp[i] = dp[i-1] + dp[i-2] (피보나치)
    마지막을 세로 1개로 채우거나, 가로 2개로 채우는 두 경우.
    """
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = (dp[i - 1] + dp[i - 2]) % mod
    return dp[n]


def easy_stairs(n: int, mod: int = 1_000_000_000) -> int:
    """쉬운 계단 수 (백준 10844). 인접한 자리의 차이가 1인 n자리 수의 개수.

    dp[길이][마지막 숫자]. 0 과 9 의 경계 처리가 이 문제의 전부다.
    첫 자리에 0 이 올 수 없다는 것도 놓치기 쉽다.
    """
    dp = [[0] * 10 for _ in range(n + 1)]
    for d in range(1, 10):
        dp[1][d] = 1                      # 첫 자리는 0 제외
    for length in range(2, n + 1):
        for d in range(10):
            if d > 0:
                dp[length][d] += dp[length - 1][d - 1]
            if d < 9:
                dp[length][d] += dp[length - 1][d + 1]
            dp[length][d] %= mod
    return sum(dp[n]) % mod


# ---------------------------------------------------------------------------
# 2. 2차원 DP
# ---------------------------------------------------------------------------

def triangle_max(triangle: list) -> int:
    """정수 삼각형 (백준 1932). 위에서 아래로 인접한 수를 골라 합의 최대.

    dp[r][c] = (r, c) 에 도달했을 때의 최대 합
    왼쪽 끝과 오른쪽 끝은 올 수 있는 경로가 하나뿐 -> 경계 처리 주의
    """
    n = len(triangle)
    dp = [row[:] for row in triangle]
    for r in range(1, n):
        for c in range(len(triangle[r])):
            if c == 0:
                dp[r][c] += dp[r - 1][0]
            elif c == len(triangle[r]) - 1:
                dp[r][c] += dp[r - 1][c - 1]
            else:
                dp[r][c] += max(dp[r - 1][c - 1], dp[r - 1][c])
    return max(dp[-1])


def rgb_street(costs: list) -> int:
    """RGB거리 (백준 1149). 인접한 집은 다른 색. 최소 비용.

    dp[i][색] = i번째 집을 그 색으로 칠했을 때의 최소 비용
             = costs[i][색] + min(dp[i-1][다른 색])
    "인접한 것끼리 같으면 안 된다" 유형의 표준형.
    """
    n = len(costs)
    dp = [row[:] for row in costs]
    for i in range(1, n):
        dp[i][0] += min(dp[i - 1][1], dp[i - 1][2])
        dp[i][1] += min(dp[i - 1][0], dp[i - 1][2])
        dp[i][2] += min(dp[i - 1][0], dp[i - 1][1])
    return min(dp[-1])


def grid_paths(grid: list) -> int:
    """등굣길 유형. (0,0) -> (n-1,m-1) 오른쪽/아래로만 이동. 경로 수.
    grid 에서 1 은 지날 수 없는 칸.
    """
    n, m = len(grid), len(grid[0])
    if grid[0][0] == 1:
        return 0
    dp = [[0] * m for _ in range(n)]
    dp[0][0] = 1
    for r in range(n):
        for c in range(m):
            if grid[r][c] == 1:
                dp[r][c] = 0
                continue
            if r > 0:
                dp[r][c] += dp[r - 1][c]
            if c > 0:
                dp[r][c] += dp[r][c - 1]
    return dp[n - 1][m - 1]


# ---------------------------------------------------------------------------
# 3. LIS (가장 긴 증가하는 부분 수열)
# ---------------------------------------------------------------------------

def lis_n2(arr: list) -> int:
    """O(N²) 기본형 (백준 11053).
    dp[i] = i번째를 마지막으로 하는 LIS 의 길이
    """
    if not arr:
        return 0
    n = len(arr)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def lis_nlogn(arr: list) -> int:
    """O(N log N). N 이 10만이면 이걸 써야 한다 (백준 12015).

    tails[k] = 길이가 k+1 인 증가 부분 수열의 **마지막 값 중 최솟값**
    bisect_left 로 들어갈 자리를 찾아 교체하거나 뒤에 붙인다.
    tails 자체는 LIS 가 아니다 (길이만 정확하다). 이 점을 오해하기 쉽다.
    """
    import bisect
    tails = []
    for v in arr:
        i = bisect.bisect_left(tails, v)
        if i == len(tails):
            tails.append(v)
        else:
            tails[i] = v
    return len(tails)


def lcs(a: str, b: str) -> int:
    """LCS (백준 9251). 가장 긴 공통 부분 수열의 길이.

    dp[i][j] = a[:i] 와 b[:j] 의 LCS 길이
      a[i-1] == b[j-1]  -> dp[i-1][j-1] + 1
      다르면            -> max(dp[i-1][j], dp[i][j-1])
    2차원 DP 의 가장 대표적인 형태. 인덱스를 1-based 로 두면 경계 처리가 편하다.
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


def edit_distance(a: str, b: str) -> int:
    """편집 거리. 삽입/삭제/교체로 a 를 b 로 만드는 최소 연산 수."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],       # 삭제
                                   dp[i][j - 1],       # 삽입
                                   dp[i - 1][j - 1])   # 교체
    return dp[n][m]


# ---------------------------------------------------------------------------
# 4. 배낭 (Knapsack)
# ---------------------------------------------------------------------------

def knapsack_01(items: list, capacity: int) -> int:
    """평범한 배낭 (백준 12865). 0/1 배낭. items: [(무게, 가치), ...]

    1차원으로 줄인 형태. **capacity 를 역순으로** 순회하는 게 핵심이다.
    정순으로 돌면 같은 물건을 여러 번 담게 되어 중복 배낭이 된다.
    이 한 줄이 0/1 배낭과 중복 배낭을 가른다.
    """
    dp = [0] * (capacity + 1)
    for weight, value in items:
        for c in range(capacity, weight - 1, -1):      # 역순
            dp[c] = max(dp[c], dp[c - weight] + value)
    return dp[capacity]


def knapsack_unbounded(items: list, capacity: int) -> int:
    """중복 배낭 (같은 물건을 여러 번). capacity 를 **정순으로** 순회한다."""
    dp = [0] * (capacity + 1)
    for weight, value in items:
        for c in range(weight, capacity + 1):          # 정순
            dp[c] = max(dp[c], dp[c - weight] + value)
    return dp[capacity]


def coin_count_ways(coins: list, target: int) -> int:
    """동전으로 target 을 만드는 **조합의 수** (순서 무시).
    동전 루프가 바깥, 금액 루프가 안쪽 -> 조합
    (반대로 하면 순열이 되어 답이 달라진다. 순서를 반드시 확인한다)
    """
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in coins:
        for amount in range(c, target + 1):
            dp[amount] += dp[amount - c]
    return dp[target]


def coin_min_count(coins: list, target: int) -> int:
    """target 을 만드는 최소 동전 개수. 불가능하면 -1.
    (그리디가 틀리는 경우의 정답. 02_sort_greedy.py 의 반례와 이어진다)
    """
    dp = [0] + [float("inf")] * target
    for amount in range(1, target + 1):
        for c in coins:
            if amount >= c and dp[amount - c] + 1 < dp[amount]:
                dp[amount] = dp[amount - c] + 1
    return dp[target] if dp[target] != float("inf") else -1


# ---------------------------------------------------------------------------
# 5. 메모이제이션 (top-down) — 점화식이 복잡할 때 더 쉽다
# ---------------------------------------------------------------------------

def n_expressions(n: int, target: int) -> int:
    """N으로 표현 (프로그래머스). n 을 최소 몇 개 사용해 target 을 만드는가.
    8개를 넘으면 -1.

    bottom-up 으로 짜기 까다로운 문제. 집합 DP + 메모이제이션이 자연스럽다.
    dp[count] = n 을 count 개 써서 만들 수 있는 수의 집합
    """
    dp = [set() for _ in range(9)]
    for count in range(1, 9):
        dp[count].add(int(str(n) * count))            # n, nn, nnn ...
        for left in range(1, count):
            right = count - left
            for a in dp[left]:
                for b in dp[right]:
                    dp[count].add(a + b)
                    dp[count].add(a - b)
                    dp[count].add(a * b)
                    if b != 0:
                        dp[count].add(a // b)
        if target in dp[count]:
            return count
    return -1


def fib_memo(n: int) -> int:
    """lru_cache 로 메모이제이션. 재귀 점화식을 그대로 옮길 수 있어 편하다.
    단, 재귀 깊이가 크면 스택이 터지므로 bottom-up 이 안전한 경우가 많다.
    """
    @lru_cache(maxsize=None)
    def f(k):
        if k < 2:
            return k
        return f(k - 1) + f(k - 2)

    return f(n)


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert make_one(10) == 3            # 10 -> 9 -> 3 -> 1
    assert make_one(2) == 1
    assert make_one(1) == 0

    assert count_123(4) == 7
    assert count_123(7) == 44
    assert count_123(1) == 1

    # 백준 2579 예제
    assert stairs([10, 20, 15, 25, 10, 20]) == 75
    assert stairs([10]) == 10
    assert stairs([10, 20]) == 30

    assert tiling_2xn(2) == 2
    assert tiling_2xn(9) == 55

    assert easy_stairs(1) == 9
    assert easy_stairs(2) == 17

    # 백준 1932 예제
    tri = [[7], [3, 8], [8, 1, 0], [2, 7, 4, 4], [4, 5, 2, 6, 5]]
    assert triangle_max(tri) == 30

    # 백준 1149 예제
    assert rgb_street([[26, 40, 83], [49, 60, 57], [13, 89, 99]]) == 96

    assert grid_paths([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
    assert grid_paths([[0, 0], [0, 0]]) == 2
    assert grid_paths([[0, 1], [1, 0]]) == 0

    # 백준 11053 예제
    assert lis_n2([10, 20, 10, 30, 20, 50]) == 4
    assert lis_nlogn([10, 20, 10, 30, 20, 50]) == 4
    assert lis_n2([]) == 0 and lis_nlogn([]) == 0
    assert lis_nlogn([5, 4, 3, 2, 1]) == 1

    # 백준 9251 예제
    assert lcs("ACAYKP", "CAPCAK") == 4
    assert lcs("", "abc") == 0

    assert edit_distance("sunday", "saturday") == 3
    assert edit_distance("abc", "abc") == 0

    # 백준 12865 예제
    assert knapsack_01([(6, 13), (4, 8), (3, 6), (5, 12)], 7) == 14
    assert knapsack_01([(10, 100)], 5) == 0
    assert knapsack_unbounded([(3, 5)], 9) == 15         # 3개 담는다

    assert coin_count_ways([1, 2, 5], 5) == 4            # 5 / 2+2+1 / 2+1+1+1 / 1x5
    assert coin_min_count([1, 4, 5], 8) == 2             # 4+4 (그리디는 4개)
    assert coin_min_count([3], 5) == -1

    # 프로그래머스 N으로 표현
    assert n_expressions(5, 12) == 4
    assert n_expressions(2, 11) == 3

    assert fib_memo(30) == 832040

    print("10_dp.py  OK")
