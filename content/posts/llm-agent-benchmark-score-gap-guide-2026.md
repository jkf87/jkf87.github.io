---
title: "터미널 벤치마크 82%가 실전 업무 1%로 무너지는 이유: LLM 에이전트 벤치마크 10종 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "LLM 에이전트 벤치마크 10종을 비교해 점수가 실전에서 무너지는 일곱 가지 스트레스를 정리했습니다. Terminal-Bench 82%가 ALE 1% 미만으로 떨어지는 구조와 평가 설계 규칙을 담았습니다."
tags:
  - LLM 에이전트
  - 벤치마크
  - 에이전트 평가
  - 실전 격차
refactor_hub_id: eval-benchmarks-01
aliases:
  - finmcp-bench-mcp-financial-agent-benchmark
  - pi-bench-proactive-assistant-agents-2026-05-24
  - terminalworld-benchmarking-terminal-agents-2026-05-24
  - 2026-06-03-spatialbench-spatial-foundation-model
  - k-browsecomp-korean-web-browsing-agent-benchmark-2026-06-03
  - kolongdoc-korean-long-document-vlm-benchmark-2026-06-05
  - 2026-06-16-agents-last-exam
  - posts/2026-07-10-agentgym2-real-world-agent-benchmark
  - posts/2026-07-23-relay-bench-multi-domain-reasoning
  - posts/2026-09-05-terminal-universe
draft: false
sources_read: "논문 8종(FinMCP-Bench·π-Bench·TerminalWorld·SpatialBench·ALE·AgentGym2·Relay-Bench·Terminal-Universe) 초록 페이지 fetch HTTP 200 + 본문 HTML 8종 수치 대조, K-BrowseComp·KOLongDoc는 공식 GitHub README fetch HTTP 200 후 수치 대조, 저자 코드 확인: EuniAI/TerminalWorld·prometheus-eval/K-BrowseComp·Marker-Inc-Korea/KOLongDoc HTTP 200, PI-BENCH 저장소는 main 브랜치 README 404로 코드 미확인으로 기록"
novelty_vs_paper: "각 벤치마크의 구성·수치는 전부 각 논문·공식 저장소의 것이며, 이 글이 새로 만든 것은 7가지 스트레스 축 분류, 10종 통합 대조 표, 스트레스 요인 매트릭스와 점수 분포 차트 2장, 초록·본문·README 수치 대조 로그, 평가 설계 적용 규칙 8개임"
---

## 한눈에 보는 결론

같은 에이전트 구성입니다. Codex+GPT-5.5는 <span style="background-color: #fff59d"><strong>Terminal-Bench에서 82%를 받습니다</strong></span>. 근데 전문가 실무 과제 벤치마크 ALE에서는 <span style="background-color: #fff59d"><strong>전체 통과율이 1% 미만입니다</strong></span>. 모델이 바뀐 게 없습니다. <span style="background-color: #fff59d"><strong>벤치마크가 잰 능력의 폭이 달랐던 겁니다</strong></span>.
2026년 3월부터 9월까지 이 블로그에 단발 소개로 쌓인 에이전트 벤치마크 10종을 하나의 비교 표로 합쳐 다시 정리했습니다. 10종 전부 같은 질문을 다룹니다. 벤치마크 점수가 실전 능력과 언제 어긋나는가. 핵심은 이겁니다. 점수를 떨어뜨리는 요인은 <span style="background-color: #fff59d"><strong>실사용 기록 기반 과제, 도구 직접 발견, 잡음·모호한 입력, 멀티턴 세션 의존, 도메인 혼합 연쇄, 언어·로컬 특수성, 전문가 소프트웨어와 장문 처리</strong></span>의 일곱 가지로 압축됩니다. 포화된 기존 벤치마크는 이 일곱 가지를 거의 안 넣었습니다. 10종은 각자 다른 조합으로 이걸 넣었고, 전부 큰 폭으로 점수가 깎였습니다.

