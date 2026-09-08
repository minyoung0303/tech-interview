# 프록시 (Forward Proxy / Reverse Proxy)

> 기준: Nginx, AWS ALB/NLB/CloudFront, Kubernetes Ingress, Go/Echo
> 실제 면접 질문: "Reverse Proxy와 Forward Proxy에 대해 얼마나 알고 있는지 설명해봐라"
> 공고 스택에 AWS, Kubernetes(EKS)가 있었다. 이 질문은 **인프라 이해도 확인용**이다.

---

## 0. 30초 답변 스크립트

이 질문은 **한 문장 정의를 먼저 던지고 시작하는 게 가장 강하다.**

> "둘 다 클라이언트와 서버 사이에 있는 중개자인데, **누구를 대신하고 누구를 숨기는지**가 다릅니다.
> Forward Proxy는 클라이언트 쪽에 서서 클라이언트를 대신하고 서버에게 클라이언트를 숨깁니다.
> Reverse Proxy는 서버 쪽에 서서 서버를 대신하고 클라이언트에게 실제 서버를 숨깁니다.
> 정의, 실무 사례, Reverse Proxy를 쓰면 얻는 것, 그리고 그 뒤에서 개발할 때 주의할 점
> 순서로 말씀드리겠습니다."

**"누구를 숨기냐"** 라는 기준 한 줄을 먼저 세우면 뒤 설명이 전부 정리된다.

---

## 1. 그림으로 잡는 차이

### Forward Proxy

```
[클라이언트] → [Forward Proxy] → 인터넷 → [서버]
                     ↑
        클라이언트 편에 있다.
        서버는 프록시의 IP만 보고, 진짜 클라이언트가 누군지 모른다.
```

- 프록시를 **클라이언트가 설정한다** (브라우저 프록시 설정, 사내망 강제 프록시, `HTTP_PROXY` 환경변수)
- 클라이언트는 목적지 서버를 알고 있다
- **숨겨지는 쪽: 클라이언트**

### Reverse Proxy

```
[클라이언트] → 인터넷 → [Reverse Proxy] → [서버 A]
                              │         → [서버 B]
                              ↑         → [서버 C]
                  서버 편에 있다.
                  클라이언트는 프록시만 알고, 실제 서버 구성을 모른다.
```

- 프록시를 **서버 운영자가 설정한다**
- 클라이언트는 자기가 프록시와 통신하는지도 모른다. 그냥 그게 서버라고 생각한다
- **숨겨지는 쪽: 서버**

### 비교 표

| | Forward Proxy | Reverse Proxy |
|---|---|---|
| 위치 | 클라이언트 앞 | 서버 앞 |
| 누가 설정하나 | 클라이언트 / 클라이언트 네트워크 관리자 | 서버 운영자 |
| 숨기는 대상 | 클라이언트 | 서버 |
| 클라이언트 인지 여부 | 안다 (설정해야 하므로) | 모른다 |
| 대표 제품 | Squid, 사내 프록시, Charles/Fiddler | Nginx, ALB, CloudFront, Envoy, Traefik |
| 주 목적 | 접근 통제, 익명성, 캐싱 | 로드밸런싱, TLS 종료, 오리진 은닉 |

---

## 2. Forward Proxy 실무 사례

- **사내망 아웃바운드 통제** — 회사에서 특정 사이트를 막거나, 외부로 나가는 트래픽을 전부 로깅/감사
- **캐싱으로 대역폭 절약** — 같은 파일을 여러 직원이 받으면 프록시가 캐시해서 한 번만 외부에서 받는다
- **IP 우회 / 지역 제한 회피** — VPN과 목적이 겹치는 부분
- **크롤러 IP 로테이션** — 여러 프록시를 돌려 차단을 피한다
- **API 클라이언트 디버깅** — Charles Proxy, Fiddler, mitmproxy로 앱의 HTTP 요청을 가로채 확인.
  로컬 개발에서 실제로 써봤으면 이 예시를 드는 게 가장 자연스럽다

### 꼬리질문: "NAT Gateway는 Forward Proxy인가?"

**엄밀히는 아니다.** NAT는 L3에서 IP 주소만 바꿔주는 것이고, HTTP 같은 애플리케이션 계층을
이해하지 못한다. Forward Proxy는 L7에서 요청 내용을 보고 판단한다 (URL 기반 차단, 캐싱 등).
"아웃바운드를 한 지점으로 모은다"는 효과는 비슷하지만 동작 계층이 다르다.
이걸 구분해서 답하면 좋다.

---

## 3. Reverse Proxy가 주는 것 (실무에서 압도적으로 중요)

