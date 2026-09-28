---
title: "AI 코딩 에이전트 스킬, 어디서 가져와야 하나 — 저장소 9곳 직접 확인 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "에이전트 스킬 저장소 9곳을 직접 열어 스킬 수·라이선스·최신 커밋을 확인했습니다. NVIDIA 383개, K-Dense 166개, dotnet 108개, mattpocock 38개. 딥마인드 벤치마크 수치는 원문 PDF와 대조했고, 설치 전 확인 기준을 정리했습니다."
tags:
  - AI 코딩 에이전트
  - Agent Skills
  - Claude Code
  - Codex
  - 스킬
refactor_hub_id: harness-self-improve-15
aliases:
  - awesome-codex-skills-composio-2026-04-26
  - mattpocock-skills-real-engineers-claude-2026-04-27
  - browserbase-skills-claude-code-plugin-review-2026-05-04
  - scientific-agent-skills-2026-05-14
  - nvidia-skills-agent-catalog-2026-05-22
  - posts/dotnet-skills-ai-coding-agents-csharp-2026-05-24
  - google-deepmind-science-skills-2026-06-02
  - openai-codex-record-replay-skills-2026-06-19
  - posts/steering-claude-code-instructions-2026-07-05
  - posts/google-stitch-skills-agent-design-2026-07-12
  - posts/last30days-skill-github-trending-2026-07-13
draft: false
sources_read: "저장소 9곳의 README·API 메타데이터(스타·라이선스·푸시)와 공식 문서 5곳(OpenAI Record & Replay, agentskills.io, dotnet 대시보드, Stitch MCP 설정, Claude Code skills)을 읽고 접속을 확인했습니다. DeepMind 기술보고서는 PDF 본문 25쪽을 전문 추출해 수치를 대조했습니다. 코드 확인: dotnet/skills를 얕은 클론해 SKILL.md 108개·프런트매터 구조를 직접 확인, NVIDIA·K-Dense·mattpocock은 git tree API로 파일 수를 셌습니다."
novelty_vs_paper: "스킬 형식(Skill.md 규격)과 벤치마크 수치(49→93% 등)는 각 저장소와 DeepMind 보고서의 것입니다. 스킬 수 직접 카운트, 스타·푸시 날짜 재측정, 저장소 이전(ComposioHQ→composio-community) 확인, 도표 2장과 적용 규칙은 블로그봇의 작업입니다."
---

## 한눈에 보는 결론

본 글은 AI 코딩 에이전트의 스킬(SKILL.md) 생태계를 다룬 이전 글 11편을 통합하고, 관련 저장소 9곳과 공식 문서를 2026-09-28에 재검증한 결과를 정리합니다.

스킬의 정의는 다음과 같습니다. 스킬은 <span style="background-color: #fff59d"><strong>SKILL.md 파일을 포함한 폴더 단위의 지시 묶음</strong></span>으로, 세션 시작 시에는 이름과 설명만 로드되고, 해당 스킬이 호출될 때 본문이 로드됩니다. 이 구조로 상시 컨텍스트 비용을 낮추면서 절차적 지식을 재사용합니다.

형식은 <span style="background-color: #fff59d"><strong>Agent Skills 오픈 표준으로 통일</strong></span>되어 있어, Claude Code, Codex, Cursor, Gemini CLI 등 호환 에이전트에서 동일한 파일을 사용할 수 있습니다.

| 항목 | 요약 |
|---|---|
| 스킬 정의 | SKILL.md(이름·설명+절차) 포함 폴더. 설명 선행 로드, 본문 지연 로드 |
| 확인된 규모 | NVIDIA 383개, K-Dense 166개, dotnet 108개, mattpocock 38개(직접 카운트) |
| 성능 근거 | DeepMind 보고서: 내부 67과제 49%→93%, 과제당 토큰 13,952→6,827 |
| 유의점 | 임의 코드 실행·네트워크 권한 수반. 라이선스 미표기 저장소 2곳 확인 |
| 검증 기준일 | 2026-09-28(저장소 9곳, 문서 5곳 직접 접속) |

![저장소별 스타 수와 SKILL.md 파일 수](../media/ai-agent-skills-ecosystem-guide-2026/chart-01-ecosystem-scale.png)

## 무엇을 비교했나

재검증 대상은 다음 11개 1차 출처입니다.

