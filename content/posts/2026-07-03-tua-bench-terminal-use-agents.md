---
title: "TUA-Bench: 터미널에서 만능 에이전트를 평가하다 — 120개 과제, 65.8%가 한계"
date: 2026-07-03T07:00:00+09:00
draft: false
tags:
  - LLM
  - AI Agent
  - Benchmark
  - Terminal
  - CLI
  - Meta AI
categories:
  - AI 연구
  - Agent
summary: "Meta AI·Duke·Stanford가 공동 개발한 TUA-Bench은 코딩을 넘어 문서 편집, 이메일, 웹 검색, 과학·엔지니어링까지 120개의 실제 터미널 과제로 에이전트를 평가합니다. 최강 모델 Claude Opus 4.8도 65.8%에 그치며, 터미널 에이전트 시대의 새로운 표준 벤치마크를 제시합니다."
source_url: "https://arxiv.org/abs/2606.28480"
authors: "Shoufa Chen, Luyuan Wang, Xuan Yang, Zhiheng Liu, Yuren Cong, Yuanfeng Ji, Feiyan Zhou, Xiaohui Zhang, Fanny Yang, Belinda Zeng"
---

> **원논문**: [TUA-Bench: A Benchmark for General-Purpose Terminal-Use Agents](https://arxiv.org/abs/2606.28480)
>
> **저자**: Shoufa Chen*, Luyuan Wang* (Meta AI), Xuan Yang (Duke), Zhiheng Liu, Yuren Cong, Yuanfeng Ji (Stanford), Feiyan Zhou, Xiaohui Zhang, Fanny Yang, Belinda Zeng (Meta AI) · *공동 1저자
>
> **공식 사이트**: [tuabench.ai](https://www.tuabench.ai)

![TUA-Bench 개요: 5개 도메인의 실제 워크플로우를 터미널 과제로 평가](/images/2026-07-03-tua-bench-terminal-use-agents/fig-p1.jpeg)

## 한 줄 요약

터미널(명령줄)에서 동작하는 LLM 에이전트가 **코딩을 넘어 일상 컴퓨터 작업과 전문 연구 워크플로우까지 처리할 수 있는가?** — 120개의 실제 과제로 구성된 TUA-Bench이 이 질문에 답합니다. 최고 성능 에이전트(Claude Code + Opus 4.8)마저 **65.8%** 에 그쳤습니다.

---

## 왜 "터미널 에이전트" 벤치마크가 필요한가?

LLM 에이전트가 컴퓨터를 다루는 방식은 크게 두 가지입니다.

1. **GUI 기반**: 스크린샷을 보고 마우스 클릭 좌표를 계산 — OSWorld, WebArena 등
2. **터미널(CLI) 기반**: 텍스트 명령으로 직접 실행 — SWE-bench, Terminal-Bench 등

GUI 방식은 인간에게 자연스럽지만, LLM에게는 **시각 인식 + 좌표 계산**이라는 부가 비용이 발생합니다. 반면 터미널은 **텍스트 네이티브** 환경이라 LLM의 강점(언어 추론, 도구 사용)과 자연스럽게 맞물립니다.

문제는 기존 터미널 벤치마크들이 **코딩·셸 스크립트에 편중**되어 있다는 점입니다. 현실에서 터미널은 문서 편집, 이메일 관리, 웹 정보 검색, 데이터 분석, 과학 시뮬레이션까지 훨씬 다양한 작업에 쓰입니다. TUA-Bench는 이 간극을 메웁니다.

---

## TUA-Bench 구성: 5개 도메인, 120개 과제

![TUA-Bench 과제 분포: 5개 카테고리와 세부 서브카테고리](/images/2026-07-03-tua-bench-terminal-use-agents/fig-p2.png)

초안 394개 과제 중 엄격한 큐레이션을 거쳐 **120개**만 선정했습니다. 5개 카테고리는:

| 카테고리 | 내용 | 예시 |
|---------|------|------|
| **Office** | 문서 편집, 이메일 관리 | Markdown → DOCX 변환, 메일박스 정리 |
| **Web & Info** | 실시간 웹 정보 검색 | API 호출로 데이터 수집 후 요약 |
| **Multimedia** | 이미지·오디오·비디오 처리 | FFmpeg로 비디오 편집, 이미지 일괄 리사이즈 |
| **System & SW** | 시스템 관리, 소프트웨어 설치 | 패키지 의존성 해결, 서비스 설정 |
| **Science & Eng** | 전문 연구 워크플로우 | 생물정보학 파이프라인, 물리 시뮬레이션 |

특히 **Science & Eng** 트랙은 생물학, 의학 물리학, 건축 공학, 기계 공학 PhD 연구자들과 **공동 설계**했다는 점이 독특합니다. 단순 코딩이 아닌, 도메인 전문 지식이 필요한 과제들입니다.

각 과제는:
- **실제 터미널 환경**에서 실행 (컨테이너화된 샌드박스)
- **결정론적 셋업 스크립트**로 환경 구성
- **실행 기반 자동 채점**으로 객관적 평가

---

## 핵심 결과: 최강 에이전트도 65.8%

![모델별·카테고리별 성능 비교](/images/2026-07-03-tua-bench-terminal-use-agents/fig-p6.png)

### 전체 리더보드 (상위 5개)

| 순위 | 에이전트 | 모델 | 추론 강도 | 성공률 |
|------|---------|------|----------|--------|
| 1 | Claude Code | Claude Opus 4.8 | max | **65.8%** |
| 2 | Codex | GPT-5.5 | xhigh | 64.7% |
| 3 | Codex | GPT-5.5 | high | 64.2% |
| 4 | OpenHands | Claude Opus 4.8 | max | 63.4% |
| 5 | Mini-SWE-Agent | GPT-5.5 | xhigh | 62.4% |

### 카테고리별 인사이트

- **System & SW**가 가장 쉽고, **Office**와 **Multimedia**가 가장 어렵습니다.
- Claude Opus 4.8은 **Web & Info**에서 압도적 우위, 다른 카테고리에서는 중위권.
- GPT-5.5 (xhigh)가 **가장 균형 잡힌** 성능 — 모든 카테고리에서 상위권.
- 오픈웨이트 모델(GLM-5.1 48.1%, DeepSeek-V4 Pro 46.2%)은 여전히 프론티어 모델과 격차가 큽니다.

---

## 왜 100%가 불가능한가? 실패 패턴 분석

논문이 밝힌 주요 실패 원인:

1. **장기 계획(Long-horizon planning)**: 여러 단계를 거치는 과제에서 중간에 길을 잃음
2. **도구 사용(Tool use)**: 특정 CLI 도구의 옵션을 잘못 이해
3. **실행 모니터링**: 중간 결과를 확인하지 않고 다음 단계로 진행
4. **오류 복구(Error recovery)**: 실패 후 원인을 파악하지 못하고 재시도만 반복

이는 단순히 모델이 "똑똑해지면" 해결되는 문제가 아닙니다. 에이전트 프레임워크(하네스)의 설계, 도구 인터페이스, 피드백 루프 전반이 개선되어야 합니다.

---

## 의의: 터미널 에이전트 시대의 기준점

TUA-Bench의 의의를 세 가지로 정리합니다:

### 1. 코딩 → 범용 컴퓨터 사용
터미널 에이전트 평가를 소프트웨어 엔지니어링에서 **일상 디지털 작업과 전문 연구**로 확장했습니다.

### 2. 실행 기반 평가의 신뢰성
각 과제마다 실제 실행 결과를 검증하므로, 모델의 자기 보고(self-report)에 의존하지 않습니다.

### 3. 현실적 한계의 정량화
"에이전트가 거의 다 한다"는 낙관론에 대해 **34.2%의 실패**라는 명확한 숫자로 경고합니다.

---

## 한국어 독자를 위한 맥락

TUA-Bench이 시사하는 바는 분명합니다. Claude Code, Codex CLI, Gemini CLI 같은 터미널 에이전트가 실제로 사용되는 시점에서, **"어디까지 믿을 수 있는가"**를 정량적으로 보여줍니다.

- 개발자: 코딩 보조를 넘어 시스템 관리, 문서 처리까지 에이전트에 위임 가능 (단, 검증 필수)
- 연구자: 벤치마크 설계 방법론(PhD 협업, 실행 기반 채점) 참고 가치
- 기업: 터미널 에이전트 도입 시 65% 성공률이라는 현실적 기준치 활용 가능

---

## 결론

TUA-Bench는 터미널 에이전트 평가의 새로운 표준을 제시합니다. 120개의 다양한 과제, 5개 도메인, 실행 기반 채점 — 그리고 **최고 에이전트의 65.8% 성공률**이라는 숫자는, 에이전트 기술이 여전히 초기 단계에 있음을 명확히 보여줍니다.

> **"터미널은 LLM에게 가장 자연스러운 인터페이스다. 하지만 자연스럽다는 것과 완벽하다는 것은 다르다."**

---

*본 포스트는 학술 논문 [arXiv:2606.28480](https://arxiv.org/abs/2606.28480)을 기반으로 작성되었습니다. 모든 Figure는 원논문에서 발췌했습니다.*
