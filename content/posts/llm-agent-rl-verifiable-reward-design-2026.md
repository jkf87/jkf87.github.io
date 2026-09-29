---
title: "정답이 없는 업무에 강화학습 보상을 만드는 법: LLM 에이전트 RLVR 확장 10편 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "검증 가능 보상(RLVR)이 깨지는 지점과 그 너머의 방법을 2026년 자료 10건으로 비교했습니다. 과정 규칙 검증, 진행 지점 보상, 개입 주입 합성 오라클, 루브릭 트리까지 초록·본문 수치 대조 기준입니다."
tags:
  - LLM 에이전트
  - 강화학습
  - RLVR
  - 보상 설계
refactor_hub_id: agent-rl-04
aliases:
  - rl-for-agents-workshop-huggingface-2026-04-22
  - rl-agent-training-2026-05-27
  - posts/2026-07-23-gear-evidence-aware-rl-long-context
  - posts/2026-07-27-vprm-verifiable-process-reward-models
  - posts/rlvr-environments-llm-agents-2026-07-28
  - posts/reasoning-effort-llm-control-2026-07-29
  - posts/rl-mas-orchestration-traces-2026-09-02
  - posts/2026-09-11-trace-synthesized-rewards-diagnostic-rl
  - posts/2026-09-13-trace-synthesized-rewards-diagnostic-agents
  - posts/2026-09-15-ppm-progressive-point-matching
draft: false
sources_read: "논문 8편 초록 전수 확인 + 본문 HTML 수치 대조(2605.25624·2605.24517·2605.24218·2607.19345·2601.17223·2605.02801·2609.10315·2609.07303), 저자 코드·데이터 확인: github.com/xlang-ai/CUA-Gym·github.com/xxzcc/awesome-llm-mas-rl·huggingface.co/osunlp/QUEST-30B-RL(HTTP 200), ECHO·GEAR·VPRM·TRACE·PPM은 논문 본문에 공개 저장소 링크 없음, 비논문 3종(워크샵 영상·RLVR 환경 영상·Raschka 칼럼) 링크 HTTP 200 확인"
novelty_vs_paper: "각 논문의 방법과 수치는 전부 각 논문의 것이며, 이 글이 새로 만든 것은 검증 출처(주어진 정답 대 직접 만든 검증장치)×채점 단위(결과 대 과정) 2축 지도로 10건을 재배치한 비교 축과 수치 대조 표, 직접 그린 차트 2장임"
---

## 한눈에 보는 결론

RLVR(검증 가능 보상 강화학습)은 정답을 프로그램으로 채점할 수 있는 수학·코드에서 자리를 잡았습니다. 실무 에이전트 업무는 그런 정답이 드뭅니다. 보고서 품질, 장애 원인 귀속, 화면 조작은 최종 결과 하나로 맞고 틀림을 가리기 어렵습니다.

2026년 자료 10건을 비교하면 해법이 세 방향으로 수렴합니다. <span style="background-color: #fff59d"><strong>채점 단위를 결과에서 과정·진행으로 내리는 것, 검증 장치를 문제 안에서 직접 만드는 것, 판정자를 믿을 수 있는 자리에만 두는 것입니다.</strong></span>

