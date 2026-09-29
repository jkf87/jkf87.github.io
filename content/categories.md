---
title: 카테고리
description: 코난쌤 블로그의 주요 글 묶음과 추천 탐색 경로입니다.
tags:
  - categories
  - navigation
---

# 카테고리

관심사별로 글을 찾을 수 있도록 묶었습니다. 모든 글은 [[posts|전체 글 모아보기]]에서 최신순으로 확인할 수 있습니다.

## 직접 해본 실험·비교

같은 조건에서 도구를 돌려 보고 결과를 기록한 글입니다.

- [[ai-coding-harness-6-tools-review-2026-05-03|AI 코딩 하네스 6종 실전 비교]]
- [[skillopt-voice-memo-doc-2026-06-03|SkillOpt로 에이전트 스킬 학습시키기: 자막 추출 오타 점검 예시]]
- [[posts/openclaw-2026-spring-updates-summary|오픈클로 2026년 봄 업데이트 3개월치 한눈에 (4.11~5.31)]]
- [[posts/openclaw-2026-mid-spring-updates-guide|오픈클로 음성·Steer 업데이트 통합 (4.15~5.28, 로컬 TTS·외부화 실측)]]
- [[autoresearchclaw-korean-asr-ai-paper-pipeline|AutoResearchClaw 실전 사용기]]

## 오픈클로(OpenClaw) 설치·설정

오픈클로를 설치하고 기능을 설정하는 방법을 정리합니다.

- [[openclaw-windows-native-no-wsl|윈도우에서 WSL 없이 오픈클로 쓰기]]
- [[openclaw-context-engine-plugins|Context Engine Plugin으로 커스텀 파이프라인 만들기]]
- [[openclaw-active-memory-setup-guide|Active Memory 설정]]
- [[openclaw-obsidian-memory-wiki-llm-wiki-setup-2026-05-28|Obsidian 연동과 Memory Wiki 설정]]
- [[openclaw-memory-lancedb-slot-warning-2026-05-28|메모리 슬롯 전환과 LanceDB 경고 정리]]
- [[openclaw-google-meet-plugin-setup-guide-2026-05-28|Google Meet 플러그인 설치]]
- [[nilbox-openclaw-security-guide|Nilbox로 오픈클로 안전하게 실행하기]]
- [[openclaw-book-recommendation-2026|오픈클로 입문서 고르기]]

## 로컬 LLM 연결

맥과 PC에서 오픈 모델을 돌리고 에이전트에 연결하는 방법입니다.

- [[gemma4-openclaw-local-backend-practical-guide|Gemma 4를 OpenClaw에 붙이는 순서]]
- [[gemma4-codex-cli-local|Gemma 4를 Codex CLI에서 로컬로 실행하기]]
- [[qwen3-6-27b-lmstudio-openclaw-2026-04-23|Qwen3.6-27B를 LM Studio + OpenClaw로 굴리기]]
- [[qwen3-6-35b-a3b-mlx-macbook-local|Qwen3.6-35B-A3B MLX를 맥북 M4에서 돌리기]]

## 에이전트 메모리·연구 정리

논문 여러 편을 비교해 설계 기준으로 묶은 글입니다.

- [[posts/llm-agent-memory-design-guide-2026|LLM 에이전트 메모리 설계 기준 정리 (2026 논문 8편 비교)]]
- [[posts/llm-agent-experience-learning-2026|LLM 에이전트가 경험으로 배우게 하는 법 (파인튜닝 없는 학습 루프 8편 비교)]]
- [[posts/llm-agent-rag-vs-knowledge-injection-2026|LLM 에이전트에 문서를 기억시키는 네 갈래: RAG·KV 캐시·장기 메모리 논문 10편 비교]]
- [[posts/llm-agent-memory-search-design-2026|LLM 에이전트 메모리와 검색 설계: 하이브리드 검색·컨텍스트 압축·포맷 이식성 9편 비교]]
- [[posts/llm-agent-memory-operations-2026|에이전트 메모리를 학습시키고 고치고 통제하는 법: RL 학습·에러 추적·권한 관리 12자료 비교]]
- [[posts/llm-agent-memory-reuse-failure-2026|LLM 에이전트 메모리·경험 재사용이 실패하는 지점: 오염·도구 충돌·거짓 보고 13자료 비교]]
- [[posts/llm-agent-memory-failure-map-2026|LLM 에이전트 메모리가 실전에서 터지는 4개 지점: 쓰기·검색·주입·검증 14자료 비교]]
- [[posts/llm-agent-long-horizon-state-2026|LLM 에이전트가 오래 돌아도 상태를 잃지 않는 설계: 수면 통합·외부 상태 뱅크·롤백 반성 6종 비교]]
- [[posts/agent-experience-memory-reuse-2026|에이전트에 메모리를 넣었는데 성능이 떨어질 때: 재구성·쿼리 조건화·스킬화 7종 비교]]

