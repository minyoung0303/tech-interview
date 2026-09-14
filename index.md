# 인덱스 (Index)

> 기준: MySQL 8.x / InnoDB
> 실제 면접 질문: "인덱스에 대해 얼마나 알고 있는지 설명해봐라"
> 공고 필수 요건이 "SQL 쿼리 성능 개선 경험"이었다. **이 주제가 그 자리의 핵심이다.**

---

## 0. 30초 답변 스크립트

> "인덱스는 데이터를 정렬된 자료구조로 따로 유지해서 조회 시 풀 스캔을 피하게 해주는 장치입니다.
> InnoDB는 B+Tree를 쓰고, PK 기반 클러스터드 인덱스와 세컨더리 인덱스로 나뉩니다.
> 구조, 복합 인덱스 설계 원칙, 인덱스를 못 타는 경우, 그리고 EXPLAIN으로 확인하는 방법
> 순서로 말씀드리겠습니다. 쓰기 성능 트레이드오프도 있어서 그것도 같이 보겠습니다."

**"쓰기 트레이드오프도 있습니다"를 먼저 꺼내면 인상이 크게 달라진다.**
인덱스를 "많이 걸면 좋은 것"으로 이해하는 지원자와 바로 구분된다.

---

## 1. 왜 필요한가

인덱스가 없으면 조건에 맞는 행을 찾기 위해 테이블 전체를 읽는다 (풀 테이블 스캔, O(N)).
인덱스가 있으면 정렬된 트리를 타고 내려가 O(log N)에 찾는다.

100만 행 테이블에서 100만 번 비교 대신 20번 정도의 비교로 끝난다는 뜻이다.

**단, 항상 이득은 아니다.** 조회 결과가 테이블의 상당 부분(대략 20~30% 이상)이면
인덱스를 타고 랜덤 I/O를 반복하는 것보다 순차적으로 다 읽는 게 빠르다.
그래서 옵티마이저가 일부러 인덱스를 무시하고 풀 스캔을 고르는 경우가 있다.

---

## 2. 구조: B+Tree

InnoDB의 인덱스는 B-Tree 계열, 정확히는 **B+Tree**다.

```
                 [ 30 | 70 ]              ← 루트
                /     |     \
        [10|20]   [40|50|60]   [80|90]    ← 브랜치
         /  |  \    ...
    [리프] ↔ [리프] ↔ [리프] ↔ [리프]      ← 리프 (양방향 연결 리스트)
```

B+Tree의 특징 두 개가 중요하다.

1. **데이터(또는 데이터 포인터)는 리프 노드에만 있다.** 브랜치는 길잡이 역할만 한다.
   덕분에 브랜치가 가벼워서 트리 높이가 낮게 유지된다 (보통 3~4단계).
2. **리프 노드끼리 양방향 연결 리스트로 이어져 있다.**
   그래서 범위 조회(`BETWEEN`, `>`, `<`)와 `ORDER BY`가 효율적이다. 하나 찾고 옆으로 쭉 훑으면 된다.

### 왜 해시 인덱스가 아니라 B+Tree인가 (자주 나오는 꼬리질문)

해시 인덱스는 등호 비교(`=`)만 O(1)로 처리하고, **범위 조회와 정렬을 전혀 못 한다.**
실무 쿼리 대부분이 범위나 정렬을 포함하므로 범용 인덱스는 B+Tree여야 한다.
InnoDB에는 내부적으로 Adaptive Hash Index가 있지만 이건 옵티마이저가 자동으로 쓰는 것이고
사용자가 만들 수 있는 건 아니다. (MEMORY 엔진은 해시 인덱스를 지원한다.)

---

## 3. 클러스터드 인덱스 vs 세컨더리 인덱스

**이 구분이 InnoDB 인덱스 이해의 핵심이다. 반드시 설명할 수 있어야 한다.**

### 클러스터드 인덱스 (= PK)

InnoDB에서 **테이블 데이터 자체가 PK 순서로 정렬되어 저장된다.**
PK 인덱스의 리프 노드가 곧 행 전체 데이터다. 별도의 데이터 영역이 없다.

PK를 명시하지 않으면 InnoDB는 이 순서로 대체 키를 찾는다.
1. `NOT NULL`인 UNIQUE 인덱스
2. 없으면 내부적으로 숨은 `DB_ROW_ID`(6바이트)를 만들어 쓴다

### 세컨더리 인덱스

리프 노드에 **인덱스 컬럼 값 + PK 값**이 저장된다. 행 데이터는 없다.

그래서 세컨더리 인덱스로 조회하면 2단계가 된다.

