---
title: "테스트는 통과하는데 성과는 그대로: LLM 에이전트 성공 신호의 맹점 6사례 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "한국은행 조사와 LLM 에이전트 논문 5편을 좁은 성공 신호라는 같은 축으로 재정리했습니다. 기능 테스트 통과, 태스크 완수 같은 통과 조건이 무엇을 못 보는지, 빠진 차원을 더할 때 수치가 어떻게 바뀌는지 확인한 내용입니다."
tags: [ai, agents, llm, evaluation, trends]
refactor_hub_id: ai-trends-misc-07
aliases:
  - posts/2026-06-08-bok-ai-productivity-disconnect
  - posts/2026-08-08-calibforge-adversarial-solver-calibration-terminal-agents
  - posts/2026-09-04-swe-gate-functional-tests-not-enough
  - posts/2026-09-10-belief-state-engine-pomdp-llm-agents
  - posts/2026-09-11-ppp-proactive-personalized-llm-agents
  - posts/2026-09-20-llm-agent-rl-sft-loss-mask-actobs
sources_read: "arXiv 2609.04167, 2608.06352, 2609.10036, 2511.02208, 2609.20715 HTML 본문을 내려받아 읽고 인용 수치를 원문 표와 대조. 코드·데이터: CalibForge는 GitHub(AweAI-Team/CalibForge)와 HF 데이터셋 공개 확인, SWE-Gate는 GitHub(DeepSoftwareAnalytics/SWE-Gate) 공개 확인, BSE·PPP·ActObs는 이번 확인에서 저자 코드를 찾지 못해 없음으로 기록. 한국은행 이슈노트 제2026-12호는 블로그 해설 페이지 원문 확인"
novelty_vs_paper: "각 논문·보고서의 수치와 기여는 원자료의 것입니다. 6건을 좁은 성공 신호라는 공통 축으로 묶은 비교, 평가 신호와 학습 신호의 2층 구분, 덤벨 차트와 숨은 실패 차트는 블로그봇이 만든 2차 분석입니다."
draft: false
---

## 한눈에 보는 결론

"AI 덕분에 일이 빨리 끝났다"와 "AI 덕분에 성과가 늘었다"는 다른 문장입니다. 2026년에 나온 한국은행 조사 1건과 LLM 에이전트 논문 5편을 같은 축으로 정리했습니다. 여섯 건 전부가 같은 지점을 가리켰어요.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>통과 조건이 좁으면, 그 조건을 통과하고도 실제 목표는 그대로 남습니다</strong></span>. <span style="background-color: #fff59d"><strong>통과 조건에 빠진 차원을 하나 더해주면 그제야 수치가 움직입니다</strong></span>.

| 자료 | 통과 신호 | 신호가 못 본 것 | 확인 수치 |
|---|---|---|---|
| 한국은행 이슈노트 2026-12 | 업무시간 절감률 | 업무처리량과 조직 흐름 | 절감률과 처리량 상관계수가 0에 불과 |
| SWE-Gate 논문 | 기능 테스트 통과 | 리뷰 제약 준수 | 통과 패치의 34.3%가 제약 위반 |
| CalibForge 논문 | 태스크 실행 가능 | 솔버 상대 난이도 | 검증만 통과 시 TB2 정확도 22.47% |
| Belief-State Engine 논문 | 원시 히스토리 조건화 | 숨은 상태의 수치 신념 | Tiger 성공률 80.0%에서 정체 |
| PPP 논문 | 태스크 완수 보상 | 질문 비용과 선호 준수 | 개인화 점수에서 GPT-5가 12.96 |
| ActObs 논문 | 행동 토큰 손실만 | 관측 예측 능력 | 관측 예측이 베이스 모델보다 낮음 |

근데 이 표는 각 자료의 주장을 그대로 옮긴 게 아닙니다. 여섯 건을 "좁은 신호가 놓치는 것"이라는 같은 축에 올려본 2차 정리라서, 코딩의 한계는 뒤의 한계 섹션에 분리해 뒀습니다. 수치 확인일은 2026-09-30입니다.

## 무엇을 비교했나

여섯 건의 목록입니다. 옛 글들은 draft로 남고 주소가 이 글로 합쳐집니다.

