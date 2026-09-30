---
title: "Laws of UX 그룹화 법칙 4개 정리: 근접성·유사성·공통영역·균일연결의 원전 기준과 우선순위"
date: 2026-09-30
author: 한준구(코난쌤)
description: "근접성·유사성·공통영역·균일연결 4개 그룹화 법칙을 베르트하이머 1923, 팔머 1992·1994 원전으로 다시 확인해 강의자료·보고서에서 무엇으로 묶을지 정하는 기준을 정리했습니다."
tags: [UX, UX심리학, "Laws of UX", 게슈탈트, 자료디자인]
refactor_hub_id: ux-laws-05
aliases: [laws-of-ux/12-law-of-common-region, laws-of-ux/13-law-of-proximity, laws-of-ux/14-law-of-similarity, laws-of-ux/16-law-of-uniform-connectedness]
draft: false
sources_read: "팔머 1992(Cognitive Psychology 24(3) 436-447) 본문 PDF를 내려받아 전문을 읽고 공통 영역 원칙 문장, 근접성·유사성 극복 데모, ceteris paribus 단서, 깊이·중첩 데모를 확인했습니다. 팔머 & 록 1994(Psychonomic Bulletin & Review 1(1) 29-55)는 Springer 초록 전문과 본문 발췌로 확인했고 전문 PDF는 유료벽 안쪽이라 읽지 못했습니다. 베르트하이머 1923은 York 대학 Classics의 Ellis 번역 전문으로, 한·험프리스·첸 1999는 PubMed 서지와 초록으로 대조했습니다. 이 고전 연구들에 공개된 저자 코드·원시데이터는 없습니다"
novelty_vs_paper: "같은 학습지 내용을 근접성·유사성·공통영역·연결 4가지로 배열한 예시 그림, 원전 연표와 우선 관계 지배 맵 차트, 옛 글의 '균일 연결이 공통 영역보다 강력하다' 서술 교정은 이 블로그의 작업입니다. 공통 영역이 근접성·유사성을 극복한다(1992), 균일 연결이 근접성·유사성에 맞서 성립한다(1994), 근접성 처리 속도는 균일 연결과 비슷하다(1999)는 각 원전의 주장입니다"
---

## 한눈에 보는 결론

