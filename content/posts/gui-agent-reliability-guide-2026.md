---
title: "GUI 에이전트가 무너지는 4가지 지점과 검증 설계: MobileGym·Qwen-UI-Agent·ERPBench 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "GUI 에이전트가 무너지는 네 지점(환경 갭, 조용한 실패, 경계 붕괴, 인터페이스 비효율)과 지점별 해법을 논문 8종의 원문 대조 수치로 정리했습니다."
tags:
  - GUI 에이전트
  - 웹 에이전트
  - LLM 에이전트
  - 벤치마크
  - 에이전트 설계
refactor_hub_id: web-gui-agents-01
aliases:
  - mobilegym-parallel-simulation-mobile-gui-agent-2026-05-28
  - 2026-06-03-mobilegym-gui-agent-simulation
  - 2026-06-14-webchallenger-generalist-web-agent
  - posts/2026-07-31-qwen-ui-agent-foundation-gui-agent
  - posts/2026-09-03-dwm-discriminative-world-models-web-agents
  - posts/2026-09-08-cua-universe-hybrid-gui-cli
  - posts/2026-09-10-jarvisgui-cross-device-gui-agents
  - posts/2026-09-18-gui-agent-erp-reliability-erpbench
  - posts/2026-09-21-recreationworld-hybrid-cua
draft: false
sources_read: "본문: arXiv 8종(2605.26114 MobileGym·2606.10423 WebChallenger·2607.28227 Qwen-UI-Agent·2609.02885 DWM·2609.05374 CUA-Universe·2609.10451 JarvisGUI·2609.17885 ERPBench·2609.22000 RecreationWorld) 초록을 2026-09-30에 fetch해 전수 대조했고, 이 중 DWM·JarvisGUI·RecreationWorld 3종은 본문 HTML까지 fetch해 수치 대조. 코드·데이터: github.com/jayoohwang1/webchallenger와 dhruvpendharkar.github.io/dwm을 HTTP 200으로 직접 확인, RecreationWorld는 논문의 공개 명시(GitHub·Hugging Face·ModelScope)만 확인, MobileGym·Qwen-UI-Agent·CUA-Universe·ERPBench·JarvisGUI 저장소는 이번 실행에서 직접 확인하지 못함"
novelty_vs_paper: "벤치마크 점수·환경 설계·하이브리드 학습 효과·붕괴 진단은 각 논문의 기여임. 이 글의 자체 기여는 9편의 옛 글을 무너짐 4지점(환경 갭·조용한 실패·경계 붕괴·인터페이스 비효율)으로 재배열해 지점별 해법을 매핑한 것, 이번 실행에서 재확인 못 한 수치 6건을 본문에서 제외하고 원문 대조값만 남긴 것, 자체 제작 차트 2장임"
---

## 결론 먼저

"에이전트가 방금 저장 눌렀는데요?" — 화면상으로는 완벽했습니다. 근데 DB를 확인해 보면 다른 값이 들어가 있어요. 이런 조용한 실패가 요즘 GUI 에이전트 연구의 중심 문제입니다.

5월부터 9월까지 이 블로그가 다룬 웹·GUI 에이전트 글 9편을 한 덩어리로 묶어서 다시 정리했습니다. 기준일 2026-09-30, <span style="background-color: #fff59d"><strong>숫자는 전부 이 날 fetch한 원문과 대조한 값</strong></span>입니다.

정리하면 이렇습니다. <span style="background-color: #fff59d"><strong>화면 조작 에이전트는 환경 갭, 조용한 실패, 경계 붕괴, 인터페이스 비효율 네 지점에서 무너진다</strong></span>는 것. 그리고 네 지점마다 해법이 이미 나와 있습니다.

첫 화면에서 기억할 숫자 세 개:

