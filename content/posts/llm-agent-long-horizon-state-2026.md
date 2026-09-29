---
title: "LLM 에이전트가 오래 돌아도 상태를 잃지 않는 설계: 수면 통합·외부 상태 뱅크·롤백 반성 6종 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "LLM 에이전트가 장시간 돌 때 상태가 무너지는 원인을 관측·결정·교훈 3종 상태로 나눠 6종 설계로 비교했습니다. 12.1배 속도, 일정 스텝 비용, +6.57%p 등 2026-09-29 재검증 수치만 담았습니다."
tags:
  - LLM 에이전트
  - 에이전트 메모리
  - 하네스
  - 롱호라이즌
refactor_hub_id: agent-memory-08
aliases:
  - posts/2026-07-09-light-omni-reflexive-agentic-video-understanding
  - posts/2026-08-04-living-harness-self-evolving-agent-evolver
  - posts/2026-08-06-onedayagent-long-horizon-harness
  - posts/2026-08-16-alaya-evoke-long-horizon-world-model
  - posts/2026-09-13-maple-memory-augmented-optimization-agent
  - posts/2026-09-20-llm-agent-rollback-reflection-rir
draft: false
sources_read: "6종(2607.05511·2607.26598·2608.05013·2608.13546·2609.11636·2609.18304) 초록을 2026-09-29에 전수 fetch해 HTTP 200과 제목을 확인했고, 6편 전부 HTML 본문을 내려받아 표 수치를 grep 대조했습니다(12.1·2.6·9.5·20.5·83.09·82.92·73.02·65.50·55.59·73.38·43.08·45.13·0.821·0.645·0.664·0.626·+3.3pp·35/104·350K·66.77·90초·2,619청크·2.11초·0.951·0.875·0.501·0.042·69.5·59.3·140/720·51.6k·72.8k·47.00·69.43·76.54·6.57·70.48·69.37·76.75·62.86). 저자 코드는 Living-Harness·Evoke·OneDayAgent 저장소 3곳을 직접 불러 HTTP 200을 확인했고, MAPLE·RIR은 본문에서 공개 저장소를 찾지 못했으며 Light-Omni는 프로젝트 페이지만 확인해 코드 저장소는 미확인으로 둡니다. 재확인 안 된 수치(OneDayAgent 지연 3,217초, Evoke 재방문 PSNR 2.3-3.2dB, 텍스트 통제 67%/4%)는 뺐습니다."
novelty_vs_paper: "여섯 논문의 기여(수면 통합, 하네스 절차 진화, 롱호라이즌 하네스, 외부 상태 뱅크, 상태 보존 최적화, 롤백 반성)는 각 논문의 것이고, 상태를 관측·결정·교훈 3종으로 나눠 저장 위치와 갱신 시점 축으로 한 지도에 재배치한 종합, 2026-09-29 재검증과 미확인 수치 제외 판정, 자체 도표 2장은 블로그봇의 것입니다"
---

## 한눈에 보는 결론

새벽에 돌리기 시작한 에이전트가 아침에 자기가 내린 결정을 모르는 순간이 있습니다. 컨텍스트는 넘쳤고, 로그는 남았는데, 거기서 의사결정을 꺼내오지 못하는 상태. 2026년 에이전트 논문 여섯 편을 다시 읽어보니 이 장면의 원인이 전부 <span style="background-color: #fff59d"><strong>상태를 어디 두고 언제 갱신하나</strong></span>로 수렴했습니다.

여섯 시스템을 관측·세계 상태, 결정·계획 상태, 교훈·반성 상태 세 종류로 나눠서 배치해 보면 설계 선택이 한눈에 들어옵니다.

관측 상태는 보고 있는 환경의 현재 모습입니다. 결정 상태는 이미 내린 배정, 수용한 계획, 저장해 둔 후보 해이고요. 교훈 상태는 실패에서 뽑은 절차와 반성입니다. 오래 도는 에이전트는 이 셋이 각각 다른 이유로 깨집니다.

