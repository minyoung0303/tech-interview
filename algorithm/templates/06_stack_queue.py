"""
06_stack_queue.py — 스택 / 큐 / 덱 / 단조 스택
===========================================================================
Day 8. 자료구조 자체는 쉽다. 중요한 건 **언제 스택을 떠올리는가**다.

스택 신호
    괄호 / 짝 맞추기
    "가장 가까운 ~" (오큰수, 탑, 히스토그램)
    되돌리기, 후위 표기식
    DFS 를 반복문으로 바꿀 때

큐 / 덱 신호
    순서대로 처리, 회전, BFS
    양쪽에서 넣고 빼기

절대 규칙
    큐는 반드시 collections.deque. list.pop(0) 은 O(N) 이라 시간 초과가 난다.

실행:  python 06_stack_queue.py
===========================================================================
"""

from collections import deque

# ---------------------------------------------------------------------------
# 1. 스택 기본 — 괄호
# ---------------------------------------------------------------------------

def is_valid_parentheses(s: str) -> bool:
    """괄호 (백준 9012). VPS 인지 판정."""
    stack = []
    for ch in s:
        if ch == "(":
            stack.append(ch)
        else:
            if not stack:              # 닫는 게 먼저 나오면 실패
                return False
            stack.pop()
    return not stack                   # 남아 있으면 실패


