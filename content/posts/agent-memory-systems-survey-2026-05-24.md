---
title: "에이전트 메모리 시스템 전체 지도 — 코딩 도구 넷이 같은 설계로 수렴한 이유"
slug: "agent-memory-systems-survey-2026-05-24"
date: 2026-05-24
tags:
  - AI에이전트
  - 메모리시스템
  - LLM
  - Mem0
  - Zep
  - MemGPT
  - ClaudeCode
  - OpenClaw
  - RAG
  - 벡터DB
description: "에이전트 메모리 시스템 서베이 분석. 검색·그래프·LLM 매개·구조적·파라메트릭 다섯 갈래 접근과 벤치마크 숫자, 그리고 Codex CLI·Copilot·Claude Code·OpenClaw가 독립적으로 같은 2계층 설계로 수렴했다는 발견."
aliases:
  - agent-memory-systems-survey-2026-05-24/index
cover: images/agent-memory-systems-survey-2026-05-24/thumbnail.jpg
draft: true
refactor_hub: agent-memory-04
refactor_status: queued
---

세션을 닫으면 대화가 사라지는 건 단순한 불편함이 아니라 에이전트가 진짜 비서가 되는 근본 장벽임. "Agent Memory Systems for Large Language Models" 서베이가 이 분야 전체를 정리해줌. 내가 매일 쓰는 OpenClaw의 메모리 구조가 어느 생태계 어디쯤에 있는지 알 수 있는 지도라 정리함.

1. 구현 방식은 다섯 갈래임. 검색 기반은 어휘 검색(BM25), 밀도 벡터 검색(RAG), 하이브리드로 대부분의 프로덕션 시스템 기반. 그래프 기반은 지식 그래프로 엔티티 관계와 시간적 유효성을 추적하는데 Zep의 Graphiti, HippoRAG가 대표적. LLM 매개 방식은 LLM이 직접 뭘 기억할지 판단하는 것으로 Mem0의 선택적 쓰기가 대표적. 구조적 방식은 컨텍스트 관리와 계층형 페이징(MemGPT), 압축·요약. 파라메트릭은 가중치에 직접 새기는 파인튜닝과 KV 캐시 재사용. 실제 시스템은 대부분 둘 이상을 조합함.

![메모리 시스템 분류 체계](/images/agent-memory-systems-survey-2026-05-24/figure1-taxonomy.jpg)

2. 벤치마크 숫자부터. LoCoMo는 평균 300턴, 9K 토큰, 최대 35세션의 초장기 대화로 단일 홉 QA부터 다중 홉 추론까지 테스트하는데 인간 성능이 LLM을 약 36% 상회함. LongMemEval는 대화당 평균 115K 토큰에 500개 질문으로 지식 업데이트와 시간 추론을 테스트함. 숫자로는 Mem0(2026)이 LoCoMo 91.6%, LongMemEval 93.4%로 압도적이고 Hindsight가 LongMemEval 91.4%, Zep이 75.1%/71.2%, MemGPT는 LoCoMo에서 48% 정도로 낮은 편. 핵심 발견은 단일 승자가 없고 시간 추론이 모든 시스템의 치명적 병목이라는 것. OpenAI Memory도 시간 관련 질문에서 21.7%만 정답임. 언제부터 언제까지 참이었는지를 묻는 질문에 아직 못 답함.

![벤치마크 성능 비교](/images/agent-memory-systems-survey-2026-05-24/figure3-benchmarks.jpg)

3. 아키텍처별 개성이 분명함. Mem0은 대화에서 핵심 사실을 동적으로 추출해서 통합하는 방식으로 풀 컨텍스트 대비 91% 레이턴시 감소를 기록함. Zep은 바이템포럴 유효성 윈도우로 "언제부터 언제까지 참이었는가"를 추적하는데, 바이템포럴은 사실이 실제로 일어난 시점과 시스템에 기록된 시점을 별도의 두 시간축으로 관리한다는 뜻임. 시간 추론에서도 여전히 헤맴. MemGPT는 OS 영감 3계층 페이징으로 무제한 컨텍스트를 가능하게 하지만 정확도가 낮은 편. Hindsight는 20B 오픈 모델로 풀 컨텍스트 GPT-4o를 능가하는데 반성 레이어가 차이를 만듦. 속도와 정확도, 영구성과 수정 가능성의 트레이드오프가 시스템마다 다르게 풀려 있음.

