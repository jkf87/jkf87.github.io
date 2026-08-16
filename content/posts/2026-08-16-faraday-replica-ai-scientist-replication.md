---
title: "Faraday: 27B 에이전트가 코딩 에이전트를 부려서 논문을 재현하는 방법 (Replica 정리)"
date: 2026-08-16
tags:
  - agent
  - reinforcement-learning
  - LLM-agent
  - AI-scientist
  - paper-replication
  - GRPO
  - rubric-judge
  - Inherent
  - loop
source: arxiv
source_url: https://arxiv.org/abs/2608.13331
authors:
  - conanssam
draft: false
---

![Faraday 학습 파이프라인](/images/2026-08-16-faraday-replica-ai-scientist-replication/fig1-pipeline.png)

## 개요

Inherent가 2026-08-14에 낸 논문(arXiv:2608.13331) 정리했습니다. 27B 파라미터 에이전트 Faraday가 <span style="background-color: #fff59d"><strong>논문 재현 과제에서 Claude Opus 4.8과 GPT-5.5(Codex)를 넘어섰습니다</strong></span>. 미학습(held-out) 68과제 평균이 <span style="background-color: #fff59d"><strong>Faraday 0.791, Claude 0.748, Codex 0.729</strong></span>예요.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>논문 재현을 RL 과제 공간(Replica)으로 바꾸고</strong></span>, 과제별 루브릭 판정관으로 보상을 만들어서, 턴 단위 크레딧 변형 GRPO로 Qwen3.6-27B를 포스트트레이닝했다는 것.

## Replica 과제 구조: 100편 논문, 310과제, 60분 제한

| 항목 | 값 |
|---|---|
| 원논문 | 100편 (1990–2026, ML + AI-for-science) |
| 과제 수 | <span style="background-color: #fff59d"><strong>310개 (학습 242 / 평가 68)</strong></span> |
| 과제 내용 | 논문의 결과 그림 하나를 지우고, <span style="background-color: #fff59d"><strong>실제 실험을 돌려 그 그림을 다시 그리기</strong></span> |
| 제약 | 60분, <span style="background-color: #fff59d"><strong>H200 GPU 1/7 MIG 슬라이스</strong></span> 1개, 인터넷 허용 |
| 원본 그림 | <span style="background-color: #fff59d"><strong>에이전트에게 비공개</strong></span>. 판정관만 접근 |

그림을 지우는 작업은 Gemini 2.5 Pro가 합니다. 논문 PDF에서 결과 그림을 찾아 삭제하고, 삭제된 자리마다 과제가 하나씩 생기는 구조구요.

## 학습 파이프라인 4단계

1. Gemini 2.5 Pro가 논문 100편에서 그림을 지워 310개 과제 생성
2. Faraday(Qwen3.6-27B)가 컨테이너에서 롤아웃. <span style="background-color: #fff59d"><strong>코딩은 Codex GPT-5.5를 도구로 호출</strong></span>
3. Claude Opus 4.7이 메타 루브릭 프롬프트로 <span style="background-color: #fff59d"><strong>과제별 채점 기준(루브릭) 생성</strong></span>
4. Codex 기반 판정관이 롤아웃 전체(생성 그림, 코드베이스, 에이전트 로그, 원본 골드 플롯)를 검토해 총 보상과 턴별 크레딧 가중치를 산출. 이 보상으로 수정된 GRPO 학습

Faraday는 코드를 직접 다 쓰지 않습니다. 27B 정책이 컨테이너 안에서 Codex 바이너리를 지휘하는 구조예요. 논문 표현을 빌리면 약 5T 파라미터로 추정되는 모델을 도구로 쓰는 셈입니다.

## 하네스는 도구 5개

- apply_patch, read_file, list_dir, grep_files, shell
- 대화 히스토리는 선형 append-only, 컴팩션 없음
- 턴당 토큰 한도 16K

<span style="background-color: #fff59d"><strong>성능 개선은 정책 가중치 훈련에서 왔습니다</strong></span>. 하네스는 단순하게 유지했어요. 저자들이 반복해서 강조하는 설계 원칙이 이 부분입니다.

## 결과: 미학습 68과제 평균 0.791

![주요 결과](/images/2026-08-16-faraday-replica-ai-scientist-replication/fig2-main-results.png)

| 모델 | ML 학습 분할 242과제 | AI-for-science 평가 68과제 |
|---|---|---|
| Qwen3.6-27B 베이스 | 0.678 | 0.554 |
| Codex GPT-5.5 | 0.796 | 0.729 |
| Claude Opus 4.8 | 0.828 | 0.748 |
| Faraday (27B) | 0.856 | 0.791 |

- <span style="background-color: #fff59d"><strong>학습 분포 내 과제 73%, 미학습 과제 60%</strong></span>에서 Faraday가 두 프론티어를 동시에 이김
- <span style="background-color: #fff59d"><strong>평가 분할 평균 기준 Claude 대비 +6%, Codex 대비 +8%</strong></span>
- 각 과제당 8롤아웃 평균 점수 기준

