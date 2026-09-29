---
title: "에이전트 메모리를 학습시키고 고치고 통제하는 법: RL 학습·에러 추적·권한 관리 12자료 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "메모리 RL 학습(Memory-R2), 에러 추적(MemTrace), 권한·삭제 거버넌스(GateMem)까지 2026년 자료 12건을 2026-09-29에 1차 출처에서 재검증해 4단계 운영 지도로 정리했습니다."
tags:
  - LLM 에이전트
  - 메모리
  - 강화학습
  - 디버깅
  - 거버넌스
refactor_hub_id: agent-memory-03
aliases:
  - mirofish-multi-agent-simulation-open-source
  - hyperagent-agent-economy-interview-newsletter-2026-05-03
  - openai-founders-agent-personal-agi-core-memory-2026
  - openhuman-ai-agent-2026-05-14
  - agent-rl-optimization-akbe-muse-2026-05-28
  - memforest-hierarchical-temporal-indexing-agent-memory-2026-05-28
  - memtrace-llm-memory-error-tracing-2026-05-29
  - openai-chatgpt-memory-dreaming-2026-06-05
  - gatemem-memory-governance-2026-06-23
  - posts/2026-07-31-metis-memory-foundation-model
  - agent-memory-rag
  - posts/2026-09-22-memory-rl-fair-credit-memory-r2
draft: false
sources_read: "논문 7종(2605.21768, 2605.23986, 2605.26952, 2605.27366, 2605.28732, 2606.18829, 2607.26760) 초록을 2026-09-29에 전수 fetch해 HTTP 200과 기본 주장을 확인했고, 이 중 6종은 HTML 본문을 내려받아 표 수치를 grep으로 대조했습니다(79.8·6배 / +1.85·18%·25% / 68.4·67.3·61.2·87.94·+10.51 / 1,514·160·7.62 / 91·2,218 / 50.60·43.14·49.67·24.12·8.97·30.61·34.64·40.72·0.47→0.27 / 357,137·406M·4B·9B·27B). 코드는 MemTrace가 공개 예정 상태(zjunlp/MemTrace)이고 GateMem·Memory-R2 등 나머지 논문은 이번 실행에서 저장소 실재만 확인했습니다. OpenHuman·MiroFish는 GitHub API로 라이선스까지 확인했구요, Dreaming은 OpenAI 공식 발표문을 fetch해 V0·V3 타임라인을 확인했습니다."
novelty_vs_paper: "F1 50.60·쓰기 6배·7.62% 회복·MGS 곱셈 구조 같은 수치와 벤치마크 설계는 각 논문의 기여이고, 이 글의 새 기여는 12자료를 저장·학습·진단·통제 4단계 지도로 배치한 종합과 2026-09-29 재검증에서 나온 정정 3건(MiroFish 라이선스 AGPL-3.0, Metis 코퍼스 357,137샘플, Dreaming 5배 수치 미확인)입니다"
---

## 한눈에 보는 결론

2026년 3월부터 9월까지 이 블로그에 쌓인 에이전트 메모리 글 12편을 한 페이지로 합쳤습니다. 논문 7편, 공식 발표 1건, 오픈소스 2건, 인터뷰 2건입니다. 2026-09-29에 1차 출처를 전부 다시 확인했구요, 재확인 안 된 수치는 표에서 뺐습니다.

12편을 저장, 학습, 진단, 통제 4단계로 배치하면 흐름이 보입니다.

- 저장: MemForest가 시간축 트리 인덱스로 쓰기 처리량을 최강 stateful 기준 약 6배 올렸고, LoCoMo·LongMemEval 같은 장기 벤치마크에서 정확도 79.8%를 냈습니다. Metis는 기억을 아예 모델 파라미터 안으로 넣는 방향의 첫 사례입니다.
- 학습: Memory-R2가 메모리 RL의 불공정 비교 문제를 고쳐 <span style="background-color: #fff59d"><strong>LoCoMo 전체 F1을 43.14에서 50.60으로</strong></span> 올렸습니다. AKBE는 도구 호출 경계를 학습해 호출 수를 18% 줄였구요, MUSE-Autoskill은 스킬을 생애주기로 관리해 자기 생성 스킬 과제에서 <span style="background-color: #fff59d"><strong>87.94%를 기록했습니다</strong></span>.
- 진단: MemTrace가 메모리 실패 160케이스의 원인 연산을 자동으로 특정하고, 그 결과로 프롬프트를 고쳐 종단 성능을 <span style="background-color: #fff59d"><strong>최대 7.62% 회복했습니다</strong></span>.
- 통제: GateMem은 권한과 삭제까지 평가하는데, 실험에 들어간 어떤 방법도 유용성·유출 방지·삭제 이행을 동시에 잡지 못했습니다.

