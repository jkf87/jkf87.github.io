---
title: "Claude Mythos, Anthropic이 풀지 않은 AI 모델 — 왜, 어떻게, 무엇이 다른가"
date: 2026-04-14
tags:
  - Claude Mythos
  - Anthropic
  - AI 모델
  - 사이버보안
  - 제로데이 취약점
  - Project Glasswing
  - Claude Opus
description: "Anthropic이 2026년 4월에 발표한 Claude Mythos Preview는 기존 Claude Opus 4.6을 압도하는 성능을 보여줬지만, 악용 위험 때문에 일반 공개하지 않았습니다. Project Glasswing, 벤치마크, 참여 기관, 보안 영향까지 정리합니다."
---

2026년 4월 7일, Anthropic은 평소와 다른 발표를 했습니다. 새 모델을 만들었는데, **일반 사용자에게는 주지 않겠다**는 것입니다.

그 모델의 이름은 **Claude Mythos Preview**. 내부 평가에서 "지금까지 만든 어떤 모델보다 훨씬 강력하다"고 Anthropic 스스로 인정한 모델입니다.

> "이 능력은 사이버보안 분야를 근본적으로 바꿀 수 있고, 악용될 경우 심각한 위협이 될 수 있다."

이 글에서는 Claude Mythos가 무엇인지, 왜 공개하지 않는지, 어떤 성능을 보이는지, 그리고 이것이 AI 업계에 무엇을 의미하는지 정리합니다.

---

## 한눈에 핵심 정리

- **Claude Mythos Preview**는 Anthropic의 새로운 최상위 모델 (기존 Opus 4.6 위)
- **SWE-bench 93.9%**, **USAMO 97.6%** 등 기존 벤치마크를 압도
- 사이버보안 분야에서 **모든 주요 OS와 웹 브라우저에서 수천 개의 제로데이 취약점** 발견
- 악용 우려로 **일반 공개하지 않고 Project Glasswing**를 통한 제한적 배포만 진행
- Apple, Google, Microsoft, Amazon, Nvidia 등 12개 런치 파트너 + 40개 기관 참여

---

## Claude Mythos란 무엇인가

### 기본 정보

| 항목 | 내용 |
|---|---|
| 정식명 | Claude Mythos Preview |
| 개발사 | Anthropic |
| 모델 티어 | Claude Haiku < Sonnet < Opus < **Capybara (Mythos)** |
| 발표일 | 2026년 4월 7일 |
| 모델 성격 | 일반 목적 모델 (보안 특화 학습 아님) |
| 공개 여부 | **초청 전용, 일반 공개 없음** |
| 가격 | 미발표 (Opus보다 현저히 비쌌다고 함) |

### 출발 배경: 3월 데이터 유출 사건

Mythos라는 이름이 처음 공개된 건 2026년 3월입니다. Anthropic의 콘텐츠 관리 시스템에서 실수로 유출된 내부 문서에 "Mythos — by far the most powerful AI model we've ever developed"라는 문구가 포함돼 있었습니다.

몇 시간 만에 Anthropic은 모델의 존재를 공식 인정했고, "능력에서 한 단계 도약(step change)"이라고 표현했습니다.

---

## 얼마나 강한가, 벤치마크 비교

Anthropic이 발표한 시스템 카드에 따르면, Mythos Preview는 이전 최상위 모델이었던 Claude Opus 4.6과 비교해 **여러 평가 지표에서 급격한 점프**를 보여줍니다.

### 핵심 벤치마크 비교표

| 벤치마크 | Claude Mythos Preview | Claude Opus 4.6 | 비고 |
|---|---:|---:|---|
| SWE-bench Verified (소프트웨어 엔지니어링) | **93.9%** | 80.8% | +13.1%p 상승 |
| USAMO 2026 (수학 올림피아드) | **97.6%** | 42.3% | +55.3%p 상승 |
| OSWorld (에이전트 자율 실행) | **79.6%** | - | 신설 벤치마크 |
| Cybench (보안) | **100%** | - | 기존 벤치마크 완전 소진 |

### 수치가 의미하는 것

**USAMO 97.6%**는 특히 눈에 띕니다. 미국수학올림피아드 문제를 거의 완벽하게 푸는 수준이며, Opus 4.6의 42.3%와 비교하면 한 세대가 넘는 도약입니다.

**SWE-bench 93.9%** 역시 실무 코딩에서 거의 인간 수준에 도달했음을 시사합니다.