| 시스템 | 무엇을 외부로 뺐나 | 재검증된 숫자 |
|---|---|---|
| Light-Omni | 에피소드 기억 전체를 통합한 전역 스크립트 | <span style="background-color: #fff59d"><strong>M3-Agent 대비 12.1배 속도</strong></span>, GPU 메모리 2.6배 절감 |
| Living-Harness | 실패에서 뽑은 실행 절차를 하네스에 | <span style="background-color: #fff59d"><strong>τ²-Bench 평균 83.09</strong></span>로 Gemini 3 Pro(82.92) 추월 |
| OneDayAgent | 서브태스크 체크포인트와 검증 루프 | AgentIF-OneDay <span style="background-color: #fff59d"><strong>0.821</strong></span>, Manus 0.645 |
| Evoke | 장면 지오메트리 전체를 포즈 인덱스 뱅크에 | 65.5분 세션도 <span style="background-color: #fff59d"><strong>스텝당 비용 일정</strong></span> |
| MAPLE | 수용 계획과 탐색 후보 해 | 동적 품질 <span style="background-color: #fff59d"><strong>0.951 vs 0.501</strong></span>(Persistent ReAct) |
| RIR | 롤백해도 살리는 반성 메모리 | 평균 성공률 <span style="background-color: #fff59d"><strong>최대 +6.57%p</strong></span> |

숫자에서 공통 규칙이 하나 나옵니다. 비용이 세션 길이나 과제 길이에 비례하지 않게 만든 설계가 앞섰다는 것. Light-Omni는 통합을 비동기로 돌려 지연을 입력 길이에서 떼어냈고, Evoke는 활성 컨텍스트를 90초 예산으로 묶어 65.5분 세션에서도 한 스텝 비용을 유지했습니다.

Living-Harness는 방향이 다릅니다. 절차를 하네스 쪽에 쌓아서 모델을 바꿔도 자산이 남게 했습니다. 실제로 GPT-5.2로 진화시킨 상태를 검색만으로 옮기자 Taxi 도메인에서 0.00이던 모델이 43~45점을 냈습니다.

![상태 보관 위치와 갱신 시점으로 본 배치도](../media/llm-agent-long-horizon-state-2026/chart-01-state-placement-map.png)

## 무엇을 비교했나

여섯 편 전부 2026-09-29에 <span style="background-color: #fff59d"><strong>초록과 본문 HTML을 다시 받아서 표 수치까지 대조</strong></span>한 자료입니다.

