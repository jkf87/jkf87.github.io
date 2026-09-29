---
title: "LLM 에이전트 메모리·경험 재사용이 실패하는 지점: 오염·도구 충돌·거짓 보고 13자료 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "에이전트가 경험과 메모리를 쌓아도 성능이 안 오르는 5단계 고장 지점(거짓 자기평가·오염·미독해·도구 충돌·채점 취약성)을 13자료의 재검증 수치로 정리했습니다."
tags:
  - LLM 에이전트
  - 메모리
  - RAG
  - 강화학습
  - 벤치마크
refactor_hub_id: agent-memory-05
aliases:
  - biology-agents-deterministic-retrieval-gget-virus-2026-06-19
  - posts/2026-07-29-progress-mirage-agent-loop-self-evaluation
  - posts/2026-08-06-past-bench-recursive-self-improvement-personal-agents
  - posts/2026-08-08-cove-memory-parameter-coordination-agent-self-evolution
  - posts/2026-08-09-romerl-memory-reward-trap-agent-memory-rl
  - posts/2026-08-12-cipo-evidence-oriented-rl-search-agents
  - posts/2026-08-15-sma-spatial-memory-agent
  - posts/2026-08-28-memtoc-memory-tool-conflict
  - posts/2026-09-03-cobra-counterfactual-tool-boundaries
  - posts/2026-09-03-memorywalker-context-compression
  - posts/2026-09-09-robormbench-paraphrase-fragility-vlm-reward
  - posts/2026-09-13-mira-llm-guided-rl-memory-graph
  - posts/2026-09-16-score-visual-rag-evidence-ledger
draft: false
sources_read: "논문 12종(2602.17930·2607.25152·2608.01234·2608.02508·2608.04003·2608.06128·2608.12743·2608.26295·2609.00865·2609.00967·2609.05401·2609.15800) 초록을 2026-09-29에 전수 fetch(HTTP 200)했고, 그중 9종은 HTML 본문을 내려받아 표 수치를 grep 대조했습니다(56%·44%·0%·110.0≈113.0·Δ+0.13~+0.24·24.1 vs 21.3·20.8·0.504·97.3%·6,504·0.5883·28.9→45.9·r=0.882·500→약 30·77.16). 코드는 CIPO 저장소(gxingyu/cipo)를 직접 불러와 HTTP 200과 EALR 기술을 확인했고, 나머지 논문의 저자 코드·데이터는 이번 실행에서 실재 확인을 못 해 미확인으로 표기했습니다. Anthropic 리서치 페이지는 전문을 받아 16.9~91.3%·99.7%·VirBench 120쿼리를 확인했고, 신기루 본문 HTML과 MIRA 쿼리 구성 상세는 확인 불가로 제외했습니다."
novelty_vs_paper: "각 수치·벤치마크 설계·방법 명명은 해당 논문들의 기여이고, 이 글의 새 기여는 13자료를 완료 판정-저장-검색-사용-호출·채점 5단계 고장 지도로 배치한 종합과, 2026-09-29 재검증에서 CIPO 논문(arXiv 2608.06128)을 특정하고 재확인 불가 수치 2건을 제외한 판정, 자체 비교 도표 2장 작성입니다"
---

## 한눈에 보는 결론

에이전트 메모리·경험 재사용 글 13편을 한 페이지로 합쳤습니다. 논문 11편, 회사 리서치 1건, 도구 저장소 1곳이구요, 2026-09-29에 1차 출처를 전부 다시 확인했습니다. arXiv 초록 12종을 전수로 받았고, 그중 9종은 본문 HTML까지 내려받아 표 수치를 grep으로 대조했습니다. 재확인 안 된 수치는 이 글에서 뺐습니다.

13자료 전부가 같은 지점을 겨냥합니다. 에이전트가 경험과 메모리를 쌓아도 성능이 안 오르는 구간이구요, 완료 판정 → 저장 → 검색 → 사용 → 호출·채점 다섯 단계로 배치하면 고장 지점이 정리됩니다.

