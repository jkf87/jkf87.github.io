---
title: "LLM 에이전트 스킬은 쌓기만 하면 망한다: 생성·검증·압축·라우팅·보안 16편 재검증"
date: 2026-09-27
author: 한준구(코난쌤)
description: "에이전트 스킬 논문 15편과 DeepMind 발표 1건을 2026-09-27 기준 arXiv 초록·본문으로 다시 확인해 한 편으로 합쳤습니다. 회귀가 이득의 59%를 상쇄한다는 수치부터 압축·라우팅·보안 관리법까지 정리했습니다."
tags: [llm-agent, agent-skills, harness, self-evolution, paper-review]
refactor_hub_id: harness-self-improve-01
aliases:
  - skillos-skill-curation-self-evolving-agents-2026-05-09
  - muse-autoskill-self-evolving-agents-2026-05-28
  - openskill-open-world-self-evolution-llm-agents-2026-06-09
  - 2026-06-18-openskill-open-world-self-evolution
  - posts/dont-ship-skills-without-evals-2026-07-17
  - posts/2026-07-27-regression-tax-skills-help-hurt-llm-agents
  - posts/2026-08-04-skill-alpha-progressive-agent-skill-rl
  - posts/2026-08-05-skill-alpha-progressive-agent-skill-rl
  - posts/2026-08-06-skill-entropy-cross-skill-long-horizon-rl
  - posts/2026-08-11-skillprox-proximal-textual-gradient-agent-skills
  - posts/2026-08-13-skillzip-evaluation-free-skill-compression
  - posts/2026-08-19-demystifying-agent-skills
  - posts/2026-08-24-skill-use-trigger-compliance-boundary
  - posts/skiller-language-level-rl-small-model-skills-2026-08-25
  - posts/2026-08-28-wikiskill-agent-skill-evolution
  - posts/2026-09-05-agentic-skill-policy-steering
  - posts/2026-09-12-cobra-skills-bandit-skill-optimization
  - posts/2026-09-15-gavel-skill-routing-frozen-llm
draft: false
sources_read: "논문 15편(SkillOS·MUSE·OpenSkill·Regression Tax·Skill-α·Skill Entropy·SkillProx·SkillZip·Demystifying·Skill-Use·SKILLER·WikiSkill·SkillShift·COBRA-Skills·Gavel)은 2026-09-27에 arXiv 초록과 HTML 본문을 읽고 수치를 대조했으며, Schmid 발표는 YouTube 영상으로 확인. 저자 코드는 skill-alpha·Skill-Entropy-RL·SkillProx·SKILLER·OpenSkill 저장소 5종을 git ls-remote로 확인, Skill2-Bench는 HuggingFace 공개(논문 명시), 나머지 논문은 공개 코드 없음 또는 확인 대상 아님"
novelty_vs_paper: "각 논문의 기여(회귀 분해, 롤백 보상, 구조 압축, 중간층 라우팅, 정책 조종 등)는 논문 것. 이 글의 생애주기 5단계 프레임, 16편 통합 비교표, 그리고 옛 글 수치 정정 3건(Skill-Use 79/177, Skill-α tau2 55.83, MUSE v2 초록 수치)은 블로그봇의 재검증 결과임"
---

## 한눈에 보는 결론

LLM 에이전트 스킬을 다룬 글 18편을 한 편으로 합쳤습니다. 1차 출처는 논문 15편과 DeepMind 발표 1건이고, OpenSkill과 Skill-α는 같은 논문을 다룬 글이 2편씩 있어 묶었습니다.

모든 핵심 수치를 2026-09-27에 arXiv 초록과 HTML 본문으로 다시 대조했습니다. 옛 글 3건의 수치가 논문과 달라서 바로잡았습니다.

핵심은 이겁니다.

