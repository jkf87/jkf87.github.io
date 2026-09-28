---
title: "AI 에이전트 결과물이 '이건 아닌데'일 때: taste를 검증 루브릭으로 바꾸는 하네스 verifier 설계법"
date: 2026-09-28
author: 한준구(코난쌤)
description: "AI 에이전트 결과물이 어딘가 미흡한데 그 이유가 말로 쓰이지 않는 상태에서 시작해, 암묵지(taste)를 측정 가능한 루브릭으로 바꾸는 4단계와 측정 라벨 3종을 정리했습니다. WCAG 명암비는 파이썬으로 직접 재계산해 확인했습니다."
tags:
  - 하네스
  - verifier
  - 루브릭
  - LLM 에이전트
  - 암묵지
refactor_hub_id: harness-self-improve-16
aliases:
  - harness-verifier-rubric-taste-to-code-2026-05-09
  - implicit-knowledge-to-verifier-design-2026-05-09
  - implicit-knowledge-to-verifier-design-2026-05-09/index
  - tacit-knowledge-to-rubric-verifier-design-2026-05-09
  - tacit-to-paper-verifier-design-2026-05-09
  - tacit-to-paper-verifier-design-2026-05-09/index
draft: false
sources_read: "옛 글 4편 본문을 전부 읽고 병합했습니다. arXiv 2009.09025(COMET)과 arXiv 2305.17926(FairEval)은 HTML 본문까지 읽어 인용 수치(80개 질의 중 66개 판정 역전)를 대조했고, 두 논문의 저자 코드(github.com/Unbabel/COMET, github.com/i-Eval/FairEval) 공개 여부를 저장소에서 확인했습니다. UbD 3단계는 Wiggins·McTighe(2005) PDF 서술과 대조했고, WCAG 수치는 WebAIM의 WCAG 2 기준 설명과 대조한 뒤 파이썬 표준 라이브러리로 재계산했습니다. 폴라니 문구는 The Tacit Dimension(1966) 인용 자료로 확인했습니다."
novelty_vs_paper: "UbD 3단계 구조, WCAG 4.5:1·7:1 기준, COMET의 사람 판단 상관 성능, LLM 채점의 순서 편향 실험(66/80)은 각 1차 출처의 주장입니다. 4단계 변환 절차·측정 라벨 3종·taste residue 구분은 옛 글(2026-05-09 커뮤니티 토론)의 프레임이고, 도표 2장 제작, WCAG 명암비 7색 재계산, 폴라니 인용 문구 정정, 폰트 기준 모순 지적은 블로그봇의 작업입니다."
---

## 한눈에 보는 결론

본 글은 2026-05-09 작성된 동일 주제 글 4편을 병합한 통합 가이드입니다. 주제는 AI 에이전트 하네스의 verifier 설계 방법론입니다. 에이전트가 생성한 결과물을 보고 <span style="background-color: #fff59d"><strong>"미흡하다"고 판단할 수 있으면서도 그 판정 근거를 문장화하지 못하는 상태</strong></span>를 출발점으로 삼고, 이를 측정 가능한 루브릭으로 변환하는 절차를 정리했습니다.

이 상태의 이름은 오래전부터 있었습니다. 폴라니는 <span style="background-color: #fff59d"><strong>"We can know more than we can tell"</strong></span>(The Tacit Dimension, 1966)로 암묵지를 정의했습니다. 좋은 결과물을 알아보는 능력은 있는데 그 기준은 말로 떨어지지 않는다는 것입니다. verifier 설계의 실제 병목도 같은 지점입니다. 코드 작업 이전에 <span style="background-color: #fff59d"><strong>"잘 됐다"를 문장으로 적는 작업</strong></span>에서 멈춥니다(옛 글 4편의 공통 기록).

병합 과정에서 옛 글의 주장을 1차 출처와 대조했고, 정량 verifier 예시로 WCAG 명암비 계산을 직접 실행했습니다. 요약은 다음 표와 같습니다.

| 정리 항목 | 내용 |
|---|---|
| 출발점 | 폴라니 암묵지 — "We can know more than we can tell"(1966) |
| 절차 | 목표를 동사로 → 차원 분해 → 측정 가능한 문장 → 5회 분산 테스트 |
| 측정 라벨 | [정량] 코드, [페르소나-LLM] 기준 독자 지정, [사람] 교차 채점 |
| 분리 | working verifier(매 단계)와 final verifier(최종 게이트) |
| 설계 순서 | 백워드 디자인(UbD)과 동일 구조 — 평가 증거를 먼저 설계 |
| 잔여분 | 루브릭으로 80%까지, 최종은 사람 게이트(원 토론 운영 기준) |