4. 이 서베이의 가장 흥미로운 발견은 프로덕션 코딩 도구임. Codex CLI, GitHub Copilot, Claude Code, OpenClaw 넷이 서로 논의 없이 동일한 2계층 설계로 수렴했다는 것. 정적 명령 계층(AGENTS.md, Steering files, CLAUDE.md, MEMORY.md)과 생성 메모리 계층(~/.codex/memories/, 독점 벡터 인덱스, ~/.claude/projects/.../memory/, SQLite/LanceDB)의 조합. 이게 현재 실무에서 검증된 패턴이라는 뜻임.

![프로덕션 도구의 메모리 아키텍처](/images/agent-memory-systems-survey-2026-05-24/figure2-prod-arch.jpg)

5. 넷 중 OpenClaw가 가장 다층적임. MEMORY.md(장기), memory/YYYY-MM-DD.md(일일), DREAMS.md(통합 일기)의 파일 계층에 기본 SQLite 백엔드에서 BM25 검색을 지원하고 임베딩 제공자가 설정되면 하이브리드 모드(벡터 70% + BM25 30%)로 전환함. 그리고 Dreaming 백그라운드 프로세스가 일일 노트의 신호를 점수화해서 MEMORY.md로 승격시킴. 인간의 수면 기억 통합과 유사한 개념인데, 앞서 정리한 SkillProx의 역방향 정리(무엇을 승격할지와 무엇을 버릴지를 같은 비중으로)와 이어지는 설계임. Claude Code가 감사 가능성과 인간 제어를 우선해서 네이티브 벡터 검색이 없다는 점, Copilot은 MRL 임베딩으로 전 세대 대비 37.6% 검색 품질 개선과 8배 메모리 절약을 했는데, MRL(마트료시카 표현 학습)은 한 번의 임베딩을 여러 차원 크기로 잘라서 쓸 수 있게 만드는 기법이라 저장 공간을 아끼면서 검색이 가능함. 생성 요약이 없다는 점도 각각의 철학을 보여줌.

6. 인프라 층도 정리돼 있음. FAISS가 가장 빠르지만 영속성과 하이브리드 검색이 없고 LanceDB가 제로 서버에 하이브리드 검색, p50 1-5ms로 에이전트 메모리 워크로드에 가장 적합하다는 판정. Qdrant, Chroma는 각각 서버형과 인프로세스형 중간 위치. 벡터 스토어 선택이 레이턴시와 검색 능력에 큰 영향을 주는데 대부분의 논문이 블랙박스로 취급한다는 지적도 있음.

7. 열린 질문 여덟 개 중 실무에 닿는 것들. 시간 추론 병목, 1M 토큰 이상 규모 저하, 벤치마크가 대화형 회상만 테스트하고 에이전트 워크플로우 메모리는 평가하지 않는다는 커버리지 문제, 자동 통합의 충실도(검증 가능한 커버리지 보증 없음), 도구 경계 간 메모리 핸드오프 표준 부재, 메모리 포이즈닝 방어 부재, 평가 LLM이 다르면 점수 비교가 불가능하다는 표준화 문제. 특히 워크플로우 메모리 평가 부재는 앞서 정리한 MemoryArena가 직접 공략한 지점이라, 이 서베이가 지적한 갭이 실제로 메워지고 있는 흐름임.

8. 결론을 실무로 옮기면 이렇게 됨. 대화 회상이 목적이면 Mem0류 선택적 쓰기가 강력하고, 시간이 중요한 도메인이면 그래프 기반이 낫지만 완벽하지 않고, 코딩·작업 에이전트라면 이미 검증된 2계층 패턴(정적 지침 파일 + 생성 메모리)에서 시작하는 게 정답. 나의 OpenClaw 스택이 그 패턴 위에 있으니 방향은 맞고, 남은 숙제는 통합 충실도(일일 노트에서 장기로 승격될 때 검증)와 시간 정보를 메모리에 어떻게 남길지임.

**참고**: [Mem0](https://github.com/mem0ai/mem0) | [Zep](https://github.com/getzep/zep) | [MemGPT/Letta](https://github.com/letta-ai/letta) | [OpenClaw](https://github.com/openclaw/openclaw) | [LanceDB](https://github.com/lancedb/lancedb)
