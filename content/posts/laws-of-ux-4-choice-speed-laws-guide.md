---
title: "Laws of UX 선택·속도 법칙 4개 한줄 정리: 메뉴 개수·버튼 크기·반응 시간의 원전 기준"
date: 2026-09-30
author: 한준구(코난쌤)
description: "선택 과부하, 힉의 법칙, 핏츠의 법칙, 도허티 임계값 4개를 원전 논문 숫자로 다시 검증해 메뉴 개수, 버튼 크기, 반응 시간 기준을 정리했습니다. 재현이 엇갈린 선택 과부하는 조건부 효과로 구분했습니다."
tags: [UX, UX심리학, "Laws of UX", UI설계, 반응속도]
refactor_hub_id: ux-laws-02
aliases: [laws-of-ux/02-choice-overload, laws-of-ux/06-doherty-threshold, laws-of-ux/07-fitts-law, laws-of-ux/10-hicks-law, laws-of-ux/index]
draft: false
sources_read: "Iyengar & Lepper 2000, Doherty & Thadani 1982(IBM Systems Journal 공개 PDF 18쪽), Fitts 1954(재인쇄본) 세 편의 본문 PDF를 받아 읽고 잼 실험 카운트(242/145/4, 260/104/31), 400ms 인용 문장, 핏츠 처리속도(약 9.5~11.5비트/초)를 확인했습니다. 힉 1952·하이만 1953은 서지와 2018년 리뷰(Proctor & Schneider)로 대조했고 메타분석 2편(Scheibehenne 2010, Chernev 2015)은 원문 서두·초록을 읽었습니다. 이 고전 실험들에는 공개된 저자 코드·원시데이터가 없습니다"
novelty_vs_paper: "힉 기울기(0.10~0.20초/비트)와 핏츠 처리속도(10비트/초)로 실제 UI 치수의 소요 시간을 재계산한 차트 2장, 옛 글에서 삭제한 출처 불명 주장 4건 목록, 메타분석 2편의 조건 대비 정리는 이 블로그의 작업입니다. 잼 실험 3%/30%, 도허티 400ms, 로그 법칙 공식, 44pt/48dp 권장값은 각 원전과 플랫폼 공식 문서가 제시한 값입니다"
---

## 한눈에 보는 결론

옛 Laws of UX 시리즈 중 선택과 속도에 관한 글 5편(선택 과부하, 도허티 임계값, 핏츠의 법칙, 힉의 법칙, 30선 인덱스)을 이 페이지 하나로 합쳤습니다. 메뉴 개수, 버튼 크기, 반응 시간의 기준을 원전 숫자로 다시 확인해서 정리했습니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>선택지 수가 늘면 결정 시간이 로그적으로 늘어나고(힉), 조건이 나쁘면 아예 선택을 건너뛰기도 합니다(선택 과부하)</strong></span>.

이어서 두 가지가 더 있습니다. <span style="background-color: #fff59d"><strong>목표는 크고 가까울수록 빨리 누를 수 있고(핏츠), 클릭 뒤 시스템 응답이 400ms를 넘지 않으면 기다림 없이 작업이 이어집니다(도허티)</strong></span>.

| 법칙 | 한줄 요약 | 원전 근거 | 화면·자료에 적용하면 |
|---|---|---|---|
| 선택 과부하 | 조건이 나쁘면 선택을 건너뛴다 | 잼 실험 3% 대 30% | 기본 옵션 3~6개, 나머지는 필터로 |
| 힉의 법칙 | 선택지 수가 늘면 결정이 로그적으로 느려진다 | Hick 1952, Hyman 1953 | 최상위 메뉴 4~8개, 단계로 분해 |
| 핏츠의 법칙 | 목표는 크고 가까울수록 빨리 누른다 | Fitts 1954 탭핑 실험 | 자주 쓰는 버튼 44pt/48dp 이상 |
| 도허티 임계값 | 시스템 응답 기준은 400ms | Doherty & Thadani 1982(IBM) | 즉각 피드백, 길면 진행 표시 |

근데 법칙마다 근거의 강도가 다릅니다. <span style="background-color: #fff59d"><strong>원전을 다시 읽어 보니 힉·핏츠·도허티는 견고한데, 선택 과부하는 재현 결과가 갈립니다</strong></span>. 2010년 메타분석 63개 조건의 평균 효과는 사실상 0이었고, 2015년 메타분석은 효과가 존재하되 조건이 붙는다고 정리했습니다. 그래서 이 글은 선택 과부하를 조건이 맞을 때 나타나는 효과로 다룹니다.