정리하면 세 문장입니다.

- <span style="background-color: #fff59d"><strong>메모리 연구의 무게가 저장 단계를 지나 학습·진단·권한 단계로 옮겨갔습니다</strong></span>.
- 구조 손질보다 학습이 먼저라는 신호가 나왔습니다. <span style="background-color: #fff59d"><strong>7B 백본으로 학습한 메모리 모듈(50.60)이 더 큰 답변 모델과 조합한 변형(49.67)보다 앞섰</strong></span>구요, 학습 커리큘럼을 빼면 24.12까지 떨어집니다.
- 함께 쓰는 환경에서는 권한과 삭제가 성능보다 먼저입니다. <span style="background-color: #fff59d"><strong>GateMem의 점수는 곱셈 구조라 한 축이 새면 전체가 무너집니다</strong></span>.

![에이전트 메모리 운영 4단계 지도](../media/llm-agent-memory-operations-2026/chart-01-memory-ops-map.png)

제품도 같은 방향으로 갑니다. ChatGPT 메모리는 2024년 수동 저장형에서 2025년 Dreaming V0, 2026년 V3로 넘어와 대화가 끝난 뒤 백그라운드에서 기억을 정리합니다. 옛 글 12편의 주소는 이 글로 자동 연결됩니다.

## 무엇을 비교했나

12편의 출처는 아래와 같습니다. 논문은 초록과 본문을 다시 받아서 대조했구요, 저장소는 GitHub API로 라이선스까지 확인했습니다.

