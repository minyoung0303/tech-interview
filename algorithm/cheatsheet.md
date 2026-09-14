# 파이썬 코딩테스트 치트시트

> 문제 풀기 전 **30초 훑기용**. 외우려고 읽지 말고, 필요할 때 찾는 색인으로 쓴다.
> 계획은 [plan.md](./plan.md), 실행 가능한 템플릿은 [templates/](./templates)에 있다.

---

## 1. 시작 골격 (매번 이걸로 시작한다)

```python
import sys
input = sys.stdin.readline          # 반드시. 안 쓰면 입력 많은 문제에서 시간 초과
sys.setrecursionlimit(10 ** 6)      # 재귀 DFS를 쓸 때만

def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    print(max(arr))

solve()
```

`input = sys.stdin.readline`은 **개행 문자를 포함**한다.
- 숫자: `int(input())` — 알아서 무시된다
- 문자열: `input().strip()` — **꼭 붙인다**

---

## 2. 입력 패턴

```python
n = int(input())                                   # 정수 하나
n, m = map(int, input().split())                   # 한 줄에 여러 개
arr = list(map(int, input().split()))              # 한 줄 배열
grid = [list(map(int, input().split()))            # 2차원 (공백 구분)
        for _ in range(n)]
grid = [list(input().strip()) for _ in range(n)]   # 2차원 (붙어 있는 문자)
grid = [[int(c) for c in input().strip()]          # 2차원 (붙어 있는 숫자)
        for _ in range(n)]
pairs = [tuple(map(int, input().split()))          # 좌표/간선 목록
         for _ in range(m)]

# 줄 수를 모를 때 (EOF까지)
for line in sys.stdin:
    if not line.strip():
        continue
    a, b = map(int, line.split())

# 전체를 한 번에 (가장 빠름)
data = sys.stdin.read().split()
```

## 3. 출력 패턴

```python
print(*arr)                              # 공백 구분: 1 2 3
print('\n'.join(map(str, arr)))          # 줄바꿈 구분 — 반복 print보다 훨씬 빠르다
sys.stdout.write(f"{a} {b}\n")
print(f"{x:.6f}")                        # 소수 6자리
print("YES" if ok else "NO")
```

**출력이 수만 줄이면 모아서 한 번에 출력한다.** `print`를 10만 번 호출하면 그것만으로 느리다.

---

## 4. 자료구조 선택표

| 필요한 것 | 쓰는 것 | 복잡도 |
|---|---|---|
| 순서 있는 목록, 인덱스 접근 | `list` | 접근 O(1), 중간 삽입/삭제 O(N) |
| **앞뒤에서 넣고 빼기** (큐, 덱) | `collections.deque` | 양쪽 O(1) |
| **존재 확인, 중복 제거** | `set` | O(1) |
| **키 → 값** | `dict` | O(1) |
| **개수 세기** | `collections.Counter` | O(1) |
| 없는 키에 기본값 | `collections.defaultdict` | O(1) |
| **항상 최소(최대)값 꺼내기** | `heapq` | push/pop O(log N) |
| 정렬된 배열에 삽입 위치 찾기 | `bisect` | O(log N) |
| 스택 | `list` + `append`/`pop` | O(1) |

> **`list`에 `in`을 쓰면 O(N)이다.** 존재 확인이 반복되면 무조건 `set`으로 바꾼다.
> 이것 하나로 시간 초과가 풀리는 경우가 아주 많다.

---

## 5. 자주 쓰는 함수

### 정렬

```python
arr.sort()                                    # 제자리, None 반환
new = sorted(arr)                             # 새 리스트
arr.sort(reverse=True)
arr.sort(key=lambda x: x[1])                  # 두 번째 원소 기준
arr.sort(key=lambda x: (x[1], -x[2], x[0]))   # 다중 기준 (오름, 내림, 오름)
arr.sort(key=lambda s: (len(s), s))           # 길이 → 사전순

# 문자열을 숫자처럼 정렬 (자릿수 다름 주의)
nums.sort(key=lambda x: x * 3, reverse=True)  # "가장 큰 수" 만들기 유형
```

**`key`에 튜플을 넣는 것과 `-`로 방향을 뒤집는 것**만 알면 정렬 문제 대부분이 끝난다.
문자열은 `-`를 못 붙이니 그때는 `sorted`를 두 번 하거나 `functools.cmp_to_key`를 쓴다.

### collections

```python
from collections import deque, Counter, defaultdict

q = deque([1, 2, 3])
q.append(4); q.appendleft(0)
q.pop(); q.popleft()
q.rotate(1)                       # 오른쪽으로 회전 (회전 큐 문제)

c = Counter("aabbbc")             # {'b':3, 'a':2, 'c':1}
c.most_common(2)                  # [('b',3), ('a',2)]
c1 - c2                           # 차집합 (완주하지 못한 선수 유형)

g = defaultdict(list)             # 그래프 인접 리스트
g[1].append(2)
cnt = defaultdict(int)
cnt['x'] += 1                     # KeyError 없음
```

### heapq

```python
import heapq

h = []
heapq.heappush(h, 3)
smallest = heapq.heappop(h)       # 최소 힙
heapq.heappush(h, -5)             # 최대 힙 = 부호 반전해서 넣고 꺼낼 때 다시 반전
heapq.heappush(h, (dist, node))   # 튜플 → 첫 원소로 정렬
heapq.heapify(arr)                # 리스트를 O(N)에 힙으로
heapq.nsmallest(3, arr)
```

### bisect

```python
import bisect

i = bisect.bisect_left(arr, x)    # x가 들어갈 가장 왼쪽 위치 (== x의 첫 등장 인덱스)
j = bisect.bisect_right(arr, x)   # x보다 큰 첫 위치
count_of_x = j - i                # 정렬된 배열에서 x의 개수 — 자주 쓴다
bisect.insort(arr, x)             # 정렬 유지하며 삽입 (삽입 자체는 O(N))
```

