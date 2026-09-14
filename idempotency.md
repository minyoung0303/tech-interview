# 결제 멱등성 (Idempotency)

> 기준: MySQL 8.x, Redis, AWS SQS, Go/Echo, PG(토스페이먼츠/포트원 등)
>
> 이 주제는 앞의 네 개와 성격이 다르다. **암기 지식이 아니라 설계 사고를 보는 질문이다.**
> "돈이 두 번 빠지면 안 된다"는 문제를 어떻게 풀어내는지 보는 것이고,
> 신입/주니어가 여기서 제대로 답하면 **가장 크게 점수가 뛰는 주제**다.

---

## 0. 30초 답변 스크립트

> "멱등성은 같은 요청을 여러 번 실행해도 결과가 한 번 실행한 것과 같은 성질입니다.
> 결제에서 중요한 이유는, 네트워크 타임아웃이 나면 클라이언트는 성공인지 실패인지 알 수 없고
> 재시도하게 되는데 그때 이중 결제가 발생하기 때문입니다.
> 필요한 상황, Idempotency-Key 기반 구현, 동시성을 어디서 막는지,
> 그리고 외부 PG와 DB 상태가 어긋났을 때 맞추는 방법 순서로 말씀드리겠습니다."

---

## 1. 정의

**멱등성(idempotency): 같은 연산을 몇 번 수행하든 결과 상태가 한 번 수행한 것과 동일한 성질.**

수학에서 `f(f(x)) = f(x)`인 성질과 같다.

### HTTP 메서드별 멱등성

| 메서드 | 멱등 | 안전(safe) | 비고 |
|---|---|---|---|
| `GET` | O | O | 상태를 안 바꾼다 |
| `HEAD` | O | O | |
| `PUT` | O | X | 같은 값으로 덮어쓰므로 결과가 같다 |
| `DELETE` | O | X | 두 번 지워도 없는 상태는 같다 (응답 코드는 달라질 수 있다) |
| `POST` | **X** | X | 호출마다 새 리소스가 생긴다 |
| `PATCH` | **X** | X | `{"amount": "+100"}` 같은 증분 연산이면 멱등하지 않다 |

**결제는 보통 `POST`다. 그래서 멱등성을 프로토콜이 보장해주지 않고, 직접 만들어야 한다.**
그 표준적인 방법이 `Idempotency-Key` 헤더다.

> 헷갈리는 지점: `DELETE`가 멱등이라는 건 **결과 상태**가 같다는 뜻이다.
> 첫 호출은 204, 두 번째는 404를 줄 수 있는데 응답 코드가 달라도 멱등성은 유지된다.

---

## 2. 왜 필요한가 — 중복이 생기는 경로 5가지

**질문에 답할 때 이 목록을 구체적으로 나열하면 설득력이 확 올라간다.**

### (1) 네트워크 타임아웃 후 재시도 (가장 중요)

```
클라이언트 → [결제 요청] → 서버 → PG 승인 성공 → DB 저장
                ↑
        여기서 응답이 유실되면
        클라이언트는 성공인지 실패인지 알 수 없다 → 재시도 → 이중 결제
```

**핵심 통찰: 클라이언트는 "실패"와 "응답 유실"을 구분할 수 없다.**
그래서 재시도는 불가피하고, 서버가 멱등해야 한다.

### (2) 사용자의 중복 클릭

결제 버튼 연타. 프론트에서 버튼을 비활성화하는 건 UX 보완이고, **방어는 서버에서 해야 한다.**
프론트만 믿으면 안 되는 이유는 API를 직접 호출할 수 있기 때문이다.

### (3) PG 웹훅 중복 발송

PG는 웹훅에 대해 **at-least-once**를 보장한다. 우리 서버가 200을 늦게 주거나 실패로 판단하면
같은 이벤트를 여러 번 보낸다. 이건 PG의 버그가 아니라 정상 동작이다.

### (4) 메시지 큐의 at-least-once (공고 스택에 SQS가 있었다)

**SQS Standard 큐는 at-least-once만 보장한다. 중복 수신이 정상 동작이다.**

- 컨슈머가 메시지를 처리했지만 `DeleteMessage` 호출 전에 죽으면 → visibility timeout 후 재전달
- 처리 시간이 visibility timeout보다 길면 → 다른 컨슈머가 같은 메시지를 또 받는다

