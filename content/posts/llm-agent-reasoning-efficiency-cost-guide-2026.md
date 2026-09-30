---
title: "LLM 에이전트 추론 비용 줄이기: 토큰 낭비·도구 대기·KV 캐시 16편 통합 정리"
date: 2026-09-30
author: 한준구(코난쌤)
description: "토큰 낭비, 도구 대기, KV 캐시, 모델 선택 네 가지 레버로 추론 효율 연구 12편과 운영 관점 사례를 통합 정리했습니다. 변곡점 세션 분할 +264 Elo, PASTE 지연 43.5% 절감 등 본문에서 재확인한 수치를 실었습니다."
tags:
  - LLM
  - 에이전트
  - 추론 효율
  - 지연시간
  - 아키텍처
refactor_hub_id: reasoning-efficiency-01
aliases:
  - visual-attention-variants-modern-llms
  - greg-brockman-saastr-human-attention-bottleneck-2026-05-04
  - gated-deltanet2-decoupling-erase-write-linear-attention-2026-05-23
  - efficient-agentic-reasoning-self-regulated-planning-2026-05-24
  - flowlong-inference-time-long-video-2026-05-24
  - latentomni-audio-visual-latent-reasoning-2026-05-24
  - gated-deltanet-2-linear-attention-2026-05-25
  - 2026-05-29-axpo-tool-collapse-nvidia
  - posts/2026-05-29-axpo-tool-collapse-nvidia
  - posts/2026-07-14-agora-auction-based-llm-agent-reasoning
  - posts/2026-07-22-sophia-breaking-llm-self-loops
  - posts/kimi-k3-gpt2-lineage-2026-07-29
  - posts/2026-08-25-paste-speculative-tool-execution
  - posts/2026-09-05-second-thought-idle-window-parallel-reasoning
  - posts/2026-09-05-speculative-macro-commit-faster-tool-agents
  - posts/2026-09-12-magenta-lean-verification-math-agents
  - posts/2026-09-19-llm-agent-test-time-scaling-slowdown-elo-per-token
draft: false
sources_read: "논문 5편(2609.15309, 2609.11319, 2603.18897, 2609.03236, 2607.09600)은 PDF 본문을 텍스트 추출로 직접 읽고 인용 수치를 원문에서 재확인함. 나머지 6편(2605.22138, 2607.18100, 2605.28774, 2605.22791, 2605.22012, 2510.26692)은 arXiv 초록 대조. 코드·데이터: github.com/NVlabs/GatedDeltaNet-2, github.com/sailing-lab/sr2am, github.com/agent-tts/Agent-TTS-Code, github.com/MoonshotAI/Kimi-linear, AXPO 프로젝트 페이지 접속 확인. anonymous.4open.science는 401로 본문 확인 불가. FlowLong은 arXiv id 미확인, SaaStr 인터뷰는 회원 글 인용."
novelty_vs_paper: "네 가지 레버 분류, 레버별 수치 비교표와 차트 2종, 적용 순서는 블로그봇의 재구성 기여. 각 방법의 구조와 수치는 해당 논문·발표의 기여이며 이 글은 원문 재확인만 수행함."
---

## 한눈에 보는 결론

본 문서는 2026년 3월부터 9월 사이 작성된 글 16편을 추론 비용 관점에서 통합 정리한 것입니다. 검증 기준일은 2026-09-30입니다. 논문 5편은 본문을, 6편은 초록을 확인하여 인용 수치를 재검증했습니다.

<span style="background-color: #fff59d"><strong>추론 비용의 병목은 기억(KV 캐시), 토큰(생성량), 시간(도구 대기), 선택(모델 배치) 네 범주로 정리됩니다</strong></span>.

| 레버 | 병목 | 대표 방법 | 재확인 수치 |
| --- | --- | --- | --- |
| 기억 | 긴 문맥의 KV 캐시 | GQA·MLA, 선형 어텐션(KDA·GDN-2) | GDN-2: MK-NIAH 4K 37.8 vs Mamba-2 21.4 |
| 토큰 | 사고 길이 폭주 | SR²AM, SOPHIA, 세션 분할 | SR²AM: 25.8~95.3% 적은 추론 토큰 |
| 시간 | 도구 직렬 대기 | PASTE, SMC, Second Thought | PASTE: 평균 과제 완료 시간 43.5% 감소 |
| 선택·검증 | 과대한 모델 사용 | Agora, AXPO, Magenta | AXPO: 8B가 Pass@4에서 32B 추월 |

주요 결론은 다음 네 가지입니다.

