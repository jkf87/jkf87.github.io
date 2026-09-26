---
title: "AI 에이전트가 긴 작업에서 무너질 때 하네스부터 고쳐야 한다: 논문 4편의 부품별 설계 비교"
date: 2026-09-26
author: 한준구(코난쌤)
description: "모델을 바꾸지 않고 하네스만 고쳐서 성공률과 비용을 움직인 논문 4편을 비교했습니다. 관찰 채널, 실행 구조, 부품 선택, 컨텍스트 압축 네 축으로 정리하고 무너지는 지점별 대응 순서를 제안합니다."
tags:
  - LLM 에이전트
  - 하네스
  - AI 코딩 에이전트
  - 컨텍스트 관리
  - 벤치마크
refactor_hub_id: harness-self-improve-06
aliases:
  - posts/2026-07-30-stateact-program-state-before-pixels
  - posts/2026-08-05-longhorizon-harness-mea-loop-long-horizon-agents
  - posts/2026-09-18-coding-agent-harness-design-ablation
  - posts/2026-09-23-ai-coding-agent-context-compaction-cliffcompaction
draft: false
---

## 한눈에 보는 결론

에이전트가 긴 작업에서 무너지는 걸 모델 능력 부족으로만 설명하면 비용이 커집니다. 2026년 7~9월에 나온 논문 4편은 전부 모델을 그대로 둔 채, 에이전트를 실어 돌리는 실행 틀인 하네스의 부품 하나씩을 바꿔서 성공률과 비용을 움직였습니다.

- 관찰 채널을 바꾼 StateAct는 스크린샷 대신 코드로 프로그램 상태를 직접 읽게 했습니다. OSWorld 2.0에서 Claude Opus 4.8이 20.6%에서 26.9%(이진 성공)로 올랐고 <span style="background-color: #fff59d"><strong>작업당 비용은 약 9분의 1로 떨어졌습니다.</strong></span>
- 실행 구조를 바꾼 LongHorizon-Harness는 실행·상태 관리·감사를 분리했습니다. Qwen 3.7-Plus가 WeaveBench에서 51.8%에서 80.7%로 올랐구요.
- 부품 선택을 다룬 176개 설정의 절제 연구는 <span style="background-color: #fff59d"><strong>모든 상황에 맞는 정답 부품이 없다는 걸 보여줍니다.</strong></span> 창 예산과 모델 강도에 따라 최적이 바뀝니다.
- 컨텍스트 정책을 바꾼 CliffCompaction은 요약을 포기하고 자르기만 했습니다. <span style="background-color: #fff59d"><strong>비용 최대 50% 절감에 Terminal-Bench 성능은 유지·향상</strong></span>입니다.

핵심은 이겁니다. 모델을 교체하기 전에, 무너지는 지점에 맞는 하네스 부품부터 고르는 게 순서입니다. 아래 표와 대응 지도가 그 고르는 기준을 정리한 겁니다.

## 무엇을 비교했나

예전에 각각 따로 다뤘던 글 4편을 하나의 비교로 합쳤습니다. 2026-09-26에 네 편의 arXiv 초록 페이지를 직접 가져와 핵심 주장을 대조했고, 초록에서 확인 안 되는 본문 표 수치는 이 글에서 뺐습니다.