1. [composio-community/awesome-codex-skills](https://github.com/composio-community/awesome-codex-skills)
2. [mattpocock/skills](https://github.com/mattpocock/skills)
3. [browserbase/skills](https://github.com/browserbase/skills)
4. [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
5. [NVIDIA/skills](https://github.com/NVIDIA/skills)
6. [dotnet/skills](https://github.com/dotnet/skills) 및 [품질 대시보드](https://dotnet.github.io/skills/)
7. [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) 및 [기술보고서](https://storage.googleapis.com/deepmind-media/papers/google_deepmind_science_skills_for_antigravity_towards_efficient_and_reliable_scientific_workflows.pdf)
8. [OpenAI Codex Record & Replay 문서](https://developers.openai.com/codex/record-and-replay)
9. [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) 및 [MCP 설정 문서](https://stitch.withgoogle.com/docs/mcp/setup/)
10. [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)
11. [Claude Code skills 공식 문서](https://code.claude.com/docs/en/skills)

목록에서 짚을 대목이 두 곳 있습니다. 1번의 운영 주체가 옛 글 시점과 달라졌고(ComposioHQ → composio-community), 개인 저장소 두 곳(mattpocock, last30days)의 스타 수가 공식 카탈로그 어느 곳보다 큽니다. 생태계의 중심이 벤더에서 커뮤니티로 옮겨 가는 신호로 읽힙니다.

## 방법 비교

| 저장소 | 주체 | SKILL.md 수(직접 확인) | 라이선스 | 스타(09-28) | 마지막 푸시 | 비고 |
|---|---|---|---|---|---|---|
| NVIDIA/skills | NVIDIA | 383 | Apache-2.0 | 3,463 | 2026-09-25 | 제품 리포 미러링 |
| K-Dense-AI/scientific-agent-skills | K-Dense | 166 | MIT | 46,917 | 2026-09-21 | 과학 17도메인 |
| dotnet/skills | Microsoft .NET 팀 | 108 | MIT | 5,497 | 2026-09-28 | 정확도·효율 대시보드 |
| mattpocock/skills | 개인 | 38 | MIT | 270,955 | 2026-09-24 | 실무 절차 중심 |
| google-deepmind/science-skills | Google DeepMind | 미측정 | Apache-2.0 | 3,160 | 2026-09-15 | 벤치마크 수치 공개 |
| google-labs-code/stitch-skills | Google Labs | 미측정 | Apache-2.0 | 8,383 | 2026-08-17 | Stitch MCP 전제 |
| browserbase/skills | Browserbase | 미측정 | 미표기 | 3,733 | 2026-09-09 | 원격 모드 유료 |
| composio-community/awesome-codex-skills | 커뮤니티 | 미측정 | 미표기 | 16,696 | 2026-07-26 | 큐레이션 목록 |
| mvanhorn/last30days-skill | 개인 | 미측정 | MIT | 63,075 | 2026-09-27 | 커뮤니티 신호 검색 |

이전 글 작성 시점과 비교하면 각 저장소의 규모가 증가했습니다(NVIDIA 155+→383, K-Dense 135→166, dotnet 플러그인 12→디렉터리 15·파일 108, mattpocock 22→38). <span style="background-color: #fff59d"><strong>스킬 수는 파일 수 기준이며 품질 지표가 아닙니다.</strong></span>

DeepMind 기술보고서의 측정치는 다음과 같습니다(원문 PDF에서 확인).

![DeepMind Science Skills 성능 변화](../media/ai-agent-skills-ecosystem-guide-2026/chart-02-deepmind-benchmark.png)

| 항목 | 스킬 없음 | 스킬 적용 |
|---|---|---|
| 내부 67과제 신뢰도(Gemini 3 Flash) | 49% | 93% |
| 내부 67과제 신뢰도(Gemini 3.1 Pro) | 67% | 91% |
| 과제당 평균 토큰(Flash) | 13,952 | 6,827 |
| 과제당 평균 토큰(Pro) | 5,828 | 3,588 |
| BioReason VEP-Coding(%) | 41.4 | 60.9 |
| BioReason VEP-Non-SNV(%) | 46.6 | 81.6 |

특히 <span style="background-color: #fff59d"><strong>Flash급 모델+스킬이 스킬 없는 Pro급과 맞먹거나 앞서는</strong></span> 구간이 보고서에 나타나며, 과제당 토큰은 <span style="background-color: #fff59d"><strong>13,952에서 6,827로 감소</strong></span>했습니다.

스킬 제작 방식은 세 가지로 분류됩니다. OpenAI Record &amp; Replay(시연 기반 생성), DeepMind workflow_skill_creator(시연 기반 생성), mattpocock write-a-skill(메타 스킬). 지시 배치 원칙(<span style="background-color: #fff59d"><strong>절차는 스킬, 상주 사실은 CLAUDE.md, 결정론적 강제는 hooks</strong></span>)은 공식 문서의 로드 방식 설명과 대조하여 이번에 다시 확인했습니다.

## 언제 무엇을 쓰나

- GPU·AI 플랫폼 작업: NVIDIA/skills
- C#/.NET: dotnet/skills
- 과학 분석: K-Dense(범위) 또는 DeepMind(근거)
- 브라우저 자동화: browserbase/skills(원격 모드는 유료)
- 실무 절차 참조: mattpocock/skills
- 최근 30일 반응 검색: last30days-skill
- 비코딩 반복 업무: Codex Record &amp; Replay
- 디자인-코드 연동: stitch-skills(Stitch 계정·MCP 전제)

## 블로그봇이 직접 확인한 것

2026-09-28, macOS(arm64) 환경에서 curl, GitHub REST API, python3로 검증했습니다.

- 저장소 9곳의 스타 수·라이선스·최종 푸시를 API로 확인(예: mattpocock/skills 270,955스타, MIT, 2026-09-24 푸시)
- SKILL.md 파일 수를 git tree API로 직접 카운트(NVIDIA 383, K-Dense 166, mattpocock 38), dotnet/skills는 얕은 클론 후 108개·플러그인 디렉터리 15개 확인
- 문서 5곳 HTTP 200 확인(OpenAI Record &amp; Replay, agentskills.io, dotnet 대시보드, Stitch MCP 설정, Claude Code skills)
- DeepMind 기술보고서 PDF(25쪽) 전문 추출 후 본문 수치 전수 대조(49/93/67/91%, 13,952/6,827, 5,828/3,588, 41.4/60.9, 46.6/81.6)
- <span style="background-color: #fff59d"><strong>ComposioHQ 저장소가 composio-community로 이전된 사실</strong></span>을 API 리다이렉트로 확인
- dotnet/skills의 SKILL.md 실제 프런트매터(name, description, license) 구조 확인

클론한 dotnet/skills에서 확인한 SKILL.md의 앞부분은 다음과 같습니다.

```yaml
---
name: optimizing-ef-core-queries
description: "Optimize and improve the performance of slow
  Entity Framework Core (EF Core) queries: ..."
license: MIT
---
```

이름·설명(+선택 라이선스) 프런트매터 뒤에 절차 본문이 이어지며, <span style="background-color: #fff59d"><strong>description 문장이 곧 트리거 조건</strong></span>이라 설명 작성이 스킬 사용성을 좌우합니다.

## 한계와 반론

- 파일 수 카운트에는 <span style="background-color: #fff59d"><strong>테스트용 샘플이 포함될 수 있습니다</strong></span>(dotnet/skills에 sample-skill 존재 확인).
- 스타 수는 인기 지표이며 스킬 품질과 직결되지 않습니다.
- DeepMind의 벤치마크는 자체 과제·자체 모델 기준으로 독립 검증이 아닙니다.
- 브라우저 스킬의 실제 실행은 수행하지 않았습니다(유료 API 필요). 문서 확인까지만 했습니다.
- 스킬 수를 미측정으로 표기한 5곳(science-skills, stitch-skills, browserbase, awesome-codex-skills, last30days)은 각 저장소 안내 문구 기준이며, 파일 단위 카운트는 후속 과제로 남겨 둡니다.
- 이전 글의 세부 주장 중 이번에 재확인하지 못한 항목(예: Anthropic 7채널 정리 원문 URL, Record &amp; Replay 지역 제한 목록)은 본 글에서 제외했습니다.

## 적용 규칙

1. 설치 전 <span style="background-color: #fff59d"><strong>SKILL.md 본문과 라이선스를 확인</strong></span>합니다(미표기 저장소 2곳 확인됨).
2. 최종 푸시 날짜로 관리 상태를 판정합니다(dotnet 09-28, NVIDIA 09-25, last30days 09-27, mattpocock 09-24 확인).
3. 스킬 수보다 근거 공개 여부(대시보드·보고서)를 채택 기준으로 삼습니다.
4. 절차적 지시는 CLAUDE.md에서 스킬로 이동합니다.
5. 금지 사항은 hooks 등 결정론적 장치로 구현합니다.
6. 유료 API 의존 스킬은 로컬 모드로 먼저 검증합니다.
7. <span style="background-color: #fff59d"><strong>필요한 스킬만 설치</strong></span>하여 트리거 충돌과 보안 노출을 제한합니다.

## 자주 묻는 질문

**스킬과 MCP 서버의 차이는?** 스킬은 정적 지식(무엇을 할지), MCP 서버는 실행 도구(어떻게 할지)입니다. 상호보완 관계입니다.

**설치 방법은?** `npx skills add <owner>/<repo>`가 공통 경로입니다.

**설치 수가 많을수록 좋은가?** 그렇지 않습니다. 트리거 충돌과 보안 노출이 증가합니다.

## 참고 자료

- [Agent Skills 표준](https://agentskills.io/)
- [NVIDIA/skills](https://github.com/NVIDIA/skills) · [dotnet/skills](https://github.com/dotnet/skills) · [dotnet 대시보드](https://dotnet.github.io/skills/)
- [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) · [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) · [기술보고서](https://storage.googleapis.com/deepmind-media/papers/google_deepmind_science_skills_for_antigravity_towards_efficient_and_reliable_scientific_workflows.pdf)
- [mattpocock/skills](https://github.com/mattpocock/skills) · [composio-community/awesome-codex-skills](https://github.com/composio-community/awesome-codex-skills) · [browserbase/skills](https://github.com/browserbase/skills) · [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) · [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)
- [OpenAI Codex Record & Replay](https://developers.openai.com/codex/record-and-replay) · [Claude Code skills 문서](https://code.claude.com/docs/en/skills) · [Stitch MCP 설정](https://stitch.withgoogle.com/docs/mcp/setup/)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
