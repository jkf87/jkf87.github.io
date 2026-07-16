---
title: "StructAgent: 인과적 상태 구조로 장기 과제를 정복하는 디지털 에이전트"
slug: 2026-07-16-structagent-long-horizon-causal-agent
publishDate: 2026-07-16
tags:
  - AI Agent
  - LLM
  - Computer Use
  - Long-Horizon Planning
  - Verification
draft: false
description: "StructAgent는 통일된 인과적 상태(unified causal state)와 구조화된 워크플로우를 통해 장기 실행 디지털 에이전트의 신뢰성을 획기적으로 높입니다. OSWorld-Verified에서 78.9% SOTA 달성."
coverImage: "/images/2026-07-16-structagent-long-horizon-causal-agent/fig-2-p3.png"
---

## 핵심 요약

**StructAgent**는 UC San Diego와 Aether AI Lab이 발표한 장기 과제(long-horizon) 디지털 에이전트 프레임워크입니다. 핵심 아이디어는 **통일된 인과적 상태(unified causal state)** 와 **구조화된 워크플로우(structured workflow)** 를 결합하여, 에이전트가 복잡한 다단계 작업을 투명하고 검증 가능하며 복구 가능하게 수행하도록 만드는 것입니다.

OSWorld-Verified 벤치마크에서 **오픈소스 SOTA인 78.9% 성공률**을 달성했으며, Qwen3.5-9B를 27.0%에서 46.9%로, Qwen3.5-27B를 31.6%에서 62.2%로 각각 끌어올렸습니다. 동일한 프레임워크를 Minecraft 환경에도 성공적으로 적용하여 범용성을 입증했습니다.

![Figure 1: OSWorld-Verified, Mind2Web, Minecraft 결과 요약. StructAgent가 다양한 백본 모델에서 일관된 성능 향상을 보이며, MiniMax-M3와 함께 78.9% SOTA 달성](/images/2026-07-16-structagent-long-horizon-causal-agent/fig-1-p2.png)

---

## 문제: 장기 과제에서 에이전트가 무너지는 이유

LLM 및 VLM 기반 디지털 에이전트는 단일 단계에서는 훌륭한 성능을 보이지만, **수십 단계에 걸친 장기 과제**에서는 급격히 신뢰성이 떨어집니다. 그 이유는:

1. **맥락 폭발**: 실행 기록이 누적되면서 중요 정보가 묻힘
2. **진행 상태 불투명**: 현재 어디까지 완료했는지, 무엇이 검증되었는지 불분명
3. **실패 복구 부재**: 중간 단계 실패 시 처음부터 다시 시작해야 함
4. **"완료" 남발**: 에이전트가 증거 없이 "Done"을 선언하는 문제

기존 접근법은 주로 역할 분담(role specialization), 프롬프트 엔지니어링, 또는 반성(reflection) 루프에 의존하지만, StructAgent는 더 근본적인 접근을 취합니다 — **상태(state) 자체를 구조화**하는 것입니다.

---

## StructAgent의 설계: 두 개의 핵심 축

### 1. 통일된 에이전트 상태 (Unified Agent State)

StructAgent는 길고 노이즈가 많은 상호작용 기록을 압축된 **상태 표현 $s_t$** 로 재구성합니다. 이 상태는 세 가지 구성 요소를 가집니다:

| 구성 요소 | 역할 |
|---|---|
| **$s_t^{req}$ (Requirements)** | 현재 수행해야 할 서브골과 검증 기준 |
| **s_t^{val}$ (Useful Values)** | 파일 경로, URL, 선택된 엔티티 등 실행 중 발견한 유용한 값 |
| **$s_t^{ver}$ (Verified Evidences)** | 검증자가 수집한 증거 — 이후 단계에서 감사 및 재사용 가능 |

모든 상태 전환은 **검증자(Verifier)의 결정에 의해서만** 발생합니다. 각 요구사항은 `Pending`, `Verified`, `Invalidated` 세 가지 상태를 가지며, 오직 증거 기반 검증만이 상태를 변경할 수 있습니다.

### 2. 구조화된 워크플로우 (Structured Workflow)

전체 실행 루프는 다음과 같은 고정된 흐름을 따릅니다:

$$s_t \xrightarrow{\text{Planner}} g_t \xrightarrow{\text{Actor}} \tau_t \xrightarrow{\text{Verifier}} d_t \xrightarrow{\text{Update}} s_{t+1}$$

- **Planner**: 상태 $s_t$를 읽고 다음 서브골 $g_t$를 결정
- **Actor**: 서브골을 환경에서 실행하여 실행 궤적 $\tau_t$ 생성
- **Verifier**: 결과를 검증하고 상태 업데이트 결정 $d_t$를 출력

![Figure 2: StructAgent 전체 구조. 통일된 상태가 공유 진행 인터페이스를 제공하고, 구조화된 워크플로우가 계획-실행-검증을 조정합니다. 검증자의 결정만이 상태를 확정하거나 무효화할 수 있습니다.](/images/2026-07-16-structagent-long-horizon-causal-agent/fig-2-p3.png)

---

## 고급 기능: 구조가 만드는 신뢰

### 진행 체크포인트 및 재개 (Progress Checkpointing)

상태 이력 자체가 재사용 가능한 체크포인트가 됩니다. 전체 상호작역 기록을 재생할 필요 없이 $s_t$만으로 실행을 재개할 수 있습니다.

### 표적 실패 복구 (Targeted Failure Recovery)

상태가 업데이트되지 않을 때, StructAgent는 단순한 재시도가 아닌 **검증된 증거 기반 진단**을 수행합니다:

