---
title: "에이전트 강화학습·하네스 논문 모음 18선"
description: "RL for Agents, verifier, harness, environment, self-evolving agent 관련 글 18개를 학습 환경과 검증 루프 관점에서 묶었습니다."
date: 2026-09-13
tags:
  - topic-cluster
  - seo
  - aeo
draft: false
---

## 결론 먼저

에이전트 성능을 모델이 아니라 환경·보상·검증 루프로 올리는 흐름입니다. 개별 글을 최신순으로만 두면 검색엔진과 독자가 흐름을 잡기 어렵습니다. 이 페이지는 관련 글을 한 주제로 묶어, 검색 유입과 내부 링크를 동시에 강화하기 위한 주제 클러스터입니다.

| 묶음 | 내용 |
|---|---|
| 주제 | 에이전트 강화학습·하네스 논문 모음 |
| 목적 | 관련 글 내부 링크 강화와 검색형 탐색 경로 제공 |
| 기준일 | 2026-09-13 |
| 포함 글 수 | 18개 |
| 원본 목록 | https://conanssam.com/posts |

## 추천 글

| 글 | 날짜 | 검색 요약 |
|---|---:|---|
| [[rl-environments-taxonomy-llm-agents-2026-08-03|LLM 에이전트 RL 환경 정리: 모델만 보면 절반만 본 겁니다]] | 2026-08-03 | Hanchung Lee의 'A Taxonomy of RL Environments for LLM Agents'를 카톡식 정리 말투로 다시 풀었다. 핵심은 RL 환경을 tas |
| [[2026-08-27-lego-rl-harness-native-rl-coding-agents|LEGO-RL: 코딩 에이전트 하네스를 통째로 RL 훈련 루프에 올리는 방법]] | 2026-08-27 | LEGO-RL은 OpenHands SDK·Claude Code·OpenCode 같은 코딩 에이전트 하네스를 내부 제어 흐름을 바꾸지 않고 정책경사 RL 훈련에 직접 연결하 |
| [[2026-07-27-openforge-rl-harness-native-agent-training|OpenForge RL: 하네스를 입은 에이전트를 그대로 훈련시키는 오픈 프레임워크]] | 2026-07-27 |  |
| [[2026-07-25-openforge-rl-train-harness-native-agents|OpenForge RL: 어떤 하네스든 어떤 환경이든 끝까지 훈련한다 — 하네스 네이티브 에이전트 RL의 오픈 인프라]] | 2026-07-25 |  |
| [[2026-08-10-evoharness-rl-self-evolving-runtime-harness|EvoHarness-RL: 에이전트가 하네스를 언제 읽을지 직접 배우는 방법]] | 2026-08-10 |  |
| [[rl-environments-llm-agents-2026|LLM 에이전트를 위한 RL 환경 설계: 에이전트 용어사전과 환경 분류학]] | 2026-05-27 | 에이전트 RL 훈련 환경의 구성 요소(태스크, 하네스, 검증기, 상태, 설정)를 체계적으로 정리하고, 하네스·스캐폴딩·정책 등 에이전트 핵심 용어를 명확히 정의함. |
| [[2026-08-03-co-harness-co-evolving-agent-harness-weights|Co-Harness: 하네스와 모델 가중치를 동시에 진화시키는 에이전트 포스트트레이닝]] | 2026-08-03 |  |
| [[2026-08-18-clawgym2-blackbox-rl-harness|ClawGym II: OpenClaw·Claude Code 같은 블랙박스 하네스 너머로 RL 학습시키기]] | 2026-08-18 |  |
| [[2026-07-19-memoharness-agent-harness-learns-from-experience|MemoHarness: 에이전트 하네스가 경험에서 학습한다면?]] | 2026-07-19T13:00:00+09:00 |  |
| [[2026-07-18-harness-evolution-evaluation-rethink|하네스 진화가 진짜 효과가 있는지 다시 묻다 — AI2·UW의 냉정한 평가]] | 2026-07-18 | Allen Institute for AI와 University of Washington이 '자동 하네스 진화'의 효과를 의문시하는 결과를 발표했다. Terminal-Ben |
| [[code-as-agent-harness-2026-05-20|Code as Agent Harness: 코드가 에이전트의 하네스가 될 때 — 102쪽 서베이 논문 리뷰]] | 2026-05-20 | UIUC·Meta·Stanford 공동으로 발표한 102쪽 서베이 논문 'Code as Agent Harness'를 정리합니다. 코드가 단순한 생성물이 아니라 에이전트의  |
| [[2026-08-03-agent-harness-distillation-inference-time-harness-extraction|에이전트 하네스를 훔친다: AMAS의 추론 시간 하네스가 새로운 공격 표면이다]] | 2026-08-03T10:00:00+09:00 |  |
| [[agent-harness-engineering-2026|AI 코딩 에이전트 성능을 올리는 방법: 하네스 엔지니어링 정리]] | 2026-04-29 | AI 코딩 에이전트 성능을 모델 교체 없이 높이는 하네스 엔지니어링 개념, AGENTS.md, 훅, 컨텍스트 정책, 검증 루프를 정리했습니다. |
| [[2026-07-21-recursive-harness-self-improvement|Recursive Harness Self-Improvement: 에이전트 하네스를 스스로 진화시키는 루프]] | 2026-07-21 |  |
| [[2026-08-05-harness-r1-executable-runtime-harness-rl|Harness-R1: 에이전트 하네스 코드를 RL로 고치는 9B 모델]] | 2026-08-05 |  |
| [[rlvr-environments-llm-agents-2026-07-28|RLVR 환경: 에이전트는 이제 문제집이 아니라 훈련장을 필요로 한다]] | 2026-07-28 | Deep Learning with Yacine의 RLVR 환경 소개 영상을 뉴스레터 형식으로 정리했다. 핵심은 데이터셋, 정책, 롤아웃, 루브릭을 묶은 재사용 가능한 환경 |
| [[self-harness-self-improving-harness-2026-08-24|Self-Harness: 하네스가 스스로를 고치는 루프 — 상하이AI랩의 에이전트 자가개선 실험]] | 2026-08-24 |  |
| [[2026-08-07-harnessopt-bench-llm-harness-optimization|HarnessOpt-Bench: Evaluating LLMs at Harness Optimization — 벤치마크 분석]] | - |  |

