"""
09_shortest_path.py — 최단경로 / 위상정렬 / 유니온 파인드 / MST
===========================================================================
Day 12. 그래프의 두 번째 묶음.

무엇을 언제
    가중치 없음, 최단거리        -> BFS (08_graph.py)
    가중치 양수, 한 점에서 전체  -> 다익스트라   O(E log V)
    음수 간선 있음               -> 벨만-포드    O(VE)
    모든 쌍 최단거리, V <= 500   -> 플로이드     O(V³)
    연결 여부 / 그룹 판정        -> 유니온 파인드 (거의 O(1))
    선후 관계로 순서 정하기      -> 위상 정렬
    모든 정점을 최소 비용으로 연결 -> MST (크루스칼)

다익스트라에서 가장 흔한 실수
    visited 배열을 쓰는 것보다 "힙에서 꺼낸 거리가 기록된 거리보다 크면 스킵"이 안전하다.
    그리고 반드시 힙을 쓴다. 매번 최소를 선형 탐색하면 O(V²) 가 된다.

실행:  python 09_shortest_path.py
===========================================================================
"""

import heapq
from collections import defaultdict, deque

INF = float("inf")


# ---------------------------------------------------------------------------
# 1. 다익스트라
# ---------------------------------------------------------------------------

def dijkstra(n: int, edges: list, start: int) -> list:
    """1..n 노드. edges: [(u, v, w), ...] 단방향.
    반환: dist[1..n] (인덱스 0 은 사용하지 않음). 도달 불가는 INF.
    """
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))

    dist = [INF] * (n + 1)
    dist[start] = 0
    pq = [(0, start)]                      # (거리, 노드) — 거리가 앞이어야 정렬된다

    while pq:
        d, node = heapq.heappop(pq)
        if d > dist[node]:                 # 이미 더 짧은 경로로 처리됨 -> 스킵
            continue
        for nxt, w in graph[node]:
            nd = d + w
            if nd < dist[nxt]:
                dist[nxt] = nd
                heapq.heappush(pq, (nd, nxt))
    return dist


def dijkstra_with_path(n: int, edges: list, start: int, goal: int):
    """경로까지 복원. parent 를 갱신할 때 함께 기록한다."""
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append((v, w))

    dist = [INF] * (n + 1)
    parent = [0] * (n + 1)
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist[node]:
            continue
        for nxt, w in graph[node]:
            nd = d + w
            if nd < dist[nxt]:
                dist[nxt] = nd
                parent[nxt] = node
                heapq.heappush(pq, (nd, nxt))

    if dist[goal] == INF:
        return INF, []
    path = []
    cur = goal
    while cur:
        path.append(cur)
        cur = parent[cur]
    return dist[goal], path[::-1]


def party_max_distance(n: int, edges: list, target: int) -> int:
    """파티 (백준 1238). 각 학생이 target 에 갔다 오는 시간 중 최대.

    요령: 정방향 다익스트라(target -> 전체)와
    **간선을 뒤집은 그래프**의 다익스트라(전체 -> target)를 각각 한 번씩 돌린다.
    학생마다 다익스트라를 돌리면 O(V * E log V) 로 느리다. 이 뒤집기 아이디어가 핵심.
    """
    reversed_edges = [(v, u, w) for u, v, w in edges]
    to_target = dijkstra(n, reversed_edges, target)   # i -> target
    from_target = dijkstra(n, edges, target)          # target -> i
    return max(to_target[i] + from_target[i] for i in range(1, n + 1))


# ---------------------------------------------------------------------------
# 2. 플로이드 워셜 — 모든 쌍. V가 작을 때만
# ---------------------------------------------------------------------------