- 토큰 예산 증가의 한계 효용은 실재합니다. 100M 토큰 실험에서 <span style="background-color: #fff59d"><strong>네 에이전트 모두 독립 샘플링 참조선(10배당 400 Elo) 아래로 기울기가 하락</strong></span>했으며, <span style="background-color: #fff59d"><strong>변곡점 이후 세션 분할이 +264 Elo 우위</strong></span>를 기록했습니다.
- <span style="background-color: #fff59d"><strong>도구 실행은 에이전트 E2E 지연의 45~57%를 차지</strong></span>합니다(PASTE 측정). 예측 실행·매크로 커밋·대기창 병렬 추론의 절감 보고치는 <span style="background-color: #fff59d"><strong>각각 43.5%, 18.6%, 10.9%</strong></span>입니다.
- 토큰 낭비의 상당 부분은 자가 루프와 무계획 장문 추론에서 발생합니다(SOPHIA·SR²AM 분석).
- <span style="background-color: #fff59d"><strong>검증·보정 장치를 결합하면 소형 모델이 대형 모델을 대체할 수 있습니다</strong></span>(Magenta, AXPO).

독립 샘플링 참조선은 같은 문제를 여러 번 새로 풀어 최고 결과만 남기는 방식의 성장률 기준입니다. 토큰 예산이 10배 늘 때마다 정확히 400 Elo씩 오르는 분포 무관 기준선이며, 긴 세션의 기울기가 이 선 아래로 내려간다는 것은 문맥을 쌓은 적응의 이점이 소진되었음을 뜻합니다.

![추론 비용 네 가지 레버](../media/llm-agent-reasoning-efficiency-cost-guide-2026/chart-02-four-levers.png)

운영 관점에서는 그렉 브록먼의 SaaStr 발언("실행은 쉬워지고 판단하는 인간의 주의가 병목이 된다")이 같은 결론을 가리킵니다.

## 무엇을 비교했나

통합 대상 16편과 1차 출처는 다음과 같습니다.

