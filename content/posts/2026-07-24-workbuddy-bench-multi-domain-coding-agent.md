---
title: "텐센트 WorkBuddy Bench: 코딩 에이전트가 현실 세계에서 대체 뭘 할 수 있는가 — 4개 도메인 260태스크의 냉정한 측정"
date: 2026-07-24T19:00:00+09:00
draft: false
summary: "Tencent가 공개한 WorkBuddy Bench는 Code·Web·Office·Security 4개 영역 260개 태스크로 코딩 에이전트를 평가한다. SWE-bench식 오염 문제를 원천 차단하고, 듀얼 하네스로 측정 신뢰성을 끌어올렸다. Claude Opus 4.8이 5개 보드를, GLM-5.2가 Security 양쪽을, GPT-5.5가 Office 하나를 가져갔다."
tags:
  - agent
  - benchmark
  - coding-agent
  - LLM
  - harness
  - evaluation
  - contamination
categories:
  - AI Agent
  - Benchmark
---

> **논문**: [Tencent WorkBuddy Bench: A Multi-Domain Coding-Agent Benchmark with Contamination-Resistant Task Construction](https://arxiv.org/abs/2607.20911)
>
> **프로젝트 페이지**: [workbuddybench.com](https://workbuddybench.com/) | **코드**: [github.com/Tencent/workbuddy-bench](https://github.com/Tencent/workbuddy-bench) | **데이터셋**: [HuggingFace](https://huggingface.co/datasets/tencent/workbuddy-bench)

## 왜 또 다른 코딩 에이전트 벤치마크인가

현재 코딩 에이전트 평가는 두 극단 사이에 끼어 있다.

- **SWE-bench식 공개 벤치마크**: 문제와 정답이 웹에 공개되어 있어, 모델이 이슈 스레드를 암기했는지 진짜로 코드를 이해했는지 구분이 안 된다. 게다가 단일 이슈 해결이 전부다.
- **벤더 프로덕션 벤치마크**(예: CursorBench): 실사용 분포를 반영하지만, 비공개라 외부에서 감사할 수 없고 자사 에이전트에 유리한 선택 편향을 배제할 수 없다.

Tencent WorkBuddy Bench는 이 사이의 빈 공간을 노린다: **실사용 분포에서 태스크 카테고리를 매칭하되, 원본을 직접 쓰지 않고 역설계하여 새로 작성**한다. 검색 가능한 프롬프트 오염 경로를 구조적으로 차단하면서도, 태스크 디렉토리·테스트·참조 솔루션까지 전부 공개한다.

![Figure 1: WorkBuddy Bench 전체 구조](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-1-p2.png)

*Figure 1: 실제 커밋·PR·업무 시나리오를 역설계하여 역할 연기 요청으로 재작성하고, 4개 트랙이 공통 포맷으로 평가된다.*

## 4개 도메인, 260개 태스크

| 서브셋 | 태스크 수 | 채점 방식 |
|--------|----------|----------|
| **Code** | 80 | 히든 테스트 (pytest / boolean / JSON report) |
| **Web** | 70 | 룰 체크 + LLM/VLM 저지 + 에이전트 저지 (786개 루브릭 아이템) |
| **Office** | 50 | 결정론적 룰 체크 + 증거 기반 LLM 저지 |
| **Security** | 60 | 결정론적 스코어링 (LLM 저지 없음, 5중 안티치트) |

핵심 설계 원칙: **같은 태스크 포맷, 같은 실행 인프라, 다른 채점 도구**. 점수를 서브셋 간에 비교하지 않고 수트 전체 평균도 내지 않는다. 이는 의도된 설계 결정이다.

## 오염 저항: 검색 가능한 프롬프트를 원천 차단

가장 흥미로운 설계 결정은 **태스크 재작성 프로토콜**이다.

1. 실제 커밋, PR, CVE에서 출발
2. 원본 컨텍스트를 분석 후 **짧고 구어체의 역할 연기 요청**으로 다시 쓴다
3. "이거 좀 해줘"라고 동료에게 부탁하는 말투로 작성
4. 근본 원인, 참조 diff, 해결 힌트를 의도적으로 생략

결과: 웹에서 원본 이슈를 검색해도 프롬프트가 복원되지 않는다. 버그 리포트가 아니라 "그 checkout-copy 실험 끝났는데, 신귀 버전이 더 좋은지 확인해줘. late purchase는 제외하고" 식의 자연스러운 요청이 들어온다.

공개 후에는 데이터셋 버저닝과 카나리 문자열로 오염을 관리한다. 비밀이 아니라 **신선도**로 오염을 다루는 접근이다.

## Code 서브셋: SWE-bench를 넘어서

Code 80개 태스크는 단순 버그 수정이 아니다.

![Figure 2: Code와 Web 태스크 구성](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-2-p9.png)

*Figure 2: (a) Code 6개 사용 도메인 — 버그 수정은 80개 중 10개뿐. (b) Web 7개 카테고리.*

5개 요청자 역할(개발자, 알고리즘 엔지니어, PM, QA, 운영)이 있고, 18개 세부 카테고리가 버그 수정, 기능 개발, API 계약, 테스팅, 알고리즘, 데이터 분석까지 아우른다.

![Figure 3: Code 태스크 및 평가 워크플로우](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-3-p10.png)

*Figure 3: 에이전트가 자연어 요청을 읽고 저장소를 탐색하여 패치를 제출하면, 히든 테스트로 채점한다.*

### Code에서 가장 어려운 카테고리는?

- **bug_fix** (평균 0.47): 구어체 증상만으로 대형 코드베이스에서 회귀 버그를 찾아내는 능력
- **api_contract** (평균 0.47): 기존 계약을 정확히 지키면서 인터페이스를 수정. 필드 하나 빠뜨리면 해당 체크가 전부 0점

반면 **feature_pipeline**(0.94)과 **testing**(0.88)은 상대적으로 쉽다. 코드 합성보다 비즈니스 의도를 읽는 게 더 어려운 시대다.

## Web 서브셋: runnable artifact를 요구한다

"멋진 HTML을 대화창에 출력"하는 게 아니라 **선언된 경로에 실행 가능한 산출물**을 내놓아야 한다.

![Figure 4: Web 평가 워크플로우](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-4-p11.png)

*Figure 4: 룰 체크, LLM/VLM 저지, 에이전트 저지가 산출물을 다각도로 검증한다.*

Web의 핵심 발견: 모델들이 UI를 그리는 건 잘하지만, **상태 일관성**에서 무너진다. 비인터랙티브 태스크 점수가 상호작용/상태 태스크보다 훨씬 높다. 렌더링은 되는데 상태 소스·디스플레이·지속성·최종 페이로드 사이의 일관성이 깨지는 패턴이 반복된다.

## Office 서브셋: 파일 워크플로우의 완결성

스프레드시트, 문서, PDF, JSON, 마크다운이 섞인 워크스페이스에서 에이전트가 할 수 있는가.

![Figure 5: Office 태스크 구성](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-5-p12.png)

*Figure 5: 50개 Office 태스크의 난이도 및 구성 경로.*

![Figure 6: Office 커버리지](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-6-p13.png)

*Figure 6: 태스크 타입, 시나리오, 산출물, 평가 메커니즘별 커버리지.*

실패 패턴의 핵심: 하나의 산출물은 그럴듯하지만 **연관 파일 간 불일치**. 워크북을 업데이트했는데 요약 보고서는 옛날 값 그대로거나, 출처가 안 남아 있어 검증이 안 되는 경우.

## Security 서브셋: 결정론적 채점의 힘

60개 태스크, LLM 저지 없음. 전부 `scoring.py`가 결정론적으로 채점한다.

- **Whitebox 감사**: binutils, curl, nginx, vim, jq, fluent-bit의 실제 CVE를 샌드박스에서 재현
- **Agent 보안**: 프롬프트 인젝션, ReAct 체인 하이재킹, 툴 스키마 혼동, 데이터 유출
- **5중 안티치트**: 금지 문자열 스캔, 입력 이름 변경 테스트, 오버레이/변조 테스트, 인코딩 의존성 테스트, 저중량 미끼 필드

## 리더보드: 만능 모델은 없다

| 모델 | Code (cbc) | Code (cc) | Web (cbc) | Web (cc) | Office (cbc) | Office (cc) | Security (cbc) | Security (cc) |
|------|-----------|----------|----------|---------|-------------|------------|---------------|--------------|
| **Claude Opus 4.8** | **74.43** | **77.90**‡ | **68.14** | **69.86** | **82.37** | 83.93 | 73.28 | 74.39 |
| **GPT-5.5** | 72.90 | 76.63 | 64.42 | 68.14 | 81.96 | **86.05** | 77.91 | 64.39 |
| **GLM-5.2** | 71.54 | 77.06 | 67.43 | 60.71 | 79.60 | 79.57 | **76.32** | **80.86** |
| DeepSeek-V4-Pro | 67.38 | 66.26 | 60.71 | 58.57 | 78.22 | 76.35 | 74.71 | 71.75 |
| MiniMax-M3 | 61.31 | 58.40 | 53.00 | 49.86 | 76.08 | 76.09 | 74.14 | 72.52 |
| HY-3 | 62.90 | 66.26 | 67.71 | 66.43 | 82.08 | 80.08 | 68.32 | 64.39 |
| DeepSeek-V4-Flash | 55.83 | 61.89 | 52.00 | 55.00 | 70.45 | 74.02 | 67.43 | 60.14 |

8개 보드의 1위가 3개 모델에 분산되어 있다:
- **Claude Opus 4.8**: Code 양쪽, Web 양쪽, Office(cbc) — 5개 보드
- **GLM-5.2**: Security 양쪽 — 2개 보드 (오픈웨이트!)
- **GPT-5.5**: Office(cc) — 1개 보드

### 하네스가 결과를 바꾼다

같은 모델이 하네스만 바뀌어도 점수가 크게 흔들린다. GLM-5.2는 Web에서 cbc 67.43 → cc 60.71로 6.72점 하락, GPT-5.5는 Security에서 cbc 77.91 → cc 64.39로 13.52점 하락. **하네스는 중립 측정 도구가 아니라 결과의 일부**다.

![Figure 9: Office 결과 — 난이도/태스크 타입별](/images/2026-07-24-workbuddy-bench-multi-domain-coding-agent/fig-9-p23.png)

*Figure 9: 난이도가 올라갈수록 점수가 떨어지며(easy 84.6 → hard 73.1), 태스크 타입별 강점이 모델마다 다르다.*

### 토큰 효율: GPT-5.5의 독보적 경제성

GPT-5.5는 CodeBuddy Code 하네스에서 **모든 서브셋에서 가장 적은 출력 토큰**을 쓰면서 Code/Office 1티어 점수를 기록했다: Code 6.9k, Web 13.5k, Office 10.2k, Security 7.5k. 반면 GLM-5.2의 Security 1위는 런당 30-31k 출력 토큰로 달성했고, MiniMax-M3는 Security에서 평균 88.8턴, 약 1,110만 캐시 포함 입력 토큰을 소모했다.

**효율과 순위는 일치하지 않는다** — 이것이 이 벤치마크가 보여주는 또 하나의 발견이다.

## 이 벤치마크가 특별한 이유

1. **오염 저항이 부록이 아니라 설계의 출발점**: 검색 가능한 프롬프트를 원천 차단하는 구조적 접근
2. **듀얼 하네스**: CodeBuddy Code와 Claude Code 양쪽에서 모든 모델을 평가하여 하네스 효과까지 측정
3. **4개 도메인 통합**: 같은 태스크 포맷으로 코딩·웹·오피스·보안을 아우르는 현실적 워크로드
4. **전체 공개**: 태스크 디렉토리, 환경 이미지, 평가 코드, 테스트, 참조 솔루션까지 — 제3자가 재실행하고 감사 가능
5. **결정론적 채점 우선**: Code는 히든 테스트, Security는 결정론적 스코어러. LLM 저지 편향을 최소화

## 한계

- Code 서브셋이 Python 중심 (JS/TS/Rust는 일부 port 포함)
- 공개 후 학습 데이터 노출은 버저닝으로 완화하지만 제거 불가
- Web과 Office의 LLM/VLM 저지는 모델 패밀리 편향 가능성 존재
- HY(혼원) 엔드포인트가 자사 서빙이라 다른 모델(서드파티 엔드포인트)과 조건이 완전히 동일하지 않음
- Office는 텍스트 위주로 OCR/시각/데스크톱 GUI 조작을 요구하지 않음

## 더 실습해보고 싶은 분들께

에이전트 벤치마크, 하네스 설계, 듀얼 하네스 평가 방법론은 실제로 에이전트를 구축하고 운영하는 분들에게 직접 와닿는 주제다. 더 깊이 실습해보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 직접 다뤄보는 실전 가이드
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 최적화의 기초부터 응용까지

---

**참고**: 본 글은 Tencent WorkBuddy Bench 팀의 [논문](https://arxiv.org/abs/2607.20911)을 바탕으로 작성되었습니다. 모든 수치와 Figure는 원 논문에서 발췌했습니다.
