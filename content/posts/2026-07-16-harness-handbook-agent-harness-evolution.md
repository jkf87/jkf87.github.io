---
title: "에이전트 하네스는 어디를 고쳐야 할까: Harness Handbook이 제안한 행동 중심 지도"
date: 2026-07-18T01:20:00+09:00
draft: false
summary: "Harness Handbook 논문은 에이전트 하네스를 파일·함수 구조가 아니라 행동 단위로 읽고 수정할 수 있게 만드는 방법을 제안한다. Codex와 Terminus-2 두 오픈소스 하네스에서 평가했을 때, Handbook-Assisted planning은 행동 위치 찾기와 편집 계획 품질을 높이고 플래너 토큰 사용량을 줄였다."
tags: ["AI Agent", "Agent Harness", "Behavior Localization", "Code Understanding", "Tencent Hunyuan", "Loop Engineering"]
categories: ["AI Agent", "Software Engineering"]
source_url: "https://arxiv.org/abs/2607.13285"
project_url: "https://ruhan-wang.github.io/Harness-Handbook/"
authors: ["Ruhan Wang", "Yucheng Shi", "Zongxia Li", "Zhongzhi Li", "Yue Yu", "Junyao Yang", "Kishan Panaganti", "Haitao Mi", "Dongruo Zhou", "Leoweiliang"]
affiliations: ["Tencent HY LLM Frontier", "Indiana University", "University of Maryland", "University of Georgia", "National University of Singapore"]
---

에이전트 하네스를 고쳐본 사람은 안다. 문제는 코드를 못 짜는 것이 아니라, **어디를 고쳐야 하는지 찾는 것**에서 자주 시작된다. “파일 삭제 전에 사용자 확인을 넣어줘” 같은 요청은 단순해 보이지만, 실제 구현은 프롬프트 생성, 도구 래퍼, 권한 정책, 상태 관리, 실행 샌드박스, 예외 처리 경로에 흩어져 있을 수 있다.

`Harness Handbook: Making Evolving Agent Harnesses Readable, Navigable, and Editable` 논문은 이 병목을 **behavior localization**, 즉 “수정하려는 행동이 구현된 모든 코드 위치를 찾는 문제”로 정의한다. 저자들은 에이전트 하네스를 파일·함수 목록이 아니라 행동 중심 지도처럼 재구성하면, 사람 개발자와 코딩 에이전트 모두가 수정 계획을 더 잘 세울 수 있다고 주장한다.

이 글은 논문의 핵심을 객관적으로 정리하되, 에이전트 자동화와 하네스 엔지니어링 관점에서 무엇을 읽어야 하는지 함께 짚어본다.

![Harness Handbook 표현 개요 - L1 시스템 개요부터 L3 소스 수준 세부 정보까지 3단계 계층 구조](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-1-p4.png)

*그림 1: Harness Handbook의 표현 구조. L1 시스템 개요, L2 컴포넌트 개요, L3 소스 수준 세부 정보로 내려가며 행동과 구현 위치를 연결한다.*

## 이 논문이 보는 병목은 무엇인가

논문은 현대 AI 에이전트의 성능이 foundation model만으로 결정되지 않는다고 본다. 실제 에이전트 시스템에는 모델 바깥의 하네스가 있다. 하네스는 프롬프트를 만들고, 상태를 관리하고, 도구를 호출하고, 실행 순서를 조정한다. 같은 모델을 써도 하네스 설계에 따라 제품 동작이 달라지는 이유다.

문제는 하네스가 계속 바뀐다는 점이다. 모델 API가 바뀌고, 실행 환경이 바뀌고, 제품 요구사항이 바뀌면 하네스도 수정해야 한다. 그런데 수정 요청은 보통 “무엇을 해야 하는가”로 들어온다. 반면 저장소는 파일, 함수, 모듈 단위로 조직되어 있다. 이 둘 사이의 매핑은 자동으로 주어지지 않는다.

논문이 말하는 **behavior localization**은 바로 이 간극을 가리킨다. 수정하려는 행동이 어느 파일, 어느 함수, 어느 상태 전이에 걸쳐 구현되어 있는지 찾아야 한다. 코드 검색, 저장소 인덱스, 긴 컨텍스트 모델은 이 과정을 도울 수 있지만, 저자들은 여전히 행동과 구현 사이의 연결을 개발자나 코딩 에이전트가 직접 복원해야 한다고 지적한다.