def is_valid_multi_brackets(s: str) -> bool:
    """여러 종류의 괄호. 짝 매핑을 dict 로 둔다."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return not stack


def stack_sequence(target: list):
    """스택 수열 (백준 1874).
    1..n 을 순서대로 push 하면서 target 순서로 pop 할 수 있는지.
    가능하면 '+'/'-' 연산 리스트, 불가능하면 None.
    """
    n = len(target)
    stack = []
    ops = []
    nxt = 1
    for want in target:
        while nxt <= want:             # 필요한 값까지 밀어 넣는다
            stack.append(nxt)
            ops.append("+")
            nxt += 1
        if not stack or stack[-1] != want:
            return None                # top 이 원하는 값이 아니면 불가능
        stack.pop()
        ops.append("-")
    return ops


def postfix_eval(tokens: list) -> float:
    """후위 표기식 계산. 스택의 교과서 예제."""
    stack = []
    for t in tokens:
        if t in "+-*/":
            b = stack.pop()
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(a / b)
        else:
            stack.append(float(t))
    return stack[0]


def remove_zero_sum(numbers: list) -> int:
    """제로 (백준 10773). 0 이 나오면 직전 수를 지운다. 최종 합."""
    stack = []
    for v in numbers:
        if v == 0:
            if stack:
                stack.pop()
        else:
            stack.append(v)
    return sum(stack)


# ---------------------------------------------------------------------------
# 2. 단조 스택 (Monotonic Stack) — "가장 가까운 ~" 유형의 핵심
# ---------------------------------------------------------------------------

def next_greater(arr: list) -> list:
    """오큰수 (백준 17298).
    각 원소의 오른쪽에서 처음으로 나오는 더 큰 수. 없으면 -1.

    아이디어: 스택에 "아직 답을 못 찾은 인덱스"를 담아둔다.
    새 값이 스택 top 의 값보다 크면 그게 top 의 답이다.
    스택은 항상 값이 내림차순(단조)으로 유지된다. O(N).
    """
    n = len(arr)
    result = [-1] * n
    stack = []                         # 인덱스를 담는다
    for i, v in enumerate(arr):
        while stack and arr[stack[-1]] < v:
            result[stack.pop()] = v
        stack.append(i)
    return result


def prev_greater_index(heights: list) -> list:
    """탑 (백준 2493).
    각 탑의 왼쪽에서 자기보다 크거나 같은 가장 가까운 탑의 번호(1-based). 없으면 0.
    """
    result = []
    stack = []                         # (높이, 번호) — 높이 내림차순 유지
    for i, h in enumerate(heights, start=1):
        while stack and stack[-1][0] < h:
            stack.pop()
        result.append(stack[-1][1] if stack else 0)
        stack.append((h, i))
    return result


def largest_rectangle(heights: list) -> int:
    """히스토그램에서 가장 큰 직사각형. 단조 스택의 대표 응용. O(N).

    각 막대를 높이로 하는 최대 폭을 구한다.
    스택에는 높이가 증가하는 인덱스만 남긴다.
    """
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):     # 끝에 0 을 붙여 스택을 비우게 한다
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] + 1 if stack else 0
            best = max(best, height * (i - left))
        stack.append(i)
    return best


# ---------------------------------------------------------------------------
# 3. 큐 / 덱
# ---------------------------------------------------------------------------

def josephus_last(n: int) -> int:
    """카드2 (백준 2164). 1..n 카드에서 맨 위를 버리고 다음 것을 맨 아래로.
    마지막에 남는 카드.
    """
    q = deque(range(1, n + 1))
    while len(q) > 1:
        q.popleft()                    # 버린다
        q.append(q.popleft())          # 다음 것을 맨 아래로
    return q[0]


def rotating_queue(n: int, targets: list) -> int:
    """회전하는 큐 (백준 1021). 원하는 원소를 앞으로 빼는 최소 회전 수.

    핵심: 목표 위치가 앞쪽에 가까우면 왼쪽 회전, 뒤쪽에 가까우면 오른쪽 회전.
    deque.rotate 를 쓰면 코드가 짧아진다.
    """
    q = deque(range(1, n + 1))
    moves = 0
    for t in targets:
        idx = q.index(t)
        if idx <= len(q) - idx:        # 왼쪽으로 도는 게 가깝다
            q.rotate(-idx)
            moves += idx
        else:
            r = len(q) - idx
            q.rotate(r)
            moves += r
        q.popleft()
    return moves


def printer_queue(priorities: list, target_index: int) -> int:
    """프린터 큐 (백준 1966). 목표 문서가 몇 번째로 인쇄되나 (1-based).

    큐에 (인덱스, 중요도) 를 담고, 남은 것 중 최대 중요도가 아니면 뒤로 보낸다.
    """
    q = deque(enumerate(priorities))
    order = 0
    while q:
        remaining_max = max(p for _, p in q)
        idx, pri = q.popleft()
        if pri == remaining_max:
            order += 1
            if idx == target_index:
                return order
        else:
            q.append((idx, pri))
    return -1


def sliding_window_max(arr: list, k: int) -> list:
    """크기 k 창의 최댓값들. 덱으로 O(N).

    덱에 인덱스를 값 내림차순으로 유지한다.
    - 창을 벗어난 인덱스는 앞에서 버린다
    - 새 값보다 작은 값은 뒤에서 버린다 (다시 최대가 될 일이 없다)
    """
    dq = deque()
    result = []
    for i, v in enumerate(arr):
        while dq and dq[0] <= i - k:            # 창 이탈
            dq.popleft()
        while dq and arr[dq[-1]] <= v:          # 쓸 일 없는 값 제거
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(arr[dq[0]])
    return result


# ---------------------------------------------------------------------------
# 4. DFS 를 스택으로 — 재귀 한도가 걱정될 때
# ---------------------------------------------------------------------------

def dfs_iterative(graph: dict, start: int) -> list:
    """재귀 대신 명시적 스택. 파이썬 재귀 한도(기본 1000)를 피할 수 있다.

    주의: 방문 순서를 재귀 DFS 와 똑같이 맞추려면
    인접 노드를 **역순으로** 넣어야 한다.
    """
    visited = set()
    order = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for nxt in sorted(graph.get(node, []), reverse=True):
            if nxt not in visited:
                stack.append(nxt)
    return order


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assert is_valid_parentheses("(())()")
    assert not is_valid_parentheses("(()(")
    assert not is_valid_parentheses(")(")
    assert is_valid_parentheses("")

    assert is_valid_multi_brackets("{[()]}")
    assert not is_valid_multi_brackets("{[(])}")

    assert stack_sequence([4, 3, 6, 8, 7, 5, 2, 1]) is not None
    assert stack_sequence([1, 2, 5, 3, 4, 8, 7, 6]) is None
    assert stack_sequence([1, 2]) == ["+", "-", "+", "-"]

    assert postfix_eval(["3", "4", "+", "2", "*"]) == 14.0

    # 백준 10773 예제: 남는 것은 1, 6 -> 7
    assert remove_zero_sum([1, 3, 5, 4, 0, 0, 7, 0, 0, 6]) == 7
    assert remove_zero_sum([0, 0]) == 0          # 빈 스택에 0 이 와도 죽지 않아야 한다

    assert next_greater([3, 5, 2, 7]) == [5, 7, 7, -1]
    assert next_greater([9, 5, 4, 8]) == [-1, 8, 8, -1]
    assert next_greater([1]) == [-1]

    assert prev_greater_index([6, 9, 5, 7, 4]) == [0, 0, 2, 2, 4]

    assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10     # 5,6 -> 5*2
    assert largest_rectangle([2]) == 2
    assert largest_rectangle([1, 1, 1, 1]) == 4

    assert josephus_last(6) == 4
    assert josephus_last(1) == 1

    assert rotating_queue(10, [1, 2, 3]) == 0
    assert rotating_queue(10, [2, 9, 5]) == 8
    assert rotating_queue(32, [27, 16, 30, 11, 6, 23]) == 59

    assert printer_queue([1, 1, 9, 1, 1, 1], 0) == 5
    assert printer_queue([1, 2, 3], 2) == 1

    assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert sliding_window_max([9], 1) == [9]

    graph = {1: [2, 3], 2: [4], 3: [4], 4: []}
    assert dfs_iterative(graph, 1) == [1, 2, 4, 3]

    print("06_stack_queue.py  OK")
