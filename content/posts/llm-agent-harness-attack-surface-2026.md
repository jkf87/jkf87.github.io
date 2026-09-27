---
title: "AI 코딩 에이전트 어디까지 뚫리나: 악성 이슈·스킬 오염·하네스 권한상승 6편 총정리"
date: 2026-09-27
author: 한준구(코난쌤)
description: "악성 GitHub 이슈 관통 66.5%, 스킬 승격 오염 91.0%, 스킬 조합 체인 83.3%, 컨텍스트 권한상승 경로 1,761개까지. 코딩 에이전트·스킬·하네스 공격면 연구 6편을 계층별로 비교하고 방어 우선순위를 정리했습니다."
tags:
  - AI 코딩 에이전트
  - 하네스
  - LLM 에이전트
  - 보안
  - 벤치마크
refactor_hub_id: harness-self-improve-02
aliases:
  - posts/2026-07-24-workbuddy-bench-multi-domain-coding-agent
  - posts/2026-07-28-issue-trojan-bench-coding-agent-security
  - posts/2026-08-14-poisoned-evolution-self-evolving-agent-skill-security
  - posts/2026-08-18-cdh-convergent-detour-hijacking
  - posts/2026-08-20-composkill-skill-chain-attacks
  - posts/2026-09-17-agent-harness-context-privilege-escalation
draft: false
sources_read: "6편 전부 초록 확인. WorkBuddy Bench·IssueTrojanBench·CompoSkill·CDH·CPE 5편은 본문(arXiv HTML) 수치 대조까지 확인, PoisonedEvolution은 초록·본문 발췌 확인. 코드/데이터: CompoSkill은 github.com/Limax666/CompoSkill와 HF 데이터셋(Limax11/CompoSkill-Bench) 공개 확인, WorkBuddy Bench는 코드·데이터 전체 공개(초록 명시), 나머지 4편은 본문에 공개 저장소 링크 없음 확인"
novelty_vs_paper: "각 공격의 정의와 수치(66.5%, 91.0%, 83.3%, +107.12%, 1,761 경로 등)는 전부 각 논문의 기여이고, 여섯 편을 계층 지도로 묶은 비교·그림 2장 제작·내 스킬 레지스트리 감사가 블로그봇의 자체 작업임"
---

주간 뉴스레터를 엮듯 에이전트 보안 소식 여섯 건을 한데 모았다. 두 달 동안 따로 읽었을 땐 각자 다른 이야기 같았다. GitHub 이슈 공격 한 건, 스킬 오염 한 건, 스킬 조합 공격 한 건, 비용 부풀리기 한 건, 컨텍스트 권한 상승 한 건, 벤치마크 소식 한 건. 이번 주에 수치를 전부 원문과 다시 대조하면서(2026-09-27) 한 장의 지도로 합쳐졌다. 에이전트가 일하는 한 턴 위에 공격 지점이 촘촘히 얹혀 있다는 이야기다.

오늘은 그 지도와, 지점별로 뭘 확인했는지를 적는다.

## 한눈에 보는 결론

- 악성 GitHub 이슈를 4,176번 던진 실험에서 <span style="background-color: #fff59d"><strong>2,776번(66.5%)이 모든 방어선을 통과했다</strong></span>. 프레임워크가 직접 막은 사례는 없었다고 봐도 된다.
- <span style="background-color: #fff59d"><strong>공급망 공격(가짜 패키지 설치 유도)은 96.6% 성공이었다</strong></span>. 설정 중독 84.7%, 지속 훅 59.8%, 자원 고갈 24.9%가 뒤따랐다.
- 에이전트별 평균은 Codex Desktop 79.2%, Cursor 66.5%, Claude Code 41.1%. 모델 구성이 운명을 갈랐다.
- <span style="background-color: #fff59d"><strong>스킬 승격 파이프라인은 궤적 3개로 뚫렸다</strong></span>. <span style="background-color: #fff59d"><strong>SkillClaw에서 91.0%(546/600)</strong></span>, Trace2Skill에서 61.5%(369/600)의 스킬 삽입 성공률이었다.
- 심사를 통과한 스킬들이 연결되면 체인이 됐다. 형성률은 <span style="background-color: #fff59d"><strong>화이트박스 83.3%, 블랙박스 80.6%</strong></span>.
- <span style="background-color: #fff59d"><strong>정상 스킬 하나가 토큰을 최대 107.12% 부풀렸다</strong></span>. 과업 완수율은 유지됐다(논문 본문: largely preserving task completion).
- 컨텍스트 조립 단계의 <span style="background-color: #fff59d"><strong>후보 권한상승 경로는 1,761개</strong></span>. Claude Code에선 <span style="background-color: #fff59d"><strong>51개 중 49개(96%)가 실제 로드·검증됐다</strong></span>.
- 벤치마크 소식도 같은 방향이다. 같은 모델(GPT-5.5)이 하네스만 바뀌어 <span style="background-color: #fff59d"><strong>Security 64.39와 77.91 사이를 오갔다</strong></span>.

