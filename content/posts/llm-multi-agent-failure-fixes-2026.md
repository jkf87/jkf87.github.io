---
title: "LLM 에이전트 여러 개가 실패하는 4가지 지점과 해법: DarkForest·SearchOS·WebSwarm 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "멀티에이전트 LLM이 무너지는 지점을 오류 전파, 상태 휘발성, 깊이와 넓이 균형, 상관 오류 집계로 묶고, 각 지점의 해법을 원문 대조 수치로 정리했습니다."
tags:
  - 멀티에이전트
  - LLM 에이전트
  - 에이전트 설계
  - AI 자동화
refactor_hub_id: multi-agent-02
aliases:
  - darkforest-less-talk-multi-agent-llms-2026-05-28
  - posts/2026-07-13-llm-agent-failure-taxonomy-synthesis
  - posts/2026-07-15-webswarm-recursive-multi-agent-web-search
  - posts/2026-07-17-searchos-multi-agent-information-seeking
  - posts/2026-07-26-capable-llms-outgrow-multi-agent-collaboration
  - posts/2026-09-12-bayesian-backward-multi-agent
draft: false
sources_read: "본문: arXiv 2605.25188(DarkForest)·2607.08662(WebSwarm)·2607.15257(SearchOS)·2609.11709(베이즈 역방향) 초록과 본문 HTML, 2607.05775(실패 분류)는 초록(본문 HTML 없음), Nature s42256-026-01268-y 본문 일부를 2026-09-30에 fetch해 수치 대조. 코드: github.com/PearLoveTana/DarkForest_Review·github.com/songxiaoshuai/WebSwarm HTTP 200 확인, SearchOS는 arXiv 페이지의 github.com/antins-labs/SearchOS 공개 링크 확인, 베이즈 역방향·실패 분류는 저자 코드 링크 확인 못 함"
novelty_vs_paper: "45% 임계점·오류 증폭 배수·충돌률·벤치마크 점수와 프레임워크 제안은 각 논문의 기여임. 이 글의 자체 기여는 6편을 실패 4지점(오류 전파·상태 휘발·깊이와 넓이·상관 오류)으로 재배열해 지점별 해법을 매핑한 것, 자체 제작 차트 2장, 미검증 수치 제외 판정임"
---

## 한눈에 보는 결론

기준일 2026-09-30. 이 글에 나오는 숫자는 전부 원문과 대조한 값입니다.

결론부터 정리했습니다. 멀티에이전트 LLM은 네 지점에서 무너집니다. <span style="background-color: #fff59d"><strong>오류 전파, 상태 휘발성, 깊이와 넓이 균형 붕괴, 상관 오류 집계</strong></span>입니다. 그리고 네 지점마다 이미 검증된 해법이 각각 나와 있습니다.

도입 전에 볼 숫자가 하나 있습니다. Nature Machine Intelligence의 통제 실험(260개 구성, LLM 3개 계열, 벤치마크 6종)에서 <span style="background-color: #fff59d"><strong>단일 에이전트 기준 성능이 약 45%를 넘으면 에이전트를 추가하는 순간 성능이 깎였습니다</strong></span>. 이 임계점은 SWE-bench Verified와 Terminal-Bench 16개 구성에서 <span style="background-color: #fff59d"><strong>멀티에이전트 효과의 부호를 94% 정확도로 예측</strong></span>했습니다.

 판단의 첫 질문은 "단일로 몇 점인가"입니다.

| 실패 지점 | 증상 | 해법(논문) | 검증된 수치 |
|---|---|---|---|
| 오류 전파·증폭 | 틀린 답이 복제돼 자신만만한 합의로 수렴 | 통신 통제+보정 집계(DarkForest) | MATH 76.80%(+5.00%p), 토큰 최대 6.5배 절감 |
| 상태 휘발성 | 진행 추적이 무너지고 같은 쿼리 반복 | 상태 외부화(SearchOS) | 검색 호출 39.1%·페이지 호출 42.7% 감소 |
| 깊이와 넓이 균형 붕괴 | 단일 궤적은 얕고 무작정 병렬은 깊이 손실 | 재귀 위임 트리(WebSwarm) | BrowseComp-Plus 68.00 vs 단일 ReAct 50.50 |
| 상관 오류 집계 | 다수결·판정관이 같은 오답으로 수렴 | 역방향 앵커(베이즈 역방향 추론) | 오류 충돌률 0.196~0.413 vs 0.680~0.829 |

![멀티에이전트 실패 4지점과 해법 매핑](../media/llm-multi-agent-failure-fixes-2026/chart-01-failure-fix-map.png)

## 무엇을 비교했나

기존 글 6편을 하나로 합치는 허브 문서입니다. 옛 URL은 이 문서로 리다이렉트됩니다. 비교 대상은 이 6종입니다.