**따라서 SQS 컨슈머는 반드시 멱등해야 한다.** 이건 선택이 아니라 요구사항이다.
`SQS FIFO` 큐는 `MessageDeduplicationId`로 5분 이내 중복을 제거해주지만,
5분을 넘기면 다시 중복될 수 있고 처리량 제한이 있어서 **애플리케이션 멱등성을 대체하지 않는다.**

### (5) 로드밸런서/게이트웨이 레벨 재시도

프록시가 타임아웃으로 판단해 다른 인스턴스로 재시도하는 경우.
백엔드는 이미 처리 중일 수 있다.

---

## 3. 구현: Idempotency-Key 패턴

### 흐름

```
1. 클라이언트가 요청마다 고유한 키를 생성해 헤더에 담는다
   Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
   ※ 재시도할 때는 같은 키를 다시 쓴다. 이게 전제 조건이다.

2. 서버는 idempotency_keys 테이블에 (키, 요청 해시, IN_PROGRESS)로 INSERT를 시도한다

3-A. INSERT 성공 → 첫 요청이다
     → 실제 결제 처리 → 결과와 응답을 저장하고 SUCCEEDED/FAILED로 갱신 → 응답 반환

3-B. INSERT 실패 (duplicate key) → 이미 온 요청이다
     → 저장된 레코드를 조회한다
        · SUCCEEDED/FAILED → 저장된 응답을 그대로 반환 (재실행하지 않는다)
        · IN_PROGRESS      → 409 Conflict + Retry-After 로 잠시 후 재시도 안내
```

### 스키마

```sql
CREATE TABLE idempotency_keys (
  id            BIGINT      NOT NULL AUTO_INCREMENT,
  idem_key      VARCHAR(64) NOT NULL,
  -- 같은 키로 다른 내용을 보내는 걸 막기 위한 요청 본문 해시
  request_hash  CHAR(64)    NOT NULL,
  -- 키를 사용자별로 격리한다. 남의 키를 추측해 응답을 훔쳐보는 걸 막는다
  user_id       BIGINT      NOT NULL,
  status        ENUM('IN_PROGRESS','SUCCEEDED','FAILED') NOT NULL,
  response_code INT         NULL,
  response_body JSON        NULL,
  created_at    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  updated_at    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                             ON UPDATE CURRENT_TIMESTAMP(6),
  PRIMARY KEY (id),
  -- ★ 여기가 멱등성의 실제 방어선이다
  UNIQUE KEY uk_user_idem (user_id, idem_key),
  KEY idx_created_at (created_at)   -- 만료 레코드 정리용
) ENGINE=InnoDB;
```

### 왜 `request_hash`가 필요한가

같은 키로 **다른 내용**을 보내는 경우를 잡아야 한다.

```
1차: Idempotency-Key: abc, body: {"amount": 10000}   → 성공
2차: Idempotency-Key: abc, body: {"amount": 99000}   → 키가 같다는 이유로
                                                        10000원 결제 응답을 돌려주면 버그다
```

키는 같은데 해시가 다르면 **422 Unprocessable Entity**로 거부한다. Stripe도 이렇게 한다.

### 왜 상태(`status`)가 필요한가

`IN_PROGRESS` 상태가 없으면, 동시에 들어온 두 요청 중 두 번째가
"레코드는 있는데 응답이 없다"는 상황에 빠져 무엇을 반환해야 할지 알 수 없다.
진행 중임을 명시하고 409로 재시도를 안내하는 게 정확한 처리다.

---

## 4. 동시성을 어디서 막는가 — 가장 중요한 포인트

### 안티패턴: 조회 후 없으면 INSERT

```go
// ❌ 이 코드는 경쟁 상태에 뚫린다
row := db.QueryRow("SELECT id FROM idempotency_keys WHERE idem_key = ?", key)
if row.Scan(...) == sql.ErrNoRows {
   // ★ 두 요청이 동시에 여기 도달하면 둘 다 "없다"고 판단한다
   db.Exec("INSERT INTO idempotency_keys ...")
   처리()
}
```

**"확인 후 행동(check-then-act)"은 원자적이지 않다.** 이건 멱등성 구현에서 가장 흔한 오류다.

### 정답: DB 유니크 제약이 최종 방어선

**먼저 INSERT를 시도하고, duplicate key 에러를 정상 흐름으로 처리한다.**

```
INSERT를 시도한다
  → 성공하면 내가 첫 번째다 (DB가 원자적으로 보장해준다)
  → 1062 에러면 다른 요청이 이미 선점했다
```

유니크 제약은 DB 엔진이 원자적으로 판정하므로 경쟁 상태가 원천적으로 생기지 않는다.

