---
title: "JarvisGUI: 크로스 디바이스 GUI 에이전트 벤치마크 (arXiv 2609.10451)"
date: 2026-09-10
tags: [agent, benchmark, gui-agent, cross-device, evaluation]
draft: false
description: JarvisGUI는 Android·Windows·Ubuntu를 아우르는 크로스 디바이스 GUI 에이전트 벤치마크다. 기존 단일 디바이스 평가에 가려져 있던 상태 전달·장기 의존성 관리 실패를 수치로 보여준 EMNLP 2026 논문을 정리했다.
---

## 결론 먼저

JarvisGUI(arXiv 2609.10451, EMNLP 2026 Main)는 Android, Windows, Ubuntu 세 플랫폼으로 구성된 크로스 디바이스 GUI 에이전트 벤치마크다. 주요 결과는 다음과 같다.

- 원자 과제 최고 성적: <span style="background-color: #fff59d"><strong>HOLO2-30B, Overall TSR 42.4%</strong></span>
- 멀티 디바이스 의존(MD) 과제: <span style="background-color: #fff59d"><strong>최고 TSR 2%, 대부분 모델 0%</strong></span>
- 서브태스크 4개 이상 조합 과제: <span style="background-color: #fff59d"><strong>전 모델 성공률 0% 부근</strong></span>

## 핵심 수치 요약

| 항목 | 수치 |
|---|---|
| 원자 과제 | 118개 (Android 24 / Ubuntu 56 / Windows 38) |
| 조합 과제 | 150개 (SW 50 / MI 50 / MD 50) |
| 서브태스크 총계 | 442개 (Ubuntu 187 / Windows 138 / Android 52 / 파일 전달 65) |
| 가상 환경 | <span style="background-color: #fff59d"><strong>Docker + KVM 기반 3 OS 병렬 실행</strong></span> |
| 평가 방식 | 최종 환경 상태 검사(파일 내용, DOM 등) |

기준일: 2026-09-10, arXiv v1 표 2·3 기준.

## 벤치마크 구성 방법

JarvisGUI는 슬롯-타입 기반 원자 과제 모델링을 사용한다. 각 과제는 입력 슬롯 I와 출력 슬롯 O, 자연어 템플릿 D, 평가 함수 집합 Φ, 대상 플랫폼 P로 정의된다.

타입 공간은 서브타입 부분 순서를 가지며, <span style="background-color: #fff59d"><strong>출력 타입이 입력 타입의 서브타입일 때만 과제를 연결할 수 있다</strong></span>. 이 규칙 아래 원자 과제를 방향 그래프로 <span style="background-color: #fff59d"><strong>자동 조합</strong></span>해 크로스 디바이스 워크플로를 생성한다.

품질 관리는 다단계로 수행된다. 원자 과제는 사람 어노테이터가 20 스텝 이내 완수 가능하도록 설계했고, 평가 함수를 실행 전후로 돌려 완료 상태 변화를 확인한다.

조합 과제는 LLM 재판관(Qwen3-30B-A3B-Thinking-2507-FP8)이 현실성·일관성·평가가능성을 5점 척도로 평가하며 세 축 모두 만점인 과제만 <span style="background-color: #fff59d"><strong>남긴다</strong></span>. 사람 검증과의 <span style="background-color: #fff59d"><strong>Cohen's Kappa는 약 0.92</strong></span>다. 사람이 검증한 50개 조합 과제 중 92%가 완전히 정상이었다.

![Figure 1: JarvisGUI 개요](/images/2026-09-10-jarvisgui-cross-device-gui-agents/fig-1-p2.png)

Figure 1은 대표 과제를 보여준다. 안드로이드 폰으로 사진을 촬영하고, 클라우드 스토리지에 업로드한 뒤, Ubuntu에서 다운로드해 ImageMagick으로 흑백 PNG로 변환하고, 다시 폰의 /sdcard/Pictures에 art.png로 저장하는 7서브태스크 워크플로다.

![Figure 2: 시스템 아키텍처](/images/2026-09-10-jarvisgui-cross-device-gui-agents/fig-2-p4.png)

환경은 4계층 구조다(Infrastructure / Environment Control / Model Interaction / Evaluation Execution). Infrastructure Layer는 Docker 기반 가상화로 세 OS를 격리 실행하며 KVM으로 효율을 높인다.