- 증거 부족인가? → 추가 검증 시도
- 이전 진행이 무효화되었는가? → 재계획
- 반복 실패인가? → 전략 변경
- 환경 차단인가? → 인간 개입 요청

![Figure 3: 멀티앱 작업에서의 복구 사례. 검증자가 근거 없는 GUI 내보내기 진행을 거부하고, 올바른 증거를 수집하여 상태를 복구합니다.](/images/2026-07-16-structagent-long-horizon-causal-agent/fig-3-p9.png)

### 도구 지원 실행 (Tool-Supported Execution)

반복적인 실행 패턴을 메모리에서 식별하여 재사용 가능한 프로시저로 요약합니다. 단, 도구 실행 결과조차도 검증자의 승인이 있어야 상태에 반영됩니다.

---

## 실험 결과

### OSWorld-Verified (데스크톱 컴퓨터 사용)

| 모델 | 베이스라인 | StructAgent | 향상 |
|---|---|---|---|
| Qwen3.5-9B | 27.0% | **46.9%** | +19.9 |
| Qwen3.5-27B | 31.6% | **62.2%** | +30.6 |
| MiniMax-M3 | — | **78.9%** | 오픈소스 SOTA |

StructAgent는 동일한 백본 모델에서 Agent S3, OS-Symphony, VLAA-GUI 등 기존 프레임워크를 일관되게 능가했습니다.

### Mind2Web (웹 일반화)

웹 환경으로의 일반화도 입증되었습니다. 구조화된 상태 중심 루프가 특정 모델이나 환경에 국한되지 않음을 보여줍니다.

### Minecraft (도메인 간 일반화)

데스크톱 증거 소스를 인벤토리 기반 검증으로 교체하여 동일한 프레임워크를 Minecraft에 적용, 유의미한 개선을 달성했습니다.

---

## 검증의 질: 왜 StructAgent가 더 정확한가

![Figure 4: 구조화된 검증이 최종 완료 판단의 정확도를 높입니다. 검증자가 더 많은 경우에 정답을 내리며, 특히 "완료"를 잘못 선언하는 경우가 크게 줄었습니다.](/images/2026-07-16-structagent-long-horizon-causal-agent/fig-4-p9.png)

구조화된 검증 도입 후:
- **리콜(recall)** 0.67 → 0.81 향상
- **F1 점수** 0.70 → 향상
- 단순 시각 판단이 아닌, 파일 시스템·앱 상태 등 **숨겨진 증거**를 적극적으로 탐색

---

## 실패 분석: 남은 과제들

![Figure 6: 점수 0인 궤적의 실패 분석. 왼쪽: 주요 실패 역할과 유형. 오른쪽: 도메인별 실패 유형 분포.](/images/2026-07-16-structagent-long-horizon-causal-agent/fig-6-p10.png)

흥미롭게도, 남은 실패의 **33%만이 Actor(실행) 문제**입니다. Planner와 Verifier가 각각 30%씩을 차지하며, 이는 단순히 실행 모델을 키운다고 해결되지 않음을 의미합니다. 도메인별로도 실패 패턴이 다릅니다:

- **Calc, GIMP, Writer**: 실행 중심 실패
- **Multi-app, Impress**: 정보 선택 및 핸드오프 실패
- **Chrome, Thunderbird**: 상태 검증 및 외부 차단

이는 장기 과제 신뢰성이 **시스템 설계 문제**임을 확인시켜 줍니다.

---

## 관련 연구와의 차별점

StructAgent는 기존 구조화된 에이전트 시스템들과 다음 점에서 다릅니다:

| 특성 | 기존 시스템 | StructAgent |
|---|---|---|
| 역할 구조화 | ✓ | ✓ |
| 진행 검증 | 부분적 | **검증자만 상태 확정** |
| 적응적 복구 | 제한적 | **증거 기반 표적 복구** |
| 재사용 가능 도구 | ✓ | ✓ |
| **공유 작업 진행 상태** | ✗ | **✓** |
| **검증자 커밋 상태 업데이트** | ✗ | **✓** |

핵심 차이는 검증(verification)이 단순한 보상이나 비평이 아니라, **상태를 확정·보존·무효화하는 메커니즘**이라는 점입니다.

---

## 의의와 전망

StructAgent는 장기 과제 에이전트 설계에서 **상태 구조화(state structuring)** 가 핵심이라는 점을 실험적으로 입증했습니다. 단순히 더 큰 모델을 쓰거나 더 많은 도구를 달아주는 것 이상으로, **무엇을 알고, 무엇을 검증했으며, 무엇이 남았는지**를 명시적으로 추적하는 것이 신뢰성의 근본이라는 메시지입니다.

이 패러다임은 데스크톱 사용을 넘어 웹 에이전트, 임바디드 에이전트, 다중 에이전트 협업으로 자연스럽게 확장될 수 있습니다. 미래 방향으로는:

- 더 풍부한 의미·인과 표현을 가진 상태
- 적응형 워크플로우 정책 학습
- 복잡한 실제 과제를 위한 확장 가능한 검증 메커니즘

을 들 수 있습니다.

---

## 참고 자료

- **논문**: [arXiv:2607.11388](https://arxiv.org/abs/2607.11388)
- **코드**: [GitHub 저장소](https://github.com/smileformylove/XScientist) (참고: 논문에 명시된 저장소)
- **벤치마크**: [OSWorld-Verified](https://os-world.github.io/)
- **저자**: Wenyi Wu, Sibo Zhu, Kun Zhou (UC San Diego / Aether AI Lab)

![Figure 7: 검증 불일치 대표 사례. 구조화된 탐사가 숨겨진 파일이나 앱 상태의 증거를 복원하는 모습을 보여줍니다.](/images/2026-07-16-structagent-long-horizon-causal-agent/fig-7-p19.png)
