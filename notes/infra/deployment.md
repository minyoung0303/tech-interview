---
topic: infra
title: 배포
level: core
status: done
confidence: 2
last_reviewed: 2026-09-14
tags: [Docker, Kubernetes, 롤링업데이트, preStop, 마이그레이션]
asked_at: [아름다운가게]
---

# 배포 (Deployment / CI·CD)

> 기준: Docker, Jenkins, GitLab CI, Kubernetes(EKS), AWS ECR, Go/Echo
> 실제 면접 질문: "배포 해봤다던데 배포 과정을 설명해봐라"
>
> **이 질문의 성격을 정확히 알아야 한다.** 이건 새로운 요구가 아니라
> **이력서 검증 질문**이다. 내가 썼다고 한 걸 진짜 했는지 확인하는 것이다.
> 따라서 정답은 "교과서적 파이프라인"이 아니라 **내가 실제로 한 것을 순서대로 말하는 것**이다.

---

## 0. 30초 답변

> "크게 **소스 → 빌드 → 이미지 → 배포 → 검증** 다섯 단계로 말씀드리겠습니다.
> main에 머지되면 Webhook으로 CI가 트리거되고, **린트와 테스트를 통과해야 다음 단계로 넘어갑니다.**
> 그다음 Docker 멀티 스테이지 빌드로 이미지를 만들어 **커밋 SHA를 태그로** 레지스트리에 올립니다. `latest`는 쓰지 않습니다. 롤백할 대상이 사라지기 때문입니다.
> 배포는 스테이징에 먼저 올려 스모크 테스트를 하고, 프로덕션은 롤링 업데이트로 교체합니다.
> 다만 **롤링 업데이트만으로는 무중단이 아닙니다.** readinessProbe와 graceful shutdown, preStop이 있어야 하고, 스키마 변경은 하위 호환이어야 합니다.
> 마지막으로 배포는 '완료'가 아니라 **'이상 없음 확인'이 끝**입니다. 지연·트래픽·에러·포화도 네 지표를 봅니다."

**"롤링 업데이트만으로는 무중단이 아니다"와 "배포는 이상 없음 확인이 끝"** 두 문장이
이 답변의 무게를 만든다. 나머지는 누구나 외운다.

---

## 0-1. 답변 전략

### 절대 원칙: 아는 것만 말하고, 모르는 건 모른다고 한다

배포 질문은 꼬리질문으로 파고들기가 아주 쉽다.
"ArgoCD로 GitOps 했습니다"라고 하면 바로 sync wave와 drift 감지를 물어본다.
**내가 실제로 손댄 범위를 정직하게 그리고, 그 안에서 깊이를 보여주는 게 훨씬 유리하다.**

```
"제가 직접 구성한 건 GitHub Actions 기반 파이프라인이고,
 쿠버네티스 환경은 사용해본 경험은 없어서 개념 수준으로만 알고 있습니다."
```

이렇게 선을 그으면 면접관은 그 선 안에서 질문한다. 통제 가능한 상황이 된다.

### 답변 골격 (5단계로 외운다)

> **소스 → 빌드 → 이미지 → 배포 → 검증**

이 다섯 단어만 잡고 있으면 어떤 환경이든 순서대로 풀어낼 수 있다.

---

## 1. 전체 파이프라인

```
1) 소스
   개발자 push → PR 생성 → 리뷰 → main 머지
   → Webhook으로 CI 트리거 (Jenkins / GitLab CI / GitHub Actions)

2) 빌드 & 검증
   의존성 캐시 복원 → 린트(golangci-lint) → 테스트(go test ./...)
   → 커버리지 확인 → 바이너리 빌드(go build)
   ※ 여기서 실패하면 즉시 중단. 배포 단계로 넘기지 않는다

3) 이미지
   Docker 이미지 빌드 (멀티 스테이지)
   → 태그 부여: 커밋 SHA + 시맨틱 버전
   → 취약점 스캔 (Trivy 등)
   → 레지스트리 push (ECR / GitLab Registry / Docker Hub)

4) 배포
   staging에 먼저 배포 → 스모크 테스트
   → production 배포 (롤링 / 블루그린 / 카나리)
   → 프록시 헬스 체크 통과 후 트래픽 유입

5) 검증
   헬스 체크 / 스모크 테스트
   → 모니터링 확인 (Sentry 에러율, Grafana 지표, CloudWatch 로그)
   → 이상 시 롤백
```

