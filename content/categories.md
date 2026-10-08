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
- [[posts/llm-agent-memory-roundup-2026-09-30|LLM 에이전트 메모리 최신 논문 7편 비교 (저장·확인·공개·학습)]]
- [[posts/llm-agent-context-compaction-roundup-2026-10|토큰 폭탄 터지기 전에: LLM 에이전트 컨텍스트 압축 논문 5편 심층 비교]]

## 에이전트 자가진화·하네스 연구 정리
- [[posts/llm-agent-harness-nooa-vs-prime-agent-2026|모델 그대로 두고 에이전트 성능 올리는 하네스 설계: NOOA와 Prime Agent 비교]]

스킬·하네스가 스스로 개선되는 루프를 논문끼리 비교해 설계 기준으로 묶은 글입니다.

- [[posts/llm-agent-self-evolution-design-guide-2026|LLM 에이전트 하네스·스킬 자가진화 설계 가이드 (논문 7편의 실패 진단과 처방 비교)]]
- [[posts/llm-agent-harness-parts-design-guide-2026|AI 에이전트가 긴 작업에서 무너질 때 하네스부터 고쳐야 한다 (논문 4편의 부품별 설계 비교)]]
- [[posts/llm-agent-harness-optimization-benchmark-guide-2026|LLM 에이전트 같은 모델인데 점수가 다를 때: 하네스 효과와 최적화 벤치마크 16편 정리]]
- [[posts/agent-harness-optimization-roundup-2026-10|AI 에이전트 하네스 최적화, 어디까지 해야 하나: 9월 말 논문 4편 비교]]
- [[posts/llm-agent-skill-lifecycle-guide-2026|LLM 에이전트 스킬은 쌓기만 하면 망한다 (생성·검증·압축·라우팅·보안 16편 재검증)]]
- [[posts/llm-agent-safety-harness-evolution-2026|LLM 에이전트 보상 해킹과 안전 가드레일 어떻게 막나 (검증 한계·하네스 공진화 6편 총정리)]]
- [[posts/llm-agent-optimization-policy-design-guide-2026|LLM 에이전트 최적화 루프 설계 기준: 탐색 정책을 하네스·에이전트·모델 가중치 어디에 둘까 (논문 5편 비교)]]
- [[posts/llm-agent-harness-native-rl-guide-2026|에이전트 강화학습은 배포 하네스 그대로 훈련하면 됩니다: OpenForge RL·Agent Lightning·LEGO-RL 비교]]
- [[posts/coding-agent-harness-design-guide-2026|같은 모델인데 코딩 에이전트 결과가 다른 이유: 하네스 설계 1차 자료 10편 통합 정리]]
- [[posts/llm-agent-environment-coevolution-guide-2026|LLM 에이전트 강화학습이 정체될 때는 환경부터: 에이전트·환경 공진화 접근 8편 비교]]
- [[posts/agent-rl-reward-signal-comparison-2026|에이전트 강화학습에서 보상 신호를 어디서 얻나: 로봇·게임·이미지·문서 8종 비교]]
- [[posts/agent-rl-credit-assignment-roundup-2026-10|LLM 에이전트 강화학습, 어떤 단계에 보상을 줄까: SHARPO·FAULT·DARS 4편 비교]]
- [[posts/gui-agent-experience-routing-roundup-2026-10|GUI 에이전트 경험은 가중치에 넣을까 컨텍스트에 둘까: 2026년 9월 말 논문 6편 비교]]
- [[posts/agent-rl-grpo-failure-fixes-2026|에이전트 강화학습(GRPO)이 실패하는 다섯 지점과 논문별 해법: 11편 1차 출처 재검증]]
- [[posts/llm-agent-rl-environment-data-guide-2026|LLM 에이전트 강화학습 환경·데이터 설계 기준: 실행 검증 합성과 측정 계약 8편 비교]]
- [[posts/llm-agent-rl-verifiable-reward-design-2026|정답이 없는 업무에 강화학습 보상을 만드는 법: LLM 에이전트 RLVR 확장 10편 비교]]
- [[posts/llm-agent-onpolicy-distillation-teacher-design-2026|증류 교사를 어디서 얻나: LLM 에이전트 온폴리시 증류 교사 설계 4편 비교]]
- [[posts/llm-agent-rl-credit-assignment-guide-2026|LLM 에이전트 강화학습 크레딧 할당 설계: 궤적 보상을 턴·스텝·토큰으로 쪼개는 12편 비교]]
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

