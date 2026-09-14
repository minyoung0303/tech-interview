"""
02_sort_greedy.py — 정렬과 그리디
===========================================================================
Day 3. 이 유형의 핵심은 코드가 아니라 **정렬 기준**과 **그리디가 왜 성립하는가**다.

정렬
    key 에 튜플을 넣는 것 + 내림차순은 -x. 이 둘로 정렬 문제 대부분이 끝난다.
그리디
    "지금 가장 좋은 걸 고른다"가 전체 최적인 이유를 말할 수 있어야 답이다.
    면접에서 "왜 그리디가 되나요?"를 물으면 이 근거를 말한다.

실행:  python 02_sort_greedy.py
===========================================================================
"""

from functools import cmp_to_key

# ---------------------------------------------------------------------------
# 1. 정렬 key 패턴
# ---------------------------------------------------------------------------

def sort_multi_key(people: list) -> list:
    """(이름, 나이, 점수) 를 나이 오름차순 → 점수 내림차순 → 이름 오름차순.

    숫자는 -x 로 방향을 뒤집을 수 있지만 문자열은 못 한다.
    문자열 방향을 섞어야 하면 안정 정렬(stable sort) 성질을 이용해
    '덜 중요한 기준부터' 여러 번 정렬한다.
    """
    return sorted(people, key=lambda p: (p[1], -p[2], p[0]))


def sort_stable_trick(words: list) -> list:
    """길이 내림차순 → 사전순 오름차순.
    파이썬 sort 는 안정 정렬이므로, 덜 중요한 기준(사전순)을 먼저 정렬한 뒤
    더 중요한 기준(길이)으로 다시 정렬하면 원하는 결과가 나온다.
    """
    tmp = sorted(words)                       # 1) 사전순
    return sorted(tmp, key=len, reverse=True)  # 2) 길이 내림차순 (같으면 1)의 순서 유지)


def largest_number(nums: list) -> str:
    """숫자들을 이어붙여 가장 큰 수 만들기. (프로그래머스 '가장 큰 수')

    핵심: 자릿수가 달라서 단순 내림차순이 안 된다. [3, 30] -> "330"
    비교 기준은 "a+b 가 b+a 보다 큰가". 문자열을 3배로 늘려 비교하는 트릭도 같은 의미다.
    """
    strs = list(map(str, nums))

    def cmp(a, b):
        if a + b > b + a:
            return -1          # a 를 앞으로
        if a + b < b + a:
            return 1
        return 0

    strs.sort(key=cmp_to_key(cmp))
    result = "".join(strs)
    return "0" if result[0] == "0" else result   # [0,0,0] -> "0"


# ---------------------------------------------------------------------------
# 2. 그리디 — 대표 5문제
# ---------------------------------------------------------------------------

def coin_change_greedy(coins: list, target: int) -> int:
    """동전 0 (백준 11047). 최소 동전 개수.

    그리디가 되는 이유: 큰 동전이 작은 동전의 배수라는 조건이 있다.
    이 조건이 없으면 그리디는 틀린다 → DP 로 풀어야 한다. (10_dp.py 참고)
      반례: coins=[1, 4, 5], target=8  → 그리디 5+1+1+1=4개, 최적 4+4=2개
    """
    count = 0
    for c in sorted(coins, reverse=True):
        if target == 0:
            break
        count += target // c
        target %= c
    return count


def meeting_rooms(meetings: list) -> int:
    """회의실 배정 (백준 1931). 최대 몇 개의 회의를 넣을 수 있나.

    정렬 기준이 답이다: **끝나는 시간 오름차순** (같으면 시작 시간 오름차순).
    이유: 빨리 끝내면 남는 시간이 가장 많다 → 이후 선택지가 최대가 된다.
    시작 시간으로 정렬하면 틀린다. 이게 이 문제의 전부다.
    """
    meetings = sorted(meetings, key=lambda m: (m[1], m[0]))
    count = 0
    last_end = float("-inf")
    for start, end in meetings:
        if start >= last_end:
            count += 1
            last_end = end
    return count


def atm_waiting_time(times: list) -> int:
    """ATM (백준 11399). 대기 시간 합의 최소.

    짧은 사람부터 처리한다. 앞에 선 사람의 시간이 뒤 모두에게 더해지므로,
    짧은 것을 앞에 둘수록 총합이 작아진다.
    i번째(0-based)로 처리하는 사람의 시간은 (n - i) 번 더해진다.
    """
    times = sorted(times)
    n = len(times)
    return sum(t * (n - i) for i, t in enumerate(times))


def lost_parenthesis(expr: str) -> int:
    """잃어버린 괄호 (백준 1541). 최솟값 만들기.

    '-' 가 한 번 나오면 그 뒤는 전부 묶어서 빼는 게 최소다.
    그래서 '-' 로 쪼갠 뒤 첫 덩어리만 더하고 나머지는 전부 뺀다.
    """
    parts = expr.split("-")
    total = sum(int(x) for x in parts[0].split("+"))
    for part in parts[1:]:
        total -= sum(int(x) for x in part.split("+"))
    return total