**Cybench 100%**는 보안 벤치마크를 완전히 소진했다는 뜻입니다. Anthropic 스스로 "이제 이 벤치마크로는 현재 프론티어 모델의 능력을 제대로 측정할 수 없다"고 밝혔습니다.

---

## 왜 일반에 공개하지 않는가

이 부분이 Mythos의 가장 중요한 스토리입니다.

### 수천 개의 제로데이 취약점 발견

Anthropic은 Mythos를 내부 테스트하는 동안 다음 결과를 얻었다고 공식 발표했습니다.

> "지난 몇 주간 Claude Mythos Preview를 사용해 **모든 주요 운영체제와 모든 주요 웹 브라우저**에서 수천 개의 제로데이 취약점, 그중 많은 것은 치명적 수준을 발견했다."

구체적 사례로:
- **OpenBSD에서 27년 된 버그** 발견 (보안 강화를 표방하는 OS에서)
- 모든 주요 OS의 취약점 다수 확인
- 모든 주요 웹 브라우저의 취약점 다수 확인

### Anthropic의 논리

Anthropic의 보안 책임자 Logan Graham은 Axios 인터뷰에서 이렇게 밝혔습니다.

> "이 능력은 너무 강력해서, 지난 수십 년간 해왔던 것과는 전혀 다른 방식으로 보안에 대비해야 한다."

즉 Anthropic의 논리는 이렇습니다:

1. **방어용으로 쓰면 세상이 더 안전해진다** — 소프트웨어의 숨겨진 취약점을 찾아내서 고칠 수 있다
2. **공격자가 쓰면 재앙이다** — 원래 보안 전문가도 못 찾던 취약점을 악용할 수 있다
3. **그래서 일단 믿을 수 있는 기관에만 주고, 준비가 될 때까지 기다린다**

이 접근 방식은 AI 안전 연구에서 자주 논의되던 **"이중 사용(dual-use)" 문제**가 실제로 현실이 된 사례입니다.

---

## Project Glasswing: 제한적 배포 프로그램

Anthropic은 Mythos를 배포하기 위해 **Project Glasswing**라는 프로젝트를 만들었습니다. 이름은 "날개가 투명한 나비"에서 따왔는데, 소프트웨어 취약점이 "비교적 눈에 보이지 않는다"는 것에 대한 비유라고 Anthropic이 설명했습니다.

### 참여 기관

**12개 런치 파트너:**
Apple, Google, Microsoft, Amazon (AWS), Nvidia, CrowdStrike, Palo Alto Networks 등

**총 참여 기관:** 약 40개 기업 (보안·소프트웨어 인프라 기업 중심)

### 운영 방식

- 참여 기관은 **방어적 보안 목적으로만** Mythos를 사용
- 자사 소프트웨어와 오픈소스 소프트웨어 모두 취약점 탐색 대상
- Anthropic이 **최대 1억 달러(약 1,350억 원)의 사용 크레딧** 제공
- 그 이상 사용 시 기관 부담

### 정부와의 소통

Anthropic은 미국 정부 기관과도 논의 중이라고 밝혔습니다:
- CISA (사이버보안 및 인프라 보안국)
- CASI (AI 표준 및 혁신 센터)

---

## 기존 Claude 모델과의 관계

### 모델 계층 변화

Mythos가 추가되면서 Anthropic의 모델 라인업은 이렇게 변합니다:

| 티어 | 모델 | 포지셔닝 |
|---|---|---|
| **Capybara (신설)** | Claude Mythos Preview | 최강, 최고가, 초청 전용 |
| Opus | Claude Opus 4.6 | 고성능, 균형 잡힌 가격 |
| Sonnet | Claude Sonnet 4.6 | 빠르고 유능 |
| Haiku | Claude Haiku 4.5 | 가장 빠르고 저렴 |

### 일반 사용자에게 미치는 영향

현재 일반 사용자가 Claude API로 쓸 수 있는 가장 강한 모델은 여전히 **Claude Opus 4.6**입니다. Mythos는 별도 트랙으로 관리되며, 일반 API 접근은 제공되지 않습니다.

다만 Anthropic은 장기적으로 **"Mythos급 성능의 모델을 안전하게 대규모 배포하는 것"**이 목표라고 밝혔습니다. 즉, 지금 이 모델이 아니라 **이 정도 성능의 모델**을 언젠가 일반에도 풀겠다는 뜻입니다.

---

## AI 업계에 미치는 시사점

### 1) 벤치마크 위기