```
1. 세컨더리 인덱스에서 조건에 맞는 항목을 찾아 PK를 얻는다
2. 그 PK로 클러스터드 인덱스를 다시 탐색해 행 전체를 읽는다   ← 이게 "랜덤 I/O"
```

이 2단계 조회를 부르는 이름이 있다.

- MySQL 문서/EXPLAIN 용어로는 이 과정을 거치는 걸 그냥 세컨더리 인덱스 조회라 하고
- Oracle 계열에서는 **테이블 풀 액세스 / random access**, 흔히 **북마크 룩업**이라 부른다

### 여기서 나오는 실전 결론 2개

**(1) PK는 짧아야 한다.**

세컨더리 인덱스 **전부**가 PK 값을 품고 있다. PK가 크면 모든 세컨더리 인덱스가 함께 커진다.

```sql
-- 나쁜 예: UUID를 CHAR(36) PK로
id CHAR(36) PRIMARY KEY          -- 36바이트가 모든 세컨더리 인덱스에 복사된다

-- 좋은 예
id BIGINT AUTO_INCREMENT PRIMARY KEY   -- 8바이트
```

**(2) PK는 단조 증가해야 좋다.**

데이터가 PK 순서로 물리 정렬되므로, 랜덤한 PK(UUID v4)로 INSERT하면
매번 페이지 중간에 끼워넣게 되어 **페이지 분할(page split)** 이 자주 일어난다.
단편화가 심해지고 INSERT 성능이 떨어진다.
`AUTO_INCREMENT`는 항상 맨 뒤에 붙으므로 분할이 거의 없다.

> UUID를 꼭 써야 하면 시간 순서가 보장되는 **UUID v7** 이나 ULID를 쓰고,
> 저장은 `BINARY(16)`으로 하는 게 정석이다. 이 답을 하면 확실히 눈에 띈다.

---

## 4. 복합 인덱스 (Composite Index)

### 규칙 1: 왼쪽부터 연속으로만 쓸 수 있다 (Leftmost Prefix)

```sql
CREATE INDEX idx_a_b_c ON t (a, b, c);
```

| 조건 | 인덱스 사용 |
|---|---|
| `WHERE a = 1` | O |
| `WHERE a = 1 AND b = 2` | O |
| `WHERE a = 1 AND b = 2 AND c = 3` | O |
| `WHERE b = 2` | **X** |
| `WHERE b = 2 AND c = 3` | **X** |
| `WHERE a = 1 AND c = 3` | △ (a까지만 인덱스로 좁히고 c는 필터링) |

전화번호부를 "성 → 이름" 순으로 정렬한 것과 같다. 성을 모르면 이름만으로는 찾을 수 없다.

### 규칙 2: 등호 조건을 앞에, 범위 조건을 뒤에

**범위 조건이 나온 컬럼 이후로는 인덱스로 탐색 범위를 좁힐 수 없다.**

```sql
-- 나쁜 순서
CREATE INDEX idx_bad ON orders (created_at, status);
SELECT * FROM orders WHERE created_at >= '2026-01-01' AND status = 'PAID';
-- created_at 범위 안의 모든 항목을 훑으면서 status를 하나하나 비교한다

-- 좋은 순서
CREATE INDEX idx_good ON orders (status, created_at);
-- status = 'PAID' 로 딱 좁힌 뒤 그 안에서 created_at 범위를 스캔한다
```

### 규칙 3: ORDER BY도 인덱스로 처리할 수 있다

```sql
CREATE INDEX idx_status_created ON orders (status, created_at);

SELECT * FROM orders
 WHERE status = 'PAID'
 ORDER BY created_at DESC
 LIMIT 20;
-- 인덱스가 이미 created_at 순으로 정렬돼 있으므로 정렬 작업이 사라진다
-- EXPLAIN Extra에서 "Using filesort"가 없어진다
```

`ORDER BY` 컬럼의 방향이 섞여 있으면(`a ASC, b DESC`) MySQL 8.0부터
**내림차순 인덱스**로 해결할 수 있다. `CREATE INDEX ... ON t (a ASC, b DESC)`.

### 규칙 4: 컬럼 순서 결정은 쿼리 패턴이 1순위

흔히 "카디널리티 높은 컬럼을 앞에"라고 하는데, 그건 **2순위**다.
1순위는 실제 쿼리의 `WHERE`에 어떤 컬럼이 항상 들어오는지다.
카디널리티가 높아도 그 컬럼이 쿼리에 안 들어오면 인덱스 자체를 못 탄다.

