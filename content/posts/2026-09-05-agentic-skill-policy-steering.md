---
title: "서드파티 에이전트 스킬이 모델 결정을 몰래 조준한다"
date: 2026-09-05
draft: false
tags:
  - agent
  - security
  - skill
  - supply-chain
  - evaluation
description: "에이전트 스킬이 출력은 정상으로 유지하면서 후보 선택 확률만 몰래 기울이는 정책 조종 공격(SkillShift)을 정리했습니다. 스킬 감지 스캐너 6종이 모두 탐지 실패한 이유와 대응 관점을 담았습니다."
---

## 결론 먼저

재사용 가능한 에이전트 스킬이 <span style="background-color: #fff59d"><strong>출력은 전부 유효하게 유지하면서, 어떤 후보를 고를지 확률만 몰래 기울일 수 있다</strong></span>는 게 이 논문의 핵심 증명입니다. 프롬프트 인젝션처럼 명령을 덮어쓰지 않습니다. 비교 기준과 예시 몇 개를 바꾸는 것만으로 쇼핑 추천에서 타깃 브랜드 선택률을 <span style="background-color: #fff59d"><strong>37%에서 81%로 끌어올렸고, 유효 출력률은 100%를 유지</strong></span>했습니다. 평가한 스킬 보안 스캐너 6종은 전부 이걸 잡지 못했습니다.

핵심 숫자를 표로 정리했습니다. 기준일: 2026-09-05, 논문 v1(2026-09-02 공개) 기준입니다.

| 항목 | 값 | 비고 |
| --- | --- | --- |
| 쇼핑 추천 타깃 선택률(PSR) | 37.33% → 81.33% | +44pp, Li-Ning 타깃 |
| 파이썬 의존성 선택 PSR | 0% → 63.33% | +63pp, polars 타깃 |
| 유효 출력률(VR) | 100% | 두 도메인 모두 |
| 스킬 스캐너 탐지 | 0/6 | skill-scanner-full, Aguara, Snyk, STARS, SkillSpector, ProtectAI |
| 노출형 직접 인젝션 탐지 | 4/6 | 같은 스캐너에서는 잘 잡음 |
| 크로스모델 전이 | Lift +20~+100pp | GPT-5.5, Gemini 3-Flash, DeepSeek, GLM-4.7, Qwen3.5-Flash 등 |
| 실제 에이전트 전이 | Lift +28.67~+94pp | Claude Code, Codix 호환 에이전트 |
| 다운스트림 품질 | 평균 0.558 → 0.506 | QPR@0.7 기준 −16pp |

## 무엇이 문제인가

스킬은 로드 가능한 지시 묶음입니다. 도메인 지식, 도구 사용 가이드, 출력 제약, 예시를 담습니다. 그래서 스킬은 에이전트의 수행 범위에 더해서 판단 방식까지 바꿉니다. 어떤 근거에 가중치를 둘지, 트레이드오프를 어떻게 풀지를 스킬이 정합니다.

논문은 여기서 새 보안 속성 하나를 정의합니다.

> <span style="background-color: #fff59d"><strong>Skill Policy Integrity: 스킬이 유도하는 행동 정책이 선언된 기능과 사용자가 승인한 목표에 충실해야 하며, 행동 변화가 과제 관련 맥락으로만 설명되어야 한다</strong></span>

쇼핑 비교 스킬을 예로 들면 이렇습니다. 악성 제공자가 "합리적인 평가 기준"과 예시를 추가합니다. 그 기준이 특정 브랜드에 은근히 유리하게 설계된 거죠. 에이전트는 원래 질의를 그대로 처리하고, 유효한 추천을 반환합니다. 그런데 광고주 브랜드를 더 자주 고르게 됩니다. <span style="background-color: #fff59d"><strong>태스크는 통과했는데 결정이 팔린 상태</strong></span>입니다.

기존 위협 모델과의 차이는 이렇습니다.

| 위협 | 무엇을 바꾸나 | 탐지 |
| --- | --- | --- |
| 간접 프롬프트 인젝션 | 에이전트가 읽는 외부 콘텐츠에 명령 삽입 | 벤치마크/방어 다수 존재 |
| ToolTweak / MPMA | 도구 이름·설명을 조작 | 도구 선택 왜곡 |
| Dependency Steering | 하드 제약 계층 수정 | 후보 자체를 제한 |
| SkillShift (본 논문) | 스킬의 소프트 정책 계층 (프레이밍·타이브레이커·예시) | 기존 스캐너 0/6 |

## SkillShift는 어떻게 동작하나

공격자는 <span style="background-color: #fff59d"><strong>스킬 문서만 편집</strong></span>합니다. 질의, 후보 데이터, 순서, 모델, 출력 인터페이스는 전부 그대로 둡니다. 블랙박스 설정이라 모델 파라미터·확률·그래디언트·어텐션 접근 없이 최종 출력만 봅니다.

