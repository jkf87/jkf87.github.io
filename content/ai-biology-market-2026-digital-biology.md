---
title: "AI는 생물학을 어디까지 바꾸고 있나: 단백질에서 세포, 신약개발 공장까지"
date: 2026-06-21
slug: ai-biology-market-2026-digital-biology
tags:
  - AI
  - biology
  - drug-discovery
  - NVIDIA
  - AlphaFold
  - biotech
  - bioinformatics
  - digital-biology
description: "AlphaFold 3, Arc Virtual Cell Challenge, NVIDIA-Lilly 협업, Evo 2와 AI 신약개발 시장 전망을 통해 생물학 AI가 구조 예측에서 세포 반응·실험 자동화·제약 R&D 인프라로 확장되는 흐름을 정리했다."
draft: false
---

세포를 컴퓨터 안에 넣을 수 있을까?

이 질문은 SF처럼 들리지만, 2026년 현재 생물학 AI 시장을 이해하는 가장 좋은 출발점이기도 하다. 다만 여기서 말하는 “컴퓨터 안의 세포”는 매트릭스식 완전한 생명 시뮬레이션이 아니다. 아직 AI가 클릭 한 번으로 신약을 만들고, 동물실험과 임상을 통째로 대체하는 단계도 아니다.

지금 실제로 벌어지는 변화는 조금 더 현실적이고, 그래서 더 중요하다.

**AI가 전임상 연구, 타깃 발굴, 분자 설계, 세포 반응 예측, 실험 자동화의 병목을 줄이는 인프라로 들어오고 있다.**

생물학은 원래 데이터가 많으면서도 부족한 분야다. 유전체, 단백질 구조, 세포 이미지, 단일세포 RNA 데이터처럼 거대한 데이터가 쌓이지만, 정작 특정 질병·특정 세포·특정 약물 후보에 대해 “이걸 넣으면 실제 생체에서 무슨 일이 벌어지나?”를 예측하려면 여전히 실험이 필요하다. 이 간극이 바로 AI가 파고드는 자리다.

이 글에서는 AlphaFold 3, Arc Institute의 Virtual Cell Challenge, NVIDIA와 Eli Lilly의 AI 연구소, Evo 2 같은 genomic foundation model, 그리고 Xaira·Recursion 같은 TechBio 기업 흐름을 묶어서 본다. 핵심 질문은 하나다.

> 왜 지금 생물학이 AI 인프라 시장이 되고 있는가?

## 한 줄 결론

생물학 AI의 승자는 “가장 멋진 모델 하나”를 가진 회사가 아닐 가능성이 크다. 오히려 **데이터를 만들고, 실험을 자동화하고, 모델 예측을 검증하고, 규제와 제약사 파이프라인까지 연결하는 플랫폼/자산 플레이어**가 더 유리해 보인다.

---

## 1. AlphaFold 이후: 구조 예측에서 상호작용 예측으로

생물학 AI의 대중적 전환점은 단연 AlphaFold였다. 단백질의 3차원 구조를 예측하는 문제는 오랫동안 생명과학의 난제였고, AlphaFold 2는 이 영역에서 “AI가 생물학의 핵심 병목 하나를 뚫을 수 있다”는 강력한 신호를 줬다.

그런데 시장이 지금 주목하는 지점은 단백질 구조 예측 그 자체를 넘어선다.

2024년에 공개된 **AlphaFold 3**는 단백질만이 아니라 DNA, RNA, 작은 분자 리간드, 이온, 번역 후 변형까지 포함한 생체분자 복합체의 구조와 상호작용 예측으로 범위를 넓혔다. DeepMind와 Isomorphic Labs는 일부 상호작용 범주에서 기존 방법 대비 50% 이상, 일부는 2배 수준의 정확도 개선을 주장했다.

이 변화의 의미는 크다.

신약개발에서 중요한 질문은 “단백질이 어떻게 생겼나?”에서 끝나지 않는다.

