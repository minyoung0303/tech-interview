# tech-interview

백엔드 개발자 취업 준비 저장소. **CS 지식 · 면접 아카이브 · 알고리즘 · 개념 시각화.**

> 이 파일은 저장소 사용 설명서다. 매일 저녁 여기서 시작한다.

---

## 오늘 할 일 (3줄)

```bash
python tools/review.py          # 오늘 복습할 노트
python tools/quiz.py -n 5       # 꼬리질문 5문제 (소리 내어 답한다)
python tools/check.py           # 커밋 전 정합성 검증
```

알고리즘은 [algorithm/plan.md](./algorithm/plan.md)의 Day N을 따라간다.

---

## 구조

```
notes/          CS 지식.      사람이 쓰고 사람이 읽는다. frontmatter 로 복습 상태를 관리한다
  database/  network/  os/  ds-algo/  infra/  backend/  language/  etc/
interview/      경험과 질문 아카이브. 가장 재사용 가치가 높은 데이터
algorithm/      2주 계획 · 치트시트 · 오답 노트 · 유형별 파이썬 템플릿
visualize/      정적 HTML 애니메이션. GitHub Pages 로 서빙된다 (빌드 없음)
tools/          위 넷을 관리하는 스크립트 4개
```

### 설계 원칙

1. **표준 라이브러리만.** `pip install` 이 필요한 도구는 두지 않는다
2. **`tools/` 가 없어도 저장소는 완전히 동작한다.** md는 md고 visualize는 정적 HTML이다
3. **상태는 md의 frontmatter와 git 히스토리에만 있다.** 별도 DB나 상태 파일을 만들지 않는다
4. **CI는 `tools/check.py` 하나만 호출한다**

---

## 도구

| 명령 | 하는 일 |
|---|---|
| `python tools/check.py` | 링크·앵커·씬 정합성·html 태그·노트 규약·알고리즘 템플릿 검증. **커밋 전에 돌린다** |
| `python tools/new.py <분류> <파일명>` | 정해진 포맷으로 새 노트 생성 |
| `python tools/review.py` | 오늘 복습할 노트. `--all` 로 전체 현황 |
| `python tools/review.py <경로> -c 4` | 복습 완료 기록 (`last_reviewed`, `confidence` 갱신) |
| `python tools/quiz.py` | 꼬리질문 랜덤 출제. `--weak` 로 약한 것만 |

```bash
# 예시
python tools/new.py network http --title "HTTP"
python tools/quiz.py --topic database -n 3
python tools/review.py notes/database/transaction.md -c 4
python tools/check.py --skip-python          # 빠르게
```

---

## 노트 규약

`tools/new.py` 가 이 골격을 만들고 `tools/check.py` 가 검사한다.

```markdown
---
topic: database          # 폴더명과 같아야 한다
title: 트랜잭션
level: core              # core(필수) | plus(가산점) | deep(심화)
status: done             # todo | drafting | done
confidence: 3            # 1~5 자기평가. 복습 주기를 결정한다
last_reviewed: 2026-09-14
tags: [ACID, MVCC]
asked_at: [회사명]        # 실제로 받은 질문이면 기록
---

# 제목

## 0. 30초 답변          ← 암기 대상. status: done 이면 필수
## 1..N 상세
## 꼬리질문 체크리스트    ← `- [ ] 질문 (→ 힌트)` 형식. quiz.py 가 출제한다
## 자주 하는 실수
```

**복습 주기**는 `confidence` 로 정해진다.

| confidence | 1~2 | 3 | 4 | 5 |
|---|---|---|---|---|
| 주기 | 2일 | 5일 | 12일 | 30일 |

---

## 색인

### notes — CS 지식

| 분류 | 노트 | 시각화 |
|---|---|---|
| database | [트랜잭션](./notes/database/transaction.md) | [transaction.html](./visualize/transaction.html) |
| database | [인덱스](./notes/database/db-index.md) | [db-index.html](./visualize/db-index.html) |
| infra | [프록시](./notes/infra/proxy.md) | [proxy.html](./visualize/proxy.html) |
| infra | [배포](./notes/infra/deployment.md) | [deployment.html](./visualize/deployment.html) |
| infra | [인프라 9문항](./notes/infra/infra.md) | [scaling](./visualize/scaling.html) · [container](./visualize/container.html) · [vpc](./visualize/vpc.html) · [dbscale](./visualize/dbscale.html) |
| backend | [결제 멱등성](./notes/backend/idempotency.md) | [idempotency.html](./visualize/idempotency.html) |

