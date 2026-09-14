"""
07_heap.py — 힙 (우선순위 큐)
===========================================================================
Day 9. "매번 가장 작은(큰) 것을 꺼낸다"가 필요하면 힙이다.

정렬로 되는 것과 힙이 필요한 것의 구분
    한 번 정렬하고 끝     -> sorted()
    중간에 원소가 계속 추가/삭제되며 매번 최소/최대가 필요 -> 힙

핵심 3줄
    1) heapq 는 **최소 힙만** 있다. 최대 힙은 -value 로 넣고 꺼낼 때 다시 -
    2) 튜플을 넣으면 첫 원소로 정렬된다. (우선순위, 값) 형태를 쓴다
    3) push/pop 은 O(log N), heapify 는 O(N)

실행:  python 07_heap.py
===========================================================================
"""

import heapq

# ---------------------------------------------------------------------------
# 1. 최소 힙 / 최대 힙 / 절댓값 힙
# ---------------------------------------------------------------------------

def min_heap_ops(commands: list) -> list:
    """최소 힙 (백준 1927). 0 이면 pop(비어 있으면 0), 아니면 push."""
    heap = []
    out = []
    for c in commands:
        if c == 0:
            out.append(heapq.heappop(heap) if heap else 0)
        else:
            heapq.heappush(heap, c)
    return out


def max_heap_ops(commands: list) -> list:
    """최대 힙 (백준 11279). 부호를 반전해서 최소 힙을 최대 힙으로 쓴다."""
    heap = []
    out = []
    for c in commands:
        if c == 0:
            out.append(-heapq.heappop(heap) if heap else 0)
        else:
            heapq.heappush(heap, -c)
    return out


def abs_heap_ops(commands: list) -> list:
    """절댓값 힙 (백준 11286).
    절댓값이 작은 것 우선, 같으면 음수 우선.
    -> 정렬 키를 (abs(x), x) 튜플로 만들면 그대로 해결된다. 튜플 힙의 좋은 예.
    """
    heap = []
    out = []
    for c in commands:
        if c == 0:
            out.append(heapq.heappop(heap)[1] if heap else 0)
        else:
            heapq.heappush(heap, (abs(c), c))
    return out


# ---------------------------------------------------------------------------
# 2. 그리디 + 힙 — 대표 유형
# ---------------------------------------------------------------------------

def merge_cards_cost(cards: list) -> int:
    """카드 정렬하기 (백준 1715).
    두 묶음을 합칠 때 비용은 두 묶음 크기의 합. 전체 최소 비용.

    매번 **가장 작은 두 개**를 합치는 게 최적 (허프만 코딩과 같은 구조).
    "가장 작은 두 개"가 계속 바뀌므로 정렬 한 번으로는 안 되고 힙이 필요하다.
    """
    if len(cards) < 2:
        return 0
    heap = list(cards)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        total += a + b
        heapq.heappush(heap, a + b)
    return total


def spicy_scoville(scoville: list, k: int) -> int:
    """더 맵게 (프로그래머스). 모든 음식이 k 이상이 되도록 섞는 최소 횟수.
    섞은 음식 = 가장 안 매운 것 + 두 번째 * 2. 불가능하면 -1.
    """
    heap = list(scoville)
    heapq.heapify(heap)
    count = 0
    while heap[0] < k:
        if len(heap) < 2:
            return -1
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, a + b * 2)
        count += 1
    return count


def max_k_sum_pairs(a: list, b: list, k: int) -> int:
    """두 배열에서 각각 하나씩 뽑아 만든 합 중 가장 큰 k개의 합.
    모든 조합을 만들면 O(N*M). 힙으로 필요한 만큼만 꺼낸다.
    """
    heap = []
    for x in a:
        for y in b:
            total = x + y
            if len(heap) < k:
                heapq.heappush(heap, total)
            elif total > heap[0]:
                heapq.heapreplace(heap, total)      # pop + push 를 한 번에
    return sum(heap)


def kth_largest(arr: list, k: int) -> int:
    """K번째 큰 수. 크기 k 의 최소 힙을 유지하면 O(N log K).
    전체 정렬 O(N log N) 보다 K 가 작을 때 유리하다.
    """
    heap = []
    for v in arr:
        heapq.heappush(heap, v)
        if len(heap) > k:
            heapq.heappop(heap)         # 가장 작은 것을 버린다
    return heap[0]


# ---------------------------------------------------------------------------
# 3. 두 힙으로 중앙값 유지 — 가운데를 말해요 (백준 1655)
# ---------------------------------------------------------------------------

