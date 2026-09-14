"""
08_graph.py — DFS / BFS / 격자 탐색
===========================================================================
Day 10~11. **코딩테스트 출제 비중 1위.** 여기에 시간을 가장 많이 쓴다.

가장 중요한 한 줄
    가중치가 없는 그래프에서 "최소 몇 번" 을 물으면 무조건 BFS 다.
    DFS 는 최단거리를 보장하지 않는다.

BFS 3대 원칙 (하나만 어겨도 틀리거나 시간 초과)
    1) visited 표시는 **큐에 넣는 순간** 한다. 꺼낼 때 하면 같은 노드가 중복 삽입된다
    2) 큐는 반드시 deque. list.pop(0) 은 O(N)
    3) 거리는 별도 dist 배열에 담거나 (노드, 거리) 튜플로 함께 넣는다

DFS 를 쓰는 경우
    영역 개수 / 연결 요소 세기, 모든 경로 탐색, 사이클 판정, 백트래킹

실행:  python 08_graph.py
===========================================================================
"""

import sys
from collections import defaultdict, deque

sys.setrecursionlimit(10 ** 6)

DR = (-1, 1, 0, 0)
DC = (0, 0, -1, 1)


# ---------------------------------------------------------------------------
# 1. 인접 리스트 만들기
# ---------------------------------------------------------------------------

def build_graph(n: int, edges: list, directed: bool = False) -> dict:
    """1..n 노드, edges: [(u, v), ...]
    번호가 1부터면 리스트 크기를 n+1 로 잡는 게 실전에서 편하다.
    """
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    for k in graph:
        graph[k].sort()          # 방문 순서를 정하는 문제에서는 정렬이 필요하다
    return graph


# ---------------------------------------------------------------------------
# 2. DFS / BFS 방문 순서 (백준 1260)
# ---------------------------------------------------------------------------

def dfs_recursive(graph: dict, start: int) -> list:
    visited = set()
    order = []

    def go(node):
        visited.add(node)
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in visited:
                go(nxt)

    go(start)
    return order


