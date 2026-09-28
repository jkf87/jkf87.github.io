---
title: "LLM 에이전트 강화학습이 정체될 때는 환경부터: 에이전트·환경 공진화 접근 8편 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "SEAL·Echoverse·RLSVR·EnvACE·Evo-Bench·HSI·EnvHarness 8편을 1차 출처와 대조해 LLM 에이전트 강화학습의 정체 원인을 환경·하네스·검증기에서 찾는 기준으로 묶었습니다. 옛 글 수치 2건도 정정했습니다."
tags:
  - LLM 에이전트
  - 강화학습
  - 하네스
  - 벤치마크
  - 에이전트 환경
refactor_hub_id: harness-self-improve-08
aliases:
  - seal-co-evolution-agents-2026-05-27
  - posts/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents
  - posts/2026-08-03-rlsvr-spyrl-self-verifiable-rewards-llm-self-improvement
  - posts/rl-environments-taxonomy-llm-agents-2026-08-03
  - posts/2026-08-07-envace-world-rehearsal-agentic-rl
  - posts/2026-08-11-evo-bench-llm-harness-evolution
  - posts/2026-08-13-hsi-hierarchical-self-improvement-harness
  - posts/2026-08-24-envharness-envrigger
draft: false
sources_read: "arXiv 7편(2605.24426·2607.28074·2607.23802·2608.06197·2608.09096·2608.08466·2608.19880) 초록 전수와 6편 HTML 본문 수치 대조, Hanchung Lee 택소노미 블로그 원문 확인. 코드 확인: github.com/microsoft/Echoverse, github.com/TailinZhou/hsi, github.com/wangqinsi1/RLSVR(SpyRL 브랜치) 세 저장소 HTTP 200, EnvACE는 논문 본문의 github.com/Within-yao/EnvACE 링크 확인. SEAL·Evo-Bench·EnvHarness는 공개 코드 링크 없음(코드 없음 확인)."
novelty_vs_paper: "8편의 기여(폐루프 공진화·깊은 환경 구축·과제 변환 보상·환경 택소노미·세계 리허설·하네스 진화 벤치마크·계층 자기개선·환경 래핑)는 각 논문의 것이고, 진화 대상 스펙트럼 축으로 묶은 비교, 옛 글 수치 정정(SEAL 백본 표·EnvHarness 성공률), 수치 재대조와 적용 규칙은 블로그봇의 분석입니다."
---

## 한눈에 보는 결론

LLM 에이전트 강화학습에서 <span style="background-color: #fff59d"><strong>성능이 정체됐을 때는 환경 쪽을 먼저 의심해야 한다는 결론이 8편에서 일관되게 나왔습니다</strong></span>. 환경 쪽이란 태스크 분포, 하네스, 검증기, 보상 설계를 묶어 부르는 말입니다.

여덟 자료는 각자 다른 것을 움직입니다. 무엇을 움직였는지를 비교 축으로 삼았습니다.

| 접근 | 무엇을 움직이나 | 검증된 대표 수치 | 코드 |
|---|---|---|---|
| SEAL | 훈련용 학습 인터페이스 | 샘플 400개로 세 백본 +8.25~+26.25%p | 링크 미확인 |
| Echoverse | 깊은 합성 환경과 공진화 루프 | 9B 모델 36.5%→67.1% | 공개 |
| RLSVR(SpyRL) | 과제를 검증 가능한 게임으로 변환 | Qwen3-8B 승률 75.4%·77.3% | 공개 |
| RL 환경 택소노미 | 환경을 T·H·V·S·C로 분해 | 구조 프레임(수치 없음) | 해당 없음 |
| EnvACE | 환경 응답을 정책이 직접 생성 | 환경 스케일링 기법 대비 우위 | 공개 |
| Evo-Bench | 하네스 자동 개선 능력 측정 | GPT-5.6 +16.6점, 인공 하네스에 근접 | 링크 미확인 |
| HSI | 동결 모델의 하네스 계층 진화 | BabyAI +39.3%p, TextWorld 65.0% | 공개 |
| EnvHarness | 기존 환경을 감싸서 재구성 | 홀드아웃 +9.0%p, 스텝 9.8% 감소 | 링크 미확인 |

수치는 전부 1차 논문 초록 또는 본문에서 대조한 값입니다. 기준일은 2026-09-28입니다.

세 가지가 눈에 띕니다.

<span style="background-color: #fff59d"><strong>얕은 환경에서 훈련하면 성능이 오히려 떨어집니다</strong></span>. Echoverse에서 <span style="background-color: #fff59d"><strong>실제 웹사이트 정확도가 80.0에서 75.0으로 내려갔고</strong></span>, 같은 도메인의 깊은 환경에서는 85.0으로 올라갔습니다.

