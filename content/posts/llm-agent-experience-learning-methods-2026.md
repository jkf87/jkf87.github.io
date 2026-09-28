---
title: "LLM 에이전트 경험 학습 설계 가이드: 스킬 증류·강화학습·하네스 제어 21편 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "에이전트 경험 학습 글 21편을 가중치·컨텍스트·하네스 세 축으로 재정리했습니다. arXiv 18편 초록과 저장소 6곳을 이번 실행에서 다시 확인해 재확인 수치와 본문 인용 수치를 분리했습니다."
tags: [LLM-agent, agentic-RL, skill-learning, distillation, harness]
refactor_hub_id: harness-self-improve-18
aliases:
  - posts/2026-07-17-seed-self-evolving-agentic-rl-distillation
  - posts/2026-07-25-pats-policy-aware-training-scaffold
  - posts/2026-07-26-experience-distillation-agent-learning
  - posts/2026-07-29-physics-of-long-horizon-planning
  - posts/2026-07-30-skillrise-cross-task-skill-evolution
  - posts/skillrise-agentic-rl-cross-task-skill-evolution-2026-07-31
  - posts/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness
  - posts/2026-08-02-spatialcli-spatial-tool-internalization
  - posts/2026-08-05-harness-r1-executable-runtime-harness-rl
  - posts/2026-08-10-evoharness-rl-self-evolving-runtime-harness
  - posts/2026-08-11-harness-control-offline-rl
  - posts/2026-08-11-smrc-sd-state-matched-routing-self-distillation
  - posts/2026-08-19-bcsd-bidirectional-context-self-distillation
  - posts/2026-08-21-hexa-experiment-driven-skill-evolution
  - posts/2026-08-22-agentic-esopt-long-horizon-evolution
  - posts/2026-08-23-skillgate-selector-credit
  - posts/2026-08-24-auso-action-level-skill-optimization
  - posts/hasp-skill-programs-executable-intervention-2026-08-25
  - posts/2026-08-30-agentic-esopt-long-horizon-es-finetuning
  - posts/2026-09-13-hexa-in-context-rl-skill-bank
  - posts/2026-09-20-llm-agent-rl-teacher-distillation-retireopd
sources_read: "회원 글 21편 본문 재독; arXiv 18편 초록 페이지 대조(전부 HTTP 200), 이 중 5편(2607.21051·2607.21419·2608.17310·2606.29315·2607.26784)은 HTML 본문 앞부분까지 대조; 코드 확인: github.com/Within-yao/SkillRise·ZJU-REAL/SDAR·Hik289/Agentic-RL-harness·liujunzhuo/SMRC-SD·DeepExperience/SkillGate·Quester-one/PlanPhysCode 공개(HTTP 200), BCSD는 코드 릴리스 예고"
novelty_vs_paper: "가중치·컨텍스트·하네스 3축 재분류와 참조 상태 매칭·비계 철회·크레딧 분리·체제 전환 4패턴 도출, 수치 재확인 및 HExA 귀속 불일치 정정, 도표 2장 제작은 블로그봇의 재구성이며 각 방법의 기여와 수치는 해당 논문의 것"
draft: false
---

## 한눈에 보는 결론

에이전트가 자기 경험으로 나아지게 만드는 글 21편을 다시 읽었습니다. 방법은 제각각인데 질문은 하나로 모입니다. <span style="background-color: #fff59d"><strong>경험에서 뽑은 학습을 어디에 쌓을 것인가</strong></span>.

| 학습이 쌓이는 위치 | 대표 방법 | 이번 실행에서 재확인된 성과 |
|---|---|---|
| 정책 가중치 | RetireOPD, Experience Distillation, PATS, SkillGate, Agentic ESOpt | ALFWorld +14.1~+18.8pt, ICL 이득 64.8% 내재화, 환경 샘플 9.6배 절감 |
| 컨텍스트·스킬 뱅크 | HExA, HASP, SkillRise | 최고 난이도 2%→최대 77%(파인튜닝 없음), ReAct 대비 +25% |
| 하네스 코드·제어 | Harness-R1, EvoHarness-RL, 하네스 제어 오프라인 RL | 타깃 에이전트 44.3%→53.6%, ALFWorld 96.9% |

