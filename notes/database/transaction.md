---
topic: database
title: 트랜잭션
level: core
status: done
confidence: 3
last_reviewed: 2026-09-14
tags: [ACID, 격리수준, MVCC, 락, 데드락]
asked_at: [아름다운가게]
---

# 트랜잭션 (Transaction)

> 기준: MySQL 8.x / InnoDB, Go `database/sql`
> 실제 면접 질문: "트랜잭션을 얼마나 이해하고 있는지 있는대로 다 설명해봐라"

---

## 0. 30초 답변 스크립트

이런 개방형 질문은 **먼저 지도를 그리고 그 다음 깊이로 들어가는** 순서가 안전하다.
답변 시작을 이렇게 잡는다.

> "트랜잭션은 여러 작업을 하나의 논리적 단위로 묶어서 전부 성공하거나 전부 취소되게 만드는 개념입니다.
> 크게 네 가지로 나눠서 말씀드리겠습니다. 성질인 ACID, 동시성 제어인 격리 수준,
> InnoDB가 그걸 구현하는 방식인 MVCC와 락, 마지막으로 실무에서 주의했던 점입니다."

이렇게 목차를 먼저 던지면 면접관이 원하는 지점을 골라서 되물어준다. 아는 영역으로 대화를 끌 수 있다.

---

## 1. ACID

| 성질 | 의미 | InnoDB 구현 |
|---|---|---|
| **A**tomicity (원자성) | 전부 반영되거나 전부 취소 | **undo log** — 변경 전 값을 기록해두고 롤백 시 되돌린다 |
| **C**onsistency (일관성) | 트랜잭션 전후로 제약조건이 깨지지 않음 | PK/FK/UNIQUE/CHECK 제약, 트리거 |
| **I**solation (격리성) | 동시 실행 트랜잭션이 서로 간섭하지 않음 | **MVCC + 락** |
| **D**urability (지속성) | 커밋된 내용은 장애가 나도 남는다 | **redo log (WAL)** + `innodb_flush_log_at_trx_commit` |

### 꼬리질문: "커밋하면 디스크에 바로 쓰이나요?"

데이터 파일에 바로 쓰이지 않는다. 변경은 메모리(버퍼 풀)의 더티 페이지에 남고,
커밋 시점에 보장되는 건 **redo log가 디스크에 flush되는 것**이다.
장애가 나면 재시작 시 redo log를 재생(replay)해서 복구한다. 이게 WAL(Write-Ahead Logging).

`innodb_flush_log_at_trx_commit` 값에 따라 강도가 달라진다.

- `1` (기본) — 커밋마다 flush + fsync. 가장 안전, 가장 느림
- `2` — 커밋마다 OS 버퍼까지만. MySQL 프로세스가 죽어도 살지만 OS가 죽으면 유실
- `0` — 1초마다. 가장 빠르고 가장 위험

---

## 2. 격리 수준과 이상 현상

### 이상 현상 3종

| 현상 | 설명 |
|---|---|
| **Dirty Read** | 아직 커밋되지 않은 다른 트랜잭션의 변경을 읽는다 |
| **Non-Repeatable Read** | 같은 행을 두 번 읽었는데 값이 다르다 (사이에 다른 트랜잭션이 UPDATE 후 커밋) |
| **Phantom Read** | 같은 조건으로 두 번 조회했는데 없던 행이 나타난다 (사이에 INSERT 후 커밋) |

### 격리 수준 4단계

| 수준 | Dirty | Non-Repeatable | Phantom | 비고 |
|---|---|---|---|---|
| READ UNCOMMITTED | O | O | O | 실무에서 거의 안 씀 |
| READ COMMITTED | X | O | O | **PostgreSQL / Oracle 기본** |
| REPEATABLE READ | X | X | △ | **MySQL InnoDB 기본** |
| SERIALIZABLE | X | X | X | 사실상 직렬 실행 |

### 여기서 점수가 갈리는 포인트 2개

**(1) MySQL의 REPEATABLE READ는 팬텀 리드를 상당 부분 막는다.**

