---
title: "하네스 진화 후 전문가 imitation은 역풍이다 — 온폴리시 교정 레시피 (arXiv 2609.09134)"
date: 2026-09-09
tags:
  - ai-agent
  - harness
  - imitation-learning
  - lora
  - arxiv
draft: false
description: "Salesforce AI 연구팀이 하네스 진화 후 전문가 트레이터리 imitation이 7개 태스크 전부에서 4~30포인트 하락시키는 이유와, 실패 턴만 고치는 온폴리시 교정으로 78.0%에서 79.7%로 올린 방법을 정리했습니다."
---

## 결론 먼저

Salesforce AI 연구팀이 에이전트 하네스(시스템 프롬프트, 도구 세트, 훅, 컨텍스트 관리)를 자동 진화시킨 뒤, 강한 모델의 트레이터리 전체를 그대로 imitation learning하면 약한 모델이 오히려 <span style="background-color: #fff59d"><strong>7개 엔터프라이즈 태스크 전부에서 4~30포인트 후퇴</strong></span>.

해결책은 학생 모델 자신의 롤아웃에서 실패한 턴 한 곳을 찾아 전문가가 그 턴만 다시 쓰게 하는 온폴리시 교정이었습니다. <span style="background-color: #fff59d"><strong>하네스 진화 이득을 지키면서 추가 이득</strong></span>.

논문: Co-Evolving Harnesses and Models: On-Policy Correction Helps Weaker Models Catch Up Where Imitation Fails (arXiv 2609.09134, 2026-09-08, Salesforce AI, Zhou Yu 외)

![Figure 1: 하네스-모델 공진화 개요](/images/2026-09-09-coevolving-harness-model-onpolicy-correction/fig-1-p3.png)
Figure 1. 각 라운드에서 약한 모델에 맞춰 하네스를 진화시키고, 그 하네스 아래에서 모델을 업데이트한다. 통짜 imitation은 모델-하네스 핏을 깨고, 온폴리시 교정은 핏을 보존한다.

## 핵심 숫자 요약

| 항목 | 값 |
|---|---|
| 태스크 수 | 7개 엔터프라이즈 에이전트 벤치마크 |
| 약한 모델 | Qwen3-Coder-30B-A3B (재현: Gemma-4-26B-A4B) |
| 전문가 | gemini-3.1-pro-preview |
| 기본 하네스 평균 성공률 | 29.2% |
| 진화된 하네스 평균 | <span style="background-color: #fff59d"><strong>78.0% (+48.8)</strong></span> |
| 전문가, 진화 하네스 | 93.6% |
| 전문가 트레이터리 imitation | <span style="background-color: #fff59d"><strong>63.1% (−14.9, 7개 태스크 전부 하락)</strong></span> |
| 온폴리시 교정 | <span style="background-color: #fff59d"><strong>79.7% (+1.7, 5개 상승 2개 노이즈)</strong></span> |
| 교정 데이터 규모 | 약 500행 (교정 ~400 + 자기 성공 ~50) |
| 학습 비용 | LoRA, 1시간 미만 (H100/H200) |

기준일: 2026-09-08 arXiv v1 기준.

## 실험 개요

하네스 진화는 GEPA 스타일 검색으로 프롬프트, 도구, 훅, 컨텍스트 관리를 편집하면서 검증 성능이 오를 때만 편집을 남기는 방식입니다. 약한 모델(Qwen3-Coder-30B)을 실행기로 태스크별 하네스를 진화시키니 평균 29.2%에서 78.0%로 올라갑니다.

여기서 자연스러운 다음 단자는 이겁니다. 전문가(gemini-3.1-pro)가 같은 하네스에서 93.6%까지 나오니, 전문가 트레이터리로 약한 모델을 파인튜닝하면 되지 않겠냐는 거죠. 근데 이게 역풍입니다.

## imitation이 무너진 지점

전문가의 성공 트레이터리를 Qwen 채팅 포맷으로 바꿔 LoRA-SFT하니 <span style="background-color: #fff59d"><strong>78.0%에서 63.1%로 떨어집니다</strong></span>. 급여 감사 −29.9, 웹사이트 관리 −20.3, 브라우저 자동화 −16.0까지, 하락이 7개 태스크 전부에서 재현됩니다. Gemma-4로 바꿔도 같은 패턴입니다.

같은 레시피를 진화 안 된 기본 하네스에 적용하면 <span style="background-color: #fff59d"><strong>29.2% → 35.5%로 오릅니다</strong></span>. 그러니 가르침 신호 자체에는 문제가 없고, 진화된 하네스와의 상호작용에 문제가 있는 겁니다.