- 약물 후보가 표적 단백질에 잘 붙는가?
- 결합했을 때 기능이 실제로 바뀌는가?
- 다른 단백질이나 세포 경로에는 어떤 영향을 주는가?
- 독성이나 부작용 신호는 없는가?
- 세포 안에서는 같은 결과가 재현되는가?

즉, **구조(structure)에서 상호작용(interaction)과 기능(function)으로 질문이 이동**한다. AlphaFold 3와 Isomorphic Labs의 상업화 전략은 이 방향을 잘 보여준다. 모델은 논문 성과로 끝나는 게 아니라 실제 drug design 파트너십의 도구가 되어야 한다.

물론 여기에도 선이 있다. 구조와 결합 예측이 좋아졌다고 해서 임상 성공률이 자동으로 올라가는 것은 아니다. 신약개발의 실패는 분자 수준에서만 생기지 않는다. 약동학, 독성, 면역 반응, 환자군 이질성, 임상 설계, 규제 판단까지 긴 사슬이 있다. 그래서 AlphaFold 이후의 시장은 “단백질 구조 AI”보다 훨씬 넓은 **생물학 R&D 운영체제** 쪽으로 확장되고 있다.

---

## 2. NVIDIA가 보는 시장: BioNeMo에서 디지털 트윈까지

NVIDIA는 이 흐름을 단순히 GPU 수요 증가로만 보지 않는다. 더 큰 그림은 **바이오 R&D 인프라 장악**에 가깝다.

2026년 1월 JP Morgan Healthcare Conference에서 NVIDIA와 Eli Lilly는 AI co-innovation lab을 발표했다. 규모는 최대 10억 달러, 기간은 5년이다. 발표 자료의 키워드는 BioNeMo, NVIDIA Vera Rubin 아키텍처, robotics, physical AI, digital twins, clinical development, manufacturing, commercial operations까지 넓게 퍼져 있다.

여기서 중요한 문장은 이것이다.

> 과학자들이 실제 분자를 만들기 전에, 방대한 생물학적·화학적 공간을 in silico로 탐색할 수 있다.

in silico는 컴퓨터 시뮬레이션 안에서 실험한다는 뜻이다. 제약사는 원래 수많은 후보물질을 만들고, 테스트하고, 버리고, 다시 설계한다. 이 과정은 비싸고 느리다. NVIDIA의 전략은 이 루프의 앞단을 AI와 고성능 컴퓨팅으로 최대한 압축하는 것이다.

다만 NVIDIA가 노리는 것은 “신약 하나를 직접 만들겠다”보다는 더 인프라적이다.

- BioNeMo: 생물학·화학 모델 개발과 배포를 위한 플랫폼
- Vera Rubin: 차세대 AI 컴퓨팅 아키텍처
- Omniverse/digital twins: 실험실, 제조, 로봇 공정의 시뮬레이션 가능성
- robotics/physical AI: 실험 자동화와 물리적 연구 환경 연결
- 제약사 협업: 실제 파이프라인과 데이터에 접근

이 조합은 생물학을 “젖은 실험실(wet lab)”만의 영역에서 “컴퓨팅-실험-제조가 연결된 공장”으로 바꾸려는 시도다. 그래서 NVIDIA에게 바이오는 단순한 vertical market이 아니라, **AI 인프라가 물리 세계로 확장되는 대표 시장**이다.

---

## 3. Virtual Cell Challenge: 가능성과 한계를 동시에 보여준 실험

생물학 AI가 단백질을 넘어 세포로 가려면, 훨씬 어려운 문제가 등장한다. 세포는 단백질 하나보다 훨씬 복잡한 시스템이다. 유전자, 단백질, 대사 경로, 신호전달, 세포 상태, 주변 환경이 얽힌다.

Arc Institute가 2025년 6월 26일 시작한 **Virtual Cell Challenge 2025**는 이 난제를 정면으로 겨냥했다. 과제는 단일 유전자 perturbation 이후 세포 반응을 예측하는 것이었다.