우선순위를 정리하면
1. 항상 등호로 들어오는 컬럼
2. 그중 카디널리티(중복도 낮음)가 높은 것
3. 범위 조건 컬럼
4. `ORDER BY` / `GROUP BY` 컬럼

### 중복 인덱스 정리

```sql
INDEX (a)
INDEX (a, b)   -- (a)는 이걸로 커버된다. INDEX(a)는 지워도 된다
```

`(a, b)`가 있으면 `(a)`는 불필요하다. 쓰기 비용만 늘린다.

---

## 5. 커버링 인덱스 (Covering Index)

**쿼리가 필요한 모든 컬럼이 인덱스 안에 있어서, 클러스터드 인덱스를 다시 안 가는 경우.**
3번에서 말한 2단계 조회의 2단계가 사라진다. 성능 차이가 크다.

```sql
CREATE INDEX idx_status_created_amount ON orders (status, created_at, amount);

-- 커버링: status, created_at, amount 모두 인덱스에 있다
SELECT amount FROM orders WHERE status = 'PAID' AND created_at >= '2026-01-01';
-- EXPLAIN Extra: "Using index"   ← 이 표시가 커버링의 증거

-- 커버링 아님: customer_name이 인덱스에 없어서 행을 읽어야 한다
SELECT customer_name FROM orders WHERE status = 'PAID';
```

세컨더리 인덱스 리프에는 PK가 항상 들어 있으므로 **PK 컬럼은 자동으로 커버된다.**

```sql
CREATE INDEX idx_status ON orders (status);
SELECT id FROM orders WHERE status = 'PAID';  -- id는 PK라 커버링이 성립한다
```

### 페이지네이션 최적화 (실전 카드)

```sql
-- 느림: OFFSET이 커질수록 앞의 100만 행을 읽고 버린다
SELECT * FROM orders ORDER BY id DESC LIMIT 20 OFFSET 1000000;

-- 개선 1) 커버링 인덱스로 PK만 먼저 뽑고 조인 (deferred join)
SELECT o.* FROM orders o
  JOIN (SELECT id FROM orders ORDER BY id DESC LIMIT 20 OFFSET 1000000) t
    ON o.id = t.id;

-- 개선 2) 커서 기반 (No Offset) — 근본적인 해결
SELECT * FROM orders WHERE id < :last_seen_id ORDER BY id DESC LIMIT 20;
```

**커서 기반 페이지네이션을 언급하면 실무 경험이 있는 것으로 읽힌다.**
OFFSET 문제는 거의 모든 서비스가 겪는 일이라 면접관이 공감하는 지점이다.

---

## 6. 인덱스를 타지 못하는 경우 (제일 자주 묻는다)

### (1) 인덱스 컬럼에 함수나 연산을 적용

```sql
-- X
WHERE DATE(created_at) = '2026-01-01'
WHERE YEAR(created_at) = 2026
WHERE price * 1.1 > 10000
WHERE SUBSTRING(phone, 1, 3) = '010'

-- O — 컬럼은 그대로 두고 반대쪽을 가공한다
WHERE created_at >= '2026-01-01' AND created_at < '2026-01-02'
WHERE price > 10000 / 1.1
WHERE phone LIKE '010%'
```

> MySQL 8.0.13+ 에서는 **함수 기반 인덱스**로 우회할 수 있다.
> `CREATE INDEX idx_d ON t ((DATE(created_at)))` — 괄호 두 겹이 문법 포인트다.

### (2) 앞쪽 와일드카드 LIKE

```sql
WHERE name LIKE '%kim'    -- X, 시작점을 알 수 없어 스캔해야 한다
WHERE name LIKE '%kim%'   -- X
WHERE name LIKE 'kim%'    -- O
```

`%kim` 형태를 꼭 써야 하면 Full-Text 인덱스나 별도 검색 엔진(Elasticsearch),
또는 문자열을 뒤집어 저장한 컬럼에 인덱스를 거는 방법을 쓴다.

### (3) 타입 불일치 (암묵적 형변환)

```sql
-- phone은 VARCHAR인데 숫자로 비교
WHERE phone = 01012345678   -- X. MySQL이 컬럼을 숫자로 캐스팅해버려 인덱스를 못 쓴다
WHERE phone = '01012345678' -- O
```

**Go에서 특히 잘 나는 실수다.** `int64` 변수를 VARCHAR 컬럼에 바인딩하면 조용히 느려진다.
조인할 때 양쪽 컬럼 타입이나 **콜레이션(collation)이 다른 경우**도 같은 이유로 인덱스를 못 탄다.
`utf8mb4_general_ci`와 `utf8mb4_unicode_ci`가 섞인 테이블 간 조인이 대표적이다.