## 에이전트 자가진화·하네스 연구 정리
- [[posts/llm-agent-harness-nooa-vs-prime-agent-2026|모델 그대로 두고 에이전트 성능 올리는 하네스 설계: NOOA와 Prime Agent 비교]]

스킬·하네스가 스스로 개선되는 루프를 논문끼리 비교해 설계 기준으로 묶은 글입니다.

- [[posts/llm-agent-self-evolution-design-guide-2026|LLM 에이전트 하네스·스킬 자가진화 설계 가이드 (논문 7편의 실패 진단과 처방 비교)]]
- [[posts/llm-agent-harness-parts-design-guide-2026|AI 에이전트가 긴 작업에서 무너질 때 하네스부터 고쳐야 한다 (논문 4편의 부품별 설계 비교)]]
- [[posts/llm-agent-harness-optimization-benchmark-guide-2026|LLM 에이전트 같은 모델인데 점수가 다를 때: 하네스 효과와 최적화 벤치마크 16편 정리]]
- [[posts/llm-agent-skill-lifecycle-guide-2026|LLM 에이전트 스킬은 쌓기만 하면 망한다 (생성·검증·압축·라우팅·보안 16편 재검증)]]
- [[posts/llm-agent-safety-harness-evolution-2026|LLM 에이전트 보상 해킹과 안전 가드레일 어떻게 막나 (검증 한계·하네스 공진화 6편 총정리)]]
- [[posts/llm-agent-optimization-policy-design-guide-2026|LLM 에이전트 최적화 루프 설계 기준: 탐색 정책을 하네스·에이전트·모델 가중치 어디에 둘까 (논문 5편 비교)]]
- [[posts/llm-agent-harness-native-rl-guide-2026|에이전트 강화학습은 배포 하네스 그대로 훈련하면 됩니다: OpenForge RL·Agent Lightning·LEGO-RL 비교]]
- [[posts/coding-agent-harness-design-guide-2026|같은 모델인데 코딩 에이전트 결과가 다른 이유: 하네스 설계 1차 자료 10편 통합 정리]]
- [[posts/llm-agent-environment-coevolution-guide-2026|LLM 에이전트 강화학습이 정체될 때는 환경부터: 에이전트·환경 공진화 접근 8편 비교]]
- [[posts/agent-rl-reward-signal-comparison-2026|에이전트 강화학습에서 보상 신호를 어디서 얻나: 로봇·게임·이미지·문서 8종 비교]]
- [[posts/agent-rl-grpo-failure-fixes-2026|에이전트 강화학습(GRPO)이 실패하는 다섯 지점과 논문별 해법: 11편 1차 출처 재검증]]
- [[posts/llm-agent-harness-efficiency-adaptation-2026|LLM 에이전트 하네스가 성능·비용을 결정한다: 토큰 절감부터 161일 자기진화까지 13편 비교]]
- [[posts/llm-agent-self-improvement-evaluation-2026|LLM 에이전트 자기 개선의 조건: 장기 실행·의도 전환·채점 오류를 잰 논문 11편 비교]]
- [[posts/llm-agent-harness-verification-design-2026|LLM 에이전트 하네스에 검증을 심는 설계: 반증 가능한 계획·세계 모델·골 드리프트 5편 비교]]
- [[posts/llm-agent-self-improvement-gates-2026|LLM 에이전트 자기개선은 어디서 고장 나나 — 검증 게이트 논문 5편 비교]]
- [[posts/llm-agent-self-improvement-layers-2026|LLM 에이전트 자기 개선 어디까지 고쳐도 되나: 3계층·실행 피드백·보안 게이트 (서베이 3종 재검증)]]
- [[posts/llm-agent-runtime-failure-repair-harness-2026|LLM 에이전트 실행 중 실패를 잡고 고치는 하네스: 감시·적응·수리 8편 비교]]

- [[posts/llm-agent-rsi-reality-check-2026|LLM 에이전트 재귀적 자기개선, 어디까지 실제인가 — 서베이 2편·Meta^n·Frontis-MA1 비교]]
- [[posts/llm-agent-experience-learning-methods-2026|LLM 에이전트 경험 학습 설계 가이드: 스킬 증류·강화학습·하네스 제어 21편 비교 (arXiv 18편 재검증)]]
- [[posts/llm-agent-harness-self-evolution-evidence-2026|LLM 에이전트 하네스 자가진화, 진짜 효과인지 확인하는 법: 검증·회귀·전이 10편 비교]]
- [[posts/llm-agent-harness-frozen-model-evidence-2026|LLM 에이전트 하네스만 고쳐서 성능 올리기: 논문 6편 1차 출처 재검증 (동결 모델 진화 5편 + 하네스 교체 대조 1편)]]
- [[posts/llm-agent-self-improvement-evidence-2026|AI 에이전트 자기개선 루프, 무엇이 진짜 이득인가: 측정·탐색·증류 논문 5편 비교]]
- [[posts/llm-agent-fix-outside-model-2026|LLM 에이전트가 같은 실패를 반복할 때 모델 대신 고칠 곳: 지식·문서·워크플로·게이트 10편 비교]]
## 에이전트 보안 연구 정리