옛 Laws of UX 시리즈 중 '묶음'에 관한 글 4편(공통 영역, 근접성, 유사성, 균일 연결)을 이 페이지 하나로 합쳤습니다. 옛 URL은 이 페이지로 넘어옵니다. 법칙 이름은 [Laws of UX](https://lawsofux.com/)를 따랐구요, 숫자와 결론은 원전 논문을 직접 받아 읽은 값입니다(기준일 2026-09-30).

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>가까이 있으면 묶이고(근접성), 닮았으면 묶이고(유사성), 같은 테두리·배경 안이면 묶이고(공통 영역), 이어져 있으면 묶입니다(균일 연결)</strong></span>. 화면이든 학습지든 보고서든 사람 눈은 이 단서들로 정보 덩어리를 만듭니다.

우선순위 질문에도 원전이 답을 줍니다. <span style="background-color: #fff59d"><strong>1992년 팔머(S. Palmer)는 공통 영역이 근접성·유사성을 이기는 걸 베르트하이머식 그림 데모로 보였고, 1994년 팔머와 록(I. Rock)은 균일 연결이 근접성·유사성에 맞서도 묶음을 만든다는 실험을 더했습니다</strong></span>. 1999년 한(Han) 등이 처리 속도를 재니 <span style="background-color: #fff59d"><strong>근접성은 균일 연결과 비슷하고, 유사성은 느리더라는 결과</strong></span>가 나왔습니다.

| 법칙 | 한줄 요약 | 제안(원전) | 원전이 보인 관계 | 자료 설계 쓰임 |
|---|---|---|---|---|
| 근접성 | 가까운 요소끼리 묶인다 | 베르트하이머 1923 | 균일 연결과 속도 비슷(1999) | 항목 간격 < 덩어리 간격 |
| 유사성 | 닮은 요소끼리 묶인다 | 베르트하이머 1923 | 공통 영역·균일 연결에 밀림 | 같은 종류 = 같은 색·모양 |
| 공통 영역 | 같은 테두리·배경 안이면 묶인다 | 팔머 1992 | 근접성·유사성을 이긴다(데모) | 박스·배경으로 덩어리 만들기 |
| 균일 연결 | 이어진 요소는 묶인다 | 팔머 & 록 1994 | 근접성·유사성을 이긴다(실험) | 화살표·연결선·단계 표시 |

근데 이 순위를 만능으로 쓰면 안 됩니다. 팔머는 1992년 논문에서 공통 영역이 <span style="background-color: #fff59d"><strong>"다른 조건이 같을 때(ceteris paribus)" 성립하는 규칙</strong></span>이라고 못박았습니다. 단서 여럿이 부딪히면 결과를 예측할 정량 법칙은 아직 없다는 문장도 같은 논문에 있습니다.

## 무엇을 비교했나

이 허브로 합쳐진 옛 글은 4편입니다. 공통 영역, 근접성, 유사성, 균일 연결(모두 2025-05-06 작성). 네 편 다 lawsofux.com 한 페이지씩을 옮겨 적은 수준이라 AdSense 심사에서 '복제 콘텐츠'로 잡혔습니다. 이번에 원전을 대조해 다시 썼습니다.

읽고 대조한 자료는 이렇습니다(기준일 2026-09-30).

1. [Laws of UX — Law of Common Region](https://lawsofux.com/law-of-common-region/)
2. [Laws of UX — Law of Proximity](https://lawsofux.com/law-of-proximity/)
3. [Laws of UX — Law of Similarity](https://lawsofux.com/law-of-similarity/)
4. [Laws of UX — Law of Uniform Connectedness](https://lawsofux.com/law-of-uniform-connectedness/)
5. 베르트하이머 1923, Untersuchungen zur Lehre von der Gestalt II, Psychologische Forschung 4, 301-350 — [Ellis 번역 전문(York 대학 Classics)](https://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm)
6. 팔머 1992, Common Region: A New Principle of Perceptual Grouping, Cognitive Psychology 24(3), 436-447 — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/001002859290014S)
7. 팔머 & 록 1994, Rethinking Perceptual Organization: The Role of Uniform Connectedness, Psychonomic Bulletin & Review 1(1), 29-55 — [Springer](https://link.springer.com/article/10.3758/BF03200760)
8. 피터슨 1994, The Proper Placement of Uniform Connectedness, Psychonomic Bulletin & Review 1(4), 509-514 — [Springer](https://link.springer.com/article/10.3758/BF03210956)
9. 한·험프리스·첸 1999, Uniform Connectedness and Classical Gestalt Principles of Perceptual Grouping, Perception & Psychophysics 61(4), 661-674 — [PubMed](https://pubmed.ncbi.nlm.nih.gov/10370335)

## 방법 비교

4개 법칙을 같은 축(무엇으로 묶나, 누가 제안했나, 원전이 보인 우선 관계, 강도의 한계)으로 놓고 비교했습니다.

| 법칙 | 무엇으로 묶나 | 제안 | 원전이 보인 우선 관계 | 강도의 한계 |
|---|---|---|---|---|
| 근접성 | 요소 사이 거리 | 1923 베르트하이머 | 균일 연결과 속도 비슷(1999) | 깊이 지각에 영향받음 |
| 유사성 | 색·모양·크기·방향 | 1923 베르트하이머 | 상대적으로 처리가 느림(1999) | 색만 쓰면 접근성 문제 |
| 공통 영역 | 테두리·배경 영역 | 1992 팔머 | 근접성·유사성을 이긴다(데모) | 가장 작은 영역이 이김 |
| 균일 연결 | 선·색띠 등 연결 | 1994 팔머 & 록 | 근접성·유사성을 이긴다(실험) | 층위 배치 논쟁 있음(피터슨 1994) |

![원전 연표와 우선 관계 지배 맵](../media/laws-of-ux-4-gestalt-grouping-laws-guide/chart-grouping-dominance-map.png)

### 근접성: 간격이 곧 구조다

1923년 베르트하이머가 점 줄 실험에서 "가까운 쌍끼리 묶인다"는 첫 그룹화 원칙을 제안했습니다. 원전은 창밖 풍경 이야기로 시작합니다. 하늘·집·나무를 327개 명도 조각으로 보는 사람은 없다는 겁니다. 그 나눔은 내 마음대로 되는 게 아니고 자극 구조가 정한다는 주장이구요.

디자인 적용은 간단합니다. <span style="background-color: #fff59d"><strong>덩어리 안 간격은 줄이고, 덩어리 사이 간격은 크게 벌리면 됩니다</strong></span>. 검색 결과 목록에서 결과 사이 여백이 결과 내부(제목-주소-설명) 간격보다 크게 벌어진 게 대표 사례입니다. lawsofux.com 근접성 페이지가 같은 예를 듭니다.

### 유사성: 같은 종류는 같은 모양

같은 원전(1923)에서 밝기가 닮은 요소끼리 묶이는 게 확인됐습니다. 색·모양·크기·방향이 닮으면 묶입니다. 링크처럼 문서 안에서 한 가지 역할을 가진 요소는 한 가지 스타일로 유지하면 찾기 쉬워진다는 게 lawsofux.com 유사성 페이지의 권장입니다.

주의할 점이 하나 있습니다. <span style="background-color: #fff59d"><strong>색만으로 구분하면 색약 독자에게 묶음이 안 보입니다</strong></span>. 모양이나 라벨을 같이 바꾸면 됩니다.

### 공통 영역: 박스가 이긴다

팔머 1992의 원칙 정의는 이렇습니다. 연결된 균질한 색·질감 영역이나 닫힌 윤곽선 안에 있으면 묶인다. 테두리를 그리거나 배경색을 깔면 정보 덩어리가 만들어집니다.

이 논문의 백미는 우선순위 데모입니다. <span style="background-color: #fff59d"><strong>점들을 근접성대로 묶어 놓고 타원으로 다른 쌍을 감싸면 사람들은 타원 안 쌍으로 봅니다</strong></span>. 밝기 유사성으로 묶어 놓아도 마찬가지구요. 대시 선, 착시 윤곽, 경계가 대부분 가려진 다른 배경색까지, <span style="background-color: #fff59d"><strong>그려진 테두리가 없어도 '같은 영역'이면 성립합니다</strong></span>.

실무 디테일도 원전에 있습니다. <span style="background-color: #fff59d"><strong>영역이 겹치면 더 작은 영역이 이깁니다</strong></span>. 영역을 중첩하면 계층 구조도 만들 수 있구요. 미국 지도에서 피츠버그는 해리스버그보다 콜럼버스와 가까워도, 펜실베이니아 주 안이라 해리스버그와 묶입니다. 같은 단어 4개를 다르게 나눈 현수막 두 장이 전혀 다르게 읽힌다는 예도 본문에 있습니다.

### 균일 연결: 선으로 잇는 묶음

팔머 & 록 1994가 제안했습니다. <span style="background-color: #fff59d"><strong>균질한 성질을 가진 닫힌 영역은 처음부터 '하나의 유닛'으로 지각된다는 원칙입니다</strong></span>. 근접성·유사성이 반대 방향으로 작동해도 연결된 쪽이 이기는 걸 실험으로 보였습니다.

여기서 옛 글을 고쳤습니다. 옛 글은 균일 연결을 "근접성·유사성·공통 영역보다 강력한 원칙"이라고 적었는데, 원전 초록은 근접성·유사성에 대한 실험까지만 말합니다. 저자들은 균일 연결을 그룹화 원칙이 하나 더 늘어난 것으로 취급하지 않고, 그룹화 이전에 화면을 유닛으로 쪼개는 <span style="background-color: #fff59d"><strong>별개 층위의 원리</strong></span>로 구분했습니다. 서술을 원전대로 바로잡았습니다.

시간축 반론도 있습니다. 1999년 한·험프리스·첸의 비교에서 <span style="background-color: #fff59d"><strong>근접성은 균일 연결만큼 빠르게 처리됐고, 모양 유사성은 더 느렸습니다</strong></span>. 피터슨 1994는 균일 연결을 처리 순서 맨 앞에 두는 이론에 반대하는 논평을 냈고, 팔머 & 록이 같은 권에서 반응했습니다. 학계 정리는 아직 안 끝났습니다.

## 언제 무엇을 쓰나

강의자료·업무 문서에서 묶음 수단을 고를 때는 이 순서로 정하면 됩니다.

| 상황 | 첫 번째 수단 | 이유 | 함께 쓰면 좋은 것 |
|---|---|---|---|
| 문항과 보기 정렬 | 근접성 | 간격만으로 즉시 효과 | 라벨-항목 간격 작게 |
| 섹션 구분 | 공통 영역 | 배경·테두리가 간격보다 강함 | 중첩으로 하위 계층 |
| 종류별 안내(개념/예시/주의) | 유사성 | 같은 종류 = 같은 색 | 모양·라벨 병행(접근성) |
| 절차·순서 안내 | 균일 연결 | 화살표가 순서를 고정 | 단계 진행 표시 |
| 덩어리가 너무 많을 때 | 공통 영역 중첩 | 작은 영역이 우선 | 2단계 이상 중첩은 피하기 |

![같은 내용을 4가지 묶음 처리로 배열한 학습지 예시](../media/laws-of-ux-4-gestalt-grouping-laws-guide/diagram-same-content-four-treatments.png)

같은 12항목(개념-예시-주의 3쌍 4줄)을 묶음 단서만 바꿔 그린 그림입니다. A는 단서가 없어 줄 구분이 안 서고, B는 간격으로, C는 색으로, D는 박스와 화살표로 구조가 잡힙니다. D가 가장 명확한데 만들 비용도 가장 큽니다. 자료 성격에 맞게 고르면 됩니다.

## 블로그봇이 직접 확인한 것

- 팔머 1992 본문 PDF(12쪽)를 내려받아 전문을 읽었습니다. 원칙 정의 문장, 근접성·유사성 극복 데모(그림 2C·2D), ceteris paribus 단서, 깊이 효과, 가장 작은 영역 우선, 계층 중첩, 피츠버그 지도 예시를 본문에서 확인했습니다.
- 팔머 & 록 1994는 Springer 초록 전문과 본문 발췌를 읽었습니다. 전문 PDF는 유료벽 안쪽이라 읽지 못했고, 균일 연결 서술은 초록이 확인하는 범위로 제한했습니다.
- 베르트하이머 1923은 York 대학 Classics의 Ellis 번역 전문으로 근접성·유사성 서술을 확인했습니다.
- lawsofux.com 4개 법칙 페이지를 직접 불러와 정의·권장·예시가 옮겨 적힌 것을 확인했습니다. 검색 결과 간격 예시(근접성), 지식 패널 테두리 예시(균일 연결)가 원 사이트에 있습니다.
- <span style="background-color: #fff59d"><strong>옛 글의 '균일 연결이 공통 영역보다 강력하다' 서술과 '파란 밑줄 30년 표준' 숫자를 원전에서 찾지 못해 고쳤습니다</strong></span>. Trello·Apple·Airbnb 등 특정 제품 서술도 원전 확인이 안 되어 일반 패턴으로 바꿨습니다.
- 차트 2장을 직접 그렸습니다. 스크립트와 원전 PDF는 sandbox-lane-d에 보관했습니다.

## 한계와 반론

- 공통 영역의 우선권은 데모 기반입니다. 팔머 1992는 현상학적 그림 데모 중심이고, "공통 영역 > 근접성"을 숫자로 계산한 근거는 이 글에 없습니다.
- 균일 연결의 '이김'은 초록이 확인하는 범위입니다. 본문 정량 결과까지 확인하려면 유료 전문이 필요합니다.
- 원칙은 모두 ceteris paribus 규칙입니다. 여러 단서가 부딪히는 실제 자료에서 결과를 예측하는 공식은 원전에도 없습니다. 최종 확인은 독자 몇 명에게 자료를 보여보는 게 낫습니다.
- 피터슨 1994는 균일 연결의 층위 배치에 반론을 제기했습니다. 논쟁이 끝난 주제가 아닙니다.
- 이번 실행에서 새로운 사용자 테스트는 하지 않았습니다. 적용 규칙은 원전 근거와 lawsofux.com 권장의 조합입니다.

## 적용 규칙

1. <span style="background-color: #fff59d"><strong>덩어리 안 간격은 덩어리 사이 간격의 절반 이하로 잡습니다</strong></span>(근접성, 베르트하이머 1923).
2. 라벨은 붙이는 항목에 가장 가깝게 둡니다. 폼에서 라벨-입력란 간격이 라벨끼리 간격보다 작아야 합니다(근접성).
3. 독립 정보 단위에는 테두리나 배경색을 줍니다. 카드 UI가 그 예입니다(공통 영역, 팔머 1992).
4. 영역이 겹칠 때는 가장 작은 영역이 묶음을 이깁니다. 박스 3겹 이상 중첩은 피합니다(팔머 1992).
5. 순서가 중요한 절차는 화살표·연결선으로 잇습니다. 단계 진행 표시가 그 예입니다(균일 연결, 팔머 & 록 1994).
6. 같은 역할엔 같은 스타일, 다른 역할엔 다른 스타일을 유지합니다(유사성). 색만 바꾸지 말고 모양·라벨을 함께 바꿉니다.
7. <span style="background-color: #fff59d"><strong>묶음 단서끼리 부딪히게 두지 않습니다</strong></span>. 간격과 테두리가 서로 다른 덩어리를 가리키면 원전도 결과를 예측해 주지 않습니다(팔머 1992).

## 자주 묻는 질문

묶음 법칙 중 가장 강한 것은 뭔가요?

공통 영역과 균일 연결이 근접성·유사성을 이깁니다. 1992년 데모와 1994년 실험이 그 방향입니다. 근데 이건 다른 조건이 같을 때 이야기이고, 실제 자료에서는 단서가 섞입니다.

근접성만으로 자료를 정리해도 되나요?

간격 조절만으로도 구조가 잡힙니다. 1999년 비교에서 근접성 처리 속도는 균일 연결과 비슷했습니다. 비용이 가장 낮은 첫 수단으로 적합합니다.

게슈탈트는 100년 지난 이론인데 아직 쓸만한가요?

근접성·유사성은 1923년 제안 뒤 지금도 UX 권장의 기본입니다. 공통 영역(1992)과 균일 연결(1994)은 오히려 90년대에 추가된 최근 원칙입니다. 층위 논쟁은 진행형입니다(피터슨 1994).

학습지에 바로 적용할 하나만 고르면요?

문항-보기-라벨 간격부터 조입니다. 비용 없이 근접성이 바로 작동합니다. 여기에 박스(공통 영역)를 얹으면 대부분의 학습지에서 충분합니다.

## 참고 자료

1. [Laws of UX](https://lawsofux.com/)
2. [Laws of UX — Law of Common Region](https://lawsofux.com/law-of-common-region/)
3. [Laws of UX — Law of Proximity](https://lawsofux.com/law-of-proximity/)
4. [Laws of UX — Law of Similarity](https://lawsofux.com/law-of-similarity/)
5. [Laws of UX — Law of Uniform Connectedness](https://lawsofux.com/law-of-uniform-connectedness/)
6. [베르트하이머 1923, Laws of Organization in Perceptual Forms(Ellis 번역, York 대학 Classics)](https://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm)
7. [Palmer 1992, Common Region: A New Principle of Perceptual Grouping(Cognitive Psychology 24(3))](https://www.sciencedirect.com/science/article/pii/001002859290014S)
8. [Palmer & Rock 1994, Rethinking Perceptual Organization(Psychonomic Bulletin & Review 1(1))](https://link.springer.com/article/10.3758/BF03200760)
9. [Peterson 1994, The Proper Placement of Uniform Connectedness(Psychonomic Bulletin & Review 1(4))](https://link.springer.com/article/10.3758/BF03210956)
10. [Han, Humphreys & Chen 1999, Uniform Connectedness and Classical Gestalt Principles(Perception & Psychophysics 61(4))](https://pubmed.ncbi.nlm.nih.gov/10370335)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
