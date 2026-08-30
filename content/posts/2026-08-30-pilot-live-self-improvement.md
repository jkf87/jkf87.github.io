---
title: "PILOT — 자기개선은 실행이 끝난 뒤가 아니라 실행 중에 일어나야 한다"
date: 2026-08-30
tags: [agent, harness, self-improvement, llm, arxiv]
draft: false
description: "홍콩이공대 PILOT(arXiv 2608.26530)은 슈퍼바이저-워커 하네스로 자기개선을 라이브로 만든다. 실행 중 감독자가 워커를 리다이렉트하고, 실행 중 배운 절차를 스킬·메모리로 증류해 Terminal-Bench 2.0 최대 +9.8%p, 출력 토큰은 40% 이상 감소."
---

## 결론 먼저

롱호라이즌 에이전트의 자기개선은 대부분 실행이 끝난 뒤에 경험을 처리합니다. 실행 중인 런을 되돌리지도 못하고, 배운 걸 바로 검증하지도 못하죠. 홍콩이공대(PolyU) 팀이 내놓은 PILOT(arXiv 2608.26530, 2026-08-27)은 이걸 "라이브"로 바꿉니다. <span style="background-color: #fff59d"><strong>실행 중에 감독자가 일꾼을 돌리고, 실행 중에 배운 걸 스킬과 메모리로 증류</strong></span>합니다.

핵심 숫자:

| 항목 | 결과 |
| --- | --- |
| Terminal-Bench 2.0 | 대응 하네스 대비 최대 +9.8%p |
| 자기개선 설정 | GLM-5.1 +14.6점, Kimi-K2.6 +12.4점 |
| 평균 출력 토큰 | 42.9% / 47.4% 감소 |
| 백만 토큰당 성공 평가 | +110.3% / +134.0% |

## 기존 구조가 못 하는 것

단일 에이전트 자기수정은 태스크 실행과 트랙토리 평가를 한 컨텍스트에서 같이 합니다. 평가가 실행을 침범하죠. 서브에이전트 위임은 실행을 분리하긴 하는데, 이미 돌고 있는 서브에이전트를 중간에 돌릴 수 없습니다.

PILOT의 진단은 이 두 구조 모두 <span style="background-color: #fff59d"><strong>"지금 이 런"을 개선하지 못한다</strong></span>는 겁니다.

## 구조: 두 개의 라이브 메커니즘

PILOT은 슈퍼바이저-워커 하네스입니다. <span style="background-color: #fff59d"><strong>Pi 코딩 에이전트 런타임 위에 확장</strong></span>으로 구현됐고, 감독자와 일꾼이 각각 별도 세션으로 뜹니다.

![PILOT 구조](/images/2026-08-30-pilot-live-self-improvement/fig-2-p3.png)

- 라이브 스티어링: <span style="background-color: #fff59d"><strong>감독자가 실행 중인 워커를 리다이렉트하거나 중단</strong></span>
- 라이브 자기진화: 실행 중 드러난 절차와 실패 양상을 재사용 가능한 스킬과 메모리로 증류

이 둘이 묶여서 자기개선 루프가 닫힙니다. <span style="background-color: #fff59d"><strong>모델은 동결(frozen) 상태 그대로</strong></span>구요. 하네스만 살아 움직입니다.

## 성능

동결 백본 2종(GLM-5.1, Kimi-K2.6), 벤치마크 3종에서 <span style="background-color: #fff59d"><strong>6개 구성 중 5개에서 1위</strong></span>였습니다.

![주요 결과](/images/2026-08-30-pilot-live-self-improvement/fig-1-p1.png)

Terminal-Bench 2.0에서는 같은 백본을 쓰는 Pi, OpenCode, Terminus-2 등 단일 에이전트 하네스들을 최대 9.8%p 차로 앞섰습니다.

자기개선 설정(20회 반복)에서는 GLM-5.1이 +14.6점, Kimi-K2.6이 +12.4점을 얻었습니다. 반복이 쌓일수록 스킬과 메모리가 불어나는 구조라 후속 런이 이득을 봅니다.

![반복별 성능](/images/2026-08-30-pilot-live-self-improvement/fig-3-p7.png)

## 효율: 토큰이 적게 드는 자기개선

성능만 오른 게 아닙니다. <span style="background-color: #fff59d"><strong>평균 출력 토큰이 42.9%, 47.4% 각각 줄었고, 백만 출력 토큰당 성공 평가 수는 110.3%, 134.0% 늘었습니다</strong></span>. 감독자가 중간에 잘못된 경로를 끊어버리니 낭비 토큰이 사라지는 거구요.

![라이브 스티어링 분석](/images/2026-08-30-pilot-live-self-improvement/table-2-p7.png)

## 내 해석

기대 포인트는 <span style="background-color: #fff59d"><strong>자기개선의 타이밍을 "사후 배치"에서 "실시간 인라인"으로 옮겼다</strong></span>는 것입니다. 스킬·메모리 진화 연구는 이미 많은데, 실행 중 감독이 개입해 런 자체를 구조화하는 쪽은 이 논문이 훨씬 명확합니다. 토큰 효율 개선까지 같이 왔다는 점도 실무적으로 중요해요.

확인할 부분: <span style="background-color: #fff59d"><strong>감독자가 틀린 판단을 하면 실행 중단이 오히려 손해</strong></span>가 될 수 있습니다. 논문의 라이브 스티어링 분석(표 2)에서 이 오차율을 어느 정도 다루고는 있지만, 더 험한 환경에서의 거짓 양성 비용은 후속 검증이 필요해 보입니다.

기준일: <span style="background-color: #fff59d"><strong>2026-08-30, arXiv v1 기준</strong></span>.

원문: [PILOT in the Loop: Live Self-Improvement for Long-Horizon Agents (arXiv 2608.26530)](https://arxiv.org/abs/2608.26530) · 코드: [github.com/XiaoYang66/Pilot](https://github.com/XiaoYang66/Pilot)

## 자주 묻는 질문

**PILOT의 자기개선이 기존 방식과 다른 점은?**

기존 방식은 실행이 끝난 뒤 경험을 처리하지만, PILOT은 실행 중에 감독자가 워커를 리다이렉트/중단하는 라이브 스티어링과, 실행 중 배운 절차를 스킬·메모리로 증류하는 라이브 자기진화를 같이 돌립니다.

**모델 가중치를 바꾸나요?**

아니요. 백본은 GLM-5.1, Kimi-K2.6 모두 동결 상태이고, 개선은 하네스(감독자 구조, 스킬, 메모리) 계층에서만 일어납니다.

**성능 향상이 토큰을 더 써서 나온 건 아닌가?**

아닙니다. 평균 출력 토큰이 42.9%(GLM-5.1), 47.4%(Kimi-K2.6) 줄었고, 백만 출력 토큰당 성공 평가 수는 110.3%, 134.0% 늘었습니다.

**비교 대상 하네스는?**

같은 백본을 쓰는 Pi, OpenCode, Terminus-2 등 단일 에이전트 하네스이며, Terminal-Bench 2.0에서 최대 9.8%p 앞섰습니다. SWE-bench Pro 포함 3종 벤치마크 6개 구성 중 5개에서 1위였습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