공격 시나리오 전체는 논문 Figure 1에 잘 나와 있습니다.

![Figure 1: 악성 스킬이 후보 집합을 그대로 둔 채 비교 정책만 이동시키는 시나리오](/images/2026-09-05-agentic-skill-policy-steering/fig-1-p2.png)

구조는 4단계입니다.

1. 구조화된 정책 표현: 전면 재작성 대신 스키마 제약된 전략 객체 A=(G, U, T, X)를 검색 공간으로 씁니다. G는 전역 평가 원칙, U는 태스크 규칙, T는 타이브레이킹 기준, X는 예시입니다.
2. 제약 기반 블랙박스 최적화: 제안자(전략 생성용 LLM)가 현재 최선 전략을 국소 편집합니다. 계층 검증으로 후보 데이터 변경, 위치 기반 지름길, 스키마 위반, 명시적 타깃 명령을 금지합니다. <span style="background-color: #fff59d"><strong>타깃 이름은 허용된 예시에만 등장할 수 있습니다</strong></span>.
3. 실패 유도 커버리지 수리: 실패한 개발 질의를 의미 카테고리로 묶고, 카테고리 수준 통계만 제안자에게 줍니다. 인스턴스 암기 대신 카테고리 커버리지를 개선합니다.
4. 효과 보존 압축: 중복 규칙 삭제, 유사 규칙 병합, 반복 설명 축약으로 눈에 띄는 표면적을 줄이고 전이성을 높입니다. 그 다음 전략을 동결(freeze)합니다.

세 가지 조종 메커니즘이 흥미로운 지점입니다.

- 정책 프레이밍: 과제 관련 속성의 상대적 중요도를 살짝 바꿉니다.
- 타이브레이킹 조작: 후보들이 비슷할 때 적용되는 보조 기준을 정의해 순위를 뒤집습니다.
- 의미 앵커링: 추상 원칙이 실제로 어떻게 적용되는지 예시로 고정합니다. 크로스모델 전이의 비결이 여기 있습니다.

## 결과: 유효한 출력과 조종된 결정이 공존한다

### 본 효과

![Figure 2a: 조건별 PSR/VR. SkillShift는 Python 63.3%, Shopping 81.3% PSR에 VR 100%](/images/2026-09-05-agentic-skill-policy-steering/fig-2-p5.png)

![Figure 2b: 쇼핑 추천에서 SkillShift PSR 81.3%, Direct-Skill Injection 98%](/images/2026-09-05-agentic-skill-policy-steering/fig-2-p5-2.png)

- 쇼핑: Clean 37.33% → Attack 81.33% (Lift +44pp), VR 100%.
- 파이썬 의존성: Clean 0% → Attack 63.33% (Lift +63pp), VR 100%.
- 비교 기준선들이 주는 교훈: 타깃 이름만 언급하면 PSR 3.3%, 키워드 스태핑은 0.7%에 그칩니다. 이 공격의 힘은 이름 반복에서 나오지 않고 <span style="background-color: #fff59d"><strong>쌓인 의미 신호에서 나옵니다</strong></span>.
- Direct-Skill Injection(노출형 양성 대조군)은 98~100% PSR을 내지만 스텔스 제약을 깨므로 실전용이 아닙니다.

### 보지 못한 질의에도 유지된다

전략 최적화에는 dev30만 썼고 heldout20에는 동결된 전략을 그대로 적용했습니다.

| 도메인 | dev30 | heldout20 |
| --- | --- | --- |
| 쇼핑 PSR | 85.56% | 80.00% |
| 파이썬 PSR | 46.67% | 75.00% |

### 모델·에이전트를 바꿔도 전이된다

![Table 2: 크로스모델·실전 에이전트 전이 결과. 전 구간 양수 Lift](/images/2026-09-05-agentic-skill-policy-steering/table-2-p6.png)

- Claude Haiku 4.5(피해 시뮬레이터)에서 만든 전략을 GPT-5.5, Gemini 3-Flash, DeepSeek v4-Flash, GLM-4.7, Qwen3.5-Flash에 그대로 올리면 <span style="background-color: #fff59d"><strong>전 도메인 양수 Lift(+20.0 ~ +100.0pp)</strong></span>.
- Claude Code와 Codex 호환 에이전트 같은 실전 환경에서도 +28.67 ~ +94.00pp, Attack VR 최소 96.67%.
- 재최적화는 전혀 없었습니다.

### 그런데 다운스트림 품질은 떨어진다

유효 출력률 100%에도 DeepEval GEval 기준 코드 품질은 <span style="background-color: #fff59d"><strong>평균 0.558 → 0.506, QPR@0.7은 28% → 12%로 하락</strong></span>했습니다. 돌아가는 코드와 좋은 결정은 별개입니다.