### (4) 선택도가 낮은 조건

```sql
-- status가 'PAID'인 행이 전체의 90%라면 인덱스를 타는 게 오히려 느리다
WHERE status = 'PAID'
-- 옵티마이저가 판단해서 풀 스캔을 고른다. 이건 버그가 아니라 정상 동작이다
```

성별, 삭제 여부(`is_deleted`) 같은 컬럼에 단독 인덱스를 거는 건 대체로 낭비다.
단, 복합 인덱스의 일부로 들어가는 건 다르다.

### (5) OR 조건

```sql
WHERE a = 1 OR b = 2
-- a, b 각각 인덱스가 있으면 index merge로 처리될 수도 있지만 보장되지 않는다
-- UNION으로 쪼개는 게 확실할 때가 있다
SELECT ... WHERE a = 1
UNION
SELECT ... WHERE b = 2;
```

### (6) 부정 조건

`!=`, `<>`, `NOT IN`, `NOT LIKE`는 "제외할 것"을 지정하므로 범위를 좁히지 못하는 경우가 많다.

---

## 7. 쓰기 비용 — 트레이드오프

**INSERT / UPDATE / DELETE 시 해당 테이블의 모든 인덱스를 함께 갱신해야 한다.**

- 인덱스 5개면 INSERT 한 번에 트리 6개(클러스터드 1 + 세컨더리 5)를 수정한다
- 인덱스는 디스크 공간도 먹는다. 큰 테이블에서 인덱스 총량이 데이터보다 커지는 경우도 흔하다
- UPDATE는 변경된 컬럼이 포함된 인덱스만 갱신한다 (그래서 자주 바뀌는 컬럼을 인덱스에 넣을 때 신중해야 함)

그래서 인덱스 설계는 **읽기 이득 vs 쓰기 비용의 저울질**이다.
"조회가 느려서 인덱스를 추가했는데 쓰기가 느려져서 다시 검토했다"는 서사가 있으면 좋다.

### 인덱스 사용 현황 확인

```sql
-- 실제로 안 쓰이는 인덱스 찾기 (performance_schema 활성 필요)
SELECT * FROM sys.schema_unused_indexes;

-- 중복 인덱스 찾기
SELECT * FROM sys.schema_redundant_indexes;
```

이 두 뷰를 알고 있으면 "인덱스 정리를 어떻게 했나"에 구체적으로 답할 수 있다.

---

## 8. EXPLAIN 읽는 법

```sql
EXPLAIN SELECT * FROM orders WHERE status = 'PAID';
EXPLAIN FORMAT=JSON SELECT ...;     -- 비용 정보까지 상세히
EXPLAIN ANALYZE SELECT ...;         -- MySQL 8.0.18+. 실제로 실행하고 실측 시간을 보여준다
```

### `type` — 접근 방식. 위에서 아래로 좋다

| type | 의미 |
|---|---|
| `system`, `const` | 행 1개. PK/UNIQUE 등호 조회. 최고 |
| `eq_ref` | 조인에서 PK/UNIQUE로 1행씩 매칭 |
| `ref` | 비유니크 인덱스 등호 조회. 일반적으로 양호 |
| `range` | 인덱스 범위 스캔. `BETWEEN`, `>`, `IN` |
| `index` | **인덱스 풀 스캔.** 인덱스를 처음부터 끝까지 읽음 |
| `ALL` | **테이블 풀 스캔. 튜닝 대상 1순위** |

### 핵심 컬럼

- `key` — 실제로 사용된 인덱스. `NULL`이면 인덱스를 안 썼다
- `possible_keys` — 후보. 여기 있는데 `key`가 NULL이면 옵티마이저가 일부러 버린 것
- `rows` — 읽을 것으로 예상되는 행 수 (추정치)
- `filtered` — `rows` 중 조건을 통과할 것으로 예상되는 비율(%). `rows × filtered`가 실제 결과 규모
- `key_len` — 사용된 인덱스의 바이트 길이. **복합 인덱스에서 몇 번째 컬럼까지 썼는지 알 수 있다**

### `Extra` — 여기가 정보량이 가장 많다

| 값 | 의미 |
|---|---|
| `Using index` | **커버링 인덱스.** 좋다 |
| `Using where` | 인덱스로 못 걸러낸 조건을 서버에서 추가 필터링 |
| `Using index condition` | ICP(Index Condition Pushdown). 스토리지 엔진에서 미리 필터. 좋다 |
| `Using filesort` | **정렬을 별도로 수행.** 인덱스로 정렬을 해결하지 못했다는 뜻 |
| `Using temporary` | **임시 테이블 생성.** `GROUP BY`, `DISTINCT`에서 자주 나온다. 무겁다 |
| `Using join buffer` | 조인 대상에 인덱스가 없어서 버퍼로 처리. 인덱스 추가 검토 |