### Redis는 최종 방어선이 될 수 없다

```go
// Redis SET NX로 1차 차단 — 이건 "최적화"일 뿐이다
ok, _ := rdb.SetNX(ctx, "idem:"+key, "1", 5*time.Minute).Result()
```

Redis를 쓰면 안 되는 게 아니라, **Redis만 쓰면 안 된다.**

- Redis는 기본적으로 비동기 복제다. 마스터가 죽으면 아직 복제되지 않은 키가 유실된다
- TTL이 만료되면 키가 사라진다
- 메모리 부족 시 eviction 정책에 따라 키가 쫓겨날 수 있다
- 장애 시 전체가 초기화될 수 있다

**돈이 걸린 판정에는 영속적이고 트랜잭션이 보장되는 DB 유니크 제약을 쓴다.**
Redis는 DB 부하를 줄이는 앞단 필터로 쓰는 게 올바른 역할 분담이다.

> Redis 분산 락(Redlock)도 마찬가지다. 네트워크 지연과 GC 정지 때문에
> 락 만료 후에도 이전 소유자가 작업을 계속하는 상황을 완전히 막을 수 없다.
> **락으로 정합성을 보장하려 하지 말고, 최종 상태를 DB 제약으로 보장한다.**

---

## 5. 트랜잭션 경계 설계 — 외부 API가 끼어들 때

[transaction.md](./transaction.md) 6번과 직접 이어지는 내용이다.

### 문제

```
❌ tx 시작 → 주문 저장 → PG 승인 API 호출(3초) → 결과 저장 → 커밋
```

- DB 커넥션과 락을 3초간 점유한다 → 트래픽이 몰리면 커넥션 풀 고갈
- **외부 호출은 롤백되지 않는다.** DB가 롤백돼도 결제는 이미 승인된 상태로 남는다

### 해결: 트랜잭션을 쪼개고 상태 머신으로 관리한다

```
tx1: 주문을 PENDING 상태로 저장하고 커밋       ← 의도를 먼저 기록한다
     ↓
     PG 승인 API 호출 (트랜잭션 밖)
     ↓
tx2: 결과에 따라 PAID / FAILED 로 갱신하고 커밋
     ↓
     ★ tx2 직전에 서버가 죽으면? → PENDING 상태로 남는다
       이건 "유실"이 아니라 "미확정"이다. 기록이 남아 있으니 나중에 맞출 수 있다
     ↓
     정합 배치(reconciliation): PENDING이 N분 이상 지속된 건을
     PG 조회 API로 실제 상태를 확인해 맞춘다
```

**핵심: 외부 호출 전에 의도를 먼저 커밋해둔다.**
그러면 어느 시점에 죽어도 추적 가능한 흔적이 남는다.
이 설계를 설명할 수 있으면 신입 수준을 넘는다.

### 상태 머신

```
CREATED → PENDING → PAID → (부분/전체) REFUNDED
             │        │
             ├→ FAILED
             └→ EXPIRED (타임아웃)
```

**전이 규칙을 코드로 강제한다.** 특히 `PAID → PENDING` 같은 역행을 막아야 한다.
웹훅이 순서가 뒤바뀌어 도착하는 일이 실제로 있기 때문이다.

```go
var allowed = map[Status][]Status{
   StatusCreated: {StatusPending, StatusFailed},
   StatusPending: {StatusPaid, StatusFailed, StatusExpired},
   StatusPaid:    {StatusRefunded},
   StatusFailed:  {},        // 종료 상태
   StatusRefunded:{},        // 종료 상태
}

func canTransit(from, to Status) bool {
   return slices.Contains(allowed[from], to)
}
```

### 상태 전이도 조건부 UPDATE로 원자화한다

```sql
-- WHERE에 현재 상태를 넣으면 동시 갱신을 DB가 걸러준다.
-- 영향받은 행이 0이면 이미 누군가 처리했다는 뜻이다.
UPDATE payments
   SET status = 'PAID', paid_at = NOW(6), pg_tid = ?
 WHERE id = ? AND status = 'PENDING';
```

`RowsAffected() == 0`이면 중복 처리로 판단하고 조용히 성공 응답을 준다.
**이 한 줄짜리 기법이 웹훅 멱등 처리의 대부분을 해결한다.**

---

## 6. Go 구현

### 미들웨어로 만드는 방법