class MedianTracker:
    """수가 하나씩 추가될 때마다 중앙값을 O(log N) 에 알려준다.

    아이디어: 작은 절반은 **최대 힙**, 큰 절반은 **최소 힙**으로 나눠 담는다.
    두 힙의 크기 차이를 1 이하로 유지하면 중앙값은 항상 최대 힙의 top 이다.
    """

    def __init__(self):
        self.low = []       # 작은 절반 (최대 힙: -value 저장)
        self.high = []      # 큰 절반 (최소 힙)

    def add(self, value: int) -> None:
        if len(self.low) == len(self.high):
            heapq.heappush(self.low, -value)
        else:
            heapq.heappush(self.high, value)

        # 경계 정리: low 의 최대가 high 의 최소보다 크면 교환
        if self.high and -self.low[0] > self.high[0]:
            a = -heapq.heappop(self.low)
            b = heapq.heappop(self.high)
            heapq.heappush(self.low, -b)
            heapq.heappush(self.high, a)

    def median(self) -> int:
        """개수가 짝수면 작은 쪽 (백준 1655 규칙)."""
        return -self.low[0]


# ---------------------------------------------------------------------------
# 4. 작업 스케줄링 — 힙 두 개 조합 (디스크 컨트롤러 유형)
# ---------------------------------------------------------------------------

def average_wait_time(jobs: list) -> int:
    """디스크 컨트롤러 (프로그래머스).
    jobs: [(요청 시각, 소요 시간), ...]
    평균 대기 시간(요청 -> 완료)을 최소화하는 SJF 스케줄링. 결과는 소수점 버림.

    구조:
      1) 요청 시각 순으로 정렬해두고
      2) 현재 시각까지 도착한 작업을 힙(소요 시간 기준)에 넣고
      3) 그중 가장 짧은 것을 처리한다
      4) 힙이 비면 다음 요청 시각으로 시간을 점프한다  <- 이 처리를 빼먹기 쉽다
    """
    jobs = sorted(jobs)
    n = len(jobs)
    heap = []
    now = 0
    idx = 0
    total = 0
    done = 0
    while done < n:
        while idx < n and jobs[idx][0] <= now:
            heapq.heappush(heap, (jobs[idx][1], jobs[idx][0]))
            idx += 1
        if heap:
            duration, requested = heapq.heappop(heap)
            now += duration
            total += now - requested
            done += 1
        else:
            now = jobs[idx][0]          # 대기 중인 작업이 없으면 시간 점프
    return total // n


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 백준 1927 예제
    assert min_heap_ops([0, 12345678, 1, 2, 0, 0, 0, 0, 32, 0]) == \
        [0, 1, 2, 12345678, 0, 32]
    # 백준 11279 예제
    assert max_heap_ops([0, 12345678, 1, 2, 0, 0, 0, 0, 32, 0]) == \
        [0, 12345678, 2, 1, 0, 32]
    # 백준 11286 예제 (명령 18개, 그중 pop 10개)
    assert abs_heap_ops(
        [1, -1, 0, 0, 0, 1, 1, -1, -1, 2, -2, 0, 0, 0, 0, 0, 0, 0]) == \
        [-1, 1, 0, -1, -1, 1, 1, -2, 2, 0]

    # 백준 1715 예제: 10 20 40 -> (10+20)=30, (30+40)=70 -> 100
    assert merge_cards_cost([10, 20, 40]) == 100
    assert merge_cards_cost([10]) == 0
    assert merge_cards_cost([]) == 0

    assert spicy_scoville([1, 2, 3, 9, 10, 12], 7) == 2
    assert spicy_scoville([1, 1], 100) == -1
    assert spicy_scoville([10, 20], 5) == 0

    assert max_k_sum_pairs([1, 2], [3, 4], 2) == 11      # 2+4=6, 2+3=5 (또는 1+4)
    assert kth_largest([3, 1, 5, 12, 2, 11], 3) == 5
    assert kth_largest([1], 1) == 1

    # 백준 1655 예제
    mt = MedianTracker()
    medians = []
    for v in [1, 5, 2, 10, -99, 7, 5]:
        mt.add(v)
        medians.append(mt.median())
    assert medians == [1, 1, 2, 2, 2, 2, 5], medians

    # 프로그래머스 디스크 컨트롤러 예제: [[0,3],[1,9],[2,6]] -> 9
    assert average_wait_time([(0, 3), (1, 9), (2, 6)]) == 9
    # 중간에 빈 구간이 있는 경우 (시간 점프 처리 확인)
    assert average_wait_time([(0, 2), (10, 2)]) == 2

    print("07_heap.py  OK")