def floyd_warshall(n: int, edges: list) -> list:
    """O(V³). V <= 500 정도까지. 3중 루프의 **k 가 가장 바깥**이어야 한다.
    순서를 틀리면 조용히 오답이 나온다.
    """
    dist = [[INF] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)    # 중복 간선 방어

    for k in range(1, n + 1):              # 경유지가 바깥 루프
        for i in range(1, n + 1):
            if dist[i][k] == INF:
                continue
            for j in range(1, n + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


# ---------------------------------------------------------------------------
# 3. 벨만-포드 — 음수 간선 / 음수 사이클 탐지
# ---------------------------------------------------------------------------

def bellman_ford(n: int, edges: list, start: int):
    """반환: (dist, has_negative_cycle)
    V-1 번 갱신한 뒤 한 번 더 갱신되면 음수 사이클이 있다.
    """
    dist = [INF] * (n + 1)
    dist[start] = 0
    for i in range(n):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break
        if i == n - 1:                     # n번째에도 갱신 -> 음수 사이클
            return dist, True
    return dist, False


# ---------------------------------------------------------------------------
# 4. 유니온 파인드 (Disjoint Set)
# ---------------------------------------------------------------------------

class UnionFind:
    """경로 압축 + union by size. 사실상 O(1).

    "연결되어 있나요?", "같은 그룹인가요?" 에 답하는 가장 빠른 도구.
    DFS 로도 되지만 간선이 계속 추가되는 상황에서는 이게 압도적으로 편하다.
    """

    def __init__(self, n: int):
        self.parent = list(range(n + 1))
        self.size = [1] * (n + 1)
        self.groups = n                    # 그룹 개수 (0번은 세지 않음)

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # 경로 압축
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                   # 이미 같은 집합 -> 이 간선은 사이클을 만든다
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.groups -= 1
        return True

    def connected(self, a: int, b: int) -> bool:
        return self.find(a) == self.find(b)


def kruskal_mst(n: int, edges: list):
    """최소 스패닝 트리 (백준 1197). 반환: (총 비용, 사용한 간선 수)

    간선을 가중치 순으로 정렬하고, 사이클을 만들지 않는 것만 채택한다.
    "사이클을 만드는가"를 유니온 파인드가 O(1) 에 판정해준다.
    """
    uf = UnionFind(n)
    total = 0
    used = 0
    for w, u, v in sorted(edges):
        if uf.union(u, v):
            total += w
            used += 1
            if used == n - 1:              # 트리가 완성되면 조기 종료
                break
    return total, used


# ---------------------------------------------------------------------------
# 5. 위상 정렬 (Topological Sort)
# ---------------------------------------------------------------------------

def topological_sort(n: int, edges: list):
    """줄 세우기 (백준 2252). 반환: 순서 리스트. 사이클이 있으면 None.

    진입 차수가 0 인 노드부터 꺼낸다. Kahn 알고리즘.
    사이클 판정에도 쓸 수 있다 — 결과 길이가 n 보다 작으면 사이클이 있다.
    """
    graph = defaultdict(list)
    indegree = [0] * (n + 1)
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    q = deque(v for v in range(1, n + 1) if indegree[v] == 0)
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)
    return order if len(order) == n else None


def topological_sort_lexicographic(n: int, edges: list):
    """사전순으로 가장 앞선 위상 정렬. deque 대신 힙을 쓰면 된다.
    "여러 답이 가능할 때 가장 작은 것"을 요구하는 변형에 쓴다.
    """
    graph = defaultdict(list)
    indegree = [0] * (n + 1)
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    pq = [v for v in range(1, n + 1) if indegree[v] == 0]
    heapq.heapify(pq)
    order = []
    while pq:
        node = heapq.heappop(pq)
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                heapq.heappush(pq, nxt)
    return order if len(order) == n else None


# ---------------------------------------------------------------------------
# 자체 검증
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 백준 1753 예제: n=5, start=1
    edges = [(5, 1, 1), (1, 2, 2), (1, 3, 3), (2, 3, 4), (2, 4, 5), (3, 4, 6)]
    dist = dijkstra(5, edges, 1)
    assert dist[1] == 0
    assert dist[2] == 2
    assert dist[3] == 3
    assert dist[4] == 7
    assert dist[5] == INF

    d, path = dijkstra_with_path(5, edges, 1, 4)
    assert d == 7 and path == [1, 2, 4], (d, path)
    assert dijkstra_with_path(5, edges, 1, 5) == (INF, [])

    # 백준 1238 예제: n=4, target=2 -> 10
    party = [(1, 2, 4), (1, 3, 2), (1, 4, 7), (2, 1, 1),
             (2, 3, 5), (3, 1, 2), (3, 4, 4), (4, 2, 3)]
    assert party_max_distance(4, party, 2) == 10

    # 플로이드
    fw = floyd_warshall(4, [(1, 2, 1), (2, 3, 1), (3, 4, 1), (1, 4, 10)])
    assert fw[1][4] == 3
    assert fw[1][1] == 0
    assert fw[4][1] == INF

    # 벨만-포드
    bf_dist, neg = bellman_ford(3, [(1, 2, 4), (1, 3, 3), (2, 3, -2)], 1)
    assert not neg and bf_dist[3] == 2
    _, neg2 = bellman_ford(3, [(1, 2, 1), (2, 3, -3), (3, 2, 1)], 1)
    assert neg2, "음수 사이클을 잡아야 한다"

    # 유니온 파인드
    uf = UnionFind(6)
    assert uf.groups == 6
    assert uf.union(1, 2)
    assert uf.union(2, 3)
    assert not uf.union(1, 3)              # 이미 같은 집합
    assert uf.connected(1, 3)
    assert not uf.connected(1, 4)
    assert uf.groups == 4                  # {1,2,3}, {4}, {5}, {6}

    # 백준 1197 예제: 총 비용 3
    mst_edges = [(1, 1, 2), (2, 2, 3), (3, 1, 3)]     # (w, u, v)
    total, used = kruskal_mst(3, mst_edges)
    assert (total, used) == (3, 2)

    # 위상 정렬 (백준 2252 예제)
    order = topological_sort(3, [(1, 3), (2, 3)])
    assert order in ([1, 2, 3], [2, 1, 3]), order
    assert topological_sort(2, [(1, 2), (2, 1)]) is None      # 사이클
    assert topological_sort_lexicographic(4, [(1, 3), (2, 3), (3, 4)]) == [1, 2, 3, 4]

    print("09_shortest_path.py  OK")