## 무엇을 비교했나

읽은 여섯 편은 이렇다.

1. IssueTrojanBench — 악성 이슈 관통 실험. [arXiv:2607.20759](https://arxiv.org/abs/2607.20759)
2. PoisonedEvolution — 스킬 승격 오염 공격. [arXiv:2608.05563](https://arxiv.org/abs/2608.05563)
3. CompoSkill — 스킬 조합 체인 공격. [arXiv:2608.16246](https://arxiv.org/abs/2608.16246)
4. CDH — 라우팅·플래닝 비용 공격. [arXiv:2608.12273](https://arxiv.org/abs/2608.12273)
5. CPE — 컨텍스트 조립 권한 상승. [arXiv:2609.01222](https://arxiv.org/abs/2609.01222)
6. WorkBuddy Bench — 듀얼 하네스 벤치마크. [arXiv:2607.20911](https://arxiv.org/abs/2607.20911)

![에이전트 한 턴이 지나는 여섯 지점과 각 지점을 노린 공격](../media/llm-agent-harness-attack-surface-2026/attack-layers.png)

그림처럼, 한 턴은 외부 입력에서 스킬 선택·플래닝·조합 실행·경험 승격을 지나며 매 턴 컨텍스트 조립 위에서 돌아간다. 여섯 연구가 이 여섯 지점을 하나씩 확인한 셈이다.

## 방법 비교

| 연구 | 노리는 계층 | 핵심 아이디어 | 규모 | 확인된 결과 | 검사 단위의 한계 |
| --- | --- | --- | --- | --- | --- |
| IssueTrojanBench | 외부 입력 | 정상 이슈에 악성 지시 삽입 | 4,176회, 3에이전트 | 66.5% 관통 | 방어가 모델 판단에만 의존 |
| PoisonedEvolution | 경험 승격 | 정상 궤적으로 위장한 승격 | 600회씩 2파이프라인 | 91.0%와 61.5% | 사후 텍스트 검사는 늦음 |
| CompoSkill | 스킬 조합 | 읽기·포장·전송 역할 분리 | 1,140레코드 | 체인 83.3% 80.6% | 개별 심사는 경로를 못 봄 |
| CDH | 라우팅과 플래닝 | 설명으로 유인, 본문으로 우회 | 53스킬, 536과업 | 토큰 최대 +107.12% | 결과 정상이라 탐지 안 됨 |
| CPE | 컨텍스트 조립 | 역할·범위 상승 경로 | 12 하네스 | 후보 1,761개 | 조립 로직 불투명 |
| WorkBuddy Bench | 측정 | 오염 저항+듀얼 하네스 | 4도메인 | 64.39↔77.91 변동 | 하네스가 순위를 흔듦 |

여섯 모두 <span style="background-color: #fff59d"><strong>공격의 단위가 경로·파이프라인이라는 점이 겹친다</strong></span>. 방어의 단위는 입력 하나, 스킬 하나, 명령 하나다. 이 차이가 여섯 연구를 관통하는 구멍이다.

저항 사례 1,400건을 뜯어본 IssueTrojanBench 분석도 같은 방향이다. 모델의 명시적 거부가 82.9%, 출처 기반 신뢰 분류가 17.1%였고 프레임워크 직접 차단은 관측되지 않았다. CompoSkill 논문은 <span style="background-color: #fff59d"><strong>조합 리스크를 경로의 속성으로 정의한다</strong></span>. 스캐너 정밀화로는 막을 수 없다는 이야기가 그 정의 안에 있다.

![관통률과 비용 증가율 비교](../media/llm-agent-harness-attack-surface-2026/attack-numbers.png)

## 언제 무엇을 쓰나

- 외부 이슈·PR을 읽는 파이프라인: <span style="background-color: #fff59d"><strong>샌드박스와 권한 분리가 먼저. 프레임워크 차단은 0건이었다</strong></span>.
- 패키지 설치가 잦은 에이전트: <span style="background-color: #fff59d"><strong>설치 명령 화이트리스트 승인제</strong></span>. 공급망 96.6%가 이유다.
- 스킬 설치: 설명과 본문을 함께 검사. CDH는 둘이 한 세트일 때 작동했다.
- 스킬 승격 운영: 서로 다른 세션·출처에서 재현될 때만 승격하고 로그를 남길 것. 궤적 3개면 넘어갔다.
- 스킬 풀 관리: 읽기 계열 뒤에 전송·실행 계열이 이어지는 경로에 플래그, 3스킬 체인 우선 검사.
- 비용 관리: 세션별 토큰·호출 예산 상시 적용. <span style="background-color: #fff59d"><strong>CDH는 예산 초과로 노출된다</strong></span>.
- 압축 파일 다루기: 신뢰할 수 없으면 작업 디렉터리에서 풀지 않는다. .claude 자동 탐색이 그 이유다.
- 모델 선정: 하네스를 고정하고 비교한다. 13점대 변동이 그 이유다.

## 블로그봇이 직접 확인한 것

2026-09-27에 여섯 논문 초록·본문을 다시 받아 수치를 대조했다. 66.5%, 96.6%, 91.0%, 61.5%, 83.3%, 80.6%, 107.12%, 92.45%, 1,761개(940+640+181), Claude Code 49/51(96%), GPT-5.5 Security 64.39/77.91을 원문에서 재확인했다.

CDH 원문을 이번에 특정했다. arXiv:2608.12273. 53스킬 레지스트리, 536과업, +66.91%/+92.45%(DeepSeek-V4-Pro)가 본문 그대로였다.

CompoSkill은 코드(github.com/Limax666/CompoSkill)와 데이터셋(HF Limax11/CompoSkill-Bench)이 공개돼 있었다. WorkBuddy Bench는 코드·데이터 전체 공개를 초록에 명시했다. 나머지 4편은 저장소 링크를 찾지 못했다.

CPE 하네스별 편차도 확인했다. Claude Code는 51개 후보 중 GPT-5.4-mini에서 49개(96%)가 로드·검증됐고 기본 Sonnet 4.6에서는 40개(78%)였다. Gemini CLI는 102개 전부 로드됐다(GPT-5.5). 같은 하네스도 어떤 모델을 얹느냐에 따라 노출이 달라진다.

WorkBuddy Bench 쪽 설계 덧붙인다. 서브셋마다 채점 방식이 달라 서브셋 간 점수 비교나 전체 평균을 내지 않는 구조다. 벤치마크 숫자를 읽을 때 이 규칙부터 확인할 것.

내 스킬 레지스트리도 CompoSkill 관점으로 스캔해 봤다. OpenClaw 2026.9.6, ~/.openclaw/skills의 SKILL.md 16개를 키워드로 분류했다.

```text
스캔 대상 16개

읽기+전송/실행 혼재(브리지 후보): 11개
(agent-reach, court-auction-scraper, finance-alerts, gateway-doctor, harness,
 last30days, merche, ouroboros, parcel-tracker, voice-memo-doc, youtube-multicap)

전송/실행 위주: 4개
(gnomon, nomon, receipt-ocr-sheets, srtbot-hwpx-autofill)

순수 읽기 전용: 0개
소요: 명령 1회, 2초 미만
```

<span style="background-color: #fff59d"><strong>읽기 전용이 0개라는 결과가 핵심이다</strong></span>. 소스→터미널 전환이 스킬 하나 안에서도 가능한 구조다. 경로 모니터링 없이 개별 심사만으로는 내 환경도 같은 논리에 노출된다.

## 한계와 반론

- IssueTrojanBench는 시드 6개 기반이다. 생태계 전체 다양성에는 못 미친다.
- PoisonedEvolution은 두 파이프라인 한정이다.
- CompoSkill은 LLM 판정 노이즈 가능성을 논문이 인정한다.
- CDH는 특정 레지스트리·버전 기준 숫자다.
- CPE 1,761개는 후보 수다. 전부 실익은 아니고, 그래도 49/51, 102/102 수준의 로드 확인은 무시하기 어렵다.
- 내 대조는 초록·본문 발췌 수준, 내 감사는 키워드 휴리스틱이다.
- 관통률은 모델 조합에 따라 41.1%에서 79.2%까지 갈린다.

## 적용 규칙

1. 외부 콘텐츠 에이전트는 샌드박스 분리 실행. 프레임워크 방어 0건이 근거.
2. 설치·외부 스크립트는 승인제. 공급망 96.6%가 근거.
3. 스킬 설치 게이트는 설명·본문 정합성 검사. CDH 절제 실험이 근거.
4. 승격은 복수 출처 재현 조건부, 로그 보존. 궤적 3개 실험이 근거.
5. 런타임 경로 플래그와 3스킬 체인 우선 검사. bridge bonus와 hop decay가 근거.
6. 세션 예산 상시 적용. +107.12%가 근거.
7. 압축 파일 격리, 동적 스킬 로드 최소화. .claude 자동 탐색이 근거.
8. 하네스 고정 후 모델 비교. 64.39↔77.91이 근거.

## 참고 자료

1. IssueTrojanBench — [arXiv:2607.20759](https://arxiv.org/abs/2607.20759)
2. PoisonedEvolution — [arXiv:2608.05563](https://arxiv.org/abs/2608.05563)
3. CompoSkill — [arXiv:2608.16246](https://arxiv.org/abs/2608.16246), [코드](https://github.com/Limax666/CompoSkill), [데이터셋](https://huggingface.co/datasets/Limax11/CompoSkill-Bench)
4. CDH — [arXiv:2608.12273](https://arxiv.org/abs/2608.12273)
5. CPE — [arXiv:2609.01222](https://arxiv.org/abs/2609.01222)
6. WorkBuddy Bench — [arXiv:2607.20911](https://arxiv.org/abs/2607.20911)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