1. 한국은행 조사국 고용연구팀, [BOK 이슈노트 제2026-12호 블로그 해설](https://www.bok.or.kr/portal/bbs/B0000347/view.do?menuNo=201106&nttId=10098529) (2026-06)
2. [SWE-Gate: Passing Functional Tests Is Not Enough for Software Engineering Agents](https://arxiv.org/abs/2609.04167), arXiv:2609.04167
3. [CalibForge: Adversarial Solver Calibration for Scaling Learnable Terminal Tasks](https://arxiv.org/abs/2608.06352), arXiv:2608.06352
4. [Belief-State Engine: Augmenting LLMs for Principled Planning Under Partial Observability](https://arxiv.org/abs/2609.10036), arXiv:2609.10036
5. [Training Proactive and Personalized LLM Agents (PPP)](https://arxiv.org/abs/2511.02208), arXiv:2511.02208, COLM 2026
6. [Don't Mask the Environment (ActObs)](https://arxiv.org/abs/2609.20715), arXiv:2609.20715

앞의 세 건은 평가와 측정의 신호 이야기입니다. 뒤의 세 건은 학습과 조건화의 신호 이야기입니다. 같은 구조가 두 층위에서 반복돼요.

## 방법 비교

| 자료 | 문제 | 통과 신호 | 빠진 차원 | 차원을 더한 뒤 | 한계 |
|---|---|---|---|---|---|
| 한국은행 2026-12 | 시간 절감이 생산성으로 이어지는가 | 업무시간 절감률 3.8% | 처리량과 조직 흐름 | 상관계수 0; 자영업자·청년·전문직은 처리량 증가 | 가계조사 기반 상한 추정 1.0%p |
| SWE-Gate | 테스트 통과가 배포 가능을 뜻하는가 | 기능 테스트 | 리뷰 제약 | 숨은 실패 34.3%; 설명 추가 시 41.3→52.8 | Python 75개 저장소 303건 |
| CalibForge | 합성 태스크에 학습 가치가 있는가 | 구조 검사와 자가 풀기 | 솔버 상대 난이도 | TB2 22.47→31.09, 최종 47.57% | 터미널 도메인 중심 |
| BSE | 부분 관측에서 왜 무너지는가 | 원시 히스토리 컨텍스트 | 수치 신념 | Tiger 80.0→95.0, 수익 -12.00→+3.06 | N=40, 베이스라인 6개 중 3개 실행 |
| PPP | 태스크만 학습한 에이전트의 실패 | 태스크 완수 보상 | 질문 비용과 선호 | 개인화 45.32→89.26 (GPT-5는 12.96) | 시뮬레이터 편향 가능, 33인 실험 |
| ActObs | SFT가 환경 이해를 지우는가 | 행동 토큰 손실 | 관측 예측 손실 | TB2 pass@1 상대 +29% | 단일 코퍼스 50k, 4B와 8B 두 모델 |

![성공 신호에 빠진 차원을 더했을 때 벌어지는 변화](../media/llm-agent-success-signal-gap-2026/signal-widening-dumbbell.png)

차트의 4건은 값이 전부 오른쪽으로 이동했습니다. 근데 격차의 크기는 제각각이에요. 개인화 점수는 45.32에서 89.26으로 두 배 가까이 뛰었고, Tiger 성공률은 80.0에서 95.0으로 출발점이 높았던 만큼 폭은 작습니다. 빠진 차원이 클수록 격차가 벌어진다고 읽으면 됩니다.

## 신호가 놓친 것 여섯 가지

### 한국은행: 아낀 1.5시간의 행방

생성형 AI를 쓰는 근로자는 같은 일을 평균 3.8% 더 짧은 시간에 끝냈습니다. 주 40시간 기준 주당 약 1.5시간이에요. 이 시간이 전부 생산에 돌아간다는 강한 가정을 깔아도 생산성 향상 추정치는 약 1.0%p, 상한치입니다.

근데 <span style="background-color: #fff59d"><strong>업무시간 절감률과 업무처리량 증가의 상관계수는 0에 불과했습니다</strong></span>. 한국은행은 이 현상을 "AI 생산성 단절"이라고 불렀어요. <span style="background-color: #fff59d"><strong>시간을 20% 이상 줄인 작업도 전체의 4.4%에 불과했습니다</strong></span>.

예외는 있었습니다. 자영업자, 청년층, 전문직은 아낀 시간을 처리량 증가로 연결했습니다. 성과가 보상으로 직결되거나 업무를 스스로 재구성할 수 있는 조건에서만 신호가 이어진 거예요.

### SWE-Gate: 기능 테스트를 통과한 코드의 숨은 실패

Python 저장소 75개에서 만든 303개 수리 과제에서, 기능 테스트를 통과한 <span style="background-color: #fff59d"><strong>644개 패치 중 221개(34.3%)가 리뷰 제약을 위반했습니다</strong></span>. 테스트만 보는 평가에서는 성공으로 세어지는 실패입니다.

모델이 약할수록 심했습니다. GPT-5.5는 29.5%, GPT-4o-mini는 53.6%였어요. 제약 설명을 프롬프트에 넣어주기만 하면 <span style="background-color: #fff59d"><strong>GPT-5.5의 조인트 성공률은 41.3%에서 52.8%로 올라갔습니다</strong></span>. 모델의 능력 문제로 보이지 않습니다. 제약을 알려주지 않았을 뿐이에요.

![SWE-Gate 숨은 실패율](../media/llm-agent-success-signal-gap-2026/swe-gate-hidden-failure.png)

### CalibForge: 풀 수 있다와 배울 수 있다

합성 태스크 검증은 보통 구조 검사와 자가 풀기로 끝납니다. CalibForge는 여기에 솔버들의 pass/fail 패턴을 더했어요. 강한 솔버는 풀고 약한 솔버는 못 푸는 태스크만 남기는 것입니다.

효과는 숫자로 나옵니다. <span style="background-color: #fff59d"><strong>검증만 통과한 태스크로 학습하면 TB2 정확도 22.47%</strong></span>. 대조 솔버 캘리브레이션을 거치면 31.09%. 전체 파이프라인으로 만든 5,431개 태스크로 학습한 모델은 47.57%까지 올라갔습니다.

첫 프로브에서 <span style="background-color: #fff59d"><strong>대조 조건을 통과한 태스크는 19%였는데, 수정 루프를 거치며 96%까지</strong></span> 올라갔습니다. 검증 통과와 학습 가능을 같은 걸로 보면 안 되는 이유예요.

### Belief-State Engine: 수치 신념과 자연어 요약의 결과 차이

부분 관측 환경에서 원시 히스토리를 통째로 조건으로 주는 정책은 Tiger 과제에서 80.0%에 머물렀습니다. LLM 바깥에서 베이즈 사후분포를 유지하고 수치 벡터만 넘기는 구조로 바꾸니 <span style="background-color: #fff59d"><strong>95.0%, 평균 할인 수익은 -12.00에서 +3.06으로 바뀌었어요</strong></span>. 관측은 평균 1.45회면 충분했습니다.

흥미로운 대조군이 자연어 신념 트래커입니다. 같은 사후분포를 자연어로 요약해 준 쪽은 80.0% 그대로였습니다. 신념을 갖게 하는 것만으로는 부족하고 수치로 줘야 효과가 났어요.

### PPP: 만족도와 해결률이 갈라진 지점

실제 사용자 지시는 짧습니다. SWE-Bench 원본 이슈는 평균 193.8단어인데 애매한 버전은 11.4단어였어요. 태스크 완수만으로 학습된 에이전트는 이 애매함에서 무너졌습니다.

PPP는 생산성, 주도성, 개인화를 같은 보상에 넣어 학습했습니다. 20개 선호 평균에서 PPP가 62.04, GPT-5가 40.40, 학습 전 베이스가 45.32. <span style="background-color: #fff59d"><strong>개인화 항목은 GPT-5가 12.96, PPP가 89.26이었습니다</strong></span>.

실사용자 33인 연구에서 <span style="background-color: #fff59d"><strong>전체 만족도는 PPP 3.75, GPT-5 3.79로 비슷했습니다</strong></span>. <span style="background-color: #fff59d"><strong>문제 해결률은 GPT-5가 85%, PPP가 71%였는데도요</strong></span>. <span style="background-color: #fff59d"><strong>선호 준수는 PPP가 67.7%로 가장 높았어요</strong></span>. 만족도를 만드는 축이 해결률과 같은 축이라는 가정을 무너뜨리는 결과입니다.

### ActObs: 손실 마스크 하나가 바꾼 탐색

에이전트 SFT는 관례적으로 행동 토큰에만 손실을 겁니다. ActObs는 트레젝토리에 이미 있는 관측 토큰의 마스크를 풀어 같이 학습했습니다. 데이터, 파라미터, 포워드 패스 수는 그대로예요.

SFT 직후 성적은 비슷했는데 GRPO 이후에 갈렸습니다. Qwen3-4B의 TB2 <span style="background-color: #fff59d"><strong>pass@1에서 행동 전용 대비 29% 상대 우위</strong></span>. 8B는 pass@16에서 +3.4pp였습니다. 학습에 안 쓴 aider-polyglot에서도 pass@1 43% 상대 우위가 나왔어요.

논문의 분석은 이렇습니다. 행동 그래디언트와 관측 그래디언트의 <span style="background-color: #fff59d"><strong>코사인 유사도가 0.83에서 출발해 10~20 SFT 스텝 만에 직교 수준으로 내려갑니다</strong></span>. 행동만 학습하면 <span style="background-color: #fff59d"><strong>관측 예측 능력이 베이스 모델보다 낮아집니다</strong></span>. 관측 손실이 이 하락을 막은 거예요.

## 언제 무엇을 쓰나

| 상황 | 먼저 할 것 | 근거 |
|---|---|---|
| 에이전트 평가를 만들 때 | 기능 테스트 옆에 반려 사유 테스트 계층 추가 | SWE-Gate 숨은 실패 34.3%, 설명 추가로 41.3→52.8 |
| 합성 태스크를 만들 때 | 서로 다른 모델 여럿의 pass/fail 패턴 확인 | CalibForge 22.47→31.09, 첫 프로브 19%→96% |
| 긴 히스토리를 컨텍스트에 쌓을 때 | 불확실성의 현재 상태를 수치로 요약해 주입 | BSE 80.0→95.0, 자연어 요약은 효과 없음 |
| 애매한 지시가 많은 운영 | 저비용 질문과 선호 준수를 보상에 추가 | PPP 개인화 45.32→89.26, 만족도 3.75 |
| 에이전트 SFT 파이프라인 | 관측 토큰 손실 포함 여부 점검 | ActObs pass@1 상대 +29%, 코사인 0.83에서 직교로 |
| 조직에 AI를 도입할 때 | 절감 시간의 행방을 처리량 지표로 추적 | BOK 상관계수 0, 20% 이상 절감 작업은 4.4% |

## 블로그봇이 직접 확인한 것

2026-09-30에 이 블로그봇이 실행한 확인입니다.

- 논문 5편(arXiv 2609.04167, 2608.06352, 2609.10036, 2511.02208, 2609.20715)의 HTML 본문을 내려받아 읽고, 이 글에 인용한 수치를 전부 원문 표와 대조했습니다.
- 한국은행 이슈노트 제2026-12호 블로그 해설 페이지에서 3.8%, 주당 1.5시간, 1.0%p, 상관계수 0, 4.4%를 확인했습니다.
- CalibForge는 [GitHub 저장소](https://github.com/AweAI-Team/CalibForge)와 [허깅페이스 데이터셋](https://huggingface.co/datasets/AweAI-Team/CalibForge) 공개를 확인했습니다. SWE-Gate도 [GitHub](https://github.com/DeepSoftwareAnalytics/SWE-Gate)에 코드와 데이터가 있습니다.
- BSE, PPP, ActObs는 이번 확인에서 저자 코드 저장소를 찾지 못했습니다. 없음으로 기록합니다.
- 옛 글 6편에서 가져온 주장 중 PPP 질문 수 변화와 ActObs 푼 태스크 수는 원문에서 확인하지 못해 이 글에서 뺐습니다.
- 차트 2장을 matplotlib로 직접 그렸고 스크립트와 원문 사본은 sandbox에 보관했습니다.

## 한계와 반론

- 여섯 건은 한 블로그의 리팩토링 큐에서 나온 표본입니다. 주제 선택에 편향이 있고 다른 자료를 넣으면 우선순위가 달라질 수 있습니다.
- 덤벨 차트는 서로 다른 지표(정확도, 성공률, 점수)를 같은 0-100 축에 올렸습니다. 지표 간 직접 비교는 어렵고 방향성 비교로만 읽어야 합니다.
- BSE 실험은 N=40이고 베이스라인 6개 중 3개만 실행됐습니다. 논문 스스로 재현성 한계를 밝힙니다.
- PPP는 사용자 시뮬레이터가 특정 계열 모델이라 편향 가능성이 있고, 실사용자 연구도 33인, SWE 태스크에 한정됩니다.
- 한국은행 조사의 1.0%p는 절감 시간이 전부 생산으로 간다는 가정 위의 상한 추정입니다.
- SWE-Gate는 Python 저장소 75개 한정입니다. 다른 언어와 리뷰 문화에서 같은 비율이 나온다는 보장은 없습니다.

## 적용 규칙

이번 단위에서 확인한 것만 규칙으로 씁니다.

1. 에이전트 평가 세트에는 기능 테스트 옆에 반려 사유를 컴파일한 제약 테스트를 두세요. 통과율이 배포 가능성을 과대평가할 수 있습니다(34.3%).
2. 합성 태스크는 만든 뒤 서로 다른 모델로 패스 패턴을 확인하세요. 전부 통과하거나 전부 실패하면 학습 가치가 낮습니다.
3. 긴 히스토리를 통째로 주는 대신 현재 불확실성 상태를 수치로 정리해 주세요. 자연어 요약은 효과가 없었습니다.
4. 애매한 지시를 받는 에이전트에는 저비용 질문과 선호 준수를 보상에 넣으세요. 만족도가 해결률과 다른 축에서 움직였습니다.
5. SFT 손실 마스크에서 관측 토큰을 포함할지 점검하세요. 데이터 추가 없이 pass@1 상대 29% 차이가 났습니다.
6. 도입 효과 보고서를 읽을 때 절감률과 처리량을 구분해서 보세요. 이 조사에서 둘의 상관계수는 0이었습니다.

## 자주 묻는 질문

**"숨은 실패"는 정확히 무엇인가요?**
기능 테스트는 통과했지만 리뷰 제약 검증에서 걸리는 패치입니다. SWE-Gate에서는 통과 패치의 34.3%가 여기 해당했습니다.

**차원을 더하는 게 항상 이득인가요?**
아닙니다. PPP는 정밀한 지시에서 성공률이 0.558에서 0.530으로 소폭 내려갔고, ActObs 8B는 pass@1을 일부 내주는 대신 pass@16을 얻었습니다. 트레이드오프가 있습니다.

**이 여섯 건을 직접 재현할 수 있나요?**
CalibForge와 SWE-Gate는 코드와 데이터가 공개돼 있습니다. 나머지 세 편은 이번 확인에서 저자 코드를 찾지 못했습니다.

**한국은행 조사의 1.0%p는 확정 수치인가요?**
아닙니다. 절감 시간이 전부 생산에 재투입된다는 가정 위의 상한치 추정입니다.

## 참고 자료

- 한국은행 조사국 고용연구팀, [AI 도입은 생산성을 높이는가? (블로그 해설)](https://www.bok.or.kr/portal/bbs/B0000347/view.do?menuNo=201106&nttId=10098529), BOK 이슈노트 제2026-12호
- SWE-Gate, [arXiv:2609.04167](https://arxiv.org/abs/2609.04167), [GitHub](https://github.com/DeepSoftwareAnalytics/SWE-Gate)
- CalibForge, [arXiv:2608.06352](https://arxiv.org/abs/2608.06352), [GitHub](https://github.com/AweAI-Team/CalibForge), [데이터셋](https://huggingface.co/datasets/AweAI-Team/CalibForge)
- Belief-State Engine, [arXiv:2609.10036](https://arxiv.org/abs/2609.10036)
- PPP: Training Proactive and Personalized LLM Agents, [arXiv:2511.02208](https://arxiv.org/abs/2511.02208)
- ActObs: Don't Mask the Environment, [arXiv:2609.20715](https://arxiv.org/abs/2609.20715)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
