---
title: "Macaron-V1: Towards Open Continual Learning with Self-Improvement and Mixture-of-LoRA — 기반 모델을 동결한 채 LoRA 어댑터로 계속 학습하는 에이전트 시스템"
date: 2026-08-13
tags:
  - agent
  - LLM
  - continual-learning
  - self-improvement
  - harness
  - LoRA
  - model-harness-co-design
  - recursive-self-improvement
  - RL
  - open-source
authors:
  - конанссам
---

![Macaron-V1-Venti 메인 결과](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-1-p1.png)

Mind Lab이 2026년 8월 10일에 공개한 Macaron-V1은 개방형 에이전트 모델 패밀리입니다. 744B GLM-5.2 기반 모델을 동결하고 4개 LoRA 전문가 어댑터(chat, agent, coding, GenUI)를 올리는 구조로, 배포 후 경험을 통한 지속 학습(continual learning)과 재귀적 자기개선(recursive self-improvement)을 설계 목표로 삼습니다.

## Mixture-of-LoRA (MoL) 아키텍처

![MoE, Skills, MoL 비교](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-2-p4.png)

MoL은 세 가지 스케일링 방식 중 세 번째입니다. MoE는 기반 자체를 확장하고, 스킬은 고정 모델 주변의 비계를 확장하며, MoL은 기반을 동결하고 LoRA 어댑터를 조합합니다.

설계 원칙 (Mind Lab 2026c):

> 체인 사고 패턴이 유사한 작업을 하나의 LoRA로 묶고, 패턴이 크게 다른 작업은 별도 LoRA로 분리한다.

Macaron-V1-Venti의 4개 어댑터:

| 라벨 | 이름 | 담당 영역 |
|---|---|---|
| L0 | Chat | 일반 대화, 라우팅 진입점 |
| L1 | Agent | 개인 비서, 도구 사용, 상태ful 작업 |
| L2 | Coding | 코드 생성, 터미널 작업 |
| L3 | GenUI | UI4A 기반 컴포넌트 렌더링 |

기반 모델 gradient는 흐르지 않습니다. 어댑터만 훈련 대상입니다.

## 라우팅 루프

별도의 라우터 모델을 두지 않고, L0의 추론으로 라우팅을 결정합니다. 사용자 턴마다 3단계 라이프사이클이 실행됩니다.

| 단계 | 설명 | Venti 지연시간 |
|---|---|---|
| Route | L0가 24토큰 예산으로 L0~L3 라벨 출력 | 0.54초 |
| Answer | 선택된 어댑터가 응답 생성 | (작업별 상이) |
| Summary | 192톤 이하 요약을 서버에 저장 | 0.97초 |

라우팅+요약 오버헤드는 3-hop 총 시간의 약 32% (Venti), 30% (Tall).

라우팅 정확도: 6,448샘플 학습 데이터 트레이스에서 99.12% (Venti), 99.04% (Tall). 단, 이 트레이스는 학습 데이터에서 추출한 것으로 일반화 추정치가 아닙니다.

### Per-Adapter Conversation View

각 어댑터는 자기만의 대화 히스토리 뷰를 갖습니다. 자신의 과거 발화는 전문 그대로, 다른 어댑터의 발화는 192톤 요약 하나로 압축됩니다. append-only 타임라인에서 결정론적으로 재구성되므로, 같은 어댑터에 재진입하면 byte-identical prefix가 생성되고 엔진의 native prefix cache가 hit합니다.

### KV 캐시 재사용

두 계층: (A) stable own-view를 통한 emergent 재사용 (프로덕션 경로, 엔진 패치 불필요), (B) same-request route-decode overlay (실험적). 3-arm Vita 비교에서 direct 0.636±0.026, routed KV-off 0.650±0.030, routed KV-on 0.632±0.019로, 5-seed unpaired에서 유의미 차이를 감지하지 못했지만 동등성을 확립하지는 않았습니다.

## 모델-하네스 공동 설계

![GenUI 접근 방식 비교](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-3-p13.png)

### UI4A: 컴포넌트 네이티브 GenUI