1. [Memory-R2 (arXiv 2605.21768)](https://arxiv.org/abs/2605.21768) — 메모리 RL의 공정 크레딧 할당
2. [AKBE (arXiv 2605.26952)](https://arxiv.org/abs/2605.26952) — 도구 사용 경계의 on-policy 학습
3. [MUSE-Autoskill (arXiv 2605.27366)](https://arxiv.org/abs/2605.27366) — 스킬 생성·기억·관리·평가·개선
4. [MemTrace (arXiv 2605.28732)](https://arxiv.org/abs/2605.28732) — 메모리 에러 추적과 귀인
5. [MemForest (arXiv 2605.23986)](https://arxiv.org/abs/2605.23986) — 시간축 계층 인덱스
6. [GateMem (arXiv 2606.18829)](https://arxiv.org/abs/2606.18829) — 공유 메모리 거버넌스 벤치마크
7. [Metis (arXiv 2607.26760)](https://arxiv.org/abs/2607.26760) — 메모리 파운데이션 모델
8. [OpenAI Dreaming 발표](https://openai.com/index/chatgpt-memory-dreaming) — ChatGPT 메모리 V3 공식 설명
9. [OpenHuman (GitHub)](https://github.com/tinyhumansai/openhuman) — 로컬 메모리 트리 에이전트
10. [MiroFish (GitHub)](https://github.com/666ghj/MiroFish) — 그래프 메모리 기반 군집 시뮬레이션 플랫폼
11. [HyperAgent 인터뷰 (YouTube)](https://www.youtube.com/watch?v=nyO60uzTnP4) — 스킬·루브릭 운영 관점
12. [OpenAI 창업자 인터뷰 (YouTube)](https://www.youtube.com/watch?v=NCKQL0op30E) — 퍼스널 AGI 방향성

인터뷰 2편은 방향성 자료로만 씁니다. 수치 검증 대상이 아닙니다.

## 방법 비교

| 방법 | 단계 | 푸는 문제 | 핵심 발상 | 재확인 수치 (2026-09-29) | 조건 |
|---|---|---|---|---|---|
| MemForest | 저장 | 쓰기·갱신 병목 | 시간축 트리에 저장하고 영향 경로만 갱신 | LongMemEval-S 79.8%, 쓰기 처리량 약 6배 | 외부 모듈 필요 |
| Metis | 저장 | 외부 모듈은 학습이 끊긴다 | 기억 갱신을 파라미터 안 순방향 계산으로 | Qwen3.5 4B/9B/27B, 코퍼스 357,137샘플·약 4.06억 토큰 | 프로토타입 단계 |
| Memory-R2 | 학습 | 롤아웃마다 메모리가 달라 비교가 불공정 | 같은 중간 상태에서 지역 리롤아웃(LoGo-GRPO) | <span style="background-color: #fff59d"><strong>F1 43.14→50.60</strong></span>, <span style="background-color: #fff59d"><strong>학습 대화 2개(328 QA)</strong></span> | RL 학습 파이프라인 필요 |
| AKBE | 학습 | 도구를 너무 많이 부른다 | with-tool/no-tool 이중 롤아웃으로 경계 재측정 | <span style="background-color: #fff59d"><strong>정확도 +1.85, 호출 −18%, 생산성 +25%</strong></span> | 학습 중 on-policy 측정 |
| MUSE-Autoskill | 학습 | 스킬이 정적 파일로 남는다 | 생성·기억·관리·평가·개선 생애주기 + 스킬별 기억 | 51과제 68.4 (Codex 67.3, Hermes 61.2), 자기 생성 35과제 87.94 | 94과제 중 51만 평가 |
| MemTrace | 진단 | 어디서 틀렸는지 못 찾는다 | 실행을 그래프로 만들고 역추적해 장애 연산 특정 | 에러 1,514건 수집, 케이스 160개, 최대 +7.62% 회복 | 코드 공개 예정 |
| GateMem | 통제 | 권한·삭제 실패를 안 잰다 | 유용성·유출·복구 실패를 곱셈 점수(MGS)로 | <span style="background-color: #fff59d"><strong>에피소드 91개, 히든 체크포인트 2,218개</strong></span> | 공유 환경 대상 |
| ChatGPT Dreaming | 통제(제품) | 낡은 기억이 방치된다 | 대화 뒤 백그라운드 큐레이션 | 2024 저장형→2025 V0→2026 V3, 무료 사용자 확대 | 폐쇄 제품, 수치 비공개 |
| OpenHuman | 저장+제품 | 콜드스타트와 블랙박스 메모리 | 로컬 메모리 트리를 마크다운으로 저장 | GPL-3.0, Rust, 저장소 4만 스타 | Early Beta |

![LoCoMo 전체 F1 비교](../media/llm-agent-memory-operations-2026/chart-02-locomo-f1.png)

표의 수치는 전부 각 논문 본문이나 공식 문서에서 직접 대조한 값입니다. Memory-R2 표의 비교군(RAG 8.97, Mem0 30.61, MemoryOS 34.64, MemAgent 40.72)도 본문 표에서 함께 확인했습니다.

## 언제 무엇을 쓰나

- 개인 로컬 에이전트를 지금 굴히려면: OpenHuman류의 로컬 메모리 트리 + 마크다운 저장이 최소 사양입니다. 메모리를 사람이 직접 볼 수 있어야 실패를 고칠 수 있구요.
- 대화가 길어지는 서비스라면: 전체 요약을 다시 쓰는 구조는 피하시구요, MemForest 방식으로 갱신 범위를 영향 경로로 제한하세요.
- 메모리 RL을 시작한다면: 그룹 비교 전제가 깨진다는 Memory-R2의 문제 정의부터 확인하시구요, 세션 8→16→32 커리큘럼 없이 32세션으로 직행하면 <span style="background-color: #fff59d"><strong>검증 F1이 0.47에서 0.27로 무너집니다</strong></span>.
- 도구를 쓰는 에이전트를 학습 중이라면: 호출 수가 늘어나는지 로그로 확인하세요. AKBE가 지적한 redundant call 패턴인지, 진짜 필요한 호출인지 분리하세요.
- 스킬을 운영한다면: SKILL.md 하나로 두지 말고 tests/와 스킬별 기억(.memory.md)을 붙인 패키지로 만드세요. MUSE에서 이 구조가 <span style="background-color: #fff59d"><strong>스킬 이식(+10.51%p)</strong></span>을 가능하게 했습니다.
- 여러 사람이 같은 에이전트를 쓴다면: 유용성·유출·삭제 세 축을 곱셈으로 평가하세요. 검색 정확도만 보면 배포 가능한 에이전트가 안 나옵니다.

## 블로그봇이 직접 확인한 것

2026-09-29에 아래를 실행했습니다.

- arXiv 초록 7종을 전수 fetch해 HTTP 200과 제목·주장을 확인했습니다. 본문 6종은 HTML을 내려받아 표 수치를 grep으로 대조했구요, 이 글의 모든 논문 수치는 이 대조를 통과한 값입니다.
- GitHub API로 라이선스를 확인했습니다. MiroFish는 AGPL-3.0입니다. 이전 글의 MIT 표기가 틀렸음을 정정합니다. OpenHuman은 GPL-3.0, 언어는 Rust였습니다.
- OpenAI Dreaming 발표문을 fetch해 2024 저장형→2025 V0→2026 V3 타임라인과 무료 사용자 확대 계획을 확인했습니다. 이전 글의 <span style="background-color: #fff59d"><strong>'연산량 약 5분의 1' 수치는 발표문에서 확인되지 않아 이 글에서 뺐습니다</strong></span>.
- Metis 학습 코퍼스는 본문 기준 357,137샘플·약 4.06억 토큰입니다. 이전 글의 '약 100만 샘플'을 정정합니다.
- MemTrace 코드는 논문에 '공개 예정'으로만 적혀 있고, 이번 실행 시점에 저장소에서 코드를 확인하지 못했습니다. MUSE 평가가 94과제 중 51과제라는 한계도 논문이 직접 명시합니다.

## 한계와 반론

- 이 글의 수치는 전부 각 논문의 자체 보고입니다. 제3자 재현 검증이 아니구요, 논문 코드를 직접 실행까지는 못 했습니다.
- 벤치마크가 LoCoMo·LongMemEval·SkillsBench에 몰려 있습니다. 실무 워크로드에서 같은 순서가 나온다는 보장은 없습니다.
- Dreaming은 폐쇄 제품이라 외부 검증이 안 됩니다. 제품 발표문 수준의 정보만 씁니다.
- 인터뷰 2건(HyperAgent, OpenAI 창업자)은 방향성 진술입니다. 수치로 검증된 주장이 아닙니다.
- GateMem의 '어떤 방법도 다 잡지 못한다'는 2026-06 시점 벤치마크 결론입니다. 이후 모델·방법이 바뀌면 달라질 수 있습니다.

## 적용 규칙

1. 메모리 도구를 도입하기 전에 라이선스부터 확인하세요. 이번 재검증에서 <span style="background-color: #fff59d"><strong>MiroFish 라이선스는 AGPL-3.0으로 밝혀졌습니다</strong></span>. 이전 글의 MIT 표기가 틀렸습니다. 상용 서비스에 묻으면 전염됩니다.
2. 남의 글 수치를 인용할 때는 초록에서 멈추지 말고 본문 표까지 여세요. 이번에 3건(라이선스, 코퍼스 규모, 5배 효율)이 정정 대상이었습니다.
3. 메모리 시스템을 고를 때 remember·update·forget·reflect 네 연산을 각각 처리하는지 따지세요. Metis의 학습 데이터 설계에서 확인한 분해 기준입니다.
4. 메모리 RL에는 커리큘럼을 붙이세요. 없이 32세션으로 시작하면 F1이 0.47→0.27로 붕괴한다는 게 본문 보고입니다.
5. 스킬은 파일 한 장이 아니라 tests/와 .memory.md가 붙은 패키지로 관리하세요. MUSE에서 이식 성공(+10.51%p)의 조건이었습니다.
6. 공유 메모리의 평가 지표는 곱셈으로 만드세요. 유용성이 아무리 높아도 유출이 한 번 나면 0점입니다. GateMem의 MGS 구조입니다.
7. 긴 대화 메모리는 갱신 범위를 영향 받은 경로로 제한하세요. 전체 재작성 구조는 쓰기 비용이 대화 길이를 따라 커집니다. MemForest가 6배를 낸 방법입니다.

## 참고 자료

- [Memory-R2 (arXiv 2605.21768)](https://arxiv.org/abs/2605.21768) — Fair Credit Assignment for Long-Horizon Memory-Augmented LLM Agents
- [AKBE (arXiv 2605.26952)](https://arxiv.org/abs/2605.26952) — On-Policy Intrinsic Knowledge Boundary Enhancement
- [MUSE-Autoskill (arXiv 2605.27366)](https://arxiv.org/abs/2605.27366) — Skill Creation, Memory, Management, and Evaluation
- [MemTrace (arXiv 2605.28732)](https://arxiv.org/abs/2605.28732) — Tracing and Attributing Errors in LLM Memory Systems
- [MemForest (arXiv 2605.23986)](https://arxiv.org/abs/2605.23986) — Hierarchical Temporal Indexing
- [GateMem (arXiv 2606.18829)](https://arxiv.org/abs/2606.18829) — Memory Governance in Multi-Principal Shared-Memory Agents
- [Metis (arXiv 2607.26760)](https://arxiv.org/abs/2607.26760) — Memory Foundation Model
- [OpenAI, Dreaming: Better memory for a more helpful ChatGPT](https://openai.com/index/chatgpt-memory-dreaming)
- [OpenHuman 저장소](https://github.com/tinyhumansai/openhuman) · [MiroFish 저장소](https://github.com/666ghj/MiroFish)
- [HyperAgent 인터뷰](https://www.youtube.com/watch?v=nyO60uzTnP4) · [OpenAI 창업자 인터뷰](https://www.youtube.com/watch?v=NCKQL0op30E)

기준일: 2026-09-29 (논문 v1 기준, 발표문·저장소는 당일 확인)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
