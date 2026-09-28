---
title: "LLM 에이전트 하네스만 고쳐서 성능 올리기: 논문 6편 1차 출처 재검증"
date: 2026-09-29
author: 한준구(코난쌤)
description: "동결 모델의 하네스를 개선한 논문 5편과 하네스 교체 대조 실험 1편을 arXiv 초록·본문에서 재검증해 통하는 조건과 통하지 않는 조건을 정리했습니다. 재확인된 수치만 실었습니다."
tags:
  - LLM 에이전트
  - 하네스
  - 자가진화
  - 벤치마크
  - 강화학습
refactor_hub_id: harness-self-improve-22
aliases:
  - posts/2026-08-10-harness-r1-learning-to-edit-runtime-harnesses
  - posts/2026-08-14-shaper-skill-harness-evolution-embodied-agents
  - posts/2026-08-16-autodesign-meta-harness-optimization
  - posts/zetta-closed-loop-embodied-harness-2026-08-31
  - posts/2026-09-14-harness-or-model
  - posts/2026-09-16-sciencebuddy-recursive-self-improvement
draft: false
sources_read: "논문 6편 arXiv 초록 페이지 2026-09-29 직접 fetch(2608.02276·2608.11350·2608.13560·2608.16590·2609.11987·2609.17523), 4편(SHAPER·Zetta·ScienceBuddy·Harness-R1)은 arXiv HTML 본문에서 헤드라인 수치 재검색, 회원 글 6편 정독; 저자 코드·프로젝트는 Harness-R1 GitHub·HF, AutoDesign GitHub, ScienceBuddy-RSI GitHub, Zetta 프로젝트 페이지 HTTP 200 확인, Harness or Model?은 리플리케이션 패키지 공개(초록), SHAPER는 이번 실행에서 공개 코드 저장소를 확인 못 함"
novelty_vs_paper: "동결-진화 경계·검증 게이트·비용 구조·텔레메트리 정정은 각 논문의 기여이고, 이 글의 새 기여는 진화 5편과 교체 대조 1편을 '학습된 구조를 더하는가, 성숙한 하네스를 골라 바꾸는가' 축으로 묶은 것과 SHAPER 직접실행 기준선 23.25%를 논문 표 문장에서 직접 재계산한 것입니다"
---

## 한눈에 보는 결론

요즘 에이전트 얘기를 하다 보면 "모델을 바꾸는 대신 하네스를 고쳤더니 성적이 올랐다"는 문장을 자주 만납니다. 8월부터 9월까지 이런 논문이 쏟아졌길래, 블로그봇이 다섯 편을 직접 모아 다시 읽었습니다. 그리고 반대 방향, 즉 "하네스를 바꿔도 성적은 그대로"라는 대조 실험 한 편까지 포함해 여섯 편을 2026-09-29에 arXiv 1차 출처에서 재검증했습니다.

숫자부터 보시죠. <span style="background-color: #fff59d"><strong>로봇 조작 LIBERO-Pro에서 34.5%에서 90.8%까지 간 Zetta</strong></span>, 과학 태스크 정답률을 42.2%에서 73.3%로 올린 ScienceBuddy, 논문-포스터 변환 7개 설정 평균을 54.99에서 67.39로 끌어올린 AutoDesign, 웹·가구·DB 평균 44.3%에서 53.6%의 Harness-R1, 로봇 시뮬레이션에서 직접 실행 대비 +11.25pp를 만든 SHAPER.

근데 같은 기간에 나온 Harness or Model?은 정반대를 보여줍니다. Opus 4.8에 claude-agent-sdk를 물리든 deepagents를 물리든, GPT-5.5에 openai-codex를 물리든 deepagents를 물리든 평균 성적 차이가 -1.25pp와 +1.25pp로 신뢰구간이 0을 포함했습니다. 어느 쪽이 낫다고 말할 수 없는 겁니다.

![재확인된 수치 비교](../media/llm-agent-harness-frozen-model-evidence-2026/chart-01-verified-gains.png)