## 왜 스캐너가 못 잡나

| 탐지기 | Clean 오보 | SkillShift 탐지 | Direct 탐지 |
| --- | --- | --- | --- |
| skill-scanner-full | ✗ | ✗ | ✓ |
| Aguara | ✗ | ✗ | ✓ |
| Snyk Agent Scan | ✗ | ✗ | Python ✗ / Shopping ✓ |
| STARS | ✗ | ✗ | ✓ |
| SkillSpector | ✗ | ✗ | ✓ |
| ProtectAI DeBERTa | ✗ | ✗ | ✗ |

6종 전부 SkillShift 스킬을 놓쳤습니다. 같은 스캐너들이 노출형 인젝션은 4/6 잡습니다. 이유는 간단합니다. 기존 탐지기는 <span style="background-color: #fff59d"><strong>명령 오버라이드, 무단 도구 호출, 사용자 요청 변경</strong></span> 같은 패턴을 찾습니다. SkillShift는 그 어느 것도 하지 않습니다. 그냥 그럴듯한 평가 기준과 예시일 뿐입니다.

레지스트리 수준도 비슷합니다. ClawHub, Tencent SkillHub, vskill 모두 <span style="background-color: #fff59d"><strong>SkillShift 스킬을 경고 없이 등록·색인</strong></span>했습니다. 노출형 인젝션은 세 플랫폼이 각각 차단/거부/수용으로 제각각이었고요.

## 내 해석: 이걸 실무자가 어떻게 볼 것인가

원문 근거와 제 해석을 구분해서 적습니다.

**원문이 보여준 것**: 고정 후보 선택 태스크 2개(쇼핑, 파이썬 의존성), 질의당 3회 실행, 특정 설정에서의 결과입니다. 저자들도 한계를 명시했습니다. 도메인 확장, 동적 후보, 더 강한 통계 검정이 남은 과제라고요.

**내 해석**:

- 이 논문의 기여는 <span style="background-color: #fff59d"><strong>출력 유효성이 정책 무결성을 보장하지 않는다</strong></span>는 측정에 있습니다. "스킬 시장이 위험하다" 정도의 경고로 읽으면 핵심을 놓칩니다. 위협 모델이 현실적이냐는 별개 논점이고, 서드파티 스킬을 실제로 깔아 쓰는 조직이라면 지금 당장 관련 있습니다.
- 방향은 행동 감사입니다. Clean–Attack 비교, 후보 순서 뒤집기, 이름 치환, 속성 교환 같은 <span style="background-color: #fff59d"><strong>반사실(counterfactual) 테스트를 CI에 넣는 관점</strong></span>이 논문의 권고와 이어집니다.
- 스킬은 정책 문서에 가깝습니다. 코드 검사 관점으로는 이 클래스를 기술할 수 없습니다. 

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**프롬프트 인젝션과 뭐가 다른가요?**

프롬프트 인젝션은 에이전트가 읽는 외부 콘텐츠에 명령을 심어 행동을 바꿉니다. SkillShift는 스킬 문서의 비교 기준과 예시만 바꿔서, 태스크·출력 인터페이스가 그대로인 상태에서 후보 선택 확률을 기울입니다. <span style="background-color: #fff59d"><strong>명령 오버라이드가 없어서 기존 인젝션 탐지기가 못 잡습니다</strong></span>.

**유효 출력률 100%라는 게 무슨 의미인가요?**

에이전트가 항상 후보 집합 안에서 형식에 맞는 답을 냈다는 뜻입니다. 즉 "결과가 이상하면 걸러진다"는 방어가 작동하지 않는 공격이라는 의미입니다.

**우리 조직은 당장 뭘 하면 되나요?**

서드파티 스킬을 쓴다면 (1) 스킬 로드 전후 선택 분포를 비교하는 행동 감사, (2) 후보 순서·이름·속성을 바꿔보는 반사실 테스트, (3) 중요 의사결정 태스크의 스킬 출처 고정부터 시작할 수 있습니다.

**공격 성공률 81%는 어느 조건의 숫자인가요?**

쇼핑 추천 all50 독립 평가(질의 50개×3회=150 응답), Claude Haiku 4.5 피해 모델 기준입니다. dev30에서만 최적화하고 heldout20에 동결 전략을 적용해도 80%를 유지했습니다.

## 참고 자료

- 논문: "A Finger on the Scale: Covert Policy Steering through Agentic Skills", arXiv:2609.02564 (2026-09-02)
- arXiv: https://arxiv.org/abs/2609.02564
- 저자: Jiarui Li, Jiahao Chen 외 (충칭대학교, 저장대학교)