Mythos가 Cybench에서 100%를 기록하면서, 기존 벤치마크가 프론티어 모델의 능력을 더 이상 제대로 측정하지 못한다는 문제가 명확해졌습니다. AI 업계는 새로운 평가 척도를 만들어야 하는 상황입니다.

### 2) AI 안전 논의의 현실화

"AI가 위험할 수 있다"는 주장이 추상적이었는데, Mythos는 구체적인 사례를 제시했습니다. 실제로 수천 개의 제로데이를 발견할 수 있는 능력이 있다는 것을 Anthropic 스스로 증명한 셈입니다.

### 3) 보안 산업의 패러다임 전환

Anthropic의 내부 평가에 따르면, Mythos의 사이버보안 능력은 "다른 어떤 AI 모델보다 한참 앞선다"고 합니다. 이는 보안 분야에서 AI가 핵심 도구가 되는 시점이 가까워졌음을 시사합니다.

### 4) 선공개 전략의 선례

모델을 만들고 일부러 공개하지 않는 접근은 이례적입니다. Meta의 Llama 시리즈나 Google의 Gemini가 전면 공개한 것과 대비되는 전략으로, AI 안보안(안전+보안) 모델의 배포 방식에 새로운 기준을 제시할 가능성이 있습니다.

---

## 자주 묻는 질문, FAQ

### Q1. Claude Mythos를 일반 사용자도 쓸 수 있나요?
아니요. Anthropic이 공식적으로 "일반 공개할 계획이 없다"고 밝혔습니다. Project Glasswing 참여 기관에만 제공됩니다.

### Q2. Mythos는 보안용으로 특별히 학습시킨 모델인가요?
아니요. 일반 목적 모델입니다. Anthropic은 "보안 특화 학습이 아니라, 코딩과 추론 능력이 워낙 강해서 보안 분야에서 압도적 성능이 나온 것"이라고 설명했습니다.

### Q3. 언제쯤 일반에 나올 수 있나요?
시기는 미정입니다. Anthropic은 "Mythos급 성능의 모델을 안전하게 대규모 배포하는 것이 장기 목표"라고만 밝혔습니다.

### Q4. OpenBSD 27년 버그는 정말인가요?
Anthropic이 공식 발표에서 언급한 내용이지만, 독립적인 제3자 검증은 아직 없습니다. Anthropic의 자체 보고이므로 해석에 주의가 필요합니다.

---

## 마무리

Claude Mythos는 AI 모델이 단순히 "더 똑똑해지는 것"을 넘어, **사회적 책임과 보안 리스크가 함께 고려되어야 하는 시대**에 진입했음을 보여주는 사례입니다.

기술적으로는 Opus 4.6을 한참 뛰어넘는 성능을 보여줬지만, 그 능력이 너무 강해서 오히려 공개할 수 없다는 역설. Anthropic이 선택한 답은 **"조심해서, 믿을 만한 곳에만, 방어 목적으로만"**이었습니다.

앞으로 이런 방식이 AI 배포의 표준이 될지, 아니면 다른 경로로 일반화될지는 두고 봐야 합니다. 다만 확실한 건 하나입니다. AI 모델의 능력은 계속 커지고 있고, 그에 맞춘 거버넌스 논의는 그 속도를 따라가지 못하고 있다는 Stanford HAI의 지적이 Mythos에서 현실이 되었습니다.

---

## 참고한 자료

- Anthropic 공식 발표, Claude Mythos Preview System Card (2026.04.07)
- TechCrunch, "Anthropic debuts preview of powerful new AI model Mythos" (2026.04.07)
- CNBC, "Anthropic limits rollout of Mythos AI model over cyberattack fears" (2026.04.07)
- New York Times, "Anthropic Claims Its New A.I. Model, Mythos, Is a Cybersecurity 'Reckoning'" (2026.04.08)
- Axios, Logan Graham 인터뷰 (2026.04)
- WaveSpeedAI, "What Is Claude Mythos Preview?" 분석 글

## 원문 링크

- [TechCrunch 보도](https://techcrunch.com/2026/04/07/anthropic-mythos-ai-model-preview-security/)
- [CNBC 보도](https://www.cnbc.com/2026/04/07/anthropic-claude-mythos-ai-hackers-cyberattacks.html)
- [New York Times 보도](https://www.nytimes.com/2026/04/07/technology/anthropic-claims-its-new-ai-model-mythos-is-a-cybersecurity-reckoning.html)
- [WaveSpeedAI 분석](https://wavespeed.ai/blog/posts/what-is-claude-mythos-preview/)