def dfs_stack(graph: dict, start: int) -> list:
    """재귀 한도가 걱정되면 이걸 쓴다.
    재귀와 같은 순서를 만들려면 인접 노드를 **역순으로** 넣어야 한다.
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
        for nxt in reversed(graph.get(node, [])):
            if nxt not in visited:
                stack.append(nxt)
    return order


def bfs_order(graph: dict, start: int) -> list:
    visited = {start}                 # 시작 노드도 넣을 때 표시
    order = []
    q = deque([start])
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in visited:
                visited.add(nxt)      # <- 꺼낼 때가 아니라 넣을 때
                q.append(nxt)
    return order


# ---------------------------------------------------------------------------
# 3. BFS 최단거리 — 이 패턴을 외운다
# ---------------------------------------------------------------------------

def bfs_shortest_path(graph: dict, start: int, goal: int) -> int:
    """간선 가중치가 모두 1일 때의 최단 거리. 도달 불가면 -1."""
    if start == goal:
        return 0
    dist = {start: 0}
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in graph.get(node, []):
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                if nxt == goal:
                    return dist[nxt]
                q.append(nxt)
    return -1


def bfs_with_path(graph: dict, start: int, goal: int):
    """경로까지 복원해야 할 때. parent 를 기록한다."""
    parent = {start: None}
    q = deque([start])
    while q:
        node = q.popleft()
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1]
        for nxt in graph.get(node, []):
            if nxt not in parent:
                parent[nxt] = node
                q.append(nxt)
    return None


def hide_and_seek(start: int, target: int, limit: int = 100_000) -> int:
    """숨바꼭질 (백준 1697). x -> x-1, x+1, 2x 로 이동. 최소 시간.

    "그래프처럼 안 보이는 것을 그래프로 보는" 연습.
    정점 = 위치, 간선 = 세 가지 이동. 가중치가 모두 1이므로 BFS.
    """
    if start == target:
        return 0
    dist = [-1] * (limit + 1)
    dist[start] = 0
    q = deque([start])
    while q:
        x = q.popleft()
        for nx in (x - 1, x + 1, x * 2):
            if 0 <= nx <= limit and dist[nx] == -1:
                dist[nx] = dist[x] + 1
                if nx == target:
                    return dist[nx]
                q.append(nx)
    return -1


# ---------------------------------------------------------------------------
# 4. 격자 BFS/DFS — 실전에서 가장 많이 나온다
# ---------------------------------------------------------------------------

def maze_shortest(grid: list) -> int:
    """미로 탐색 (백준 2178). (0,0) -> (n-1,m-1) 최소 칸 수 (시작·도착 포함).
    grid: 1 = 지날 수 있음, 0 = 벽
    """
    n, m = len(grid), len(grid[0])
    dist = [[0] * m for _ in range(n)]
    dist[0][0] = 1
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        if (r, c) == (n - 1, m - 1):
            return dist[r][c]
        for d in range(4):
            nr, nc = r + DR[d], c + DC[d]
            if 0 <= nr < n and 0 <= nc < m and grid[nr][nc] == 1 and dist[nr][nc] == 0:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return -1


def count_islands(grid: list, diagonal: bool = False) -> int:
    """단지번호붙이기 / 유기농 배추 (백준 2667, 1012). 연결 요소(영역) 개수.

    이중 루프를 돌면서 아직 방문하지 않은 1 을 만나면 BFS/DFS 로 한 덩어리를 전부 지운다.
    이 구조가 "영역 세기" 문제의 표준형이다.
    """
    if not grid or not grid[0]:
        return 0
    n, m = len(grid), len(grid[0])
    visited = [[False] * m for _ in range(n)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] \
        if diagonal else list(zip(DR, DC))
    count = 0
    for sr in range(n):
        for sc in range(m):
            if grid[sr][sc] != 1 or visited[sr][sc]:
                continue
            count += 1
            visited[sr][sc] = True
            q = deque([(sr, sc)])
            while q:
                r, c = q.popleft()
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < m \
                            and grid[nr][nc] == 1 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        q.append((nr, nc))
    return count


def island_sizes(grid: list) -> list:
    """각 영역의 크기를 오름차순으로. 단지번호붙이기의 실제 출력 형태."""
    n, m = len(grid), len(grid[0])
    visited = [[False] * m for _ in range(n)]
    sizes = []
    for sr in range(n):
        for sc in range(m):
            if grid[sr][sc] != 1 or visited[sr][sc]:
                continue
            size = 0
            visited[sr][sc] = True
            q = deque([(sr, sc)])
            while q:
                r, c = q.popleft()
                size += 1
                for d in range(4):
                    nr, nc = r + DR[d], c + DC[d]
                    if 0 <= nr < n and 0 <= nc < m \
                            and grid[nr][nc] == 1 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        q.append((nr, nc))
            sizes.append(size)
    return sorted(sizes)


def tomato_days(grid: list):
    """토마토 (백준 7576). 익은 토마토가 여러 개 -> **다중 시작점 BFS**.

    핵심: 시작점을 전부 큐에 먼저 넣는다. 그러면 한 번의 BFS 로
    "가장 가까운 시작점으로부터의 거리"가 계산된다.
    반환: (모두 익는 날수, 전부 익을 수 있는지)
      1 = 익음, 0 = 안 익음, -1 = 빈 칸
    """
    n, m = len(grid), len(grid[0])
    dist = [[-1] * m for _ in range(n)]
    q = deque()
    remaining = 0
    for r in range(n):
        for c in range(m):
            if grid[r][c] == 1:
                dist[r][c] = 0
                q.append((r, c))
            elif grid[r][c] == 0:
                remaining += 1

    days = 0
    while q:
        r, c = q.popleft()
        for d in range(4):
            nr, nc = r + DR[d], c + DC[d]
            if 0 <= nr < n and 0 <= nc < m and grid[nr][nc] == 0 and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                days = max(days, dist[nr][nc])
                remaining -= 1
                q.append((nr, nc))
    return (days, remaining == 0)


def fire_escape(grid: list):
    """불! (백준 4179). 불과 지훈이 **동시에** 퍼진다 -> BFS 두 번.

    순서가 중요하다. 불을 먼저 전부 BFS 해서 각 칸의 발화 시각을 구하고,
    그다음 사람 BFS 에서 "도착 시각 < 발화 시각" 인 칸만 지나갈 수 있게 한다.
    이 분리를 못 하면 아주 복잡해진다.
    grid: '.' 빈 칸, '#' 벽, 'J' 지훈, 'F' 불
    반환: 탈출 시간 (1-based) 또는 None
    """
    n, m = len(grid), len(grid[0])
    INF = float("inf")
    fire = [[INF] * m for _ in range(n)]
    fq = deque()
    start = None
    for r in range(n):
        for c in range(m):
            if grid[r][c] == "F":
                fire[r][c] = 0
                fq.append((r, c))
            elif grid[r][c] == "J":
                start = (r, c)

    while fq:                                  # 1) 불 확산 시각 계산
        r, c = fq.popleft()
        for d in range(4):
            nr, nc = r + DR[d], c + DC[d]
            if 0 <= nr < n and 0 <= nc < m and grid[nr][nc] != "#" and fire[nr][nc] == INF:
                fire[nr][nc] = fire[r][c] + 1
                fq.append((nr, nc))

    dist = [[-1] * m for _ in range(n)]        # 2) 사람 이동
    sr, sc = start
    dist[sr][sc] = 0
    q = deque([(sr, sc)])
    while q:
        r, c = q.popleft()
        for d in range(4):
            nr, nc = r + DR[d], c + DC[d]
            if not (0 <= nr < n and 0 <= nc < m):
                return dist[r][c] + 1          # 격자 밖으로 나가면 탈출
            if grid[nr][nc] == "#" or dist[nr][nc] != -1:
                continue
            if dist[r][c] + 1 >= fire[nr][nc]: # 불이 먼저 오거나 동시면 못 간다
                continue
            dist[nr][nc] = dist[r][c] + 1
            q.append((nr, nc))
    return None


def safe_zones(grid: list) -> int:
    """안전 영역 (백준 2468). 물 높이를 0..max 로 바꿔가며 영역 개수의 최대.
    "매개변수를 바꿔가며 연결 요소를 세는" 반복 패턴.
    """
    n, m = len(grid), len(grid[0])
    highest = max(max(row) for row in grid)
    best = 1                                   # 비가 안 올 때 최소 1
    for level in range(highest):
        mask = [[1 if grid[r][c] > level else 0 for c in range(m)] for r in range(n)]
        best = max(best, count_islands(mask))
    return best


# ---------------------------------------------------------------------------
# 5. 사이클 판정
# ---------------------------------------------------------------------------

def has_cycle_undirected(n: int, edges: list) -> bool:
    """무향 그래프 사이클 판정. 부모를 제외한 이미 방문한 노드를 만나면 사이클."""
    graph = build_graph(n, edges)
    visited = set()

    def go(node, parent):
        visited.add(node)
        for nxt in graph.get(node, []):
            if nxt == parent:
                continue
            if nxt in visited or go(nxt, node):
                return True
        return False

    for v in range(1, n + 1):
        if v not in visited and go(v, None):
            return True
    return False


def has_cycle_directed(n: int, edges: list) -> bool:
    """유향 그래프 사이클 판정. 0=미방문, 1=탐색 중, 2=완료.
    **탐색 중(1)인 노드를 다시 만나면 사이클.** 이 3색 표시가 핵심이다.
    """
    graph = build_graph(n, edges, directed=True)
    state = [0] * (n + 1)

    def go(node):
        state[node] = 1
        for nxt in graph.get(node, []):
            if state[nxt] == 1:
                return True
            if state[nxt] == 0 and go(nxt):
                return True
        state[node] = 2
        return False

    for v in range(1, n + 1):
        if state[v] == 0 and go(v):
            return True
    return False


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 백준 1260 예제: n=4, 간선 1-2, 1-3, 1-4, 2-4, 3-4, 시작 1
    g = build_graph(4, [(1, 2), (1, 3), (1, 4), (2, 4), (3, 4)])
    assert dfs_recursive(g, 1) == [1, 2, 4, 3]
    assert dfs_stack(g, 1) == [1, 2, 4, 3]
    assert bfs_order(g, 1) == [1, 2, 3, 4]

    assert bfs_shortest_path(g, 1, 4) == 1
    assert bfs_shortest_path(g, 1, 1) == 0
    g2 = build_graph(5, [(1, 2), (2, 3), (3, 4)])
    assert bfs_shortest_path(g2, 1, 4) == 3
    assert bfs_shortest_path(g2, 1, 5) == -1
    assert bfs_with_path(g2, 1, 4) == [1, 2, 3, 4]
    assert bfs_with_path(g2, 1, 5) is None

    # 백준 1697 예제: 5 -> 17 은 4초
    assert hide_and_seek(5, 17) == 4
    assert hide_and_seek(5, 5) == 0
    assert hide_and_seek(1, 2) == 1

    # 백준 2178 예제
    maze = [
        [1, 0, 1, 1, 1, 1],
        [1, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1],
    ]
    assert maze_shortest(maze) == 15
    assert maze_shortest([[1]]) == 1

    # 백준 2667 예제
    village = [
        [0, 1, 1, 0, 1, 0, 0],
        [0, 1, 1, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 1, 1, 1],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 0, 0, 0],
    ]
    assert count_islands(village) == 3
    assert island_sizes(village) == [7, 8, 9]

    # 대각선 연결이면 개수가 달라진다
    cross = [[1, 0], [0, 1]]
    assert count_islands(cross) == 2
    assert count_islands(cross, diagonal=True) == 1

    # 백준 7576 예제
    tomato = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1],
    ]
    assert tomato_days(tomato) == (8, True)
    assert tomato_days([[1, 1], [1, 1]]) == (0, True)
    assert tomato_days([[0, -1], [-1, 1]]) == (0, False)

    # 백준 4179 예제
    fire_map = [list("####"), list("#JF#"), list("#..#"), list("#..#"), list("#.##"),
                list("#.##"), list("####")]
    assert fire_escape(fire_map) is None       # 불이 먼저 막는다
    open_map = [list("...."), list(".J.."), list("...."), list("....")]
    assert fire_escape(open_map) == 2          # 불이 없으면 최단 탈출

    # 백준 2468 예제
    region = [
        [6, 8, 2, 6, 2],
        [3, 2, 3, 4, 6],
        [6, 7, 3, 3, 2],
        [7, 2, 5, 3, 6],
        [8, 9, 5, 2, 7],
    ]
    assert safe_zones(region) == 5

    assert has_cycle_undirected(3, [(1, 2), (2, 3), (3, 1)])
    assert not has_cycle_undirected(3, [(1, 2), (2, 3)])
    assert has_cycle_directed(3, [(1, 2), (2, 3), (3, 1)])
    assert not has_cycle_directed(3, [(1, 2), (1, 3), (2, 3)])

    print("08_graph.py  OK")