```go
const mysqlErrDupEntry = 1062

func isDupEntry(err error) bool {
   var me *mysql.MySQLError
   return errors.As(err, &me) && me.Number == mysqlErrDupEntry
}

type idemRecord struct {
   Status       string
   RequestHash  string
   ResponseCode sql.NullInt64
   ResponseBody []byte
}

func IdempotencyMiddleware(db *sql.DB) echo.MiddlewareFunc {
   return func(next echo.HandlerFunc) echo.HandlerFunc {
      return func(c echo.Context) error {
         key := c.Request().Header.Get("Idempotency-Key")
         if key == "" {
            return echo.NewHTTPError(http.StatusBadRequest, "Idempotency-Key required")
         }
         ctx := c.Request().Context()
         userID := currentUserID(c)

         // 본문을 읽어 해시를 만들고, 핸들러가 다시 읽을 수 있도록 되돌려 놓는다
         body, err := io.ReadAll(c.Request().Body)
         if err != nil {
            return err
         }
         c.Request().Body = io.NopCloser(bytes.NewReader(body))
         sum := sha256.Sum256(body)
         reqHash := hex.EncodeToString(sum[:])

         // ── 1) 선점 시도. 유니크 제약이 동시성을 판정한다 ──
         _, err = db.ExecContext(ctx, `
            INSERT INTO idempotency_keys
                   (idem_key, user_id, request_hash, status)
            VALUES (?, ?, ?, 'IN_PROGRESS')`,
            key, userID, reqHash)

         if err != nil {
            if !isDupEntry(err) {
               return err
            }
            // ── 2) 중복. 기존 레코드를 보고 판단한다 ──
            var rec idemRecord
            if err := db.QueryRowContext(ctx, `
               SELECT status, request_hash, response_code, response_body
                 FROM idempotency_keys
                WHERE user_id = ? AND idem_key = ?`,
               userID, key,
            ).Scan(&rec.Status, &rec.RequestHash, &rec.ResponseCode, &rec.ResponseBody); err != nil {
               return err
            }

            // 같은 키에 다른 본문 → 거부
            if rec.RequestHash != reqHash {
               return echo.NewHTTPError(http.StatusUnprocessableEntity,
                  "Idempotency-Key reused with a different request body")
            }

            if rec.Status == "IN_PROGRESS" {
               c.Response().Header().Set("Retry-After", "1")
               return echo.NewHTTPError(http.StatusConflict, "request already in progress")
            }

            // 저장된 응답을 그대로 재생한다. 핸들러는 실행하지 않는다
            c.Response().Header().Set("Idempotent-Replay", "true")
            return c.JSONBlob(int(rec.ResponseCode.Int64), rec.ResponseBody)
         }

         // ── 3) 첫 요청. 응답을 가로채기 위해 ResponseWriter를 감싼다 ──
         rec := &bodyCapture{ResponseWriter: c.Response().Writer, buf: &bytes.Buffer{}}
         c.Response().Writer = rec

         handlerErr := next(c)

         status := "SUCCEEDED"
         code := c.Response().Status
         if handlerErr != nil || code >= 500 {
            // 5xx는 일시적 장애일 수 있으므로 키를 아예 지워 재시도를 허용한다.
            // 4xx는 같은 요청이면 같은 결과이므로 FAILED로 기록해 응답을 재생한다.
            if code >= 500 || handlerErr != nil {
               _, _ = db.ExecContext(ctx,
                  `DELETE FROM idempotency_keys WHERE user_id = ? AND idem_key = ?`,
                  userID, key)
               return handlerErr
            }
            status = "FAILED"
         }

         _, _ = db.ExecContext(ctx, `
            UPDATE idempotency_keys
               SET status = ?, response_code = ?, response_body = ?
             WHERE user_id = ? AND idem_key = ?`,
            status, code, rec.buf.Bytes(), userID, key)

         return handlerErr
      }
   }
}

// 응답 본문을 저장하면서 클라이언트로도 흘려보낸다
type bodyCapture struct {
   http.ResponseWriter
   buf *bytes.Buffer
}

func (w *bodyCapture) Write(b []byte) (int, error) {
   w.buf.Write(b)
   return w.ResponseWriter.Write(b)
}
```

### 5xx일 때 키를 지우는 이유 (설계 판단 포인트)

- **5xx / 타임아웃** = 일시적 장애일 가능성이 크다. 재시도해야 성공한다 → **키를 해제한다**
- **4xx** = 요청 자체가 잘못됐다. 재시도해도 같은 결과다 → **응답을 저장해 재생한다**