## Harness Handbook은 코드를 어떻게 다시 조직하나

Harness Handbook의 핵심은 구현 지식을 파일 구조가 아니라 **행동 구조**로 재배열하는 것이다. 표현은 크게 세 단계로 구성된다.

1. **L1 — 시스템 개요**  
   전체 아키텍처, 실행 모델, 주요 단계, 전역 데이터 흐름을 요약한다. 처음 읽는 사람이나 에이전트가 “이 하네스는 전체적으로 어떻게 움직이는가”를 파악하는 층이다.

2. **L2 — 컴포넌트/단계 개요**  
   특정 실행 단계나 컴포넌트의 책임, 입력, 출력, 의존성, 지역 상태를 설명한다. 예를 들어 도구 호출, 권한 확인, 상태 업데이트처럼 행동 단위에 가까운 구조를 보여준다.

3. **L3 — 소스 연결 세부 정보**  
   실제 구현 위치와 연결된 세부 항목이다. 어떤 함수나 파일이 해당 행동에 관여하는지, 어느 라인이 증거인지, 현재 저장소에서 그 위치가 여전히 유효한지 검증한다.

여기서 중요한 원칙은 두 가지다. 첫째, **progressive disclosure**다. 처음부터 전체 코드를 다 펼치지 않고 L1 → L2 → L3로 필요한 만큼만 내려간다. 둘째, **behavior–implementation alignment**다. Handbook의 설명은 현재 소스 코드와 연결되어야 하며, 더 이상 유효하지 않은 locator는 localization에서 제외된다.

## 자동 생성은 어떻게 하나

저자들은 Harness Handbook을 수동 문서가 아니라 자동 생성되는 표현으로 설계한다. 생성 파이프라인은 세 단계다.

![Harness Handbook 생성 파이프라인 - 정적 분석, 행동 조직, 계층적 합성](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-2-p5.png)

*그림 2: Harness Handbook 생성 파이프라인. 정적 분석으로 소스 사실을 뽑고, 행동 조직 단계를 거쳐 L1-L3 문서와 상태 레지스터 뷰를 만든다.*

**1단계는 정적 사실 추출이다.** 언어별 어댑터가 저장소를 파싱해 함수, 외부 경계, 소스 위치, 시그니처, 호출 edge를 추출한다. 이 단계는 LLM 호출 없이 결정론적으로 수행된다. 확인되지 않은 호출은 임의로 추정하지 않고 unresolved로 남긴다.

**2단계는 행동 조직이다.** 소스 단위를 실행 단계 골격에 배치한다. 논문은 두 가지 leaf mode를 둔다. 신뢰할 수 있는 실행 단계 skeleton이 있으면 `function-as-leaf`를 사용하고, 그렇지 않거나 저장소 규모가 크면 `file-as-leaf`로 단계 구조를 추론한다.

**3단계는 계층적 합성과 패키징이다.** L1-L3 문서 트리와 cross-stage state register view를 만들고, 각 L3 항목을 소스 위치와 연결한다. 이 연결은 이후 수정과 재동기화의 기준이 된다.

## 코딩 에이전트는 이 지도를 어떻게 쓰나

논문은 Harness Handbook을 단순 문서가 아니라 수정 워크플로우에 붙인다. 이름은 **Behavior-Guided Progressive Disclosure(BGPD)**다.

요청이 들어오면 코딩 에이전트는 먼저 L1 수준에서 관련 행동 영역을 찾고, L2에서 관련 컴포넌트를 좁힌 뒤, L3에서 실제 소스 위치를 확인한다. 그런 다음 후보 위치가 현재 저장소에 존재하는지 검증하고, 그 증거를 기반으로 편집 계획을 만든다. 실행기가 실제 diff를 만들고 나면, 변경된 저장소에 맞춰 Handbook도 다시 동기화한다.

이 설계에서 논문이 강조하는 점은 “코드를 더 많이 보여주는 것”이 아니다. 오히려 필요한 행동 경로를 먼저 찾고, 그 경로와 관련된 구현만 단계적으로 공개하는 쪽이다. 이는 긴 컨텍스트를 무작정 쓰는 방식과 구분된다.

## 실험은 어떻게 했나

