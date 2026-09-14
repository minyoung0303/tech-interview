"""
05_binary_search.py — 이분 탐색과 파라메트릭 서치
===========================================================================
Day 6. 여기서 중요한 건 "정렬된 배열에서 값 찾기"가 아니다.
**답 자체를 이분 탐색하는 전환(파라메트릭 서치)** 이 이 유형의 본체다.

신호
    "~ 이하가 되도록 하는 최댓값"
    "K개로 나눌 수 있는 최소 길이"
    "N개를 만들 수 있는 가장 이른 시간"
    -> 답의 범위를 잡고, "이 답이 가능한가?"를 판정하는 함수를 만들어 이분 탐색

구현 규칙 (경계에서 틀리는 걸 막는 유일한 방법)
    1) 판정 함수 possible(x) 가 단조(monotonic)여야 한다
       x 가 커지면 계속 True (또는 계속 False) 여야 한다
    2) lo, hi 를 "답이 반드시 그 안에 있게" 넉넉히 잡는다
    3) while lo <= hi 형태와 while lo < hi 형태를 섞지 않는다. 하나만 쓴다

실행:  python 05_binary_search.py
===========================================================================
"""

import bisect

# ---------------------------------------------------------------------------
# 1. 기본형 — 값 찾기
# ---------------------------------------------------------------------------

def binary_search(arr: list, target: int) -> int:
    """정렬된 배열에서 target 의 인덱스. 없으면 -1.
    lo <= hi 형태로 통일한다.
    """
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def lower_bound(arr: list, target: int) -> int:
    """target 이상인 첫 인덱스. (= bisect_left)
    직접 구현할 수 있어야 파라메트릭 서치의 경계 처리가 흔들리지 않는다.
    """
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(arr: list, target: int) -> int:
    """target 보다 큰 첫 인덱스. (= bisect_right)"""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def count_equal(arr: list, target: int) -> int:
    """정렬된 배열에서 target 의 개수. 실전에서는 bisect 로 두 줄이면 된다."""
    return bisect.bisect_right(arr, target) - bisect.bisect_left(arr, target)


# ---------------------------------------------------------------------------
# 2. 파라메트릭 서치 — 이 유형의 본체
# ---------------------------------------------------------------------------