HTML 네이티브의 표현력과 스키마 네이티브의 검증성 사이의 trade-off를 해결하기 위해, UI4A는 에이전트가 제한된 런타임 경계 내에서 일반 프론트엔드 코드를 작성하게 합니다. Import + Component + State + Action 구조. 측정 결과 raw HTML 평균 1,224 토큰 대비 UI4A 평균 672 토큰 (45% 절감).

![UI4A-Bench 갤러리](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-4-p14.png)

### REPL 에이전트 하네스

![실행 가능한 합성: 함수 호출 vs REPL](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-5-p15.png)

도구 호출을 discrete JSON-per-turn이 아닌 persistent Python namespace에서 처리합니다. 의존 값이 변수로 유지되어 중간 관찰이 모델을 재통과하지 않습니다. `save_tool` → 검증 → `promote_tool` 순서로, 검증 통과한 헬퍼만 이후 세션에서 호출 가능합니다.

### Harness Context Protocol (HCP)

TOML 기반 버전 계약으로, 모델 선택·도구 정책·스킬·프롬프트·MCP 서버·훅·세션 상태를 직렬화합니다. 학습/서빙 설정 차이를 감사 가능하게 만듭니다.

## 재귀적 자기개선 (RSI)

![3개 루프가 하나의 하네스를 공유](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-6-p17.png)

3단계 사이클 (MindForge가 오케스트레이션):

1. Discovery — 시드 뱅크에서 현재 모델이 신뢰성 있게 풀지 못하는 작업 변형 제안. 각 제안은 검증 가능한 답 또는 평가 루브릭을 포함해야 함
2. Expansion — 동결된 모델로 작업 실행. HCP 설정(프롬프트, 스킬, 도구 노출, 훅)만 변경하면서 통과하는 설정 탐색
3. Update — 선택된 궤적으로 GRPO 기반 LoRA 어댑터 업데이트

### 확장 단계 결과

동결된 GLM-5.2 기반이 TerminalBench 2.1에서 전부 실패한 122개 작업 (29개 소스 패밀리)에 대해:

- 단일 설정 전체 스윕: 4/122 (3.3%), 11/122 (9.0%)
- 적응적 설정 탐색: 69개 job, 450 시도 (작업당 3.69회)로 122/122 달성
- 오류율: 단일 설정 2개 job에서 109건 중 97건의 하네스 에러 집중
- 적응 탐색의 per-attempt 효율은 단일 설정의 13배

이 결과는 설정 탐색 커버리지를 측정한 것이며, 가중치 업데이트 후 일반화를 측정한 것은 아닙니다.

## 인프라

- MinT — LoRA RL 수명주기 관리. adapter revision을 불변 스냅샷으로 export. 백만 단위 어댑터 카탈로그
- LongStraw — 응답 전용 장문 실행. B300 8대에서 CP8 LayerSplit으로 900K 토큰 TTFT 107.1초 → 49.2초. EAGLE 사용시 TPOT 8.6ms, 110 tokens/s (concurrency 1)
- Sparse MoE 안정화 — FlashMLA sparse attention이 GLM-5.2 48 설정에서 전부 clean. 기본 DSA decode는 GLM-5.1에서 6/48만 clean

## 배포 효율

MoL은 기반 1개만 상주. Venti 구성에서 기반 744B + 어댑터 약 30.8B = 약 774.8B 논리 파라미터. 복제 배치(4개 머지된 복사본, 2.976T) 대비 74.0% 절감. H20 1대에서 56K 토큰 16 동시 요청 지원.

## 평가 및 한계

Personal Intelligence (ChatBench, LivingBench), UI4A-Bench, 범용 능력 벤치마크에서 6개 비교 모델 대상 평가. 보고서가 명시하는 한계:

- 단일 LoRA 예산 매치 비교 부재 (간섭 효과 미정량화)
- 라우팅 트레이스가 학습 데이터에서 추출 (일반화 추정치 아님)
- KV 재사용 비교가 5-seed unpaired (동등성 미확립)
- 세대 간 누적 개선 미측정
- 집단 지능 (독립 훈련 전문가 합성)은 목표 단계

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