- [[posts/agent-security-defense-stack-roundup-2026-10|LLM 에이전트 가드레일 벤치마크 점수가 실전에서 안 맞는 문제: 10월 2일 방어 논문 6편 비교]]
- [[posts/llm-agent-security-defense-guide-2026|LLM 에이전트 보안 설계 기준 정리 (2026 논문 7편 비교)]]
- [[posts/llm-agent-harness-attack-surface-2026|AI 코딩 에이전트 어디까지 뚫리나: 악성 이슈·스킬 오염·하네스 권한상승 6편 총정리]]
- [[posts/llm-agent-safety-attack-eval-defense-guide-2026|LLM 에이전트는 어디서 무너지나: 공격·평가·방어 13종 총정리]]
- [[posts/llm-agent-misalignment-safety-guide-2026|LLM 에이전트 미스얼라인먼트 어떻게 막나: Claude 협박률 96%→0%와 훈련·성찰·모니터 3층 정리]]
- [[posts/ai-cybersecurity-glasswing-nday-2026|AI 사이버보안 어디까지 사실인가: Glasswing 1만 취약점·N-day 익스플로잇 실험·OpenMythos 재구현]]

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

## 멀티에이전트 설계·운영 정리

멀티에이전트 LLM 연구를 비교해 설계 기준을 정리한 글입니다.

- [[posts/llm-multi-agent-design-guide-2026|LLM 에이전트 팀 설계, 언제 이기고 언제 지나: 멀티에이전트 11편 통합 정리]]
- [[posts/llm-multi-agent-failure-fixes-2026|LLM 에이전트 여러 개가 실패하는 4가지 지점과 해법: DarkForest·SearchOS·WebSwarm 비교]]
- [[posts/llm-multi-agent-org-structure-2026|멀티 에이전트 오케스트레이션 실패 원인과 조직 설계 해법: $5,000 후기와 Fugu·ORCH 비교]]

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

## 에이전트 벤치마크·평가 정리

에이전트 벤치마크 점수와 실전 성과의 격차를 측정한 글을 모았습니다.

- [[posts/llm-agent-benchmark-score-gap-guide-2026|터미널 벤치마크 82%가 실전 업무 1%로 무너지는 이유: LLM 에이전트 벤치마크 10종 비교]]
- [[posts/llm-agent-evaluation-design-guide-2026|LLM 에이전트 평가 설계 가이드: 점수 다음에 볼 축·신뢰성·비용 — 벤치마크·연구 14종 비교]]
- [[posts/ai-personalized-evaluation-guide-2026|AI가 내 취향에 맞는지 어떻게 평가하나: LLM Judge 개인화·취향 루브릭·이미지 벤치마크 6종 비교]]
- [[posts/gui-agent-reliability-guide-2026|GUI 에이전트가 무너지는 4가지 지점과 검증 설계: MobileGym·Qwen-UI-Agent·ERPBench 비교]]
- [[posts/llm-agent-stop-decision-roundup-2026-10|LLM 에이전트가 멈추지 않는 문제: 중단·질문·기권 판단 논문 6편 비교]]

## 브라우저·화면 작업에 AI 붙이기

사람이 쓰는 브라우저·캡처·영상·문서 작업에 AI를 붙이는 도구와 기법을 옛 글 11편에서 통합 정리한 허브입니다.

- [[posts/ai-agent-browser-screen-tools-guide-2026|AI 에이전트와 브라우저·화면 작업을 나눠 쓰는 법: ego lite, macshot, VOID, PolicyGuide 통합 정리]]
- [[posts/ai-agent-practical-guide-2026|AI 에이전트 실무 통합 가이드: 폰 서버 구축부터 GUI 에이전트 클릭 정확도·이미지 편집 규칙까지]]

## AI 에이전트 실전 배포·동향 정리

에이전트를 실무에 올릴 때 걸리는 지점과 2026년 흐름을 주제별로 비교한 글입니다.

- [[posts/llm-agent-production-checklist-2026|LLM 에이전트 실무 배포, 모델을 안 바꾸고 고치는 다섯 계층 — 논문·플랫폼 10개 비교]]
- [[posts/2026-09-30-llm-agent-reliability-synthesis|LLM 에이전트 신뢰성 총정리 — 오류 폭발·아첨·전략 고착과 이걸 잡은 설계들(2026년 논문 11편)]]
- [[posts/2026-09-30-small-model-stack-synthesis|노트북에서 직접 만드는 소형 LLM 스택 — 10M 모델 학습·보정·온디바이스 배포·에이전트 감시]]
- [[posts/2026-09-30-graph-structured-agent-design-synthesis|LLM 에이전트 성능을 그래프로 끌어올리기: 태스크 DAG·지식그래프·워크플로우 컴파일 6건 비교]]
- [[posts/2026-09-30-ai-trends-loop-structure-synthesis|AI 에이전트 트렌드 2026 상반기 총정리: 모델 밖에서 성능을 만드는 구조 7가지]]
- [[posts/ai-agent-demo-to-production-2026|AI 에이전트 데모에서 실전으로 넘어가는 조건: 2026년 사례 11건 비교]]
- [[posts/llm-agent-success-signal-gap-2026|테스트는 통과하는데 성과는 그대로: LLM 에이전트 성공 신호의 맹점 6사례 비교]]

