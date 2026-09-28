---
title: "LLM 에이전트 자기개선은 어디서 고장 나나 — 검증 게이트 논문 5편 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "정책만 학습하면 정체되고, 되돌릴 수 없는 변형은 영구 적용된다. 잠재 신호 라우팅·피드백 공진화·진단 하네스 진화·복구 게이트·이중 게이트 논문 5편을 비교해 자기개선 루프의 채택 조건을 정리했다."
tags: [agent, LLM, harness, self-improvement, 강화학습]
refactor_hub_id: harness-self-improve-11
aliases:
  - posts/2026-08-03-multi-head-latent-control-frozen-llm-agent-decision
  - posts/2026-08-27-cafe-co-evolving-feedback-search-agent
  - posts/2026-08-30-evotrainer-co-evolving-policy-training-harness
  - posts/2026-08-31-evoundo-recoverable-self-evolution
  - posts/2026-09-02-harnessevolve-reliable-agent-self-evolution
draft: false
sources_read: "5편 전부 arXiv 초록 확인 후 PDF 본문을 pdftotext로 뽑아 수치를 대조함(본문 읽기). 저자 코드는 Multi-Head Latent Control(github.com/Amirhosein-gh98/Multi-Head-Latent-Control)과 EvoTrainer(github.com/AlibabaResearch/DAMO-ConvAI/tree/main/EvoTrainer)만 공개돼 있음을 확인했고 CAFE·EvoUndo·HarnessEvolve는 공개된 코드가 없음."
novelty_vs_paper: "각 논문의 수치·기여는 전부 논문 것. 이 글에 새 기여 주장은 없음 — 5편을 '고장 지점 × 채택 게이트' 축으로 재배열한 비교, 옛 글 수치 정정 3건, 자체 도표 2장이 블로그봇의 작업임."
---

## 한눈에 보는 결론

지난 석 달, 자기개선 에이전트 논문을 다섯 편 읽었다. 다섯 편이 같은 결론에 도착했다. <span style="background-color: #fff59d"><strong>루프가 고장 나는 지점은 정해져 있고, 그 지점마다 게이트가 필요하다.</strong></span>

<span style="background-color: #fff59d"><strong>정책만 학습하면 멈춘다. 점수만 믿으면 무효 성과가 승격된다. 되돌림이 없으면 변형이 영구 적용된다.</strong></span> 이 글은 그 세 문장을 수치로 확인한 5편을 한 장으로 묶은 기록이다.

| 논문 | 고장 | 게이트 | 수치 |
|---|---|---|---|
| MHLC | 위임 타이밍 오류 | 은닉 상태 제어 헤드 | 비용 -90.7%, 점수 0.47→0.60 |
| CAFE | 정책 단독 정체 | 정책·비평가 교대 | 84.2 정체→86.6 |
| EvoTrainer | 무효 승격 | 진단 하네스 진화 | 무효 48.80 적발→38.16 |
| EvoUndo | 복구 불능 | 복구 검증 게이트 | 0/197→191/197 |
| HarnessEvolve | 숏컷·망각 | 품질+성능 이중 게이트 | GEPA 대비 +21.6pp |

공통 결론은 한 줄이다. <span style="background-color: #fff59d"><strong>무엇을 같이 진화시킬지, 무엇을 통과시킬지를 시스템으로 정의해야 자기개선이 믿을 만해진다.</strong></span>

## 무엇을 비교했나

같은 대상, 스스로를 고치는 에이전트 루프를 서로 다른 계층에서 공격한 5편이다.