표준 스펙상 REPEATABLE READ는 팬텀을 허용하지만, InnoDB는 두 가지 장치로 막는다.

- 일반 SELECT(consistent read)는 MVCC 스냅샷을 읽으므로 새 행이 안 보인다
- 락을 잡는 읽기(`SELECT ... FOR UPDATE`)는 **갭 락 / 넥스트키 락**으로 범위 자체를 잠가 INSERT를 차단한다

그래서 위 표에서 △로 적었다. "MySQL 기본이 REPEATABLE READ인데 팬텀이 나나요?"라고 물으면
이 두 장치를 설명하면 된다.

**(2) SERIALIZABLE에서 InnoDB가 하는 일**

`autocommit`이 꺼진 상태에서 SERIALIZABLE이면, 평범한 `SELECT`도 자동으로
`SELECT ... FOR SHARE`로 바뀌어 공유 락을 잡는다. 그래서 읽기만 해도 쓰기를 막아 동시성이 급락한다.

### 설정 확인 / 변경

```sql
SELECT @@transaction_isolation;            -- 현재 세션
SELECT @@global.transaction_isolation;     -- 전역

SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

---

## 3. MVCC (Multi-Version Concurrency Control)

**핵심 한 문장: 읽기가 쓰기를 막지 않고, 쓰기가 읽기를 막지 않게 만드는 기법.**
같은 행의 여러 버전을 유지해서 각 트랜잭션이 자기 시점의 버전을 읽는다.

### InnoDB 구현

모든 행에는 숨은 컬럼이 붙어 있다.

- `DB_TRX_ID` — 이 행을 마지막으로 변경한 트랜잭션 ID
- `DB_ROLL_PTR` — undo log의 이전 버전을 가리키는 포인터
- `DB_ROW_ID` — PK가 없을 때 쓰이는 내부 행 ID

행을 UPDATE하면 이전 버전이 undo log로 밀려나고, `DB_ROLL_PTR`로 연결된 **버전 체인**이 만들어진다.
읽을 때는 **ReadView**(내가 볼 수 있는 트랜잭션 ID 집합)를 기준으로 체인을 거슬러 올라가
자기가 볼 수 있는 가장 최신 버전을 찾는다.

### 격리 수준별 차이가 여기서 나온다

| 격리 수준 | ReadView 생성 시점 |
|---|---|
| **READ COMMITTED** | **SELECT 문마다 새로 만든다** → 매번 최신 커밋 상태를 보게 되어 Non-Repeatable Read 발생 |
| **REPEATABLE READ** | **트랜잭션의 첫 읽기 때 한 번 만들고 끝까지 재사용** → 항상 같은 스냅샷, 반복 읽기 일관성 확보 |

이 한 줄 차이가 두 격리 수준의 동작 차이를 전부 설명한다. **이걸 말하면 깊이가 인정된다.**

### 꼬리질문: "MVCC의 단점은?"

- **undo log가 계속 쌓인다.** 오래 열려 있는 트랜잭션이 있으면 그 트랜잭션이 볼 수 있어야 하는
  옛 버전들을 지울 수 없어서 undo 영역이 계속 커진다 (History list length 증가).
  → 배치나 리포트용 긴 트랜잭션이 운영 DB를 망가뜨리는 대표적 경로다.
- 버전 체인이 길어지면 읽기 시 체인을 더 많이 타서 조회가 느려진다.
- purge 스레드가 정리하지만, 긴 트랜잭션이 이걸 막는다.

### 함정: Lost Update는 MVCC가 막아주지 않는다

```sql
-- 두 트랜잭션이 동시에 이걸 하면 하나가 덮어써진다
SELECT stock FROM products WHERE id = 1;   -- 둘 다 10을 읽음
-- 애플리케이션에서 10 - 1 = 9 계산
UPDATE products SET stock = 9 WHERE id = 1; -- 둘 다 9로 씀. 2개 팔았는데 1개만 줄었다
```

해결책 3가지 (면접에서 자주 파고든다)

```sql
-- (1) 원자적 UPDATE — 가장 간단하고 가장 빠르다
UPDATE products SET stock = stock - 1 WHERE id = 1 AND stock >= 1;
-- 영향받은 행 수가 0이면 재고 부족으로 처리