여기서 perturbation은 세포에 어떤 변화를 일부러 주는 것을 말한다. 예를 들어 특정 유전자의 발현을 낮추거나 막은 뒤 세포가 어떻게 반응하는지 보는 것이다. 이번 챌린지에서는 **CRISPRi** perturbation이 사용됐다. CRISPRi는 유전자를 자르는 대신 특정 유전자의 발현을 억제하는 방식이다.

데이터는 약 30만 개의 H1 human embryonic stem cells, 300개 CRISPRi perturbations, 그리고 single-cell RNA-seq profiles였다. single-cell RNA-seq는 세포 하나하나에서 어떤 유전자가 얼마나 발현되는지 읽는 기술이다. 한 덩어리 조직의 평균값이 아니라, 세포별 상태를 보는 것이 핵심이다.

규모도 컸다.

- 114개국 참여
- 5,000명 이상 등록
- 1,200개 이상 팀 제출
- 300개 이상 final submissions
- 후원: NVIDIA, 10x Genomics, Ultima Genomics
- 1위: BioMap Research의 Team BM_xTVC, 모델 xTrimoSCPerturb

겉으로 보면 “가상 세포 경쟁”이라는 이름만으로도 굉장히 미래적이다. 하지만 더 중요한 것은 결과가 꽤 냉정했다는 점이다.

Arc의 자체 평가에 따르면, perturbation prediction 모델들은 모든 지표에서 아직 naive baseline을 일관되게 이기지 못했다. 여기서 naive baseline은 아주 단순한 기준 모델이다. 예를 들어 “복잡한 딥러닝 없이 평균적 반응을 활용하는 방식”에 가깝다.

그리고 우승 접근법도 순수 end-to-end 딥러닝만으로 해결하지 않았다. 딥러닝 모델과 고전적인 통계 특징을 결합한 하이브리드 접근이 중요했다.

이건 실패담이 아니다. 오히려 시장을 이해하는 데 더 좋은 신호다.

**세포 수준 예측은 가능성이 있지만, 아직 ‘스케일만 키우면 해결’되는 단계가 아니다.** 데이터 품질, 실험 설계, baseline, 통계적 구조, 생물학적 prior가 모두 필요하다. 생물학 AI가 LLM처럼 거대한 모델 하나로 밀어붙이면 되는 시장이 아니라는 점이 드러난 것이다.

---

## 4. Evo 2와 genomic foundation model: DNA를 읽고 쓰려는 시도

단백질과 세포 사이에는 유전체가 있다. 유전체는 생물학의 코드처럼 보이지만, 실제로는 프로그래밍 언어보다 훨씬 난해하다. 같은 DNA 서열도 세포 유형, 발달 단계, 환경에 따라 다르게 작동한다.

Arc Institute의 **Evo 2**는 이 영역의 대표적 시도다. 공개 정보 기준으로 Evo 2는 40B parameter 규모, 1 megabase context, 약 9조~9.3조 nucleotides로 학습된 genomic foundation model이다. 박테리아부터 진핵생물까지 all domains of life를 대상으로 DNA/RNA/protein 관련 예측과 설계 작업을 겨냥한다.

여기서 1 megabase context가 중요하다. 유전체에서 기능은 짧은 조각만 보고 알기 어려운 경우가 많다. 멀리 떨어진 조절 서열이 특정 유전자 발현에 영향을 줄 수 있고, 구조적 맥락이 중요하다. 긴 context를 보는 모델은 이런 장거리 의존성을 포착하려는 시도다.

NVIDIA NIM/BioNeMo 생태계에서도 Evo 2 접근이 제공된다는 점은 상징적이다. 생물학 foundation model이 연구실 데모를 넘어 **클라우드/API/엔터프라이즈 인프라 형태**로 유통되기 시작했다는 뜻이기 때문이다.

