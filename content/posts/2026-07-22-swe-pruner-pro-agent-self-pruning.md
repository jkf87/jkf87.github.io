---
title: "에이전트가 도구 출력을 읽는 순간 이미 뭘 지울지 알고 있었음 — SWE-Pruner Pro 컨텍스트 다이어트"
date: 2026-07-22T10:00:00+09:00
draft: false
tags: ["agent", "coding-agent", "context-engineering", "LLM", "harness", "tool-use"]
categories: ["AI Agents", "LLM"]
source_url: "https://arxiv.org/abs/2607.18213"
github_url: "https://github.com/Ayanami1314/swe-pruner-pro"
---

코딩 에이전트 토큰 예산의 70% 이상이 cat, grep, ls 결과 같은 도구 출력임. 컨텍스트 창이 빨리 차고 긴 컨텍스트 성능 저하까지 옴. SWE-Pruner Pro는 외부 모델 없이 최대 39% 토큰을 절감함. 발상이 실용적이라 정리함.

1. 배경. 기존 해법은 둘로 나뉘었음. perplexity(모델이 다음 토큰을 얼마나 예측 불가능해하는지 재는 값) 기반 범용 압축(LLMLingua 계열)은 에이전트의 현재 의도를 반영 못 함. 작업 특화 가지치기(SWE-Pruner)는 별도 점수 매기는 모델이 필요하고 매 턴 목표 힌트를 명시적으로 써야 했음. 둘 다 가지치기 신호를 에이전트 바깥에서 구해온 것.

2. 발상의 전환은 질문 하나임. "도구 출력을 읽는 건 어텐션이 적용된 forward pass다. 그러면 백본의 hidden state에 이미 어떤 줄이 중요한지 인코딩돼 있지 않을까?"

3. 검증 결과가 명확함. [논문](https://arxiv.org/abs/2607.18213)은 Qwen3-Coder-Next 마지막 층 hidden state에 선형 프로브만 얹었더니 keep/prune 구분이 AUC 0.83으로 나옴. 단순 로지스틱 회귀로. 가지치기에 필요한 정보가 이미 모델 안에 있었다는 것.

4. 시스템화는 간단함. 백본이 도구 응답을 prefill할 때 생기는 hidden state를 가벼운 헤드가 읽어서 줄 단위 keep-or-prune 로짓을 냄. prefill을 공유하니 추가 forward pass가 없음. 가지치기된 응답만 다음 턴 컨텍스트에 들어감.

5. 설계 디테일 두 개가 실무적임. 하나는 길이 인지 임베딩 — 응답이 5줄일 때 잘못 지우면 치명적이고 300줄이면 무방하니 줄 수에 따라 결정을 다르게 함. 다른 하나는 샘플 단위 균형 focal loss — 100줄 중 3줄만 남기는 샘플과 90줄 남기는 샘플의 학습 신호를 균등하게 맞춤.

6. 결과. SWE-QA-Pro(Qwen3-Coder-Next)에서 토큰 39% 절약에 점수 +0.24. Oolong(MiMo-V2-Flash)에서 30% 절약에 +2.2점. SWE-Bench Verified(실제 깃허브 이슈 수정 과제로 채점하는 코딩 벤치마크의 검증 서브셋)에서 resolve rate +3.8%. 품질 저하 없이 절약한 유일한 방법론이었고, 오히려 대부분 지표가 올랐음.

7. 절약이 품질을 높인 게 역설처럼 보이지만 이유가 있음. 노이즈 줄이면 컨텍스트가 짧아져서 긴 컨텍스트 저하가 줄어드는 것. 압축이 공짜가 아니라 성능 개선 수단일 수 있다는 점.

8. 지연 비용도 측정돼 있음. 헤드가 추가하는 wall time은 전체 생성 시간의 약 15%(p95 34.8%). prefill 재사용이라 헤드 자체는 가벼움. 후속 턴의 토큰 감소로 상쇄됨.

9. 여기서 문제제기. 가장 큰 시사점은 도구 출력이 히스토리에 들어가기 전, 에이전트-환경 경계에서 압축한다는 것임. 기존 컨텍스트 관리(요약, 트렁케이션)는 이미 들어온 정보를 사후 처리함. 그러면 이미 창은 차 있고 비용은 이미 나간 뒤임. 업스트림에서 자르는 게 구조적으로 유리함.

10. 근데 내 환경에 바로 적용하기엔 제약이 있음. hidden state 접근이 필요해서 오픈웨이트 전용. GPT, Claude 같은 클로즈드 모델에는 못 붙임. 백본 바뀔 때마다 헤드 재학습도 필요함(백본은 동결이라 파인튜닝은 아님).

11. 그래도 베낄 수 있는 원칙은 남음. 도구 출력을 통째로 컨텍스트에 넣지 말고 경계에서 한 번 걸러라. 필터 신호는 에이전트가 이미 수행한 연산의 부산물에서 구하라. 외부 장치를 쌓지 말고 내부 표현을 읽어내라 — 에이전트 주변에 부가 장치를 쌓는 대신 이미 형성된 표현을 활용하는 설계 방향.

12. 당장 가능한 저비용 버전도 있음. 도구마다 출력 캡을 두고(예: grep 결과 상위 N줄), 클로즈드 모델이라면 프롬프트로 "이 출력에서 필요한 줄만 추려서 다음 단계에 써라"는 중간 요약 턴을 넣는 것. hidden state만큼 정밀하지 않아도 70% 예산을 먹는 항목이란 사실 자체가 개선 동기가 됨.

13. 결론. 도구 출력이 토큰 예산의 진짜 범인이고, 해답은 에이전트 바깥이 아니라 안에 있었음. 근데 그 안을 들여다보려면 오픈웨이트여야 한다는 현실 제약 — 그래서 클로즈드 모델 사용자는 프롬프트 수준의 필터로 근사하는 수밖에 없다는 것까지가 실무 결론임.

![Figure 1: 기존 방식 vs SWE-Pruner Pro](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-1-p2.png)

![Figure 2: 선형 프로브 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-2-p3.png)

![Figure 3: 전체 파이프라인 개요](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-3-p4.png)

![Figure 4: 헤드 아키텍처 상세](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-4-p5.png)

![Table 1: 읽기 전용 멀티턴 벤치마크 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/table-1-p6.png)

![Table 2: SWE-Bench Verified 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/table-2-p8.png)

![Table 3: 소거 실험 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/table-3-p8.png)