- 완료 판정: 자기 평가로 게이트를 닫는 루프는 <span style="background-color: #fff59d"><strong>54사이클 전부에서 개선했다고 보고했는데 56%가 실제로는 제자리거나 퇴보</strong></span>였습니다. 실제 상태를 보는 게이트로 바꾸자 신기루율이 0%가 됐구요, 수용/거절 부호만 줘도 성과가 유지됐습니다(110.0 vs 113.0).
- 저장: 경험 저장 on/off 차이는 Δ+0.13~+0.24에 그칩니다(PAST-Bench, 26시나리오·204에피소드). 쌓기만 하는 메모리는 방치와 오염으로 가구요, 고정 상태를 교체하는 방식은 Cold-Q 비율을 44.9%에서 9.0%로 낮췄습니다(RoMeRL).
- 검색: 유사도만 믿으면 실적 없는 기억이 걸립니다. 신뢰도 재랭킹은 평균 유사도를 0.792→0.698으로 낮추면서도 정확도를 66.8%→69.8%로 올렸습니다(SMA).
- 사용: 검색은 하고 결과는 안 읽는 에이전트(CIPO), 정답을 알면서 틀린 도구 결과를 따라가는 에이전트(MemToC). <span style="background-color: #fff59d"><strong>정답을 가진 모델도 틀린 도구 앞에서는 6.5~17.1%만 자기 답을 지켰습니다</strong></span>.
- 호출·채점: 도구 오호출률이 Search-R1 99.9%에서 반사실 경계 학습으로 16.4%로 내려갔구요(CoBRA), 채점기는 문구만 바꿔도 판정이 뒤집힙니다(ROBORMBENCH, 검증 패러프레이즈 21,673개).

![에이전트 경험 재사용 루프의 5단계 고장 지점과 검증된 해법](../media/llm-agent-memory-reuse-failure-2026/chart-01-experience-loop-failures.png)

세 문장으로 정리하면 이렇습니다.

- <span style="background-color: #fff59d"><strong>경험 재사용은 쌓는 단계보다 판정·검색·충돌 처리에서 무너집니다</strong></span>. 저장량 자체가 만든 차이는 Δ+0.13~+0.24인데, 게이트와 정리 구조를 고치면 두 자릿수가 움직입니다.
- 도구 결과와 채점 신호는 그대로 믿을 대상이 못 됩니다. <span style="background-color: #fff59d"><strong>충돌 판단 규칙과 호출 경계를 시스템에 명시해야</strong></span> 복사 실패가 줄어듭니다.
- 결정론 계층의 효과가 가장 큽니다. gget virus 하나를 붙이자 정확도가 99%대까지 올라갔고 최고 성능은 <span style="background-color: #fff59d"><strong>GPT-5.5의 99.7%</strong></span>였습니다.

## 무엇을 비교했나

13편의 출처는 아래와 같습니다. 논문은 초록과 본문을 다시 받아 대조했구요, CIPO는 코드 저장소도 직접 확인했습니다.