### interview — 경험과 질문

| 파일 | 용도 |
|---|---|
| [asked.md](./interview/asked.md) | **실제로 받은 질문과 내 답변.** 가장 가치 높은 파일 |
| [stories.md](./interview/stories.md) | 경험 서술 (STAR). 노트 개수보다 이게 합격을 만든다 |
| [reverse-questions.md](./interview/reverse-questions.md) | 면접관에게 물어볼 역질문 |

### algorithm

| 파일 | 용도 |
|---|---|
| [plan.md](./algorithm/plan.md) | 2주 14일 계획, 문제 푸는 절차 7단계, 복잡도 역산표 |
| [cheatsheet.md](./algorithm/cheatsheet.md) | 파이썬 문법·자료구조·함정 요약 |
| [wrong.md](./algorithm/wrong.md) | 오답 노트 (D+1 / D+3 / D+7 재풀이) |
| [templates/](./algorithm/templates) | 유형별 템플릿 12개. 전부 실행 가능 |

```bash
python algorithm/templates/run_all.py     # 템플릿 12개 자체 검증
```

### visualize

애니메이션 9개 주제, 66장면. [visualize/index.html](./visualize/index.html) 이 허브다.

GitHub Pages 를 켜면 폰에서도 볼 수 있다 (**Settings → Pages → Source: main / root**).
빌드 단계가 없으므로 켜기만 하면 끝이다.

```
https://minyoung0303.github.io/tech-interview/visualize/
```

---

## 하루 루프

```
아침 15분 (이동 중)
  python tools/quiz.py -n 5
  또는 폰으로 visualize 한 페이지의 "정리" 문단만 읽기

저녁 2.5시간
  0:00–0:20  알고리즘 재풀이        algorithm/wrong.md 의 D+1 / D+3 / D+7
  0:20–1:50  알고리즘 새 문제        algorithm/plan.md Day N
  1:50–2:20  CS 노트 1개 작성/보강   python tools/new.py <분류> <파일명>
  2:20–2:30  복습 기록 + 검증 + 커밋
             python tools/review.py <경로> -c 3
             python tools/check.py
             git add . && git commit -m "notes: ..."
```

커밋 자체가 학습 기록이 된다. 별도 트래커가 필요 없다.

---

## 백로그

아직 안 쓴 주제. 위쪽이 면접 빈도가 높다.

- [ ] **network** — HTTP/1.1·2·3, HTTPS/TLS 핸드셰이크, TCP vs UDP, 3-way handshake, TIME_WAIT, DNS, 쿠키/세션, CORS
- [ ] **os** — 프로세스 vs 스레드, 컨텍스트 스위칭, 뮤텍스/세마포어, 데드락 4조건, 가상메모리/페이징, 블로킹·논블로킹 × 동기·비동기
- [ ] **database** — 정규화, 조인 종류, 락(공유/배타/갭), NoSQL vs RDB, 커넥션 풀
- [ ] **ds-algo** — 해시 충돌 해결, BST/AVL/B-Tree/힙, 그래프 표현, 정렬 비교, 시간복잡도
- [ ] **backend** — REST API 설계, 캐시 전략(Cache-Aside, 캐시 스탬피드), 낙관적·비관적 락, 메시지 큐, MSA vs 모놀리식
- [ ] **language** — 지원 포지션 스택 (Go면 goroutine/channel/GC, Java면 JVM·GC·Spring 트랜잭션 전파)
- [ ] **etc** — Git 브랜치 전략, rebase vs merge

**시각화는 "글로 읽으면 헷갈려서 그림이 필요한 것"만 만든다.** 페이지 하나가 700줄이라 전부 만들면 지친다.
TLS 핸드셰이크, TCP 상태 전이, 락 경합 타임라인 정도가 해당한다.

---

## 커밋 메시지

```
notes:  CS 노트 추가/보강
algo:   알고리즘 풀이·템플릿
vis:    시각화 페이지
iv:     면접 아카이브
tools:  도구
fix:    링크·오타·오류 수정
```