하지만 여기서도 과장은 금물이다. DNA를 모델이 생성할 수 있다는 것과, 그 DNA가 실제 생물학 시스템에서 안전하고 예측 가능한 기능을 한다는 것은 다르다. 유전체 모델은 설계 후보를 넓히고 좁히는 데 강력할 수 있지만, 결국 검증은 실험과 규제를 통과해야 한다.

---

## 5. 시장 전망: 숫자는 크지만, 정의에 따라 크게 달라진다

AI 신약개발 시장 전망은 출처마다 차이가 크다. 어떤 보고서는 2030년대 초 100억 달러 안팎을 말하고, 어떤 곳은 400억 달러 이상을 제시한다. 차이가 나는 이유는 단순하다. **무엇을 시장에 포함하느냐가 다르기 때문**이다.

“AI in drug discovery”만 볼 수도 있고, “drug discovery technologies” 전체를 볼 수도 있다. 전자는 AI 기반 타깃 발굴·분자 설계·스크리닝·예측 모델 중심이고, 후자는 자동화 장비, 분석 기술, 실험 플랫폼까지 포함하는 더 넓은 시장이다.

아래 표는 주요 출처별 전망을 같은 눈높이에서 정리한 것이다.

| 출처 | 시장 정의 | 기준/전망 수치 | CAGR | 해석 포인트 |
|---|---:|---:|---:|---|
| Precedence Research / BioSpace | AI in drug discovery | 2025년 69.3억 달러 → 2034년 165.2억~178.1억 달러 | 약 9.9~10.1% | 비교적 보수적인 성장률. AI 신약개발을 이미 상당한 규모의 시장으로 본다. |
| Mordor Intelligence | AI in drug discovery | 2025년 25.8억 달러, 2026년 32.5억 달러 → 2031년 102.9억 달러 | 25.94% | 시작 규모는 작게 보지만 성장률은 높게 잡는다. |
| Market Research Future | AI drug discovery | 2024년 9.3억 달러, 2025년 11.7억 달러 → 2035년 118.2억 달러 | 26% | 더 좁은 정의에서 출발해 장기 고성장을 가정한다. |
| Global Market Insights | AI in drug discovery | 2025년 31억 달러, 2026년 40억 달러 → 2035년 439억 달러 | 30.5% | 매우 공격적인 전망. AI 적용 범위 확대를 크게 본다. |
| MarketsandMarkets | drug discovery technologies | 2025년 305.8억 달러 → 2030년 515.1억 달러 | 11.0% | AI 전용이 아니라 더 넓은 drug discovery technologies 시장. 비교 시 주의 필요. |

표에서 봐야 할 것은 “어느 숫자가 맞느냐”만이 아니다. 더 중요한 것은 대부분의 기관이 **두 자릿수 성장률**을 제시한다는 점이다. 동시에 출발점과 시장 경계가 크게 다르다는 점도 봐야 한다.

즉, 이 시장은 커질 가능성이 높지만, 투자자와 기업 입장에서는 “AI 신약개발”이라는 단어만 보고 같은 시장이라고 착각하면 안 된다. 소프트웨어 라이선스 시장인지, 실험 자동화 장비 시장인지, 제약 파이프라인 자산 시장인지에 따라 매출 구조와 리스크가 완전히 달라진다.

---

## 6. 누가 돈을 벌까: 모델 회사보다 플랫폼·데이터·자산 플레이어

생물학 AI에서 돈을 버는 방식은 크게 네 갈래로 나눌 수 있다.

### 1) 빅테크와 인프라 기업

NVIDIA, Google DeepMind/Isomorphic Labs, 클라우드 기업들이 여기에 속한다. 이들은 모델 자체뿐 아니라 컴퓨팅, API, 워크플로우, 엔터프라이즈 통합을 판다. NVIDIA의 BioNeMo와 Lilly 협업은 이 흐름의 전형적인 사례다.

장점은 명확하다. 제약사와 바이오텍이 자체적으로 모든 AI 인프라를 만들기 어렵기 때문에, 표준 플랫폼이 될 수 있다. 단점은 실제 신약 가치의 큰 몫은 플랫폼 바깥, 즉 파이프라인 자산에서 발생할 수 있다는 점이다.