---

## 2. 이미지 태깅 — `latest`를 쓰면 안 되는 이유

**작지만 면접에서 확실히 먹히는 포인트다.**

```bash
# 나쁜 예
docker build -t myapp:latest .

# 좋은 예
docker build -t myapp:$(git rev-parse --short HEAD) -t myapp:v1.4.2 .
```

`latest`가 문제인 이유

1. **어떤 버전이 돌고 있는지 알 수 없다.** 장애 시 원인 커밋을 특정할 수 없다
2. **롤백할 대상이 없다.** 이전 `latest`는 덮어써져 사라졌다
3. **`imagePullPolicy`와 엉킨다.** 태그가 같으면 노드가 캐시된 이미지를 그대로 쓸 수 있어
   배포했는데 코드가 안 바뀌는 현상이 생긴다
4. 같은 태그가 다른 내용을 가리키므로 재현이 불가능하다

**커밋 SHA를 태그로 쓰면 이미지 ↔ 소스 코드가 1:1로 대응된다.** 이게 핵심 이유다.

---

## 3. Dockerfile — 멀티 스테이지 빌드 (Go)

```dockerfile
# ---------- build stage ----------
FROM golang:1.23-alpine AS builder

WORKDIR /app

# 의존성 파일만 먼저 복사한다.
# 소스가 바뀌어도 go.mod/go.sum이 그대로면 이 레이어 캐시가 재사용된다.
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# CGO_ENABLED=0 → 정적 링크. scratch/alpine에서 동작하게 만든다
# -ldflags "-s -w" → 디버그 심볼 제거로 바이너리 크기 축소
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /app/server ./cmd/server

# ---------- runtime stage ----------
FROM alpine:3.20

# HTTPS 호출을 위한 CA 인증서, 로그 타임스탬프를 위한 타임존
RUN apk add --no-cache ca-certificates tzdata && \
    adduser -D -u 10001 appuser

WORKDIR /app
COPY --from=builder /app/server .

# root로 실행하지 않는다 (컨테이너 보안 기본)
USER appuser

EXPOSE 8080
ENTRYPOINT ["/app/server"]
```

### 멀티 스테이지를 쓰는 이유

- **이미지 크기**: `golang` 베이스는 800MB 이상, alpine 런타임은 20MB 이하.
  이미지가 작으면 push/pull이 빠르고 곧 배포 속도가 된다
- **보안**: 최종 이미지에 컴파일러, 소스 코드, 빌드 도구가 남지 않는다. 공격 표면이 줄어든다

### 레이어 캐시 순서가 중요한 이유

Docker는 레이어 단위로 캐시한다. **자주 바뀌는 것을 뒤에 둬야 한다.**
`COPY . .`를 맨 앞에 두면 소스 한 글자만 바뀌어도 `go mod download`부터 다시 한다.
이 순서 하나로 CI 시간이 몇 분씩 차이난다.

---

## 4. 무중단 배포 전략

| 전략 | 방식 | 장점 | 단점 |
|---|---|---|---|
| **Recreate** | 다 내리고 새로 올린다 | 단순, 리소스 절약 | **다운타임 발생** |
| **Rolling Update** | 일부씩 순차 교체 | 추가 리소스 적음, K8s 기본 | 두 버전이 동시에 존재 |
| **Blue/Green** | 새 환경 전체를 띄우고 한 번에 스위치 | **롤백이 즉시** (다시 스위치) | 리소스 2배 |
| **Canary** | 소수 트래픽만 신 버전 → 지표 확인 → 점진 확대 | 위험 최소화, 실사용자 검증 | 구성 복잡, 관측 도구 필요 |

### 롤링 업데이트 설정

```yaml
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # 목표 개수보다 최대 1개 더 띄울 수 있다 (최대 5개)
      maxUnavailable: 0   # 사용 불가 파드를 0개로 → 용량이 절대 줄지 않는다
```

`maxUnavailable: 0`이 **무중단의 핵심**이다. 새 파드가 Ready가 된 뒤에야 구 파드를 내린다.
반대로 `maxSurge: 0, maxUnavailable: 1`이면 리소스는 안 늘지만 처리 용량이 일시적으로 줄어든다.

### 두 버전이 동시에 존재한다는 것의 의미 (중요)

