---
title: "HExA — 물리 법칙을 알아도 못 푸는 에이전트, 실험에서 스킬을 배우게 만들기"
date: 2026-08-21
tags: [agent, in-context-rl, skill-bank, LLM, benchmark]
draft: false
---

HExA(Hierarchical Experimentalist Agents, arXiv 2606.29315)는 <span style="background-color: #fff59d"><strong>가중치 업데이트 없이</strong></span>, 에이전트가 직접 실험을 설계·수행하고 그 결과를 <span style="background-color: #fff59d"><strong>자연어 스킬 뱅크로 증류해 재사용</strong></span>하는 프레임워크입니다.

논문의 중간 평가에서 Claude Sonnet 4.6 기준으로 catapult 난이도 성공률 <span style="background-color: #fff59d"><strong>2% → 67.3±9.3%</strong></span>, 에피소드당 평균 반복 횟수는 <span style="background-color: #fff59d"><strong>22.9(ReAct) → 14.4</strong></span>로 줄었습니다.

## 핵심 아이디어

LLM이 물리 법칙을 파라미터에 알고 있다고 해서, 새로운 물리 퍼즐에서 올바른 배치를 바로 찾지는 못합니다. 저자들은 이걸 수치로 보여줍니다. 도구 없이 한 번에 답하는 Direct 조건에서 Claude Sonnet 4.6는 8개 레벨 중 가장 어려운 catapult에서 <span style="background-color: #fff59d"><strong>2% 성공</strong></span>에 그칩니다.

HExA의 접근은 이렇습니다.

1. actor(도구 호출 LLM)가 시뮬레이터를 도구로 쓰면서 개입·실험을 수행합니다.
2. evolver(같은 모델의 다른 프롬프트)가 궤적 배치를 읽고, <span style="background-color: #fff59d"><strong>고보상 궤적과 저보상 궤적을 대조해</strong></span> 자연어 스킬과 실수 기록을 뽑아냅니다.
3. retriever가 스킬 뱅크에서 상위 M개 스킬과 상위 N개 실수 기록을 골라 다음 에피소드 시스템 프롬프트 앞에 붙입니다.

전부 프롬프트 컨텍스트로 동작합니다. <span style="background-color: #fff59d"><strong>파인튜닝도, 오라클 정답도, 오프라인 데이터도 없습니다</strong></span>. 폐쇄형 API 모델에도 그대로 적용할 수 있는 이유입니다.

![](/images/2026-08-21-hexa-experiment-driven-skill-evolution/fig-1-p2.png)

Figure 1. HExA 프레임워크 개요. actor-evolver-retriever 루프가 Interphyre 물리 퍼즐에서 어떻게 도는지 보여줍니다. (원문 Figure 1)

## 스킬 뱅크 구조

스킬 뱅크는 두 컬렉션으로 구성됩니다.

- 스킬: 제목, 원리(2~3문장), 적용 조건, 예시, 유래 seed, 보상 점수로 이루어진 구조화된 레코드
- 실수 기록: 무엇이 틀렸는지(δ), 어떤 잘못된 인과 믿음 때문인지(ρ), 수정 전략(α)의 세 필드

각 스킬에는 `r_k = clamp((r̄_src + 1) / 2, 0.1, 1.0)` 형태의 보상 라벨이 붙습니다. 빠르게 성공한 궤적에서 나온 스킬일수록 점수가 높고, <span style="background-color: #fff59d"><strong>실패 궤적 안의 부분적 정답</strong></span>(메커니즘은 맞았는데 실행이 틀린 경우)도 낮은 점수로 살아남습니다. 뱅크 크기는 상한이 있어서, evolver는 유지/병합/삭제를 강제받습니다.

