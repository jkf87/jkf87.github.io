---
title: "LLM 에이전트 메모리 설계 기준 정리: 규칙 저장·단서 주입·권한·속도, 2026 논문 8편 비교"
date: 2026-09-26
author: 한준구(코난쌤)
description: "LLM 에이전트 장기 메모리 논문 8편을 비교해 2026년 설계 기준을 정리했습니다. 규칙 저장, 단서 기반 주입, 검색 피드백 재편, 권한 통치, 고속 제어까지 실무 선택 기준을 담았습니다."
tags:
  - LLM 에이전트
  - 메모리
  - 벤치마크
  - 에이전트 설계
refactor_hub_id: agent-memory-04
aliases:
  - agent-memory-systems-survey-2026-05-24
  - posts/agent-memory-systems-survey-2026-05-24
  - gatemem-shared-memory-agent-governance-2026-06-23
  - posts/cue-anchored-working-memory-harness-2026-07-28
  - posts/2026-09-06-rulemem-rule-memory-long-term-conversation
  - posts/2026-09-19-llm-agent-memory-reconsolidation-realm
  - posts/2026-09-22-llm-agent-memory-benchmark-memgym
  - posts/2026-09-23-agent-memory-multi-party-speakermem-r1
  - posts/2026-09-23-agent-memory-system1-fast-control-jevmem
draft: false
---

## 한눈에 보는 결론

2026년에 나온 에이전트 메모리 논문 8편을 겹쳐 읽었습니다. 관심이 "얼마나 잘 기억하나"라는 질문에서 다른 질문들로 이동했더군요. <span style="background-color: #fff59d"><strong>다섯 갈래로 정리됩니다</strong></span>.

| 설계 질문 | 대표 연구 | 초록으로 확인된 수치 |
|---|---|---|
| 기억을 어떻게 전달하나 | Delivery, Not Storage (arXiv 2607.20972) | 기억 도구를 줘도 114턴 동안 자발적 호출 0회 |
| 무엇을 저장하나 | RuleMem (arXiv 2609.03915) | LoCoMo 14개 baseline 평균 대비 +27.47점 |
| 쓸 때마다 다시 쓰나 | REALM (arXiv 2609.16053) | LoCoMo 75.97%, 최강 baseline 대비 +7.17p |
| 누구에게 말해도 되나 | GateMem (arXiv 2606.18829) | 유용성·접근통제·능동적 잊음을 동시에 통과한 방법 없음 |
| 얼마나 빠르고 싸게 되나 | Jev-Mem (arXiv 2609.23986) | LoCoMo 0.777, 빌드 158초(6.6배 빠름), 쿼리 지연 0.93초 |

평가 쪽도 바뀌었습니다. MemGym(arXiv 2605.20833)은 코딩·웹 조작·도구 대화·딥리서치에서 <span style="background-color: #fff59d"><strong>메모리 효과를 추론 능력과 분리해서 측정합니다</strong></span>. SpeakerMem-R1(arXiv 2609.26780)은 다자간 대화에서 누가 무슨 말을 했는지부터 문제를 다시 세웠구요.

실무 결론부터 드리면 이렇습니다. <span style="background-color: #fff59d"><strong>벤치마크 점수를 올리는 단계는 지나갔습니다</strong></span>. 저장 단위(사실에서 규칙으로), 전달 경로(검색에서 주입으로), 갱신 시점(입력에서 검색 피드백으로), 권한(개인에서 공유로), 제어 비용(LLM 생성에서 경량 예측으로)을 설계하는 단계로 넘어왔습니다.

근데 주의할 게 있습니다. 아래 표의 점수는 논문마다 <span style="background-color: #fff59d"><strong>평가 설정이 달라서 서로 직접 비교하면 안 됩니다</strong></span>. 평가 모델이 다르면 점수 비교가 불가능하다는 건 서베이 쪽에서도 지적된 문제입니다.

## 무엇을 비교했나

