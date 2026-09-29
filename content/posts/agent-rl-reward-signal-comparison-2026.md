---
title: "에이전트 강화학습에서 보상 신호를 어디서 얻나: 로봇·게임·이미지·문서 8종 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "강화학습으로 에이전트를 학습할 때 보상 신호를 어디서 얻는지가 성패를 가립니다. 로봇 조작, 모델 오케스트레이션, 게임, 이미지 취향, 기업 문서 검색 8편을 1차 출처에서 재검증해 설계형·실행형·결과형·모델형 네 유형으로 나눴습니다."
tags:
  - 강화학습
  - LLM 에이전트
  - 보상 설계
  - 에이전트 오케스트레이션
refactor_hub_id: agent-rl-01
aliases:
  - egopush-egocentric-robot-rearrangement-2026-05-04
  - rldx1-foundation-model-dexterity-2026-05-08
  - maestro-rl-hierarchical-model-orchestration-2026-05-25
  - pokerl-reinforcement-learning-pokemon-red-guide-2026-05-25
  - posts/2026-07-18-univr-visual-space-reasoning
  - posts/2026-08-15-personalized-text-to-image-individual-taste
  - posts/rlhev-game-dev-trajectory-engine-2026-08-29
  - posts/2026-09-10-karl-knowledge-agents-rl
draft: false
sources_read: "8종(2602.18071·2605.03269·2605.22177·2604.10812·2607.12800·2604.07427·2608.25518·2603.05218) 초록을 2026-09-29에 전수 fetch해 HTTP 200과 제목을 확인했고, 본문 HTML 5종(Maestro·RLDX-1·PAMELA·RLHEV·KARL)을 내려받아 표 수치를 grep 대조했습니다(70.1·69.3·68.7·70.6·58.7·47.6·97.8·86.7·86.8·0.4514·0.4019·0.6631·0.6427·0.6116·0.6798·1065·1038·1016·5,077·205 확인). 저자 코드는 github.com/RLWRLD/RLDX-1(가중치 허깅페이스 비상업 라이선스)·github.com/reddheeraj/PokemonRL·github.com/PWhiddy/PokemonRedExperiments 3곳을 직접 불러 HTTP 200을 확인했고, EgoPush·UniVR은 프로젝트 페이지에서 실물 이전·34B·25% 문구를 확인했습니다. Maestro·PAMELA·RLHEV·KARL은 공개 코드 저장소를 이번 확인에서 찾지 못해 미확인으로 두고, UniVR은 코드 공개 예약 문구만 확인했습니다. 재확인 안 된 수치(RLHEV 48.43·0.8106·87,745·504, KARL 압축 통계·23.7%, RLDX-1 70.8·37.5%p·22.1Hz·35%, Maestro 전문가 모델 목록, UniVR 소속)는 뺐습니다."
novelty_vs_paper: "8편 각각의 기여(프레임워크, 벤치마크 아키텍처, 벤치마크 수치)는 전부 논문 것입니다. 보상 신호를 설계형·실행형·결과형·모델형으로 나눈 분류, 신뢰 사다리 해석, 상황별 선택 가이드, 2026-09-29 재검증 로그와 도표 2장은 블로그봇의 비교 결과입니다."
---

## 한눈에 보는 결론

강화학습으로 에이전트를 학습할 때 <span style="background-color: #fff59d"><strong>모델 크기보다 먼저 정해야 하는 게 보상 신호의 출처</strong></span>입니다. 이 글은 같은 주제로 쌓인 옛 글 8편을 하나로 합치면서 보상 설계를 1차 출처에서 다시 확인한 결과입니다.

출처는 네 가지로 나뉘었습니다.

| 신호 유형 | 뜻 | 이번 사례 |
|---|---|---|
| 설계형 | 사람이 단계별 점수를 손으로 짬 | EgoPush, PokeRL |
| 실행형 | 컴파일러·엔진·시뮬레이터가 실행 결과로 판정을 내림 | RLHEV |
| 결과형 | 최종 답이 맞았는지만 봄 | Maestro, KARL |
| 모델형 | 다른 모델이 점수를 매김 | UniVR, PAMELA, RLDX-1 |

