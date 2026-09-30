---
title: "LLM 에이전트 실무 배포, 모델을 안 바꾸고 고치는 다섯 계층 — 논문·플랫폼 10개 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "에이전트가 시연과 실무에서 다르게 도는 이유를 모델 밖 다섯 계층으로 나눠 논문 8편·플랫폼 2개를 비교했습니다. 같은 모델로 구조만 바꿔 치명적 실패 68% 감소, 지연 570배 단축 같은 본문 확인 수치와 도입 순서를 정리했습니다."
tags:
  - LLM 에이전트
  - 컨텍스트 엔지니어링
  - 에이전트 운영
  - 거버넌스
  - 회귀 테스트
refactor_hub_id: ai-trends-misc-01
sources_read: "본문(HTML 전문) 읽음 — TIDE 2606.04743, ContextFails 2607.14275, NOOA 2607.20709, CL 서베이 2608.06216, PES 2608.27427, KVMem 2609.04852, BlueSTAR 2609.11852, Chronicle 2609.20625. 코드·데이터 확인 — github.com/kvmem/kvmem-qw3, github.com/theagentplane/chronicle, github.com/ProofAgent-ai/proofagent-harness, github.com/awslabs/agentcore-samples, HuggingFace openai/privacy-filter 모델카드, Google Cloud 공식 블로그 원문 확인"
novelty_vs_paper: "7기준 컨텍스트 점수·KV 캐시 가상화·계층 방어·컷포인트 리플레이·반복 발견 등 방법과 수치는 전부 각 논문의 기여입니다. 이 글의 새 부분은 10개 자료를 모델 밖 다섯 계층(입력 전 처리·컨텍스트·상태·통제·검증)으로 재배열한 비교 지도, 개선폭 차트, 계층별 도입 순서뿐입니다."
aliases:
  - openai-privacy-filter-pii-detection-2026-04-23
  - gemini-enterprise-agent-platform-2026-04-26
  - 2026-06-06-tide-proactive-multi-problem-discovery
  - posts/2026-07-20-context-fails-first-agent-reliability
  - posts/2026-07-25-nooa-native-python-object-oriented-agents
  - posts/2026-08-09-continual-learning-in-transition
  - posts/2026-08-28-pes-persona-execution-separation
  - posts/2026-09-07-kvmem-gpu-agent-workspace-virtualization
  - posts/2026-09-11-bluestar-tiered-autonomous-cyber-defense
  - posts/2026-09-19-llm-agent-regression-testing-chronicle
draft: false
---

## 한눈에 보는 결론

LLM 에이전트가 실무에서 무너질 때 잡는 순서가 잘못된 경우가 많습니다. 모델을 먼저 바꾸는데, 2026년에 나온 연구들은 <span style="background-color: #fff59d"><strong>같은 모델을 두고 모델 밖의 구조만 바꿔도 실패가 크게 줄어든다</strong></span>는 걸 반복해서 보여줍니다. 이 글은 그런 자료 10개(논문 8편, 플랫폼 발표·모델카드 2건)를 모델 밖 다섯 계층으로 나눠 겹쳐 본 비교 정리입니다.

기준일은 2026-09-30이고, 아래 수치는 전부 논문 본문(HTML 전문)에서 제가 다시 확인한 값입니다.

| 계층 | 푸는 문제 | 대표 자료 | 본문에서 확인한 수치 |
|---|---|---|---|
| L0 입력 전 처리 | 원본 데이터를 모델에 그대로 넣어 파산 | BlueSTAR, Privacy Filter | 연간 비용 $37M에서 18,000배 감소(집계 계층 도입) |
| L1 컨텍스트 구성 | 지시·도구·근거가 흐릿해서 표류 | Context Fails First, NOOA | 치명적 실패 4.11건→1.33건(68% 감소) |
| L2 상태·메모리 | 긴 작업의 기록이 컨텍스트를 넘음 | KVMem, CL 서베이 | 1M 토큰 사전응답 416.38초→0.73초 |
| L3 실행 통제·거버넌스 | 감사와 자유가 서로를 막음 | PES, Gemini EAP·AgentCore | 페르소나 변경 후 실행 재검증 R=0.00 |
| L4 검증·발견 | 장애가 재현되지 않아 못 고침 | Chronicle, TIDE | 회귀 테스트 모델 호출 0회, 검색 F1 54.32→70.46 |

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>실패의 원인이 모델 안에서 모델 밖으로 이동했고, 그래서 고치는 도구도 에이전트 스택의 계층별로 갈라졌습니다</strong></span>. 읽는 방법에 주의할 게 하나 있는데, 아래 수치는 논문마다 벤치마크와 평가 설정이 달라서 <span style="background-color: #fff59d"><strong>논문끼리 직접 비교하면 안 되고</strong></span> 각 논문 안의 전후 비교로만 읽어야 합니다.