## 빠른 목록

- [[rl-environments-taxonomy-llm-agents-2026-08-03|LLM 에이전트 RL 환경 정리: 모델만 보면 절반만 본 겁니다]]
- [[2026-08-27-lego-rl-harness-native-rl-coding-agents|LEGO-RL: 코딩 에이전트 하네스를 통째로 RL 훈련 루프에 올리는 방법]]
- [[2026-07-27-openforge-rl-harness-native-agent-training|OpenForge RL: 하네스를 입은 에이전트를 그대로 훈련시키는 오픈 프레임워크]]
- [[2026-07-25-openforge-rl-train-harness-native-agents|OpenForge RL: 어떤 하네스든 어떤 환경이든 끝까지 훈련한다 — 하네스 네이티브 에이전트 RL의 오픈 인프라]]
- [[2026-08-10-evoharness-rl-self-evolving-runtime-harness|EvoHarness-RL: 에이전트가 하네스를 언제 읽을지 직접 배우는 방법]]
- [[rl-environments-llm-agents-2026|LLM 에이전트를 위한 RL 환경 설계: 에이전트 용어사전과 환경 분류학]]
- [[2026-08-03-co-harness-co-evolving-agent-harness-weights|Co-Harness: 하네스와 모델 가중치를 동시에 진화시키는 에이전트 포스트트레이닝]]
- [[2026-08-18-clawgym2-blackbox-rl-harness|ClawGym II: OpenClaw·Claude Code 같은 블랙박스 하네스 너머로 RL 학습시키기]]
- [[2026-07-19-memoharness-agent-harness-learns-from-experience|MemoHarness: 에이전트 하네스가 경험에서 학습한다면?]]
- [[2026-07-18-harness-evolution-evaluation-rethink|하네스 진화가 진짜 효과가 있는지 다시 묻다 — AI2·UW의 냉정한 평가]]
- [[code-as-agent-harness-2026-05-20|Code as Agent Harness: 코드가 에이전트의 하네스가 될 때 — 102쪽 서베이 논문 리뷰]]
- [[2026-08-03-agent-harness-distillation-inference-time-harness-extraction|에이전트 하네스를 훔친다: AMAS의 추론 시간 하네스가 새로운 공격 표면이다]]
- [[agent-harness-engineering-2026|AI 코딩 에이전트 성능을 올리는 방법: 하네스 엔지니어링 정리]]
- [[2026-07-21-recursive-harness-self-improvement|Recursive Harness Self-Improvement: 에이전트 하네스를 스스로 진화시키는 루프]]
- [[2026-08-05-harness-r1-executable-runtime-harness-rl|Harness-R1: 에이전트 하네스 코드를 RL로 고치는 9B 모델]]
- [[rlvr-environments-llm-agents-2026-07-28|RLVR 환경: 에이전트는 이제 문제집이 아니라 훈련장을 필요로 한다]]
- [[self-harness-self-improving-harness-2026-08-24|Self-Harness: 하네스가 스스로를 고치는 루프 — 상하이AI랩의 에이전트 자가개선 실험]]
- [[2026-08-07-harnessopt-bench-llm-harness-optimization|HarnessOpt-Bench: Evaluating LLMs at Harness Optimization — 벤치마크 분석]]

## FAQ: 에이전트 강화학습·하네스 논문 모음 검색 질문

### 이 페이지는 무엇을 위한 페이지인가요?

에이전트 강화학습·하네스 논문 모음와 관련된 기존 글을 한 번에 탐색하도록 만든 주제 클러스터입니다.

### 왜 주제 클러스터가 SEO에 도움이 되나요?

비슷한 글들이 서로 연결되면 검색엔진이 사이트의 전문 주제를 이해하기 쉽고, 독자도 한 글에서 다음 글로 이동하기 쉬워집니다.

### 새 글도 이 페이지에 추가되나요?

네. 이후 관련 글이 쌓이면 이 클러스터에 계속 연결해 내부 링크 구조를 강화하는 것이 좋습니다.