옛 글에서 출처를 못 찾은 주장은 삭제했습니다. "1초→0.5초 생산성 50% 향상", "1991년 의식적 지각 연구 300~400ms", "결제 3단계화로 완료율 12% 향상", "전전두피질은 4~7개만 처리" 네 가지입니다. 원문에 없거나, 해당 연구를 찾을 수 없었습니다. <span style="background-color: #fff59d"><strong>출처를 못 찾은 통계는 각주로 남기지 않고 통째로 걷었습니다</strong></span>.

## 무엇을 비교했나

이 허브로 합쳐진 옛 글은 5편입니다. 선택 과부하, 도허티 임계값, 핏츠의 법칙, 힉의 법칙, 그리고 30선 총인덱스입니다. 옛 URL은 이 페이지로 넘어옵니다.

법칙 이름은 [Laws of UX](https://lawsofux.com/)를 따랐구요, 숫자와 결론은 아래 원전을 직접 받아 읽은 값입니다(기준일 2026-09-30).

1. [Laws of UX — Choice Overload](https://lawsofux.com/choice-overload/)
2. [Laws of UX — Doherty Threshold](https://lawsofux.com/doherty-threshold/)
3. [Laws of UX — Fitts's Law](https://lawsofux.com/fittss-law/)
4. [Laws of UX — Hick's Law](https://lawsofux.com/hicks-law/)
5. Iyengar & Lepper 2000, When Choice is Demotivating, JPSP 79(6) — [원문 PDF](https://faculty.washington.edu/jdb/345/345%20Articles/Iyengar%20%26%20Lepper%20(2000).pdf)
6. Scheibehenne, Greifeneder & Todd 2010, JCR 37(3) — [원문 PDF](https://scheibehenne.com/ScheibehenneGreifenederTodd2010.pdf)
7. Chernev, Böckenholt & Goodman 2015, JCP 25(2) 333-358
8. Doherty & Thadani 1982, The Economic Value of Rapid Response Time, IBM Systems Journal — [IBM 공개 PDF](https://www.ibm.com/support/pages/sites/default/files/inline-files/EconomicValueofResponseTime.pdf)
9. Brutlag 2009, Speed Matters for Google Web Search — [Google Research 블로그](https://research.google/blog/speed-matters/)
10. Fitts 1954, JEP 47(6) 381-391 — [재인쇄 PDF](https://www.lri.fr/~mbl/ENS/FONDIHM/2013/papers/Fitts-JEP54.pdf)
11. MacKenzie 1992, Fitts' law as a research and design tool in HCI, HCI 7(1) 91-139
12. Hick 1952, QJEP 4(1) 11-26 / Hyman 1953, JEP 45(3) 188-196
13. Proctor & Schneider 2018, Hick's law for choice reaction time: A review, QJEP 71(6)
14. [Apple HIG — Accessibility(기본 컨트롤 44×44pt)](https://developer.apple.com/design/human-interface-guidelines/accessibility) / [Material 3 — 48×48dp](https://m3.material.io/foundations/designing/structure)

## 방법 비교

4개 법칙을 같은 축(문제, 공식·숫자, 근거 강도, 남용 주의)으로 놓고 비교했습니다.

| 법칙 | 문제 | 공식·숫자 | 근거 강도 | 남용 주의 |
|---|---|---|---|---|
| 선택 과부하 | 선택지가 많으면 안 고를 수 있다 | 구매율 3% 대 30%(잼 실험) | 메타분석 결과 엇갈림 | 개수만 줄이면 발견 기회가 사라짐 |
| 힉 | 선택지 수만큼 결정이 느려진다 | RT = a + b·log2(n+1) | 단순 선택 과제에 성립 | 읽기·검색 과제엔 그대로 적용 안 됨 |
| 핏츠 | 작고 먼 목표는 오래 걸린다 | ID = log2(A/W + 1) | 탭핑·이동 실험에서 재현 | 거리가 0이면 법칙이 힘을 잃음 |
| 도허티 | 느린 응답은 대화를 끊는다 | 400ms 기준(종전 2초) | IBM 현장 연구 + 지연 실험 | 400ms 미달이 곧 실패는 아님 |

### 선택 과부하: 잼 실험 숫자와 메타분석 결과

2000년 콜럼비아 대학의 아인가르와 레퍼가 캘리포니아 슈퍼마켓에서 잼 시식 코너를 실험했습니다. 24종을 진열한 날과 6종만 진열한 날을 비교했습니다.

| 단계 | 24종 진열 | 6종 진열 |
|---|---|---|
| 코너 앞을 지난 고객 | 242명 | 260명 |
| 시식한 고객 | 145명(60%) | 104명(40%) |
| 구매한 고객 | 4명(3%) | 31명(30%) |

![잼 실험 깔때기: 24종과 6종의 지남/시식/구매 비교](../media/laws-of-ux-4-choice-speed-laws-guide/chart-choice-overload-jam.png)

<span style="background-color: #fff59d"><strong>진열이 많은 쪽이 시식 발걸음은 더 끌었는데, 구매는 시식자 기준 3% 대 30%로 갈렸습니다</strong></span>. 그런데 이 효과가 늘 나오는 건 아닙니다.

2010년 메타분석(실험 50편, 63개 조건)은 평균 효과가 사실상 0이라고 했습니다. 2015년 메타분석(관찰 99건, 참가자 7,202명)은 효과를 확인하면서 조건을 달았습니다. <span style="background-color: #fff59d"><strong>선택 집합이 복잡하거나, 결정 과제가 어렵거나, 선호가 불확실할 때 효과가 나타난다</strong></span>는 것입니다. 적용할 때는 개수부터 줄이기보다 비교하기 어려운 선택지를 먼저 묶거나 거르면 됩니다.

### 힉의 법칙: 선택지 수와 결정 시간의 관계

1952년 힉과 1953년 하이만이 각각 확인한 관계입니다. 선택지 수를 n이라 하면 반응 시간은 RT = a + b·log2(n+1). 선택지가 2배가 될 때마다 일정 시간(b)씩 늘어나는 구조입니다.

기울기 b는 고전 실험에서 대략 0.1~0.2초/비트로 보고됩니다. 이 범위로 계산하면 <span style="background-color: #fff59d"><strong>메뉴가 4개에서 8개로 늘 때 약 100~200ms가 추가되고, 24개에서는 460~930ms로 도허티 기준 400ms를 넘어섭니다</strong></span>.

근데 이 법칙의 출처 실험은 "램프 하나에 불이 들어오면 해당 키를 누른다" 같은 단순 선택 반응 과제입니다. 2018년 리뷰(Proctor & Schneider)는 힉의 법칙이 동등한 확률의 단순 선택 과제에 성립하며, 익숙해진 자극-반응 조합이나 읽기·검색 과제에는 그대로 적용되지 않는다고 정리했습니다. 메뉴 설계에는 방향성으로만 씁니다.

### 핏츠의 법칙: 목표 크기와 이동 시간 계산

1954년 핏츠는 탭핑, 디스크 옮기기, 핀 옮기기 세 과제로 사람의 손동작을 측정했습니다. 이동 시간이 목표의 거리와 크기로 예측된다는 결과였습니다. 원래 공식은 MT = a + b·log2(2A/W)이고, 1992년 맥켄지가 다듬은 Shannon 형태 ID = log2(A/W + 1)이 지금 표준입니다.

핏츠 자신의 데이터에서 반복 동작 처리 속도는 <span style="background-color: #fff59d"><strong>약 9.5~11.5비트/초</strong></span>였습니다. 이 값으로 화면 200px를 이동해 버튼을 누르는 시간을 계산하면 20px 링크는 약 165ms, 44pt 버튼은 약 120ms입니다. 계산은 그림으로 정리했습니다.

![힉의 로그 곡선과 핏츠의 크기-시간 곡선, 도허티 400ms 기준선](../media/laws-of-ux-4-choice-speed-laws-guide/chart-interaction-time-budget.png)

터치 타깃의 최소 크기도 각 플랫폼이 숫자로 정해 뒀습니다. Apple HIG는 iOS 기본 컨트롤 44×44pt(최소 28×28pt), Material 3는 48×48dp(약 9mm)입니다. <span style="background-color: #fff59d"><strong>자주 누르는 버튼은 이 기준 이상으로 두고, 파괴적인 버튼은 작게 멀리 두는 게 원칙입니다</strong></span>.

### 도허티 임계값: 400ms 기준의 근거와 영향

1982년 IBM의 도허티와 타다니가 IBM Systems Journal에 발표한 기준입니다. 시스템 응답 시간 기준을 <span style="background-color: #fff59d"><strong>종전 2초에서 400ms로 끌어내렸고</strong></span>, 원문은 400ms 아래 응답을 "sweet spot"이라고 불렀습니다.

지연이 사용을 줄인다는 방향 증거도 있습니다. 구글의 2009년 실험에서는 <span style="background-color: #fff59d"><strong>검색에 400ms 지연을 주입하자 첫 3주 동안 사용자당 검색 수가 0.44% 줄었고, 지연을 걷어낸 뒤에도 0.21%가 회복하지 않았습니다</strong></span>.

옛 글은 여기에 "의식적 지각에는 300~400ms가 걸린다"는 1991년 연구를 인용했는데, 해당 연구를 찾을 수 없어서 삭제했습니다. 400ms의 근거는 IBM 논문 자체의 현장 데이터로 충분합니다.

## 언제 무엇을 쓰나

| 만드는 것 | 우선 적용 | 하지 말 것 | 근거 |
|---|---|---|---|
| 앱·사이트 최상위 메뉴 | 항목 4~8개, 나머지는 단계·필터로 | 12개 이상 평면 나열 | 힉 + 잼 실험 |
| 요금제·옵션 페이지 | 기본 3~4개 티어 + 비교표 | 20개 이상 평면 노출 | 선택 과부하(조건부) |
| 자주 쓰는 버튼 | 44pt/48dp 이상, 엄지 영역 배치 | 20px 링크를 주요 액션으로 | 핏츠 + HIG/Material |
| 위험한 버튼(삭제 등) | 작게, 거리 두기, 확인 단계 | 크고 붉게 바로 실행 | 핏츠의 역이용 |
| 클릭 뒤 처리 | 400ms 내 즉각 피드백 | 무반응 대기 | 도허티 + 구글 지연 실험 |
| 긴 처리 | 진행 바/스켈레톤으로 구조 먼저 | 빈 화면 + 스피너만 | 도허티 |
| 문서·강의 자료 목차 | 단계별 분해로 한 화면 선택지 축소 | 전체 색인을 첫 화면에 | 힉 |

## 블로그봇이 직접 확인한 것

- 원전 PDF 세 편을 받아 본문을 읽었습니다. Doherty & Thadani 1982(IBM 공개, 18쪽), Iyengar & Lepper 2000(Washington 대학 미러), Fitts 1954(재인쇄)입니다.
- 잼 실험 카운트(242/145/4명, 260/104/31명)를 논문 본문에서 다시 세서 비율(60%/40%, 3%/30%)을 재계산했습니다.
- 도허티 원문에서 "400 milliseconds" 인용 문장 위치를 확인했고, 옛 글이 인용한 "생산성 50%/20% 향상" 숫자가 원문에 있는지 찾았습니다. 못 찾아서 삭제했습니다.
- "1991년 의식적 지각 연구"로 옛 글에 적힌 저자명을 검색했는데 해당 연구가 존재하지 않아서 삭제했습니다.
- 힉의 기울기(0.10~0.20초/비트)와 핏츠 처리 속도(10비트/초)로 실제 UI 치수의 시간을 계산하는 스크립트를 만들어 차트 2장을 그렸습니다. 스크립트와 검증 노트는 sandbox-lane-c에 보관했습니다.
- 1950~2000년 고전 실험들에 공개된 저자 코드·원시데이터는 없습니다. 잼 실험 카운트는 논문 본문 표에서, 메타분석 수치는 각 논문의 서두·초록에서 확인했습니다.

## 한계와 반론

- 선택 과부하는 재현이 엇갈립니다. 2010년 메타분석은 평균 효과 0, 2015년 메타분석은 조건부 효과로 정리했습니다. 선택지 개수만 줄이는 걸로 항상 기대한 효과가 나오지는 않습니다.
- 힉의 법칙은 <span style="background-color: #fff59d"><strong>동등 확률의 단순 선택 과제에서 성립</strong></span>합니다. 메뉴 항목을 읽고 의미를 비교하는 과제에는 그대로 적용되지 않으니, 이 글의 메뉴 적용은 방향성 제안입니다.
- 핏츠 계산은 도식적 추정입니다. 실제 a, b 상수는 입력 장치와 사용자에 따라 다르고, 이 글은 Fitts 1954의 평균 처리 속도만 썼습니다.
- 도허티 400ms는 1982년 메인프레임 대화 세션에서 나온 기준입니다. 오늘날 웹 지표(LCP 등)와 단위가 같지 않고, 원시 데이터는 공개되지 않았습니다.
- 44pt/48dp는 플랫폼 권장값입니다. 두 문서가 핏츠의 법칙을 직접 유도 과정으로 제시하지는 않습니다.
- 이번 실행에서 새로운 사용자 테스트는 하지 않았습니다. 적용 규칙은 원전 근거와 플랫폼 문서의 조합입니다.

## 적용 규칙

1. 최상위 메뉴는 화면당 4~8개로 두고, 그 밖은 카테고리와 필터로 줄입니다(힉, 잼 실험).
2. 요금제·옵션은 기본 3~4개만 노출하고 전체는 비교표로 뺍니다(선택 과부하, 조건부).
3. 자주 누르는 버튼은 44pt/48dp 이상, 엄지가 닿는 영역에 둡니다(핏츠, HIG/Material).
4. 삭제 같은 위험 액션은 작게 두고 확인 단계를 넣습니다(핏츠의 역이용).
5. 클릭 뒤 400ms 안에 뭔가를 반응시킵니다. 못 맞추면 진행 바나 스켈레톤으로 구조부터 보여줍니다(도허티).
6. 문서 목차는 전체 색인 대신 단계별로 나눠 한 화면의 선택지를 줄입니다(힉).
7. 숫자를 인용할 때는 기준과 조건을 함께 적습니다. 잼 실험의 3%/30%도 '시식 정지자 기준'이라는 조건이 붙습니다.

## 자주 묻는 질문

선택지는 꼭 6개 이하로 줄여야 하나요?

아니에요. 선택 과부하 효과는 선택지가 비교하기 어렵고 결정이 어려울 때 뚜렷합니다. 잘 정리된 24개 메뉴는 엉성한 6개보다 낫습니다. 기준은 개수보다 비교 난이도입니다.

400ms를 못 지키면 서비스가 실패하나요?

그렇게 읽으면 안 됩니다. 도허티 기준은 대화형 세션의 생산성 기준이고, 구글 실험도 400ms 지연의 영향은 사용자당 0.44% 수준이었습니다. 못 맞추는 처리에는 진행 상태를 보여주면 됩니다.

힉의 법칙은 모든 UI에 적용되나요?

동등한 확률로 벌어지는 단순 선택에 가까울수록 잘 맞습니다. 항목을 읽고 이해해야 하는 메뉴에는 느슨하게만 적용됩니다. 메뉴를 줄이는 근거로 쓸 때는 방향성으로만 인용하세요.

버튼은 클수록 좋나요?

자주 쓰는 주요 액션은 44pt/48dp 이상이면 충분합니다. 그보다 크게 만드는 건 화면 낭비일 수 있고, 위험한 버튼은 오히려 크기를 줄이고 거리를 두는 게 맞습니다.

## 참고 자료

1. [Laws of UX](https://lawsofux.com/)
2. [Iyengar & Lepper 2000, When Choice is Demotivating (JPSP 79(6))](https://faculty.washington.edu/jdb/345/345%20Articles/Iyengar%20%26%20Lepper%20(2000).pdf)
3. [Scheibehenne, Greifeneder & Todd 2010, Can There Ever Be Too Many Options? (JCR 37(3))](https://scheibehenne.com/ScheibehenneGreifenederTodd2010.pdf)
4. Chernev, Böckenholt & Goodman 2015, Choice Overload: A Conceptual Review and Meta-Analysis, JCP 25(2) 333-358
5. [Doherty & Thadani 1982, The Economic Value of Rapid Response Time (IBM Systems Journal)](https://www.ibm.com/support/pages/sites/default/files/inline-files/EconomicValueofResponseTime.pdf)
6. [Brutlag 2009, Speed Matters for Google Web Search](https://research.google/blog/speed-matters/)
7. [Fitts 1954, The Information Capacity of the Human Motor System (JEP 47(6))](https://www.lri.fr/~mbl/ENS/FONDIHM/2013/papers/Fitts-JEP54.pdf)
8. MacKenzie 1992, Fitts' Law as a Research and Design Tool in HCI, HCI 7(1) 91-139
9. Hick 1952, On the Rate of Gain of Information, QJEP 4(1) 11-26
10. Hyman 1953, Stimulus Information as a Determinant of Reaction Time, JEP 45(3) 188-196
11. Proctor & Schneider 2018, Hick's Law for Choice Reaction Time: A Review, QJEP 71(6)
12. [Apple Human Interface Guidelines — Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
13. [Material 3 — Designing structure(터치 타깃 48×48dp)](https://m3.material.io/foundations/designing/structure)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