실패 분석이 핵심입니다. 모델은 트레이터리를 흉내 내면서 전문가의 지식을 실제로 얻습니다. 도메인 계산 레시피 사용률이 <span style="background-color: #fff59d"><strong>30.8%에서 76.1%로 오릅니다</strong></span>. 문제는 계획(planning)입니다.

계획 실패 비중이 <span style="background-color: #fff59d"><strong>1.1%에서 14.6%로 폭등합니다</strong></span>. 급여 감사 케이스에서 파인튜닝된 모델은 정답을 손에 넣고도 제출을 못 합니다. <span style="background-color: #fff59d"><strong>검증 스텝을 29번 반복</strong></span>하고 프롬프트를 <span style="background-color: #fff59d"><strong>20번 다시 읽다가</strong></span> 78스텝 만에 종료 없이 끝납니다 78스텝 만에 종료 없이 끝납니다. 하네스는 모델의 원래 스텝 바이 스텝 리듬에 맞춰 진화됐는데, 그 리듬이 전문가 스타일로 덮어씌워진 겁니다.

## 온폴리시 교정 파이프라인

제안 방법은 이렇습니다.

- 학생 모델 자신의 롤아웃에서 시작합니다.
- 자동 실패 위치 파악 단계가 실패한 롤아웃에서 잘못된 턴 한 곳을 찾습니다.
- <span style="background-color: #fff59d"><strong>전문가가 그 턴만 다시 씁니다</strong></span>. 앞뒤 스텝은 그대로 둡니다.
- 턴당 3개 후보를 뽑아 품질 판정으로 최선을 남깁니다.
- 이렇게 만든 이렇게 만든 <span style="background-color: #fff59d"><strong>약 500행(교정 ~400행 + 자기 성공 ~50행)</strong></span>으로 LoRA-SFT합니다.

전 과정을 메타 레벨 MLE 에이전트가 자동화합니다. 결과는 79.7%입니다. 웹사이트 관리 +5.6, 재고 알림 +2.2, 코드 리팩토링 +2.2 등 5개 태스크에서 오르고 나머지 둘은 노이즈 범위입니다.

<span style="background-color: #fff59d"><strong>계획 실패 비중은 1.8%로 바닥을 유지</strong></span>, 지식 실패는 46.2%에서 43.2%로 줄어듭니다. 지식 이득은 취하고 하네스 핏은 안 깨뜨리는 구조입니다.

## 실무에 바로 쓸 지점

- 하네스를 특정 모델에 맞춰 진화시켰다면, 이후 파인튜닝은 모델이 실제 방문한 상태에서 가르치세요. <span style="background-color: #fff59d"><strong>통짜 imitation은 하네스 이득을 지웁니다</strong></span>.
- 증류 데이터를 만들 때 전문가 전체 트레이터리보다 학생 롤아웃의 실패 턴 교정이 안전합니다.
- 전문가가 진화된 하네스를 더 잘 쓴다고 해서(93.6% vs 78.0%) <span style="background-color: #fff59d"><strong>그 격차가 imitation으로 닫힌다는 보장은 없습니다</strong></span>.
- <span style="background-color: #fff59d"><strong>LoRA 학습이 1시간 미만</strong></span>이라 이 레시피는 하네스 진화 루프에 얹어 반복할 수 있습니다 이 레시피는 하네스 진화 루프에 얹어 반복할 수 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**하네스 진화 후 전문가 imitation이 실패한 원인은 무엇인가요?**

전문가의 계획 스타일까지 함께 이전되면서, 모델의 고유 계획 스타일에 맞춰 진화된 하네스와의 핏이 깨졌기 때문입니다. 지식 실패는 줄었지만 계획 실패가 1.1%에서 14.6%로 폭등했습니다.

**온폴리시 교정은 성능을 얼마나 올렸나요?**

평균 78.0%에서 79.7%로 +1.7포인트입니다. 7개 중 5개 태스크에서 상승했고 나머지 2개는 노이즈 범위였습니다. 통짜 imitation의 −14.9와 대비됩니다.

**교정 학습 데이터는 얼마나 필요한가요?**

약 500행입니다. 실패 턴 교정 약 400행과 학생 모델 자신의 성공 롤아웃 약 50행을 섞었습니다. 전문가 전체 트레이터리보다 적은 데이터로 안전한 이득을 냈습니다.

**기본 하네스에서는 imitation이 도움이 되나요?**

네. 기본 하네스에서는 같은 imitation 레시피가 29.2%에서 35.5%로 +6.3포인트 올립니다. 문제는 모델에 맞춰 진화된 하네스와의 상호작용이었습니다.