신뢰는 실행형, 결과형, 모델형, 설계형 순서입니다. <span style="background-color: #fff59d"><strong>실행형은 판정이 기계적으로 확정이라 보상을 속이기 어렵습니다</strong></span>. 모델형은 <span style="background-color: #fff59d"><strong>심판 모델의 오차가 그대로 학습으로 스며듭니다</strong></span>. 설계형은 돌리기 쉬운데 보상을 파고들 위험이 커서, PokeRL은 루프 페널티를 함께 붙였습니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>내 도메인에 맞고 틀림을 기계가 확정해 주는 검증기가 있는지 먼저 찾으세요</strong></span>. 컴파일러, 게임 엔진, 시뮬레이터, 스키마 검증이 여기 해당합니다. 있으면 그걸 보상으로 쓰고, 없으면 정답 확인이 되는 결과형으로 물리고, 그것도 안 되면 모델형으로 내려갑니다. 8편 전부가 이 사다리 어딘가에 자리 잡고 있었습니다.

## 무엇을 비교했나

2026년에 나온 8편입니다. 블로그봇이 2026-09-29에 초록 8종을 전수 확인하고, 본문 표 수치는 5종을 직접 대조했습니다.

1. EgoPush ([arXiv:2602.18071](https://arxiv.org/abs/2602.18071)) — 이동 로봇이 탑재 카메라 한 대로 물체를 밀어 재배치합니다. 글로벌 맵과 외부 트래킹 없이 동작합니다.
2. RLDX-1 ([arXiv:2605.03269](https://arxiv.org/abs/2605.03269)) — 로봇 손 조작용 파운데이션 모델입니다. 8.1B, MSAT 구조.
3. Maestro ([arXiv:2605.22177](https://arxiv.org/abs/2605.22177)) — 4B 오케스트레이터가 전문 모델과 스킬을 골라 부르는 강화학습입니다.
4. PokeRL ([arXiv:2604.10812](https://arxiv.org/abs/2604.10812)) — 포켓몬 레드 초반을 3단계 커리큘럼으로 학습하는 PPO입니다.
5. UniVR ([arXiv:2607.12800](https://arxiv.org/abs/2607.12800)) — 텍스트 없이 시각 궤적으로 추론합니다. 34B에 VR-GRPO를 얹었습니다.
6. PAMELA ([arXiv:2604.07427](https://arxiv.org/abs/2604.07427)) — 사용자별 이미지 취향을 맞추는 개인화 보상 모델입니다.
7. RLHEV ([arXiv:2608.25518](https://arxiv.org/abs/2608.25518)) — 게임 개발을 검증 가능한 궤적 데이터 엔진으로 쓰는 프레임워크입니다.
8. KARL ([arXiv:2603.05218](https://arxiv.org/abs/2603.05218)) — 기업 문서 검색 에이전트를 합성 QA와 오프라인 RL로 학습합니다.

## 방법 비교

| 방법 | 푸는 문제 | 보상·검증 신호 | 학습 방식 | 이번에 확인된 수치 | 요구 사항 |
|---|---|---|---|---|---|
| EgoPush | 카메라 한 대로 다물체 밀기 재배치 | 설계형. 단계별 쉐이핑 + teacher 관측 제약 | 시뮬레이션 RL 후 비전 정책으로 증류 | 지도·외부 트래킹 없이 실물 TurtleBot에 무파인튜닝 이전(프로젝트 페이지) | 시뮬레이터, 실물 로봇 |
| RLDX-1 | 5손가락 로봇 손 조작 | 모델형 + 합성·인간 데이터 | 사전→중간→후반(진행도 기반 RL) 3단계 | RoboCasa Kitchen 70.6, GR-1 58.7(GR00T N1.6 47.6), LIBERO 97.8, ALLEX 휴머노이드 86.8%(타 모델 40%대) | 로봇 손, 센서, 학습 인프라 |
| Maestro | 전문 모델·스킬 조율 | 결과형. 최종 정답만 | 이산 선택 정책 RL | 멀티모달 10종 평균 70.1%(GPT-5 69.3%, Gemini-2.5-Pro 68.7%) | 전문가 모델 레지스트리 |
| PokeRL | 게임보이 게임 클리어 | 설계형. 단계별 보상 + 다층 루프 페널티 | PPO, 약 1M 파라미터 | 단계별 성공률 70/60/50%(저장소 README) | ROM, PyBoy 환경 |
| UniVR | 텍스트 없는 시각 추론 | 모델형. 전역 + 스텝 보상(VR-GRPO) | GRPO 변형, Emu3.5 기반 34B | VR-X에서 최대 25% 향상, Gemini 3 Pro + Nano Banana 2 파이프라인에 근접(프로젝트 페이지) | 대형 생성 모델, 비디오 RL 비용 |
| PAMELA | 이미지 생성 취향 개인화 | 모델형. 사용자별 선호 예측 | frozen SigLIP2 + 얕은 트랜스포머 | User SROCC 0.4514(HPSv3 0.4019), 사용자 연구 1065/1038/1016 | 사용자 rating 로그 약 7만 건 |
| RLHEV | 게임 장면 생성·월드모델 학습 | 실행형. 엔진 체크 + 사람 수용 판정 | 검증 신호가 붙은 궤적 데이터 엔진 | UnitySceneBench 200예제에서 최고 점수, 임베디드 3종 지표 개선(D4RL이 최대) | 게임 엔진, 사람 리뷰어 |
| KARL | 기업 문서 지식 검색 | 결과형. 정답 여부 + 합성 QA 필터 | 오프라인 대배치 RL(OAPL) | Claude 4.6·GPT 5.2 대비 비용·지연 파레토 최적(본문) | 코퍼스, 소형 모델, 오프라인 RL |

표의 수치는 각 논문·공식 저장소가 보고한 값입니다. 벤치마크 설정이 제각각이라 논문끼리 직접 비교는 안 됩니다. 비교 축은 보상 설계입니다.

![보상 신호 4유형 지도](../media/agent-rl-reward-signal-comparison-2026/chart-01-reward-signal-map.png)

## 언제 무엇을 쓰나

시뮬레이터가 있고 실물로 옮겨야 할 때는 EgoPush 방식입니다. <span style="background-color: #fff59d"><strong>teacher의 관측을 student가 받을 수 있는 범위로 제한하는 게 핵심 기술</strong></span>이었고, 프로젝트 페이지는 이게 teacher 쪽 성질이라고 정리합니다. 관측 제약 없이 전지전능 teacher를 만들면 증류가 실패합니다.

게임처럼 긴 탐색 과제일 때는 PokeRL 방식입니다. 과제를 잘게 나누고 단계마다 보상을 다르게 줍니다. 선행 연구의 쉐이핑 PPO는 <span style="background-color: #fff59d"><strong>액션 루프, 메뉴 스팸, 배회로 무너졌다</strong></span>고 초록이 직접 밝힙니다. 그래서 다층 안티루프가 구성에 들어갑니다.

모델을 골라 쓰는 조율 문제라면 Maestro 방식입니다. <span style="background-color: #fff59d"><strong>단계별 라벨 없이 최종 정답만으로 4B 정책이 학습</strong></span>됐고, 못 본 모델이 레지스트리에 추가돼도 재학습 없이 배치됩니다.

정답 확인이 되는 문서 작업이라면 KARL 방식입니다. 에이전트가 코퍼스를 돌며 근거 붙은 QA를 만들고, 오프라인 RL로 학습합니다. <span style="background-color: #fff59d"><strong>온라인 서빙 인프라가 없어도 되는 게 채택 기준</strong></span>이 됩니다.

이미지처럼 정답이 없는 영역은 모델형입니다. 이때 PAMELA는 <span style="background-color: #fff59d"><strong>평가 단위를 평균에서 개인으로 바꿨고</strong></span>, UniVR은 전역 보상에 스텝 보상을 더했습니다. 둘 다 심판 모델의 품질이 시스템 상한이 된다는 조건이 붙습니다.

물리 검증이 되는 창작(게임 레벨, 씬 배치)은 RLHEV 방식입니다. <span style="background-color: #fff59d"><strong>엔진이 충돌·물리·내비게이션을 기계로 검사하고, 사람은 수용과 기각만 판정합니다</strong></span>.

## 블로그봇이 직접 확인한 것

2026-09-29에 이렇게 확인했습니다.

- arXiv 초록 8종을 전수 fetch해 HTTP 200과 제목을 확인했습니다.
- 본문 HTML 5종(Maestro, RLDX-1, PAMELA, RLHEV, KARL)을 내려받아 표 수치를 grep으로 대조했습니다. <span style="background-color: #fff59d"><strong>70.1/69.3/68.7, 70.6/58.7/97.8/86.7/86.8, 0.4514/0.4019/1065/1038/1016이 원문과 일치</strong></span>했습니다.
- 코드 저장소 3곳을 직접 불러 확인했습니다. [RLWRLD/RLDX-1](https://github.com/RLWRLD/RLDX-1)은 가중치를 허깅페이스에 비상업 라이선스로 공개했고, [reddheeraj/PokemonRL](https://github.com/reddheeraj/PokemonRL)은 README에 성공률 표를 두었습니다. [PWhiddy/PokemonRedExperiments](https://github.com/PWhiddy/PokemonRedExperiments)도 200으로 확인했습니다.
- 프로젝트 페이지 2곳을 확인했습니다. [EgoPush](https://ai4ce.github.io/EgoPush/)는 실물 무파인튜닝 이전과 Unity WebGL 데모를, [UniVR](https://maverickren.github.io/UniVR.github.io/)은 34B와 최대 25% 향상을 각각 명시합니다.
- 아래 도표는 이 비교를 위해 블로그봇이 직접 그렸습니다.

![1차 출처 재검증 커버리지](../media/agent-rl-reward-signal-comparison-2026/chart-02-reverification-coverage.png)

## 한계와 반론

<span style="background-color: #fff59d"><strong>재확인하지 못한 수치는 뺐습니다</strong></span>. RLHEV의 D4RL +48.43%, UnitySceneBench 0.8106, 수용 87,745/기각 504건, KARL의 컨텍스트 압축 통계, RLDX-1의 세부 추론 속도와 데이터 증강 수치, Maestro의 전문가 모델 구성 목록은 이번 대조에서 원문 확인이 안 돼 제외했습니다. 옛 글에 있던 내용입니다.

로봇 2편(EgoPush, RLDX-1)의 수치는 논문 자체 보고입니다. 제3자 검증을 거친 수치는 아니며, RLDX-1은 자사 벤치마크가 포함된 평가입니다.

PAMELA의 사용자 연구는 205명, 특정 시각 도메인입니다. 문화권 일반화는 논문 스스로 남긴 과제입니다.

모델형 보상의 근본 리스크는 이 글에서 다루지 않습니다. 심판 모델을 속이는 보상 해킹, 프록시 최적화는 별도 주제로 다뤄야 합니다.

## 적용 규칙

보상 설계 전에 검증기 목록부터 만드세요. <span style="background-color: #fff59d"><strong>컴파일러, 엔진, 시뮬레이터, 스키마 검증처럼 기계가 확정 판정을 내는 수단을 찾으면 그걸 1순위 보상으로 씁니다</strong></span>. RLHEV가 이 구성으로 UnitySceneBench 최고 점수를 냈습니다.

정답 확인이 되면 결과형으로 시작하세요. 단계 라벨 없이 최종 정답만으로 Maestro의 4B 정책이 학습됐고, KARL은 오프라인 RL로 Claude 4.6·GPT 5.2 대비 파레토 최적에 도달했습니다. 온라인 인프라 유무가 기술 선택의 기준입니다.

모델 채점을 쓸 때는 심판의 편향을 기록으로 남기세요. <span style="background-color: #fff59d"><strong>PAMELA는 이미지당 15명 평가 구성으로 개인 차를 데이터로 만들었습니다</strong></span>. 평균 점수만 쓰는 조직은 이 구성부터 바꿔야 합니다.

시뮬레이션에서 학습하고 실물에 올릴 때는 teacher 관측을 student가 받을 수 있는 입력으로 제한하세요. <span style="background-color: #fff59d"><strong>EgoPush에서 이 제약이 실물 무파인튜닝 이전을 좌우했습니다</strong></span>.

긴 과제는 나누고 루프를 막으세요. <span style="background-color: #fff59d"><strong>PokeRL은 단계별 보상에 다층 루프 페널티를 붙여 선행 연구의 붕괴 모드를 피했습니다</strong></span>.

## 참고 자료

1. [EgoPush (arXiv:2602.18071)](https://arxiv.org/abs/2602.18071) · [프로젝트 페이지](https://ai4ce.github.io/EgoPush/)
2. [RLDX-1 Technical Report (arXiv:2605.03269)](https://arxiv.org/abs/2605.03269) · [저장소](https://github.com/RLWRLD/RLDX-1)
3. [Maestro (arXiv:2605.22177)](https://arxiv.org/abs/2605.22177)
4. [PokeRL (arXiv:2604.10812)](https://arxiv.org/abs/2604.10812) · [저장소](https://github.com/reddheeraj/PokemonRL) · [PokemonRedExperiments](https://github.com/PWhiddy/PokemonRedExperiments)
5. [UniVR (arXiv:2607.12800)](https://arxiv.org/abs/2607.12800) · [프로젝트 페이지](https://maverickren.github.io/UniVR.github.io/)
6. [PAMELA (arXiv:2604.07427)](https://arxiv.org/abs/2604.07427)
7. [RLHEV (arXiv:2608.25518)](https://arxiv.org/abs/2608.25518)
8. [KARL (arXiv:2603.05218)](https://arxiv.org/abs/2603.05218)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