-- (2) 비관적 락 — 읽고 나서 판단할 로직이 복잡할 때
SELECT stock FROM products WHERE id = 1 FOR UPDATE;

-- (3) 낙관적 락 — 버전 컬럼으로 충돌 감지, 충돌 시 재시도
UPDATE products SET stock = 9, version = version + 1
 WHERE id = 1 AND version = 3;
```

---

## 4. 락 (Lock)

### 행 수준 락

| 락 | 표기 | 의미 |
|---|---|---|
| 공유 락 | S | 읽기 락. 여러 트랜잭션이 동시에 가질 수 있다 |
| 배타 락 | X | 쓰기 락. 하나만 가질 수 있고 S와도 충돌한다 |

```sql
SELECT ... FOR UPDATE;   -- X 락
SELECT ... FOR SHARE;    -- S 락 (구버전 문법: LOCK IN SHARE MODE)

SELECT ... FOR UPDATE NOWAIT;         -- 못 잡으면 즉시 에러
SELECT ... FOR UPDATE SKIP LOCKED;    -- 잠긴 행은 건너뜀 (큐/작업 배분에 유용)
```

`SKIP LOCKED`는 DB를 작업 큐로 쓸 때 워커들이 서로 다른 행을 집어가게 만드는 데 쓴다.
알아두면 쓸 데가 많다.

### 락의 범위

| 종류 | 잠그는 대상 |
|---|---|
| **레코드 락** | 인덱스 레코드 하나 |
| **갭 락** | 인덱스 레코드 사이의 빈 구간. 그 구간에 INSERT를 막는다 |
| **넥스트키 락** | 레코드 락 + 그 앞 갭 락. REPEATABLE READ의 기본 동작 |
| **인텐션 락 (IS/IX)** | 테이블 수준. "이 테이블 안에서 행 락을 잡을 예정" 표시. DDL과 충돌 감지용 |

### 반드시 알아야 할 사실: InnoDB 락은 인덱스에 걸린다

**행에 거는 게 아니라 인덱스 레코드에 건다.** 그래서

```sql
-- status에 인덱스가 없으면
UPDATE orders SET status = 'DONE' WHERE status = 'PENDING';
-- 풀 스캔하면서 스캔한 모든 행에 락을 건다 → 사실상 테이블 전체 잠김
```

**인덱스 설계가 곧 락 범위 설계다.** 인덱스 노트와 이어지는 지점이고,
"인덱스 왜 중요한가"에 성능 말고 하나 더 답할 수 있는 카드다.

---

## 5. 데드락 (Deadlock)

### 정의

두 트랜잭션이 서로가 가진 락을 기다려서 영원히 진행되지 않는 상태.

```
T1: A 락 획득 → B 락 대기
T2: B 락 획득 → A 락 대기
```

### InnoDB의 처리

`innodb_deadlock_detect`가 켜져 있으면(기본값 ON) **자동으로 감지해서 한쪽을 롤백시킨다.**
롤백 대상은 보통 변경량이 적은 쪽(undo log가 작은 쪽)이다.
클라이언트는 에러 코드 **1213 (ER_LOCK_DEADLOCK)** 를 받는다.

락 대기 타임아웃은 별개다. `innodb_lock_wait_timeout`(기본 50초) 초과 시 에러 **1205**.

```sql
SHOW ENGINE INNODB STATUS;  -- LATEST DETECTED DEADLOCK 섹션에서 원인 분석
```

### 예방책

1. **락 획득 순서를 통일한다.** 가장 효과적. 항상 작은 ID부터 잡는 식으로 규칙을 정한다
2. **트랜잭션을 짧게 유지한다.** 락 보유 시간이 곧 충돌 확률
3. **인덱스를 제대로 걸어 락 범위를 좁힌다** (위 4번)
4. **데드락은 완전히 없앨 수 없다고 가정하고 재시도 로직을 넣는다.** 1213은 재시도하면 대체로 성공한다

---

## 6. 실무에서 주의한 점 (여기가 차별점이다)

### (1) 트랜잭션 안에서 외부 API를 호출하지 않는다

```
[안티패턴]
tx 시작 → DB 저장 → PG 결제 승인 API 호출 (3초) → DB 저장 → 커밋
```

문제가 세 가지다.

- **DB 커넥션을 외부 응답 시간만큼 점유한다.** 트래픽이 몰리면 커넥션 풀이 마르고 전체 장애로 번진다
- **락을 그 시간만큼 붙잡고 있다** → 데드락과 락 대기 타임아웃 급증
- **외부 호출은 롤백이 안 된다.** DB는 롤백됐는데 결제는 승인된 상태가 남는다

해결은 트랜잭션 경계를 쪼개는 것이다.

```
tx1: pending 레코드 저장 후 커밋
     → PG API 호출 (트랜잭션 밖)