- 스킬을 추가하면 평균은 오릅니다. 근데 <span style="background-color: #fff59d"><strong>이미 풀리던 작업이 무너지는 회귀가 이득의 59%를 상쇄</strong></span>합니다. 5,832회 실행에서 나온 숫자입니다(arXiv 2607.22520).
- 스킬이 작동하는 이유는 <span style="background-color: #fff59d"><strong>절차를 안정화해서</strong></span>입니다. 효과의 65.7%가 절차 앵커링이고 명시적 지식 주입은 4.5%에 그칩니다(arXiv 2608.14036).
- 스킬 사용 능력은 아직 불안정합니다. 79개 공개 스킬·177개 과제 벤치마크에서 <span style="background-color: #fff59d"><strong>최강 조합도 SU 0.613</strong></span>입니다. SU 0.5 미만 스킬은 없을 때보다 성적이 나쁩니다(arXiv 2608.04828).
- 관리가 새 전선입니다. <span style="background-color: #fff59d"><strong>쓰기 시점 압축으로 31.2%를 줄이고</strong></span>(arXiv 2608.11079), <span style="background-color: #fff59d"><strong>얼린 LLM 중간층에서 7.9M 파라미터로 스킬을 골라내고</strong></span>(arXiv 2609.15982), <span style="background-color: #fff59d"><strong>정책 조종 공격은 기존 스캐너 6종이 전부 놓칩니다</strong></span>(arXiv 2609.02564).

| 생애주기 단계 | 대표 방법 | 검증된 수치 | 비용 |
|---|---|---|---|
| 생성 | Skill-α, SKILLER, OpenSkill, MUSE, SkillOS | CL-Bench 10.38(베이스라인 7.30) | 편집마다 롤아웃 2회 |
| 검증·회귀 통제 | Skill-Use, Regression Tax, Demystifying | SU 0.613, 회귀 59% 상쇄, 앵커링 65.7% | 평가 실행 비용 |
| 정리 | SkillZip, SkillProx | 압축 31.2%(롤아웃 0회), 46%→54% | 286초 |
| 선택 | Gavel, Skill Entropy | 트리거 .909, 34.4%→68.4% | 순전파 재사용 |
| 보안 | SkillShift | 타깃 선택률 81.33% | 방어는 행동 감사 |

![스킬 생애주기 5단계와 각 단계 논문 배치](../media/llm-agent-skill-lifecycle-guide-2026/chart-01-skill-lifecycle-map-2026-09-27.png)

## 무엇을 비교했나

합친 글과 각각의 1차 출처입니다.