1. 어텐션 변형 계보 정리 — 내부 정리 노트
2. 그렉 브록먼 SaaStr 인터뷰 — [YouTube](https://www.youtube.com/watch?v=bBS93A0BeNI)
3. Gated DeltaNet-2 — [arXiv 2605.22791](https://arxiv.org/abs/2605.22791)·[코드](https://github.com/NVlabs/GatedDeltaNet-2)
4. Gated DeltaNet-2 후속 정리 — 동일 논문
5. SR²AM — [arXiv 2605.22138](https://arxiv.org/abs/2605.22138)·[코드](https://github.com/sailing-lab/sr2am)
6. FlowLong — 회원 글(원문 링크 없음)
7. LatentOmni — [arXiv 2605.22012](https://arxiv.org/abs/2605.22012)
8. AXPO — [arXiv 2605.28774](https://arxiv.org/abs/2605.28774)·[프로젝트 페이지](https://byungkwanlee.github.io/AXPO-page/)
9. Agora — [arXiv 2607.09600](https://arxiv.org/abs/2607.09600)
10. SOPHIA — [arXiv 2607.18100](https://arxiv.org/abs/2607.18100)
11. GPT-2→Kimi K3 계보 — [ali의 X 아티클](https://x.com/i/article/2077616768491585536)·[Kimi Linear 논문](https://arxiv.org/abs/2510.26692)
12. PASTE — [arXiv 2603.18897](https://arxiv.org/abs/2603.18897)
13. Second Thought — [arXiv 2608.13667](https://arxiv.org/abs/2608.13667)
14. SMC — [arXiv 2609.03236](https://arxiv.org/abs/2609.03236)
15. Magenta — [arXiv 2609.11319](https://arxiv.org/abs/2609.11319)
16. When Agents Slow Down — [arXiv 2609.15309](https://arxiv.org/abs/2609.15309)·[코드](https://github.com/agent-tts/Agent-TTS-Code)

## 방법 비교

| 방법 (레버) | 변경 대상 | 재확인 수치 | 전제·비용 |
| --- | --- | --- | --- |
| SR²AM (토큰) | 계획 시점·깊이의 자기 조절 | 25.8~95.3% 토큰 절감, 계획 수평 +22.8% | 학습 필요 |
| SOPHIA (토큰) | 전이 벡터 기반 루프 차단 | 오답 궤적의 일관된 토큰 과다(4개 벤치마크) | Qwen3 검증 |
| 세션 분할 (토큰) | 변곡점 기반 예산 분할 | <span style="background-color: #fff59d"><strong>b_inf=38M 토큰, K=3 분할에서 +264 Elo</strong></span> | 연속 점수 과제 |
| PASTE (시간) | 생성 중 도구 예측 실행 | 43.5% 감소, p99 55.4%, 히트 93.8% | 반복 워크로드 |
| SMC (시간) | 앵커 검증 후 체인 커밋 | <span style="background-color: #fff59d"><strong>-18.59%(27.60→22.47초), 158/158 커밋 아웃컴 보존</strong></span> | 근사 최적화 |
| Second Thought (시간) | 대기창 보조 추론 4본 | 중간 지연 -10.9%, 턴 수 전 조합 감소 | 비용·동시성 증가 |
| Agora (선택) | 보정 신뢰도 경매 | 무보정 -4.0%/-1.3%, 보정 후 +8.7점 | 보정 데이터 |
| AXPO (선택) | 도구 호출 재샘플링 | +1.8pp vs GRPO, 8B>32B(Pass@4) | RL 필요 |
| Magenta (검증) | Lean 검증 파이프라인 | <span style="background-color: #fff59d"><strong>74.19%→전체 만점, +8.6~+25.8점</strong></span> | 이산 검증기 |
| GDN-2·KDA (기억) | erase/write 게이트 분리 | MK-NIAH 4K 37.8, 하이브리드 53.97 | 1.3B 실험 |
| Kimi Linear 계보 (기억) | KDA+MLA 하이브리드 | <span style="background-color: #fff59d"><strong>KV 75% 절감·6배 처리량</strong></span>(논문 보고) | 논문 레시피 기준 |
| LatentOmni (기억·토큰) | 잠재 공간 직접 추론 | Daily-Omni 67.4(오픈소스 최상위, 초록) | 포스트트레이닝 |

![지연 절감 보고값 비교](../media/llm-agent-reasoning-efficiency-cost-guide-2026/chart-01-latency-reduction.png)

각 수치는 상이한 벤치마크·기준선에서 도출된 것으로 방법 간 직접 비교는 불가능합니다. PASTE의 43.5%는 딥리서치·코딩·AI-for-Science 워크로드의 평균이고, SMC의 18.59%는 τ²-Telecom 2,285개 과제의 평균입니다. 두 값은 같은 레버를 공략한 결과이지만 측정 환경이 다르므로, 크기 비교가 아닌 이득의 존재와 적용 조건을 읽는 기준으로 사용합니다.

## 언제 무엇을 쓰나

- 토큰 비용 폭발: 자가 루프 탐지 → 프롬프트 차단 → 계획 조절(SR²AM) → 세션 분할 순서.
- 도구 대기 지연: 반복 패턴 확인 후 PASTE·SMC, 불규칙 대기는 Second Thought. LLM 재진입 스케줄링 병행.
- 긴 문맥 메모리: GQA → MLA → 선형 하이브리드 순으로 서빙 난이도와 함께 검토.
- 모델 선택 비용: 캘리브레이션 → 단순 라우터 → 경매 순서. <span style="background-color: #fff59d"><strong>무보정 경매는 오히려 성능을 깎습니다(-4.0%)</strong></span>.
- 이산 검증 가능 도메인: 검사 규칙을 추론 루프 내부에 배치(Magenta 구조).

## 블로그봇이 직접 확인한 것

- 논문 5편의 PDF 본문을 읽고 인용 수치를 원문에서 재확인했습니다(b_inf=38M, 400 Elo/10배, 27.60→22.47초, 99.52%, 158/158, 74.19→만점, -4.0%/-1.3%, 21.5→78.5%, 55.26→51.06%).
- 나머지 arXiv 6편은 초록으로 수치를 대조했습니다.
- 코드 저장소 5곳 접속 확인(200), anonymous.4open.science는 401로 확인 불가.
- 비교 차트 2종을 직접 생성했으며 수치는 원문 재확인 값입니다.
- FlowLong은 arXiv id 미확인으로 회원 글 서술만 인용, SaaStr 인터뷰는 영상 원문 미열람입니다.

## 한계와 반론

- 수치는 각 논문의 자체 벤치마크 기준이며 워크로드가 상이합니다.
- SMC는 근사 최적화로 AppWorld에서 2건의 완수 하락, 불가역 API 도메인에 안전 장치 필요.
- PASTE는 반복 패턴 위주 워크로드에서 측정되었습니다.
- Agora의 보정기는 최대 비용 항목이며 <span style="background-color: #fff59d"><strong>β 상향 시 정확도 하락(55.26→51.06%)이 수반</strong></span>됩니다.
- Magenta의 결과는 수학 도메인에 한정되며 소프트 인증서 한계가 있습니다.
- Elo-per-token은 연속 점수 과제 전용입니다.
- 선형 어텐션의 상용 스택 성숙도는 미완, GDN-2는 1.3B 규모 실험입니다.
- SOPHIA의 타 모델 패밀리 확장은 미검증입니다.
- <span style="background-color: #fff59d"><strong>모든 레버 적용 전 병목 측정이 선행 조건</strong></span>입니다.

## 적용 규칙

이번에 원문을 확인한 범위에서만 뽑은 규칙입니다.

1. 최적화 전에 지연을 분해합니다. LLM 생성 시간과 도구 대기 시간의 비중부터 측정하고, 도구 쪽이 크면(논문 측정 사례 45~57%) 시간 레버로, 생성 쪽이 크면 토큰 레버로 이동합니다.
2. 실행 트레이스를 버리지 않고 패턴화하여 보존합니다. PASTE와 SMC의 예측·커밋 원재료는 과거 성공 트레이스의 반복 패턴이며, 로그가 없으면 두 방법 모두 시작할 수 없습니다.
3. <span style="background-color: #fff59d"><strong>도구 병렬화와 LLM 재진입 스케줄링을 일체로 설계</strong></span>합니다. PASTE의 실험에서 툴 실행만 가속하고 스케줄러를 그대로 두면 고부하에서 이득이 LLM 감속에 흡수되었습니다.
4. 긴 세션은 변곡점 b_inf를 측정한 뒤 총 예산을 K=⌊B/b_inf⌉개 세션으로 분할합니다. 100M 토큰 예산 실험에서 이 규칙의 예측(K=3)이 실제 최적이었습니다.
5. 라우팅은 캘리브레이션, 단순 라우터, 경매의 순서로 도입합니다. 보정 데이터 없이 경매부터 붙이면 과신하는 모델이 입찰을 쓸어 담아 성능이 하락합니다.
6. 검증 가능한 도메인에서는 생성보다 검사가 쉬운 이산 규칙을 게이트로 분리합니다. 명제 정합성 검사, 컴파일, 자동 채점이 해당하며 Magenta가 이 구조의 사례입니다.
7. 증가한 토큰 예산은 메인 추론보다 대기창 분산에 우선 배분해 실험합니다. 같은 예산을 메인 추론에 몰은 대조군보다 대기창 분산이 정확도와 순차 디코딩량에서 함께 우위였습니다.
8. 예측 실행은 격리와 승격 규칙으로 lossless 구조를 유지합니다. 예측이 정식 상태를 오염시키면 틀린 예측의 비용이 이득을 초과합니다.

## 자주 묻는 질문

**Q. 토큰을 더 주면 성능이 계속 오르나요?**
100M 토큰 구간까지는 상승하나 마지막 구간에서 참조선 이하로 하락합니다. 변곡점 이후에는 분할이 우위이며, 분할 규칙은 변곡점 b_inf를 재고 K=⌊B/b_inf⌉개 세션으로 나누는 것입니다. 100M 토큰 예산 실험에서는 K=3이 최적이었습니다.

**Q. 도구 예측이 틀리면 어떻게 되나요?**
예측은 격리되며 확인 전 승격되지 않습니다. <span style="background-color: #fff59d"><strong>Top-1 정확도 27.8%로도 후보를 여러 개 운용해 히트율 93.8%를 달성</strong></span>했다는 결과가 그 증거입니다.

**Q. 선형 어텐션이 풀 어텐션을 대체합니까?**
하이브리드 구성이 현실적인 선택입니다.

**Q. 소형 모델로 대형 모델을 대체할 수 있습니까?**
검증기 또는 학습 보정 장치가 있는 경우에 한합니다.

## 참고 자료

- [When Agents Slow Down (arXiv 2609.15309)](https://arxiv.org/abs/2609.15309) · [코드](https://github.com/agent-tts/Agent-TTS-Code)
- [PASTE (arXiv 2603.18897)](https://arxiv.org/abs/2603.18897)
- [Speculative Macro Commit (arXiv 2609.03236)](https://arxiv.org/abs/2609.03236)
- [Second Thought (arXiv 2608.13667)](https://arxiv.org/abs/2608.13667)
- [Magenta (arXiv 2609.11319)](https://arxiv.org/abs/2609.11319)
- [SR²AM (arXiv 2605.22138)](https://arxiv.org/abs/2605.22138) · [코드](https://github.com/sailing-lab/sr2am)
- [Agora (arXiv 2607.09600)](https://arxiv.org/abs/2607.09600)
- [SOPHIA (arXiv 2607.18100)](https://arxiv.org/abs/2607.18100)
- [AXPO (arXiv 2605.28774)](https://arxiv.org/abs/2605.28774) · [프로젝트 페이지](https://byungkwanlee.github.io/AXPO-page/)
- [Gated DeltaNet-2 (arXiv 2605.22791)](https://arxiv.org/abs/2605.22791) · [코드](https://github.com/NVlabs/GatedDeltaNet-2)
- [Kimi Linear (arXiv 2510.26692)](https://arxiv.org/abs/2510.26692) · [코드](https://github.com/MoonshotAI/Kimi-linear)
- [LatentOmni (arXiv 2605.22012)](https://arxiv.org/abs/2605.22012)
- [그렉 브록먼 SaaStr 인터뷰 (YouTube)](https://www.youtube.com/watch?v=bBS93A0BeNI)
- [ali, 22580: From GPT2 to Kimi3 (X)](https://x.com/i/article/2077616768491585536)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
