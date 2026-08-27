---
title: "OpsHarness — 루트 코즈 분석 하네스가 스스로 진화하는 구조 (arXiv 2608.25661)"
date: 2026-08-28
tags: [paper-review, llm-agents, harness, rca, aiops, self-evolving]
draft: false
description: "arXiv 2608.25661 리뷰. OpsHarness는 범용 코딩 에이전트를 감싸는 자가진화형 RCA 하네스로, OpenRCA/RCAEval에서 top-1 59.0%, 범용 에이전트 대비 +63.4%, 기존 RCA 에이전트 대비 4.02배를 기록했다."
---

## 결론 먼저

이 논문의 핵심 주장은 명확합니다. <span style="background-color: #fff59d"><strong>LLM 기반 루트 코즈 분석(RCA)의 성능 격차는 에이전트 바깥의 하네스 레이어에서 발생한다는 것입니다.</strong></span>

CUHK와 ByteDance가 제안한 OpsHarness는 Claude Code나 Codex 같은 범용 에이전트를 그대로 재사용하면서, 그 바깥에 자가진화하는 하네스를 얹었습니다. 결과는 <span style="background-color: #fff59d"><strong>4개 백본 평균 top-1 정확도 59.0%</strong></span>, 맨살 범용 에이전트 대비 +63.4%, 전용 RCA 에이전트 대비 <span style="background-color: #fff59d"><strong>4.02배</strong></span>입니다.