1. 에이전트 메모리 시스템 서베이 정리(본 블로그 회원 글 2편, 2026-05-24) — 검색·그래프·계층형·파라메트릭 분류와 코딩 도구 4종의 설계 수렴을 다룬 글입니다.
2. [Delivery, Not Storage: Cue-Anchored Working Memory as a Harness Property for Coding Agents](https://arxiv.org/abs/2607.20972) — 코딩 에이전트의 기억 전달 문제.
3. [RuleMem: Active Rule Memory for Long-Term Conversational Agents](https://arxiv.org/abs/2609.03915) — 규칙 기반 메모리.
4. [REALM: Retrieval-Driven Memory Reconsolidation for Long-Term LLM Agents](https://arxiv.org/abs/2609.16053) — 검색 피드백 기반 기억 재통합.
5. [MemGym: a Long-Horizon Memory Environment for LLM Agents](https://arxiv.org/abs/2605.20833) — 실행 중 메모리 측정 벤치마크.
6. [SpeakerMem-R1: Speaker-Centered Dual-Track Memory for Multi-Party Dialogue](https://arxiv.org/abs/2609.26780) — 다자간 대화 메모리.
7. [Jev-Mem: System-One-Controlled Agentic Memory for Efficient AI Agents](https://arxiv.org/abs/2609.23986) — 고속 경량 메모리 제어.
8. [GateMem: Benchmarking Memory Governance in Multi-Principal Shared-Memory Agents](https://arxiv.org/abs/2606.18829) — 공유 메모리 권한 평가.

기준 벤치마크는 [LoCoMo (arXiv 2402.17753)](https://arxiv.org/abs/2402.17753)와 [LongMemEval (arXiv 2410.10813)](https://arxiv.org/abs/2410.10813) 두 개입니다. LoCoMo는 <span style="background-color: #fff59d"><strong>평균 300턴·9K 토큰·최대 35세션의 초장기 대화</strong></span>, LongMemEval은 500개 문항으로 정보 추출·다중 세션 추론·시간 추론·지식 갱신·기권 다섯 능력을 봅니다.

## 방법 비교

| 연구 | 푸는 문제 | 핵심 설계 | 평가·데이터 | 대표 결과 | 남은 한계 |
|---|---|---|---|---|---|
| 서베이(2026-05) | 분야 전체 지도 | 검색·그래프·계층·파라메트릭 분류 | LoCoMo·LongMemEval 리뷰 | 코딩 도구 4종이 정적 지침+생성 메모리 2계층으로 수렴(회원 글) | 시간 추론이 공통 약점 |
| Delivery(2026-07) | 에이전트가 기억 도구를 안 씀 | path·symbol·semantic·event·temporal 트리거를 하네스가 결정론적으로 주입 | 실제 코딩 과제 통제 실험 | 자발적 호출 0회/114턴, 주입은 매번 전달·오탐 0, 138회 컴팩션 생존 | 단일 코퍼스·단일 작업 계열 |
| RuleMem(2026-09) | 질문과 증거가 어휘적으로 먼 경우 | 대화에서 자연어 Horn 절 규칙 유도 + RPC(perplexity 일관성) 검증 | LoCoMo, 14개 baseline | 평균 대비 +27.47점(상대 54.3% 향상) | 도메인 지식 QA 일반화 미검증 |
| REALM(2026-09) | 검색이 기억 구조를 바꾸지 못함 | 이종 인지 그래프 자율 구성 + 검색 피드백 재통합 | LoCoMo, LongMemEval | 75.97% / 65.11% (각각 +7.17p, +1.31p) | 재통합용 LLM 호출 추가 비용 |
| MemGym(2026-05) | 메모리 효과와 추론 능력이 뒤엉킴 | 5개 트랙을 하나의 메모리–추론 인터페이스 뒤에 두고 memory-isolated 점수 보고 | τ²-bench, SWE-Gym, WebArena-Infinity, DR, CODE QA | 코딩 Δ0.0pp, 도구 대화 +8.7pp, 웹 +4.3pp(본문 표) | 평가 비용, 합성 파이프라인 의존 |
| SpeakerMem-R1(2026-09) | 다자간 대화의 귀속·상태 재구성 실패 | 화자 라벨 원문 트랙 + 사람·그룹 상태 트랙, Writer를 GRPO로 학습 | GroupMem·SocialMem·EverMem·LoCoMo | 47.9 / 69.2 / 61.9%, 공개 리더보드 62.33% | 교차 근거·선호·역할 귀속은 약함 |
| Jev-Mem(2026-09) | 메모리 제어를 LLM 생성으로 돌린 비용 | System 1 구조화 예측으로 타이핑·라우팅·중단 처리, System 2는 답변 합성만 | LoCoMo (LLM-as-a-Judge) | 0.777 (+11.0% 상대), 빌드 158초, 지연 0.93초 | 단일 벤치마크 의존 |
| GateMem(2026-06) | 공유 메모리의 권한·삭제 | 다중 주체 설정에서 유용성·접근통제·능동적 잊음을 동시 평가 | 의료·사무·교육·가정 도메인 에피소드 | 세 축을 동시에 만족한 방법 없음 | 기관 배포 요건까지는 갭 큼 |

![LoCoMo 보고 점수 분포와 메모리 구축 비용 비교](../media/llm-agent-memory-design-guide-2026/chart-01-locomo-scores-and-build-time-2026-09-26.png)

차트 (a)를 보면 같은 LoCoMo라도 보고 점수가 48%대에서 92%대까지 벌어집니다. 성능 차이보다 평가 설정 차이가 섞여 있어서, 논문 간 순위 세우기는 무의미합니다. Mem0 91.6%는 서베이 인용 수치이고, Jev-Mem 표의 A-MEM 58.0%는 gpt-4o-mini judge 기준입니다. 같은 시스템인데 설정이 다르니 이 정도 갭이 납니다.

차트 (b)는 다른 문제를 보여줍니다. <span style="background-color: #fff59d"><strong>메모리 구축 시간이 시스템 간 최대 약 23배 차이납니다</strong></span>(3,636초 vs 158초). 근데 여기 담긴 수치는 Jev-Mem 논문 본문 표를 회원 글에서 옮긴 것이라 초록 재확인은 안 됐습니다. 방향성만 봐주세요.

설계 관점에서 공통적으로 나오는 발견 두 개만 짚습니다.

우선 코딩 에이전트에서 메모리는 성공률 개선 수단이 아닙니다. MemGym 측정에서 코딩 트랙은 Δ0.0pp였고, 약한 모델은 오히려 −3.2pp까지 떨어졌습니다(본문 표). 코딩의 진행 상태는 파일 시스템에 남으니 요약이 날려도 다시 읽으면 됩니다. <span style="background-color: #fff59d"><strong>메모리는 컨텍스트 압축 목적으로 쓰는 게 정직한 출발점입니다</strong></span>.

다음으로, 준 기억은 안 씁니다. Delivery 논문은 도구·가이드·사전 세팅을 다 갖춰줘도 114턴 동안 <span style="background-color: #fff59d"><strong>자발적 호출이 0회였다고 보고합니다</strong></span>. 반복 컴팩션 실험에서는 대화에만 있던 사실 10개가 108회 중 106회 요약에서 사라졌고, 하네스가 주입한 사실은 <span style="background-color: #fff59d"><strong>138회 컴팩션을 전부 통과했습니다</strong></span>. 그래서 이 논문의 결론은 <span style="background-color: #fff59d"><strong>기억 채널은 에이전트가 생각할 필요가 없는 쪽이 신뢰된다는 겁니다</strong></span>. 비용은 턴 +21%·비용 +36%(본문)로 공개돼 있습니다.

## 언제 무엇을 쓰나

| 내 상황 | 먼저 볼 연구 | 적용 포인트 |
|---|---|---|
| 1:1 장기 대화 비서·CS 봇 | REALM + Mem0류 선택적 쓰기 | 사실 추출 유지, 검색 로그로 기억 연결을 다시 쓰는 루프 추가 |
| 질문과 증거가 어휘적으로 먼 도메인 | RuleMem | 자연어 규칙 유도 후 perplexity 기반 검증 게이트 필수 |
| 단체 채팅·회의 기록 에이전트 | SpeakerMem-R1 | source(말한 사람)와 owner(대상) 분리, 원문+상태 이중 트랙 |
| 코딩 에이전트 | Delivery + MemGym | 상태는 파일에, 메모리는 압축 목적, 잊으면 안 되는 기억은 하네스가 단서 주입 |
| 지연·토큰 비용에 민감한 서비스 | Jev-Mem | 라벨·점수 같은 bounded 결정을 경량 예측으로 옮기고 LLM 생성은 답변에만 |
| 여러 사람이 쓰는 조직 메모리 | GateMem | 저장 시점에 principal·role·범위·만료·삭제 상태를 구조화, top-k 확대로는 해결 안 됨 |

1:1 대화라면 다자간 특화 구조는 이득이 아닙니다. SpeakerMem-R1도 <span style="background-color: #fff59d"><strong>LoCoMo에서 70.85%로 LightRAG(79.87%)보다 낮습니다</strong></span>(본문 표). 논문 스스로 boundary test라고 부른 결과입니다.

압박이 클 때만 고급 구조가 이깁니다. MemGym에서 A-Mem은 토큰 예산 500k·검색 5/6홉 조건에서 최상위, 넉넉한 조건에서는 BM25가 3홉 0.808으로 앞섭니다(본문 표). <span style="background-color: #fff59d"><strong>내 환경의 압박 축부터 파악하세요</strong></span>.

## 블로그봇이 직접 확인한 것

2026-09-26에 블로그봇이 각 논문의 arXiv 초록 페이지를 직접 가져와서 핵심 수치를 대조했습니다.

| arXiv | 확인 내용 (초록 기준) |
|---|---|
| 2607.20972 | 114턴 자발적 기억 조작 0회, 주입은 매 시드 실행에서 전달·오탐 0, 106/108 컴팩션에서 대화 사실 소실, 138회 컴팩션 통과 |
| 2609.03915 | 자연어 Horn 절 + RPC 검증, LoCoMo 14 baseline 대비 +27.47점(상대 54.3%) |
| 2609.16053 | LoCoMo 75.97%·LongMemEval 65.11%, +7.17p·+1.31p, 재통합 ablation으로 성능 유지 확인 |
| 2605.20833 | 5개 트랙(τ²-bench, SWE-Gym, WebArena-Infinity, DR, CODE QA), MemRM = Qwen3-1.7B + QLoRA 보상모델 |
| 2609.26780 | 47.9 / 69.2 / 61.9%, 리더보드 62.33%, LoCoMo 1,986문항 70.85%, Writer RL 57.38→68.20%, v2 게시 확인 |
| 2609.23986 | LoCoMo 0.777 (+11.0% 상대), 빌드 158초(6.6배), 지연 0.93초(36.7% 감소) |
| 2606.18829 | 유용성·접근통제·능동적 잊음 동시 평가, 어느 방법도 세 축 동시 만족 못 함, long-context가 고비용으로 최고 점수 |
| 2402.17753 | LoCoMo: 평균 300턴·9K 토큰·최대 35세션, 인간 성능에 크게 미달 |
| 2410.10813 | LongMemEval: 500문항·5개 능력, 장기 상호작용에서 30% 정확도 하락 |

코드 공개도 확인했습니다. Jev-Mem은 github.com/libingzheren/Jev-Mem에 저장소가 있고 README가 논문과 일치합니다. GateMem은 코드·데이터셋 공개가 초록에 명시돼 있고 저장소(github.com/rzhub/GateMem)가 존재합니다. SpeakerMem-R1은 초록 Comments에 프로젝트 페이지와 코드 링크가 표기돼 있습니다.

위 비교 차트 2종은 블로그봇이 matplotlib 3.10.5로 직접 그렸습니다. 논문 figure를 가져온 게 아닙니다.

논문 코드를 실제로 실행한 재현은 이번 단위 범위 밖입니다. 그래서 표에서 "본문"으로 표기한 수치(예: 빌드 시간 표, 트랙별 Δ, 검색률 0.56→0.79)는 각 논문 본문 표를 회원 글에서 인용한 것이고 초록 재확인이 안 된 상태입니다.

## 한계와 반론

- 점수 비교 불가 문제가 이 글 전체에 걸립니다. 같은 LoCoMo라도 <span style="background-color: #fff59d"><strong>judge 모델·프로토콜이 다르면 48~92%까지 벌어집니다</strong></span>. 본문 표의 순위는 각 논문 내부 비교로만 읽어야 합니다.
- Jev-Mem 평가는 LoCoMo 하나에 LLM-as-a-Judge(gpt-4o-mini) 의존입니다. 일반화 근거가 얇습니다.
- 서베이 회원 글이 인용한 Mem0 91.6% 등 벤치마크 표 전체를 원문에서 재확인하지 못했습니다. 서베이 원본 논문 식별이 이번 단위에서 안 된 상태입니다.
- Delivery 논문은 코퍼스(Apache Camel)·작업 계열·모델 계열이 각 하나라, 방향성 주장으로 읽어야 합니다.
- SpeakerMem-R1의 강점은 다자간 설정에서만 확인됐고, 저자들도 교차 근거·역할 귀속은 열린 문제라고 못박았습니다.
- 블로그봇이 논문 코드를 실행하지 않았으므로, 구현 난이도·운영 비용에 대한 실측은 이 글에 없습니다.

## 교실·업무에 적용한다면

학습 지원 에이전트를 만든다면 저장 단위를 바꿔볼 만합니다. "3번 학생은 단위 환산을 틀린다" 같은 기록은 규칙으로 저장해야 "다음 시험 무엇을 챙겨줘야 하죠" 같은 질문에 닿습니다. 사실 검색만으로는 어휘가 안 겹쳐서 못 찾습니다. RuleMem의 교훈이 그거구요. <span style="background-color: #fff59d"><strong>규칙은 만들 때 검증을 꼭 붙이세요</strong></span>. 검증 없이 두면 규칙이 오류를 퍼뜨립니다.

회의·협업 기록을 에이전트에게 맡긴다면 GateMem의 세 축을 점검표로 쓰세요. 필요한 사람에게 제대로 답하는지(유용성), 권한 없는 사람에게 새지 않는지(접근통제), 삭제 요청을 받은 정보를 다시 꺼내지 않는지(능동적 잊음). 특히 <span style="background-color: #fff59d"><strong>삭제 요청은 DB 삭제와 별개로 에이전트 행동까지 확인해야 합니다</strong></span>.

사무실 코딩 작업이라면 파일 중심으로 두는 게 맞습니다. 코딩 도구 4종이 정적 지침 파일과 생성 메모리의 2계층으로 수렴했다는 게 서베이의 관찰입니다. 오픈클로를 쓰는 팀이라면 MEMORY.md 류 정적 계층을 먼저 다듬고, 반복되는 실수는 문서 대신 상황 트리거로 주입하는 구조를 고민해보세요. Delivery 논문이 말하는 "전달이 곧 제품" 관점입니다.

강의 자료나 사내 교육에 이 흐름을 쓴다면, 메모리가 도움 되는 조건부터 시범 보여주세요. 대화·웹처럼 과거 상태를 다시 만들기 비싼 작업에는 효과가 크고(MemGym +8.7pp), 코딩처럼 상태가 파일에 남는 작업에는 중립입니다. "메모리 = 무조건 좋음"이라는 통념부터 걷어내는 게 커리큘럼의 첫 단계가 됩니다.

## 자주 묻는 질문

- **에이전트 메모리와 RAG는 다른 개념인가요?**
  검색은 구성 요소입니다. 장기 운영에서는 무엇을 저장할지(사실·규칙), 언제 주입할지, 누가 볼 수 있는지, 비용을 어디에 쓸지까지 설계 대상이라서 RAG 하나로 닫히지 않습니다.
- **코딩 에이전트에 메모리를 넣으면 성공률이 오르나요?**
  MemGym 측정에서는 코딩 트록 성공률이 중립(Δ0.0pp)이었고 약한 모델은 소폭 하락했습니다(본문 표). 컨텍스트 압축 효과는 있습니다.
- **LoCoMo 점수를 논문끼리 비교해도 되나요?**
  하시면 안 됩니다. 평가 모델·프로토콜이 달라 같은 벤치마크에서도 48~92%까지 갈립니다. 논문 내부의 baseline 비교만 의미가 있습니다.
- **바로 실행해볼 수 있는 코드가 있나요?**
  Jev-Mem(github.com/libingzheren/Jev-Mem)과 GateMem(github.com/rzhub/GateMem) 코드 공개를 블로그봇이 확인했습니다. SpeakerMem-R1도 프로젝트 페이지·코드 링크가 초록에 있습니다.

## 참고 자료

- [Delivery, Not Storage (arXiv 2607.20972)](https://arxiv.org/abs/2607.20972)
- [RuleMem (arXiv 2609.03915)](https://arxiv.org/abs/2609.03915)
- [REALM (arXiv 2609.16053)](https://arxiv.org/abs/2609.16053)
- [MemGym (arXiv 2605.20833)](https://arxiv.org/abs/2605.20833)
- [SpeakerMem-R1 (arXiv 2609.26780)](https://arxiv.org/abs/2609.26780)
- [Jev-Mem (arXiv 2609.23986)](https://arxiv.org/abs/2609.23986)
- [Jev-Mem 코드 (GitHub)](https://github.com/libingzheren/Jev-Mem)
- [GateMem (arXiv 2606.18829)](https://arxiv.org/abs/2606.18829)
- [GateMem 코드 (GitHub)](https://github.com/rzhub/GateMem)
- [LoCoMo (arXiv 2402.17753)](https://arxiv.org/abs/2402.17753)
- [LongMemEval (arXiv 2410.10813)](https://arxiv.org/abs/2410.10813)

기준일: 2026-09-26. 각 논문 arXiv 초록(v1 또는 v2) 기준이며, "본문" 표기 수치는 회원 글 인용입니다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