평가는 두 개의 오픈소스 에이전트 하네스에서 수행됐다. 하나는 **Codex**, 다른 하나는 **Terminus-2**다. Codex는 저장소 규모 때문에 `file-as-leaf` 모드로, Terminus-2는 신뢰할 수 있는 seed skeleton이 있어 `function-as-leaf` 모드로 평가했다.

각 하네스에는 30개의 행동 기반 수정 요청이 주어졌다. 요청은 세 유형으로 나뉜다.

- **Query(Q)**: 기존 행동을 바꾸지만 목표 위치를 알려주지 않는 요청
- **Cross-file(CF)**: 여러 파일이나 모듈을 가로지르는 기능 추가 요청
- **Search-Hostile(SH)**: 키워드 검색만으로 관련 구현을 찾기 어려운 요청

계획 생성에는 DeepSeek-V4-Pro 기반의 read-only planner가 사용됐고, 계획 품질은 GPT-5.5, Opus 4.8, DeepSeek-V4-Pro 세 모델이 독립적으로 평가했다. 평가 차원은 localization, scope control, reasoning이다. localization에는 가장 큰 가중치가 부여됐다.

![계획 품질 및 플래너 토큰 사용량 비교](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-3-p8.png)

*그림 3: Codex와 Terminus-2에서의 계획 품질 win rate와 planner token 사용량 비교. Handbook-Assisted arm은 두 하네스 모두에서 더 높은 win rate와 더 낮은 평균 planner token 사용량을 보였다.*

## 결과는 어느 정도였나

논문이 보고한 주요 결과는 세 가지다.

첫째, **계획 품질 win rate가 개선됐다.** Handbook-Assisted arm은 Codex에서 38.3% 대 28.3%, Terminus-2에서 45.6% 대 26.7%로 baseline보다 높은 전체 win rate를 보였다. 세 judge 모두에서 개선 방향은 같았다.

둘째, **planner token 사용량은 줄었다.** Codex에서는 요청당 평균 0.102M tokens에서 0.089M tokens로 줄어 약 12.7% 감소했고, Terminus-2에서는 0.058M에서 0.053M으로 줄어 약 8.6% 감소했다. 논문은 이 결과를 더 큰 토큰 예산이 아니라 구조화된 탐색의 효과로 해석한다.

셋째, **localization metric이 전반적으로 개선됐다.** Table 1에서 Handbook-Assisted arm은 두 하네스, 두 reference model(Opus 4.8, GPT-5.5), 두 granularity(file, symbol)에 걸친 Recall, Precision, F1 비교 24개 모두에서 baseline보다 높은 값을 보였다. F1 개선 폭은 5.0~18.8 points였다.

![현지화 메트릭 표](/images/2026-07-16-harness-handbook-agent-harness-evolution/table-1-p9.png)

*표 1: reference plan 대비 localization metric. Codex와 Terminus-2 모두에서 Handbook-Assisted arm의 Recall, Precision, F1이 전반적으로 높게 나타났다.*

또 하나 눈에 띄는 결과는 complete miss의 감소다. 논문에서 Wrong은 reference plan과 zero overlap인 경우를 뜻한다. Handbook guidance는 Wrong 비율을 증가시키지 않았고, 일부 조건에서는 최대 25.9 points까지 낮췄다. 이는 이미 맞춘 위치를 조금 더 잘 맞춘 것뿐 아니라, 아예 엉뚱한 위치로 가는 실패도 줄였다는 뜻이다.

## 어디에서 효과가 컸나

저자들은 요청 유형과 난이도별로도 결과를 나눠본다. 여섯 개 harness-by-type 비교 모두 Handbook-Assisted arm이 우세했고, 개선 폭은 16.3~33.3 percentage points였다. Codex에서는 Query 요청에서, Terminus-2에서는 Search-Hostile 요청에서 가장 큰 개선이 보고됐다.

![수정 요청 유형별 승률](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-5-p9.png)

*그림 5: 수정 요청 유형과 localization difficulty별 win rate. Query, Cross-file, Search-Hostile 요청 전반에서 Handbook-Assisted arm이 baseline보다 높은 결과를 보였다.*

이 대목은 실무적으로 중요하다. 키워드 검색으로 쉽게 잡히는 수정이라면 기존 도구만으로도 충분할 수 있다. 하지만 행동이 여러 모듈에 흩어져 있거나, 드물게 실행되는 경로에 숨어 있거나, 상태 전이를 따라가야 하는 경우라면 행동 중심 표현의 이점이 커질 수 있다. 논문 결과는 적어도 이 실험 설정에서 그런 경향을 보여준다.