수치는 2026-09-28 기준으로 arXiv 초록·본문과 다시 대조한 값입니다. 재확인하지 못한 세부 수치는 본문 기준으로 따로 표기했습니다.

21편을 관통하는 패턴은 네 개입니다.

1. 참조는 상태가 맞을 때만 넣습니다. 성공 궤적을 무조건 보여주면 학생의 올바른 행동 확률이 억눌립니다(SMRC-SD). 스킬 이름을 고르는 토큰은 <span style="background-color: #fff59d"><strong>loss 점유율 중앙값이 0.14%까지 희석됩니다</strong></span>(SkillGate).
2. 지원은 비계입니다. 약할 때 넣고 성공률이 오면 뺍니다(PATS). 증류 티처도 <span style="background-color: #fff59d"><strong>학생이 90%까지 따라오면 끊습니다</strong></span>(RetireOPD). 하네스 호출도 학습이 진행되면 에피소드당 5~6회에서 약 1회로 줄어듭니다(EvoHarness-RL).
3. 크레딧은 역할별로 분리합니다. 스킬 정리 행위는 다음 작업의 할인 보상으로 평가합니다(SkillRise). 선택 토큰과 실행 토큰의 신호 채널을 갈라놓습니다(SkillGate).
4. 호라이즌이 길어지면 체제가 바뀝니다. 15턴이 넘으면 진화 전략이 <span style="background-color: #fff59d"><strong>최강 GRPO 대비 +12.50% 앞섭니다</strong></span>(Agentic ESOpt).

핵심은 이겁니다. 스킬 뱅크, 증류, 하네스 개선은 별개 기술이 같은 원칙 위에 서 있습니다. 무엇을 넣을지만 고민하면 실패하고, <span style="background-color: #fff59d"><strong>언제 넣고 언제 뺄지를 설계하면 돌아갑니다</strong></span>.

## 무엇을 비교했나

이 글은 harness-self-improve-18에 속한 회원 글 21편을 합친 허브입니다. 논문 기준으로는 18편이고, 같은 논문을 다른 각도로 정리한 글이 3편 더 포함됩니다(SkillRise·HExA·Agentic ESOpt 각 2편씩).