def max_lan_length(lans: list, need: int) -> int:
    """랜선 자르기 (백준 1654).
    주어진 랜선들을 잘라서 need 개 이상 만들 수 있는 **최대 길이**.

    판정: 길이 x 로 자르면 sum(l // x for l in lans) 개가 나온다.
    x 가 커지면 개수가 줄어든다 -> 단조. 이분 탐색 가능.
    """
    def possible(x: int) -> bool:
        return sum(l // x for l in lans) >= need

    lo, hi = 1, max(lans)
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if possible(mid):
            best = mid          # 가능하면 더 길게 시도
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def cut_trees(trees: list, need: int) -> int:
    """나무 자르기 (백준 2805).
    높이 H 로 자를 때 얻는 나무 길이 합이 need 이상이 되는 **최대 H**.

    H 가 커지면 얻는 양이 줄어든다 -> 단조.
    """
    def harvested(h: int) -> int:
        return sum(t - h for t in trees if t > h)

    lo, hi = 0, max(trees)
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if harvested(mid) >= need:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def install_routers(houses: list, count: int) -> int:
    """공유기 설치 (백준 2110).
    집 좌표에 공유기 count 개를 설치할 때 **인접한 공유기 간 최소 거리의 최대값**.

    이 문제가 파라메트릭 서치의 대표 예다.
    판정: 최소 간격을 d 로 두고 그리디하게 놓아 count 개 이상 놓을 수 있는가.
    d 가 커지면 놓을 수 있는 개수가 줄어든다 -> 단조.
    """
    houses = sorted(houses)

    def placeable(d: int) -> int:
        placed = 1
        last = houses[0]        # 첫 집에 놓는 게 항상 최적 (그리디)
        for h in houses[1:]:
            if h - last >= d:
                placed += 1
                last = h
        return placed

    lo, hi = 1, houses[-1] - houses[0]
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if placeable(mid) >= count:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def kth_in_multiplication_table(n: int, k: int) -> int:
    """K번째 수 (백준 1300). n x n 곱셈표(A[i][j] = i*j)를 1차원으로 정렬했을 때 k번째 수.

    표를 만들면 n=10^5 에서 10^10 개라 불가능하다.
    "값 x 이하인 원소가 몇 개인가"를 O(n) 에 셀 수 있으므로 **값을 이분 탐색**한다.
    i번째 행에서 x 이하인 개수는 min(x // i, n).
    """
    def count_le(x: int) -> int:
        return sum(min(x // i, n) for i in range(1, n + 1))

    lo, hi = 1, k
    answer = k
    while lo <= hi:
        mid = (lo + hi) // 2
        if count_le(mid) >= k:
            answer = mid        # 조건을 만족하는 가장 작은 값이 답
            hi = mid - 1
        else:
            lo = mid + 1
    return answer


def min_time_to_serve(times: list, people: int) -> int:
    """심사대/입국심사 유형. 각 창구의 처리 시간이 times, people 명을 처리하는 최소 시간.

    판정: 시간 t 안에 처리 가능한 인원 = sum(t // time).
    t 가 커지면 처리 인원이 늘어난다 -> 단조 (방향이 위 문제들과 반대다).
    그래서 possible 이면 hi 를 줄인다.
    """
    def served(t: int) -> int:
        return sum(t // x for x in times)

    lo, hi = 1, min(times) * people
    best = hi
    while lo <= hi:
        mid = (lo + hi) // 2
        if served(mid) >= people:
            best = mid
            hi = mid - 1        # 가능하면 더 짧게 시도
        else:
            lo = mid + 1
    return best


# ---------------------------------------------------------------------------
# 3. 실수 이분 탐색 — 반복 횟수로 끝낸다
# ---------------------------------------------------------------------------

def sqrt_binary(x: float, iterations: int = 100) -> float:
    """실수 이분 탐색은 `while lo < hi` 로 하면 부동소수 오차로 무한 루프가 난다.
    **고정 횟수 반복**(보통 100회)으로 끝내는 게 안전하다.
    100회면 구간이 2^-100 배가 되므로 어떤 정밀도 요구도 통과한다.
    """
    lo, hi = 0.0, max(1.0, x)
    for _ in range(iterations):
        mid = (lo + hi) / 2
        if mid * mid < x:
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------------------
# 4. 회전된 정렬 배열에서 찾기 (변형 문제 대비)
# ---------------------------------------------------------------------------

def search_rotated(arr: list, target: int) -> int:
    """[4,5,6,7,0,1,2] 처럼 한 번 회전된 정렬 배열에서 target 찾기.
    mid 를 기준으로 어느 쪽이 정렬되어 있는지 판단하는 것이 요령.
    """
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[lo] <= arr[mid]:                 # 왼쪽 절반이 정렬됨
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                   # 오른쪽 절반이 정렬됨
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    arr = [1, 3, 3, 3, 5, 7, 9]
    assert binary_search(arr, 5) == 4
    assert binary_search(arr, 4) == -1
    assert lower_bound(arr, 3) == 1 == bisect.bisect_left(arr, 3)
    assert upper_bound(arr, 3) == 4 == bisect.bisect_right(arr, 3)
    assert lower_bound(arr, 0) == 0
    assert lower_bound(arr, 100) == len(arr)
    assert count_equal(arr, 3) == 3
    assert count_equal(arr, 4) == 0

    # 백준 1654 예제: 802, 743, 457, 539 -> 11개 -> 200
    assert max_lan_length([802, 743, 457, 539], 11) == 200
    assert max_lan_length([10], 1) == 10

    # 백준 2805 예제: 20 15 10 17, 필요 7 -> 15
    assert cut_trees([20, 15, 10, 17], 7) == 15
    assert cut_trees([4, 42, 40, 26, 46], 20) == 36

    # 백준 2110 예제: 집 1 2 8 4 9, 공유기 3개 -> 3
    assert install_routers([1, 2, 8, 4, 9], 3) == 3
    assert install_routers([1, 100], 2) == 99

    # 백준 1300 예제: n=3, k=7 -> 6
    assert kth_in_multiplication_table(3, 7) == 6
    assert kth_in_multiplication_table(1, 1) == 1
    assert kth_in_multiplication_table(2, 3) == 2      # [1,2,2,4] -> 3번째는 2

    # 입국심사: 처리시간 [7, 10], 6명 -> 28
    assert min_time_to_serve([7, 10], 6) == 28

    assert abs(sqrt_binary(2) - 1.41421356237) < 1e-9
    assert abs(sqrt_binary(0.25) - 0.5) < 1e-9

    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_rotated([1], 1) == 0

    print("05_binary_search.py  OK")