롤링/카나리 중에는 **구 버전과 신 버전이 같은 DB를 동시에 바라본다.**
그래서 DB 스키마 변경이 반드시 **하위 호환**이어야 한다. 7번에서 이어진다.

---

## 5. Kubernetes 배포 — 실전 필수 개념

### Probe 3종 (이거 모르면 무중단 배포를 설명할 수 없다)

```yaml
containers:
  - name: app
    image: 123456789.dkr.ecr.ap-northeast-2.amazonaws.com/myapp:a3f9c21

    # 부팅이 느린 앱을 위한 유예 시간. 이게 성공할 때까지 다른 probe는 시작되지 않는다
    startupProbe:
      httpGet: { path: /healthz, port: 8080 }
      failureThreshold: 30
      periodSeconds: 2        # 최대 60초까지 기다려준다

    # "트래픽 받을 준비가 됐나" → 실패하면 Service 엔드포인트에서 제거된다 (재시작 안 함)
    readinessProbe:
      httpGet: { path: /readyz, port: 8080 }
      periodSeconds: 5
      failureThreshold: 3

    # "죽었나" → 실패하면 컨테이너를 재시작한다
    livenessProbe:
      httpGet: { path: /healthz, port: 8080 }
      periodSeconds: 10
      failureThreshold: 3
```

| Probe | 실패 시 동작 | 확인할 것 |
|---|---|---|
| `startupProbe` | 계속 대기 (임계 초과 시 재시작) | 초기화 완료 여부 |
| `readinessProbe` | **트래픽만 차단** | DB 커넥션, 캐시 워밍 등 의존성 준비 |
| `livenessProbe` | **컨테이너 재시작** | 프로세스 자체가 응답하는지 |

### readiness와 liveness를 구분해야 하는 이유

**liveness에 DB 연결 체크를 넣으면 안 된다.**
DB가 잠깐 흔들리면 모든 파드의 liveness가 실패하고, 전부 동시에 재시작되면서
연쇄 장애로 번진다. DB 의존성은 **readiness**에 넣어 트래픽만 빠지게 해야 한다.

- `livenessProbe` → 프로세스가 살아있는지만. 가볍게. `return 200` 수준
- `readinessProbe` → 의존성 확인. DB ping, Redis ping

**이 구분을 설명하면 확실히 깊이가 인정된다.**

### Graceful Shutdown과 preStop (실무 함정)

파드가 종료될 때 순서가 이렇다.

```
1. 파드가 Terminating 상태로 전환
2. (동시에) Service 엔드포인트에서 제거 요청 + 컨테이너에 SIGTERM 전송
3. terminationGracePeriodSeconds(기본 30초) 대기
4. 아직 살아있으면 SIGKILL
```

**문제는 2번이 동시에 일어난다는 것이다.**
엔드포인트 제거가 kube-proxy와 ALB까지 전파되는 데 수 초가 걸린다.
그 사이에 앱이 SIGTERM을 받고 바로 종료하면, **아직 라우팅되고 있는 요청이 502로 실패한다.**

해결은 `preStop`으로 인위적인 지연을 넣는 것이다.

```yaml
    lifecycle:
      preStop:
        exec:
          command: ["sleep", "10"]   # 엔드포인트 전파를 기다린다. 그 사이엔 정상 처리
terminationGracePeriodSeconds: 45    # preStop(10) + 앱 종료 시간보다 넉넉하게
```

**이 문제를 알고 있으면 실무 경험자로 읽힌다.** 무중단 배포를 했다는데 502가 났던 경험이
있으면 원인이 대체로 이것이다.

### Go/Echo Graceful Shutdown 구현

```go
func main() {
   e := echo.New()
   // ... 라우트 등록 ...

   // 서버를 별도 고루틴에서 실행한다 (아래 시그널 대기를 블로킹하지 않도록)
   go func() {
      if err := e.Start(":8080"); err != nil && !errors.Is(err, http.ErrServerClosed) {
         e.Logger.Fatalf("server start failed: %v", err)
      }
   }()

   // SIGTERM(쿠버네티스), SIGINT(로컬 Ctrl+C)를 받는다
   quit := make(chan os.Signal, 1)
   signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
   <-quit
   e.Logger.Info("shutdown signal received")

   // 새 요청은 거부하고, 진행 중인 요청은 최대 30초까지 마무리를 기다린다
   ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
   defer cancel()

   if err := e.Shutdown(ctx); err != nil {
      e.Logger.Errorf("graceful shutdown failed: %v", err)
   }

   // 리소스 정리 순서: 서버를 먼저 닫고 나서 DB를 닫는다.
   // 순서를 바꾸면 처리 중인 요청이 DB 접근에서 실패한다.
   if err := db.Close(); err != nil {
      e.Logger.Errorf("db close failed: %v", err)
   }
   e.Logger.Info("shutdown complete")
}
```