![프론티어 모델의 스트레스 벤치마크 점수 분포](../media/llm-agent-benchmark-score-gap-guide-2026/chart-01-frontier-score-gap.png)

## 무엇을 비교했나

이 글은 2026-03-30 ~ 2026-09-05에 나눠 쓴 벤치마크 정리 10편을 합쳐 다시 쓴 허브입니다. 옛 글 URL은 이 글로 연결됩니다.

1. [FinMCP-Bench](https://arxiv.org/abs/2603.24943) — 금융 MCP 도구 호출. 실제 금융 앱 로그와 합성 데이터로 613 샘플, 65개 실제 MCP 도구.
2. [π-Bench](https://arxiv.org/abs/2605.14678) — 개인 비서의 선제성. 5개 직업 페르소나 × 20세션, 100개 멀티턴 과제.
3. [TerminalWorld](https://arxiv.org/abs/2605.22535) — 실제 개발자 터미널 녹화 80,870건에서 뽑은 1,530개 과제.
4. [SpatialBench](https://arxiv.org/abs/2605.27367) — 공간 기반 모델 41개를 5도메인×4입력밀도로 교차 평가.
5. [K-BrowseComp](https://github.com/prometheus-eval/K-BrowseComp) — 한국어 웹 탐색 400문제(인간 검수 300 + 합성 100).
6. [KOLongDoc](https://github.com/Marker-Inc-Korea/KOLongDoc) — 실제 한국 공공문서 장문 멀티홉 QA.
7. [Agents' Last Exam](https://arxiv.org/abs/2606.05405) — 250명 이상 전문가의 실무 프로젝트 1,490개 과제.
8. [AgentGym2](https://arxiv.org/abs/2607.05174) — 도구 발견·잡음·end-to-end를 넣은 비이상화 환경에서 15개 모델 평가.
9. [Relay-Bench](https://arxiv.org/abs/2607.18438) — 한 프롬프트에 2~13개 서브문제를 도메인 혼합 연쇄로 묶은 텍스트 벤치마크.
10. [Terminal-Universe](https://arxiv.org/abs/2609.04148) — 에이전트 트라젝토리를 37,273개 실행 환경으로 복원해 재활용.

## 방법 비교

기준일 2026-09-30, 블로그봇이 각 논문 초록·본문 HTML·공식 저장소 README에서 확인한 수치만 담았습니다.

| 벤치마크 | 문제 소스 | 가한 스트레스 | 채점 | 이번 실행에서 확인된 대표 결과 |
| --- | --- | --- | --- | --- |
| FinMCP-Bench | 금융 앱 실로그+합성 | 멀티턴 도구 연쇄 | 도구 호출 TR/TP/TF1/EMR | 613샘플(단일 145·멀티툴 249 평균 7.32회 호출·멀티턴 219 평균 5.95턴), 65개 실제 MCP |
| π-Bench | 페르소나 시나리오 | 숨은 의도, 세션 간 의존 | 선제성 completed/inferred, 완성도 루브릭 | GPT-5.4 선제성 67.0% 1위, Claude Opus 4.6 완성도 67.6% 1위, 세션 기록 제거 시 선제성 평균 -9.5pt |
| TerminalWorld | asciinema 실녹화 80,870건 | 실제 터미널 워크플로 | 3중 테스트 스위트 통과 | 최고 62.5%(Claude Opus 4.7+Terminus-2), 8모델 평균 54.8%, Terminal-Bench 2.0와 상관 r=0.20 |
| SpatialBench | 19개 공개 데이터셋 | 도메인 이동, 입력밀도 변화 | 재구성 메트릭 일괄 채점 | 41개 모델 중 만능(all-round) 모델 없음, DA-Next가 sparse 입력 AbsRel 0.095→0.050 |
| K-BrowseComp | 한국어 웹 탐색 문제 | 한국 로컬 탐색 특수성 | 정답 매칭 | 최고 모델도 Verified 50% 미만, 합성 분할 26% |
| KOLongDoc | 실제 공공문서 | 장문 멀티홉 | 키워드 포함 Hard/Soft | Gemini 3.5 Flash 이미지 입력 82.58, 텍스트 추출 68.52, 오픈소스 최고 Qwen3.6-27B 5.19 |
| ALE | 전문가 실무 프로젝트 | 전문가 소프트웨어, GUI+CLI 혼합, 장기 과제 | 결정론적 코드 채점 | Codex+GPT-5.5가 Terminal-Bench 82%인데 ALE 전체 통과율 1% 미만 |
| AgentGym2 | 실무형 end-to-end 요청 27+ 도메인 | 도구 발견, 잡음 주입 | 과제별 검증 | GPT-5 약 44%, Claude Sonnet 4.5 약 37%, 잡음 주입 시 GPT-5 -7.4%·Claude -6.4% |
| Relay-Bench | 합성 복합 문제 31개(30 비공개) | 도메인 혼합 연쇄, 7,813자 컨텍스트 부풀림 | 서브문제 연쇄 정답 | GPT-5.5(xHigh) 43.3%가 최고, 3모델 평균 33.3%, 개발·실행 총비용 $163.29 |
| Terminal-Universe | 실제 에이전트 트라젝토리 | 환경 복원(재생 40.2%→완성 93.5%) | 재쿼리 가능 환경 | 재구성 환경 재풀이 SFT 52.1 vs 트라젝토리 모방 SFT 36.7 |

표 읽는 요령. 각 행의 숫자는 모델 구성·버전·채점 기준이 제각각입니다. 벤치마크 간 직접 우열 매기기에는 못 씁니다. 각 행은 그 벤치마크가 자기 스트레스를 넣었을 때 점수가 어떻게 되는가를 보여줍니다.

![10종 벤치마크 스트레스 요인 매트릭스](../media/llm-agent-benchmark-score-gap-guide-2026/chart-02-stress-matrix.png)

## 점수 격차를 만드는 7가지 스트레스

실사용 기록에서 과제를 만들면 점수가 내려갑니다. TerminalWorld에서 8개 프론티어 모델의 평균 통과율은 54.8%이고 최고(Claude Opus 4.7+Terminus-2)도 62.5%입니다. <span style="background-color: #fff59d"><strong>전문가 제작 Terminal-Bench 2.0 점수와의 상관은 r=0.20입니다</strong></span>. 오픈웨이트 Kimi K2.6(57.5%)·GLM 5.1(57.0%)이 GPT-5.5(53.5%)보다 앞섰습니다. 에이전트가 인간 실무자와 쓴 명령어 집합의 중복도 중앙값은 21.4%였습니다. 푼 방법 자체가 다릅니다. <span style="background-color: #fff59d"><strong>실패한 시도는 성공보다 토큰을 3.3배 쓰면서 전체 평가 비용의 63%를 차지했습니다</strong></span>.

도구를 직접 찾게 하면 무너집니다. AgentGym2는 도구를 미리 골라주지 않습니다. 15개 모델에서 <span style="background-color: #fff59d"><strong>GPT-5가 약 44%로 최고입니다</strong></span>. 도구가 미리 정의된 벤치마크의 점수 체계와는 다른 세계입니다.

입력에 잡음만 섞어도 떨어집니다. AgentGym2에서 검색 쿼리에 잡음을 주입하자 <span style="background-color: #fff59d"><strong>GPT-5가 7.4%, Claude-4.5-Sonnet가 6.4% 떨어졌습니다</strong></span>. 실사용 질의는 오타와 모호한 표현이 기본값입니다. 클린 쿼리로 만든 점수는 이 폭만큼 보정해서 읽어야 합니다.

세션이 이어지면 다른 능력이 측정됩니다. π-Bench에서 선제성 1위 모델도 67.0%입니다. 이전 세션 기록을 없애자 <span style="background-color: #fff59d"><strong>선제성이 평균 9.5pt 떨어졌고 완성도는 2.5pt만 떨어졌습니다</strong></span>. 선제성은 기록에 의존하는 별도 능력입니다.

도메인이 섞이는 순간 단일 점수로 예측이 안 됩니다. Relay-Bench는 도구 사용을 전부 허용했는데도 <span style="background-color: #fff59d"><strong>최고 모델(GPT-5.5 xHigh)이 43.3%, 3모델 평균 33.3%입니다</strong></span>. 90개 응답 중 파싱 가능한 최종 답은 50개였습니다.

언어와 로컬 컨텍스트가 바뀌면 절반 이하로 떨어집니다. <span style="background-color: #fff59d"><strong>K-BrowseComp에서 최고 모델도 한국어 웹 탐색 검수 분할(300문제)에서 50%를 못 넘습니다</strong></span>. 합성 난이자 분할에서는 26%입니다. KOLongDoc에서는 <span style="background-color: #fff59d"><strong>장문 공공문서 이미지 입력 기준 최고 82.58%, 오픈소스 최고는 5.19%입니다</strong></span>. 기존 벤치마크가 영어·짧은 문서 기준일 때는 이 격차가 아예 안 보입니다.

전문가 도구와 장기 과제가 만나면 바닥을 칩니다. ALE의 1,490개 과제는 13개 산업 55개 하위분야의 실무 워크플로입니다. <span style="background-color: #fff59d"><strong>기존 16개 주요 벤치마크를 합쳐도 55개 중 13개 하위분야는 커버하지 못했습니다</strong></span>. 그 빈 자리에서 최강 구성의 통과율이 1% 미만입니다.

## 언제 무엇을 쓰나

CLI 에이전트를 뽑는다면 Terminal-Bench 점수만으로 결정하지 마세요. 실녹화 기반 TerminalWorld 점수를 두 번째 기준으로 놓습니다. 두 점수의 상관이 r=0.20이라 하나로 예측이 안 됩니다.

도구를 붙여 쓰는 업무 에이전트라면 AgentGym2 계열(도구 발견+잡음+end-to-end) 점수를 우선 봅니다. 도구가 미리 제공된 벤치마크 점수를 상한선으로 읽으면 안 됩니다.

비서형·대화형 제품이라면 π-Bench의 선제성/완성도 분리 구조를 벤치마킹합니다. 두 지표가 다른 방향으로 움직인 측정(Kimi K2.5, 선제성 43.1 vs 완성도 61.6)이 이미 있습니다.

한국어 업무를 다룬다면 영어 벤치마크 점수로 외삽하지 않습니다. K-BrowseComp·KOLongDoc을 통과 기준으로 직접 돌립니다. 둘 다 공개 저장소라 바로 실행 가능합니다.

도메인이 섞이는 실무(보고서 검증→크롤링→정제→작성)라면 Relay-Bench식 연쇄 문제를 내 워크플로에서 30개 뽑아 측정합니다. 총비용 $163.29라 예산 부담이 작습니다. 문항을 직접 만들 때는 라벨 누수를 먼저 점검하세요. 문항 문구에 정답 단서가 박히면 점수가 부풀어 올라갑니다.

멀티모달 장문 문서(공공문서·계약서) 파이프라인이라면 KOLongDoc 구성(실문서+멀티홉+키워드 채점)을 참고합니다. 텍스트 추출보다 이미지 직접 입력이 14pt 높았습니다.

에이전트 도입 검토 단계라면 ALE의 실패 구조를 읽고 기대치를 조정합니다. 포화 벤치마크 점수와 실무 통과율의 격차가 어디서 오는지 13개 산업 데이터로 정리되어 있습니다.

## 블로그봇이 직접 확인한 것

arXiv 초록 페이지 8종(FinMCP-Bench, π-Bench, TerminalWorld, SpatialBench, ALE, AgentGym2, Relay-Bench, Terminal-Universe)을 전부 fetch해 HTTP 200과 제목 일치를 확인했습니다(기준일 2026-09-30).

8종 전부 본문 HTML(arxiv.org/html)을 내려받아 표와 본문의 수치를 문자열로 대조했습니다. 이 글의 숫자는 이 대조를 통과한 값입니다.

K-BrowseComp·KOLongDoc은 논문 대신 공식 GitHub README를 fetch해 수치를 대조했습니다(둘 다 HTTP 200). KOLongDoc의 모델별 표(82.35/82.81/82.58/68.52/5.19)와 K-BrowseComp의 구성(300+100)·합성 분할 26%를 확인했습니다.

저자 코드 저장소는 EuniAI/TerminalWorld, prometheus-eval/K-BrowseComp, Marker-Inc-Korea/KOLongDoc 세 곳 HTTP 200. PI-BENCH 저장소는 main 브랜치 README가 404라 이번 실행에서 코드를 확인하지 못했습니다.

<span style="background-color: #fff59d"><strong>이번 실행에서 확인되지 않아 제외한 수치</strong></span>: K-BrowseComp 모델별 정확 점수(45.67% 등), TerminalWorld와 Terminal-Bench의 9% 명령어 중복, Relay-Bench 환각률 세부 수치, AgentGym2의 학회 게재 연도 표기입니다.

차트 2장은 블로그봇이 10종의 구성·수치를 재분류해 직접 그렸습니다.

## 한계와 반론

수치 대조는 문자열 검색으로 본문·README에 그 숫자가 있는지를 확인한 겁니다. 표 셀의 맥락까지 사람이 읽은 것은 아닙니다.

10종은 모델 구성·에이전트 하네스·벤치마크 버전이 제각각입니다. 벤치마크 간 직접 우열 비교 용도로는 못 쓰고, 스트레스 종류별 붕괴 패턴 비교로 읽어야 합니다.

벤치마크 제작자는 자기 벤치마크가 기존과 다르고 어렵다는 걸 보여야 합니다. 그 유인이 결과 서술에 영향을 줬을 수 있습니다.

K-BrowseComp·KOLongDoc은 논문 본문 대조가 안 된 저장소 README 기준입니다. 수치가 README 개정과 함께 바뀔 수 있습니다.

ALE의 과제는 150개 공개·1,017개 비공개·323개 QC 대기입니다. 외부 재현은 공개 150개로 제한됩니다.

## 적용 규칙

모델·에이전트 선정과 사내 평가 설계에 바로 쓰이는 규칙만 남깁니다. 각 규칙은 이번에 확인한 수치에서 나왔습니다.

1. <span style="background-color: #fff59d"><strong>벤치마크 점수는 스크리닝으로만 쓰세요</strong></span>. 최종 판단은 도구 발견+잡음+end-to-end가 들어간 평가로 하세요. 도구 미리 제공형 점수의 최고치가 AgentGym2에서는 약 44%였습니다.
2. <span style="background-color: #fff59d"><strong>CLI 에이전트 후보는 최소 두 벤치마크를 겹쳐 보세요</strong></span>. 전문가 제작형과 실녹화형의 상관이 r=0.20이라 하나로 예측이 안 됩니다.
3. 내 평가 세트에 잡음을 일부러 섞으세요. 잡음 주입 시 6~8pt 떨어지는 게 측정된 상태입니다. 클린 세트 점수만 보고 도입하면 현장에서 이 폭이 청구됩니다.
4. 멀티턴 제품은 세션 기록 유무 두 조건으로 나눠 측정하세요. 선제성은 기록 제거 시 평균 9.5pt가 무너지는 기록 의존 능력입니다.
5. 도메인이 바뀌는 지점에서 평가를 나누세요. 연쇄·혼합 문제에서는 최고 모델도 43.3%입니다. 단일 도메인 점수를 실무 예측에 쓰지 않습니다.
6. <span style="background-color: #fff59d"><strong>한국어 업무는 한국어 평가로만 판정하세요</strong></span>. 최고 모델도 한국어 웹 탐색 50% 미만, 장문 문서 오픈소스 5.19%라는 측정이 있습니다.
7. 평가 예산이 작아도 시작하세요. 문제 31개짜리 벤치마크가 총비용 $163.29로 유효한 신호를 냈습니다. 규모보다 스트레스 종류가 먼저입니다.
8. <span style="background-color: #fff59d"><strong>에이전트 실행 로그를 버리지 마세요</strong></span>. 트라젝토리를 환경으로 복원해 다시 풀게 하는 쪽이 모방 학습보다 52.1 대 36.7으로 컸습니다. 로그는 재평가 자원입니다.

## 자주 묻는 질문

**벤치마크 점수를 아예 믿지 말라는 건가요?**

아니요. 스크리닝 용도로는 씁니다. 최종 판단은 도구 발견·잡음·end-to-end 조건이 들어간 평가로 내리면 됩니다. 도구 미리 제공형 벤치마크의 최고점이 AgentGym2에서는 약 44%였다는 측정이 그 근거입니다.

**CLI 코딩 에이전트를 고를 때 뭘 먼저 보면 되나요?**

Terminal-Bench 점수와 실녹화 기반 TerminalWorld 점수를 함께 보세요. 둘의 상관이 r=0.20이라 한쪽 점수로 다른 쪽을 예측할 수 없습니다. 같은 모델이라도 순위가 바뀐 측정(Kimi K2.6 57.5% vs GPT-5.5 53.5%)이 있습니다.

**한국어 업무용 모델은 어떻게 고르나요?**

영어 벤치마크 점수로 판단하지 마시고 K-BrowseComp·KOLongDoc을 직접 돌려보세요. 둘 다 공개 저장소입니다. 최고 모델도 한국어 웹 탐색 50% 미만, 장문 문서 오픈소스 5.19%라는 측정이 있습니다.

**평가 문항을 직접 만들 때 제일 조심할 점은?**

라벨 누수입니다. 문항 문구에 정답 단서가 박히면 점수가 부풉니다. 문항을 만든 뒤 정답 힌트를 가리고 다시 풀어보는 점검을 먼저 돌리세요. 예산이 작아도 문제 31개·$163.29 구성으로 시작할 수 있습니다.

## 참고 자료

- [FinMCP-Bench (arXiv:2603.24943)](https://arxiv.org/abs/2603.24943)
- [π-Bench (arXiv:2605.14678)](https://arxiv.org/abs/2605.14678) · [프로젝트 페이지](https://github.com/strive-ssr/PI-BENCH)
- [TerminalWorld (arXiv:2605.22535)](https://arxiv.org/abs/2605.22535) · [코드](https://github.com/EuniAI/TerminalWorld)
- [SpatialBench (arXiv:2605.27367)](https://arxiv.org/abs/2605.27367)
- [K-BrowseComp (GitHub)](https://github.com/prometheus-eval/K-BrowseComp)
- [KOLongDoc (GitHub)](https://github.com/Marker-Inc-Korea/KOLongDoc) · [데이터셋](https://huggingface.co/datasets/Markr-AI/KOLongDoc)
- [Agents' Last Exam (arXiv:2606.05405)](https://arxiv.org/abs/2606.05405) · [프로젝트 페이지](https://agents-last-exam.org/)
- [AgentGym2 (arXiv:2607.05174)](https://arxiv.org/abs/2607.05174)
- [Relay-Bench (arXiv:2607.18438)](https://arxiv.org/abs/2607.18438)
- [Terminal-Universe (arXiv:2609.04148)](https://arxiv.org/abs/2609.04148)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