1. SkillOS 정리 글 — [arXiv 2605.06614](https://arxiv.org/abs/2605.06614). 얼린 executor 옆에서 RL로 훈련된 큐레이터가 스킬 저장소를 insert/update/delete로 다듬는 구조.
2. MUSE-Autoskill 정리 글 — [arXiv 2605.27366](https://arxiv.org/abs/2605.27366). 생성·기억·관리·평가·정제의 스킬 라이프사이클.
3. OpenSkill 정리 글 2편 — [arXiv 2606.06741](https://arxiv.org/abs/2606.06741). 정답 없는 열린 세상에서 지식 수집과 가상 테스트로 스킬을 만드는 방법. [코드](https://github.com/OpenLAIR/OpenSkill).
4. DeepMind 발표 정리 글 — Philipp Schmid, ["Don't Ship Skills Without Evals"](https://www.youtube.com/watch?v=0vphxNt4wyk). eval 없이 배포한 스킬은 자산이 아니라 부채라는 발표.
5. Regression Tax 정리 글 — [arXiv 2607.22520](https://arxiv.org/abs/2607.22520). 스킬 회귀의 세 통로 분해.
6. Skill-α 정리 글 2편 — [arXiv 2608.01678](https://arxiv.org/abs/2608.01678). 편집 단위 생성과 롤백 보상. [코드](https://github.com/ejhshen/skill-alpha).
7. Skill Entropy 정리 글 — [arXiv 2608.05139](https://arxiv.org/abs/2608.05139). 스킬 전환 난이도의 정량화와 훈련법. [코드](https://github.com/Gen-Verse/Skill-Entropy-RL).
8. SkillProx 정리 글 — [arXiv 2608.07449](https://arxiv.org/abs/2608.07449). 재실행 게이트와 leave-one-out 삭제 감사. [코드](https://github.com/Steven011018/SkillProx).
9. SkillZip 정리 글 — [arXiv 2608.11079](https://arxiv.org/abs/2608.11079). 롤아웃 없는 구조 압축.
10. Demystifying 정리 글 — [arXiv 2608.14036](https://arxiv.org/abs/2608.14036). 스킬이 작동하는 메커니즘 분해.
11. Skill-Use 정리 글 — [arXiv 2608.04828](https://arxiv.org/abs/2608.04828). 인식·준수·경계의 3축 벤치마크.
12. SKILLER 정리 글 — [arXiv 2608.10538](https://arxiv.org/abs/2608.10538). 작은 모델용 executor 특화 스킬 생성. [코드](https://github.com/DANG-ai/SKILLER).
13. WikiSkill 정리 글 — [arXiv 2608.27454](https://arxiv.org/abs/2608.27454). 위키 지식층과 함께 진화하는 스킬.
14. SkillShift 정리 글 — [arXiv 2609.02564](https://arxiv.org/abs/2609.02564). 스킬 기반 정책 조종 공격.
15. COBRA-Skills 정리 글 — [arXiv 2609.11682](https://arxiv.org/abs/2609.11682). 컨텍스트 밴딧으로 스킬 최적화 비용 절감.
16. Gavel 정리 글 — [arXiv 2609.15982](https://arxiv.org/abs/2609.15982). 얼린 LLM 중간층에서 스킬 라우팅 신호 읽기.

## 방법 비교

| 방법 | 해결하는 문제 | 핵심 방법 | 검증된 근거(2026-09-27 확인) | 비용 | 확인된 한계 |
|---|---|---|---|---|---|
| SkillOS | 스킬 저장소 수동 큐레이션 한계 | 얼린 executor + RL 큐레이터, GRPO 합성 보상 | 최대 +9.8%, 상호작용 -6.0%. 8B 큐레이터가 Gemini-2.5-Pro executor 단독보다 우수 | 큐레이터 훈련 | 스트리밍 태스크 그룹 가정 |
| MUSE | 스킬을 만들고 끝내는 운영 | 생성-기억-관리-평가-정제 라이프사이클 | 자동 생성 스킬 85.24% vs 인간 작성 81.17%(커버 태스크). Hermes 이식 51.90% | 유닛 테스트 자동 생성 | SkillsBench·SkillLearnBench 중심 |
| OpenSkill | 정답·큐레이션 없는 배포 환경 | 열린 세상 지식 수집 + 가상 테스트 검증 | SkillsBench 최강 폐쇄형 대비 +8.9/+8.8. 검증기가 정답 의도의 88.9% 커버 | 검색·반복 정제 호출 | 검증 앵커 없는 도메인 취약 |
| Schmid 발표 | eval 없는 스킬 배포 | 발동 5개·비발동 5개 + on/off 짝 비교 | SkillsBench 1.1 평균 약 +15%(발표 공개 수치) | 소규모 평가 셋 | 제품 에이전트의 fallback은 eval이 담당 |
| Regression Tax | 평균만 보고 회귀를 놓침 | 이득·회귀 분리 보고, 설명만 넣은 대조 조건 | 5,832회 실행. 회귀 324건이 이득 553건의 59% 상쇄. 회귀의 72.8%가 그라운딩 전위 | 실험 설계 | 오피스 자동화 벤치마크 2종 |
| Skill-α | 스킬의 정답 신호 부재 | Create/Update/Merge/Prune/Noop 편집 + 롤백 보상 | CL-Bench 10.38(최강 베이스라인 7.30). tau2 55.83(SkillPro 49.17). Merge/Prune 제거 시 39.17 | 편집마다 워커 2회 실행 | 검증기·앵커 질문 설계 필요 |
| Skill Entropy | 스킬이 바뀌는 순간의 붕괴 | 전환 난이도를 skill entropy로 정량화, 라벨 예측 RL | Skill2-Bench 558 스킬·9 도메인. 4B 34.4%→68.4%, 1.7B 14.6%→40.1% | 스킬 라벨 필요 | 기준 모델 종속 난이도 |
| SkillProx | 쌓인 스킬의 음수 유틸리티 | 정방향 재실행 게이트 + 역방향 leave-one-out 감사 | 29,129자에서 3.12% 삭제로 정확도 46%→54%. 4B에서 EvoSkill 대비 +14.3pp | 검증 세트 실행 | 감사 주기 운영 비용 |
| SkillZip | append-only 스킬 비대화 | 계약 타입 분해 + 최단 충실 설명(MDL) | 압축률 31.2%, 롤아웃 0회, 286초. 성능 0.577로 상승. 16라운드 증가 2.5~3.7배→1.6~1.9배 | 1회 구조화 추출 | 커버리지가 성능 검증을 대체 |
| Demystifying | 스킬 작동 원리 불명 | 8,135 트라이얼 대조 실행 + 궤적 코딩 | 절차 앵커링 65.7% vs 지식 주입 4.5%. Workflow Memory 대비 +6.06 | 대규모 대조 실험 | 택소노미 라벨링 주관 가능 |
| Skill-Use | 스킬 사용 능력 무측정 | Trigger×(0.7·Compliance+0.3·Boundary) | 79 스킬·177 과제. 최고 SU 0.613(Trigger 0.972, Compliance 0.611). 하네스 바꾸면 순위 역전 | Docker 샌드박스 실행 | 하네스 2종만 비교 |
| SKILLER | 소형 모델용 스킬 부재 | 강한 모델이 critic·actor, 자연어 RL | Qwen3.5-9B +4.3~20.4pp, 4B +1.8~13.3pp. Manus 스킬은 소형 모델에서 역효과 | 초기 생성 비용 집중 | 소형 모델 에이전트 루프 전제 |
| WikiSkill | 교훈의 반복 분석 | Raw·Wiki·Skills 3층, 스킬만 롤백 | 9B+WikiSkill 47.4% > 27B 무스킬 39.4%. 규모별 +12.3/+17.5/+23.9. 위키 어블레이션에서 효과 감소 | 위키 정리 호출 | 도메인별 이동성 편차 |
| SkillShift | 서드파티 스킬 공급망 위험 | 정책 프레이밍·타이브레이킹·예시 조작 | 타깃 선택률 81.33%/63.33%, 유효 출력 100% 유지. 스캐너 6종 전부 탐지 실패 | 공격은 저비용 | 고정 후보 선택 태스크 2종 |
| COBRA-Skills | 스킬 검증 비용 | 컨텍스트 밴딧 우선순위 + 주기적 진화 | SkillOpt 대비 비용 55~58% 감소. 벤치마크당 예제 50개 | 밴딧 보상 이력 필요 | 과제별 편차 존재 |
| Gavel | 스킬 선택 병목 | 얼린 LLM 중간층(64블록 중 45번째) 선형 사영 2개 | 학습 파라미터 7.9M. Skill-Use 트리거 .909로 외부 파이프라인 상회 | 순전파 1회로 스킬 등록 | 오픈웨이트 백본 전제 |

연구 흐름이 표에서 그대로 읽힙니다. 2026년 5월까지는 스킬을 어떻게 만들까가 주제였습니다. 8~9월엔 회귀·압축·선택·보안이 주제입니다. <span style="background-color: #fff59d"><strong>연구 무게중심이 생성에서 운영으로 넘어왔습니다</strong></span>.

## 언제 무엇을 쓰나

![16편에서 직접 확인한 핵심 수치](../media/llm-agent-skill-lifecycle-guide-2026/chart-02-verified-numbers-2026-09-27.png)

- 스킬을 처음 쓴다면 <span style="background-color: #fff59d"><strong>체크리스트 형식으로 쓰세요</strong></span>. 셋업 순서, 도구 호출 순서, 흔한 함정 회피가 효과의 본체입니다(Demystifying).
- 스킬을 추가하기 전에는 <span style="background-color: #fff59d"><strong>on/off 짝 비교를 먼저</strong></span> 돌리세요. 발동되어야 할 프롬프트 5개, 되면 안 되는 프롬프트 5개로 시작하면 됩니다(Schmid 발표).
- 스킬을 만들 때 삭제까지 설계하세요. Create만 남기면 중복·충돌이 쌓여 성능이 무너집니다(Skill-α 제거 실험 39.17). 지울 근거가 부족하면 편집하지 않는 Noop도 정식 선택입니다.
- 스킬 파일이 계속 커지면 쓰기 시점 압축을 round 1부터 넣으세요. 중복은 쌓이고 나서 지우는 비용이 더 큽니다(SkillZip).
- 작은 모델로 실행한다면 강한 모델용 스킬을 그대로 이식하지 마세요. Manus 스킬이 소형 모델에서 기준선보다 낮아진 실측이 있습니다(SKILLER). executor에 맞춘 스킬을 다시 뽑으세요.
- 스킬 수가 수십 개를 넘으면 선택이 병목입니다. 오픈웨이트 백본이라면 중간층 read-out 라우터가 현재 가장 싼 선택입니다(Gavel). 검색 정확도에 과투자하지 마세요. 스킬 풘이 커져도 최종 성공률은 거의 유지됩니다(Demystifying).
- 도메인이 바뀌는 긴 작업에서는 각 단계마다 <span style="background-color: #fff59d"><strong>'지금 필요한 스킬'을 먼저 명시</strong></span>하게 하세요. 전환 비용이 실측된 약점입니다(Skill Entropy).
- 검증 예산이 부족하면 후보 전부를 실행하지 말고 밴딧으로 우선순위를 매기세요(COBRA-Skills).
- 서드파티 스킬을 쓴다면 스킬 로드 전후의 선택 분포를 비교하는 행동 감사를 붙이세요. 정상 출력을 유지하면서 결정만 조종하는 공격이 실증됐습니다(SkillShift).

## 블로그봇이 직접 확인한 것

2026-09-27에 이 머신에서 확인한 내용입니다.

- arXiv 논문 15편의 초록을 전부 불러왔고, 핵심 수치는 HTML 본문까지 대조했습니다. 이 글 표의 숫자는 초록이나 본문에서 직접 확인한 값입니다.
- 저자 코드 저장소 5종을 git ls-remote로 존재 확인했습니다. Skill-α(ejhshen/skill-alpha), Skill-Entropy-RL(Gen-Verse), SkillProx(Steven011018), SKILLER(DANG-ai), OpenSkill(OpenLAIR)입니다. Skill2-Bench 데이터셋은 논문에 HuggingFace 공개가 명시돼 있습니다.
- SkillProx는 옛 글에 arXiv 번호가 없었습니다. 이번에 2608.07449로 확인해서 링크를 붙였습니다.
- Schmid 발표 영상의 제목과 채널을 YouTube에서 확인했습니다.
- 옛 글 수치 3건을 정정했습니다. Skill-Use 옛 글의 '공개 스킬 7,979개·과제 177,177개'는 논문 본문이 79개·177개입니다. Skill-α 옛 글의 'tau2 평균 70.33'은 본문 표가 55.83입니다(최강 베이스라인 SkillPro 49.17). MUSE 옛 글 수치는 v2 초록 기준인 85.24% vs 81.17%(커버 태스크)와 Hermes 이식 51.90%로 바꿨습니다.

## 한계와 반론

- 이 글의 재검증은 초록과 본문 수치 대조까지입니다. 논문 코드를 직접 실행해 재현하지는 못했습니다. Skill-α나 SkillProx의 롤백·감사 루프를 실무에 옮길 때는 직접 돌려보고 판단해야 합니다.
- 인용된 연구 대부분이 SkillsBench·tau2-bench·Terminal-Bench 같은 벤치마크 환경입니다. 실제 운영 환경에서 같은 비율이 유지되는지는 미확인입니다.
- Skill-Use는 79개 스킬·177개 과제 규모고 하네스도 2종만 비교했습니다. Gavel은 백본 순전파에 접근해야 해서 API 전용 모델에는 못 씁니다.
- SkillZip은 압축 후 성능을 롤아웃이 아니라 구조 커버리지로 갈음합니다. 우연한 동시 삭제로 인한 미묘한 하락을 잡는 장치가 약하다는 건 논문이 인정하는 약점입니다.
- 긍정적으로 읽히는 숫자에도 조건이 붙어 있습니다. MUSE의 85.24%는 성공적으로 커버된 부분집합 수치이고, Gavel의 .909는 mini-swe-agent 통합 설정의 값입니다. 조건을 떼고 인용하면 과장이 됩니다.

## 적용 규칙

스킬을 실제로 운영하는 분을 위한 규칙입니다. 이번 재검증에서 확인된 사실만 담았습니다.

1. 스킬 배포에는 발동 프롬프트 5개·비발동 프롬프트 5개, on/off 짝 비교를 기본으로 붙인다. 검증 없이 붙인 스킬은 부채가 된다.
2. 스킬 평가는 이득과 회귀를 분리해서 보고한다. 평균 상승만 보고 배포하면 회귀 59%를 숨긴다.
3. SU 0.5를 못 넘는 스킬은 걷어내거나 병합한다. 부분 준수 스킬은 순이득이 음수다.
4. 스킬은 절차 체크리스트로 쓴다. 지식 주입은 효과의 4.5%에 그친다.
5. 편집 어휘에 Merge·Prune·Noop를 포함한다. 추가만 하는 운영은 실측에서 무너진다.
6. 압축은 쓰기 시점에, round 1부터 넣는다. 쌓인 다음 지우는 비용이 더 크다.
7. executor 모델을 바꾸면 스킬을 다시 검증한다. 강한 모델용 스킬이 소형 모델에서 역효과를 낸 실측이 있다.
8. 서드파티 스킬에는 행동 감사와 반사실 테스트를 붙인다. 출력 검사로는 정책 조종을 못 잡는다.
9. description은 배경 설명이 아니라 행동 지시어로 쓴다. 그 문장은 매 호출마다 토큰 비용을 낸다.

## 참고 자료

- SkillOS — [arXiv 2605.06614](https://arxiv.org/abs/2605.06614)
- MUSE-Autoskill — [arXiv 2605.27366](https://arxiv.org/abs/2605.27366)
- OpenSkill — [arXiv 2606.06741](https://arxiv.org/abs/2606.06741) · [코드](https://github.com/OpenLAIR/OpenSkill)
- Don't Ship Skills Without Evals — [YouTube](https://www.youtube.com/watch?v=0vphxNt4wyk)
- The Regression Tax — [arXiv 2607.22520](https://arxiv.org/abs/2607.22520)
- Skill-α — [arXiv 2608.01678](https://arxiv.org/abs/2608.01678) · [코드](https://github.com/ejhshen/skill-alpha)
- Skill Entropy — [arXiv 2608.05139](https://arxiv.org/abs/2608.05139) · [코드](https://github.com/Gen-Verse/Skill-Entropy-RL)
- SkillProx — [arXiv 2608.07449](https://arxiv.org/abs/2608.07449) · [코드](https://github.com/Steven011018/SkillProx)
- SkillZip — [arXiv 2608.11079](https://arxiv.org/abs/2608.11079)
- Demystifying Agent Skills — [arXiv 2608.14036](https://arxiv.org/abs/2608.14036)
- Skill-Use — [arXiv 2608.04828](https://arxiv.org/abs/2608.04828)
- SKILLER — [arXiv 2608.10538](https://arxiv.org/abs/2608.10538) · [코드](https://github.com/DANG-ai/SKILLER)
- WikiSkill — [arXiv 2608.27454](https://arxiv.org/abs/2608.27454)
- SkillShift — [arXiv 2609.02564](https://arxiv.org/abs/2609.02564)
- COBRA-Skills — [arXiv 2609.11682](https://arxiv.org/abs/2609.11682)
- Gavel — [arXiv 2609.15982](https://arxiv.org/abs/2609.15982)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