evolver의 증류는 두 패스로 나뉩니다. 패스 1은 성공 vs 실패를 대조해 전략 스킬 4~6개를 뽑고, 패스 2는 실패 궤적만으로 반복 실수 패턴과 부분 스킬을 추출합니다. <span style="background-color: #fff59d"><strong>성공 궤적만으로는 "어느 중간 단계가 필수였는지"를 알 수 없어서, 실패 분석이 독립된 학습 신호가 된다</strong></span>는 게 저자들의 논점입니다.

![](/images/2026-08-21-hexa-experiment-driven-skill-evolution/fig-2-p4.png)

Figure 2. actor-evolver-retriever 루프로 스킬 뱅크를 만들고 재사용하는 구조. (원문 Figure 2)

## Interphyre 벤치마크

평가 환경 Interphyre는 <span style="background-color: #fff59d"><strong>PHYRE 2D 절차적 물리 환경 위에 tool-calling API를 얹은</strong></span> 벤치마크입니다. 

에이전트는 장면 조회, 개입 배치, 시뮬레이션 실행 API로 가설을 검증합니다. 8개 레벨은 기본 모델 성적으로 두 티어로 나뉘고, Tier 2(pass_the_parcel, catapult)가 주 실험대입니다. 측정은 성공률(50 seed)과 seed당 평균 반복 횟수(미해결은 25턴 상한)입니다.

![](/images/2026-08-21-hexa-experiment-driven-skill-evolution/table-1-p8.png)

Table 1. Direct(도구 없음) 베이스라인의 레벨별 성공률. catapult에서는 모든 모델이 사실상 0에 가깝습니다. (원문 Table 1)

## 결과

catapult에서 Claude Sonnet 4.6 기준 비교입니다.

| 방법 | 성공률 (%) | 평균 반복 |
|---|---|---|
| Direct (도구 없음) | 2.0 | 1.0 |
| ReAct | 8.0 | 22.9 |
| Reflexion (K=2) | 21.3±2.5 | 21.2±0.7 |
| HExA (보상 라벨 없음) | 50.7±9.4 | 16.5±2.7 |
| HExA (Off2On Evolving) | **67.3±9.3** | **14.4±1.8** |

성공률이 오르는 동시에 반복 횟수도 <span style="background-color: #fff59d"><strong>약 37% 줄어듭니다</strong></span>. 누적 스킬이 탐색 비용을 상각해 주기 때문입니다. 

Reflexion의 언어적 성찰이 21.3%에 머무는 것과 비교하면, <span style="background-color: #fff59d"><strong>경험을 명시적·재사용 가능한 뱅크로 바꾸는 게 성찰만으로는 부족하다</strong></span>는 걸 보여줍니다.

![](/images/2026-08-21-hexa-experiment-driven-skill-evolution/fig-5-p10.png)

Figure 5. 보상 유도 스킬 축적이 catapult 성공률에 미치는 영향. (원문 Figure 5)

오픈 웨이트 모델에서도 이득이 있습니다. Qwen-2.5-7B는 down_to_earth 62%→72%, two_body_problem 18%→34%. GPT-OSS-120B는 catapult에서 <span style="background-color: #fff59d"><strong>ReAct 0% → HExA 54%</strong></span>입니다. 프론티어 모델의 사전 지식만으로는 설명되지 않는다는 근거입니다.

## 어블레이션에서 걸리는 지점

설정별 차이가 큽니다. catapult 기준으로 <span style="background-color: #fff59d"><strong>Off2On Evolving 76%, Online 시작 44%, Iterative Replacement 56%</strong></span>. pass_the_parcel에서는 60/58/48입니다. 즉 기존 뱅크를 버리고 매번 새로 증류하면 이전 스킬이 사라져 과적합이 커지고, 웜스타트+점진 진화가 유리합니다.

보상 라벨을 빼면 Qwen-2.5-7B 기준 down_to_earth 64% vs 72%, two_body_problem 26% vs 34%로 내려갑니다. 

catapult에서는 <span style="background-color: #fff59d"><strong>67.3%→50.7%까지 떨어집니다</strong></span>. 다만 보상이 아예 없어도 evolver의 사전 지식만으로 50% 선은 지키는 걸 보면, 환경 보상이 없는 도메인에도 적용 여지는 있습니다.