1. StateAct — Program State, before Pixels, for Long-Horizon Computer-Use Agents ([arXiv:2607.22798](https://arxiv.org/abs/2607.22798))
2. LongHorizon-Harness: Advancing Long-Horizon Agents for Real-World Tasks ([arXiv:2608.01964](https://arxiv.org/abs/2608.01964))
3. An Empirical Study of Harness Design for Coding Agents ([arXiv:2609.20804](https://arxiv.org/abs/2609.20804))
4. CliffCompaction: Cost-Efficient Compaction for Long-Horizon Coding Agents ([arXiv:2609.26779](https://arxiv.org/abs/2609.26779))

정정한 것도 적어둡니다. 옛 글에 있던 "Opus 4.7 OSWorld 2.0 서브셋 20.6% → 35.3%"는 초록의 <span style="background-color: #fff59d"><strong>20.0% → 34.3%</strong></span>과 달라서 초록 쪽으로 바로잡았습니다.

## 방법 비교

| 축 | 논문 (arXiv) | 무엇을 바꿨나 | 핵심 장치 | 초록으로 확인된 수치 |
|---|---|---|---|---|
| 관찰 채널 | StateAct (2607.22798) | 스크린샷 → 코드로 프로그램 상태 직접 읽기 | GUI 서브에이전트를 안전망으로 유지(108개 작업 중 28개, 메인 스텝의 1.1%만 호출), 구조 실패를 잡는 독립 finish gate | OSWorld 2.0 이진 성공 20.6→26.9%, 비용 약 9배 절감 |
| 실행 구조 | LongHorizon-Harness (2608.01964) | 한 컨텍스트 통합 → Manage-Execute-Audit 분리 | 작업 상태를 실행 밖에서 유지하고 검증된 사실로만 갱신, 읽기 전용 감사자, AgentAdapter로 기존 하네스 그대로 연결 | WeaveBench 51.8→80.7%, Terminal-Bench 2.1 69.7→77.2%, OSWorld 2.0 2.8→8.3% |
| 부품 선택 | Empirical Study (2609.20804) | 통짜 비교 → 부품별 절제 | 실행 루프를 고정하고 컨텍스트 관리·플래닝·액션 공간만 교체한 176개 매칭 설정 | 창이 빡빡할수록 컨텍스트 관리 가치 상승, 복원 장치는 거의 쓰이지 않음 |
| 컨텍스트 정책 | CliffCompaction (2609.26779) | LLM 요약 → 자르기·버리기만 | 컴팩션의 컴팩션 금지, 매번 원본에서 다시 압축해 문맥 표류 차단 | 비용 최대 50% 절감, KernelBench 400스텝 3.58배 스피드업 |

![같은 모델, 하네스만 바꿨을 때 성공률 변화](../media/llm-agent-harness-parts-design-guide-2026/chart-01-same-model-harness-gain.png)

위 차트는 블로그봇이 matplotlib 3.10.5로 직접 그린 그림입니다. 논문 figure를 가져온 게 아니고, 네 편의 초록에 적힌 수치만 넣었습니다.

### 관찰 채널: StateAct

스크린샷은 프로그램 상태의 손실 렌더링이라는 게 출발점입니다. 서로 다른 상태가 같은 픽셀을 만들 수 있어서, 완벽한 인식 모델이라도 화면만으로 원래 상태를 복원할 수 없습니다. 코드는 그 상태를 직접 읽고 고칠 수 있구요.

그래서 메인 에이전트는 코드와 구조적 조작만 다루고, 마우스·키보드가 필요한 소수 하위 목표만 전용 GUI 서브에이전트에 넘깁니다. <span style="background-color: #fff59d"><strong>GUI 조작은 108개 작업 중 28개, 메인 스텝의 1.1%에서만 호출됐습니다.</strong></span>

검증도 같은 원칙입니다. finish가 호출되면 독립 finish gate가 저장 결과를 다시 확인해서, 결과가 없거나 저장 안 됐거나 잘못된 경로에 쓰인 구조 실패를 잡습니다.

여기서 빼놓으면 안 되는 숫자가 하나 있습니다. GUI 서브에이전트를 아예 없앤 코드온리 변형은 부분 성공 45.9%로, 스크린샷 베이스라인의 54.8%보다 낮습니다. <span style="background-color: #fff59d"><strong>상태 우선 접근이 GUI 안전망 위에서만 완성된다는 뜻입니다.</strong></span>

### 실행 구조: LongHorizon-Harness

기존 하네스는 작업 실행, 작업 상태, 완료 판정을 하나의 커지는 컨텍스트 안에서 처리합니다. 저자들의 진단은 그 구조가 상태 추적을 어렵게 하고 <span style="background-color: #fff59d"><strong>잘못된 자기 평가가 이후 판단으로 그대로 전파된다는 것</strong></span>입니다.

Manage-Execute-Audit 루프는 이 세 역할을 분리합니다. 매니저는 작업 상태를 유지하며 다음 서브태스크를 정하고, 실행자는 새 컨텍스트에서 서브태스크만 수행하고, 감사자는 실행 뒤의 환경 상태를 읽기 전용으로 검증합니다. 상태는 환경에서 독립적으로 검증된 사실로만 갱신됩니다. 가벼운 AgentAdapter가 모델·하네스 백엔드를 바꿔 끼울 수 있게 해줘서, 기존 에이전트 루프를 수정하지 않고 붙일 수 있습니다.

같은 구조가 강한 모델에도 들어맞습니다. Claude Opus 4.7 기준 OSWorld 2.0 서브셋에서 20.0%에서 34.3%로 올랐습니다.

### 부품 선택: 176개 설정의 절제 연구

이 연구는 하네스를 통째로 비교하지 않고, 실행 루프를 고정한 채 세 부품(컨텍스트 관리, 플래닝, 액션 공간)만 갈아끼웠습니다. 모델 4종을 SWE-Bench Verified와 Terminal-Bench 2.1에 올려 <span style="background-color: #fff59d"><strong>176개 매칭 설정</strong></span>을 비교했구요.

초록이 정리한 발견은 실무에 바로 쓸 수 있는 형태입니다.

- 컨텍스트 관리는 창 예산이 빡빡할수록 가치가 커지고, 그 이득에서 가장 큰 몫은 오버플로 실패 방지입니다.
- 규칙 기반 생략을 LLM 요약 앞에 두는 게 효율이 가장 좋습니다. 생략한 내용을 복원 가능하게 만드는 장치는 모델이 거의 안 쓰고 정확도 이득도 없었습니다.
- 플래닝은 약한 모델에선 정확도 지지대, 강한 모델에선 <span style="background-color: #fff59d"><strong>검증 꼬리를 잘라내는 비용 절감 수단</strong></span>으로 역할이 바뀝니다.
- 미리 정의된 도구 세트는 bash가 약한 모델을 살리고, bash를 잘하는 모델은 bash-only 인터페이스로도 잘 돌아가는데 비용은 훨씬 낮습니다.

트레이젝토리 분석까지 이유를 설명합니다. 컨텍스트 관리는 실행 궤적을 길게 늘리고, 플래닝은 궤적이 멈추는 지점을 바꾸고, 액션 공간은 코드를 쓰는 단위를 바꾼다는 겁니다.

### 컨텍스트 정책: CliffCompaction

CliffCompaction의 출발은 역방향입니다. 요약이 문제라면 요약을 하지 않으면 됩니다. 압축할 때 <span style="background-color: #fff59d"><strong>내용을 다시 쓰거나 재구성하지 않고 자르거나 버리기만 합니다.</strong></span>

두 번째 규칙이 핵심 기여입니다. 컴팩션의 컴팩션을 절대 하지 않습니다. 새 컴팩션이 발동하면 이전 컴팩션 결과를 통째로 버리고 매번 원본에서 다시 압축해서, 요약이 요약을 낳는 문맥 표류가 쌓이는 경로 자체를 차단합니다.

결과는 이겁니다. bounded context에서 비용 최대 50% 절감에 Terminal-Bench 성능 유지·향상. 테스트타임 스케일링은 풀 컨텍스트 두 번 비용보다 싸게 Terminal-Bench에서 10포인트 이상을 더 얻고, Kimi K2.6가 Opus 4.7과 동급, Opus 4.6과 GPT-5.3 Codex를 넘었습니다. 세션이 100만 토큰을 넘는 KernelBench에선 200스텝 2.23배, 400스텝 3.58배 스피드업으로 전용 탐색 알고리즘·학습된 에이전트를 추월했습니다. 구현은 Claude Code, Codex 등에 붙일 수 있는 scaffold 무관 API 프록시로 공개돼 있습니다.

## 언제 무엇을 쓰나

![문제별 하네스 대응 지도](../media/llm-agent-harness-parts-design-guide-2026/chart-02-symptom-part-map.png)

위 지도도 블로그봇이 직접 그린 그림입니다. 글로 정리하면 이런 순서가 됩니다.

1. 화면 조작 에이전트인데 인식 오류와 스텝 비용이 크다 → 관찰 채널부터. 앱의 상태 저장소·파일·API로 직접 읽고 쓰게 하고, 안 되는 부분만 GUI 조작으로 남깁니다.
2. 긴 작업 중간에 길을 잃거나, 끝내지도 않았는데 끝냈다고 보고한다 → 실행 구조부터. 서브태스크마다 새 컨텍스트로 실행하고, 완료 판정은 환경을 읽는 독립 검증으로 바꿉니다.
3. 컨텍스트가 창을 넘어 세션이 터지거나 비용이 폭증한다 → 컨텍스트 정책부터. 요약 대신 규칙 기반 자르기를 먼저 넣고, 요약이 꼭 필요한 것만 뒤에 둡니다.
4. 부품을 뭘 켜야 할지 모르겠다 → 모델 강도와 창 예산으로 조건을 묶습니다. 아래 표가 그 요약입니다.

| 조건 | 먼저 켤 부품 | 뺄 후보 |
|---|---|---|
| 창 예산이 빡빡한 모델(로컬·경량 배포) | 컨텍스트 관리, 규칙 기반 생략 우선 | 복원(recall) 장치 |
| 약한 모델 | 플래닝, 미리 정의된 도구 세트 | bash-only |
| 강한 모델 + 셸 중심 과제 | bash-only 인터페이스 | 도구 세트, 과도한 검증 루프 |
| 세션이 수십만~수백만 토큰 | 자르기식 컴팩션 | LLM 요약 컴팩션 |

공통 분모도 보입니다. StateAct의 finish gate와 LongHorizon-Harness의 감사자는 둘 다 <span style="background-color: #fff59d"><strong>완료 판정을 실행한 주체에게서 떼어 놓는 독립 검증</strong></span>입니다. StateAct의 fresh 서브에이전트와 LH-Harness의 fresh-context 실행자도 같은 방향이구요. 긴 작업의 안정성은 뭘 넣느냐보다 <span style="background-color: #fff59d"><strong>실행·상태·검증을 어디까지 분리하느냐</strong></span>로 결정되는 부분이 큽니다.

## 블로그봇이 직접 확인한 것

- 2026-09-26에 네 편의 arXiv 초록 페이지를 직접 가져와서 이 글의 수치를 대조했습니다. 옛 글 수치 하나(OSWorld 서브셋 20.6→35.3)가 초록(20.0→34.3)과 달라서 바로잡았고, 초록에 없는 본문 표 수치는 뺐습니다.
- CliffCompaction 저장소([github.com/nguyenvuthientrang/cliffcompaction](https://github.com/nguyenvuthientrang/cliffcompaction))에 접속해 응답을 확인했습니다. README에서 pip·uv 설치, API 프록시 방식의 동작 안내를 확인했구요.
- 나머지 세 편은 코드를 실행하지 않았습니다. 재현 난이도와 운영 비용에 대한 실측은 이 글에 없습니다.

## 한계와 반론

- 벤치마크가 제각각입니다. OSWorld 2.0, WeaveBench, Terminal-Bench 2.1, SWE-Bench Verified, KernelBench는 서로 다른 과제라서 <span style="background-color: #fff59d"><strong>논문 간 점수를 나란히 놓고 서열을 매길 수 없습니다.</strong></span>
- 네 편 모두 각자의 기준선과 설정에서 낸 수치입니다. 같은 조건에서 네 하네스를 재비교한 결과는 없어서 "누가 최선인가"는 이 글로 답이 안 나옵니다.
- StateAct는 오디오·비디오 같은 비텍스트 상태를 다루지 않고, 프로그램 상태 접근 권한이 있다는 전제가 실무 환경에서 안 맞을 수 있습니다. 저자들도 병목이 인식에서 추론으로 이동했다고 적습니다. 하네스로 다 되는 게 아니라는 솔직한 진단입니다.
- LongHorizon-Harness는 파일·메타데이터처럼 검증 가능한 환경 상태에 최적화돼 있고, 주관적 품질 기준이 섞인 작업엔 그대로 못 옮깁니다.
- CliffCompaction은 recall을 줄인 설계라 <span style="background-color: #fff59d"><strong>오래된 원문을 정확히 인용해야 하는 작업에는 부적합</strong></span>합니다. 툴 호출로 다시 읽을 수 있는 워크플로에 맞춰져 있습니다.
- 이 글의 재확인은 초록 수준입니다. 본문 표의 세부 수치와 구현 디테일은 원문을 직접 확인해야 합니다.

## 교실·업무에 적용한다면

수업 준비나 사무 자동화에 에이전트를 쓰고 있다면 이렇게 시작하면 됩니다.

완료 판정부터 바꿔보세요. 에이전트가 "끝냈습니다"라고 하면 믿지 말고, 결과 파일이 있는지, 빌드가 통과하는지, 시트의 해당 셀이 채워졌는지를 별도 확인으로 검사합니다. 스프레드시트 체크리스트 하나로도 충분합니다.

긴 작업은 쪼개서 새 컨텍스트로 돌립니다. 실행 기록을 통째로 끌고 가지 말고, 서브태스크별로 목표와 수락 기준만 넘기고, 검증된 결과만 다음 단계에 남깁니다.

컨텍스트 비용이 걱정되면 요약부터 넣지 말고 자르기부터 넣습니다. 오래된 실행 로그는 규칙으로 잘라내고, 원본이 필요하면 다시 읽게 하는 게 싸고 견고합니다.

도구는 쓰는 모델에 맞춥니다. 작은 로컬 모델에는 정해진 도구 몇 개를 알려주고, 큰 모델은 셸 하나로 두는 게 비용 면에서 유리한 경우가 많습니다.

오픈클로로 이걸 하신다면 검증 게이트·컴팩션 임계값·서브에이전트 분리를 설정과 스킬 파일로 붙인다고 보시면 됩니다.

## 자주 묻는 질문

### 하네스를 고치는 게 모델을 바꾸는 것보다 낫다는 건가요?
그렇게 주장하는 게 아닙니다. 네 편 모두 "같은 모델에서도 부품 하나로 수치가 이만큼 움직인다"는 쪽의 증거입니다. 모델 교체와 하네스 수정은 독립적인 선택지고, 순서를 하네스 먼저로 잡자는 얘기입니다.

### 컨텍스트 관리는 그냥 항상 켜면 안 되나요?
켜 놓고 손해 볼 건 초록에서 확인되지 않습니다. 다만 창이 넉넉한 강한 모델에선 이득 폭이 작아지니, 비용 대비로 우선순위를 정하면 됩니다.

### 요약 없이 잘라내면 필요한 정보를 잃지 않나요?
잃을 수 있습니다. 그래서 CliffCompaction은 짧은 툴 결과는 남기고, 긴 결과는 다시 툴 호출로 복구 가능한 것만 버립니다. 오래된 원문 인용이 핵심인 작업이라면 이 방식은 안 맞습니다.

### 네 방식을 전부 한 에이전트에 얹을 수 있나요?
충돌 없이 조합 가능한 조각이 있습니다. 독립 검증(finish gate·감사자)과 자르기식 컴팩션은 함께 쓸 수 있습니다. 근데 관찰 채널 변경은 작업 환경이 프로그램 상태에 접근할 수 있어야 하고, 부품 선택은 모델마다 다시 정해야 합니다.

## 참고 자료

1. Program State, before Pixels, for Long-Horizon Computer-Use Agents — [arXiv:2607.22798](https://arxiv.org/abs/2607.22798)
2. LongHorizon-Harness: Advancing Long-Horizon Agents for Real-World Tasks — [arXiv:2608.01964](https://arxiv.org/abs/2608.01964)
3. An Empirical Study of Harness Design for Coding Agents — [arXiv:2609.20804](https://arxiv.org/abs/2609.20804)
4. CliffCompaction: Cost-Efficient Compaction for Long-Horizon Coding Agents — [arXiv:2609.26779](https://arxiv.org/abs/2609.26779), [코드(github.com/nguyenvuthientrang/cliffcompaction)](https://github.com/nguyenvuthientrang/cliffcompaction)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