1. [DarkForest](https://arxiv.org/abs/2605.25188) — 통신을 통제한 멀티에이전트 조정 프레임워크
2. [LLM 에이전트 실패 6클러스터 종합](https://arxiv.org/abs/2607.05775) — 2023~2026년 연구 27편 교차 분석
3. [WebSwarm](https://arxiv.org/abs/2607.08662) — 재귀 위임 기반 다중 에이전트 검색
4. [SearchOS](https://arxiv.org/abs/2607.15257) — 상태를 시스템으로 뺀 다중 에이전트 검색
5. [Nature Machine Intelligence 통제 실험](https://www.nature.com/articles/s42256-026-01268-y) — 단일 대비 멀티에이전트 성능 비교
6. [베이즈 역방향 집계](https://arxiv.org/abs/2609.11709) — 역방향 사후분포 앵커 집계법

## 방법 비교

### 오류 전파는 통신 통제와 보정 집계로

문제의 진단이 먼저입니다. DarkForest 논문은 에이전트끼리 원본 추론을 주고받으면 틀린 중간 추론이 채택되고 증폭된다고 봅니다. MATH에서 독립 에이전트 3개 중 최소 하나는 정답을 냈는데, 조정 과정에서 그 답을 잃어버리는 경우가 확인됐습니다.

해법은 세 가지로 짜여 있습니다. 에이전트는 서로 출력을 보지 않고 독립적으로 답을 냅니다. 코디네이터는 전체 트레이스 대신 정책이 허용한 압축 증거만 받습니다. 집계는 표 개수로 세지 않고 <span style="background-color: #fff59d"><strong>에이전트 신뢰도·파싱 품질·독립성 보정을 조합한 보정 신뢰도 분포</strong></span>로 합니다.

결과는 6개 추론 벤치마크에서 최강 베이스라인 대비 최대 30.7% 개선, 토큰 소모는 최대 6.5배 절감이었습니다. MATH 정확도는 <span style="background-color: #fff59d"><strong>76.80%로 Self-Consistency보다 5.00점 높았습니다</strong></span>. 코디네이터 가드레일 개입률은 13.80%, 그중 잘못된 개입은 3.20%였습니다.



### 상태 휘발성은 외부 상태 저장소로

계획·증거·실패 기록이 대화 이력에만 있으면 작업이 길어지는 순간 잃어버립니다. SearchOS 논문의 진단입니다. 검색이 실패하면 같은 쿼리를 반복하고, 에이전트를 늘리면 같은 작업을 중복합니다.

해법은 정보 탐색을 표 완성 문제로 정의하는 것입니다. 진행 상황을 <span style="background-color: #fff59d"><strong>작업 큐·증거 그래프·커버리지 맵·실패 메모리 네 가지 외부 상태</strong></span>로 빼고, 제어를 프롬프트 대신 미들웨어가 맡습니다. 실패 메모리가 없으면 에이전트 그룹이 같은 막다른 경로를 여러 번 탐색한다는 것도 실험으로 확인했다고 합니다.

결과는 WideSearch·GISA에서 평가한 단일·다중 기준선 전체를 앞선 것이었습니다. 검색 전략·사이트 접근 스킬을 재사용하자 <span style="background-color: #fff59d"><strong>검색 호출 39.1%, 페이지 호출 42.7%, 세션 시간 36.6%가 줄었습니다</strong></span>. 시행착오가 줄어서 품질과 효율이 같이 오르는 구조입니다.

### 깊이와 넓이는 재귀 위임으로

단일 ReAct 에이전트는 하나의 긴 궤적에 묶여 깊이와 넓이를 같이 잡지 못합니다. 무작정 병렬로 나누면 이번엔 깊이를 못 팝니다. WebSwarm이 겨냥한 딜레마입니다.

해법은 실행 중에 만들어지는 위임 트리입니다. 각 노드에 <span style="background-color: #fff59d"><strong>지역 목표와 검색 모드의 쌍</strong></span>을 부여합니다. 모드는 atom(단일 팩트 조회)·deep(탐색+검증 직렬)·wide(병렬 분할 정복)·entity_collect(집합 수집) 4종입니다.

 노드는 스스로 풀거나 하위 노드로 위임합니다. wide 확장 전에는 경량 탐색으로 웹 정보 구조를 먼저 파악합니다.

결과는 GLM-4.5 백본에서 BrowseComp-Plus <span style="background-color: #fff59d"><strong>68.00(단일 ReAct 50.50, +17.50)</strong></span>, WideSearch Row F1 44.14(기존 최고 39.98 대비 +10.91), DeepWideSearch 성공률 6.58(+2.63)이었습니다.

 Kimi-K2·Qwen 계열 백본에서도 개선이 유지돼서, 개선이 모델 능력보다 오케스트레이션 구조에서 온다는 해석이 성립합니다.

### 상관 오류는 방향을 뒤집는 앵커로

투표든 LLM 판정관이든 증거에서 결론으로 가는 순방향 경로 안에서 판단합니다. 그래서 순방향 풀이가 공유하는 오류를 그대로 상속합니다. 베이즈 역방향 집계 논문의 진단입니다.

해법은 명시적 우도로 사후분포를 한 번 뒤집는 것입니다. 만든 <span style="background-color: #fff59d"><strong>역방향 사후분포 R을 융합 앵커로 쓰는데, LLM 호출 2회 추가</strong></span>면 됩니다. R은 단독 정확도가 더 낮은데 융합에 넣으면 최고 성능이 나옵니다. 다른 인수분해에서 나왔기 때문에 오류가 덜 겹치는 것입니다.

결과는 DDXPlus(49개 감별진단 레이블) 5개 백본 평가에서, 순방향 5에이전트 top-1이 갈리는 구간에서 최고 순방향 선거 규칙보다 <span style="background-color: #fff59d"><strong>+1.2~+4.7pp</strong></span>였습니다.

 오류 충돌률은 <span style="background-color: #fff59d"><strong>R이 0.196~0.413, 풀 내 에이전트는 0.680~0.829</strong></span>로 겹침이 확실히 적었습니다.

### 에이전트를 늘리기 전에 볼 기준

Nature MI 실험은 잣대입니다. 오류 증폭 배수를 보면 독립형이 17.2배, 중앙집중형이 4.4배였습니다. <span style="background-color: #fff59d"><strong>검증 계층이 집계 앞에서 오류를 걸러낸다</strong></span>는 뜻입니다. 성능 변화 폭은 구조화된 재무 추론에서 +80.8%, 순차 계획에서 −70.0%로 갈렸고, 갈림길은 작업 분해 가능성이었습니다.

실패 6클러스터 종합(arXiv 2607.05775)도 같은 방향입니다. 27편(벤치마크 19종)을 교차 분석한 결과 <span style="background-color: #fff59d"><strong>하위 작업 성공이 전체 성공으로 이어지지 않고, 실패는 작업 길이에 따라 비선형으로 커졌습니다</strong></span>. 스캐폴딩을 더 얹는 것도 효과가 일관되지 않았습니다.

## 언제 무엇을 쓰나

1. 단일 에이전트로 먼저 측정합니다. 그 점수가 약 45%를 넘으면 단일을 유지합니다. 회귀 모델이 같은 도메인 내 최적 아키텍처를 고른 비율은 87%(R²=0.373)였습니다.
2. 분해 가능한 분석 작업(요인이 독립인 경우)이면 중앙집중형 병렬이 후보입니다. 순차 의존이 강한 계획 작업은 단일로 둡니다.
3. 합의가 필요한데 오염이 걱정이면 DarkForest식 구조, 즉 독립 생성과 보정 집계를 씁니다.
4. 반복 조사·장기 탐색이면 SearchOS식 상태 외부화를 씁니다. 커버리지 맵으로 빈칸을 배분하고 실패 메모리를 공유하면 됩니다.
5. 깊이와 넓이가 동시에 필요하면 WebSwarm식 재귀 위임을 쓰되, 트리 크기 상한을 먼저 정합니다.
6. 폐쇄 레이블 집합을 다수결로 집계하는 지점에는 역방향 앵커 호출 2회를 붙입니다.

## 블로그봇이 직접 확인한 것

2026-09-30에 원문을 직접 fetch해 대조했습니다. arXiv 초록 5종, 본문 HTML 4종(DarkForest·WebSwarm·SearchOS·베이즈 역방향), Nature 본문 일부, 전부 정상 응답을 받았습니다.

이 글의 벤치마크 수치는 문서 본문에서 해당 숫자를 직접 찾아 확인한 값입니다. 확인 결과가 아래 차트입니다.

![인용 수치의 원문 대조 결과](../media/llm-multi-agent-failure-fixes-2026/chart-02-verified-numbers.png)

코드는 3곳을 확인했습니다. [DarkForest_Review](https://github.com/PearLoveTana/DarkForest_Review)와 [WebSwarm](https://github.com/songxiaoshuai/WebSwarm) 저장소는 HTTP 200을 반환했습니다. SearchOS는 arXiv 페이지에 [antins-labs/SearchOS](https://github.com/antins-labs/SearchOS) 공개 링크가 붙어 있었습니다. 베이즈 역방향과 실패 분류 논문에서는 저자 코드 링크를 확인하지 못했습니다.

확인하지 못한 수치는 뺐습니다. 실패 분류 글의 도구 오류 12~18%(본문 HTML 부재), Nature 글의 분산형 7.8배·조정 오버헤드 9.5배/21.8배·벤더별 세부 수치, 베이즈 글의 R 단독 정확도 감소 폭(7.8~26.4pp)은 원문에서 재확인하지 못해 이번 버전에서 제외했습니다.

## 한계와 반론

Nature MI 실험은 현재 토큰 기반 조정만 테스트했습니다. 잠재 공간 표현 공유 같은 대안은 미검증이라고 논문 스스로 밝힙니다. 성능 변화 폭(+80.8%/−70.0%)은 서술적 패턴으로 보고된 값이라 확정 효과로 읽으면 안 됩니다.

실패 6클러스터 종합은 원본 실험을 재현하지 않고 27편을 재분석한 2차 연구입니다. 27편이 전체 문헌을 대표한다는 보장도 없습니다.

SearchOS 평가는 텍스트 웹 검색에 한정됩니다. 조사 과제를 표로 세우는 스키마 설계가 전체 성능의 병목이 될 수 있다는 점도 논문이 인정한 한계입니다.

역방향 앵커는 폐쇄 레이블 집합(분류·감별진단)에서만 검증됐습니다. 자유 생성·도구 사용 과제에서는 우도 정의 자체가 열린 문제라고 저자가 명시합니다.

DarkForest도 완승은 아닙니다. FinQA 실행 정확도는 15.67%로 2위였고 1위보다 0.33점 낮았습니다. 압축 통신이 코드·수치 계산류에서 정보 손실로 작용할 수 있다는 해석이 가능합니다.

WebSwarm의 재귀 위임은 노드가 늘면 호출 비용도 함께 늘어납니다. 본문이 제시하는 운영 난제이고, 트리 상한 설계가 필수인 이유입니다.

## 적용 규칙

1. 멀티에이전트 구성을 제안받으면 단일 베이스라인 점수부터 요구하세요. 약 45%를 넘으면 이번 실험의 근거로 단일을 유지하면 됩니다.
2. 다중 구성을 쓴다면 검증 계층을 집계 앞에 두세요. 오류 증폭은 중앙집중형 4.4배, 독립 방치는 17.2배였습니다.
3. 통신량을 늘리지 마세요. 집계 품질(신뢰도·독립성 보정)로 올리는 편이 정확도와 토큰 비용에서 같이 이겼습니다(최대 6.5배 절감).
4. 반복 조사에는 실패 메모리를 파일로 공유하세요. 스킬 재사용으로 검색 호출이 39.1% 줄었습니다.
5. 재귀 위임에는 노드 수·깊이 상한을 설정하세요. 트리 비용이 재귀적으로 커지는 구조입니다.
6. 다수결 집계 지점에는 역방향 질문 호출 2회를 붙이세요. 단, 레이블 집합이 닫힌 과제에서만입니다.

## 자주 묻는 질문

- 멀티에이전트 LLM은 언제 단일 에이전트보다 성능이 떨어지나요? 단일 기준 성능이 약 45%를 넘을 때입니다. 16개 검증 구성에서 부호 예측 정확도는 94%였습니다(기준일 2026-09-30).
- 다중 에이전트의 오류 전파는 어떻게 줄이나요? 에이전트를 독립으로 두고 통신을 압축 증거로 제한한 뒤 보정 집계하면 됩니다. DarkForest는 MATH 76.80%, 토큰 최대 6.5배 절감을 기록했습니다.
- 검색 에이전트가 같은 실패를 반복하면 뭘 고쳐야 하나요? 상태 저장소입니다. 실패 메모리를 세션 넘어 공유하고 커버리지 맵으로 빈칸을 배분하는 구조가 반복 탐색을 줄였습니다(검색 호출 39.1% 감소).
- 에이전트 다수결이 같은 오답으로 수렴하면 어떻게 하나요? 결론에서 증거로 거꾸로 가는 역방향 우도 호출 2회를 앵커로 추가해 보세요. 오류 충돌률이 0.680~0.829에서 0.196~0.413로 내려갔습니다.

## 참고 자료

1. DarkForest: Less Talk, Higher Accuracy for Multi-Agent LLMs — [arXiv 2605.25188](https://arxiv.org/abs/2605.25188)·[코드](https://github.com/PearLoveTana/DarkForest_Review)
2. 실패 6클러스터 종합 — [arXiv 2607.05775](https://arxiv.org/abs/2607.05775)
3. WebSwarm — [arXiv 2607.08662](https://arxiv.org/abs/2607.08662)·[코드](https://github.com/songxiaoshuai/WebSwarm)
4. SearchOS — [arXiv 2607.15257](https://arxiv.org/abs/2607.15257)·[코드](https://github.com/antins-labs/SearchOS)
5. 단일 대비 멀티에이전트 통제 실험 — [Nature Machine Intelligence s42256-026-01268-y](https://www.nature.com/articles/s42256-026-01268-y)
6. 베이즈 역방향 집계 — [arXiv 2609.11709](https://arxiv.org/abs/2609.11709)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