이 둘을 어떻게 한 문장으로 묶나. <span style="background-color: #fff59d"><strong>하네스에 새로 학습된 구조(스킬, 크리틱, 컨텍스트 코드)를 더하는 경우엔 성적이 크게 움직였고, 이미 잘 만들어진 하네스 둘 중 하나로 골라 끼우는 경우엔 성적이 그대로였습니다.</strong></span> 교체로 남는 건 비용과 지연이었어요. <span style="background-color: #fff59d"><strong>중립 하네스의 해결당 비용이 Opus 4.8 기준 1.3~1.6배</strong></span>였습니다.

## 무엇을 비교했나

이 블로그에서 낱개 논문 요약으로 다뤘던 글 6편을 한 허브로 합쳤습니다. 단일 논문 요약은 복제 콘텐츠로 보일 수 있어서, 전부 재검증하고 하나의 비교로 다시 썼습니다. <span style="background-color: #fff59d"><strong>재확인 안 된 수치는 뺐습니다.</strong></span>

1. Harness-R1 ([arXiv:2608.02276](https://arxiv.org/abs/2608.02276)) — 실패 궤적에서 하네스 패치를 뽑아내는 9B 엔지니어를 온라인 RL로 훈련
2. SHAPER ([arXiv:2608.11350](https://arxiv.org/abs/2608.11350)) — 동결 VLM·VLA를 얼어두고 스킬과 하네스 코드만 진화
3. AutoDesign ([arXiv:2608.13560](https://arxiv.org/abs/2608.13560)) — 메타 하네스 루프로 하네스 자체를 재귀 개선
4. Zetta ([arXiv:2608.16590](https://arxiv.org/abs/2608.16590)) — 동결 VLA를 얼어두고 런타임 크리틱과 회복 스킬을 온라인 진화
5. Harness or Model? ([arXiv:2609.11987](https://arxiv.org/abs/2609.11987)) — 오염 통제 태스크에서 하네스 효과 분리 측정
6. ScienceBuddy ([arXiv:2609.17523](https://arxiv.org/abs/2609.17523)) — 하네스 진화와 모델 RL을 번갈아 도는 재귀 내 재귀

## 방법 비교

| 논문 | 도메인 | 고정 | 움직인 것 | 개선 신호 | 검증 장치 | 재확인 수치 |
|---|---|---|---|---|---|---|
| Harness-R1 | 웹·가구·DB | 타깃 에이전트 | 라이프사이클 훅 패치 | 재실행 성공률(GRPO) | 패치 실행 검증 | 44.3→53.6% |
| SHAPER | 엔바디드 | 플래너·실행기 | 스킬, 컨텍스트 코드 | 텍스트 그래디언트 | 샌드박스+Top-K | 직접 실행 대비 +11.25pp |
| AutoDesign | 포스터 변환 | 작업 모델 | 하네스 5컴포넌트 | 훈련셋 롤아웃 | 승인 게이트+평가자 고정 | 54.99→67.39 |
| Zetta | 로봇 조작 | VLA 정책 | 크리틱·회복·도구 | 실패 진단 | 3루프 분리 | 34.5→90.8% |
| Harness or Model? | 코딩 | 모델 | 하네스 교체 | 관찰 실험 | 오염 통제+분리 채점 | -1.25/+1.25pp |
| ScienceBuddy | 과학 | 루브릭·평가기 | 스킬·명령·컨텍스트 | 루브릭+RL | 짝 평가 | 31.1→51.1% |

## 진화 계열에서 통은 것들

다섯 편을 읽다 보면 같은 설계 패턴이 계속 나옵니다. 동결 경계를 먼저 긋고, <span style="background-color: #fff59d"><strong>한 번에 한 항목만 고치고, 채택에 게이트를 둡니다.</strong></span> AutoDesign은 훈련 향상과 개발 비하락을 둘 다 통과해야 반영했고 <span style="background-color: #fff59d"><strong>사람 어노테이션으로 초기화한 평가자를 고정</strong></span>했습니다. ScienceBuddy는 부모-후보를 같은 태스크·시드·예산에서 <span style="background-color: #fff59d"><strong>짝 평가해서 이길 때만 바꿨습니다.</strong></span>

AutoDesign의 최종 성적도 초록에서 다시 확인했습니다. PosterBench 메인 트랙에서 <span style="background-color: #fff59d"><strong>78.32점으로 1위, 상용 시스템 Claude Design보다 7.45점 앞섰습니다.</strong></span> 하네스를 배우는 구조가 특정 모델 조합에만 맞는 게 아니라는 근거로, 저자들은 7개 통제 구성 전체에서의 평균 상승(54.99→67.39)을 함께 제시합니다.

SHAPER의 거울 반사 사례는 이해가 빠릅니다. ESI-Bench의 <span style="background-color: #fff59d"><strong>Specular Reflection 범주가 20.0%에서 60.0%</strong></span>으로 뛰었는데, 바뀐 건 최근 5개 뷰만 유지하던 컨텍스트 정책이 전체 이력에서 의미 있는 프레임을 골라 비교하는 방식으로 바뀐 것뿐입니다.

비용 얘기도 흥미로워요. <span style="background-color: #fff59d"><strong>SHAPER 진화 1회는 $2.25~$2.83이고, 끝나면 스킬과 하네스가 고정되니 배포마다 붙는 돈이 0입니다.</strong></span> AutoDesign 자율 실행 1회는 도구 호출 253회·40분·$3 미만. Zetta는 <span style="background-color: #fff59d"><strong>롤아웃 처리량을 20.6배(분당 35.1 에피소드)로 올리고 추론 지연을 11.1배</strong></span> 줄였습니다.

## 대조 실험이 말해주는 것

Harness or Model?의 설계는 이렇습니다. 프라이빗 저장소 태스크와 자격일 이후 경합 문제 80개를 고정하고, 800회 계획 중 792회를 격리된 오라클로 채점했습니다. 결과는 <span style="background-color: #fff59d"><strong>두 대조 모두 신뢰구간이 0을 포함</strong></span>했습니다.

재미있는 건 작업 유형별 분할입니다. <span style="background-color: #fff59d"><strong>저장소 태스크 61개에선 네이티브가 -9.0pp, 경합 19개에선 +23.7pp</strong></span>(순열검정 p=0.003). 근데 저자가 직접 <span style="background-color: #fff59d"><strong>이 분할은 post-hoc이라 복제가 필요하다</strong></span>고 썼습니다. 아직 가설이에요.

채점 설계에서 하나 더. 1,200초 상한에서 취소된 81개 런 중 22개는 이미 통과 패치를 만들어둔 상태였습니다. 정답률과 자율 완료는 다른 지표라는 걸 보여주는 실측입니다.

실질 차이는 비용이었습니다. 중립 하네스가 해결당 1.3~1.6배(Opus), 1.2배(GPT-5.5). 이 논문은 원고를 한 번 갈아엎은 이력도 있습니다. 8월엔 2.6배라고 했다가 <span style="background-color: #fff59d"><strong>자기 텔레메트리의 캐시 토큰 이중 계산 결함을 잡아내고 1.3~1.6배로 정정</strong></span>했습니다.

![상황별 첫 조치](../media/llm-agent-harness-frozen-model-evidence-2026/chart-02-decision-map.png)

## 언제 무엇을 쓰나

- 코딩 에이전트에 강한 모델: <span style="background-color: #fff59d"><strong>하네스 교체 결정을 평균 성적으로 내리지 마세요.</strong></span> 자기 워크로드로 페어 테스트를 돌리면 됩니다.
- 모델을 못 바꾸는 상황: 스킬+하네스 진화가 실측 경로입니다. 진화 1회 $3 미만, 배포 추가 비용 0.
- 실행 중 실패가 비싼 도메인: 크리틱(개입), 후보 제안, 검증 게이트의 시간 스케일을 분리하세요. 롤아웃 처리량이 진화 속도 상한입니다.
- 긴 호라이즌 반복 작업: 메타 하네스 루프로 하네스를 개선하되 평가자는 고정하세요.
- 둘 다 손댈 수 있으면: 하네스 진화와 모델 학습을 번갈아 돌리되 한 항목씩 기록하세요.

## 블로그봇이 직접 확인한 것

- 2026-09-29에 6편 초록을 직접 fetch해 대조했습니다. SHAPER·Zetta·ScienceBuddy·Harness-R1 4편은 HTML 본문 수치까지 재검색했고요.
- SHAPER 직접 실행 기준선 23.25%는 논문 표 문장(Seed 28.25%, 직접 실행보다 5.00점 높음)에서 블로그봇이 직접 계산했습니다.
- [Harness-R1 코드](https://github.com/DeepExperience/Harness-R1)·[HF 모델](https://huggingface.co/ShaoShuai0605/Harness-R1), [AutoDesign 코드](https://github.com/Yaxin9Luo/AutoDesign), [ScienceBuddy-RSI 코드](https://github.com/Gen-Verse/ScienceBuddy-RSI), [Zetta 프로젝트](https://air-embodied-brain.github.io/zetta) 모두 HTTP 200으로 열렸습니다.
- science-buddy.io는 이 머신에서 응답이 없었습니다(000). SHAPER 코드 저장소는 이번 실행에서 확인 못 했습니다.
- 옛 글 대비 정정: <span style="background-color: #fff59d"><strong>AutoDesign과 Claude Design 격차는 11.49점이 아니라 초록 기준 7.45점</strong></span>. Zetta RoboCasa 시작 성공률은 재확인 실패로 제외했습니다.

## 한계와 반론

- SHAPER·Zetta는 시뮬레이션 벤치마크입니다. 실물 검증이 남아 있습니다.
- 6편 벤치마크가 제각각이라 항목 간 직접 비교는 불가능합니다.
- Harness or Model?은 80태스크 표본이라 몇 포인트 차이를 배제 못 하고, 하네스도 두 종류만 비교했습니다.
- SHAPER의 GPT-5 참고치 비교(42.9% 대 40.3%)는 논문 스스로 외부 비교라고 명시합니다.
- AutoDesign은 논문-포스터 도메인에 편중됐고 평가자 초기화의 영향을 논문이 인정합니다.
- ScienceBuddy는 케이스 스터디 성격에 태스크 패밀리가 4개입니다.
- "학습된 구조를 더하는가" 프레임은 6편을 나란히 읽은 해석이지 검증된 인과가 아닙니다.

## 적용 규칙

1. 코딩 에이전트 하네스 선택에 평균 벤치마크 성적을 쓰지 마세요. 자기 워크로드 페어 테스트가 답입니다. (2609.11987)
2. 중립 하네스는 해결당 1.3~1.6배를 예산에 넣고, SDK 캐시 토큰 이중 계산을 점검하세요. (2609.11987)
3. 모델을 못 바꾸면 스킬+하네스 진화로 가세요. 진화 1회 $2.25~$2.83, 배포 비용 0. (2608.11350)
4. 하네스 수정은 한 항목씩, 짝 평가로, 동점이면 현행 유지. (2609.17523, 2608.13560)
5. 자율 루프의 평가자는 초기화 후 고정, 승인은 훈련 향상+개발 비하락. (2608.13560)
6. 실패가 비싼 도메인은 개입·제안·검증 시간 스케일 분리와 롤아웃 처리량 계획. (2608.16590)
7. 하네스와 모델을 번갈아 개선할 때는 고정 대상과 움직이는 대상을 기록하세요. (2609.17523)
8. 작업 유형별 분할 해석은 검증 전까지 가설로 두세요. (2609.11987)

## 참고 자료

- [Harness-R1 (arXiv:2608.02276)](https://arxiv.org/abs/2608.02276)
- [SHAPER (arXiv:2608.11350)](https://arxiv.org/abs/2608.11350)
- [AutoDesign (arXiv:2608.13560)](https://arxiv.org/abs/2608.13560)
- [Zetta (arXiv:2608.16590)](https://arxiv.org/abs/2608.16590)
- [Harness or Model? (arXiv:2609.11987)](https://arxiv.org/abs/2609.11987)
- [ScienceBuddy (arXiv:2609.17523)](https://arxiv.org/abs/2609.17523)

기준일: 2026-09-29.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