tx2: 결과로 상태 업데이트 후 커밋
     → 미확정 건은 배치로 PG에 조회해서 정합 맞춤 (reconciliation)
```

이 패턴은 [idempotency.md](../backend/idempotency.md)에서 이어진다.

### (2) 트랜잭션 범위를 최소화한다

읽기만 하는 조회, 파일 업로드, 이미지 리사이즈, 로깅 같은 건 트랜잭션 밖으로 빼낸다.
"핸들러 전체를 트랜잭션으로 감싸는" 구조는 나중에 반드시 문제가 된다.

### (3) 커넥션 풀 크기와 트랜잭션 길이는 같은 문제다

긴 트랜잭션 하나가 커넥션을 계속 점유하면, 풀 크기를 늘려도 DB 쪽 부하만 커진다.
`SetMaxOpenConns`를 올리기 전에 트랜잭션 길이를 먼저 본다.

---

## 7. Go 구현 예시

### 기본 패턴

```go
func withTx(ctx context.Context, db *sql.DB, fn func(*sql.Tx) error) error {
   tx, err := db.BeginTx(ctx, nil)
   if err != nil {
      return fmt.Errorf("begin tx: %w", err)
   }
   // 커밋에 성공했다면 Rollback은 sql.ErrTxDone을 반환하고 아무 일도 하지 않는다.
   // 그래서 defer로 걸어두는 게 안전하다 (panic이나 early return에서도 정리됨).
   defer func() { _ = tx.Rollback() }()

   if err := fn(tx); err != nil {
      return err
   }
   return tx.Commit()
}
```

### 계좌 이체 — 데드락 예방까지 반영

```go
var ErrInsufficientBalance = errors.New("insufficient balance")

func Transfer(ctx context.Context, db *sql.DB, fromID, toID, amount int64) error {
   return withTx(ctx, db, func(tx *sql.Tx) error {
      // 데드락 예방: 항상 작은 id부터 락을 잡도록 순서를 고정한다.
      // ORDER BY id 를 붙여도 실제 락 획득 순서는 옵티마이저에 달려 있으므로
      // 두 행을 한 문장으로 잡는 편이 더 확실하다.
      rows, err := tx.QueryContext(ctx, `
         SELECT id, balance
           FROM accounts
          WHERE id IN (?, ?)
          ORDER BY id
            FOR UPDATE`, fromID, toID)
      if err != nil {
         return fmt.Errorf("lock accounts: %w", err)
      }

      balances := make(map[int64]int64, 2)
      for rows.Next() {
         var id, bal int64
         if err := rows.Scan(&id, &bal); err != nil {
            rows.Close()
            return err
         }
         balances[id] = bal
      }
      if err := rows.Err(); err != nil {
         rows.Close()
         return err
      }
      // database/sql은 트랜잭션 하나에 커넥션 하나를 쓴다.
      // rows를 닫기 전에 같은 tx로 다른 쿼리를 던지면 에러가 난다. 반드시 먼저 닫는다.
      rows.Close()

      if len(balances) != 2 {
         return errors.New("account not found")
      }
      if balances[fromID] < amount {
         return ErrInsufficientBalance // defer의 Rollback이 정리한다
      }

      if _, err := tx.ExecContext(ctx,
         `UPDATE accounts SET balance = balance - ? WHERE id = ?`,
         amount, fromID); err != nil {
         return fmt.Errorf("debit: %w", err)
      }
      if _, err := tx.ExecContext(ctx,
         `UPDATE accounts SET balance = balance + ? WHERE id = ?`,
         amount, toID); err != nil {
         return fmt.Errorf("credit: %w", err)
      }
      return nil
   })
}
```

### 데드락 재시도

```go
const mysqlErrDeadlock = 1213

