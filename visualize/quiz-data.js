/* 자동 생성 파일입니다. 직접 고치지 마세요.
   노트를 고친 뒤:  python tools/build_quiz.py  */
window.QUIZ_DATA = {
 "generated": "2026-09-20",
 "blob": "https://github.com/minyoung0303/tech-interview/blob/main/",
 "notes": [
  {
   "path": "notes/backend/idempotency.md",
   "topic": "backend",
   "title": "결제 멱등성",
   "level": "plus",
   "status": "done",
   "confidence": 2,
   "count": 18
  },
  {
   "path": "notes/database/db-index.md",
   "topic": "database",
   "title": "인덱스",
   "level": "core",
   "status": "done",
   "confidence": 3,
   "count": 15
  },
  {
   "path": "notes/database/transaction.md",
   "topic": "database",
   "title": "트랜잭션",
   "level": "core",
   "status": "done",
   "confidence": 3,
   "count": 12
  },
  {
   "path": "notes/infra/deployment.md",
   "topic": "infra",
   "title": "배포",
   "level": "core",
   "status": "done",
   "confidence": 2,
   "count": 15
  },
  {
   "path": "notes/infra/infra.md",
   "topic": "infra",
   "title": "인프라 9문항",
   "level": "core",
   "status": "done",
   "confidence": 2,
   "count": 88
  },
  {
   "path": "notes/infra/proxy.md",
   "topic": "infra",
   "title": "프록시",
   "level": "core",
   "status": "done",
   "confidence": 3,
   "count": 14
  },
  {
   "path": "notes/network/http.md",
   "topic": "network",
   "title": "HTTP",
   "level": "core",
   "status": "todo",
   "confidence": 1,
   "count": 0
  }
 ],
 "items": [
  {
   "q": "멱등성이 뭔가? 결제에서 왜 필요한가?",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "HTTP 메서드 중 멱등한 것은? POST는 왜 아닌가?",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "DELETE가 멱등인데 두 번째 호출이 404면 멱등성이 깨진 건가?",
   "hint": "아니다, 결과 상태 기준",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "이중 결제가 발생하는 경로를 말해보라",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "Idempotency-Key는 누가 생성하나?",
   "hint": "클라이언트. 재시도 시 같은 키를 재사용",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "같은 키로 다른 본문이 오면?",
   "hint": "request_hash 비교 후 422",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "동일한 키로 두 요청이 동시에 들어오면?",
   "hint": "DB 유니크 제약이 판정, 두 번째는 409",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "\"조회해서 없으면 INSERT\"는 왜 안 되나?",
   "hint": "check-then-act, 경쟁 상태",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "Redis로만 멱등 처리를 하면 왜 위험한가?",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "트랜잭션 안에서 PG API를 호출하면 왜 안 되나?",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "PG 호출 직후 서버가 죽으면 어떻게 복구하나?",
   "hint": "PENDING 선기록 + 정합 배치",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "SQS는 왜 중복이 오나? 컨슈머는 어떻게 대응하나?",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "SQS FIFO의 중복 제거로 충분한가?",
   "hint": "5분 윈도우 한계, 애플리케이션 멱등성 필요",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "웹훅 보안은 어떻게 하나?",
   "hint": "HMAC 서명, raw body, 상수 시간 비교",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "웹훅이 순서가 뒤바뀌어 오면?",
   "hint": "상태 머신으로 역행 차단",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "결제 금액 검증은 어디서 하나?",
   "hint": "서버 DB의 주문 금액과 대조",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "Exactly-once 전달이 가능한가?",
   "hint": "사실상 불가능. 멱등성으로 해결",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "멱등 키는 얼마나 보관하나? 정리는 어떻게 하나?",
   "hint": "",
   "topic": "backend",
   "title": "결제 멱등성",
   "confidence": 2,
   "src": "notes/backend/idempotency.md"
  },
  {
   "q": "인덱스 자료구조는? 왜 해시가 아니라 B+Tree인가?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "B-Tree와 B+Tree의 차이는?",
   "hint": "데이터가 리프에만, 리프 연결 리스트",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "클러스터드 인덱스와 세컨더리 인덱스의 차이는?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "세컨더리 인덱스로 조회하면 왜 두 번 탐색하는가?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "PK를 UUID로 하면 어떤 문제가 있나?",
   "hint": "세컨더리 인덱스 비대, 페이지 분할",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "복합 인덱스 (a, b, c)에서 WHERE b = 1은 인덱스를 타나?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "복합 인덱스 컬럼 순서는 어떻게 정하나?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "커버링 인덱스가 뭐고 어떻게 확인하나?",
   "hint": "Using index",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "인덱스를 걸었는데도 안 타는 경우는?",
   "hint": "6번 전체",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "인덱스를 많이 걸면 안 되는 이유는?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "EXPLAIN에서 무엇을 먼저 보나?",
   "hint": "type, key, Extra",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "Using filesort를 없애려면?",
   "hint": "ORDER BY를 인덱스 순서에 맞춤",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "OFFSET 1000000이 느린 이유와 해결책은?",
   "hint": "커서 기반",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "인덱스와 락은 무슨 관계인가?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "카디널리티가 뭔가? 낮은 컬럼에 인덱스를 거는 게 왜 비효율인가?",
   "hint": "",
   "topic": "database",
   "title": "인덱스",
   "confidence": 3,
   "src": "notes/database/db-index.md"
  },
  {
   "q": "MySQL의 기본 격리 수준은? 왜 그게 기본인가?",
   "hint": "",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "READ COMMITTED와 REPEATABLE READ의 구현상 차이는?",
   "hint": "ReadView 생성 시점",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "REPEATABLE READ인데 팬텀 리드가 발생할 수 있나?",
   "hint": "갭 락, consistent read",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "MVCC가 뭐고 단점은?",
   "hint": "undo log 증가, 긴 트랜잭션 문제",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "Lost Update는 격리 수준으로 막히나?",
   "hint": "아니다, 원자적 UPDATE나 락 필요",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "비관적 락과 낙관적 락의 선택 기준은?",
   "hint": "충돌 빈도. 잦으면 비관적, 드물면 낙관적",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "데드락이 나면 어떻게 되나? 어떻게 예방하나?",
   "hint": "",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "커밋하면 디스크에 바로 쓰이나?",
   "hint": "redo log / WAL",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "트랜잭션 안에서 외부 API를 호출하면 안 되는 이유는?",
   "hint": "",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "락은 행에 걸리나 인덱스에 걸리나?",
   "hint": "인덱스. 락 범위 = 인덱스 설계",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "SELECT FOR UPDATE와 그냥 SELECT의 차이는?",
   "hint": "",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "분산 환경에서 여러 DB에 걸친 트랜잭션은?",
   "hint": "2PC의 한계, Saga 패턴, 최종적 일관성",
   "topic": "database",
   "title": "트랜잭션",
   "confidence": 3,
   "src": "notes/database/transaction.md"
  },
  {
   "q": "배포 과정을 처음부터 끝까지 설명해보라",
   "hint": "소스/빌드/이미지/배포/검증",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "무중단 배포는 어떻게 하나? 전략별 차이는?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "롤백은 어떻게 하나? 이미지 태그를 latest로 하면 왜 문제인가?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "readinessProbe와 livenessProbe의 차이는? DB 체크는 어디에 넣나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "Graceful shutdown이 왜 필요한가? Go에서 어떻게 구현하나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "무중단 배포인데 502가 난다면 원인은?",
   "hint": "엔드포인트 전파 지연, preStop",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "멀티 스테이지 빌드를 쓰는 이유는?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "Docker 레이어 캐시를 잘 쓰려면 Dockerfile을 어떻게 쓰나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "컨테이너를 root로 실행하면 왜 안 되나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "시크릿은 어떻게 관리하나? K8s Secret은 암호화된 건가?",
   "hint": "아니다, base64",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "DB 마이그레이션은 배포 전인가 후인가? 롤백은 어떻게 하나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "롤링 배포 중 두 버전이 동시에 도는데 스키마 변경은 어떻게 하나?",
   "hint": "확장-수축",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "배포 후 무엇을 확인하나?",
   "hint": "골든 시그널 4개",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "CrashLoopBackOff가 나면 어떻게 디버깅하나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "스테이징 환경은 어떻게 구성했나?",
   "hint": "",
   "topic": "infra",
   "title": "배포",
   "confidence": 2,
   "src": "notes/infra/deployment.md"
  },
  {
   "q": "L4는 왜 경로 기반 라우팅을 못 하나?",
   "hint": "HTTP를 파싱하지 않는다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "L7에서 클라이언트 IP는 어떻게 알아내나?",
   "hint": "XFF, 그리고 위조 가능하다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "TLS 종료를 L4에서 할 수 있나?",
   "hint": "안 한다. 그래서 인증서 관리를 뒤로 미룬다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "ALB와 NLB 중 고정 IP가 필요하면?",
   "hint": "NLB",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "로드 밸런싱 알고리즘은 뭐가 있나?",
   "hint": "라운드 로빈, 최소 연결, IP 해시, 가중치",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "헬스 체크는 L4와 L7에서 어떻게 다른가?",
   "hint": "TCP 연결 / HTTP 200",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "sticky session은 어떻게 구현되나?",
   "hint": "L7은 쿠키, L4는 소스 IP 해시",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "로드 밸런서가 단일 장애점이 되지 않나?",
   "hint": "관리형 LB는 내부적으로 다중화, 멀티 AZ",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "왜 무조건 Scale-out이 정답이 아닌가?",
   "hint": "분산 복잡도, 비용, 먼저 할 게 있다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Scale-out을 하려면 애플리케이션이 어떤 조건을 만족해야 하나?",
   "hint": "stateless",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "세션을 서버 메모리에 두면 무슨 문제가 생기나? (→ sticky session 필요, 재시작 시 로그아웃) → Q9",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "파일 업로드는 어디에 저장하나?",
   "hint": "S3. 로컬 디스크는 안 된다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "서버를 늘렸는데 배치가 여러 번 도는 문제는 어떻게 해결하나?",
   "hint": "CronJob 분리, 분산 락, 멱등성",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "DB도 Scale-out 할 수 있나? (→ 읽기는 Replica, 쓰기는 샤딩. 난이도가 다르다) → Q7",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "파드를 늘렸는데 오히려 느려졌다면?",
   "hint": "DB 커넥션 포화, 락 경합, 외부 API rate limit",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Auto Scaling 기준 지표는 뭘로 잡나?",
   "hint": "CPU만으로는 부족. 요청 수, p99 지연, 큐 길이",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Web 서버와 WAS의 차이를 한 줄로?",
   "hint": "정적/프록시 vs 동적/로직",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Nginx 없이 앱만 띄우면 안 되나?",
   "hint": "된다. 다만 위 6가지를 다른 것이 대신해야 한다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Apache와 Nginx의 차이는?",
   "hint": "프로세스/스레드 기반 vs 이벤트 기반 비동기. C10K 문제",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "WAS를 여러 대 두면 세션은 어떻게 하나? (→ Redis 또는 JWT) → Q9",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "3-tier 아키텍처가 뭔가? (→ Web / App / DB 계층 분리. Subnet 설계와 대응된다) → Q5",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "정적 파일은 어디에 두는 게 좋나?",
   "hint": "S3 + CloudFront",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Nginx의 client_max_body_size 기본값은?",
   "hint": "1MB. 업로드 붙이고 413 나는 전형적 원인",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "컨테이너와 VM의 가장 큰 차이는?",
   "hint": "커널 공유 여부",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "컨테이너 격리는 무엇으로 구현되나?",
   "hint": "namespace + cgroup + UnionFS",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "컨테이너가 VM보다 격리가 약하다는 게 무슨 뜻인가?",
   "hint": "커널 취약점이 호스트 전체에 영향",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "이미지와 컨테이너의 차이는?",
   "hint": "불변 레이어 vs 쓰기 레이어를 얹은 실행 인스턴스",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "컨테이너 안의 데이터는 어떻게 되나?",
   "hint": "사라진다. 볼륨/외부 스토리지",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "왜 latest 태그를 쓰면 안 되나?",
   "hint": "롤백 불가, 재현 불가",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "멀티 스테이지 빌드는 왜 쓰나?",
   "hint": "크기, 보안",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Dockerfile 레이어 순서는 왜 중요한가?",
   "hint": "캐시 재사용",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "컨테이너에 SSH를 넣어도 되나?",
   "hint": "안 된다. kubectl exec를 쓴다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "ENTRYPOINT와 CMD의 차이는? exec 형식과 shell 형식의 차이는?",
   "hint": "시그널 전달",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Docker와 Kubernetes의 관계는?",
   "hint": "컨테이너 런타임 vs 오케스트레이터",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "컨테이너가 VM 위에서 도는 건가?",
   "hint": "클라우드에서는 대개 그렇다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Public Subnet과 Private Subnet의 차이는 무엇으로 결정되나?",
   "hint": "라우팅 테이블의 IGW 경로",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Private Subnet에서 인터넷으로 나갈 수 있나?",
   "hint": "NAT Gateway 경유하면 가능. 인바운드는 불가",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "NAT Gateway는 왜 Public Subnet에 두나?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Public Subnet인데 접속이 안 되는 이유는?",
   "hint": "Public IP 없음 / SG 차단",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "SG와 NACL의 차이는?",
   "hint": "stateful/stateless, allow만/deny 가능, ENI/서브넷",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "DB를 Private에 뒀는데 로컬에서 접속하려면?",
   "hint": "Bastion, SSM 포트 포워딩, VPN",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "서브넷은 AZ를 걸칠 수 있나?",
   "hint": "못 한다. 그래서 AZ마다 서브넷을 만든다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "IGW와 NAT Gateway의 차이는?",
   "hint": "양방향 / 아웃바운드 단방향",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "S3에 접근하는데 NAT 비용을 줄이려면?",
   "hint": "S3 Gateway Endpoint",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "3-tier 아키텍처와 서브넷 설계는 어떻게 대응되나?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "네 가지 방식과 각각의 트레이드오프는?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Rolling Update만 하면 무중단인가?",
   "hint": "아니다. readiness + graceful shutdown이 필요",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "maxSurge와 maxUnavailable은 뭔가? 무중단을 위한 값은?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Blue/Green의 단점은?",
   "hint": "리소스 2배, DB는 여전히 하나",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Blue/Green과 Canary 중 뭘 고르나?",
   "hint": "롤백 즉시성 vs 점진적 위험 감소",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Canary의 트래픽 분할은 어떻게 구현하나?",
   "hint": "LB 가중치, 서비스 메시, 파드 수",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Canary와 A/B 테스트의 차이는?",
   "hint": "안전장치 vs 제품 실험",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "롤링 중 두 버전이 같은 DB를 쓰는데 스키마 변경은?",
   "hint": "확장-수축",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "무중단 배포인데 502가 나는 이유는?",
   "hint": "엔드포인트 전파 지연, preStop 부재",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "롤백은 어떻게 하나?",
   "hint": "이전 이미지 태그 재배포, kubectl rollout undo, Blue/Green 스위치 복귀",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "배포 후 무엇을 확인하나?",
   "hint": "골든 시그널 4개: 지연, 트래픽, 에러, 포화도",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Read Replica와 샤딩의 차이를 한 줄로?",
   "hint": "같은 데이터 복사(읽기) vs 데이터 분할(쓰기)",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Read Replica로 쓰기 부하가 줄어드나?",
   "hint": "아니다. 쓰기는 Primary 한 대",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "복제 지연이 왜 생기나? 어떻게 대응하나?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Read-after-write 문제를 겪으면 어떻게 해결하나?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "모든 SELECT를 Replica로 보내도 되나?",
   "hint": "트랜잭션 내부, 방금 쓴 데이터는 Primary",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Primary가 죽으면 어떻게 되나?",
   "hint": "페일오버. Multi-AZ, 승격 후 DNS 전환. 그 사이 쓰기 불가",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "샤드 키는 어떻게 정하나? 잘못 정하면?",
   "hint": "핫스팟, 크로스 샤드 쿼리 폭증",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "샤딩 후 조인은 어떻게 하나?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "샤드를 추가할 때 무슨 일이 생기나?",
   "hint": "리샤딩. 그래서 일관된 해싱/논리 샤드",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "파티셔닝과 샤딩의 차이는?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "샤딩 전에 해볼 수 있는 건?",
   "hint": "위 순서 1~7",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "샤딩 환경에서 PK는 어떻게 만드나?",
   "hint": "Snowflake, UUID v7, ULID",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "숨겨지는 쪽이 각각 누구인가?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "NAT Gateway는 Forward Proxy인가?",
   "hint": "엄밀히 아니다. NAT는 L3, Forward Proxy는 L7",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "CDN은 어느 쪽인가?",
   "hint": "Reverse Proxy. 오리진을 대신한다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Reverse Proxy와 로드 밸런서는 같은 것인가?",
   "hint": "로드 밸런싱은 여러 기능 중 하나",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "X-Forwarded-For는 신뢰할 수 있나?",
   "hint": "위조 가능. 오른쪽에서 신뢰 프록시 수만큼 세어 들어간다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "프록시 뒤에서 리다이렉트가 http로 나가는 이유는?",
   "hint": "TLS 종료. X-Forwarded-Proto 확인",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "타임아웃이 두 겹이라는 게 무슨 뜻인가?",
   "hint": "짧은 쪽이 먼저 끊는다. 504",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "헬스 체크가 401이면?",
   "hint": "모든 파드가 unhealthy. 인증 미들웨어에서 제외",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "세션 방식이 Scale-out에서 왜 문제가 되나?",
   "hint": "서버 메모리에 둘 때",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Sticky Session의 단점은?",
   "hint": "불균등 분산, 서버 죽으면 로그아웃, 배포 시 세션 소실",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Redis 세션의 단점은?",
   "hint": "네트워크 홉, Redis 가용성이 서비스 가용성이 된다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "JWT는 왜 stateless인가?",
   "hint": "서명 검증만으로 완결. 저장소 조회 없음",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "JWT를 강제 로그아웃하려면?",
   "hint": "블랙리스트. 그러면 stateless가 깨진다",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "JWT의 payload는 암호화되어 있나?",
   "hint": "아니다. Base64 인코딩. 민감정보 금지",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Access/Refresh를 나누는 이유는?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Refresh Token은 어디에 저장하나? Rotation은 왜 하나?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "JWT를 localStorage에 저장하면?",
   "hint": "XSS 위험. HttpOnly 쿠키 권장",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "alg: none 공격이 뭔가?",
   "hint": "",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "권한이 변경되면 JWT에는 언제 반영되나?",
   "hint": "재발급 시점. 그래서 만료를 짧게",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Redis가 죽으면 세션 방식은?",
   "hint": "전원 로그아웃. 그래서 Redis도 HA 구성",
   "topic": "infra",
   "title": "인프라 9문항",
   "confidence": 2,
   "src": "notes/infra/infra.md"
  },
  {
   "q": "Forward Proxy와 Reverse Proxy의 차이를 한 문장으로?",
   "hint": "누구를 대신하고 숨기는가",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "Reverse Proxy를 쓰는 이유 3가지 이상?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "L4와 L7 로드밸런서의 차이는? 경로 기반 라우팅은 어느 쪽에서 되나?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "ALB와 NLB를 어떻게 선택하나?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "TLS 종료가 뭔가? 프록시 뒤 구간은 암호화하나?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "Reverse Proxy 뒤에서 클라이언트 IP를 어떻게 얻나?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "X-Forwarded-For를 그대로 믿으면 안 되는 이유는?",
   "hint": "위조 가능",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "로드밸런싱 알고리즘은 어떤 게 있나? sticky session은 언제 필요한가?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "sticky session을 안 쓰려면?",
   "hint": "세션을 Redis로 외부화, stateless 서버",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "API Gateway와 Reverse Proxy의 차이는? (→ 게이트웨이는 인증/rate limit/API 키 관리 등",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "CDN은 Forward인가 Reverse인가?",
   "hint": "Reverse. 오리진 서버를 대신한다",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "Kubernetes Ingress와 Service의 차이는?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "헬스 체크는 왜 필요한가? 무중단 배포와 어떤 관계인가?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  },
  {
   "q": "프록시 타임아웃과 애플리케이션 타임아웃 중 어느 쪽이 길어야 하나?",
   "hint": "",
   "topic": "infra",
   "title": "프록시",
   "confidence": 3,
   "src": "notes/infra/proxy.md"
  }
 ]
};