LLM 에이전트 보안 논문을 비교해 방어 설계 기준을 정리한 글입니다.

- [[posts/llm-agent-security-defense-guide-2026|LLM 에이전트 보안 설계 기준 정리 (2026 논문 7편 비교)]]
- [[posts/llm-agent-harness-attack-surface-2026|AI 코딩 에이전트 어디까지 뚫리나: 악성 이슈·스킬 오염·하네스 권한상승 6편 총정리]]

## 코딩 에이전트 운영·신뢰 정리

코딩 에이전트 글 14편을 1차 출처 재검증으로 통합한 가이드입니다.

- [[posts/ai-coding-agent-trust-operations-2026|AI 코딩 에이전트 어디까지 믿을 수 있나: 검증·운영 전략 14편 통합 가이드]]

## 코딩 에이전트 디자인 일관성 정리

코딩 에이전트·디자인 글 8편을 1차 출처 재검증으로 통합한 가이드입니다.

- [[posts/ai-coding-agent-design-consistency-2026|AI 코딩 에이전트가 만든 UI가 어딘가 비슷할 때: DESIGN.md·getdesign.md·soul.md 통합 가이드]]

## 코딩 에이전트 비용·통제 구조 정리

코딩 에이전트 글 10편을 기초·실행 환경·실전·통제 구조로 통합한 가이드입니다.

- [[posts/ai-coding-agent-stack-guide-2026|AI 코딩 에이전트 비용 아끼고 신뢰까지 확보하는 법: 로컬 LLM·free-claude-code·LLM-as-Code 비교]]

## 코딩 에이전트 코드베이스 맥락 정리

코딩 에이전트·코드 지식 그래프 글 8편을 1차 출처 재검증과 로컬 미니 재현으로 통합한 가이드입니다.

- [[posts/ai-coding-agent-codebase-context-2026|AI 코딩 에이전트가 큰 레포에서 헤맬 때: 지식 그래프·LSP 플러그인·터미널 8편 통합 가이드]]

## 코딩 에이전트 실패 지점·검증 계층 정리

코딩 에이전트 글 14편을 1차 출처 재검증과 로컬 재현으로 통합한 가이드입니다.

- [[posts/ai-coding-agent-failure-points-2026|AI 코딩 에이전트가 조용히 무너지는 지점: 토큰 낭비·조용한 실패·거짓 보고 14편 비교]]

## 코딩 에이전트 실행 환경(Codex 생태계) 정리

Codex 앱·모바일·Windows 샌드박스와 AionUi 허브 등 코딩 에이전트 글 7편을 1차 출처 재검증으로 통합한 가이드입니다.

- [[posts/ai-coding-agent-codex-ecosystem-2026|AI 코딩 에이전트 어디서 돌릴까: Codex 앱·모바일·Windows 샌드박스·AionUi 허브 7편 통합 가이드]]

## Claude Code 신기능·구독 안전 정리

Claude Code 주간 신기능 정리 4편과 구독·인증 안전 글 3편을 1차 출처 재검증으로 통합한 가이드입니다.

- [[posts/ai-coding-agent-claude-code-features-safety-2026|AI 코딩 에이전트 Claude Code 신기능 어디까지 살아남았나: Auto Mode·Computer Use 현재 상태와 Pro 구독 안전 가이드]]

## 오픈소스 개발 도구 비교

유료 SaaS의 오픈소스 대안 도구를 비교하고 직접 설치·실행한 기록입니다.

- [[posts/open-source-devtools-hands-on-2026|오픈소스로 유료 SaaS를 갈아타도 되나 (지도·음악·실험추적·에이전트 도구 16종 직접 설치해 비교)]]

- [[posts/llm-agent-tool-use-tuning-debug-2026|LLM 에이전트 도구 호출 비용 줄이고 실패 잡는 순서 (측정·훈련·조절·감사·디버깅 10편 통합)]]

## 사이트 안내

- [[about|운영자 소개]]
- [[contact|연락처]]
- [[privacy-policy|개인정보처리방침]]
- [[editorial-policy|콘텐츠 제작 원칙]]

## 에이전트 스킬 생태계 정리

스킬(SKILL.md) 표준과 저장소 9곳을 직접 확인해 비교한 글입니다.

- [[posts/ai-agent-skills-ecosystem-guide-2026|AI 코딩 에이전트 스킬, 어디서 가져와야 하나 — 저장소 9곳 직접 확인 비교]]

## 하네스 verifier·루브릭 설계 정리

암묵지(taste)를 검증 루브릭으로 바꾸는 절차를 다룬 옛 글 4편을 1차 출처 대조와 WCAG 명암비 재계산으로 통합한 가이드입니다.

- [[posts/ai-agent-verifier-rubric-guide-2026|AI 에이전트 결과물이 '이건 아닌데'일 때: taste를 검증 루브릭으로 바꾸는 하네스 verifier 설계법]]