func isDeadlock(err error) bool {
   var me *mysql.MySQLError
   return errors.As(err, &me) && me.Number == mysqlErrDeadlock
}

func TransferWithRetry(ctx context.Context, db *sql.DB, from, to, amount int64) error {
   const maxAttempts = 3
   var err error
   for attempt := 1; attempt <= maxAttempts; attempt++ {
      err = Transfer(ctx, db, from, to, amount)
      if err == nil || !isDeadlock(err) {
         return err // 성공했거나, 재시도해도 소용없는 에러
      }
      // 지수 백오프 + 지터로 같은 타이밍에 다시 부딪히는 걸 피한다
      backoff := time.Duration(1<<attempt)*10*time.Millisecond +
         time.Duration(rand.Intn(20))*time.Millisecond
      select {
      case <-ctx.Done():
         return ctx.Err()
      case <-time.After(backoff):
      }
   }
   return fmt.Errorf("deadlock retry exhausted: %w", err)
}
```

### 격리 수준 지정

```go
tx, err := db.BeginTx(ctx, &sql.TxOptions{
   Isolation: sql.LevelReadCommitted,
   ReadOnly:  false,
})
```

읽기 전용 트랜잭션은 `ReadOnly: true`를 주면 InnoDB가 트랜잭션 ID 할당을 생략해서 약간 더 빠르다.

---

## 8. 예상 꼬리질문 체크리스트

- [ ] MySQL의 기본 격리 수준은? 왜 그게 기본인가?
- [ ] READ COMMITTED와 REPEATABLE READ의 구현상 차이는? (→ ReadView 생성 시점)
- [ ] REPEATABLE READ인데 팬텀 리드가 발생할 수 있나? (→ 갭 락, consistent read)
- [ ] MVCC가 뭐고 단점은? (→ undo log 증가, 긴 트랜잭션 문제)
- [ ] Lost Update는 격리 수준으로 막히나? (→ 아니다, 원자적 UPDATE나 락 필요)
- [ ] 비관적 락과 낙관적 락의 선택 기준은? (→ 충돌 빈도. 잦으면 비관적, 드물면 낙관적)
- [ ] 데드락이 나면 어떻게 되나? 어떻게 예방하나?
- [ ] 커밋하면 디스크에 바로 쓰이나? (→ redo log / WAL)
- [ ] 트랜잭션 안에서 외부 API를 호출하면 안 되는 이유는?
- [ ] 락은 행에 걸리나 인덱스에 걸리나? (→ 인덱스. 락 범위 = 인덱스 설계)
- [ ] `SELECT FOR UPDATE`와 그냥 `SELECT`의 차이는?
- [ ] 분산 환경에서 여러 DB에 걸친 트랜잭션은? (→ 2PC의 한계, Saga 패턴, 최종적 일관성)

## 9. 자주 하는 실수

- ACID 네 글자만 나열하고 끝낸다 → 각각을 InnoDB가 **어떻게** 구현하는지까지 가야 한다
- 격리 수준 이름만 외우고 어떤 이상 현상을 막는지 연결하지 못한다
- MySQL 기본값을 READ COMMITTED로 답한다 (그건 PostgreSQL/Oracle)
- "트랜잭션 걸면 동시성 문제가 해결된다"고 답한다 → Lost Update 반례가 있다
- 겪은 사례가 없다 → 데드락이든 락 대기든 커넥션 풀 고갈이든 **본인 경험 하나는 반드시 준비**