def make_big_number(number: str, k: int) -> str:
    """큰 수 만들기 (프로그래머스). k개를 제거해 가장 큰 수.

    단조 스택 그리디: 앞에서부터 훑으며, 지금 숫자가 스택 top 보다 크면
    top 을 버린다(앞쪽 숫자가 더 큰 자릿값을 가지므로).
    O(N). 조합으로 완전 탐색하면 터진다.
    """
    stack = []
    remove = k
    for ch in number:
        while stack and remove > 0 and stack[-1] < ch:
            stack.pop()
            remove -= 1
        stack.append(ch)
    if remove:                      # 내림차순이라 하나도 못 버린 경우 뒤에서 자른다
        stack = stack[:-remove]
    return "".join(stack)


def lifeboat(people: list, limit: int) -> int:
    """구명보트 (프로그래머스). 보트 하나에 최대 2명, 무게 합 limit 이하.

    정렬 + 투 포인터 그리디: 가장 무거운 사람과 가장 가벼운 사람을 짝지어 본다.
    안 되면 무거운 사람은 혼자 태운다.
    """
    people = sorted(people)
    left, right = 0, len(people) - 1
    boats = 0
    while left <= right:
        if people[left] + people[right] <= limit:
            left += 1
        right -= 1
        boats += 1
    return boats


def min_max_pair_sum(arr: list) -> int:
    """작은 것과 큰 것을 짝지어 '최대 합'을 최소화하는 고전 패턴.
    정렬 후 양 끝을 묶는다.
    """
    arr = sorted(arr)
    left, right = 0, len(arr) - 1
    best = 0
    while left < right:
        best = max(best, arr[left] + arr[right])
        left += 1
        right -= 1
    return best


# ---------------------------------------------------------------------------
# 3. 그리디가 틀리는 경우를 직접 확인해본다 (중요)
# ---------------------------------------------------------------------------

def coin_change_dp(coins: list, target: int) -> int:
    """그리디가 틀리는 동전 조합에서의 정답. DP.
    "동전이 배수 관계인가"를 확인하는 습관을 들이기 위해 나란히 둔다.
    """
    INF = float("inf")
    dp = [0] + [INF] * target
    for i in range(1, target + 1):
        for c in coins:
            if i >= c and dp[i - c] + 1 < dp[i]:
                dp[i] = dp[i - c] + 1
    return dp[target] if dp[target] != INF else -1


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 정렬
    people = [("kim", 21, 90), ("lee", 20, 80), ("park", 21, 95), ("ahn", 20, 80)]
    assert sort_multi_key(people) == [
        ("ahn", 20, 80), ("lee", 20, 80),          # 나이 20, 점수 80 → 이름순
        ("park", 21, 95), ("kim", 21, 90),         # 나이 21, 점수 내림차순
    ]
    assert sort_stable_trick(["bb", "a", "cc", "b"]) == ["bb", "cc", "a", "b"]

    assert largest_number([6, 10, 2]) == "6210"
    assert largest_number([3, 30, 34, 5, 9]) == "9534330"
    assert largest_number([0, 0]) == "0"

    # 그리디
    # 백준 11047 예제: 1000*4 + 500 + 100*2 + 50 + 10*4 = 12개
    assert coin_change_greedy(
        [1, 5, 10, 50, 100, 500, 1000, 5000, 10000, 50000], 4790) == 12
    assert coin_change_greedy([1, 5, 10], 0) == 0

    assert meeting_rooms([(1, 4), (3, 5), (0, 6), (5, 7), (3, 8),
                          (5, 9), (6, 10), (8, 11), (8, 12), (2, 13), (12, 14)]) == 4
    assert meeting_rooms([(1, 1), (1, 2), (2, 2)]) == 3   # 시간 0짜리 회의 반례

    assert atm_waiting_time([3, 1, 4, 3, 2]) == 32

    assert lost_parenthesis("55-50+40") == -35
    assert lost_parenthesis("10+20+30+40") == 100
    assert lost_parenthesis("00009-00009") == 0

    assert make_big_number("1924", 2) == "94"
    assert make_big_number("1231234", 3) == "3234"
    assert make_big_number("4177252841", 4) == "775841"
    assert make_big_number("999", 2) == "9"          # 내림차순이면 뒤에서 자른다

    assert lifeboat([70, 50, 80, 50], 100) == 3
    assert lifeboat([70, 80, 50], 100) == 3

    assert min_max_pair_sum([1, 2, 4, 5]) == 6       # (1,5), (2,4)

    # 그리디가 틀리는 반례 — 이 차이를 직접 보고 넘어간다
    assert coin_change_greedy([1, 4, 5], 8) == 4     # 5+1+1+1
    assert coin_change_dp([1, 4, 5], 8) == 2         # 4+4  ← 정답
    print("그리디 반례 확인:  coins=[1,4,5], target=8  →  greedy 4개 / DP 2개")

    print("02_sort_greedy.py  OK")