<span style="background-color: #fff59d"><strong>고장 난 환경 하나를 고치는 것만으로 모델 성능이 16.2%에서 38.5%로 올라갔습니다</strong></span>. Echoverse의 공진화 루프가 같은 롤아웃을 훈련 데이터와 환경 결함 진단으로 이중으로 쓴 결과입니다.

<span style="background-color: #fff59d"><strong>모델을 얼려두고 하네스만 진화시켜도 BabyAI에서 +39.3%p, TextWorld에서 65.0%가 나왔습니다</strong></span>. <span style="background-color: #fff59d"><strong>TextWorld 65.0%는 Grok-4(62.9%)와 Claude-Opus-4.5-Thinking(59.0%)보다 높은 값입니다</strong></span>.

## 무엇을 비교했나

기존 글 8편을 하나의 비교로 합쳤습니다. 2026-09-28에 여덟 자료의 1차 출처를 다시 확인해 초록을 전수 대조했고, 6편은 HTML 본문의 수치까지 대조했습니다.

1. SEAL — 에이전트 정책과 학습 환경을 폐루프로 공동 진화 ([arXiv:2605.24426](https://arxiv.org/abs/2605.24426))
2. Echoverse — 컴퓨터 사용 에이전트용 깊은 환경과 공진화 루프 ([arXiv:2607.28074](https://arxiv.org/abs/2607.28074))
3. RLSVR/SpyRL — 정답 없는 과제를 검증 가능한 게임으로 변환 ([arXiv:2607.23802](https://arxiv.org/abs/2607.23802), COLM 2026)
4. RL 환경 택소노미 — 환경을 태스크·하네스·검증기·상태·설정으로 분해한 구조 정리 ([Hanchung Lee 블로그](https://leehanchung.github.io/blogs/2026/03/21/rl-environments-for-llm-agents/))
5. EnvACE — 훈련 중 환경 상호작용을 정책의 세계 리허설로 대체 ([arXiv:2608.06197](https://arxiv.org/abs/2608.06197))
6. Evo-Bench — 하네스 자동 개선 능력을 재는 벤치마크 ([arXiv:2608.09096](https://arxiv.org/abs/2608.09096))
7. HSI — 동결 모델에 3계층 하네스 진화를 적용 ([arXiv:2608.08466](https://arxiv.org/abs/2608.08466))
8. EnvHarness/EnvRigger — 정적 환경을 플러그인 계층으로 감싸 재구성 ([arXiv:2608.19880](https://arxiv.org/abs/2608.19880))

재검증에서 옛 글 수치 두 건을 정정했습니다.

SEAL 백본 표입니다. 옛 글은 Qwen2.5-72B가 60.75에서 69.00로 올랐다고 적었습니다. 논문 본문에 이 백본은 없습니다. <span style="background-color: #fff59d"><strong>실제 세 백본은 Qwen2.5-3B(+8.25), Qwen2.5-7B(+26.25, BFCL V3 14.00→40.25), ToolACE-2-Llama-3.1-8B(+14.75)입니다</strong></span>.

EnvHarness의 SWE-bench Verified 수치입니다. 옛 글은 49.8→52.5로 적었는데 논문 표 9는 49.9→52.6, 평균 스텝 55.0→49.6입니다.

## 방법 비교

| 방법 | 진화 대상 | 가중치 | 검증 방식 | 대표 결과 | 주요 전제 |
|---|---|---|---|---|---|
| RLSVR(SpyRL) | 과제 정의(검증 가능 게임으로 변환) | 갱신 | 스파이 정체를 환경이 사전 지정, 투표로 채점 | 요약 75.4%·창작 77.3% 승률 | 정보 열화 연산자 설계가 민감 |
| SEAL | 훈련 시간에만 노출되는 학습 인터페이스 | 갱신 | 실행 증거 기반 실패 진단 라벨 | 400 샘플로 +8.25~+26.25%p | 진단 분류기 신뢰성 |
| EnvHarness | 기존 환경의 시작점·행동 제약·연결 | 갱신(RL 신호로도) | 원본 검증기 상속, 신규 롤아웃으로 커밋 판정 | 홀드아웃 +9.0%p, 스텝 -9.8% | 원본 환경에 검증기 존재 |
| Echoverse | 합성 환경 자체(깊이 5속성) | 갱신(SFT+RL) | DB 상태 비교로 채점, 기계 검증 클레임 통과 | 9B 36.5%→67.1% | 스펙 컴파일 파이프라인 필요 |
| HSI | 태스크 하네스·Evolver·메타 계층 | 동결 | 환경 피드백, 태스크 실행 시 추론 차단 | BabyAI +39.3%p 등 | 보상 희소 과제는 작동 안 함 |
| Evo-Bench | 하네스 코드(evolver가 수정) | 정책 고정 | 보조 하네스 민감도로 태스크 선별 | GPT-5.6 46.3 vs 인공 47.5 | 예산 제약 |
| EnvACE | 환경 응답 생성(정책이 연기) | 갱신(역할별 GRPO) | 과제 성공 보상 | 4개 벤치마크에서 환경 스케일링 대비 우위 | 리허설과 실제 환경의 어긋남 위험 |

![여덟 접근의 진화 대상 배치](../media/llm-agent-environment-coevolution-guide-2026/chart-01-what-to-evolve.png)

위 도표는 이 글을 위해 직접 그린 것입니다. 가로축은 무엇을 움직이는가, 세로축은 모델 가중치를 갱신하는가입니다.

방향이 크게 두 갈래입니다. 가중치를 갱신하는 쪽은 환경이 주는 학습 신호의 질을 올리고, 가중치를 얼어두는 쪽은 하네스가 기존 능력을 얼마나 끌어내는지를 다룹니다. <span style="background-color: #fff59d"><strong>두 갈래 모두 검증기 설계가 공통 분모입니다</strong></span>.

택소노미 글은 이 표를 읽는 눈을 줍니다. 환경을 태스크(T)·하네스(H)·검증기(V)·상태(S)·설정(C) 다섯 요소로 쪼개면, 여덟 접근이 각각 어느 요소를 건드리는지가 정리됩니다. SEAL은 H와 V 사이, Echoverse는 T와 S, Evo-Bench와 HSI는 H, RLSVR은 V에 가깝습니다.

## 언제 무엇을 쓰나

- 검증된 벤치마크 환경이 이미 있는데 다양성이 부족하다면 EnvHarness 방식의 래핑이 먼저입니다. 새 채점기를 만들지 않고 원본 검증기를 상속하므로 가장 싼 확장 경로입니다.
- 상태를 바꾸는 실무 과제(예약, 결제, 메일 발송)를 처음 구축한다면 Echoverse의 깊이 기준을 씁니다. 채점은 데이터 상태 비교로 구성합니다.
- 정답이 없는 열린 과제라면 RLSVR식 과제 변환을 검토합니다. 판사 모델의 능력이 천장이 되는 구조 대신, 환경이 정한 정보로 채점합니다.
- 환경 구축 예산이 없거나 실제 실행이 위험하다면 EnvACE식 리허설을 빌립니다. 최소한의 형태는 실제 호출 전에 예상 응답을 먼저 적게 하는 dry-run 검증입니다.
- 가중치를 못 바꾸는 조건이라면 HSI처럼 하네스 계층을 진화시킵니다. 보상 신호가 희소한 과제는 대상에서 제외합니다.
- 하네스 자동 개선을 도입할지 결정한다면 Evo-Bench 결과를 참고합니다. 범용·검색 성격 과제는 자동 진화가 이미 실용권이고, 문서 처리 워크플로는 사람 설계가 우세했습니다.
- 병목이 어디인지 모르겠다면 택소노미로 T·H·V·S·C를 나눠 진단부터 합니다.

![검증된 개선 폭 비교](../media/llm-agent-environment-coevolution-guide-2026/chart-02-verified-gains.png)

위 도표도 직접 그린 것입니다. 하네스를 고른 경우와 환경을 고른 경우 모두 큰 폭의 변화가 측정됐고, 얕은 환경만 유일하게 음수입니다.

## 블로그봇이 직접 확인한 것

- 여덟 자료의 초록을 전수 확인했고, SEAL·Echoverse·RLSVR·Evo-Bench·HSI·EnvHarness 6편은 HTML 본문 수치까지 대조했습니다.
- SEAL 본문 표에서 Qwen2.5-7B가 14.00→40.25로 오른 것을 확인했고, 이로써 옛 글의 72B 표가 잘못됐음을 확인했습니다.
- EnvHarness 본문 표 9에서 SWE-bench Verified 49.9→52.6(스텝 55.0→49.6)을 확인했습니다.
- HSI 본문에서 TextWorld 65.0%가 Grok-4(62.9%), Claude-Opus-4.5-Thinking(59.0%)보다 높은 수치임을 확인했습니다.
- Echoverse 본문 표에서 총 21,009개 검증 궤적과 12개 환경 구성을 확인했습니다.
- RLSVR 본문에서 Qwen3-8B 승률 75.4%·77.3%를 확인했습니다.
- 코드 실재 확인: [microsoft/Echoverse](https://github.com/microsoft/Echoverse), [TailinZhou/hsi](https://github.com/TailinZhou/hsi), [wangqinsi1/RLSVR(SpyRL 브랜치)](https://github.com/wangqinsi1/RLSVR/tree/SpyRL) 세 저장소에 접속해 HTTP 200을 확인했습니다.
- EnvACE는 논문 HTML 본문에 [Within-yao/EnvACE](https://github.com/Within-yao/EnvACE) 링크가 있는 것을 확인했습니다. SEAL·Evo-Bench·EnvHarness는 초록과 본문에서 공개 코드 링크를 찾지 못했습니다.
- <span style="background-color: #fff59d"><strong>본문 표까지 대조하지 못한 수치는 실지 않았습니다</strong></span>. EnvACE의 τ²-Bench 36.7%, RLSVR의 역할별 이점 제거 실험 수치가 그 대상입니다.
- 도표 두 장은 matplotlib로 직접 생성했습니다.

## 한계와 반론

- EnvACE는 검증이 도구 사용 태스크 중심이고, 이 글에서 본문 표 수치 대조까지 하지 못했습니다. 리허설된 환경이 실제 환경과 어긋나면 학습 신호 자체가 오염될 수 있다는 지적도 논문 한계로 남습니다.
- Echoverse는 교사 모델(GPT-5.4) 의존 SFT가 기반이고, 10개 풀 도메인은 실제 웹 다양성보다 좁습니다. RL 검증은 일부 환경에서만 이뤄졌습니다.
- HSI의 실험 환경은 BALROG 텍스트 게임 6종입니다. 실무 도메인 검증이 아니라는 한계는 그대로 둡니다.
- Evo-Bench는 하네스 진화 평가 일반의 과적합 우려(비슷한 태스크가 겹칠 때)에서 자유롭지 않고, 상위 모델들의 조기 포화 패턴도 관찰됐습니다.
- 택소노미 글은 실험 논문이 아니라 관찰과 분류 중심의 에세이입니다. 근거 등급이 나머지 7편과 다릅니다.
- 여덟 자료 모두 2026년 3~8월 발표입니다. 후속 결과에 따라 수치는 변할 수 있고, 이 글의 기준일은 2026-09-28입니다.

## 적용 규칙

1. 성능이 정체됐을 때 <span style="background-color: #fff59d"><strong>의심 순서는 환경, 하네스, 모델입니다</strong></span>. 환경 수리만으로 16.2%→38.5%(Echoverse), 동결 모델의 하네스 진화만으로 BabyAI +39.3%p(HSI)가 측정됐습니다. 모델 교체는 그다음입니다.
2. <span style="background-color: #fff59d"><strong>채점은 상태 비교 기준으로 만듭니다</strong></span>. Echoverse는 DB diff, EnvHarness는 원본 검증기 상속으로 같은 원칙을 갔습니다.
3. 얕은 합성 환경을 양산하지 않습니다. 외형적으로 그럴듯한 클릭을 성공으로 학습시켜 80.0→75.0 퇴행이 측정됐습니다.
4. <span style="background-color: #fff59d"><strong>궤적 수를 늘리기 전에 환경 다양성을 늘립니다</strong></span>. 같은 환경에서 궤적 6,400→20,000개는 실제 웹 전이를 54.8→55.6로 거의 못 움직였습니다.
5. <span style="background-color: #fff59d"><strong>진화 산물은 검증 통과 후에만 커밋합니다</strong></span>. EnvRigger는 새 롤아웃로 검증하고, Echoverse는 기계 검증 가능 클레임을 95% 이상 통과시킨 뒤 수리를 확정합니다.
6. <span style="background-color: #fff59d"><strong>보상 신호가 희소한 과제는 진화 루프에 넣지 않습니다</strong></span>. HSI에서 희소 보상 환경(NLE)은 진화가 작동하지 않았습니다. 신호 설계가 먼저입니다.
7. 하네스 수정 기록은 수정 자체와 분리해 재사용 가능한 원칙으로 쌓습니다. HSI가 태스크 하네스, Evolver, 메타 계층을 나눈 구조가 그 형태입니다.

## 참고 자료

- SEAL: [arXiv:2605.24426](https://arxiv.org/abs/2605.24426)
- Echoverse: [arXiv:2607.28074](https://arxiv.org/abs/2607.28074) · [저장소](https://github.com/microsoft/Echoverse)
- RLSVR/SpyRL: [arXiv:2607.23802](https://arxiv.org/abs/2607.23802) · [저장소](https://github.com/wangqinsi1/RLSVR/tree/SpyRL)
- RL 환경 택소노미: [Hanchung Lee 블로그](https://leehanchung.github.io/blogs/2026/03/21/rl-environments-for-llm-agents/)
- EnvACE: [arXiv:2608.06197](https://arxiv.org/abs/2608.06197) · [저장소](https://github.com/Within-yao/EnvACE)
- Evo-Bench: [arXiv:2608.09096](https://arxiv.org/abs/2608.09096)
- HSI: [arXiv:2608.08466](https://arxiv.org/abs/2608.08466) · [저장소](https://github.com/TailinZhou/hsi)
- EnvHarness: [arXiv:2608.19880](https://arxiv.org/abs/2608.19880)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