**주의: `SIGTERM`을 못 받는 경우가 있다.**
Dockerfile에서 `ENTRYPOINT`를 shell 형식(`ENTRYPOINT /app/server`)으로 쓰면
쉘이 PID 1이 되어 시그널이 앱에 전달되지 않는다.
**반드시 exec 형식(`ENTRYPOINT ["/app/server"]`)을 쓴다.** 이것도 좋은 답변 소재다.

### 롤백

```bash
kubectl rollout status deployment/myapp        # 진행 상황 확인
kubectl rollout history deployment/myapp       # 리비전 목록
kubectl rollout undo deployment/myapp          # 직전 리비전으로
kubectl rollout undo deployment/myapp --to-revision=3
```

이미지 태그가 커밋 SHA면 해당 SHA로 다시 배포하는 것도 확실한 롤백이다.

### 리소스 설정

```yaml
    resources:
      requests: { cpu: 100m, memory: 128Mi }   # 스케줄링 기준. 이만큼은 보장받는다
      limits:   { cpu: 500m, memory: 512Mi }   # 상한. 초과 시 CPU는 스로틀, 메모리는 OOMKilled
```

메모리 limit을 넘으면 컨테이너가 **OOMKilled**된다. `CrashLoopBackOff`의 흔한 원인이다.
Go 앱이면 `GOMEMLIMIT`을 memory limit의 80~90% 수준으로 맞춰주면
GC가 미리 동작해서 OOM을 피할 수 있다. 이건 알면 확실히 눈에 띄는 디테일이다.

---

## 6. 설정과 시크릿 관리

**원칙: 설정은 코드에서 분리하고, 시크릿은 절대 이미지나 저장소에 넣지 않는다** (12 Factor App).

| 방법 | 용도 |
|---|---|
| 환경 변수 | 기본. 12 Factor의 권장 방식 |
| K8s `ConfigMap` | 비민감 설정 파일/값 |
| K8s `Secret` | 민감 값. 단 **기본은 base64 인코딩일 뿐 암호화가 아니다** |
| AWS Secrets Manager / Parameter Store | 자동 로테이션, 감사 로그, IAM 기반 접근 제어 |
| External Secrets Operator | Secrets Manager 값을 K8s Secret으로 자동 동기화 |

`K8s Secret은 암호화가 아니다`는 자주 물어보는 함정이다.
etcd 암호화(`EncryptionConfiguration`)를 켜거나 외부 시크릿 저장소를 써야 한다고 답해야 한다.

---

## 7. DB 마이그레이션 — 배포에서 가장 위험한 부분

**여기를 말할 수 있으면 주니어 중 상위권으로 인식된다.**

### 문제의 핵심

애플리케이션은 롤백할 수 있지만 **스키마 변경은 되돌리기 어렵다.**
게다가 롤링 배포 중에는 **구 버전 코드와 신 버전 코드가 같은 스키마를 동시에 쓴다.**

```
[사고 시나리오]
1. 코드를 배포하면서 컬럼 이름을 name → full_name 으로 변경
2. 롤링 중 구 버전 파드가 아직 name 컬럼을 조회 → 500 에러 폭발
3. 롤백해도 스키마는 이미 바뀌어 있어서 복구가 안 된다
```

### 해결: 확장-수축 패턴 (Expand and Contract)

**스키마 변경을 여러 배포에 나눠서 항상 하위 호환을 유지한다.**

```
[1단계 Expand]  full_name 컬럼을 추가한다 (nullable). 기존 코드는 영향 없음
[2단계]         신규 코드를 배포한다. 쓸 때는 name과 full_name 양쪽에 쓰고, 읽을 때는 name
[3단계 Backfill] 기존 데이터를 full_name으로 채운다 (배치로 나눠서)
[4단계]         읽기를 full_name으로 전환한 코드를 배포한다
[5단계 Contract] 충분히 안정화된 후 name 컬럼을 제거한다
```