### 2) AI 바이오 스타트업

Xaira Therapeutics는 2024년 10억 달러 이상 committed capital로 출범했다. ARCH Venture Partners와 Foresite Labs가 공동 incubate했고, David Baker가 공동창업자로 참여했으며, Marc Tessier-Lavigne이 CEO를 맡았다.

이 사례가 중요한 이유는 AI 바이오 회사가 단순 SaaS보다 **자체 파이프라인/자산 플레이**로 가치를 만들려는 흐름을 보여주기 때문이다. 신약개발에서 가장 큰 upside는 결국 승인된 약물과 임상 자산에서 나온다. “모델 사용료”보다 “후보물질의 권리”가 훨씬 클 수 있다.

### 3) TechBio 플랫폼 기업

Recursion은 대표적인 TechBio 기업이다. Roche/Genentech, Sanofi, Bayer 등과 협업하고, NVIDIA와의 관계 및 BioHive-2 supercomputer를 강조한다. Recursion의 메시지는 명확하다. 대규모 실험 데이터, 자동화된 세포 이미지 분석, 머신러닝, 슈퍼컴퓨팅을 묶어 신약개발 엔진을 만들겠다는 것이다.

다만 균형 있게 봐야 한다. Recursion은 아직 시장에 출시된 약을 보유한 회사가 아니다. 후보물질은 임상과 개발 단계에 있다. 이 점은 AI 신약개발 전체의 리스크를 잘 보여준다. 플랫폼이 좋아 보여도, 최종 검증은 임상과 승인이다.

### 4) 실험 자동화·데이터 인프라 기업

Virtual Cell Challenge를 후원한 10x Genomics, Ultima Genomics 같은 회사들은 직접 “AI 모델 회사”는 아닐 수 있다. 하지만 AI 생물학에서 매우 중요한 위치를 차지한다. 왜냐하면 좋은 모델은 좋은 데이터 없이 나오기 어렵고, 생물학 데이터는 실험으로 만들어야 하기 때문이다.

앞으로 돈이 되는 병목은 “모델을 누가 더 크게 만들었나”보다 “검증 가능한 데이터를 누가 더 빠르고 싸게 만들 수 있나”가 될 수 있다.

---

## 7. 리스크: 모델보다 검증이 어렵다

생물학 AI 시장의 가장 큰 리스크는 모델 성능 자체만이 아니다. 오히려 더 큰 리스크는 모델이 낸 답을 실제 생물학과 의학 시스템에서 검증하는 과정에 있다.

### 임상 검증

전임상에서 좋아 보이는 후보가 임상에서 실패하는 일은 흔하다. AI가 후보 발굴 속도를 높여도, 사람 몸에서 안전하고 효과적이라는 증거는 따로 필요하다. 임상은 느리고 비싸며, 실패 비용이 크다.

### 데이터 품질

생물학 데이터는 실험 조건, 세포주, 장비, 배치 효과, 샘플 처리 방식에 민감하다. 데이터가 크다고 항상 좋은 것은 아니다. 모델이 배치 효과나 실험실 특이성을 학습하면, 다른 환경에서 성능이 무너질 수 있다.

### 재현성

AI 모델이 예측한 결과가 다른 실험실에서도 반복되는가? 같은 perturbation이 다른 세포 유형에서도 비슷하게 작동하는가? 생물학에서는 재현성이 시장 가치와 규제 신뢰의 핵심이다.

### 규제 수용성

FDA는 NAMs(New Approach Methodologies)를 통해 동물실험을 reduce/replace/refine하려는 방향을 분명히 하고 있다. NAMs에는 organoids, organ-on-chip, human cell-based assays, computational models 등이 포함된다.

하지만 이것은 “동물실험이 곧 사라진다”는 뜻이 아니다. 더 정확히는 **전임상 안전성·효능 근거의 일부를 human-relevant data로 보완하거나 대체하는 방향**이다. AI 모델과 계산 생물학은 이 흐름의 일부가 될 수 있지만, 규제기관이 받아들일 수 있는 검증 체계가 필요하다.

