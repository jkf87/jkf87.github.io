---
title: "GPT 제대로 쓰는 법 — OpenAI 공식 프롬프트 가이드 핵심 정리"
date: 2026-04-30
tags: [AI, GPT, 프롬프트, OpenAI, 실무활용]
description: "OpenAI가 GPT-5.5 시대에 맞춰 공개한 공식 프롬프트 가이드. 결과 중심 구조, 모델별 전략, Reasoning Effort 조절법까지 한국어로 정리."
---

![GPT 프롬프트 가이드](./images/openai-prompt-guidance-2026-04-30/hero.png)

GPT 프롬프트를 잘 쓰고 있다고 생각했음.

근데 아니었음.

OpenAI가 GPT-5.5 시대에 맞춰 공식 프롬프트 가이드를 업데이트했음. 핵심 메시지는 하나.

**"과정을 지시하지 마라. 결과를 정의해라."**

예전 방식이 왜 아쉬운지, 새 방식은 어떻게 다른지 정리함.

---

## 1. 왜 프롬프트 방식이 바뀌었나

GPT-5 이전까지는 모델한테 단계를 알려줬음.
"먼저 이걸 해. 그 다음 저걸 해. 마지막으로 이렇게 해."

GPT-5.5에서는 그게 오히려 방해임.
모델이 스스로 효율적인 경로를 찾을 수 있음.
근데 프롬프트에서 이미 경로를 고정해버리면 그 능력이 막힘.

OpenAI가 직접 적어놓은 문장:

> *"Shorter, outcome-first prompts usually work better than process-heavy prompt stacks"*

결과를 정의하면 됨. 과정은 모델한테 맡겨.

---

## 2. 프롬프트 기본 구조

![프롬프트 구조 템플릿](./images/openai-prompt-guidance-2026-04-30/prompt-template.png)

OpenAI가 제안한 프롬프트 템플릿 구조임.

```
Role: [역할, 1-2문장]
# Personality: [톤, 협업 스타일]
# Goal: [사용자에게 보여줄 결과물]
# Success criteria: [완료 조건]
# Constraints: [제한사항, 안전, 근거 조건]
# Output: [섹션, 길이, 톤]
# Stop rules: [재시도, 폴백, 중단 조건]
```

**Personality**는 짧게. 역할과 협업 방식 두 가지만.

**Goal**은 "무엇을 만들어야 하는가"에만 집중.

**Stop rules**가 핵심임. 언제 멈출지, 언제 다시 물어볼지 명시해야 반복 루프가 없어짐.

---

## 3. Reasoning Effort 조절

![Reasoning Effort 선택 가이드](./images/openai-prompt-guidance-2026-04-30/reasoning-effort.png)

GPT-5 모델은 추론에 쓰는 리소스를 직접 설정할 수 있음.

| 레벨 | 용도 |
|------|------|
| `none` | 빠름, 저비용. 단순 분류, 포맷팅 |
| `low` | 지연시간 민감 + 약간의 정확도 |
| `medium` | 균형. 대부분 여기서 시작 |
| `high` | 복잡한 추론이 필요한 경우 |
| `xhigh` | 장기 에이전트 작업 전용 |

OpenAI의 조언: 기본은 `none`, `low`, `medium`에서 시작. 구조 개선 없이 `xhigh`부터 쓰는 건 낭비.

---

## 4. 모델별 전략 요약

**GPT-5.5**
- 결과 중심 짧은 프롬프트가 효과적
- 과정 지시 대신 성공 기준만 명시
- 스트리밍 앱에서는 tool call 전에 짧은 진행 상황 안내 추가

**GPT-5.4**
- "명확한 의도 + 되돌릴 수 없는 동작"만 질문하고 나머지는 알아서 진행
- Tool은 정확성을 높여주는 경우에만 사용하도록 지시
- 검색은 꼭 필요한 만큼만. 같은 결과로 반복 검색은 낭비

**GPT-5.3 / Codex (코딩 전용)**
- upfront plan 지양. 바로 구현으로
- `apply_patch` diff 포맷 그대로 사용 (이 형식으로 훈련됨)
- 파일 읽기는 병렬로. 순차 읽기는 시간 낭비

---

## 5. 자주 쓰이는 패턴 3가지

**Output Contract (출력 계약)**
"정확히 요청한 섹션만, 요청한 순서대로 반환해라."
구조화된 결과물이 필요한 작업에 필수.

**Empty Result Recovery (빈 결과 대응)**
"검색 결과가 없으면 다른 쿼리, 더 넓은 필터, 다른 출처 시도 후에 결론 내려라."
에이전트가 빈 결과 보고 그냥 멈추는 문제 방지.

**Default Follow-Through (기본 진행 정책)**
"의도가 분명하고 되돌릴 수 있는 작업이면 물어보지 말고 진행해라."
작업 흐름이 자꾸 끊기는 문제 해결.

---

## 6. 작은 모델 (mini / nano) 주의점

GPT-5.4-mini는 literal함. 암묵적 가정을 잘 못함.
nano는 더 좁은 범위 전용. 분류, enum 출력, 짧은 JSON에만 씀.

mini/nano 프롬프트에서는:
- 중요한 규칙을 맨 앞에
- 도구 사용 순서 명시
- 번호가 매겨진 단계, 의사결정 규칙 사용
- 애매한 상황 대처 방법 명시

nano에 멀티스텝 오케스트레이션 맡기면 안 됨. 복잡한 건 상위 모델로 라우팅.

---

실제로 써보면 차이가 확실히 느껴짐.

"이렇게 해, 저렇게 해" 대신 "이게 성공 기준이야, 이건 하면 안 돼"로 바꾸는 것만으로 결과가 달라짐.

원문: [OpenAI Prompt Guidance](https://developers.openai.com/api/docs/guides/prompt-guidance)