> `Using filesort`가 "파일에 정렬한다"는 뜻은 아니다. 데이터가 작으면 메모리에서 정렬한다.
> 이걸 알고 있으면 좋다.

### 튜닝 순서 (실무 답변용)

1. **느린 쿼리를 찾는다** — slow query log, `performance_schema.events_statements_summary_by_digest`
2. `EXPLAIN`으로 `type`과 `Extra`를 본다
3. `type=ALL`이거나 `Using filesort`/`Using temporary`가 보이면 인덱스 후보를 세운다
4. 인덱스를 추가하고 `EXPLAIN ANALYZE`로 **실측 전후를 비교한다**
5. 쓰기 성능과 디스크 사용량 영향을 확인한다
6. 인덱스로 해결이 안 되면 쿼리 자체를 다시 쓴다 (서브쿼리 → 조인, N+1 제거, 커서 페이지네이션)

```sql
-- 느린 쿼리 상위 10개
SELECT DIGEST_TEXT, COUNT_STAR, AVG_TIMER_WAIT/1000000000 AS avg_ms
  FROM performance_schema.events_statements_summary_by_digest
 ORDER BY AVG_TIMER_WAIT DESC
 LIMIT 10;
```

---

## 9. 락과의 연결 (가산점 구간)

**InnoDB의 락은 행이 아니라 인덱스 레코드에 걸린다.**

```sql
-- status에 인덱스가 없다면
UPDATE orders SET status = 'DONE' WHERE status = 'PENDING';
-- 풀 스캔하면서 스캔한 모든 행에 락 → 테이블 전체가 잠긴 것과 같아진다
```

그래서 인덱스는 **성능 도구이면서 동시에 동시성 도구**다.
"인덱스가 왜 중요한가"에 조회 속도 말고 이 답을 하나 더 얹을 수 있으면 차별화된다.
[transaction.md](./transaction.md) 4번과 이어진다.

---

## 10. 예상 꼬리질문 체크리스트

- [ ] 인덱스 자료구조는? 왜 해시가 아니라 B+Tree인가?
- [ ] B-Tree와 B+Tree의 차이는? (→ 데이터가 리프에만, 리프 연결 리스트)
- [ ] 클러스터드 인덱스와 세컨더리 인덱스의 차이는?
- [ ] 세컨더리 인덱스로 조회하면 왜 두 번 탐색하는가?
- [ ] PK를 UUID로 하면 어떤 문제가 있나? (→ 세컨더리 인덱스 비대, 페이지 분할)
- [ ] 복합 인덱스 `(a, b, c)`에서 `WHERE b = 1`은 인덱스를 타나?
- [ ] 복합 인덱스 컬럼 순서는 어떻게 정하나?
- [ ] 커버링 인덱스가 뭐고 어떻게 확인하나? (→ `Using index`)
- [ ] 인덱스를 걸었는데도 안 타는 경우는? (→ 6번 전체)
- [ ] 인덱스를 많이 걸면 안 되는 이유는?
- [ ] `EXPLAIN`에서 무엇을 먼저 보나? (→ `type`, `key`, `Extra`)
- [ ] `Using filesort`를 없애려면? (→ `ORDER BY`를 인덱스 순서에 맞춤)
- [ ] `OFFSET 1000000`이 느린 이유와 해결책은? (→ 커서 기반)
- [ ] 인덱스와 락은 무슨 관계인가?
- [ ] 카디널리티가 뭔가? 낮은 컬럼에 인덱스를 거는 게 왜 비효율인가?

## 11. 자주 하는 실수

- "인덱스는 조회를 빠르게 한다"에서 멈춘다 → **쓰기 비용, 안 타는 경우, 락 관계**까지가 한 세트
- 클러스터드/세컨더리 구분을 못 한다 → InnoDB 인덱스 이해의 기준선이다
- 복합 인덱스를 "컬럼 여러 개에 각각 인덱스 거는 것"으로 오해한다
- `EXPLAIN`을 읽을 줄 모른다 → **최소한 `type`과 `Extra`는 즉시 해석할 수 있어야 한다**
- 개선 경험을 "인덱스 걸어서 빨라졌다"로만 말한다 → **전후 수치**를 준비한다.
  "2.3초에서 40ms로 줄었습니다" 같은 숫자 하나가 답변의 무게를 바꾼다