백엔드 개발자가 매일 마주치는 건 이쪽이다. **여기를 두껍게 말해야 한다.**

### (1) 로드 밸런싱

여러 서버(또는 파드)에 트래픽을 분산한다. 알고리즘도 알아두면 좋다.

- **라운드 로빈** — 순서대로. 기본값
- **least connections** — 연결 수가 가장 적은 쪽으로. 요청 처리 시간이 들쭉날쭉할 때 유리
- **IP hash / sticky session** — 같은 클라이언트를 같은 서버로. 세션을 서버 메모리에 두면 필요하지만,
  **애초에 세션을 Redis 같은 외부 저장소로 빼서 서버를 stateless하게 만드는 게 정석**이다
  (공고 스택에 Redis가 있는 이유 중 하나)

### (2) TLS 종료 (TLS Termination)

HTTPS 복호화를 프록시에서 처리하고, 뒤쪽 애플리케이션 서버로는 HTTP로 넘긴다.

- 인증서를 한 곳에서만 관리하면 된다 (ACM + ALB 조합)
- 암복호화 CPU 비용을 프록시가 흡수한다
- 애플리케이션 코드는 TLS를 몰라도 된다

보안 등급이 높은 환경에서는 프록시 뒤 구간도 다시 암호화한다 (**TLS re-encryption / end-to-end TLS**).

### (3) 캐싱

정적 파일이나 변하지 않는 API 응답을 프록시가 저장해 원 서버 부하를 줄인다.
CloudFront 같은 CDN이 이 역할을 지리적으로 분산해서 하는 것이다.

### (4) 라우팅 (L7이라서 가능한 일)

```nginx
location /api/  { proxy_pass http://backend; }
location /admin/ { proxy_pass http://admin_server; }
location /      { root /var/www/html; }   # 정적 파일은 Nginx가 직접 서빙
```

경로 기반, 호스트(도메인) 기반, 헤더 기반 라우팅. MSA에서 서비스 분기의 진입점이 된다.

### (5) 오리진 은닉 & 보안 경계

실제 서버는 프라이빗 서브넷에 두고 프록시만 퍼블릭에 노출한다.
공격 표면이 한 지점으로 줄어든다.

- **Rate Limiting** — 요청 수 제한. 애플리케이션에 도달하기 전에 차단
- **WAF** — SQL Injection, XSS 패턴 차단 (AWS WAF + ALB)
- **DDoS 완충** — CloudFront/Shield

### (6) 헬스 체크와 무중단 배포

프록시가 주기적으로 백엔드 상태를 확인하고 **죽은 서버로는 트래픽을 안 보낸다.**
이게 무중단 배포의 전제 조건이다. [04-deployment.md](./04-deployment.md)와 직접 이어진다.

### (7) 압축, 요청 버퍼링, 느린 클라이언트 흡수

Nginx가 gzip/brotli 압축을 처리하고, 느린 클라이언트의 요청을 다 받은 뒤에
한 번에 백엔드로 넘긴다. 백엔드 워커가 느린 네트워크에 묶여 있지 않게 된다.
**Go 서버 앞에 Nginx를 두는 이유 중 잘 알려지지 않은 실질적 이득이다.**

---

## 4. L4 vs L7 (거의 항상 이어서 물어본다)

| | L4 (전송 계층) | L7 (애플리케이션 계층) |
|---|---|---|
| 판단 근거 | IP, 포트, TCP/UDP | HTTP 메서드, 경로, 헤더, 쿠키 |
| HTTP 내용 이해 | 못 한다 | 한다 |
| 경로 기반 라우팅 | **불가능** | 가능 |
| TLS 종료 | 안 함 (그대로 통과) | 함 |
| 성능 | 더 빠르고 오버헤드 적다 | 상대적으로 무겁다 |
| AWS | **NLB** | **ALB** |
| 기타 | LVS, HAProxy(tcp mode) | Nginx, Envoy, CloudFront, API Gateway |

**Reverse Proxy는 기본적으로 L7 개념이다.** L4는 "로드 밸런서"라고 부르는 게 더 정확하다.

### 선택 기준

- gRPC, WebSocket, 초고성능 TCP, 고정 IP가 필요하면 → **NLB**
  (ALB도 gRPC/WebSocket을 지원하지만 고정 IP는 NLB의 특성)
- HTTP 경로/호스트 라우팅, TLS 종료, WAF 연동이 필요하면 → **ALB**

---

## 5. Reverse Proxy 뒤에서 개발할 때 주의할 점

**여기가 실무 경험을 보여주는 구간이다. 이론만 아는 지원자와 확실히 갈린다.**