## 이 논문을 읽을 때 조심해야 할 점

이 연구는 하네스 엔지니어링에서 중요한 문제를 잘 짚지만, 몇 가지 해석상의 주의가 필요하다.

첫째, 평가는 실제 end-to-end 코드 수정 성공률이 아니라 **localization과 edit planning 품질**에 초점을 둔다. 논문은 편집을 생성하는 능력보다 “어디를 편집해야 하는지 결정하는 능력”을 다룬다. 따라서 결과를 곧바로 “전체 코딩 에이전트 성공률이 이만큼 오른다”로 읽으면 과하다.

둘째, judge에는 LLM이 사용됐다. 세 모델을 독립 judge로 두고 reference plan과도 비교했지만, 여전히 평가 방식은 모델 기반 판단을 포함한다. 논문의 수치는 이 평가 설계 안에서의 결과로 보는 것이 안전하다.

셋째, 대상 하네스는 Codex와 Terminus-2 두 개다. 다양한 request type과 difficulty를 구성했지만, 모든 에이전트 프레임워크나 모든 조직의 코드베이스에 그대로 일반화된다고 보기는 어렵다.

## 그래도 이 논문이 흥미로운 이유

이 논문은 “더 긴 컨텍스트를 넣으면 된다”는 방향과 조금 다르게 문제를 본다. 저자들의 주장은 하네스 수정의 핵심 병목 중 하나가 컨텍스트 크기만이 아니라 **행동과 구현 사이의 지도 부재**라는 것이다.

에이전트 시스템이 커질수록 실패나 수정 요청은 보통 행동 언어로 들어온다. “승인 없이 이 도구를 부르지 말라”, “검색 결과가 부족하면 다시 탐색하라”, “이 상태에서는 사용자에게 물어보라” 같은 식이다. 하지만 저장소는 여전히 파일과 함수로 구성되어 있다. Harness Handbook은 이 둘 사이에 행동 중심 중간 표현을 넣자는 제안이다.

저는 이 지점이 하네스, 루프엔지니어링, 자동화 시스템을 다루는 사람에게 특히 실용적이라고 봅니다. 다만 이 판단은 논문 결과를 넘어선 개인적 해석이다. 논문 자체가 보여준 것은, 두 오픈소스 하네스의 planning 실험에서 행동 중심 표현이 localization과 계획 품질을 개선하고 토큰 사용량을 낮췄다는 점이다.

## 당장 가져갈 수 있는 작은 체크리스트

이 논문을 읽고 바로 대규모 Handbook 생성기를 만들 필요는 없다. 작은 팀이나 개인 프로젝트라면 다음 정도부터 시작할 수 있다.

1. 자주 고치는 에이전트 행동 5개를 적는다.
2. 각 행동이 걸치는 파일, 함수, 상태, 도구 호출을 표로 정리한다.
3. “이 행동을 바꾸려면 어디를 봐야 하는가”를 코드 위치와 함께 남긴다.
4. 수정 후 그 표가 여전히 맞는지 확인한다.
5. 코딩 에이전트에게 작업을 맡길 때 파일명이 아니라 행동명으로 먼저 접근하게 한다.

이 정도만 해도 하네스를 “코드 덩어리”가 아니라 “행동들의 지도”로 보기 시작할 수 있다. 논문이 제안한 Harness Handbook은 그 작업을 더 체계적이고 자동화된 형태로 밀어붙인 사례에 가깝다.

## 더 실습해보고 싶은 분들께

이 글에서 다룬 에이전트 하네스, 자동화, 루프 설계를 직접 실습해보고 싶은 분들을 위해 제가 정리한 자료도 함께 남깁니다. 오픈클로를 일상 자동화 도구로 써보고 싶다면 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』를, 에이전트가 반복적으로 실행·검증·개선되는 구조를 더 깊게 보고 싶다면 AIFrenz의 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 강의를 참고하시면 됩니다.

## 원문과 자료

- 논문: [Harness Handbook: Making Evolving Agent Harnesses Readable, Navigable, and Editable](https://arxiv.org/abs/2607.13285)
- 프로젝트 페이지: [ruhan-wang.github.io/Harness-Handbook](https://ruhan-wang.github.io/Harness-Handbook/)
- PDF: [arXiv PDF](https://arxiv.org/pdf/2607.13285)