단, 5xx라도 **외부 PG 호출이 이미 나갔다면 키를 지우면 위험하다.**
그래서 실제로는 PG 호출 여부까지 상태로 기록하고, 애매한 건 정합 배치에 맡긴다.
**"애매하면 지우지 않고 미확정으로 남긴다"가 돈을 다루는 시스템의 원칙이다.**

---

## 7. PG 웹훅 처리

### 반드시 해야 하는 4가지

**(1) 서명 검증**

웹훅 엔드포인트는 인증 없이 외부에 열려 있다. 누구나 "결제 성공" 요청을 위조할 수 있다.
PG가 제공하는 서명 헤더를 **원본 바이트로** 검증한다.

```go
func verifySignature(rawBody []byte, signature, secret string) bool {
   mac := hmac.New(sha256.New, []byte(secret))
   mac.Write(rawBody)
   expected := hex.EncodeToString(mac.Sum(nil))
   // 타이밍 공격 방지를 위해 상수 시간 비교를 쓴다
   return hmac.Equal([]byte(expected), []byte(signature))
}
```

JSON을 파싱한 뒤 다시 직렬화해서 검증하면 키 순서나 공백 때문에 실패한다. **raw body를 써야 한다.**

**(2) 중복 처리** — 이벤트 ID에 유니크 제약을 걸고, 이미 있으면 200을 주고 끝낸다

```sql
CREATE TABLE webhook_events (
  event_id   VARCHAR(128) NOT NULL,
  received_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (event_id)
) ENGINE=InnoDB;
```

**(3) 순서 역전 대비** — 웹훅은 순서를 보장하지 않는다.
`PAID` 다음에 `PENDING`이 도착할 수 있다. 5번의 상태 머신으로 역행을 막는다.

**(4) 빨리 200을 반환한다** — 웹훅 핸들러에서 무거운 작업을 하면 PG가 타임아웃으로 보고
재발송을 반복한다. **검증하고 큐에 넣고 즉시 200을 준 뒤 비동기로 처리한다.**
여기서 SQS가 쓰이고, 컨슈머는 다시 멱등해야 한다.

### 금액 검증을 잊지 않는다

웹훅이나 결제 승인 응답의 금액이 **우리 DB에 저장된 주문 금액과 일치하는지 반드시 확인한다.**
클라이언트가 금액을 조작해 보내는 공격(가격 위조)을 막는 지점이다.

```go
if webhook.Amount != order.Amount {
   // 즉시 결제 취소 + 알림
   return errAmountMismatch
}
```

**결제 구현에서 가장 흔한 실무 취약점이다.** 이걸 언급하면 보안 감각을 보여줄 수 있다.

---

## 8. 정합 배치 (Reconciliation)

**미확정 상태를 그대로 두지 않고 주기적으로 맞춘다.**

```
매 N분:
  1. status = 'PENDING' 이고 created_at 이 10분 이상 지난 건을 조회
  2. 각 건에 대해 PG 조회 API로 실제 상태를 확인
  3-A. PG에 승인 기록이 있다 → PAID 로 갱신 (우리가 놓친 것)
  3-B. PG에 기록이 없다     → EXPIRED / FAILED 로 갱신
  3-C. PG는 승인인데 우리 쪽에 상품이 안 나갔다 → 알림 발생 + 수동 확인 대상
  4. 일 단위로 PG 거래 내역 전체와 우리 DB를 대조해 차이를 리포트
```

**"장애를 완전히 없앨 수는 없으니, 어긋난 걸 발견하고 맞추는 장치를 둔다"** 는 관점이
결제 시스템 설계의 핵심이다. 이 문장 자체가 좋은 답변이 된다.

### 만료된 멱등 키 정리

```sql
-- 보관 기간은 PG의 재시도 윈도우보다 길게 잡는다. 보통 24시간~7일
DELETE FROM idempotency_keys
 WHERE created_at < NOW() - INTERVAL 7 DAY
 LIMIT 1000;   -- 한 번에 다 지우면 락이 길어진다. 나눠서 반복 실행
```

`LIMIT`으로 쪼개는 이유는 대량 DELETE가 락과 복제 지연을 유발하기 때문이다.
이 디테일도 실무 감각으로 읽힌다.

---

## 9. 관련 개념 정리

### 멱등성 vs 중복 제거 vs Exactly-Once