### (1) 클라이언트 IP가 안 보인다

애플리케이션이 보는 원격 주소는 **프록시의 IP**다. 그래서 프록시가 원래 정보를 헤더로 전달한다.

| 헤더 | 내용 |
|---|---|
| `X-Forwarded-For` | 원 클라이언트 IP. 프록시를 거칠 때마다 뒤에 추가된다 |
| `X-Forwarded-Proto` | 원래 프로토콜 (`https`) |
| `X-Forwarded-Host` | 원래 Host 헤더 |
| `X-Real-IP` | Nginx에서 관습적으로 쓰는 단일 클라이언트 IP |
| `Forwarded` | RFC 7239 표준. 위 헤더들을 하나로 합친 형식 |

```
X-Forwarded-For: 203.0.113.10, 10.0.1.5, 10.0.2.7
                 ↑ 원 클라이언트   ↑ 프록시1   ↑ 프록시2
```

### (2) X-Forwarded-For는 위조할 수 있다 (중요)

클라이언트가 처음부터 `X-Forwarded-For: 1.2.3.4`를 넣어 보내면 프록시가 그 뒤에 덧붙인다.
그래서 **맨 왼쪽 값을 그대로 신뢰하면 IP 기반 rate limit이나 차단이 전부 우회된다.**

올바른 방법은 **내가 신뢰하는 프록시 개수를 알고, 오른쪽에서 그만큼 세어 들어간 값을 쓰는 것**이다.

```
신뢰 프록시가 ALB 1개라면 → 오른쪽에서 1번째를 건너뛴 값이 실제 클라이언트
```

Echo에서는 IP extractor로 처리한다.

```go
e := echo.New()

// 신뢰할 프록시 대역을 명시한다. 그 대역에서 온 XFF만 신뢰한다.
e.IPExtractor = echo.ExtractIPFromXFFHeader(
   echo.TrustLoopback(false),
   echo.TrustLinkLocal(false),
   echo.TrustPrivateNet(true), // VPC 내부 ALB → 사설 대역 신뢰
)

e.GET("/whoami", func(c echo.Context) error {
   return c.String(200, c.RealIP()) // 위 설정을 반영한 실제 클라이언트 IP
})
```

기본값(`ExtractIPDirect`)은 XFF를 아예 무시하고 TCP 연결의 원격 주소를 쓴다.
**프록시 뒤에 있으면서 이걸 설정하지 않으면 모든 요청의 IP가 ALB IP로 기록된다.**
Sentry나 CloudWatch 로그를 봐도 실제 사용자 IP를 못 찾게 된다.

### (3) 리다이렉트가 http로 나가는 문제

프록시에서 TLS를 종료하면 애플리케이션은 자기가 HTTP로 서비스된다고 생각한다.
절대 URL로 리다이렉트를 만들면 `http://...`가 나가서 브라우저 경고나 무한 리다이렉트가 생긴다.
→ `X-Forwarded-Proto`를 읽어 스킴을 결정하거나, 가급적 **상대 경로 리다이렉트**를 쓴다.

### (4) 타임아웃이 두 겹이다

ALB의 idle timeout(기본 60초)이 애플리케이션 타임아웃보다 짧으면
백엔드는 아직 처리 중인데 클라이언트는 504를 받는다.
**프록시 타임아웃 ≥ 애플리케이션 타임아웃** 순서로 맞춰야 한다. Nginx라면
`proxy_read_timeout`, `proxy_connect_timeout`, `proxy_send_timeout`.

### (5) 업로드 용량 제한

Nginx `client_max_body_size` 기본값은 1MB다. 이걸 안 올리고 파일 업로드를 붙이면
애플리케이션 코드는 멀쩡한데 **413 Request Entity Too Large**가 난다.
파일 업로드 장애의 흔한 원인이다.

### (6) WebSocket은 업그레이드 헤더를 넘겨줘야 한다

```nginx
location /ws/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;   # 기본 60초면 연결이 계속 끊긴다
}
```

### (7) 헬스 체크 엔드포인트는 인증에서 제외해야 한다

프록시의 헬스 체크는 인증 토큰이 없다. `/healthz`가 인증 미들웨어에 걸려 401을 반환하면
프록시는 서버가 죽었다고 판단하고 트래픽을 다 끊는다. **배포 직후 전면 장애의 전형적 원인이다.**

---

## 6. Nginx 기본 설정 예시

