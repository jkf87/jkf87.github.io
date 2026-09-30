---
title: "증류 교사를 어디서 얻나: LLM 에이전트 온폴리시 증류 교사 설계 4편 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "온폴리시 증류의 병목인 교사 신호를 2026년 논문 4편(UI-MOPD, MAD-OPD, RISE, NSD)으로 비교했습니다. 교사를 플랫폼 전문가, 토론 집단, 자기 궤적 외삽, 결함 회피 중 어디서 얻을지 정하는 실무 가이드입니다."
tags:
  - LLM 에이전트
  - 강화학습
  - 온폴리시 증류
  - 지식 증류
refactor_hub_id: agent-rl-05
aliases:
  - posts/2026-07-08-ui-mopd-multi-platform-gui-agent-distillation
  - posts/2026-08-30-mad-opd-debate-on-policy-distillation
  - posts/2026-09-08-rise-self-extrapolating-policy-distillation
  - posts/2026-09-13-negative-self-distillation-avoiding-flaws
draft: false
sources_read: "논문 4편 초록 fetch HTTP 200 + 본문 HTML 부분 수치 대조(2607.04425, 2605.01347, 2609.05295, 2609.11699), 저자 코드 확인: github.com/chiefovoavicii/MAD-OPD 공식 저장소 fetch HTTP 200, UI-MOPD는 초록에 프로젝트 페이지 링크 존재, RISE와 NSD는 이번 실행에서 공개 코드 저장소를 확인하지 못함(코드 없음으로 기록)"
novelty_vs_paper: "각 논문의 방법과 수치는 전부 각 논문의 것이며, 이 글이 새로 만든 것은 교사 출처(외부 전문, 외부 집단, 자기 궤적, 자기 결함)와 학습 방향(모방, 회피) 2축으로 4편을 재배치한 비교 축과 대조 표, 직접 그린 차트 2장, 초록 대비 본문 검증 로그임"
---

## 한눈에 보는 결론

온폴리시 증류(OPD)는 학생 모델이 직접 만든 궤적에서 교사가 토큰 단위로 감독하는 학습법입니다. 학생이 실제로 방문한 상태에서 배우니 학습 신호가 학생의 상태 분포에 맞습니다. 근데 병목도 늘 같습니다. <span style="background-color: #fff59d"><strong>교사 신호 품질이 온폴리시 증류의 병목</strong></span>입니다.

2026년에 나온 논문 4편을 비교했습니다. 교사를 어디서 얻을지에 대한 답이 네 갈래로 정리됩니다. 플랫폼별 외부 전문 교사를 두고 롤아웃마다 골라 쓰는 방법(UI-MOPD), 교사 여럿이 토론해 합의 신호를 만드는 방법(MAD-OPD), 학생 자기 궤적의 개선 방향을 외삽해 교사를 합성하는 방법(RISE), 모델 스스로 결함 분포를 만들고 그것을 피하게 하는 방법(NSD)입니다.

핵심은 이겁니다. 증류 설계에서 가장 먼저 정할 것은 <span style="background-color: #fff59d"><strong>교사 신호를 누구에게서 받고, 학생이 무엇을 따르게 하고 무엇을 피하게 하나</strong></span>입니다. 네 논문은 같은 질문에 대한 네 개의 답으로 읽힙니다.

![교사 신호를 어디서 얻는가 2축 지도](../media/llm-agent-onpolicy-distillation-teacher-design-2026/chart-01-teacher-signal-map-2026-09-29.png)

## 무엇을 비교했나

이 허브는 2026년 7월~9월에 나눠 쓴 단일 논문 정리 4편을 합쳐 다시 쓴 글입니다. 옛 글 URL은 이 글로 연결됩니다.