## 실험 설정과 결과

평가 대상은 UI-Venus-Ground-7B, UI-TARS-1.5-7B, MAI-UI-8B, GUI-Owl-32B, Qwen3-VL-30B-A3B-Instruct, HOLO2-30B-A3B다. 기존 GUI 모델이 단일 플랫폼 관행에 맞춰 학습되었으므로, Qwen3-VL-Plus를 중앙 플래너로 세 플랫폼 스크린샷을 동시에 입력받는 Planner-Grounder 구조를 사용했다.

| 모델 | Atomic Overall TSR | SW TSR | MI TSR | MD TSR |
|---|---|---|---|---|
| HOLO2-30B | 42.4 | 16.0 | 6.0 | 2.0 |
| GUI-Owl-32B | 39.0 | 12.0 | 8.0 | 2.0 |
| UI-TARS-1.5-7B | 37.3 | 14.0 | 4.0 | 0.0 |
| Qwen3-VL-30B | 35.6 | 10.0 | 2.0 | 0.0 |
| UI-Venus-7B | 37.3 | 4.0 | 0.0 | 0.0 |

논문이 분석한 주요 실패 요인은 다음 세 가지다.

1. <span style="background-color: #fff59d"><strong>상태 추론 병목</strong></span>: 다른 디바이스의 실행 기록만으로 대상 디바이스의 현재 상태를 추론하지 못한다.
2. <span style="background-color: #fff59d"><strong>장기 임계 경로</strong></span>: 순차 단계에서 중간 한 단계 실패가 전체 체인을 끊는다.
3. 멀티 디바이스 인지 과부하: 화면 세 개 동시 처리가 그라운딩 정확도를 떨어뜨리고, 암시적 지시의 플랫폼 매핑이 실패한다.

![Figure 4: 서브태스크 수별 성공률](/images/2026-09-10-jarvisgui-cross-device-gui-agents/fig-4-p9-2.png)

Figure 4에서 서브태스크 수가 증가하면 전 모델의 성공률이 급감하며 4개 이상에서 <span style="background-color: #fff59d"><strong>0% 부근에 수렴한다</strong></span>. <span style="background-color: #fff59d"><strong>실행되지 않은 의존 단계를 완료로 가정하는 캐스케이드 오류</strong></span>가 원인이다.

플랫폼별로는 전 모델이 <span style="background-color: #fff59d"><strong>Windows에서 상대적으로 약했</strong></span>으며, 논문은 사전학습 데이터에서 고품질 Windows GUI 데이터가 부족하기 때문으로 분석한다.

![Table 1: 기존 벤치마크 비교](/images/2026-09-10-jarvisgui-cross-device-gui-agents/table-1-p5.png)

기존 벤치마크 중 크로스 디바이스를 다룬 CRAB은 <span style="background-color: #fff59d"><strong>관련 과제가 18개에 그치</strong></span>며 현실적 파일·데이터 전달을 모델링하지 않는다. JarvisGUI는 크로스 디바이스 실행, 동적 환경 최종 상태 평가, 동적 과제 생성을 동시에 만족한다.

## 더 실습해보고 싶은 분들께

에이전트 실습 관련 자료:

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**JarvisGUI가 기존 벤치마크와 다른 점은?**
세 OS 크로스 디바이스 평가, 타입 시스템 기반 동적 과제 합성, 최종 환경 상태 기반 자동 평가를 동시에 제공한다. CRAB은 크로스 디바이스 과제 18개에 그쳤다.

**에이전트들이 가장 많이 실패하는 지점은?**
MD(멀티 디바이스 의존) 과제로, 최고 모델도 TSR 2%, 대부분 0%다. 상태 추론 실패와 장기 임계 경로 단절이 주원인이다.

**JarvisGUI 과제 수와 구성은?**
원자 과제 118개, 조합 과제 150개, 서브태스크 총 442개다.

**환경 구성은 어떻게 재현하나?**
Docker + KVM으로 세 OS를 병렬 실행한다. KVM 미지원 환경에서는 재현에 제약이 있다.

## 참고 자료

- 논문: [arXiv:2609.10451](https://arxiv.org/abs/2609.10451)
- PDF: https://arxiv.org/pdf/2609.10451
- 채택: EMNLP 2026 Main Conference