```nginx
upstream backend {
    least_conn;
    server 10.0.1.10:8080 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8080 max_fails=3 fail_timeout=30s;
    keepalive 32;   # 백엔드와 커넥션 재사용. 없으면 매 요청마다 TCP 핸드셰이크
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    client_max_body_size 20m;
    gzip on;
    gzip_types application/json text/css application/javascript;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;

        # 원 요청 정보를 백엔드로 전달
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 5s;
        proxy_read_timeout    65s;   # 애플리케이션 타임아웃보다 길게
    }

    location = /healthz {
        access_log off;
        proxy_pass http://backend;
    }
}
```

`$proxy_add_x_forwarded_for`는 기존 XFF에 `$remote_addr`를 덧붙여준다.
직접 `$remote_addr`만 넣으면 앞단 프록시 정보가 사라진다.

---

## 7. Kubernetes / AWS에서의 구조 (EKS 스택이면 반드시 정리)

```
사용자
  │
CloudFront                (CDN / 엣지 캐싱, Reverse Proxy)
  │
ALB                       (L7 로드밸런서, TLS 종료, WAF)
  │
Ingress (ALB Controller)  (규칙 정의. 실제 트래픽 처리는 ALB가 함)
  │
Service (ClusterIP)       (파드 집합에 대한 안정적인 가상 IP + 로드밸런싱)
  │
Pod → Container           (Go/Echo 애플리케이션)
```

### 알아둘 포인트

- **Ingress는 프록시가 아니라 "규칙 선언"이다.** 실제로 프록시 역할을 하는 건
  Ingress Controller가 프로비저닝한 ALB(또는 Nginx Ingress Controller의 Nginx 파드)다.
  이 구분을 하면 이해도가 확실히 드러난다.
- **Service는 L4다.** kube-proxy(iptables/IPVS)가 파드로 분산한다. HTTP 내용을 모른다.
- **ALB Target Type** — `instance`는 노드 포트를 거치고, `ip`는 파드 IP로 직접 보낸다.
  `ip` 모드가 홉이 하나 줄어 효율적이고 파드 단위 헬스 체크가 정확하다.
- **Service Mesh (Istio, Linkerd)** — 각 파드에 사이드카 프록시(Envoy)를 붙여
  서비스 간 통신까지 프록시가 관리한다. mTLS, 재시도, 서킷 브레이커, 트래픽 분할.
  이름과 목적만 알아도 충분하다.

---

## 8. 예상 꼬리질문 체크리스트

- [ ] Forward Proxy와 Reverse Proxy의 차이를 한 문장으로? (→ 누구를 대신하고 숨기는가)
- [ ] Reverse Proxy를 쓰는 이유 3가지 이상?
- [ ] L4와 L7 로드밸런서의 차이는? 경로 기반 라우팅은 어느 쪽에서 되나?
- [ ] ALB와 NLB를 어떻게 선택하나?
- [ ] TLS 종료가 뭔가? 프록시 뒤 구간은 암호화하나?
- [ ] Reverse Proxy 뒤에서 클라이언트 IP를 어떻게 얻나?
- [ ] `X-Forwarded-For`를 그대로 믿으면 안 되는 이유는? (→ 위조 가능)
- [ ] 로드밸런싱 알고리즘은 어떤 게 있나? sticky session은 언제 필요한가?
- [ ] sticky session을 안 쓰려면? (→ 세션을 Redis로 외부화, stateless 서버)
- [ ] API Gateway와 Reverse Proxy의 차이는? (→ 게이트웨이는 인증/rate limit/API 키 관리 등
      API 관리 기능이 더해진 상위 개념)
- [ ] CDN은 Forward인가 Reverse인가? (→ Reverse. 오리진 서버를 대신한다)
- [ ] Kubernetes Ingress와 Service의 차이는?
- [ ] 헬스 체크는 왜 필요한가? 무중단 배포와 어떤 관계인가?
- [ ] 프록시 타임아웃과 애플리케이션 타임아웃 중 어느 쪽이 길어야 하나?

## 9. 자주 하는 실수

- "Forward는 나갈 때, Reverse는 들어올 때"로만 외운다 → 방향이 아니라 **누구를 대리하는가**가 기준.
  헷갈리면 "숨겨지는 쪽이 누구냐"로 되짚는다
- Reverse Proxy를 로드밸런서와 같은 것으로 본다 → 로드밸런싱은 여러 기능 중 하나다
- L4/L7 구분을 못 한다 → 이 질문은 거의 항상 따라온다
- Nginx만 말하고 실무 환경(ALB, CloudFront, Ingress)과 연결하지 못한다 →
  **공고 스택이 AWS/EKS라면 그 구조로 설명해야 점수가 붙는다**
- XFF 위조 문제를 모른다 → 보안 감각을 보여줄 수 있는 몇 안 되는 지점이다. 꼭 챙긴다