LLM 채점의 체계적 편향은 실측 연구로 확인된 현상입니다(arXiv 2305.17926). 그래서 <span style="background-color: #fff59d"><strong>전 항목을 LLM 채점에 맡기면 무한 PASS로 수렴</strong></span>할 위험이 있고, 항목마다 측정 주체를 지정하는 것이 이 글의 핵심 처방입니다.

## 무엇을 비교했나

병합 대상 글은 다음 4편입니다. 모두 2026-05-09 오픈클로 커뮤니티 토론을 소스로 하는 재작성이라, 상호 보강 관계입니다.

1. 암묵지를 종이로 끄집어내는 방법 — 하네스 Verifier 설계법(병합 기준본, 최장 버전)
2. 암묵지를 종이로 끄집어내는 법 — 하네스 verifier 설계법(구어체 재작성)
3. 암묵지를 종이로 끄집어내는 방법 — 하네스 Verifier 설계법(구조화 버전)
4. 암묵지를 종이로 끄집어 내는 방법 — 하네스 verifier 설계법(절차·체크리스트 버전)

대조에 사용한 1차 출처는 다음과 같습니다.

- [Wiggins & McTighe, Understanding by Design(2005) PDF](https://andymatuschak.org/files/papers/Wiggins,%20McTighe%20-%202005%20-%20Understanding%20by%20design.pdf)
- [WebAIM Contrast Checker(WCAG 명암비 기준)](https://webaim.org/resources/contrastchecker/)
- [COMET: A Neural Framework for MT Evaluation(arXiv 2009.09025)](https://arxiv.org/abs/2009.09025) · [Unbabel/COMET 코드](https://github.com/Unbabel/COMET)
- [Large Language Models are not Fair Evaluators(arXiv 2305.17926)](https://arxiv.org/abs/2305.17926) · [i-Eval/FairEval 코드](https://github.com/i-Eval/FairEval)
- Michael Polanyi, The Tacit Dimension(1966)

## 방법 비교

루브릭 항목별 측정 주체를 세 방법으로 구분합니다. 세 방법을 같은 축으로 비교하면 다음과 같습니다.

| 측정 방법 | 판정 대상 | 판정 방식 | 신뢰 근거 | 비용 | 한계 |
|---|---|---|---|---|---|
| [정량] 코드 | 폰트 크기, 색대비, 링크 상태, 테스트 exit code | 스크립트 실행 | 결정적 — 같은 입력에 같은 결과 | 거의 0원, 초 단위 | 코드로 셀 수 있는 항목만 판정 |
| [페르소나-LLM] | 톤 일치, 이해 쉬움, 흐름 | 기준 독자를 프롬프트에 명시해 채점 | 페르소나가 기준을 고정 | 저렴, 초~분 단위 | 동일 계열 모델의 맹점 공유 위험 |
| [사람] | 최종 품질, taste 잔여분 | 5건 직접 채점 후 LLM 점수와 상관계수 비교 | 상관계수로 루브릭 신뢰 확인 | 고비용, 확장 불가 | 표본이 적으면 신뢰 하락 |

도메인별로 즉시 사용 가능한 정량 신호는 다음과 같습니다.

| 도메인 | 정량 신호 예시 |
|---|---|
| 코드 | test exit code, type-check(tsc·mypy), lint(ESLint·Ruff), build 성공 |
| 번역 | COMET·BLEU 점수, 길이 비율, 고유명사 보존률 |
| 블로그·문서 | 링크 HTTP 상태, 맞춤법 검사, 이미지 alt 존재 |
| UI | 스크린샷 diff, DOM 스냅샷, WCAG 명암비 |

전체 변환 절차를 한 장으로 정리하면 다음 그림입니다.

![암묵지에서 verifier까지의 변환 절차](../media/ai-agent-verifier-rubric-guide-2026/chart-01-taste-to-verifier-pipeline.png)

1단계에서 목표를 동사 문장으로 적습니다. "좋은 카드뉴스"는 판정할 수 없으므로 <span style="background-color: #fff59d"><strong>"독자가 5초 안에 핵심을 말할 수 있는가"</strong></span> 형태로 바꿉니다. 2단계에서 사실 정확성·명료성·UX 등 3~6개 차원으로 분해합니다. 3단계에서 각 항목을 Y/N 또는 척도 문장으로 바꿉니다. "이미지가 어울리는가"라는 표현은 판정이 불가능하고, <span style="background-color: #fff59d"><strong>"키워드-이미지 의미 연결 Y/N"</strong></span> 형태여야 채점이 가능합니다. 4단계에서 측정 주체 라벨을 붙이고 같은 결과물에 5회 반복 실행해 점수 분산을 확인합니다.

옛 글의 카드뉴스 예시를 변환 규칙에 적용하면 이렇습니다. 시각 자료 항목은 "이미지-텍스트 의미 연결 Y/N[페르소나-LLM], 해상도 기준 충족[정량], 톤 일치[페르소나-LLM]"으로 분해됩니다. 콘텐츠 명료성은 "슬라이드당 메시지 1개[정량], 기준 독자의 5초 요약 가능[페르소나-LLM]"으로, UX는 "색명암비 기준 충족[정량], 텍스트 여백 준수[정량], 정보 위계[페르소나-LLM]"으로 분해됩니다.

작성(writer)을 먼저 설계하고 검증(verifier)을 나중에 붙이면 verifier가 writer의 변형판이 됩니다. 같은 모델 계열의 맹점을 공유하므로 동일한 실수를 걸러내지 못합니다. 그래서 설계 순서는 교육학 백워드 디자인과 동일하게 <span style="background-color: #fff59d"><strong>목표 정의 → 증거(루브릭) 설계 → 경험(워크플로) 설계</strong></span> 순으로 가져갑니다.

## 언제 무엇을 쓰나

- 정량 측정이 가능한 항목은 전부 정량 신호로 처리합니다. <span style="background-color: #fff59d"><strong>verifier마다 정량 신호를 최소 1개 포함</strong></span>합니다. 정량 판정이 FAIL이면 LLM 채점이 PASS를 낼 수 없습니다.
- 정성 판정이 필요한 항목은 페르소나를 먼저 정의합니다. "25~35세 직장인이 5초 안에 핵심을 요약할 수 있는가"처럼 기준 독자를 명시하면 LLM 채점의 기준이 고정됩니다.
- 사람 채점은 두 지점으로 제한합니다. 초기 검증(5건 교차 채점)과 최종 게이트입니다.
- 매 단계에서 동작하는 working verifier는 빠르고 저렴하게, 최종 게이트 final verifier는 깊고 정확하게 만듭니다. 이 구분은 교육 평가의 형성평가·총괄평가 구분에 대응합니다.
- 매 단계 검사와 최종 검사를 하나로 합치면 양쪽 판정이 모두 약해집니다. 분리를 유지합니다.

## 블로그봇이 직접 확인한 것

병합 과정에서 옛 글의 주장을 1차 출처와 대조했습니다. 결과는 다음과 같습니다.

- UbD 백워드 디자인 3단계(원하는 결과 정의 → 수용 가능한 증거 설계 → 학습 경험·수업 설계)는 원문 서술과 일치합니다. 옛 글의 "평가를 먼저 설계하라"는 요약은 2단계 표현에 근거가 있습니다.
- 폴라니 문구는 정확히는 "We can know more than we can tell"입니다. <span style="background-color: #fff59d"><strong>옛 글 3편의 "We know more than we can tell"은 어순이 다른 인용</strong></span>이므로 이 글에서 정정합니다.
- WCAG 명암비 기준은 <span style="background-color: #fff59d"><strong>AA 일반 텍스트 4.5:1, 큰 텍스트 3:1, AAA 일반 텍스트 7:1, 큰 텍스트 4.5:1</strong></span>입니다. 옛 글의 4.5:1·7:1 표기와 일치합니다.
- COMET(arXiv 2009.09025) 본문을 확인했습니다. 신경망 기반 MT 평가 프레임워크로 원문(source)과 참조번역(reference) 정보를 함께 사용하며, WMT 2019 Metrics 태스크에서 사람 판단과의 상관으로 새로운 표준 성능을 기록했다는 서술입니다. <span style="background-color: #fff59d"><strong>참조번역이 필요한 지표</strong></span>라는 점도 본문에 명시돼 있습니다. 코드는 github.com/Unbabel/COMET에 공개돼 있고 현재도 관리됩니다.
- LLM 채점 편향(arXiv 2305.17926) 본문을 확인했습니다. 응답 순서만 바꿔도 비교 결과가 뒤집히며, ChatGPT를 심판으로 사용한 실험에서 <span style="background-color: #fff59d"><strong>80개 질의 중 66개에서 순서 조작으로 우위 판정이 역전</strong></span>됐습니다. 코드와 사람 어노테이션은 github.com/i-Eval/FairEval에 공개돼 있습니다.

정량 verifier 실습으로 WCAG 명암비 계산식을 파이썬 표준 라이브러리로 재구현해 회색 7종을 재계산했습니다(M2 Max, macOS 26.5.1, Python 3). 실행 결과의 일부는 다음과 같습니다.

```text
$ python3 verify_contrast.py
foreground                 ratio  AA(4.5) AAA(7.0)
#000000 black              21.00   PASS     PASS
#767676 gray                4.54   PASS     FAIL
#777777 gray                4.48   FAIL     FAIL
#999999 mid gray            2.85   FAIL     FAIL
#B3B3B3 light gray          2.10   FAIL     FAIL
```

![회색 텍스트 7종의 실측 명암비](../media/ai-agent-verifier-rubric-guide-2026/chart-02-wcag-contrast-measured.png)

<span style="background-color: #fff59d"><strong>#767676은 4.54로 AA를 통과하고 AAA는 실패</strong></span>합니다. 한 단계 밝은 #777777은 4.48로 AA에서 실패합니다. LLM 채점에 "가독성이 좋은가"라는 질문을 넘기는 대신, 이 표로 판정하는 것이 정량 verifier의 실제 모습입니다. 이번 실행에서 재계산한 대상은 WCAG 명암비뿐이며, 옛 글의 카드뉴스 루브릭 전체는 재현하지 않았습니다.

## 한계와 반론

- 4편 모두 동일 커뮤니티 토론(2026-05-09)의 재작성이므로 독립 근거로 취급할 수 없습니다. 상관계수 0.7 기준과 80/20 구분(taste residue)은 원 토론의 운영 기준이며 외부 출처로 검증하지 못했습니다.
- LLM 채점 편향 연구는 순서(위치) 편향이 중심입니다. 옛 글이 사용한 self-similarity bias라는 명칭의 효과는 토론 내 관찰에 가깝고, 이번 대조에서 별도 출처를 확인하지 못했습니다.
- GAN 비유(discriminator가 generator와 함께 학습하는 구조와 하네스의 inference 루프 차이)는 개념 설명이며 측정값이 없습니다.
- 카드뉴스 메이커 사례는 2026-05 프로젝트 기록입니다. 이번 실행에서 재현한 것은 WCAG 명암비 계산뿐입니다.
- 옛 글 간 모바일 폰트 기준이 16pt와 24pt로 서로 다릅니다. 도메인별 수치는 프로젝트마다 재정의할 대상이므로 본 글은 특정 수치를 권고하지 않습니다.

## 적용 규칙

1. 루브릭 항목을 적을 때마다 [정량] [페르소나-LLM] [사람] 라벨을 명시합니다. 라벨이 없으면 LLM 채점이 전 항목을 차지합니다.
2. verifier마다 정량 신호를 최소 1개 포함합니다. 본 글의 WCAG 재계산(10여 줄 스크립트, 회색 7종 판정)이 최소 규모의 예시입니다.
3. 설계 순서는 목표(동사) → 증거(루브릭) → 경험(워크플로) 순으로 합니다. UbD 3단계와 동일한 순서입니다.
4. working verifier와 final verifier를 분리합니다. 매 단계 검사는 빠르게, 최종 게이트는 깊게 설계합니다.
5. 같은 결과물에 verifier를 5회 실행해 점수 분산을 확인합니다. 분산이 크면 루브릭이 아직 모호하다는 신호이므로 항목을 더 분해합니다.
6. 초기 검증 단계에서 사람이 5건 직접 채점해 LLM 점수와 상관계수를 비교합니다(운영 기준 0.7). 미달 시 항목을 다듬습니다.
7. 루브릭 만점인데 결과물이 미흡한 케이스를 수집해 주기적으로 루브릭을 갱신합니다. 측정이 목표로 바뀌면 지표가 무너진다는 <span style="background-color: #fff59d"><strong>굿하트 법칙</strong></span>에 대한 대비입니다.
8. 최종 게이트는 <span style="background-color: #fff59d"><strong>사람 판정으로 유지</strong></span>합니다. 전 과정 자동화 시 결과물이 평균 품질로 수렴한다는 것이 원 토론의 결론입니다.

## 참고 자료

- [Understanding by Design, 2nd ed.(Wiggins & McTighe, 2005) PDF](https://andymatuschak.org/files/papers/Wiggins,%20McTighe%20-%202005%20-%20Understanding%20by%20design.pdf)
- [WebAIM WCAG 명암비 기준 설명](https://webaim.org/resources/contrastchecker/)
- [COMET — A Neural Framework for MT Evaluation(arXiv 2009.09025)](https://arxiv.org/abs/2009.09025), [Unbabel/COMET 저장소](https://github.com/Unbabel/COMET)
- [Large Language Models are not Fair Evaluators(arXiv 2305.17926)](https://arxiv.org/abs/2305.17926), [i-Eval/FairEval 저장소](https://github.com/i-Eval/FairEval)
- Michael Polanyi, The Tacit Dimension(1966)
- 병합된 옛 글 4편은 draft 상태로 보존되며, 옛 URL은 이 글의 aliases로 연결됩니다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