## LLM 강의 노트 정리

LLM 학습 비용과 병렬화를 다룬 강의노트를 한 흐름으로 묶은 글입니다.

- [[posts/llm-training-cost-to-parallelism-guide-2026|LLM 학습 비용 계산부터 GPU 병렬화까지: ECE7115 강의노트 10편 한 흐름 정리]]

## 모델 출시·선택 기준 정리

2026년에 나온 상용·오픈 모델을 가격·벤치마크·접근 조건으로 비교한 글입니다.

- [[posts/frontier-model-releases-2026-comparison|2026년 프론티어 모델 출시 6종 비교: Claude Opus·GPT-5.5 가격과 벤치마크 흐름 정리]]
- [[posts/claude-mythos-gpt-5-6-trusted-access-2026|Claude Mythos는 왜 일반 공개 안 하나: 벤치마크 포화와 GPT-5.6·Opus 5 접근 통제 정리]]
- [[posts/open-weight-local-llm-selection-2026|로컬 LLM 모델 선택 기준 2026: Qwen3.6, Gemma 4, Nemotron 오픈소스 모델 비교]]
- [[posts/2026-open-model-release-comparison|오픈소스 모델 선택 기준 2026: Kimi K2.6·DeepSeek-V4·Solar Open 2·GLM-5.3 릴리즈 비교]]

## 멀티모달·실시간 에이전트 정리

영상·음성·행동을 함께 다루는 실시간 에이전트 연구를 비교한 글입니다.

- [[posts/2026-realtime-multimodal-agent-comparison|실시간 멀티모달 LLM 에이전트 2026: StreamingClaw·Qwen-VLA·MHS까지 7건 비교]]

## 추론 비용·메모리 절약 정리

토큰·지연·메모리를 줄이는 기법을 같은 축으로 비교한 글입니다.

- [[posts/llm-agent-reasoning-efficiency-cost-guide-2026|LLM 에이전트 추론 비용 줄이기: 토큰 낭비·도구 대기·KV 캐시 16편 통합 정리]]
- [[posts/llm-memory-saving-weights-vs-kv-cache-quantization-2026|로컬 LLM 메모리 절약 두 갈래: 가중치 2비트(OA-EM)와 KV 캐시 압축(TurboQuant) 정리]]

## 연구 자동화 에이전트 정리

자율 연구 에이전트 시스템과 그 결과를 검증하는 벤치마크를 비교한 글입니다.

- [[posts/autonomous-research-agents-verification-guide-2026|AI 연구 자동화의 현주소: 자율 연구 에이전트 시스템과 검증 벤치마크 11편 통합 정리]]
- [[posts/deep-research-agent-reliability-roundup-2026-10|딥리서치 에이전트가 틀리는 지점과 고치는 법: 2026년 9월 말 논문 6편 비교]]

## UX 법칙으로 자료 만들기

Laws of UX의 법칙을 원전 연구 숫자와 함께 문서·발표·강의 자료 기준으로 옮긴 글입니다.

- [[posts/laws-of-ux-10-laws-docs-classroom-guide|Laws of UX 법칙 10개 한줄 정리: 보고서·발표 자료·강의 자료에 바로 쓰는 법]]
- [[posts/laws-of-ux-4-choice-speed-laws-guide|Laws of UX 선택·속도 법칙 4개 한줄 정리: 메뉴 개수·버튼 크기·반응 시간의 원전 기준]]
- [[posts/laws-of-ux-3-memory-capacity-laws-guide|Laws of UX 기억 법칙 3개 한줄 정리: 7±2에서 4±1까지, 청킹·밀러의 법칙·작업 기억의 원전 기준]]
- [[posts/laws-of-ux-9-complexity-familiarity-laws-guide|Laws of UX 복잡성·익숙함 법칙 9개 한줄 정리: 야콥·테슬러·포스텔·파레토·파킨슨 원전 기준]]
- [[posts/laws-of-ux-4-gestalt-grouping-laws-guide|Laws of UX 그룹화 법칙 4개 정리: 근접성·유사성·공통영역·균일연결의 원전 기준과 우선순위]]
