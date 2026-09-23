---
title: "경험을 저장하는 것과 경험으로 나아지는 건 다름 — PAST-Bench가 처음으로 제대로 측정한 것"
date: 2026-08-06
tags:
  - agent
  - self-improvement
  - benchmark
  - personal-agent
  - memory
  - harness
  - LLM
  - evaluation
  - persistence
  - recursive-self-improvement
draft: true
refactor_hub: agent-memory-05
refactor_status: queued
---

에이전트가 이전 세션 경험을 저장하고 다음 세션에서 더 나은 행동을 하는지, 통제된 조건에서 제대로 측정한 벤치마크가 없었음. PAST-Bench가 그걸 처음 한다는 것 자체가 의미임. 26개 시나리오, 204개 에피소드로 같은 작업 패밀리 안에서 경험 저장 기회를 주고 재사용을 검사하는 구조임.

1. 왜 기존 벤치마크로 안 되는가. OSWorld나 AgentBench(다양한 환경에서 에이전트 능력을 종합 측정하는 벤치마크)는 fresh session 원샷 점수만 냄. LongMemEval(장기 대화 기억력을 측정하는 벤치마크) 같은 메모리 벤치마크는 개별 컴포넌트만 격리 테스트함. "경험을 축적하면 실제로 나아지는가"라는 질문에 둘 다 답을 못 함.

2. PAST-Bench의 설계 포인트는 매칭 컨트롤임. persistence를 켜고 끄는 조건을 나눠서, 점수가 올라가도 그게 경험 재사용 때문인지 모델 능력이나 프롬프트 노출 때문인지 분리함. 평가 단위도 작업 하나가 아니라 작업 패밀리 전체 궤적임.

![벤치마크 구조](/images/2026-08-06-past-bench-recursive-self-improvement-personal-agents/fig-1-p1-1.png)

3. 세션 사이에 컨텍스트를 완전히 초기화함. 그래서 이전 에피소드가 다음 에피소드에 영향을 주려면 persistence layer, 즉 메모리 스토어나 스킬 파일, 세션 기록을 통해서만 가능함. cold → learn → evaluation → control 순서로 에피소드가 진행됨.

4. 자가진화를 4개 역량으로 분해함. Memory는 사용자 취향·제약·이전 사례의 저장과 조회. Procedural Reuse는 다단계 기술 절차의 저장과 재실행. Information Gathering은 저장된 정보를 적절한 시점에 능동 검색. Update는 오래된 정보를 새 정보로 교체하고 이전 값 유출을 막는 것임.

5. 결과. 7개 모델과 여러 프레임워크에서 전체 Δ(persistence on-off)가 +0.13~+0.24 범위임. 경험 저장이 실제로 도움이 됨. 근데 여기서부터가 재밌는 부분임.

6. 같은 Δ 값을 가진 에이전트라도 어떤 역량에서 점수가 올랐는지가 다름. GPT-5.4는 Memory와 Update에 고르게, GLM-5.1은 Update에 46% 집중, Kimi K2.6은 Memory에 49% 집중임. nanobot과 Hermes는 둘 다 Δ=+0.13인데 nanobot은 Update 한 곳만 올리고 메커니즘 근거가 약했고(Mech 0.57) Hermes는 4개 역량 모두에서 올림(Mech 0.64)임.

7. 그래서 PAST-Bench는 task score와 mechanism-evidence score를 분리 보고함. 단일 숫자가 같아도 내부 동작이 완전히 다르다는 것. 점수만 보고 개선을 판단하면 무엇이 좋아진 건지 모르게 된다는 교훈임.

8. 논문의 실질 공헌은 진단임. Hermes 에이전트의 실패 패턴을 분석해서 5개 메커니즘으로 떨어뜨림. E1 Plan은 저장된 상태를 안 보고 계획을 세우는 문제, 실행 전 필수 조회로 해결. E2 Render는 stale과 current가 섞이는 문제, typed binding으로 해결. E3 Route는 절차가 텍스트로만 남는 문제, ranked skill 저장으로 해결. E4 Gate는 저장된 증거를 안 찾아보는 문제, 회상 의존 행동 전 검색 강제로 해결. E5 Close는 수정이 다음 세션에 안 감기는 문제, 에피소드 종료 시 동기 flush로 해결함.

![5개 메커니즘](/images/2026-08-06-past-bench-recursive-self-improvement-personal-agents/fig-3-p10-1.png)

9. Hermes+ 적용 결과. Overall Δ가 +0.13→+0.15, Mech은 0.64→0.73. Update 역량에서 가장 크게 개선(+0.12→+0.24)됨.

10. 근데 논문이 정직한 지점. 그 +0.02 전체 개선은 run-to-run variation(±0.04~±0.06)보다 작음. 전체적으로는 만능 개선책이 아니라 진단 도구로서의 가치가 크다는 걸 스스로 밝힘. 이런 보고 태도가 신뢰를 만듦.

![결과](/images/2026-08-06-past-bench-recursive-self-improvement-personal-agents/fig-4-p20-1.png)

11. 실무 채점. 우리 개인 에이전트 운영에 바로 쓸 것임. 첫째, "경험 축적한다"고 말할 때 persistence on/off 비교로 실제 개선분을 측정할 것. 둘째, 개선이 어느 역량에서 왔는지 분해해서 볼 것. 셋째, 5개 실패 메커니즘은 자체 점검 체크리스트로 그대로 쓸 만함. 특히 E5(수정이 다음 세션에 안 감김)와 E4(저장된 증거를 안 찾아봄)는 흔하고 놓치기 쉬운 지점임.

12. 특히 Update 역량의 취약함은 개인 비서 계열 에이전트의 실제 사고 지점임. 사용자 정보가 바뀌었는데 옛 값을 계속 쓰는 건 저장 실패보다 사용자 경험을 더 해침. 오래된 값 유출 방지가 별도 역량으로 측정된다는 설계 자체가 시사적임.

13. 한계. 개인 에이전트 도메인 중심이고 204 에피소드는 크지 않음. 그리고 4개 역량이 자가진화의 전부는 아닐 것임. 그래도 없던 측정 단위를 만든 첫 벤치마크라는 가치는 분명함.

14. 결론. 경험을 저장하는 것과 경험으로부터 개선되는 것은 다른 능력임. 같은 크기의 개선이라도 어떤 경로를 통해 왔는지가 중요하고, 이 분리가 재귀적 자기개선 연구의 다음 단계 전제 조건임.

원문: [arXiv:2608.04003](https://arxiv.org/abs/2608.04003)