기준일: 2026-08-26 arXiv v1 기준. 원문: [arXiv:2608.25661](https://arxiv.org/abs/2608.25661)

## 핵심 숫자 요약

| 항목 | 값 |
|---|---|
| top-1 정확도 (4 백본 평균) | 59.0% |
| 범용 에이전트(Direct) 대비 상대 개선 | +63.4% |
| 전용 RCA 에이전트 대비 | 4.02× |
| 맨살 범용 에이전트 평균 (Direct) | 36.1% |
| 산업 배포 (Company A) | 0.74 vs 0.24 A@1 |
| 케이스당 비용 | 약 106k 토큰, 325초 |
| 하네스 디스크 풋프린트 | 약 228KB |

## 문제 정의: 전용 에이전트가 이미 진 기준

저자들이 먼저 확인한 사실이 흥미롭습니다. OpenRCA와 RCAEval 두 벤치마크에서 GPT-5.5, Claude Sonnet 4.6, GLM-5.2, DeepSeek-V4 네 모델로 비교했더니, RCA 전용으로 설계된 에이전트(RCA-Agent 17.9%, mABC 5.6%)보다 그냥 Codex/Claude Code에 붙인 범용 에이전트(36.1%)가 모든 백본에서 앞섭니다.

GPT-5.5 기준으로는 bare Codex가 <span style="background-color: #fff59d"><strong>OpenRCA 질의의 45%를 맞히고, OpenRCA 논문 자체의 RCA-Agent는 32%에 그칩니다.</strong></span> 전용 설계가 이미 범용 프레임워크를 따라잡지 못한 상태입니다.

근데 범용 에이전트도 51.2%가 최대라 프로덕션 요구에는 못 미칩니다. 저자들의 분석은 이렇습니다. 실패 원인이 추론 능력 부족이 아니라 <span style="background-color: #fff59d"><strong>시스템 특화 진단 지식 부족</strong></span>이라는 것입니다. 새로 합류한 유능한 엔지니어가 팀의 노이즈 프로필을 모르는 상황과 같습니다. 실제 실패 사례로는 절대값이 크게 튀는 노이즈 카운터를 원인으로 오판하고, baseline이 0 근처라 상대적으로 작은 docker_003 컨테이너 CPU 포화를 놓친 케이스가 나옵니다.

![](/images/2026-08-28-opsharness-self-evolving-rca-harness/fig-1-p1.png)

그림 1. 원문의 핵심 메시지: LLM 기반 RCA의 열쇠는 잘 만든 외부 하네스.

## OpsHarness 구조

![](/images/2026-08-28-opsharness-self-evolving-rca-harness/fig-3-p5.png)

그림 3. OpsHarness 전체 설계 (원문 Fig. 3).

데이터 플레인과 컨트롤 플레인으로 나뉩니다.

데이터 플레인:
- 계층화된 운영 지식 저장소 (K0 시스템 프로필, K1 텔레메트리 스키마, K2/K3 진단 지식)
- 아이디어카드 형태의 도구 라이브러리

컨트롤 플레인 (4개 워크플로):
- setup: 시스템 텔레메트리를 샘플링해 스키마를 추론, 초기 하네스 작성
- diagnose: 지식 + 도구를 활용해 Top-N 원인 리스트 반환
- evolve: 진단 트랙토리에서 성공/실패 패턴을 원자적 제안으로 증류
- verify: 듀얼 게이트 샌드박스 검증 통과 시에만 승격

## 자기진화 루프와 듀얼 게이트

![](/images/2026-08-28-opsharness-self-evolving-rca-harness/fig-4-p7.png)

그림 4. 자기진화 루프 (원문 Fig. 4).

진화는 3단계로 돌아갑니다. 트랙토리 마이닝 → 근거 마이닝/제안 합성 → 단계별 검증.

검증이 이 논문의 묘미입니다. inner 게이트에서는 진화된 하네스가 제안이 나온 원본 케이스에서 <span style="background-color: #fff59d"><strong>정확도 하락이 없어야 하고(ΔA ≥ 0)</strong></span>, 비용 증가가 max(0.05·C, 1) 토큰 이내여야 하며, 정확도든 비용이든 하나는 엄격하게 개선되어야 합니다. outer 게이트에서는 별도 보류 배치에서도 회귀가 없어야 통과합니다. <span style="background-color: #fff59d"><strong>이 듀얼 게이트가 과적합과 회귀를 막는 장치입니다.</strong></span>

## 결과

![](/images/2026-08-28-opsharness-self-evolving-rca-harness/fig-5-p9.png)

그림 5. 12개 연속 진화 윈도우의 A@1 변화 (원문 Fig. 5).

- 연속 진단 모드에서 12개 윈도우 동안 정확도가 지속 상승. <span style="background-color: #fff59d"><strong>게이트를 제거한 no-verify 변형은 초반 상승 후 하락(과적합)</strong></span>
- 검증 없이 진화만 켜면 오히려 나빠진다는 점이 ablation으로 확인됩니다
- 산업 배포: Company A 변경 이상 데이터셋에서 6개 설정 전부 Direct 대비 개선, <span style="background-color: #fff59d"><strong>평균 0.74 vs 0.24 A@1</strong></span>
- 오픈소스 스택(OpenCode + GLM-5.2)에서도 0.73 A@1로 유지됩니다

![](/images/2026-08-28-opsharness-self-evolving-rca-harness/fig-8-p10.png)

그림 8. Company A 산업 데이터셋 결과 (원문 Fig. 8).

## 비용

케이스당 약 106k 토큰, 325초로 Direct(112k, 317s), ICL(106k, 308s)과 동급입니다. <span style="background-color: #fff59d"><strong>전용 에이전트들은 토큰 1.7~2.7배, 시간 2.3~3.5배를 씁니다.</strong></span>

비진화 단계 비용은 setup 0.82M 토큰, evolution 0.75M, verification 1.55M이며 드물게 실행되어 상각됩니다. <span style="background-color: #fff59d"><strong>하네스 전체 온디스크 크기는 약 228KB</strong></span>(도구 106KB, 스킬 95KB, 진화된 지식 27KB)입니다.

## 실무 관점 정리

- 도메인 에이전트를 새로 만들 계획이라면, 범용 에이전트 + 외부 하네스 조합을 먼저 베이스라인으로 잡는 게 순서입니다. 논문 데이터상 전용 에이전트가 이 베이스라인을 이기기 어렵습니다
- <span style="background-color: #fff59d"><strong>"쓸수록 좋아지는" 경험은 진단 트랙토리에서 자동 증류가 가능하며, 듀얼 게이트 없이는 과적합으로 되돌아옵니다</strong></span>
- 시스템이 바뀌어도 콜드스타트(41.4%)가 Direct(36.1%)보다 높아 <span style="background-color: #fff59d"><strong>graceful degradation 합니다</strong></span>

## 더 실습해보고 싶은 분들께

하네스·루프 설계 감각을 키우고 싶다면 두 가지 자료를 추천합니다.

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

OpsHarness가 정확히 뭘 자동화하나요?
범용 에이전트 주변의 RCA 특화 인프라(지식 저장소, 도구 라이브러리, setup/diagnose/evolve/verify 워크플로)를 자동화합니다. 에이전트 자체는 Codex/Claude Code/OpenCode를 그대로 씁니다.

성능은 얼마나 나오나요?
OpenRCA/RCAEval 4 백본 평균 top-1 <span style="background-color: #fff59d"><strong>59.0%</strong></span>이고, 범용 에이전트 대비 +63.4%, 전용 RCA 에이전트 대비 4.02배입니다(2026-08-26 v1 기준).

진화가 과적합되면 어떻게 되나요?
inner/outer 듀얼 게이트가 원본 케이스와 보류 배치 양쪽에서 회귀를 검사하고, 통과 못 한 제안은 폐기합니다. no-verify ablation에서 게이트 제거 시 성능 하락이 확인됐습니다.

추가 비용이 크나요?
케이스당 Direct와 동급(약 106k 토큰, 325초)이고, 진화·검증 비용은 드물게 실행되어 상각됩니다. 전용 에이전트 대비 토큰 1.7~2.7배 저렴합니다.

**원문은 어디서 보나요?**
[arXiv:2608.25661](https://arxiv.org/abs/2608.25661), DOI: [10.48550/arXiv.2608.25661](https://doi.org/10.48550/arXiv.2608.25661). 벤치마크는 [OpenRCA](https://arxiv.org/abs/2503.14152)와 [RCAEval](https://arxiv.org/abs/2405.16150)를 사용했습니다.