번거롭지만 **모든 단계가 롤백 가능하다.** 이게 목적이다.

### 온라인 DDL 주의

MySQL 8.0은 대부분의 DDL을 온라인으로 처리하지만, 큰 테이블에서는 여전히 위험하다.

```sql
-- 상대적으로 안전 (INSTANT / INPLACE)
ALTER TABLE orders ADD COLUMN memo VARCHAR(255) NULL;   -- 8.0에서 INSTANT
ALTER TABLE orders ADD INDEX idx_status (status);        -- INPLACE

-- 위험 (테이블 재생성 + 락)
ALTER TABLE orders MODIFY COLUMN amount BIGINT;          -- 타입 변경
ALTER TABLE orders CHANGE COLUMN name full_name VARCHAR(100);
```

큰 테이블은 `gh-ost`나 `pt-online-schema-change` 같은 도구로 무중단 변경을 한다.
이름만 알아도 답변에 쓸 수 있다.

### 마이그레이션 실행 위치

- **K8s Job / initContainer** — 애플리케이션 배포 전에 한 번 실행
- **앱 시작 시 자동 실행은 위험** — 파드가 여러 개면 동시에 실행된다.
  마이그레이션 도구의 락(golang-migrate는 DB 락을 잡는다)에 의존하게 되므로 권장되지 않는다

```bash
# golang-migrate 예시
migrate -path ./migrations -database "mysql://user:pass@tcp(host:3306)/db" up
```

---

## 8. 배포 후 검증 — 모니터링 (공고에 Sentry/Grafana/CloudWatch가 있었다)

배포는 "배포 완료"가 끝이 아니라 **"이상 없음 확인"이 끝이다.**

| 도구 | 배포 직후 볼 것 |
|---|---|
| **Sentry** | 신규 에러 발생 여부, 에러율 급증. 릴리즈 태그를 붙여두면 어느 배포에서 터졌는지 바로 보인다 |
| **Grafana** | p95/p99 응답 시간, 처리량(RPS), 에러율, CPU/메모리 |
| **CloudWatch** | 애플리케이션 로그, ALB 5xx 카운트, Target 헬스 |

### 알아두면 좋은 개념: 네 가지 골든 시그널

**지연시간(Latency), 트래픽(Traffic), 에러(Errors), 포화도(Saturation)**.
"배포 후 뭘 보나요?"에 이 네 개로 답하면 정리된 답변이 된다.

### Sentry에 릴리즈 연동

```go
sentry.Init(sentry.ClientOptions{
   Dsn:         os.Getenv("SENTRY_DSN"),
   Environment: os.Getenv("APP_ENV"),   // production / staging
   Release:     os.Getenv("GIT_SHA"),   // 이미지 태그와 동일하게 → 에러 ↔ 배포 매칭
})
```

---

## 9. CI 설정 예시 (GitHub Actions)

이 저장소도 `.github/workflows/deploy.yml`로 배포하고 있으니 그걸 설명 소재로 써도 된다.

```yaml
name: deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write        # OIDC로 AWS 인증 (액세스 키를 저장소에 안 넣는 방법)

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'
          cache: true        # 모듈 캐시로 빌드 시간 단축

      - name: Lint
        uses: golangci/golangci-lint-action@v6

      - name: Test
        run: go test -race -coverprofile=coverage.out ./...

      # 액세스 키 대신 OIDC + IAM Role 사용 (시크릿 유출 위험 제거)
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ap-northeast-2

      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr

      - name: Build and push
        env:
          REGISTRY: ${{ steps.ecr.outputs.registry }}
          TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/myapp:$TAG .
          docker push $REGISTRY/myapp:$TAG

      - name: Deploy
        env:
          TAG: ${{ github.sha }}
        run: |
          kubectl set image deployment/myapp app=$REGISTRY/myapp:$TAG
          kubectl rollout status deployment/myapp --timeout=5m
```

**`-race` 플래그**는 Go 테스트에서 데이터 레이스를 잡아준다. CI에 넣어두는 게 관례다.
**OIDC 인증**은 액세스 키를 저장소 시크릿에 넣지 않는 방법이다. 보안 감각을 보여줄 수 있다.

---

## 10. 내 경험 서술 템플릿

빈칸을 채워서 소리 내어 연습한다. **면접에서 필요한 건 이 문단 하나다.**