- 과정 규칙 검증(VPRM): <span style="background-color: #fff59d"><strong>결과 전용 RLVR 대비 F1 +6.5%, 프롬프팅 최고 성능 대비 최대 +20%</strong></span> ([arXiv:2601.17223](https://arxiv.org/abs/2601.17223)).
- 진행 지점 보상(PPM): <span style="background-color: #fff59d"><strong>통합 통과율 0.004인 문제 세트에서도 학습 신호가 살아남</strong></span> ([arXiv:2609.07303](https://arxiv.org/abs/2609.07303)).
- 합성 오라클(TRACE): <span style="background-color: #fff59d"><strong>35B 학습 모델이 FullAttr@1 0.757로 122B 프롬프팅(0.283)과 Claude Opus 5(0.686)를 앞참</strong></span> ([arXiv:2609.10315](https://arxiv.org/abs/2609.10315)).
- 환경 합성(CUA-Gym): <span style="background-color: #fff59d"><strong>mock 앱 110개·검증 튜플 32,112개로 OSWorld-Verified 62.2%→72.6%(397B-A17B)</strong></span> ([arXiv:2605.25624](https://arxiv.org/abs/2605.25624)).

| 방향 | 자료 | 이번에 확인된 수치 |
|---|---|---|
| 채점 단위를 과정으로 | VPRM·GEAR·PPM·ECHO | F1 +6.5% / n=24 정확도 0.091→0.191 / 8B 2.70%→5.17% |
| 검증 장치를 제조 | TRACE·QUEST·CUA-Gym | 0.596→0.757(r_full) / DeepResearch 36.4%→48.2% / 62.2%→72.6% |
| 판정자·비용 가드레일 | 워크샵 패널·Raschka 정리·RL-MAS 서베이 | 바이너리 판정만 안전 / effort는 원가 노브 / 보상 8종·크레딧 8종 |

기준일: 2026-09-29. 수치는 아래 논문 8편의 arXiv 초록과 본문 표에서 직접 대조한 값이고, 대조되지 않은 수치는 뺐습니다.

![검증 가능 보상 설계 지도](../media/llm-agent-rl-verifiable-reward-design-2026/chart-01-reward-verification-map-2026-09-29.png)

## 무엇을 비교했나

옛 글 10편에 담긴 1차 자료를 공통 축으로 다시 배열했습니다. 논문 8편은 초록과 본문 수치를 대조했고, 발표·영상·칼럼 3종은 링크와 주장 대상을 확인했습니다.

1. [CUA-Gym](https://arxiv.org/abs/2605.25624) — 컴퓨터 사용 에이전트용 검증 환경 대량 합성(Qwen 팀)
2. [ECHO](https://arxiv.org/abs/2605.24517) — 터미널 에이전트에 환경 토큰 예측 손실 추가(Microsoft Research)
3. [QUEST](https://arxiv.org/abs/2605.24218) — 루브릭 트리로 합성 과제를 채점하는 딥리서치 에이전트(OSU NLP)
4. [GEAR](https://arxiv.org/abs/2607.19345) — 긴 컨텍스트에서 증거 중심 복사를 n-gram 보상으로 유도
5. [VPRM](https://arxiv.org/abs/2601.17223) — 도메인 규칙으로 추론 단계별 보상 계산
6. [RL-MAS 서베이](https://arxiv.org/abs/2605.02801) — 멀티에이전트 RL 84편을 오케스트레이션 트레이스로 재분류
7. [TRACE](https://arxiv.org/abs/2609.10315) — 개입 주입으로 정답 오라클을 제조해 진단 에이전트 학습
8. [PPM](https://arxiv.org/abs/2609.07303) — 참조 풀이의 중간 지점 도달을 세그먼트 보상으로 전환(Berkeley/CMU)
9. [RL for Agents 워크샵](https://www.youtube.com/live/cixmqTsi2A4) — 판정자 안전 구역과 환경 생태계 패널(Hugging Face)
10. [RLVR 환경 해설](https://www.youtube.com/watch?v=52UlnK-SW7I) — 데이터셋·정책·롤아웃·루브릭으로 구성된 환경 단위
11. [Controlling Reasoning Effort](https://magazine.sebastianraschka.com/p/controlling-reasoning-effort-in-llms) — reasoning effort를 원가 노브로 다루는 훈련 레시피 비교

## 방법 비교

| 자료 | 푸는 문제 | 핵심 방법 | 확인된 결과 | 조건·한계 |
|---|---|---|---|---|
| VPRM | 결과만 맞으면 통과시키는 검증의 구멍 | 단계 식별자+라벨을 도메인 규칙(Cochrane RoB 2.0)으로 채점 | Qwen2.5-7B F1 +6.5%(결과 전용 RLVR 대비), 프롬프팅 대비 최대 +20% | 결정론적 규칙이 존재하는 도메인 한정 |
| GEAR | 긴 컨텍스트에서 입력 통째로 베끼기 | 핵심 증거 n-gram 중복 보상(α=0.1) + 방해물 페널티(β=0.3) | 8K 3-gram 중복 20~43.7%, 64K 70.8% 측정, 사고 토큰 82% 절감 사례(2,920토큰) | 증거·방해물 경계가 구조적으로 주어진 과제 |
| PPM | 최종 정답 보상의 신호 소멸 | 참조 풀이 reasoning points 도달을 세그먼트 보상으로 채점 | n=24 정확도 0.091→0.191, 통과율 0.004 세트에서 학습 성공 | 1.7B~4B 실험, 판정자(Kendall 0.856) 의존 |
| ECHO | 실패 롤아웃의 학습 신호 낭비 | GRPO에 환경 토큰 cross-entropy(λ=0.05) 추가 | <span style="background-color: #fff59d"><strong>Qwen3-8B 2.70%→5.17%, 14B 5.17%→10.79%</strong></span> | 터미널 과제 중심 |
| TRACE | 검증자가 없는 진단 업무 | 시뮬레이터에 개입을 주입해 오라클 라벨 확보 | FullAttr@1 0.159→0.637(SFT)→0.757(SFT+RL), 툴 호출 22.05→11.73회 | 시뮬레이터 충실도가 상한, no-signal 0.49 vs Opus 0.87 |
| QUEST | 개방형 리서치 과제 채점 | 루브릭 트리로 검증 가능한 제약으로 분해 | GAIA 80.8%, DeepResearch 36.4%→48.2%(SFT→RL) | 합성 과제 기반 |
| CUA-Gym | 컴퓨터 사용 훈련 환경 부족 | Generator·Discriminator·Orchestrator로 환경+보상 합성, 정보 격리 | 환경 110개·튜플 32,112개, OSWorld-V 54.5→62.1%(A3B), 62.2→72.6%(A17B) | mock 앱 기반 |
| RL-MAS 서베이 | 멀티에이전트 보상·크레딧 설계 | 84편을 오케스트레이션 이벤트 트레이스로 재분류 | 보상 8종·크레딧 단위 8종·하위 결정 O1–O5, K2.6 300에이전트·4,000스텝 보고 | 단일 저자 서베이, 컷오프 2026-05-04 |
| 워크샵 패널 | LLM 판정자의 신뢰 범위 | 합의 가능한 바이너리 질문만 판정자에게 위임 | 패널 합의 서술(정량 없음) | 정성 진술 |
| Raschka 정리 | effort 메뉴의 정체 | effort 라벨 조건부 SFT + 길이 페널티 RLVR 레시피 비교 | 모델별로 상이한 레시피 확인 | 칼럼 정리 |

공통 패턴은 세 가지입니다.

- <span style="background-color: #fff59d"><strong>채점 단위를 내릴수록 같은 롤아웃에서 더 많은 학습 신호가 나옵니다.</strong></span> ECHO·PPM·VPRM이 같은 방향입니다.
- <span style="background-color: #fff59d"><strong>정답이 없으면 정답이 있는 상황을 설계합니다.</strong></span> TRACE는 개입 주입, QUEST는 루브릭 트리, CUA-Gym은 환경 합성입니다.
- <span style="background-color: #fff59d"><strong>판정자는 바이너리·검증 가능 영역에서만 쓰는 게 안전하다는 게 워크샵 패널의 합의입니다.</strong></span> PPM은 판정자 품질을 순위상관 0.856으로 실측해 검증했습니다.

## 언제 무엇을 쓰나

- 최종 답을 프로그램으로 비교 가능(수학·코드·SQL): 기본 RLVR으로 시작합니다. <span style="background-color: #fff59d"><strong>부분 점수만 주면 대충 맞추는 전략이 학습되니</strong></span>, TRACE의 r_full(완전 일치 이진 항) 구조를 붙입니다.
- 절차 규칙이 문서로 존재(체크리스트·가이드라인): VPRM처럼 규칙 기반 단계 검증으로 옮깁니다. 신경망 판정자보다 신호가 깨끗합니다.
- 성공 확률이 0에 가까운 긴 과제: PPM처럼 참조 풀이 1개의 중간 지점 도달로 채점합니다. 베이스가 가끔이라도 풀어야 훈련셋에 남기는 관습을 버리게 됩니다.
- 참조 풀이조차 없는 진단·분석: <span style="background-color: #fff59d"><strong>TRACE처럼 시뮬레이터에 개입을 심어 오라클을 만듭니다</strong></span>. 오라클 검증기 통과 에피소드만 훈련에 씁니다.
- 화면 조작 에이전트: CUA-Gym처럼 mock 앱 환경을 합성하되, 보상 함수 작성자가 정답 상태를 모르게 정보 격리를 둡니다.
- 멀티에이전트: 터미널 보상만 기다리지 말고 집계 품질 같은 중간 측정을 먼저 설계합니다. 보상이 촘촘하면 크레딧 분해 부담이 줄어듭니다(서베이).
- 판정자가 꼭 필요할 때: 합의 가능한 바이너리 질문으로 바꿔 쓰고, 정성 판단은 사람 영역으로 남겨둡니다.
- 토큰 비용이 병목일 때: effort를 훈련 노브로 다룹니다. 모델마다 medium의 의미가 다르니 내 워크로드에서 비용-성능 곡선을 직접 잽니다.

## 블로그봇이 직접 확인한 것

2026-09-29 수행 항목입니다.

- 논문 8편 arXiv 초록 페이지 전수 확인(HTTP 200, 제목·주장 대조): 2605.25624, 2605.24517, 2605.24218, 2607.19345, 2601.17223, 2605.02801, 2609.10315, 2609.07303.
- 본문(arxiv.org/html) 표 수치 grep 대조. 확인 값: 환경 110개·튜플 32,112개·54.5→62.1·62.2→72.6(CUA-Gym), 2.70→5.17·5.17→10.79·λ 0.05(ECHO), 80.8·74.1·73.1·36.4→48.2(QUEST).
- 같은 방식 확인: 43.7%·70.8%·α 0.1·β 0.3·2,920토큰·82%(GEAR), +6.5%·최대 20%(VPRM), 84편·300에이전트·4,000스텝(RL-MAS), 0.091·0.191·0.004·0.856/0.768·0.060/0.510(PPM).
- TRACE 수치: 0.159·0.637·0.757·0.596·0.686·0.283·22.05→11.73회·0.434·0.724·0.49/0.87·가중치 0.65/0.30/0.05.
- 코드·데이터 확인: [CUA-Gym 저장소](https://github.com/xlang-ai/CUA-Gym), [awesome-llm-mas-rl](https://github.com/xxzcc/awesome-llm-mas-rl), [QUEST-30B-RL 모델](https://huggingface.co/osunlp/QUEST-30B-RL) HTTP 200. ECHO·GEAR·VPRM·TRACE·PPM은 논문 본문에 저자 저장소 링크를 확인하지 못했습니다.
- 비논문 3종(워크샵 영상, RLVR 환경 영상, Raschka 칼럼) 링크 HTTP 200 확인.
- 대조 실패로 제외한 수치: ECHO "85% 롤아웃 실패"(본문 미확인), QUEST "미드트레이닝 130만 건"(400만 raw triplet 캐시만 확인), RL-MAS "중단 결정 학습 0편"(본문 대조 미확인).
- 차트 2장 직접 작성했습니다. 수치 출처는 각 논문 표입니다.

![검증 설계 변경 전후 성능](../media/llm-agent-rl-verifiable-reward-design-2026/chart-02-verified-gains-2026-09-29.png)

## 한계와 반론

- TRACE·CUA-Gym·QUEST는 합성 시뮬레이터·합성 과제 기반입니다. 실무 데이터와의 격차가 남고, 시뮬레이터 충실도가 결과의 상한을 정합니다.
- VPRM은 결정론적 규칙이 존재하는 도메인에서만 성립합니다. 개방형 창작·평가에는 그대로 적용할 수 없습니다.
- PPM은 1.7B~4B 규모 실험이고 판정자 품질이 새 의존성입니다.
- <span style="background-color: #fff59d"><strong>TRACE의 no-signal 구간(0.49 vs Opus 0.87)은 '증거 부족 시 답하지 않기'가 학습으로 약해질 수 있다는 반론 근거입니다.</strong></span> 배포 전 별도 점검이 필요합니다.
- <span style="background-color: #fff59d"><strong>이 글의 검증은 초록·본문 수치 대조와 링크 확인까지입니다.</strong></span> 실험 재현은 포함하지 않습니다.

## 적용 규칙

1. 검증 가능 보상이 없는 도메인에 RL을 쓰려면, 개입을 심어 정답을 제조할 수 있는지부터 확인합니다(TRACE 패턴).
2. <span style="background-color: #fff59d"><strong>부분 점수만 주지 않고 완전 일치 이진 항을 명시적으로 넣습니다.</strong></span> 0.596→0.757 상승이 그 효과입니다.
3. 신경망 판정자 앞에, 절차 문서를 규칙으로 코딩할 수 있는지 먼저 봅니다(VPRM).
4. 성공 확률 0에 가까운 과제는 참조 풀이 1개의 중간 지점 도달로 채점합니다(PPM).
5. 판정자를 쓴다면 품질을 실측 신호(몬테카를로 성공률과의 순위상관)로 검증하고, 바이너리 질문으로 재구성합니다.
6. <span style="background-color: #fff59d"><strong>SFT 웜스타트를 건너뛰지 않습니다.</strong></span> 베이스 직접 RL은 0.434에 그쳤습니다.
7. 합성 에피소드는 오라클 검증기로 풀 수 있음을 확인한 것만 훈련에 씁니다.
8. 학습 뒤 '증거 부족 시 답하지 않기'를 별도 평가 항목으로 둡니다.

## 자주 묻는 질문

- **LLM 판정자로 보상을 만들면 안 되나요?**
  완전 주관 평가는 위험합니다. 합의 가능한 바이너리 질문으로 바꿔 쓰는 게 워크샵 패널의 합의이고, PPM은 판정자 품질을 순위상관 0.856으로 실측했습니다.
- **정답이 없는 창작·기획 업무에도 RLVR을 쓸 수 있나요?**
  루브릭을 검증 가능한 제약으로 분해할 수 있다면 부분적으로 씁니다(QUEST). 그게 안 되면 검증 게이트 설계가 먼저입니다.
- **작은 모델 학습이 프롬프팅 최고 모델을 앞선다는 게 사실인가요?**
  검증된 도메인에서는 그렇습니다(TRACE 35B 0.757 vs Opus 5 0.686, 122B 프롬프팅 0.283). 도메인 밖 일반화는 미확인입니다.
- **환경을 만들 예산이 없는 팀은 뭘 먼저 하나요?**
  eval harness부터 만듭니다. 좋은 eval은 나중에 RL 환경으로 확장됩니다.

## 참고 자료

1. CUA-Gym — <https://arxiv.org/abs/2605.25624> · 코드 <https://github.com/xlang-ai/CUA-Gym>
2. ECHO — <https://arxiv.org/abs/2605.24517>
3. QUEST — <https://arxiv.org/abs/2605.24218> · 모델 <https://huggingface.co/osunlp/QUEST-30B-RL>
4. GEAR — <https://arxiv.org/abs/2607.19345>
5. VPRM — <https://arxiv.org/abs/2601.17223>
6. RL-MAS 서베이 — <https://arxiv.org/abs/2605.02801> · 아티팩트 <https://github.com/xxzcc/awesome-llm-mas-rl>
7. TRACE — <https://arxiv.org/abs/2609.10315>
8. PPM — <https://arxiv.org/abs/2609.07303>
9. RL for Agents 워크샵 — <https://www.youtube.com/live/cixmqTsi2A4>
10. RLVR 환경 해설 — <https://www.youtube.com/watch?v=52UlnK-SW7I> · [verifiers](https://github.com/PrimeIntellect-ai/verifiers)
11. Controlling Reasoning Effort in LLMs — <https://magazine.sebastianraschka.com/p/controlling-reasoning-effort-in-llms>

기준일: 2026-09-29. 수치는 각 논문의 arXiv 초록과 본문 표 기준입니다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.