### itertools

```python
from itertools import permutations, combinations, product, accumulate

list(permutations([1,2,3], 2))            # 순열 (순서 있음) 6개
list(combinations([1,2,3], 2))            # 조합 (순서 없음) 3개
list(product([0,1], repeat=3))            # 중복 순열 8개 — 완전 탐색에 유용
list(accumulate([1,2,3,4]))               # 누적합 [1,3,6,10]
```

> N이 작으면(≤ 10) `permutations`/`product`로 **완전 탐색이 가장 빠른 정답**이다.
> 직접 백트래킹을 짜기 전에 이걸 먼저 고려한다.

### 수학 / 진법 / 문자

```python
divmod(7, 2)                # (3, 1)
abs(-3); pow(2, 10); pow(2, 10, 1000)   # 마지막은 모듈러 거듭제곱
import math
math.gcd(12, 18); math.lcm(4, 6)        # lcm은 3.9+
math.ceil(7/2); -(-7//2)                # 올림 나눗셈 (후자가 정수 연산이라 안전)
math.isqrt(10)                          # 정수 제곱근

bin(10)[2:]; int('1010', 2)             # 2진 변환
format(255, 'x')                        # 16진
ord('a'); chr(97)                       # 97, 'a'
ord('C') - ord('A')                     # 알파벳 인덱스
s.isdigit(); s.isalpha(); s.upper()
```

### 2차원 배열

```python
grid = [[0] * m for _ in range(n)]      # ✅
grid = [[0] * m] * n                    # ❌ 같은 행을 n번 참조한다

for r in range(n):
    for c in range(m):
        ...

# 방향 배열 — 격자 문제의 기본
dr = (-1, 1, 0, 0)
dc = (0, 0, -1, 1)
for d in range(4):
    nr, nc = r + dr[d], c + dc[d]
    if 0 <= nr < n and 0 <= nc < m:
        ...

# 8방향
D8 = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))

# 전치 / 90도 회전
transposed = list(zip(*grid))
rotated = [list(row) for row in zip(*grid[::-1])]   # 시계 방향 90도
```

---

## 6. 복잡도 역산표

| N | 허용 복잡도 | 알고리즘 |
|---|---|---|
| ≤ 10 | O(N!) | 완전 순열, 백트래킹 |
| ≤ 25 | O(2^N) | 부분집합, 비트마스크 |
| ≤ 500 | O(N³) | 플로이드 워셜 |
| ≤ 5,000 | O(N²) | 2중 루프 DP |
| ≤ 100,000 | **O(N log N)** | 정렬, 이분 탐색, 힙, 다익스트라 |
| ≤ 1,000,000 | **O(N)** | 투 포인터, 누적합 |
| ≥ 10^12 | O(log N) | 이분 탐색, 수식 |

**파이썬은 1초에 약 1,000만~2,000만 연산**으로 잡는다. C++ 기준 문제라면 PyPy 제출을 고려한다.

---

## 7. 유형 판정 신호

| 문제 표현 | 유형 |
|---|---|
| "최소 몇 번", 가중치 없는 최단 거리 | **BFS** |
| 가중치 있는 최단 거리 | **다익스트라** |
| 모든 경우, 가능한 조합 | **백트래킹 / itertools** |
| 최댓값·최솟값 + 선택이 앞 선택에 의존 | **DP** |
| 정렬하면 답이 보이는 최대 개수 | **그리디** |
| 연속 구간, 부분 수열의 합 | **투 포인터 / 슬라이딩 윈도우 / 누적합** |
| "~이하가 되게 하는 최댓값" | **파라메트릭 서치** |
| 가장 가까운 큰 값, 괄호, 되돌리기 | **스택** |
| K번째, 매번 최소/최대 | **힙** |
| 연결 여부, 같은 그룹 | **유니온 파인드 / DFS** |
| 선후 관계로 순서 정하기 | **위상 정렬** |
| 존재 여부 반복 확인 | **set / dict** |

---

## 8. 반례 체크리스트 (제출 직전 10초)

- [ ] N = 1, 원소 1개
- [ ] 빈 입력 / 빈 문자열
- [ ] 최댓값·최솟값 (음수 포함? 0 포함?)
- [ ] 중복 원소
- [ ] 시작점 == 도착점
- [ ] 답이 없을 때의 출력 (`-1`? `0`? 빈 줄?)
- [ ] 그래프가 **연결되어 있지 않은** 경우
- [ ] 자기 루프, 양방향/단방향 혼동
- [ ] 나눗셈에서 0으로 나누기
- [ ] 출력 형식 — 대소문자, 공백, 개행

---

## 9. 파이썬 함정 요약

| 함정 | 대응 |
|---|---|
| `input()` 느림 | `input = sys.stdin.readline` |
| 재귀 한도 | `sys.setrecursionlimit(10**6)`, 깊으면 스택 DFS |
| `list.pop(0)` O(N) | `deque.popleft()` |
| 문자열 `+=` 반복 | `''.join(list)` |
| 리스트 `in` O(N) | `set` |
| `[[0]*m]*n` | `[[0]*m for _ in range(n)]` |
| `heapq` 최소 힙만 | 최대 힙은 `-value` |
| `-7 // 2 == -4` | 올림 나눗셈은 `-(-a//b)` |
| 백트래킹 결과 공유 | `result.append(path[:])` |
| BFS `visited` 시점 | **큐에 넣을 때** 표시 |
| `map` 재사용 불가 | `list(map(...))` |
| 얕은 복사 | `copy.deepcopy` 또는 슬라이스 |
