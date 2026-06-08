---
title: "When AI builds itself — Recursive Self-Improvement"
source: https://www.anthropic.com/institute/recursive-self-improvement
author: The Anthropic Institute
date: 2026-06-08
clipped: 2026-06-08
tags: [AI, recursive-self-improvement, Anthropic, Claude, coding-agents, AI-safety]
---

# When AI builds itself — Recursive Self-Improvement

> For most of AI's history, humans drove every step in its development cycle. But at Anthropic, we are delegating a growing share of AI development to AI systems themselves, which is speeding up our work.

## 핵심 요약

Anthropic이 공개한 내부 데이터와 공개 벤치마크를 근거로, **AI가 AI 개발을 가속화**하고 있다는 증거를 체계적으로 정리한 글. 재귀적 자기 개선(recursive self-improvement)은 아직 완성되지 않았지만, 그 방향으로 빠르게 이동하고 있다.

---

## 진화 타임라인

| 시기 | 단계 | 설명 |
|------|------|------|
| 2021–2023 | 최초의 Claude 구축 | 일반 기업처럼 사람이 코드와 문서 작성 |
| 2023–2025 | 챗봇 | 짧은 코드 스니펫 생성 → 복사/붙여넣기 |
| 2025–2026 | 코딩 에이전트 | 파일 단위로 코드 작성/수정 |
| 현재 | 자율 에이전트 | 코드 직접 실행, 다른 에이전트에 작업 위임 |
| 20XX? | 루프 완성 | 에이전트가 모델 자체를 빌드/훈련 |

---

## 외부 증거: 벤치마크

- **태스크 지속 시간**: 4개월마다 2배 증가 (이전엔 7개월)
  - 2024.03: Claude Opus 3 → ~4분 태스크
  - 2025.03: Claude Sonnet 3.7 → ~1.5시간 태스크
  - 2026.03: Claude Opus 4.6 → ~12시간 태스크
  - 예측: 2027년에는 주 단위 태스크 가능

- **SWE-bench** (실제 오픈소스 버그 수정): 2년 만에 한자리 수 → 포화
- **CORE-Bench** (논문 재현): 2024년 ~20% → 15개월 후 포화
- **METR**: Claude Mythos Preview → "최소 16시간" 작업, 측정 한계 상단

---

## 내부 증거: Anthropic 데이터

### 엔지니어링

- **2026년 5월 기준, 병합되는 코드의 80% 이상이 Claude 작성**
  - Claude Code 출시 전(2025.02)에는 한자리 수%
- **엔지니어당 일일 코드 병합량**: 2024년 대비 8배 증가 (2026 Q2)
  - 2021-2024: 거의 일정
  - 2025: 상승 시작 (에이전트가 코드 제안이 아닌 직접 실행)
  - 2026: 다시 가파른 상승 (장시간 자율 작업)
- **코드 품질**:
  - 2025 말: 인간 코드보다 약간 낮음
  - 현재(2026): 대등(parity)
  - 예상: 올해 안에 인간보다 나아질 것
- **자동 코드 리뷰**: Claude가 과거 인시던트 버그의 약 1/3을 사전에 발견할 수 있었음
- **가장 개방적인 태스크 성공률**: 76% (2026.05, 6개월 전보다 +50%p)

### 생산성

- **130명 연구원 설문**: Mythos Preview 사용 시 중앙값 약 4배 생산성 향상 추정
- **예시**: 2026년 4월, Claude가 800개 이상의 수정으로 API 오류를 1/1000로 감소. 담당 엔지니어 추산: 인간이면 4년 걸릴 작업

### 연구

- **실험 최적화**: 작은 모델 학습 코드 최적화 태스크
  - 2025.05 (Opus 4): ~3배 속도 향상
  - 2026.04 (Mythos Preview): ~52배 속도 향상
  - 인간 숙련자 기준: 4-8시간에 4배
- **자율 연구**: AI 안전 문제(약한 모델이 강한 모델을 감독할 수 있는가?)를 에이전트에 할당
  - 인간 2명, 1주일: 성능 갭의 23% 복구
  - Claude 에이전트, 800시간/$18,000: 97% 복구
- **다음 단계 판단**: 인간이 "오프트랙"된 129개 지점에서
  - 2025.11 (Opus 4.5): 인간보다 나은 선택 51%
  - 2026.04 (Mythos Preview): 64%

---

## 인간의 역할 변화

> "The doing now costs almost nothing in human time, even if it still has costs in compute."

- 인간의 비교우위(현재): 연구 취향과 판단력 — 어떤 문제가 중요한지, 어떤 결과를 신뢰할지
- 코드 품질이 동등해지면 → 인간은 코드 작성 중단, 리뷰만
- 리뷰 속도 < 생성 속도 → 리뷰가 병목

### 직원들의 말

> "I started leaning hard into Claudifying about a year ago. It's now been ~5 months since I last wrote any code myself."

> "On days where everything works well, I can't help but think nothing I do matters... But then there are days where everything breaks and I realize I have no idea what I've been up to anymore."

> "Work ran on a gift economy of small favors... Claude is faster, it creates zero debt, but each of these is a lost bid for human collaboration."

---

## 반론에 대한 응답

- **"연구 방향 설정이 가장 중요한데, 그건 인간이 한다"** → 대부분의 AI 발전은 유레카가 아닌 증분적 개선. 스케일업 → 확인 → 수정 → 반복. 이게 Claude가 잘하는 것.
- 에디슨: "천재는 1% 영감, 99% 땀" → 땀의 자동화가 진행 중
- 보수적 해석: 인간이 방향 설정만 하고 Claude가 나머지 → 여전히 복합 가속
- 덜 보수적 해석: 연구 판단력도 AI 능력의 하나일 뿐, 다른 정성적 능력들처럼 결국 좋아질 것

---

## 시사점

- AI가 자신을 만드는 시대 → 과학, 의료 등에 엄청난 긍정적 가능성
- 동시에 인간의 AI 통제력 상실 위험 증가
- 보안, 모니터링, 행동 형성의 중요성 급증
- 대부분의 프론티어 진전은 자동화 가능 → 도구와 자원이 속도 결정