- 시뮬레이션 82.1% → 실기기 92.2% (Qwen-UI-Agent)
- <span style="background-color: #fff59d"><strong>저장 최대 85%, DB 정답 최소 3%</strong></span> (ERPBench)
- <span style="background-color: #fff59d"><strong>1위 모델의 완전 통과 2.8%</strong></span> (RecreationBench)

## 무엇을 비교했나

옛 글 9편이 다룬 논문 8종입니다. 이번 실행에서 초록 8종 전부 HTTP 200으로 다시 확인했고, 3종은 본문 HTML까지 대조했습니다.

1. [MobileGym](https://arxiv.org/abs/2605.26114) — 모바일 시뮬레이션 환경 (EMNLP 2026 Main). 5/28·6/3 두 글이 같은 논문을 다뤄 하나로 합침
2. [WebChallenger](https://arxiv.org/abs/2606.10423) — 오픈 모델 웹 에이전트
3. [Qwen-UI-Agent](https://arxiv.org/abs/2607.28227) — 실기기 중심 GUI 에이전트 기술보고서
4. [DWM](https://arxiv.org/abs/2609.02885) — 구별적 월드 모델
5. [CUA-Universe](https://arxiv.org/abs/2609.05374) — 하이브리드 환경·데이터 파이프라인
6. [JarvisGUI](https://arxiv.org/abs/2609.10451) — 크로스 디바이스 벤치마크 (EMNLP 2026 Main)
7. [ERPBench](https://arxiv.org/abs/2609.17885) — 엔터프라이즈 신뢰성 벤치마크
8. [RecreationWorld](https://arxiv.org/abs/2609.22000) — 하이브리드 CUA 환경

## 방법 비교

| 프레임워크 | 겨냥한 지점 | 핵심 방법 | 원문 대조 수치 |
|---|---|---|---|
| MobileGym | 환경 갭 | 브라우저 시뮬레이션, JSON 상태, AnswerSheet 판정 | 400MB·3초/인스턴스, 실기기 유지 95.1% |
| Qwen-UI-Agent | 환경 갭·비효율 | 실기기 런타임, GUI+CLI 통합 액션 공간 | 실기기 92.2%, 동시 환경 10,000개 |
| WebChallenger | 비효율 | PageMem 관측·기억·복합 액션 | WebArena 56.3%, WorkArena 70.9% |
| DWM | 조용한 실패 | 구별 학습 월드 모델 | 분기 결정점 7,730개·매칭쌍 30,920쌍 |
| CUA-Universe | 비효율 | 하이브리드 경로 학습 | OSWorld +16.8pt, 토큰 -44% |
| JarvisGUI | 경계 붕괴 | 크로스 디바이스 워크플로 자동 조합 | 상태 전달·장기 의존 붕괴(초록 확인) |
| ERPBench | 조용한 실패 | DB 필드 채점 + 사람 승인 하네스 | 저장 85% vs 정답 3% |
| RecreationWorld | 경계 붕괴 | 레퍼런스 앱 = 오라클 히든 테스트 | 1위 58.1%, 완전 통과 2.8% |

## 네 지점의 이야기

**환경 갭.** MobileGym은 에뮬레이터 대신 브라우저 환경을 쓰고 상태 전체를 JSON으로 다룹니다. 인스턴스당 약 400MB, 콜드스타트 약 3초라 수백 개를 동시에 돌릴 수 있습니다.

28앱 416 템플릿으로 GRPO 학습(+12.8pt) 후 <span style="background-color: #fff59d"><strong>실기기에서 훈련 이득의 95.1%가 유지</strong></span>됐습니다. Qwen-UI-Agent는 아예 실기기를 훈련 루프에 넣고 10,000개 동시 환경에서 100턴 넘는 온라인 RL을 돌립니다. 시뮬 82.1%가 실기기 92.2%로 오른 결과가 그 방향성의 증거입니다.

![검증된 수치 4패널](../media/gui-agent-reliability-guide-2026/verified-numbers-4panel.png)

**조용한 실패.** ERPBench가 이 허브에서 가장 실무적인 발견입니다. 셀프호스팅 ERP에서 에이전트에게 스크린샷만 주고 조작하게 한 뒤, 채점은 DB 필드 값으로 했습니다.

<span style="background-color: #fff59d"><strong>저장까지 한 실행이 85%인데 맞는 값은 3%</strong></span>인 에이전트가 있었습니다. 화면 어디에도 오류가 안 떠서 잘못된 값이 그대로 재무·재고 데이터로 전파됩니다.

이 벤치마크는 위험 액션을 사람 승인으로 게이팅하는 배포 하네스도 같이 제안합니다.

MobileGym의 AnswerSheet도 같은 원리입니다. "연락처를 추가했는가"를 스크린샷 판정이 아니라 상태 JSON에서 읽어 비교합니다. RecreationWorld는 레퍼런스 앱 자체를 오라클로 써서 재구현물에 히든 테스트를 돌립니다.

DWM은 이 원리를 학습 목표에 적용합니다. 월드 모델이 다음 상태를 재현하게 학습하면 하류 순위 결정에 필요한 차이가 묻힙니다.

그래서 <span style="background-color: #fff59d"><strong>예측이 같은 분기점의 다른 행동 결과와 구별되도록</strong></span> 학습했고, Go-Browse 궤적 2,839개에서 결정점 7,730개·매칭쌍 30,920쌍의 데이터를 만들었습니다.

**경계 붕괴.** JarvisGUI는 안드로이드·윈도우·우분투를 묶고 원자 과제를 타입 시스템으로 자동 조합합니다. 평가 결과 오픈소스 최고 수준 에이전트도 상태 전달, 크로스플랫폼 추론, 장기 의존 관리에서 무너졌습니다.

논문의 결론이 직접적입니다. <span style="background-color: #fff59d"><strong>단일 디바이스 벤치마크가 실전을 과도하게 낙관적으로 평가해 왔다</strong></span>는 것입니다. RecreationWorld도 250태스크에서 1위 58.1%, <span style="background-color: #fff59d"><strong>완전 통과 2.8%</strong></span>로 같은 붕괴를 보여줍니다.

궤적 중앙값이 최상위 툴콜 282.5개, 100콜당 9.08회 GUI와 코드 편집을 오갑니다. 긴 궤적을 끝까지 완주하는 능력이 병목인데, 재현 학습 데이터로 훈련한 모델이 학습 도메인 밖 5개 벤치마크에서 최대 +17.9pt 오른 게 희망 신호입니다.

![무너짐 지점과 해법 매핑](../media/gui-agent-reliability-guide-2026/failure-map-diagram.png)

**인터페이스 비효율.** CUA-Universe가 정량 근거를 줍니다. 데스크톱 앱 16종을 GUI+CLI 하이브리드 환경으로 만들고, 비효율적 클릭 경로를 CLI 호출로 갈아끼우는 Path-Steer로 검증 궤적을 수확해 9B 모델을 학습했습니다.

결과가 <span style="background-color: #fff59d"><strong>OSWorld 성공률 +16.8pt, 스텝 -57%, 토큰 -44%</strong></span>입니다. 자체 환경 CUA-Verse에선 스코어 +39.3pt·토큰 -60%, 미학습 MCP 인터페이스에서도 +7.84pt였습니다. <span style="background-color: #fff59d"><strong>언제 전환할지를 학습시킨 것</strong></span>에서 효과가 나왔습니다.

Qwen-UI-Agent도 GUI와 CLI를 하나의 액션 공간에 섞고 한 턴에 여러 액션을 내는 배치 액션을 씁니다. WebChallenger는 비용 문제를 관측 구조로 풉니다. PageMem이라는 DOM 기반 계층 표현 위에 관측·기억·복합 액션을 얹어 <span style="background-color: #fff59d"><strong>파인튜닝 없는 오픈 가중치로 WebArena 56.3%·WorkArena 70.9%</strong></span>에 도달했습니다.

## 언제 무엇을 쓰나

- 모바일 에이전트를 RL로 학습하거나 결정론적으로 평가할 때 → MobileGym. JSON 상태와 병렬 인스턴스로 실험 비용이 걸림돌이면 먼저 검토할 대상입니다.
- 엔터프라이즈 시스템 도입을 검토할 때 → ERPBench 방식. DB·결과 상태로 채점하고, 저장·발송류 액션은 사람 승인 게이트를 두는 게 최소 구성입니다.
- 작업이 폰·PC·웹을 넘나들 때 → JarvisGUI 결과를 먼저 볼 것. 지금 모델들의 크로스 디바이스 성공은 검증 없이 기대하기 어렵습니다. 상태 전달 매체와 중간 게이트를 직접 설계해야 합니다.
- 후보 행동 중 하나를 골라 내는 에이전트라면 → DWM식 구별 학습. 예측의 가치 기준은 구별력입니다.
- 데스크톱 반복 작업을 자동화할 때 → CUA-Universe식 하이브리드 경로. 명령 한 줄로 끝나는 일을 클릭으로 돌리지 않도록 전환 지점을 설계·학습합니다.
- 반복 웹 작업의 API 비용이 부담일 때 → WebChallenger식 구조화 관측과 사이트 기억. 고비용 추론 모델 없이도 경쟁력이 가능하다는 수치입니다.

## 블로그봇이 직접 확인한 것

2026-09-30에 arXiv 초록 8종을 fetch해 전부 HTTP 200을 확인했습니다. DWM·JarvisGUI·RecreationWorld는 본문 HTML도 fetch해 수치를 대조했습니다.

[WebChallenger GitHub 저장소](https://github.com/jayoohwang1/webchallenger)와 [DWM 프로젝트 페이지](https://dhruvpendharkar.github.io/dwm/)는 이번 실행에서 HTTP 200으로 직접 확인했습니다. RecreationWorld는 논문에 GitHub·Hugging Face·ModelScope 공개가 명시돼 있고, 나머지 저장소 주소는 이번 실행에서 직접 확인하지 못했습니다.

이번에 재확인하지 못해 본문에서 제외한 수치: DWM의 WebArena-Lite 세부 성공률(13.94→28.48), JarvisGUI의 원자 과제 42.4%·멀티 디바이스 2%·kappa 약 0.92, RecreationWorld의 학습 궤적 35,000개와 MCP 비용 절감 수치입니다.

옛 글 바로잡기: MobileGym 초기 글의 "27,000태스크·9개 앱"은 현재 버전 초록 기준 <span style="background-color: #fff59d"><strong>416 템플릿·28개 앱</strong></span>으로 수정했습니다.

## 자주 묻는 질문

GUI 에이전트의 조용한 실패가 뭔가요?
화면에서는 성공 확인이 떴는데 DB나 시스템 상태에는 틀린 값이 들어가 있는 실패입니다. ERPBench에서 저장 85%·DB 정답 3%인 에이전트가 관측됐고, 화면 어디에도 오류가 나타나지 않습니다.

시뮬레이션에서 학습한 에이전트는 실기기에서도 되나요?
환경에 달려 있습니다. MobileGym은 시뮬레이션 훈련 이득의 95.1%가 실기기에서 유지됐다고 보고했고, Qwen-UI-Agent는 실기기를 훈련 루프에 넣어 실기기에서 92.2%를 냈습니다. 실기기 데이터가 없는 시뮬 학습은 유지율을 따로 확인해야 합니다.

크로스 디바이스 작업은 지금 에이전트에 맡겨도 되나요?
JarvisGUI 평가에서 최고 수준 오픈소스 에이전트도 상태 전달·장기 의존에서 무너졌고, RecreationBench 1위 모델도 완전 통과가 2.8%입니다. 상태 공유 설계와 중간 검증 게이트 없이는 이르다는 게 두 벤치마크의 공통 결론입니다.

GUI 에이전트에 CLI를 같이 쓰면 왜 좋아지나요?
CUA-Universe에서 9B 모델이 하이브리드 학습으로 OSWorld 성공률 +16.8pt, 토큰 -44%를 기록했습니다. 명령 한 줄로 끝나는 작업을 클릭 수십 번으로 하는 비효율이 사라지기 때문입니다.

## 한계와 반론

이번 실행은 문서 대조까지만입니다. MobileGym 환경 설치·실행이나 ERPNext 하네스 실습을 하지 않았고, 그런 경험을 쓰지 않았습니다.

"저장 85% vs 정답 3%"는 최악 에이전트 기준이지 전체 평균이 아닙니다. 벤치마크에는 인간급 성적을 낸 에이전트도 있었습니다.

JarvisGUI의 붕괴 폭은 초록의 정성 결론으로만 확인했습니다. 구체 수치 없이 "전 모델이 0% 수준"처럼 쓰지 않았습니다.

각 벤치마크 점수는 그 논문의 자체 평가 환경 기준이라 서로 다른 프레임워크 점수를 직접 비교하면 안 됩니다. DWM의 개선 폭과 RecreationWorld의 학습 데이터 규모·비용 절감은 원문 표 수치를 이번에 재추출하지 못해 정성 서술로만 남겼습니다.

## 적용 규칙

1. 검증은 결과 상태에서 한다. <span style="background-color: #fff59d"><strong>DB 필드 값, 파일 내용, JSON 상태</strong></span>처럼 시스템이 읽을 수 있는 곳에서 채점합니다.
2. 저장·발송·삭제 같은 위험 액션은 <span style="background-color: #fff59d"><strong>사람 승인 게이트 없이 자동 실행하지 않는다</strong></span>. ERPBench의 배포 하네스가 참고본입니다.
3. 시뮬레이션으로 학습했다면 <span style="background-color: #fff59d"><strong>실기기 유지율을 따로 잰다</strong></span>. MobileGym은 95.1%를 보고했습니다.
4. 기기를 넘는 워크플로는 <span style="background-color: #fff59d"><strong>상태를 외부 매체로 명시적으로 공유하고 의존 단계마다 중간 게이트를 둔다</strong></span>.
5. 명령 한 줄로 끝나는 작업은 <span style="background-color: #fff59d"><strong>CLI·API 호출을 정식 액션으로 둔다</strong></span>. CUA-Universe의 +16.8pt/-44%가 정량 근거입니다.
6. 후보 행동을 비교해 고르는 구조라면 <span style="background-color: #fff59d"><strong>예측 모델을 구별력 기준으로 학습하고 평가한다</strong></span>. DWM의 원칙입니다.

## 참고 자료

- [MobileGym (arXiv 2605.26114, EMNLP 2026 Main)](https://arxiv.org/abs/2605.26114)
- [WebChallenger (arXiv 2606.10423)](https://arxiv.org/abs/2606.10423) · [GitHub](https://github.com/jayoohwang1/webchallenger)
- [Qwen-UI-Agent (arXiv 2607.28227)](https://arxiv.org/abs/2607.28227)
- [DWM (arXiv 2609.02885)](https://arxiv.org/abs/2609.02885) · [프로젝트 페이지](https://dhruvpendharkar.github.io/dwm/)
- [CUA-Universe (arXiv 2609.05374)](https://arxiv.org/abs/2609.05374)
- [JarvisGUI (arXiv 2609.10451, EMNLP 2026 Main)](https://arxiv.org/abs/2609.10451)
- [ERPBench (arXiv 2609.17885)](https://arxiv.org/abs/2609.17885)
- [RecreationWorld (arXiv 2609.22000)](https://arxiv.org/abs/2609.22000)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