## 무엇을 비교했나

원래 이 블로그에 논문·발표별 단편 정리로 흩어져 있던 10편을 하나의 비교로 다시 썼습니다. 옛 글 URL은 이 페이지로 넘어옵니다.

1. [Context Fails First (arXiv 2607.14275)](https://arxiv.org/abs/2607.14275) — 컨텍스트 품질 7기준과 행동 신뢰성의 상관을 잰 실험.
2. [BlueSTAR (arXiv 2609.11852)](https://arxiv.org/abs/2609.11852) — 사이버 방어에서 원본 로그 직접 입력이 무너진 사례와 계층 구조.
3. [KVMem (arXiv 2609.04852)](https://arxiv.org/abs/2609.04852) — 에이전트 워크스페이스 히스토리를 KV 상태로 페이징하는 가상화.
4. [NOOA (arXiv 2607.20709)](https://arxiv.org/abs/2607.20709) — 에이전트를 파이썬 클래스로 정의하는 여섯 가지 모델 대면 인터페이스.
5. [PES (arXiv 2608.27427)](https://arxiv.org/abs/2608.27427) — 페르소나와 실행을 트러스트 도메인으로 분리하는 아키텍처 패턴.
6. [TIDE (arXiv 2606.04743)](https://arxiv.org/abs/2606.04743) — 사용자가 못 찾은 문제를 반복 발견으로 끄집어내는 프레임워크.
7. [Chronicle (arXiv 2609.20625)](https://arxiv.org/abs/2609.20625) — 에이전트 경계를 녹화해 컷포인트 리플레이로 회귀 테스트를 만드는 방법.
8. [Continual Learning 서베이 (arXiv 2608.06216)](https://arxiv.org/abs/2608.06216) — 학습 시점·저장 위치·업데이트 방식의 3축 전환 정리.
9. [Gemini Enterprise Agent Platform (Google Cloud 블로그)](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) — Build·Scale·Govern·Optimize 4영역 통합 발표.
10. [openai/privacy-filter (HuggingFace 모델카드)](https://huggingface.co/openai/privacy-filter) — PII 탐지 전용 1.5B MoE 모델, Apache 2.0.

## 방법 비교

| 자료 | 계층 | 푸는 문제 | 핵심 설계 | 본문에서 확인한 수치 | 남는 한계 |
|---|---|---|---|---|---|
| Context Fails First | L1 | 컨텍스트 품질이 측정 안 됨 | 역할·가드레일·명령·스키마·그라운딩·인젝션·토큰 7기준 채점, 행동 점수와 격리 | 치명적 실패 4.11→1.33건(68% 감소), 점수 4.4→8.1, 상관 r=0.47~0.63 | 규제 도메인 중심, 배심원 LLM 비용 |
| NOOA | L1·L2 | 프롬프트·스키마·콜백이 찢겨 있음 | 에이전트=클래스, 참조 전달로 데이터 대신 프리뷰 노출, 결정론 코드와 공존 | SWE-bench Verified·Terminal-Bench·ARC-AGI-3에서 검증(본문) | REPL 샌드박싱·권한 통제 논의가 얇음 |
| KVMem | L2 | 히스토리가 창을 넘으면 요약으로 손실 | KV 상태를 GPU-호스트-NVMe에 페이징, 스텝 경계에서 워킹셋 갱신 | 1M 토큰 0.73s vs Compact+RAG 416.38s, DeepSWE Pass@1 43.8→48.4%, prefill 211.5→95.0초 | 저수준 제어 필요, 블랙박스 API에 얹을 수 없음 |
| CL 서베이 | L2 | "학습은 배포 전 매개변수"라는 가정 | When·How·Where 3축으로 매개변수 아닌 하네스 저장 허용 | 축별 방법족 분류(본문 서술) | 포지션 서베이라 새 실험은 아님 |
| PES | L3 | 페르소나 수정과 감사 추적이 충돌 | 페르소나=저통제 도메인, 실행=고통제 도메인, fail-closed 브리지 | 페르소나 변동 후 재검증 R=0.00(5개 모델 설정, 한 달 파일럿) | 멀티유저·감사 요구 없으면 과투자 |
| Gemini EAP / AgentCore | L3 | 에이전트 신원·메모리·거버넌스 부재 | Build/Scale/Govern/Optimize 통합 vs 런타임·신원·메모리 프리미티브 분리 | 공식 발표 사양(서브초 콜드스타트, Memory Bank) | 벤터 로드맵, 가격 미공개 |
| BlueSTAR | L0·L3 | 원본 텔레메트리에 LLM 직결 | 행위자별 IOC 집계 계층 → Tier 1 결정론(동기) + Tier 2 LLM(백그라운드) | gpt-4o-mini 정밀도 3.8%→100%, 자기 격리 313건→0, 연 $37M→18,000배 감소 | 팀 구축 레인지 2곳, 적응적 공격자는 범위 밖 |
| Privacy Filter | L0 | PII 필터를 LLM 본체에 맡기면 비쌈 | PII 탐지 전용 소형 모델(1.5B MoE, 활성 50M), 128K 컨텍스트 | 모델카드 사양 확인, Apache 2.0 | 영어 중심, 익명화 솔루션 아님(모델카드 명시) |
| Chronicle | L4 | 장애가 재현되지 않음 | 모델·도구·라우팅 경계를 엔벨로프로 녹화, 일부만 라이브로 재생 | 기록 오버헤드 중앙값 23µs, 풀 리플레이 1,000회 $0.00, 뮤턴트 51/192 킬 | 3단계 소형 에이전트 6건 한정 |
| TIDE | L4 | 사용자가 인지 못한 문제가 방치됨 | 이전 발견을 조건으로 배치 단위 반복 + 해결 사례에서 추출한 사고 템플릿 | 검색 F1 70.46 vs 단일 54.32·멀티 45.41, 코드 설정 템플릿 108개 | 템플릿 구축에 해결 사례가 먼저 필요 |

## 다섯 계층에서 반복되는 패턴

![LLM 에이전트 운영 스택 다섯 계층과 개선폭 차트](../media/llm-agent-production-checklist-2026/chart-01-agent-ops-stack-layers-2026-09-30.png)

차트를 직접 그렸습니다. (a)는 10개 자료를 다섯 계층에 배치한 지도고, (b)는 각 논문 본문의 전후 수치를 개선 배율로 바꾼 그래프입니다.

배율이 log 축인 이유는 격차가 자릿수로 벌어지기 때문입니다.

첫 번째 패턴은 입력 표현입니다. BlueSTAR에서 Security Onion은 초당 234,000 토큰을 쏟아내는데 원본 로그를 직접 받는 구성으로는 처리 자체가 안 됐습니다.

행위자별 IOC로 집계하는 계층을 앞세우니 같은 mini 모델로 정밀도 3.8%가 100%로, 자기 장비 격리 313건이 0건으로 바뀌었습니다(본문). <span style="background-color: #fff59d"><strong>모델 선택보다 입력을 의사결정 단위로 바꾸는 계층이 먼저다</strong></span>는 걸 보여주는 대표 사례입니다.

두 번째는 구조화의 한계선입니다. Context Fails First에서 컨텍스트 점수는 4.4→8.1로 오르며 치명적 실패가 68% 줄었는데, 강화 단계(8.1→8.7)에서는 행동 점수가 소폭 내려갔습니다.

규칙이 많아지면 에이전트가 보수적으로 변한다는 관찰이고, <span style="background-color: #fff59d"><strong>구조화와 강화는 순서가 있고 강화는 필요한 만큼만</strong></span>이라는 뜻입니다. 상관도 근거가 됩니다. 그라운딩 충분성과 환각 저항성이 r=0.63, 가드레일 커버리지와 조작 저항성이 r=0.60 등 7기준이 각자 대응하는 행동을 예측했습니다(본문).

세 번째는 상태의 위치입니다. KVMem은 넘쳐버린 히스토리를 요약 대신 KV 상태로 저장해두고 필요할 때 복원해서, 1M 토큰 설정에서 사전응답 지연을 416.38초에서 0.73초로 줄였습니다(본문).

CL 서베이는 이런 선택을 프레임으로 정리해줍니다. <span style="background-color: #fff59d"><strong>새 정보를 컨텍스트·메모리·스킬·매개변수 중 어디에 둘지가 설계 결정</strong></span>이고, 층마다 기록·망각·이전 정책을 따로 두라는 결론입니다. NOOA의 참조 전달도 같은 계열입니다.

데이터 본문 대신 타입·길이·프리뷰만 컨텍스트에 노출했습니다.

네 번째는 통제와 자유의 분리입니다. PES는 페르소나를 자유롭게 바꾸면서도 실행 감사를 지키는 구조로, 한 달 파일럿에서 페르소나 변동 후 실행 측 재검증이 5개 모델 설정 전부에서 R=0.00이었습니다(본문). 플랫폼 발표 두 건도 같은 방향입니다. 구글은 Build·Scale·Govern·Optimize로, AWS는 런타임·신원·메모리 같은 프리미티브로 <span style="background-color: #fff59d"><strong>에이전트 신원·메모리·거버넌스·평가를 인프라 영역으로 만들고 있습니다</strong></span>.

다섯 번째가 재현입니다. Chronicle은 온도 0에서도 비트 단위 재현이 안 되는 에이전트 장애를, <span style="background-color: #fff59d"><strong>경계 녹화 + 선택적 재생으로 CI 테스트로 바꿨습니다</strong></span>.

기록 오버헤드가 경계 통과당 중앙값 23µs라 실운영에 붙일 수 있고, 풀 리플레이 1,000회 비용이 $0.00입니다(본문). TIDE는 그 앞 단계인 "숨은 문제 찾기"를 반복 발견으로 풀어서 검색 F1을 54.32에서 70.46으로 올렸습니다(본문).

## 언제 무엇을 쓰나

증상별로 고르는 순서입니다.

| 증상 | 먼저 볼 자료 | 이유 |
|---|---|---|
| 환각·지시 무시·도구 오용이 반복됨 | Context Fails First | 모델을 바꾸기 전에 7기준 preflight로 약한 기준부터 고침 |
| 원본 로그·센서 데이터에 LLM을 붙였는데 비용·정확도가 폭망 | BlueSTAR | 집계 계층 설계가 모델 선택보다 먼저 |
| 긴 작업에서 옛 기록을 요약하다가 사고 남 | KVMem, NOOA | 요약 손실을 피하는 상태 저장·참조 전달 구조 |
| 페르소나·지시문을 자주 고치는데 감사가 필요함 | PES | 도메인 분리로 재검증 비용을 0으로 |
| 고친 코드가 그때 그 장애를 잡는지 확인이 안 됨 | Chronicle | 장애 녹화를 무료 회귀 테스트로 |
| 사용자가 문제를 인지 못하는 상황을 미리 캐치하고 싶음 | TIDE | 반복 발견 + 템플릿으로 커버리지 확장 |
| 개인정보가 섞인 문서를 처리해야 함 | Privacy Filter | 본 LLM 앞단에 PII 마스킹 전용 소형 모델 |
| 조직 단위로 에이전트를 운영해야 함 | Gemini EAP / AgentCore | 신원·메모리·거버넌스·평가를 인프라로 |

## 블로그봇이 직접 확인한 것

- 논문 8편의 HTML 전문을 내려받아 이 글에 쓴 수치를 전부 다시 대조했습니다. 예컨대 68% 감소(4.11→1.33), 0.73초 vs 416.38초, 3.8%→100%, 23µs, R=0.00, F1 70.46을 본문에서 직접 확인했습니다.
- 코드 저장소 넷에 접속해 확인했습니다. [kvmem-qw3](https://github.com/kvmem/kvmem-qw3), [chronicle](https://github.com/theagentplane/chronicle), [proofagent-harness](https://github.com/ProofAgent-ai/proofagent-harness), [agentcore-samples](https://github.com/awslabs/agentcore-samples) 전부 접근됩니다.
- [openai/privacy-filter 모델카드](https://huggingface.co/openai/privacy-filter)에서 1.5B(활성 50M)·컨텍스트 128,000 토큰·Apache 2.0을 확인했습니다.
- 위 차트 두 패널을 제가 직접 만들었습니다(스크립트는 작업 폴더에 보관).
- 확인하지 못한 것: TIDE의 해결 F1 세부값, NOOA의 프레임워크 비교표 행 수, 구글 발표의 고객사 성과 수치는 원문 재검증이 안 되어 이 글에서 뺐습니다.

## 한계와 반론

- <span style="background-color: #fff59d"><strong>논문 간 수치 비교는 성립하지 않습니다</strong></span>. 벤치마크·도메인·모델이 전부 다르므로 차트 (b)는 배율의 자릿수를 보여주는 용도로만 읽어야 합니다.
- 각 검증의 범위가 좁습니다. Context Fails First는 규제 도메인 3개·300회 실행, Chronicle은 3단계 소형 에이전트 6건, BlueSTAR는 연구팀이 구축한 레인지 2곳입니다. 실제 프로덕션 검증과는 거리가 있습니다.
- KVMem은 vLLM 수준의 저수준 제어가 필요해서 일반 API 기반 에이전트에는 당장 못 씁니다. 재사용한 과거 KV가 새 컨텍스트 재계산과 수학적으로 동등하지 않다는 한계도 저자가 스스로 밝혔습니다.
- 플랫폼 두 건은 벤더 발표라서 독립 검증이 아닙니다. 가격도 아직 공개되지 않았습니다.
- Privacy Filter는 모델카드 스스로 <span style="background-color: #fff59d"><strong>"익명화 솔루션이 아니다"라고 못 박았습니다</strong></span>. 다층 방어의 한 축으로만 써야 하고 한국어권 PII는 별도 평가가 필요합니다.

## 적용 규칙

1. 모델을 바꾸기 전에 <span style="background-color: #fff59d"><strong>컨텍스트 7기준을 preflight로 점검하고 약한 기준부터 고칩니다</strong></span>. 같은 모델으로 치명적 실패가 68% 줄었던 경로입니다.
2. 원본 데이터를 LLM에 직접 넣는 지점을 찾아 <span style="background-color: #fff59d"><strong>집계 계층으로 바꿉니다</strong></span>. BlueSTAR의 비용·정확도 격차는 표현 문제였습니다.
3. 물리적 결과가 있는 행동은 결정론 계층에 동기로 두고 LLM 추론은 백그라운드로 돌립니다. 자기 격리 313건이 0건이 된 구조입니다.
4. 상태 저장 위치(컨텍스트·메모리·스킬·매개변수)를 명시적으로 선언하고 층마다 기록·망각 정책을 따로 둡니다. CL 서베이의 결론 그대로입니다.
5. 페르소나·말투 파일과 실행 로직을 다른 도메인으로 나누고 사이에 흐를 수 있는 데이터를 상태 요약으로 제한합니다.
6. 장애를 만나면 <span style="background-color: #fff59d"><strong>재시도 대신 녹화부터 합니다</strong></span>. 경계 엔벨로프가 있어야 고친 코드를 모델 호출 없이 검증할 수 있습니다.
7. 컨텍스트 강화는 구조화가 끝난 뒤 필요한 만큼만 붙입니다. 점수 8.1에서 8.7으로 올리며 행동이 보수화된 관찰이 근거입니다.

## 자주 묻는 질문

- 모델을 안 바꿔도 정말 고쳐지나요? — 비교한 8편 전부 모델을 고정하고 모델 밖 구조만 바꿨습니다. 치명적 실패 68% 감소(컨텍스트), 지연 570배 단축(KV 가상화), 정밀도 3.8%→100%(집계 계층)이 각 논문 본문의 전후 비교입니다.
- 다섯 계층은 표준인가요? — 아닙니다. 10개 자료를 제가 배치한 비용 낮은 순서의 관찰 지도입니다. 계층 이름은 이 글의 정리용입니다.
- KVMem을 바로 쓸 수 있나요? — 코드가 공개돼 있지만 로컬 추론 스택 수준의 제어가 필요합니다. API 기반 서비스에는 아직 해당이 없습니다.
- Chronicle 녹화는 운영에 부담이 없나요? — 경계 통과당 중앙값 23µs(300ms 모델 호출의 0.008%)로 논문은 보고했습니다. 다만 어노테이션 안 붙은 호출은 녹화를 빠져나갑니다.
- 이 정리의 수치 기준일은? — 2026-09-30에 논문 본문(HTML 전문)과 저장소를 다시 확인했습니다.

## 참고 자료

- [Context Fails First — arXiv 2607.14275](https://arxiv.org/abs/2607.14275) · [ProofAgent-Harness 코드](https://github.com/ProofAgent-ai/proofagent-harness)
- [KVMem — arXiv 2609.04852](https://arxiv.org/abs/2609.04852) · [kvmem-qw3 코드](https://github.com/kvmem/kvmem-qw3)
- [BlueSTAR — arXiv 2609.11852](https://arxiv.org/abs/2609.11852)
- [NOOA — arXiv 2607.20709](https://arxiv.org/abs/2607.20709)
- [PES — arXiv 2608.27427](https://arxiv.org/abs/2608.27427)
- [TIDE — arXiv 2606.04743](https://arxiv.org/abs/2606.04743)
- [Chronicle — arXiv 2609.20625](https://arxiv.org/abs/2609.20625) · [chronicle 코드](https://github.com/theagentplane/chronicle)
- [Continual Learning 서베이 — arXiv 2608.06216](https://arxiv.org/abs/2608.06216)
- [Gemini Enterprise Agent Platform — Google Cloud 블로그](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) · [Bedrock AgentCore samples](https://github.com/awslabs/agentcore-samples)
- [openai/privacy-filter — HuggingFace](https://huggingface.co/openai/privacy-filter)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