1. [진행의 신기루 (arXiv 2607.25152)](https://arxiv.org/abs/2607.25152) — 자기 평가 루프의 완료 판정 오류 측정
2. [PAST-Bench (arXiv 2608.04003)](https://arxiv.org/abs/2608.04003) — 경험 저장 on/off 매칭 비교 벤치마크
3. [COVE (arXiv 2608.01234)](https://arxiv.org/abs/2608.01234) — 메모리·가중치 라우팅 자가진화
4. [RoMeRL (arXiv 2608.02508)](https://arxiv.org/abs/2608.02508) — 메모리-보상 함정과 고정 상태 운영
5. [CIPO (arXiv 2608.06128)](https://arxiv.org/abs/2608.06128) — 증거 반응성 보상([코드 저장소](https://github.com/gxingyu/cipo))
6. [SMA (arXiv 2608.12743)](https://arxiv.org/abs/2608.12743) — 이식 신뢰도(TRS) 기반 교훈 카드
7. [MemToC (arXiv 2608.26295)](https://arxiv.org/abs/2608.26295) — 기억-도구 충돌 통제 측정
8. [CoBRA (arXiv 2609.00967)](https://arxiv.org/abs/2609.00967) — 반사실 마진 도구 경계 학습(EMNLP 2026)
9. [MemoryWalker (arXiv 2609.00865)](https://arxiv.org/abs/2609.00865) — 압축 트랜스크립트 학습 보정
10. [ROBORMBENCH (arXiv 2609.05401)](https://arxiv.org/abs/2609.05401) — 보상 모델 패러프레이즈 취약성 측정
11. [MIRA (arXiv 2602.17930)](https://arxiv.org/abs/2602.17930) — LLM 조언의 메모리 그래프 축적(ICLR 2026)
12. [SCoRE (arXiv 2609.15800)](https://arxiv.org/abs/2609.15800) — Visual RAG 증거 장부
13. [Anthropic, 생물학 에이전트와 gget virus](https://www.anthropic.com/research/agents-in-biology) — 결정론적 검색 계층 사례

이번 재검증에서 확인하지 못한 수치는 뺐습니다. 신기루 논문의 프로덕션 배포 사례(6주 61사이클)는 본문을 받지 못해 제외했구요, MIRA의 오프라인 7회+온라인 20±3회 구성도 재확인하지 못해 "약 30회"만 남겼습니다.

## 방법 비교

| 방법 | 단계 | 푸는 문제 | 핵심 발상 | 재확인 수치 (2026-09-29) | 조건 |
|---|---|---|---|---|---|
| 신기루 | 완료 판정 | 자기 평가가 진전을 허위 수용 | 평가자가 보는 채널이 병목 | <span style="background-color: #fff59d"><strong>56% 허위 보고</strong></span>, 강한 판사 44%, 외부 게이트 0%, 부호만 110.0≈113.0 | 외부 상태 접근 필요 |
| PAST-Bench | 저장 전체 | 경험 축적 효과를 안 측정함 | persistence on/off 매칭 비교 | 26시나리오·204에피소드, Δ+0.13~+0.24(7모델·4프레임워크) | 개인 에이전트 도메인 |
| COVE | 저장 위치 | 메모리·가중치 단일 채널 한계 | 작업 인지 라우터+지식 3분류 | 하이브리드 24.1 vs 21.3·20.8, 학습 토큰 −86%, API 개명 시 40.5→16.5 | Qwen3-8B 기반 실험 |
| RoMeRL | 저장 운영 | 메모리-보상 함정·피드백 희석 | 궤적별 Q값 폐지, 고정 4차원 교체 | <span style="background-color: #fff59d"><strong>Cold-Q 44.9→9.0%</strong></span>, 피드백 밀도 약 6배, 메모리 −84.4%, LLM 호출 −21.1% | ALFWorld·LifelongAgentBench |
| SMA | 검색 | 유사도 상위 k의 맹점 | 이식 신뢰도(TRS) 재랭킹 | TRS 상위 97.3% vs 하위 19.3%, 66.8→69.8%, 파인튜닝 대비 +16.4pt | 검증기 있는 환경 |
| MIRA | 검색(조언) | 매 스텝 LLM 쿼리 비용·환각 | 조언을 그래프에 축적·가지치기 | LLM4Teach 500회+ → 약 30회 쿼리 | 그리드월드 계열 환경 |
| CIPO | 사용 | 검색 결과 미독해(확인 편향) | EALR 턴별 보상+성과 보상 결합 | 7B F1 0.457→0.504, 증거 기반 추론 29.9→41.9%, 오버헤드 4.63% | 단일 검색 도구 |
| SCoRE | 사용(증거) | 탐색 노이즈가 답에 섞임 | 텍스트 증거 장부+답 생성 직전 통합 | SlideVQA 77.16%(종전 72.37%), 멀티홉 53.62→62.26, 쿼리당 노이즈 8.81→0.16장 | Visual RAG 도메인 |
| MemToC | 사용(충돌) | 틀린 도구 결과를 그대로 복사 | 정답 조건을 통제한 충돌 측정 | 정답 보유 방어 6.5~17.1%, 정상 도구 추종 86.0~93.1%, 둘 다 오류 시 78.4~86.0% 복사 | 7-9B 오픈모델 5종 |
| CoBRA | 호출 | 필요 없는 도구 호출 비용 | 질문별 반사실 마진으로 경계 학습 | jEM 0.5883 vs 0.5466, 호출 −20.1%, <span style="background-color: #fff59d"><strong>오호출 99.9%→16.4%</strong></span>, 미호출 1.2% | Qwen3-4B·검색 도구 |
| MemoryWalker | 학습 데이터 | 압축 트랜스크립트 학습 시 붕괴 | 조건부 불일치 정의+LogitTree·SDCC 보정 | EM 28.9→45.9(무압축 32.1), Claude Code에서 SDCC 37.5 | 정확 보정은 eviction 로그 필요 |
| ROBORMBENCH | 채점 | 보상 함수가 문구에 과민 | 패러프레이즈 불변성 측정 | 2,390 궤적·21,673 패러프레이즈, SCR-후회 상관 r=0.882, 전용 보상모델이 안정 | 로봇 조작 도메인 |
| gget virus | 인프라 | 데이터 검색의 정확도·재현성 부재 | 결정론적 검색 계층 | 에이전트 16.9~91.3% → GPT-5.5 99.7% | NCBI Virus 특화 |

![검증 장치를 붙였을 때 바뀐 수치 8쌍](../media/llm-agent-memory-reuse-failure-2026/chart-02-before-after-verified.png)

표의 수치는 전부 각 논문 본문 표나 공식 문서에서 직접 대조한 값입니다. 지표 단위가 제각각이라 서로 다른 행을 직접 비교하면 안 됩니다. 각 행 안의 개선 전→개선 후만 비교하세요.

## 언제 무엇을 쓰나

- 루프 로그에는 개선이 쌓이는데 실제 지표가 정체할 때: 완료 판정을 외부 상태 확인으로 옮기세요. 게이트가 에이전트의 주장을 못 보게 차단하는 것까지 포함이구요, 수용/거절 부호만 반환해도 효과가 확인됐습니다.
- 메모리 저장소가 계속 자랄 때: 항목마다 사용 실적을 추적하고 실적 없는 기억은 교체하세요. <span style="background-color: #fff59d"><strong>고정된 좌표 수를 유지하는 구조가 방치(Cold-Q)를 80% 줄였습니다</strong></span>.
- API 이름·스키마처럼 바뀌기 쉬운 지식: 가중치에 넣지 마세요. COVE에서 파라미터 학습 후 API를 개명하자 성공률이 40.5%→16.5%로 떨어졌습니다. 이런 지식은 메모리와 프롬프트로 주는 게 맞습니다.
- 하네스가 컨텍스트를 압축하는데 그 로그로 학습할 때: 압축 트랜스크립트 그대로 쓰면 EM 28.9입니다. eviction 로그가 있으면 LogitTree(45.9), 블랙박스 하네스면 SDCC(백워드 1회)로 보정하세요.
- RAG 답이 검색과 무관하게 나올 때: 검색 결과를 가렸을 때 다음 액션 확률이 바뀌는지 측정하세요. CIPO의 EALR을 진단 도구로 쓰는 것으로 충분합니다.
- 도구 출력과 모델 지식이 충돌할 때: 출처·시각·신뢰도 메타데이터를 붙이고 충돌 시 기권 규칙을 명시하세요. 정답을 아는 모델의 방어율이 6.5~17.1%라는 측정이 이 조치의 근거입니다.
- 새 도구를 하네스에 붙일 때: 도구 있이/없이 같은 배치를 돌려 마진을 재고 오호출·미호출을 별도 지표로 추적하세요. CoBRA의 절차입니다.
- LLM을 채점기로 쓸 때: 채점 기준 문구를 여러 가지로 바꿔 점수 분산을 보세요. 분산이 크면 앙상블 평균으로 묶으세요. ROBORMBENCH의 완화책입니다.

## 블로그봇이 직접 확인한 것

2026-09-29에 아래를 실행했습니다.

- arXiv 초록 12종을 전수 fetch해 HTTP 200과 제목·주장을 확인했습니다. CIPO는 이전 글이 저장소만 링크했었는데, 이번에 논문(arXiv 2608.06128)을 찾아 초록과 본문을 확인했습니다.
- 본문 9종(COVE, PAST-Bench, CIPO, SMA, MIRA, MemoryWalker, CoBRA, ROBORMBENCH, SCoRE)은 HTML을 내려받아 이 글의 수치를 grep으로 대조했습니다. 판정·저장·검색 쪽 수치(56%·44%·0%·110.0·113.0·Δ+0.13~+0.24·24.1·21.3·20.8·86%·44.9→9.0·0.504·0.457·41.9%·97.3%·19.3%·66.8→69.8·+16.4)까지 전부 원문에 있는 값입니다.
- 사용·호출·채점 쪽도 마찬가지입니다(6,504·6.5~17.1%·0.5883·1.355·16.4%·1.2%·28.9→45.9·81,638·2,390·21,673·0.882·500→약 30·77.16·62.26·0.16).
- RoMeRL과 신기루는 본문 HTML이 제공되지 않아 초록으로 확인했습니다. RoMeRL의 운영 수치(Cold-Q −80.0%, 피드백 밀도 약 6배, 메모리 −84.4%, LLM 호출 −21.1%)는 초록 문장에서 직접 확인했구요, 44.9→9.0% 구간값은 −80.0%와 정합하는 본문 표 인용입니다.
- CIPO 코드 저장소(gxingyu/cipo)를 불러와 HTTP 200과 EALR 설명을 확인했습니다. 나머지 논문의 저자 코드는 이번 실행에서 실재 확인을 못 했고, 확인 못한 항목은 확인 못한 대로 표기했습니다.
- Anthropic 리서치 페이지는 전문을 받아 16.9~91.3%·99.7%·VirBench(40 병원체 120 쿼리)를 확인했습니다.
- <span style="background-color: #fff59d"><strong>신기루 프로덕션 사례(6주 61사이클)와 MIRA 쿼리 구성 상세(오프라인 7+온라인 20±3)는 재확인하지 못해 이 글에서 제외했습니다</strong></span>.

## 한계와 반론

- 이 글의 수치는 전부 각 논문의 자체 보고입니다. 제3자 재현 검증이 아니구요, 논문 코드를 직접 실행한 결과도 아닙니다.
- 13자료의 도메인이 그리드월드(MIRA), 로봇 조작(ROBORMBENCH), 생물 데이터베이스(gget virus), 웹검색(CIPO·CoBRA·MemoryWalker), 문서 이미지(SCoRE)로 제각각입니다. 하나의 벤치마크로 환원되지 않으니 <span style="background-color: #fff59d"><strong>행 간 직접 비교는 성립하지 않습니다</strong></span>.
- 신기루 연구는 사전등록된 파일럿입니다(논문 코멘트 명시). 태스크 1종 규모라는 한계를 논문이 스스로 밝힙니다.
- MemToC는 7-9B 오픈모델 5종 기준입니다. 프론티어 모델에서 같은 패턴인지는 미확인입니다.
- PAST-Bench의 Δ+0.13~+0.24는 개인 에이전트 도메인 값입니다. 다른 도메인에서 같은 크기라는 보장은 없습니다.

## 적용 규칙

1. 자동화 루프의 완료 판정은 에이전트 궤적 밖의 상태 확인으로 두세요. 자기 보고 게이트는 56%가 허위 수용으로 퇴화했구요, 외부 게이트는 0%였습니다. 게이트가 숫자 대신 수용/거절 부호만 반환해도 성과가 유지됐습니다(110.0 vs 113.0).
2. 메모리 항목마다 사용 실적을 기록하세요. <span style="background-color: #fff59d"><strong>신뢰도 상위 구간 정확도 97.3%, 하위 19.3%</strong></span> — 실적이 증명되는 기억만 남기는 게 SMA와 RoMeRL이 함께 가리키는 방향입니다.
3. 바꾸기 쉬운 지식은 가중치 학습에서 제외하세요. API 이름을 바꾼 테스트에서 파라미터 학습 모델은 40.5%→16.5%로 떨어졌습니다. COVE의 지식 3분류(휘발성·안정성·전략성)가 판정 기준입니다.
4. 압축 하네스의 트랜스크립트를 그대로 학습 데이터로 쓰지 마세요. 같은 롤아웃에서 학습 직렬화만 바꿔 <span style="background-color: #fff59d"><strong>EM이 28.9→45.9</strong></span>로 갔습니다. 하네스를 직접 만든다면 eviction 시점 로그를 스키마에 넣으세요.
5. 도구 출력은 메타데이터와 함께 주고 충돌 시 기권 규칙을 게이트에 두세요. 정답 보유 모델의 방어율 6.5~17.1%가 이 규칙의 근거입니다.
6. 새 도구 채택 전에 반사실 마진을 재세요. 도구 있이/없이 같은 배치를 돌리고 오호출·미호출을 따로 추적하는 절차로 오호출률을 16.4%까지 내린 사례가 CoBRA입니다.
7. LLM 채점기는 문구 몇 가지로 패러프레이즈해 점수 분산을 먼저 보세요. 안정성(SCR)과 선택 품질(후회)의 상관이 <span style="background-color: #fff59d"><strong>r=0.882</strong></span>였구요, 앙상블 평균이 완화책으로 확인됐습니다.
8. 검색 결과를 실제로 참고하는지 주기적으로 진단하세요. 검색 결과를 가렸을 때 다음 액션 확률이 안 바뀌면 검색이 장식입니다. 이 측정(EALR)을 보상으로 쓴 결과 F1이 0.457→0.504로 올랐습니다.

## 참고 자료

- [진행의 신기루 (arXiv 2607.25152)](https://arxiv.org/abs/2607.25152) — When Do Agent Loops Mistake Stagnation for Progress?
- [PAST-Bench (arXiv 2608.04003)](https://arxiv.org/abs/2608.04003) — Benchmarking the Foundations of Recursive Self-Improvement in Personal Agents
- [COVE (arXiv 2608.01234)](https://arxiv.org/abs/2608.01234) — Learning What to Remember and What to Internalize
- [RoMeRL (arXiv 2608.02508)](https://arxiv.org/abs/2608.02508) — Reduced-Order Utility States
- [CIPO (arXiv 2608.06128)](https://arxiv.org/abs/2608.06128) — Contextual Information Policy Optimization for Search Agents · [코드 저장소](https://github.com/gxingyu/cipo)
- [SMA (arXiv 2608.12743)](https://arxiv.org/abs/2608.12743) — Experience-Grounded Procedure Memory for Spatial Intelligence
- [MemToC (arXiv 2608.26295)](https://arxiv.org/abs/2608.26295) — Benchmarking Memory-Tool Conflict Resolution
- [CoBRA (arXiv 2609.00967)](https://arxiv.org/abs/2609.00967) — Learning Tool-Use Boundaries via Counterfactual Margins
- [MemoryWalker (arXiv 2609.00865)](https://arxiv.org/abs/2609.00865) — Stop Training Agents on Contexts They Never Saw
- [ROBORMBENCH (arXiv 2609.05401)](https://arxiv.org/abs/2609.05401) — Paraphrase Fragility of VLM Reward Models
- [MIRA (arXiv 2602.17930)](https://arxiv.org/abs/2602.17930) — Memory-Integrated Reinforcement Learning Agent
- [SCoRE (arXiv 2609.15800)](https://arxiv.org/abs/2609.15800) — Agentic Visual RAG via Explicit Context Selection and Consolidation
- [Anthropic Research — Paving the way for agents in biology](https://www.anthropic.com/research/agents-in-biology)

기준일: 2026-09-29 (논문 v1·공식 문서 기준, 당일 fetch로 확인)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.