GRPO(Qwen-2.5-3B, 이진 보상)와 동일 seed 예산에서 비교하면 저데이터 영역에서는 HExA가 앞서지만, <span style="background-color: #fff59d"><strong>학습을 충분히 돌리면 GRPO가 역전합니다</strong></span>(down_to_earth 100% 수렴). 

저자들은 "<span style="background-color: #fff59d"><strong>새 도메인 초기 진전 확보용 in-context 부트스트랩 + 이후 파라미터 RL</strong></span>" 하이브리드를 후속 과제로 제시합니다.

## 스킬 이전

catapult를 한 번도 풀지 않은 상태에서, 쉬운 레벨들에서 진화한 스킬 뱅크를 evolver가 대상 씬에 재접지해서 주입하는 zero-shot 이전만으로 <span style="background-color: #fff59d"><strong>44%까지 갑니다</strong></span>. ReAct 8%, Reflexion 16%, Direct 0%와 비교됩니다. 

이전 프롬프트에는 "<span style="background-color: #fff59d"><strong>대상 좌표를 지어내지 말 것, 원본 스킬 ID로 소급 가능해야 할 것</strong></span>" 같은 제약이 붙어 있어서, 좌표 암기를 차단하고 메커니즘 추상화만 옮겨지도록 설계돼 있습니다.

![](/images/2026-08-21-hexa-experiment-driven-skill-evolution/fig-4-p10.png)

Figure 4. 진화된 스킬 뱅크가 catapult seed 45를 어떻게 풀었는지. ReAct는 25턴 실패, HExA는 6턴 성공. (원문 Figure 4)

## 실제로 풀리는 과정

seed 45 사례에서 HExA는 뱅크의 스킬들을 조합합니다. cat_ev_7_002로 낙하 높이를 기본 y=0.4 대신 y=0.9로 올리고, cat_ev_1_001의 정준 위치 (x=0.5, r=1.5)를 첫 시도로 씁니다. 

천장 충돌로 실패하자 cat_ev_10_008의 폴백 x=0.3을 적용해 다음 시뮬레이션에서 성공합니다. 여기엔 새 추론이 거의 없습니다. <span style="background-color: #fff59d"><strong>뱅크에 조합 가능한 답이 이미 들어 있었기 때문입니다</strong></span>.

## 한계와 내 판단

논문이 밝힌 한계는 세 가지입니다. <span style="background-color: #fff59d"><strong>evolver의 추론 능력이 스킬 품질의 상한이 된다</strong></span>는 점, 현재의 이진 성공+효율 보상이 간결한 성공 기준 없는 도메인으로 바로 안 간다는 점, 그리고 evolver 호출 오버헤드가 매 라운드 추가된다는 점. 상호작용 예산이 커지면 GRPO 같은 경사 기반 RL의 상한을 넘는지는 열린 질문입니다.

제 판단을 붙이면, 이 논문의 실용적 가치는 <span style="background-color: #fff59d"><strong>"실험 → 스킬 뱅크 → 검색 주입" 루프가 모델 교체 없이 폐쇄형 API 위에서도 돈다</strong></span>는 점입니다. 

CLAUDE.md 같은 프로젝트 메모나 에이전트 스킬 파일을 매번 사람이 손으로 쓰는 대신, <span style="background-color: #fff59d"><strong>evolver가 궤적에서 자동 증류하는 구성으로 바꿀 수 있다는 근거</strong></span>가 됩니다. 물리 시뮬레이터라는 깔끔한 성공 기준이 있어서 가능한 결과라는 점은 도메인 옮길 때 직접 검증해야 합니다.

원문: [HExA: Hierarchical Experimentalist Agents (arXiv 2606.29315)](https://arxiv.org/abs/2606.29315)

## 더 실습해보고 싶은 분들께

에이전트 하네스와 스킬 진화를 직접 다뤄보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