```
제가 참여한 프로젝트에서는 ______(GitHub Actions / Jenkins)로 배포를 구성했습니다.

main 브랜치에 머지되면 ______가 트리거되고,
먼저 ______(린트 / 테스트)를 실행해서 실패하면 그 지점에서 중단시켰습니다.

통과하면 Docker 이미지를 빌드했는데, ______(멀티 스테이지)를 적용해서
이미지 크기를 ___MB에서 ___MB로 줄였습니다.
태그는 ______(커밋 SHA)로 붙여서 어떤 커밋이 배포됐는지 추적할 수 있게 했습니다.

이미지를 ______(ECR / Docker Hub)에 push하고,
______(kubectl set image / docker compose / SSH 스크립트)로 배포했습니다.

배포 중에 겪은 문제는 ______였고,
______해서 해결했습니다.

배포 후에는 ______(헬스 체크 / Sentry / 로그)로 이상 여부를 확인했습니다.
```

### "배포 중에 겪은 문제" 후보 (하나는 꼭 준비한다)

- 무중단 배포인데 502가 났다 → graceful shutdown 미구현, preStop 부재
- 배포했는데 코드가 안 바뀌었다 → `latest` 태그 + 이미지 캐시
- 헬스 체크가 401을 반환해서 전체 트래픽이 끊겼다 → 인증 미들웨어 예외 처리
- 컨테이너가 계속 재시작됐다 → 메모리 limit 초과 OOMKilled, 또는 liveness probe 오설정
- 환경 변수를 빼먹어서 staging 설정으로 production이 떴다 → 필수 환경 변수 검증 로직 추가
- CI가 너무 느렸다 → 레이어 캐시 순서 조정, 의존성 캐시 도입

---

## 11. 예상 꼬리질문 체크리스트

- [ ] 배포 과정을 처음부터 끝까지 설명해보라 (→ 소스/빌드/이미지/배포/검증)
- [ ] 무중단 배포는 어떻게 하나? 전략별 차이는?
- [ ] 롤백은 어떻게 하나? 이미지 태그를 `latest`로 하면 왜 문제인가?
- [ ] `readinessProbe`와 `livenessProbe`의 차이는? DB 체크는 어디에 넣나?
- [ ] Graceful shutdown이 왜 필요한가? Go에서 어떻게 구현하나?
- [ ] 무중단 배포인데 502가 난다면 원인은? (→ 엔드포인트 전파 지연, preStop)
- [ ] 멀티 스테이지 빌드를 쓰는 이유는?
- [ ] Docker 레이어 캐시를 잘 쓰려면 Dockerfile을 어떻게 쓰나?
- [ ] 컨테이너를 root로 실행하면 왜 안 되나?
- [ ] 시크릿은 어떻게 관리하나? K8s Secret은 암호화된 건가? (→ 아니다, base64)
- [ ] DB 마이그레이션은 배포 전인가 후인가? 롤백은 어떻게 하나?
- [ ] 롤링 배포 중 두 버전이 동시에 도는데 스키마 변경은 어떻게 하나? (→ 확장-수축)
- [ ] 배포 후 무엇을 확인하나? (→ 골든 시그널 4개)
- [ ] `CrashLoopBackOff`가 나면 어떻게 디버깅하나?
      (→ `kubectl describe pod`, `kubectl logs --previous`, 종료 코드 확인)
- [ ] 스테이징 환경은 어떻게 구성했나?

## 12. 자주 하는 실수

- **안 해본 걸 해봤다고 말한다** → 배포 질문은 꼬리질문 밀도가 가장 높다. 한 번에 무너진다.
  선을 그어 답하는 게 훨씬 안전하고, 실제로 더 좋은 평가를 받는다
- `git push`하면 배포된다 수준으로만 말한다 → 각 단계에서 **무엇을 검증하는지**가 핵심이다
- 롤백 이야기를 안 한다 → 배포를 아는 사람은 항상 롤백을 먼저 생각한다
- 무중단 배포를 "롤링 업데이트로 합니다"에서 끝낸다 →
  **헬스 체크 + graceful shutdown이 없으면 롤링 업데이트도 무중단이 아니다**
- DB 마이그레이션을 언급하지 않는다 → 배포에서 가장 위험한 부분인데 대부분 빼먹는다.
  여기서 차이가 난다