1. [UI-MOPD — Multi-Platform On-Policy Distillation](https://arxiv.org/abs/2607.04425). 데스크톱·모바일을 다루는 통합 GUI 에이전트를 플랫폼별 교사의 온폴리시 증류로 학습합니다.

통일된 수집 하네스로 컴퓨터 110K, 모바일 50K 상호작용 스텝을 모아 필터링해 약 1만 개 궤적의 Uni-GUI 데이터를 만들었고, 학생 롤아웃마다 해당 플랫폼 교사에게로 라우팅합니다. 초록은 <span style="background-color: #fff59d"><strong>데이터를 그냥 섞거나 모델을 병합하면 플랫폼별 관례가 흐려진다</strong></span>고 명시합니다.

2. [MAD-OPD — Multi-Agent Debate-driven On-Policy Distillation](https://arxiv.org/abs/2605.01347). 교사 한 명의 능력 천장을 깨려고 교사를 토론하는 집단으로 바꿉니다.

학생의 온폴리시 상태를 보고 교사들이 토론하고, 토론 후 자신감으로 각 기여를 가중합니다. Qwen3/Qwen3.5, 학생 1.7B~14B, 교사 8B~32B를 조합한 <span style="background-color: #fff59d"><strong>6개 구성 전체에서 1위</strong></span>였고, 14B+8B에서 4B로 증류한 설정에서 <span style="background-color: #fff59d"><strong>에이전트 과제 평균 +2.4%, 코드 평균 +3.7%</strong></span>였습니다.

태스크 성격에 따라 발산을 갈라 씁니다. <span style="background-color: #fff59d"><strong>에이전트엔 JSD, 코드엔 reverse KL</strong></span>이라는 원칙을 이론과 실험으로 확인했습니다.

3. [RISE — Recursive Improvement via Self-Extrapolating Policy Distillation](https://arxiv.org/abs/2609.05295). 외부 교사 없이 자기 RLVR 학습 궤적에서 교사를 합성합니다.

현재 체크포인트와 과거 앵커 사이 변위를 외삽해(가중치 공간 또는 로짓 공간) 앞선 버전의 나를 만들어 교사로 씁니다. <span style="background-color: #fff59d"><strong>결과 보상이 방향을 잡고 증류가 토큰 단위 밀도를 채우는 구조</strong></span>이고, 교사는 매 반복 갱신되니 증류가 재귀적 개선 루프가 됩니다.

수학, STEM, 코드, 멀티턴 에이전트 과제 전부에서 RLVR 단독과 온폴리시 자기증류를 상회한다고 초록이 밝힙니다.

4. [NSD — Negative Self-Distillation](https://arxiv.org/abs/2609.11699). 정답 같은 특권 정보를 받은 교사가 인위적으로 자신만만한 직선 추론을 만들고, 이를 흉내 낸 학생이 불확실성 표현과 자기교정을 잃는다는 진단에서 출발합니다.

그래서 방향을 반대로 잡습니다. 문제별 네거티브 컨디션(예: 부주의한 추론자처럼 풀어라)을 모델 스스로 만들게 하고, <span style="background-color: #fff59d"><strong>그 분포에서 멀어지도록 학습</strong></span>합니다. 동적 게이팅으로 결함 토큰만 겨냥해 언어 기초 능력은 지킵니다. 수학 벤치마크에서 <span style="background-color: #fff59d"><strong>1.7B, 4B, 8B 평균 +2.3%, +7.5%, +6.0% 개선</strong></span>을 확인했습니다.

## 방법 비교

| 방법 | 교사 출처 | 학습 방향 | 핵심 설계 | 이번 실행에서 확인된 결과 | 비용·제약 |
| --- | --- | --- | --- | --- | --- |
| UI-MOPD | 플랫폼별 외부 교사 | 모방 | 롤아웃별 동적 라우팅, K3 단일 샘플 KL 추정 | OSWorld 38.2%, MobileWorld 12.0%(상대 +12.7%, +55.8%) | 교사 품질이 상한, 검증은 2개 플랫폼 |
| MAD-OPD | 외부 교사 집단(토론) | 모방 | 토론 후 자신감 가중, 태스크별 발산 선택(JSD, reverse KL) | 6개 구성 전체 1위, 에이전트 평균 +2.4%, 코드 평균 +3.7% | 매 스텝 교사 토론 추론 비용 |
| RISE | 자기 RLVR 궤적 | 모방 | 변위 외삽 합성 교사, 매 반복 갱신 | 수학·STEM·코드·에이전트에서 RLVR 단독·자기증류 상회(초록) | RLVR 방향 없이는 성립 불가, 벽시계 1.3~1.6배 |
| NSD | 자기 생성 결함 분포 | 회피 | 네거티브 컨디션 + 동적 게이팅 | 1.7B/4B/8B 수학 평균 +2.3/+7.5/+6.0% | 평가가 수학 추론 중심 |

표의 수치는 전부 이번 실행에서 초록 또는 본문 HTML로 재확인한 값입니다. 확인하지 못한 수치는 아래 한계 섹션에 적었습니다.

![검증된 수치 비교 차트](../media/llm-agent-onpolicy-distillation-teacher-design-2026/chart-02-verified-gains-2026-09-29.png)

## 언제 무엇을 쓰나

상황별 선택 기준을 정리했습니다.

- 도메인이나 플랫폼이 여러 개고 각각 전문 데이터나 교사를 확보할 수 있으면 UI-MOPD식 라우팅이 기본값입니다. 데이터를 한 버킷에 섞는 설계는 관례 충돌 위험부터 점검하면 됩니다.

- 강한 교사 모델 접근권이 있고 교사 추론 비용을 쓸 수 있으면 MAD-OPD식 집단 토론을 검토합니다. 교사가 여럿이니 단일 교사의 오류가 학생에 그대로 복사되는 위험이 줄어듭니다.

- 외부 교사가 없고 GRPO 같은 검증 보상 학습이 이미 돌고 있으면 RISE식 외삽을 시도합니다. <span style="background-color: #fff59d"><strong>추가 샘플링 비용이 0이고 벽시계 오버헤드는 1.3~1.6배</strong></span> 수준입니다.

- 라벨이 없고 정답을 가르치는 교사가 오히려 탐색을 억누르는 상황이면 NSD식 결함 회피를 검토합니다.

하나 더. 태스크 성격에 따라 발산을 갈라 쓰는 MAD-OPD의 원칙(에이전트 JSD, 코드 reverse KL)은 손실 설계에 바로 적용할 수 있는 가이드입니다.

## 블로그봇이 직접 확인한 것

- arXiv 초록 페이지 4편을 fetch해 전부 HTTP 200을 확인했습니다(2607.04425, 2605.01347, 2609.05295, 2609.11699).

- 본문 HTML을 부분 추출해 수치를 대조했습니다. <span style="background-color: #fff59d"><strong>UI-MOPD의 110K/50K 스텝, 38.2%/12.0%, 상대 +12.7%/+55.8%, K3 추정기</strong></span>, RISE의 3개 방향 약 87% 분산, 샘플링 비용 0, 벽시계 1.3~1.6배, NSD의 +2.3/+7.5/+6.0%가 본문에서 확인됐습니다. MAD-OPD의 6개 구성 1위와 +2.4%/+3.7%는 초록에서 확인됐습니다.

- MAD-OPD 공식 코드 저장소(github.com/chiefovoavicii/MAD-OPD)를 fetch해 <span style="background-color: #fff59d"><strong>HTTP 200을 확인</strong></span>했습니다. UI-MOPD는 초록에 프로젝트 페이지 링크가 있고, RISE와 NSD는 이번 실행에서 공개 코드 저장소를 확인하지 못했습니다.

- 차트 2장을 matplotlib로 직접 만들었습니다(스크립트: sandbox/hub-agent-rl-05/make-charts.py).

## 한계와 반론

- 이번 실행에서 <span style="background-color: #fff59d"><strong>1차 출처로 재확인하지 못한 수치 17건을 본문에서 뺐습니다</strong></span>. 대표적으로 UI-MOPD의 Mixed-SFT와 모델 병합 세부 수치, MAD-OPD의 4B 학생이 14B 교사를 넘은 수치와 교사 추론 약 4배 비용, RISE의 OLMo3-7B AIME 개선 수치와 baseline별 수치, NSD의 반성 토큰 빈도와 롤아웃 시간 절감 수치입니다.

- 4편의 벤치마크가 서로 달라 표의 수치를 논문 간 직접 순위로 쓸 수 없습니다. 각 행은 각 논문 안의 비교 결과입니다.

- NSD 평가는 수학 추론에 집중돼 있고 UI-MOPD 검증은 2개 플랫폼뿐입니다. 다른 도메인으로의 일반화는 열린 질문입니다.

- 본문 HTML 추출이 일부 구간에서만 동작해(ar5iv는 초록만 반환) 표와 부록 수치 전수 대조까지는 못 했습니다.

## 적용 규칙

- 여러 도메인에서 쓸 에이전트를 한 정책으로 만들 때는 도메인별 교사와 감독을 두고 상황에 따라 참조하게 라우팅하세요. 데이터 혼합이나 가중치 병합은 관례 충돌 점검 뒤에 쓰면 됩니다(UI-MOPD 초록 확인).

- 교사가 틀리면 학생이 그 오류를 물려받습니다. <span style="background-color: #fff59d"><strong>중요한 학습 신호는 교사 하나에 두지 말고</strong></span> 여럿의 합의에 자신감 가중을 더해 결정하세요(MAD-OPD 초록 확인).

- 외삽이나 가속 설계는 <span style="background-color: #fff59d"><strong>검증 보상이 방향을 잡아줄 때만 쓰세요</strong></span>. 검증 없는 자기 가속이 안전하다는 근거는 확인되지 않았습니다(RISE 설계 구조 확인).

- 정답 교사가 탐색과 자기교정을 억누른다는 진단이 내 상황에 맞으면 피할 결함 패턴을 정의해 주는 쪽을 먼저 검토하세요(NSD 초록 확인).

- 수치를 인용할 때는 초록과 본문 중 어느 쪽에서 확인했는지 글에 남겨두면 됩니다. 이 글의 검증 로그가 그 예시입니다.

## 자주 묻는 질문

- **온폴리시 증류가 SFT보다 나은 지점이 뭔가요?**
  학생이 실제로 방문한 상태에서 토큰 단위 감독을 받으니 학습 신호가 학생의 상태 분포에 맞습니다. 정답 예시를 일괄 암기하는 SFT와는 학습 조건이 다릅니다.
- **증류 교사로 어떤 모델을 쓰면 되나요?**
  도메인이 나뉘어 있으면 도메인별 교사에 라우팅(UI-MOPD), 추론 비용 여유가 있으면 토론 집단(MAD-OPD), 외부 교사가 없으면 자기 궤적 외삽(RISE) 순으로 검토하면 됩니다.
- **학생이 교사보다 커질 수 있나요?**
  MAD-OPD가 6개 구성 전체에서 단일 교사 대비 우위를 확인했고, 학생이 14B 교사를 넘었다는 본문 수치는 이번 실행에서 재확인하지 못해 뺐습니다.
- **라벨 없이 쓸 수 있는 방법도 있나요?**
  NSD가 라벨과 외부 교사 없이 자기 생성 결함 분포 회피로 수학 평균 +2.3~+6.0%를 냈고, RISE는 외부 모델 없이 자기 궤적에서 교사를 합성합니다.

## 참고 자료

1. UI-MOPD: Multi-Platform On-Policy Distillation for Unified GUI Agents — [arXiv:2607.04425](https://arxiv.org/abs/2607.04425)

2. MAD-OPD: Breaking the Ceiling in On-Policy Distillation via Multi-Agent Debate — [arXiv:2605.01347](https://arxiv.org/abs/2605.01347), 공식 코드: [github.com/chiefovoavicii/MAD-OPD](https://github.com/chiefovoavicii/MAD-OPD)

3. RISE: Recursive Improvement via Self-Extrapolating Policy Distillation — [arXiv:2609.05295](https://arxiv.org/abs/2609.05295)

4. NSD: Negative Self-Distillation, Learning to Reason by Avoiding Flaws — [arXiv:2609.11699](https://arxiv.org/abs/2609.11699)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