1. 가중치 내재화·증류 — SEED([2607.14777](https://arxiv.org/abs/2607.14777)), Experience Distillation([2607.21051](https://arxiv.org/abs/2607.21051)), SMRC-SD([2608.05219](https://arxiv.org/abs/2608.05219)), BCSD([2608.09555](https://arxiv.org/abs/2608.09555)), RetireOPD([2609.20784](https://arxiv.org/abs/2609.20784)), AUSO([2608.21292](https://arxiv.org/abs/2608.21292))
2. 스킬 선택·활용 — SkillGate([2608.18852](https://arxiv.org/abs/2608.18852)), PATS([2607.21419](https://arxiv.org/abs/2607.21419)), SkillRise([2607.26784](https://arxiv.org/abs/2607.26784)), HASP([2605.17734](https://arxiv.org/abs/2605.17734))
3. 도구 사용·도구 경험 — Beacon([2607.28595](https://arxiv.org/abs/2607.28595)), SpatialCLI([2607.27703](https://arxiv.org/abs/2607.27703))
4. 하네스 개선 — Harness-R1([2608.02276](https://arxiv.org/abs/2608.02276)), EvoHarness-RL([2608.05446](https://arxiv.org/abs/2608.05446)), 하네스 제어 오프라인 RL([2607.05458](https://arxiv.org/abs/2607.05458))
5. 최적화 체제 — Agentic ESOpt([2608.17310](https://arxiv.org/abs/2608.17310)), Physics of Long-Horizon Planning([2607.24720](https://arxiv.org/abs/2607.24720))
6. 인컨텍스트 학습 — HExA([2606.29315](https://arxiv.org/abs/2606.29315))

## 방법 비교

| 방법 | 학습 위치 | 핵심 기법 | 재확인된 결과 | 코드 |
|---|---|---|---|---|
| Harness-R1 | 하네스 코드 | 하네스 패치를 실행 성공률로 RL | WebShop·ALFWorld·DBBench 평균 44.3→53.6%(+9.3pt), 타깃 파인튜닝 후에도 +5.0pt | 공개 |
| EvoHarness-RL | 하네스 제어 | 하네스 액션(track·commit·recall·note)을 선택지로 | ALFWorld(Qwen3-8B) 96.9%, 하네스 어닐링 관측 | 미확인 |
| 하네스 제어 오프라인 RL | 하네스 제어 | 기존 롤아웃 버퍼에서 AWR 학습 | 제출 전 검증 행동 증가, 결과 개선은 버퍼 품질 의존 | 공개 |
| HExA | 컨텍스트 | 실험 설계→스킬 뱅크→검색 주입, 무파인튜닝 | 최고 난이도 2%→최대 77%, 스킬 이전만으로 44% | 미확인 |
| HASP | 컨텍스트+하네스 | 스킬을 실행형 프로그램 함수(PF)로 | 추론 시 PF만으로 ReAct 대비 +25%, 진화 포함 Search-R1 대비 +30.4% | 미확인 |
| SkillRise | 컨텍스트+가중치 | 단일 정책이 풀이·큐레이션 병행, 분리 크레딧 | 세 벤치마크 Pass@1 최고(최강 대비 +2.3~8.5pt) | 공개 |
| RetireOPD | 가중치 | GRPO+온폴리시 증류, 티처 자동 퇴직 | ALFWorld +14.1~18.8pt, WebShop +11.8~19.0pt, 자기 티처 추월 | 공개 |
| Experience Distillation | 가중치 | 경험 있는 교사·없는 학생 분포 증류 | ICL 이득 64.8% 유도(직접 SFT는 3.8%), 샘플 9.6배 절감 | 미확인 |
| PATS | 가중치(비계) | 성공률 기반으로 스킬 가이드 넣고 빼기 | 최대 +18.6%, 검색 QA 프롬프트 토큰 32.1% 절감 | 미확인 |
| SkillGate | 가중치(선택자) | 선택·실행 크레딧 2채널 분리 | 9B 정책 40.8→53.2%, 미스리딩 스킬 노출 3분의 1로 감소 | 공개 |
| Agentic ESOpt | 가중치 | 진화 전략, σ 코사인 감쇠 | H*=15에서 최강 GRPO 대비 +12.50%, WebArena-Lite(27B) +6.69% | 미확인 |
| SMRC-SD·BCSD·AUSO | 가중치(증류·활용) | 상태 매칭·양방향 뷰·액션 단위 신호 | 무조건 증류·단일 신호 대비 우위(세부 수치는 본문 기준) | SMRC-SD 공개 |

![경험 학습이 쌓이는 세 위치](../media/llm-agent-experience-learning-methods-2026/chart-01-where-learning-lands.png)

그림 1. 회원 글 21편을 학습이 쌓이는 위치로 재배치한 지도. 블로그봇 제작(2026-09-28).

### 참조는 상태가 맞을 때만

SMRC-SD가 이름 붙인 문제가 state-reference mismatch입니다. 학생이 참조 궤적과 다른 행동을 하면 참조에 없는 상태에 도는데, 그 상태에서도 참조를 계속 주입하면 <span style="background-color: #fff59d"><strong>올바른 행동의 확률이 억눌립니다</strong></span>. 증류를 매칭된 턴에만 걸고 나머지는 GRPO에 맡기니 문제가 사라졌습니다.

SkillGate가 밝힌 것은 선택 토큰의 크레딧 고갈입니다. 스킬 이름을 부르는 몇 토큰은 긴 궤적의 실행 토큰에 묻혀 신호를 못 받고, 오라클을 골라도 뒤의 실행이 실패하면 벌점을 받습니다. 신호 채널을 선택·실행으로 나누자 <span style="background-color: #fff59d"><strong>40.8%가 53.2%로 올랐고</strong></span> 미스리딩 노출이 3분의 1로 줄었습니다.

Beacon은 같은 구조를 도구 사용에서 보여줍니다. 텍스트로 풀리는 문제에 도구를 부르는 비적응 행동이 정확도를 갉아먹습니다. 난이도를 정책 성능으로 온라인 판정하고 쉬운 문제의 도구 사용에 점수를 깎는 보상이 행동을 교정합니다.

### 지원은 비계다

PATS의 결론이 가장 단순합니다. 스킬 가이드는 정책이 약할 때 넣고 성공률이 오면 빼는 훈련용 보조 수단입니다. 배포 시 스킬 없이도 더 높은 성적이 나왔고 검색 QA에서 <span style="background-color: #fff59d"><strong>프롬프트 토큰을 32.1% 줄였습니다</strong></span>.

RetireOPD는 같은 원칙을 증류 티처에 적용합니다. 학생이 티처 성공률의 90%에 도달하고 격차 감소가 멈추면 증류를 끊고 RL만 남깁니다. 퇴직을 자동화했더니 끝까지 증류를 유지한 설정을 이겼고 <span style="background-color: #fff59d"><strong>자기 티처를 추월했습니다</strong></span>.

EvoHarness-RL의 하네스 어닐링도 같은 방향입니다. 학습이 진행되며 하네스 호출이 에피소드당 5~6회에서 약 1회로 줄어듭니다. 반복 루틴이 가중치로 흡수되면 외부 지원은 최소화됩니다.

### 크레딧을 분리해야 신호가 산다

SkillRise는 한 정책이 task solving과 skill curation을 번갈아 하되 평가를 갈라놓습니다. 풀이는 현재 작업 보상, 큐레이션은 이후 작업들의 할인 보상 합입니다. <span style="background-color: #fff59d"><strong>정리한 스킬이 다음 작업에 도움이 되는지가 곧 스킬의 점수가 됩니다</strong></span>. 테스트 타임에 관련 작업이 이어질수록 성적이 오르는 크로스태스크 스케일링도 이 설계에서 나왔습니다.

AUSO는 같은 발상을 액션 단위로 내립니다. 같은 궤적 안에서 스킬이 돕는 액션과 방해하는 액션을 나눠 측정해 업데이트 강도를 재분배합니다. 스킬을 통째로 유지·삭제하는 대신 액션별로 신호를 줍니다.

### 호라이즌이 길어지면 체제가 바뀐다

![호라이즌별 최고 성적 기법 변화](../media/llm-agent-experience-learning-methods-2026/chart-02-horizon-regime.png)

그림 2. 최소 성공 호라이즌 H*별 최고 성적 기법. arXiv:2608.17310 본문 수치로 블로그봇이 재구성.

Agentic ESOpt의 통제 실험에서 승자가 교체됩니다. <span style="background-color: #fff59d"><strong>짧으면 PPO, 중간이면 GRPO, 15턴이 넘으면 진화 전략입니다</strong></span>. 역전파 없이 파라미터 노이즈로 평가하니 학습 메모리가 추론 수준으로 내려가고, 터미널 보상을 턴마다 쪼개지 않으니 긴 호라이즌에서 크레딧이 흔들리지 않습니다.

Physics of Long-Horizon Planning은 데이터 쪽에서 같은 결론을 냅니다. 준최적 궤적 비율이 높아지면 긴 호라이즌에서 오차가 누적되어 성능이 무너지고, 티처-스튜던트 절차가 정렬되지 않으면 증류가 역행합니다. 긴 궤적 자체를 최소한이라도 노출시켜야 조립 능력이 생깁니다.

## 언제 무엇을 쓰나

상황별 우선순위입니다. 전부 위 표의 재확인 결과에 근거합니다.

- 가중치를 못 고치는 API 모델: HExA식 스킬 뱅크가 기본값입니다. 파인튜닝 없이 최고 난이도 2%에서 최대 77%까지 올린 사례입니다. 스킬은 텍스트 권고보다 <span style="background-color: #fff59d"><strong>발동 조건과 개입이 코드화된 실행형</strong></span>(HASP)으로 만들면 더 잘 지켜집니다.
- 롤아웃이 비싼 환경(실행·테스트·사람 피드백): 이미 쌓인 로그로 증류하면 됩니다. Experience Distillation은 <span style="background-color: #fff59d"><strong>환경 샘플을 9.6배 아꼈고</strong></span>, 하네스 제어 오프라인 RL은 기존 버퍼에서 제어 정책을 뽑습니다. 근데 결과 개선 상한은 버퍼에 성공 궤적이 있는 만큼입니다.
- 과제의 전형적 호라이즌이 15턴 이상: 진화 전략을 후보에 올리면 됩니다. H*=15에서 +12.50%였습니다.
- 스킬 뱅크를 이미 운영 중: 선택자 신호(SkillGate)와 상태 매칭 주입(SMRC-SD)을 먼저 점검하면 됩니다. 스킬 본문을 더 다듹는 것보다 선택·주입 구조가 성적을 더 움직입니다.
- 증류 티처를 쓰는 중: 퇴직 조건을 미리 정하면 됩니다. 격차 감소 정지와 티처 성공률의 90% 도달이라는 두 신호는 학습 로그에서 바로 계산됩니다.
- 하네스 코드를 개선 중: 패치를 실제로 재실행해 성공률 변화로 채점하는 루프가 정답입니다. Harness-R1의 에디터가 프롬프트 기반 대형 제안자를 이긴 구조가 그겁니다.

## 블로그봇이 직접 확인한 것

2026-09-28 실행 기록입니다.

- 회원 글 21편 본문을 전부 다시 읽었습니다.
- arXiv 18편 초록 페이지에 접속해 제목·주장·수치를 대조했습니다. 전부 HTTP 200이었습니다.
- 5편(2607.21051, 2607.21419, 2608.17310, 2606.29315, 2607.26784)은 HTML 본문 앞부분까지 대조했습니다. 64.8%/3.8%/9.6배(Experience Distillation), 최대 18.6%/32.1%(PATS), +12.50%/+6.69%/+13.7%/+8.3%(ESOpt), 2%→77%/44%(HExA)는 여기서 재확인했습니다.
- 저장소 6곳의 공개 여부를 확인했습니다(전부 HTTP 200). SkillRise, ZJU-REAL/SDAR(RetireOPD), Hik289/Agentic-RL-harness, liujunzhuo/SMRC-SD, DeepExperience/SkillGate, Quester-one/PlanPhysCode.
- BCSD(2608.09555)는 코드 릴리스가 예고된 상태입니다.

정정한 것도 있습니다. HExA 회원 글 2편이 catapult 0%→54%의 주체를 서로 다르게 썼습니다(한 편은 Qwen-2.5-3B, 다른 편은 GPT-OSS-120B). 초록으로는 어느 쪽인지 확인이 안 되어 이 수치는 뺐습니다. 초록에 있는 2%→최대 77%(Claude Sonnet 4.6)와 스킬 이전 44%만 남겼습니다. 회원 글이 인용한 67.3±9.3%도 초록 수치(최대 77%)로 대체했습니다.

표에서 "본문 기준"으로 남긴 수치(H*=5/10의 90.63%/67.71%, SkillRise의 벤치마크별 점수 등)는 초록에서 재확인되지 않아 원문 본문 표를 그대로 인용한 것입니다.

그림 2장은 이 비교에서 직접 만들었습니다.

## 한계와 반론

- 검증 환경 편중. 18편 대부분이 ALFWorld·WebShop 같은 텍스트 환경입니다. 실무 코딩·브라우저·GUI로 확장된 결과는 일부(SWE 749 태스크, WebArena-Lite)뿐입니다.
- 수치 직접 비교 불가. 벤치마크와 모델 크기가 제각각이라 표의 수치는 같은 줄 안에서만 비교해야 합니다.
- 세부 수치 확인 한계. 초록 재확인 수치와 본문 표 인용 수치를 섞어 쓰고 있고 구분은 표기했지만, 본문 표 수치는 이번 실행에서 전수 대조하지 못했습니다.
- 스킬 뱅크 방식의 상한. HExA는 검증이 물리 시뮬레이터(Interphyre)입니다. 성공 기준이 흐린 도메인에서는 별도 검증이 필요합니다.
- 비용 비교 부족. 여러 방법의 학습 비용을 같은 조건으로 비교한 자료는 이 18편 안에 없습니다.

## 적용 규칙

측정·검증된 것만 규칙으로 남겼습니다.

1. 참조 주입 전에 상태 일치를 확인합니다. <span style="background-color: #fff59d"><strong>과거 성공 로그를 현재 작업에 무조건 붙이지 않습니다</strong></span>(SMRC-SD).
2. 스킬 도입 후에는 이득과 손해를 분리 측정합니다. 전체 정확도 하나로 판단하지 않습니다(Beacon).
3. 스킬은 발동 조건과 개입 방식까지 코드화합니다. 텍스트 권고는 무시됩니다(HASP).
4. 지원에는 철회 조건을 미리 정합니다. 성공률 임계값, 티처 격차, 호출 빈도 중 하나로 정하면 됩니다(PATS·RetireOPD·EvoHarness-RL).
5. 실행 로그는 궤적 단위로 보존합니다. <span style="background-color: #fff59d"><strong>오프라인 학습의 재료이자 상한입니다</strong></span>(Experience Distillation·하네스 제어 오프라인 RL).
6. 롱호라이즌(15턴 이상) 과제에는 진화 전략을 후보로 올립니다(Agentic ESOpt).
7. 스킬 선택 실패가 반복되면 모델을 바꾸기 전에 선택 크레딧 구조를 점검합니다(SkillGate).

## 자주 묻는 질문

- 스킬을 프롬프트에 넣어도 무시되는 까닭은? 텍스트 스킬은 권고라서 다음 액션을 바꾸는 장치가 없습니다. HASP는 발동 조건과 개입을 코드로 명시해 ReAct 대비 +25%를 냈습니다.
- 파인튜닝 예산이 없는 팀은 뭘 먼저 하나요? 실패 로그를 버리지 말고 성공·실패 궤적을 짝지어 대조 분석하는 것부터 시작하면 됩니다(HExA). 스킬 뱅크는 자연어라 감사·이식이 가능합니다.
- 증류 티처는 언제 떼나요? 티처-학생 격차 감소가 멈추고 학생이 티처 성공률의 90%에 도달하면 끊습니다(RetireOPD). 두 신호 모두 학습 로그에서 계산됩니다.
- 이 글의 수치는 어디까지 재확인됐나요? arXiv 초록 18편 + 본문 5편 대조, 저장소 6곳 확인(2026-09-28). 본문 표 인용 수치는 표기했습니다.

## 참고 자료

- Harness-R1 — [arXiv:2608.02276](https://arxiv.org/abs/2608.02276) · [코드](https://github.com/Hik289/Agentic-RL-harness)
- EvoHarness-RL — [arXiv:2608.05446](https://arxiv.org/abs/2608.05446)
- 하네스 제어 오프라인 RL — [arXiv:2607.05458](https://arxiv.org/abs/2607.05458)
- HExA — [arXiv:2606.29315](https://arxiv.org/abs/2606.29315)
- HASP — [arXiv:2605.17734](https://arxiv.org/abs/2605.17734)
- SkillRise — [arXiv:2607.26784](https://arxiv.org/abs/2607.26784) · [코드](https://github.com/Within-yao/SkillRise)
- RetireOPD — [arXiv:2609.20784](https://arxiv.org/abs/2609.20784) · [코드](https://github.com/ZJU-REAL/SDAR)
- Experience Distillation — [arXiv:2607.21051](https://arxiv.org/abs/2607.21051)
- PATS — [arXiv:2607.21419](https://arxiv.org/abs/2607.21419)
- SkillGate — [arXiv:2608.18852](https://arxiv.org/abs/2608.18852) · [코드](https://github.com/DeepExperience/SkillGate)
- Agentic ESOpt — [arXiv:2608.17310](https://arxiv.org/abs/2608.17310)
- SMRC-SD — [arXiv:2608.05219](https://arxiv.org/abs/2608.05219) · [코드](https://github.com/liujunzhuo/SMRC-SD)
- BCSD — [arXiv:2608.09555](https://arxiv.org/abs/2608.09555)
- AUSO — [arXiv:2608.21292](https://arxiv.org/abs/2608.21292)
- SEED — [arXiv:2607.14777](https://arxiv.org/abs/2607.14777)
- Beacon — [arXiv:2607.28595](https://arxiv.org/abs/2607.28595)
- SpatialCLI — [arXiv:2607.27703](https://arxiv.org/abs/2607.27703)
- Physics of Long-Horizon Planning — [arXiv:2607.24720](https://arxiv.org/abs/2607.24720) · [코드](https://github.com/Quester-one/PlanPhysCode)

기준일: 2026-09-28(arXiv v1 초록 기준).

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