### 긴 개발 사이클

소프트웨어 시장에서는 제품을 출시하고 빠르게 개선할 수 있다. 신약개발은 다르다. 타깃 발굴부터 승인까지 10년 이상 걸리는 경우도 많다. AI 도입 효과가 실제 매출로 확인되기까지 시간이 오래 걸린다.

---

## 8. 타임라인: 생물학 AI가 인프라 시장이 되기까지

| 시점 | 사건 | 의미 |
|---|---|---|
| 2024 | AlphaFold 3 공개 | 단백질 구조 예측에서 생체분자 복합체 상호작용 예측으로 확장 |
| 2024 | Xaira Therapeutics 출범, 10억 달러 이상 자본 | AI 바이오가 SaaS보다 자체 파이프라인/자산 플레이로 가치를 만들려는 흐름 |
| 2025-06 | Arc Virtual Cell Challenge 출범 | 단일 유전자 perturbation 이후 세포 반응 예측을 공개 경쟁 형태로 검증 |
| 2025 | Evo 2 preprint 및 genomic foundation model 확산 | DNA/RNA/protein을 아우르는 foundation model 생태계 확대 |
| 2025 | Recursion 등 TechBio 기업의 대형 제약 협업 지속 | AI+자동화 실험+제약 파이프라인 결합 모델 확산 |
| 2025-12 | Virtual Cell Challenge 결과 발표, BioMap Research 1위 | 가능성과 함께 한계도 확인. 순수 딥러닝보다 하이브리드 접근 필요 |
| 2026-01 | NVIDIA-Lilly AI co-innovation lab 발표, 최대 10억 달러/5년 | 바이오 R&D가 AI 컴퓨팅·로보틱스·디지털 트윈 인프라 시장으로 이동 |
| 2026 | FDA NAMs draft guidance 등 제도화 흐름 강화 | 동물실험 대체/보완 방법론이 규제 논의 중심으로 진입 |

---

## 결론: 신약을 클릭 한 번에 만드는 기술이 아니다

생물학 AI를 둘러싼 마케팅은 쉽게 과장된다. “AI가 신약개발을 끝낸다”, “동물실험은 사라진다”, “가상 세포가 모든 실험을 대체한다” 같은 문장은 매력적이지만, 지금의 현실을 정확히 설명하지 못한다.

더 정확한 그림은 이렇다.

**AI는 생물학을 더 공학적으로 다루게 만드는 인프라 변화다.**

AlphaFold 3는 생체분자 상호작용 예측의 범위를 넓혔다. Evo 2 같은 genomic foundation model은 DNA와 단백질 설계의 탐색 공간을 넓힌다. Arc Virtual Cell Challenge는 세포 수준 예측의 가능성과 한계를 동시에 보여줬다. NVIDIA와 Lilly의 협업은 제약 R&D가 컴퓨팅, 로보틱스, 디지털 트윈, 제조까지 연결된 AI 인프라 시장이 되고 있음을 보여준다.

하지만 병목은 여전히 남아 있다. 임상 검증, 데이터 품질, 재현성, 규제 수용성, 긴 개발 사이클이다. 그래서 생물학 AI의 다음 격전지는 단순히 “모델이 더 크냐”가 아니다.

다음 질문이 더 중요하다.

- 누가 더 좋은 생물학 데이터를 만들 수 있는가?
- 누가 실험 자동화와 모델 학습을 하나의 루프로 묶을 수 있는가?
- 누가 제약사 파이프라인과 규제 검증까지 연결할 수 있는가?
- 누가 예측을 실제 후보물질과 임상 가치로 바꿀 수 있는가?

결국 생물학 AI의 승자는 모델 하나가 아니라, **데이터 생성 능력, 실험 자동화, 검증 체계, 제약 자산을 함께 가진 플레이어**일 가능성이 크다.