| 개념 | 의미 |
|---|---|
| **At-least-once** | 최소 한 번은 전달. 중복 가능. SQS Standard, 대부분의 웹훅 |
| **At-most-once** | 최대 한 번. 유실 가능 |
| **Exactly-once** | 정확히 한 번. **분산 시스템에서 순수하게 달성 불가능에 가깝다** |
| **멱등성** | 중복이 와도 결과가 같게 만든다 → **실질적으로 exactly-once 효과를 낸다** |

**정리: "정확히 한 번 전달"을 만들려 하지 말고, "여러 번 와도 괜찮게" 만든다.**
이게 분산 시스템의 정석적인 접근이고, 면접에서 이 문장을 말하면 사고 수준이 드러난다.

### Outbox 패턴 (SQS 발행과 DB 커밋의 정합)

```
❌ tx 커밋 → SQS 발행    : 커밋 후 발행 직전에 죽으면 메시지 유실
❌ SQS 발행 → tx 커밋    : 롤백되면 없는 일에 대한 메시지가 나간다

✅ Outbox
   tx: 주문 저장 + outbox 테이블에 메시지 저장 (같은 트랜잭션)
   별도 워커: outbox를 폴링해 SQS로 발행하고 발행 완료 표시
   → 발행이 at-least-once가 되므로 컨슈머는 멱등해야 한다
```

DB 변경과 메시지 발행을 **하나의 트랜잭션으로 묶는** 방법이다.
이름만 알아도 "메시지 유실은 어떻게 막나요?"에 답할 수 있다.

---

## 10. 예상 꼬리질문 체크리스트

- [ ] 멱등성이 뭔가? 결제에서 왜 필요한가?
- [ ] HTTP 메서드 중 멱등한 것은? `POST`는 왜 아닌가?
- [ ] `DELETE`가 멱등인데 두 번째 호출이 404면 멱등성이 깨진 건가? (→ 아니다, 결과 상태 기준)
- [ ] 이중 결제가 발생하는 경로를 말해보라
- [ ] Idempotency-Key는 누가 생성하나? (→ 클라이언트. 재시도 시 같은 키를 재사용)
- [ ] 같은 키로 다른 본문이 오면? (→ `request_hash` 비교 후 422)
- [ ] 동일한 키로 두 요청이 **동시에** 들어오면? (→ DB 유니크 제약이 판정, 두 번째는 409)
- [ ] "조회해서 없으면 INSERT"는 왜 안 되나? (→ check-then-act, 경쟁 상태)
- [ ] Redis로만 멱등 처리를 하면 왜 위험한가?
- [ ] 트랜잭션 안에서 PG API를 호출하면 왜 안 되나?
- [ ] PG 호출 직후 서버가 죽으면 어떻게 복구하나? (→ PENDING 선기록 + 정합 배치)
- [ ] SQS는 왜 중복이 오나? 컨슈머는 어떻게 대응하나?
- [ ] SQS FIFO의 중복 제거로 충분한가? (→ 5분 윈도우 한계, 애플리케이션 멱등성 필요)
- [ ] 웹훅 보안은 어떻게 하나? (→ HMAC 서명, raw body, 상수 시간 비교)
- [ ] 웹훅이 순서가 뒤바뀌어 오면? (→ 상태 머신으로 역행 차단)
- [ ] 결제 금액 검증은 어디서 하나? (→ 서버 DB의 주문 금액과 대조)
- [ ] Exactly-once 전달이 가능한가? (→ 사실상 불가능. 멱등성으로 해결)
- [ ] 멱등 키는 얼마나 보관하나? 정리는 어떻게 하나?

## 11. 자주 하는 실수

- 멱등성을 "중복 요청을 막는 것"으로만 설명한다 →
  **막는 게 아니라 여러 번 와도 결과가 같게 만드는 것**이다. 차단이 아니라 흡수다
- 프론트에서 버튼을 비활성화하는 걸 해결책으로 제시한다 → UX 보완이지 방어가 아니다
- 애플리케이션 코드로 중복을 체크한다 → 경쟁 상태에 뚫린다. **DB 유니크 제약이 방어선**
- Redis 락으로 해결한다고 답한다 → 락은 최적화, 최종 보장은 영속 저장소의 제약
- `IN_PROGRESS` 상태를 두지 않는다 → 동시 요청 처리가 정의되지 않는다
- 실패 케이스만 생각하고 **"성공했는데 응답이 유실된 경우"** 를 놓친다 →
  이게 사실 이중 결제의 주된 원인이다
- 정합 배치를 언급하지 않는다 → 돈을 다루는 시스템은 항상 대조 장치가 있다