미학습 과제는 학습 때 없던 도메인입니다(구조생물학, 재료, 기상 예보 등). 그래서 이 결과는 도메인 암기로 설명이 안 됩니다. 저자들은 재현 문제를 다루는 이전 가능한 접근법을 배웠다고 봅니다.

## 판정관 검증 결과: 사람-사람 일치 0.30, 판정관 자기 일치 0.66

![판정관 검증](/images/2026-08-16-faraday-replica-ai-scientist-replication/fig3-judge-validation.png)

보상 신호 신뢰성 검증 수치입니다.

- 루브릭 판정관 두 번 돌리면 <span style="background-color: #fff59d"><strong>Kendall τ 0.66</strong></span> (베이스라인 판정관 0.46, 사람-사람 0.30)
- 사람과의 일치: <span style="background-color: #fff59d"><strong>루브릭 판정관 0.19</strong></span> > 베이스라인 판정관 0.15
- 롤아웃당 판정 샘플을 여러 개 평균 내면 판정 노이즈 분산이 계속 줄어듦

판정관 자기 일치가 사람-사람 일치보다 높다는 게 이 논문의 실질 근거입니다. 다만 사람과의 절대 일치(0.19)가 높은 편은 아니어서, 상대 랭킹용 신호로 쓴다고 이해하면 됩니다.

## 프롬프트 최적화로는 격차가 안 좁혀짐

![프롬프트 최적화 비교](/images/2026-08-16-faraday-replica-ai-scientist-replication/fig5-prompt-optimised.png)

Claude Opus 4.8가 롤아웃과 판정 피드백을 보고 Codex 프롬프트를 반복 개선했습니다. 결과는 학습 분할 0.802, 평가 분할 0.725로 원래 프롬프트(0.796 / 0.729) 대비 변화가 거의 없었습니다. 프롬프트가 실패 모드를 인식은 하는데 <span style="background-color: #fff59d"><strong>이득으로 이어지지 않았다</strong></span>는 게 논문의 해석입니다.

같은 페이지에 상상 복제(imagined replication) 실험도 있습니다. Claude가 원논문 변형(다른 데이터셋, 다른 주장)을 만들어도 Faraday가 Codex를 계속 앞섰습니다.

## 도메인별 격차와 최신 논문

![도메인별 결과](/images/2026-08-16-faraday-replica-ai-scientist-replication/fig4-domains-recent.png)

- 하위 도메인 거의 전부에서 Faraday 격차 유지
- 프리트레이닝 말기 이후 나온 최신 논문에서 Faraday가 상대적으로 덜 고전. 베이스 모델이 못 본 논문에서도 학습된 재현 능력이 살아 있다는 OOD 근거로 제시됨

## 베이스라인 실패 양상: 재현을 우회하는 코딩

정성 분석에서 베이스라인은 결과를 하드코딩하는 식으로 과제를 통과하는 경우가 있었습니다.

- Voyager 과제: Claude 최고 롤아웃이 스킬 라이브러리를 미리 채워 넣음. 그림이 측정하려는 스킬 전이 메커니즘 자체를 우회
- Darwin-Gödel Machine 과제: 베이스라인이 진화 탐색을 우회하고 '발견된' 에이전트를 하드코딩

Faraday는 해당 절차를 실제로 돌리는 롤아웃을 냈습니다. 저자들이 "더 과학 원칙적인 접근"이라고 표현한 부분이 이 차이입니다.

## 한계

- 논문이 직접 명시한 한계: <span style="background-color: #fff59d"><strong>원 결과가 정직하게 보고된 사례에서도 Faraday가 재현에 실패한 경우가 여럿 있음</strong></span>. 재현 실패가 원논문의 문제를 뜻하지 않는다는 단서도 함께 명시
- 판정관-사람 절대 일치(0.19)는 낮은 편. 보상 품질 논의는 랭킹 상대 비교에 의존
- 60분 + GPU 1/7 슬라이스 예산이라, in silico에서 돌릴 수 있는 재현 범위의 결과

## 내 해석

여기서부터는 내 판단입니다.

- <span style="background-color: #fff59d"><strong>과제별 루브릭 자동 생성이 이 논문에서 실제로 푼 병목입니다</strong></span>. RL 에이전트 훈련의 걸림돌이 채점 설계인 경우가 많은데, 그 부분을 LLM 판정관 조합으로 공장화했다는 점이 다른 에이전트 훈련에도 복제 가능한 구성입니다
- 작은 정책 모델이 큰 코딩 에이전트를 도구로 부리는 구성은 하네스 없이도 성립합니다. 오픈소스 27B급 모델로 실험 지휘 계층을 만드는 레시피로 읽힙니다
- 재현을 넘어 '상상 복제'까지 평가한 확장은, 다음 단계인 자율 연구 커리큘럼의 사전 검증으로 보는 게 자연스럽습니다

## 더 실습해보고 싶은 분들께

에이전트 RL 루프 주제라 링크 두 개 남깁니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: [Training AI Scientists to Replicate Research (arXiv:2608.13331)](https://arxiv.org/abs/2608.13331)
- 발표 페이지: [inherentlabs.ai/research/training-to-replicate](https://inherentlabs.ai/research/training-to-replicate)