그리고 그 점에서 생물학은 AI의 다음 “앱 시장”이라기보다, AI 인프라가 가장 깊게 들어갈 산업 중 하나에 가깝다.

---

## 참고자료

- Arc Institute, [Virtual Cell Challenge 2025](https://arcinstitute.org/news/virtual-cell-challenge-2025)
- Arc Institute, [Virtual Cell Challenge 2025 Wrap-Up](https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up)
- Eli Lilly, [NVIDIA and Lilly Announce Co-Innovation AI Lab to Reinvent Drug Discovery in the Age of AI](https://lilly.gcs-web.com/news-releases/news-release-details/nvidia-and-lilly-announce-co-innovation-ai-lab-reinvent-drug)
- NVIDIA Investor Relations, [NVIDIA and Lilly Announce Co-Innovation AI Lab](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-and-Lilly-Announce-Co-Innovation-AI-Lab-to-Reinvent-Drug-Discovery-in-the-Age-of-AI/default.aspx)
- Isomorphic Labs, [Rational drug design with AlphaFold 3](https://www.isomorphiclabs.com/articles/rational-drug-design-with-alphafold-3)
- Isomorphic Labs, [AlphaFold 3 predicts the structure and interactions of all of life’s molecules](https://www.isomorphiclabs.com/articles/alphafold-3-predicts-the-structure-and-interactions-of-all-of-lifes-molecules)
- Arc Institute, [Evo](https://arcinstitute.org/tools/evo)
- NVIDIA Build, [Evo2 40B Model Card](https://build.nvidia.com/arc/evo2-40b/modelcard)
- bioRxiv, [Evo 2 preprint](https://www.biorxiv.org/content/10.1101/2025.02.18.638918v1)
- Business Wire, [Xaira Therapeutics Launches](https://www.businesswire.com/news/home/20240423707240/en/Xaira-Therapeutics-Launches-to-Deliver-Transformative-Medicines-by-Advancing-and-Harnessing-AI-for-Drug-Discovery-and-Development)
- Fierce Biotech, [Xaira rises with $1B funding](https://www.fiercebiotech.com/biotech/new-ai-drug-discovery-powerhouse-xaira-rises-1b-funding)
- Recursion, [Partners](https://www.recursion.com/partners)
- Recursion, [Company site](https://www.recursion.com)
- Pharmaceutical Technology, [Big tech meets biotech: Recursion and the AI gold rush in pharma](https://www.pharmaceutical-technology.com/analyst-comment/big-tech-meets-biotech-recursion-ai-gold-rush-pharma)
- FDA, [New Approach Methodologies, NAMs](https://www.fda.gov/science-research/science-and-research-special-topics/new-approach-methodologies-nams)
- FDA, [Draft guidance on alternatives to animal testing in drug development](https://www.fda.gov/news-events/press-announcements/fda-releases-draft-guidance-alternatives-animal-testing-drug-development)
- BioSpace, [AI in Drug Discovery Market Size to Worth USD 16.52 Bn by 2034](https://www.biospace.com/press-releases/ai-in-drug-discovery-market-size-to-worth-usd-16-52-bn-by-2034)
- Precedence Research, [Artificial Intelligence in Drug Discovery Market](https://www.precedenceresearch.com/artificial-intelligence-in-drug-discovery-market)
- Mordor Intelligence, [Artificial Intelligence in Drug Discovery Market](https://www.mordorintelligence.com/industry-reports/artificial-intelligence-in-drug-discovery-market)
- Market Research Future, [AI Drug Discovery Market](https://www.marketresearchfuture.com/reports/ai-drug-discovery-market-9393)
- Global Market Insights, [AI in Drug Discovery Market](https://www.gminsights.com/industry-analysis/ai-in-drug-discovery-market)
- MarketsandMarkets, [Drug Discovery Technologies Market](https://www.marketsandmarkets.com/Market-Reports/drug-discovery-technologies-market-35597436.html)