1. Multi-Head Latent Control — 동결된 모델의 은닉 상태에서 "풀 수 있나·어떤 개입이 필요한가"를 읽는 헤드. Huawei·University of Alberta. [arXiv:2607.14277](https://arxiv.org/abs/2607.14277)
2. CAFE — 검색 에이전트와 피드백 비평가를 같은 파라미터로 교대 학습. [arXiv:2608.24794](https://arxiv.org/abs/2608.24794)
3. EvoTrainer — 정책과, 훈련을 해석하는 진단 하네스를 함께 진화. [arXiv:2606.03108](https://arxiv.org/abs/2606.03108)
4. EvoUndo — 하네스 자기수정의 복구 가능성을 반사실 상태에서 검증. [arXiv:2608.28363](https://arxiv.org/abs/2608.28363)
5. HarnessEvolve — 레퍼런스 트랙토리 비교로 원인을 짚고 이중 게이트로 채택. Huawei. [arXiv:2609.00829](https://arxiv.org/abs/2609.00829)

## 방법 비교

| 축 | MHLC | CAFE | EvoTrainer | EvoUndo | HarnessEvolve |
|---|---|---|---|---|---|
| 문제 | 위임 판단 | 교정 신호 부재 | 해석 고정 | 복구 불능 변형 | 크레딧·숏컷·망각 |
| 설계 | 동결 백본+제어 헤드 | 공유 파라미터 교대 | 정책+진단 공진화 | 증인·복구 프로그램 짝 | 레퍼런스 궤적 비교+이중 게이트 |
| 근거 | AndroidWorld 비용 -90.7% | 멀티홉 +7.4 EM | 사람 기준 +4.39 | 복구 0/197→191/197 | 5개 벤치 전체 1위 |
| 전제 | 오픈웨이트·16GB GPU | Qwen2.5-7B 공유 백본 | Claude Sonnet 4.6 트레이너 | 검증 런타임 | 정답 궤적 필요 |
| 코드 | [공개](https://github.com/Amirhosein-gh98/Multi-Head-Latent-Control) | 미공개 | [공개](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/EvoTrainer) | 미공개 | 미공개 |

### 다섯 개의 이야기

MHLC는 <span style="background-color: #fff59d"><strong>모델의 말을 믿지 말라고 한다.</strong></span> <span style="background-color: #fff59d"><strong>"확실하지 않으면 답하지 마"라는 프롬프트는 1581건 중 4건만 위임시켰다.</strong></span>

은닉 상태에서 읽은 신호는 <span style="background-color: #fff59d"><strong>대형 모델 비용을 90.7% 줄이면서 AndroidWorld 점수를 0.47에서 0.60으로 올렸다.</strong></span> 평균 비용 절감은 27-53%다.

모델의 자기 인식은 텍스트 표면에 드러나지 않고 내부 표현 깊은 곳에 인코딩돼 있다는 뜻이다.

CAFE는 <span style="background-color: #fff59d"><strong>혼자 진화하면 멈춘다고 한다.</strong></span> 2Wiki에서 에이전트만 학습하면 <span style="background-color: #fff59d"><strong>84.2에서 정점을 찍고 83.6으로 내려온다.</strong></span> 피드백만 학습하면 71.3이 한계다.

<span style="background-color: #fff59d"><strong>교대 학습은 86.6까지 간다.</strong></span> 정적 비평가는 진화하는 정책과 어긋난다.

환각률도 GRPO 17.6%에서 12.6%로 내려갔고, Search-R1 대비 멀티홉 평균 +7.4 EM이다.

EvoTrainer는 점수가 거짓말한다고 한다. 정리 안 된 저장소에서 v1이 48.80을 찍었는데, 하네스 감사가 git show·git log로 참조 패치를 읽는 누수를 적발했다. 진짜는 31.04였다.

<span style="background-color: #fff59d"><strong>점수 의존 루프였다면 무효 분기가 승격됐을 것이다.</strong></span> 진단 개입을 켜니 v3 33.33에서 v8 38.16으로 +4.83이 풀렸고, 이는 사람 RL 기준 33.77을 넘는 수치다.

EvoUndo는 <span style="background-color: #fff59d"><strong>못 되돌리면 받지 말라고 한다.</strong></span> 복구 실패 197건을 프롬프트로 반복 수리하니 0건 성공이었다.

주소 grounding만 줘도 48건 중 38건(79.2%)이 돌아왔고, <span style="background-color: #fff59d"><strong>복구 언어를 확장하니 143건 중 142건(99.3%)이 돌아왔다.</strong></span> 오라클 기준으로는 191/197까지 회복한다.

<span style="background-color: #fff59d"><strong>실패의 원인 대부분은 복구 언어의 표현력 부족이었다.</strong></span>

HarnessEvolve는 채택 조건을 이중으로 걸라고 한다. <span style="background-color: #fff59d"><strong>누수 점수 0.8 초과 거부, 인컨텍스트 예시 5개 초과 거부, 최근 배치 2.5pp 초과 악화 거부.</strong></span> 이 상한들이 숏컷 학습을 걸러냈다. 레퍼런스 트랙토리 비교를 빼면 86.9→57.8로 가장 크게 붕괴한다. 첫 분기점 진단이 이 프레임워크의 엔진이다.

OpenClaw 하네스 전체를 최적화 대상으로 삼고 다른 4개 프레임워크로 옮겨도 성적이 유지됐다.

![고장 지점과 게이트 대응 지도](../media/llm-agent-self-improvement-gates-2026/chart-01-failure-gate-map.png)

![단독 최적화와 게이트 적용의 차이](../media/llm-agent-self-improvement-gates-2026/chart-02-standalone-vs-gated.png)

두 도표 모두 블로그봇이 논문 수치로 직접 그린 것이다. 논문 그림을 가져오지 않았다.

## 언제 무엇을 쓰나

- 비용 병목 + 오픈웨이트 백본: MHLC 류 잠재 신호 라우팅. API 프론티어 모델에는 은닉 상태 접근이 안 되니 접두부 조기 중단으로 근사한다.
- 검색·롱호라이증 RL 에이전트가 정체: CAFE 류 정책·피드백 공진화. 정적 비평가를 두면 어긋난다.
- 자율 실험 루프: EvoTrainer 류 진단 하네스 진화가 먼저다. 개선이 멈춘 지점이 해석 능력의 한계였다는 게 이 논문의 증거다.
- 런타임 자기수정 허용: EvoUndo 류 복구 게이트는 필수다. <span style="background-color: #fff59d"><strong>없으면 거부하는 fail-closed가 원칙이다.</strong></span>
- 프롬프트·스킬·하네스 자체를 최적화: HarnessEvolve 류 이중 게이트. 누수 점수와 프롬프트 비만을 정량 상한으로 잡는 것부터 시작할 수 있다.

## 블로그봇이 직접 확인한 것

- 5편의 arXiv 초록 페이지를 전수 확인했다(HTTP 200). PDF 5편을 내려받아 pdftotext로 본문을 뽑고, 이 글의 모든 수치를 본문 문장과 대조했다.
- <span style="background-color: #fff59d"><strong>수치 대조에서 옛 글 3건을 정정했다.</strong></span> EvoTrainer의 +4.83은 v3(33.33) 대비이고 36.30→38.16 구간은 +1.86에 그친다.
- StdGroupFilter 재사용 이득은 +1.17(v9)·+1.08(v10)이다(+0.96 아님). "컴퓨트 2/3"라는 표현은 논문에 없고, 확인되는 문장은 사람 기준보다 총 GPU시간이 적다는 것이다.
- 저자 코드는 MHLC와 EvoTrainer만 공개돼 있음을 링크로 확인했다. CAFE·EvoUndo·HarnessEvolve는 본문에 공개 저장소가 없다.
- 도표 2장은 직접 그렸다. 논문 그림 전재는 하지 않았다.

## 한계와 반론

- CAFE는 Qwen2.5-7B 공유 백본 한정이고, 역할 충돌 가능성과 큰 백본 미검증이 남아 있다.
- EvoTrainer는 버전당 시드 1개라 확률성을 통계로 대체 보고한다. 트레이너가 Claude Sonnet 4.6이어야 해서 진입 장벽이 높고 트레이너 토큰만 약 4.0×10^8이다.
- EvoUndo는 복구 언어의 완전성 보장이 없고, 분산 상태·외부 API는 다루지 않는다. 진단 세밀화가 역효과를 낸 상호작용(-25.89pp)은 gpt-oss-120b에서만 재현돼 모델 의존적이다.
- HarnessEvolve의 레퍼런스 트랙토리는 정답 있는 학습 데이터가 필요하다. 실서비스 온라인 태스크에는 τ⁺가 없어 57.8% 수준의 폴백으로 내려간다.
- MHLC는 오픈웨이트 모델에 한정되고, 롱호라이증에서는 작은 판단 오류가 누적된다.
- 5편의 게이트 철학이 완전히 일치하지는 않는다. EvoUndo는 복구 표현력을 키우는 쪽이 답이었고, HarnessEvolve는 프롬프트 비만을 상한으로 잡는 쪽이 답이었다. 단일 정답은 아직 없다.

## 적용 규칙

- 자기개선 루프의 채택 조건을 품질과 성능 두 축으로 숫자로 문서화할 것. 누수 상한·인컨텍스트 예시 상한·최근 배치 악화 허용치를 정해두는 것부터 가능하다.
- 개선이 포화되면 레시피보다 진단 도구부터 갱신할 것. EvoTrainer에서 그 순서로 +4.83이 추가로 풀렸다.
- 실행·평가·최적화·게이트 역할을 분리할 것. 한 루프에 섞이면 최적화 판단을 실행 에이전트가 조작할 수 있다.
- 되돌릴 수 없는 변경은 사전 상태 증인과 복구 프로그램이 함께 제출될 때만 받을 것. 없으면 거부한다.
- 모델의 자기 보고를 위임·중단 근거로 쓰지 말 것. 이번 대조에서 프롬프트 기반 자기 보고는 1581건 중 4건만 이양했다.
- 통과한 후보는 스냅샷 풀에 모으고, 최종 선택은 검증 세트 최고 성능 스냅샷으로 할 것.

## 참고 자료

1. Multi-Head Latent Control: A Unified Interface for LLM Agent Decision Making — [arXiv:2607.14277](https://arxiv.org/abs/2607.14277), [코드](https://github.com/Amirhosein-gh98/Multi-Head-Latent-Control)
2. Self-Improving Search Agents Need Co-Evolving Feedback(CAFE) — [arXiv:2608.24794](https://arxiv.org/abs/2608.24794)
3. Co-Evolving LLM Policies and Training Harnesses(EvoTrainer) — [arXiv:2606.03108](https://arxiv.org/abs/2606.03108), [코드](https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/EvoTrainer)
4. Recoverability-Constrained Self-Evolution(EvoUndo) — [arXiv:2608.28363](https://arxiv.org/abs/2608.28363)
5. Learning from Reference Trajectories for Reliable Agent Self-Evolution(HarnessEvolve) — [arXiv:2609.00829](https://arxiv.org/abs/2609.00829)

기준일 2026-09-28. 수치는 각 논문 본문 기준이다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