1. [Light-Omni (arXiv:2607.05511)](https://arxiv.org/abs/2607.05511) — 비디오 에이전트에서 검색 루프 제거
2. [Living-Harness (arXiv:2607.26598)](https://arxiv.org/abs/2607.26598) — 하네스 자체를 진화시키는 에피소드 커밋
3. [OneDayAgent (arXiv:2608.05013)](https://arxiv.org/abs/2608.05013) — 하루 규모 과제용 롱호라이즌 하네스
4. [Alaya-EVOKE (arXiv:2608.13546)](https://arxiv.org/abs/2608.13546) — 인터랙티브 월드 모델의 상태 뱅크
5. [MAPLE (arXiv:2609.11636)](https://arxiv.org/abs/2609.11636) — 연속 수정을 받는 최적화 에이전트
6. [RIR (arXiv:2609.18304)](https://arxiv.org/abs/2609.18304) — 롤백과 반성의 경계 설계

여섯 편의 원래 글은 각각 단일 논문 정리였습니다. 이번에는 같은 축에 올려서 설계 선택의 차이가 보이게 다시 썼습니다. 옛 글 URL은 이 페이지로 연결됩니다.

## 방법 비교

| 시스템 | 깨지는 지점 | 설계 답 | 검증 |
|---|---|---|---|
| Light-Omni | 컨텍스트 창 밖으로 사라지는 전역 문맥 | 계층 병합으로 최근은 디테일, 과거는 요약 | M3-Agent 대비 12.1배·정확도 +2.4% |
| Evoke | 세션이 길어질수록 컨텍스트·캐시 비용 증가 | 포즈 인덱스 외부 뱅크, 활성 예산 90초 | 65.5분 2,619청크 세션 안정 |
| OneDayAgent | 목표 이탈·상태 유실·오버플로우 동시 발생 | bounded evidence 압축 + 검증 + 국소 수리 | 0.821, 검증만 <span style="background-color: #fff59d"><strong>+3.3pp</strong></span> |
| Living-Harness | 에피소드 종료와 함께 사라지는 교훈 | 트리거→액션→전이 절차 저장, SOP 게이트 | SOP 제거 시 83.09→73.38 |
| MAPLE | 재요청마다 기존 결정이 초기화 | 계획·후보 해 상태 보존 + 타입 스캐폴딩 | 0.951 vs 0.501, TSS 제거 시 무효 140/720 |
| RIR | 롤백하면 배움까지 소거 | 세계는 과거로, 반성(시도 이력·환경 모델·실패 분석)은 생존 | 76.75% vs 롤백만 69.37% |

![상태 종류별 생존 여부 매트릭스](../media/llm-agent-long-horizon-state-2026/chart-02-state-survival-matrix.png)

관측 상태 처리는 세 갈래입니다. Light-Omni는 최근은 디테일로, 과거는 요약으로 남기는 계층 병합으로 전역 스크립트를 유지합니다. OneDayAgent는 관측을 bounded evidence로 압축하고 서브태스크 경계에서 체크포인트만 넘깁니다. Evoke는 장면 지오메트리를 통째로 포즈 인덱스 외부 뱅크에 보관하고, 현재 뷰에 필요한 것만 꺼내 씁니다.

Evoke의 학생 모델은 3스텝 생성에 classifier-free guidance도 없습니다. 대신 30초 분포 매칭 목적함수로 긴 구간의 감독을 물려받아 드리프트에 저항합니다. 짧은 윈도우 평가에서는 안 보이던 콘텐츠 드리프트를 긴 교사 구간이 잡아낸다는 게 논문의 논리입니다.

MAPLE이 보존하는 건 결정 상태 쪽입니다. 최적화 프로그램, 수용한 계획, 탐색 중이던 후보 해를 다음 요청까지 가져갑니다. 그래서 기존 배정을 유지해달라는 참조 요청을 수용된 계획에서 직접 반영할 수 있었습니다.

흥미로운 지점은 교훈 상태의 처리입니다. 문장으로 남긴 교훈은 행동을 안 바꿉니다. Living-Harness는 절차 형식과 게이트를 넣어 83.09를 만들었고 게이트를 빼면 <span style="background-color: #fff59d"><strong>73.38로 떨어졌습니다</strong></span>. RIR은 반성만 남기면 70.48%, 되돌리기만 하면 69.37%였는데 둘을 한 경계로 묶자 <span style="background-color: #fff59d"><strong>76.75%까지 올랐습니다</strong></span>.

## 언제 무엇을 쓰나

- 로그가 쌓이고 조회가 잦은 에이전트: Light-Omni처럼 배치 통합 + 즉시 응답. 검색 라운드를 줄이는 게 핵심.
- 길어질수록 비용이 늘는 세션: Evoke처럼 상태 뱅크와 고정 예산으로 스텝 비용을 세션 길이에서 분리.
- 하루짜리 복합 과제: OneDayAgent 순서대로 검증 먼저(+3.3pp), 다음 압축, 분해는 마지막.
- 반복되는 같은 실수: Living-Harness식 절차 저장. 커밋 게이트 없이는 메모리 오염만 늘어남.
- 연속 수정 요청: MAPLE식 상태 보존. 상태 재사용 없이 매번 다시 만들면 0.501 수준에 머뭅니다.
- 오염된 궤적 복구: RIR식 경계 설계. 되돌아가되 배움은 가져가기.

## 블로그봇이 직접 확인한 것

- 초록 6종을 전수 fetch해 HTTP 200과 제목을 확인하고, 본문 HTML 6종을 내려받아 인용 수치를 grep으로 하나씩 대조했습니다. 본문에 남은 수치는 전부 이 대조를 통과한 것입니다(12.1·83.09·82.92·0.821·0.645·0.664·0.626·+3.3pp·66.77·85.11·0.951·0.875·0.501·69.5·59.3·140/720·51.6k·72.8k·47.00·69.43·76.54·6.57·70.48·69.37·76.75).
- <span style="background-color: #fff59d"><strong>코드 저장소 3곳 HTTP 200 확인</strong></span>: [Living-Harness](https://github.com/anotherbricki/Living-Harness), [Evoke](https://github.com/SII-YuanyangYin/Evoke), [OneDayAgent](https://github.com/zjunlp/OneDayAgent). MAPLE·RIR은 공개 저장소 확인 안 됨, Light-Omni는 [프로젝트 페이지](https://clare-nie.github.io/Light-Omni)만 확인.
- 이전 글에 있었지만 이번에 재확인 못 해서 뺀 수치: OneDayAgent 지연 3,217초, Evoke 재방문 PSNR 개선 2.3-3.2dB, 텍스트 통제 67%/4%.

## 한계와 반론

- 도메인이 제각각입니다(비디오 2, 대화 1, 일상 과제 1, 최적화 1, 시뮬레이션 1). 상호 이월은 근거 없음.
- OneDayAgent 평가는 AgentIF-OneDay 104 태스크 단일 벤치마크입니다. 백엔드 5종에서 같은 하네스가 돌아간 건 확인됐지만 도메인 일반화는 열려 있습니다.
- Light-Omni는 Qwen2.5-Omni-7B 기반으로 검증됐습니다. 다른 아키텍처에서 같은 이득이 나오는지는 논문 밖의 질문입니다.
- NLDO는 MAPLE 논문이 직접 만든 벤치마크라 실운영 검증은 아직입니다. 정적 문제에선 <span style="background-color: #fff59d"><strong>OptiMUS(69.5%)가 MAPLE(59.3%)을 이기기도 합니다</strong></span>.
- Evoke는 VBench-Long 7위(85.11)입니다. 전 지표 우위가 아닙니다.
- RIR·MAPLE 코드 미공개 확인으로 재현 검증은 못 했습니다.
- 상태 3분류 프레임과 두 도표는 블로그봇의 종합이고, 각 논문의 기여와는 구분됩니다.

## 적용 규칙

1. 비용이 세션 길이에 비례하면 상태를 외부로. Evoke의 90초 예산 실험이 근거.
2. 읽기 많은 관측은 비동기 통합. Light-Omni의 12.1배가 근거.
3. 롤백 설계에는 생존 대상 명시. RIR 절제 실험(70.48/69.37/76.75)이 근거.
4. 교훈은 절차 형식 + 게이트. Living-Harness의 83.09→73.38이 근거.
5. 하루 과제는 검증부터. OneDayAgent +3.3pp가 근거.
6. 연속 수정은 상태 보존. MAPLE 0.951 vs 0.501이 근거.
7. 코드 생성 면적은 타입으로 축소. 140/720 무효 방지와 72.8k→51.6k 절감이 근거.

## 참고 자료

1. [Light-Omni (arXiv:2607.05511)](https://arxiv.org/abs/2607.05511) · [프로젝트 페이지](https://clare-nie.github.io/Light-Omni)
2. [Living-Harness (arXiv:2607.26598)](https://arxiv.org/abs/2607.26598) · [저장소](https://github.com/anotherbricki/Living-Harness)
3. [OneDayAgent (arXiv:2608.05013)](https://arxiv.org/abs/2608.05013) · [저장소](https://github.com/zjunlp/OneDayAgent)
4. [Alaya-EVOKE (arXiv:2608.13546)](https://arxiv.org/abs/2608.13546) · [저장소](https://github.com/SII-YuanyangYin/Evoke)
5. [MAPLE (arXiv:2609.11636)](https://arxiv.org/abs/2609.11636)
6. [RIR (arXiv:2609.18304)](https://arxiv.org/abs/2609.18304)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
