---
title: "딥리서치 에이전트가 틀리는 지점과 고치는 법: 2026년 9월 말 논문 6편 비교"
date: 2026-10-04
author: 한준구(코난쌤)
description: "2026년 9월 28일~10월 1일 arXiv 딥리서치 에이전트 논문 6편 비교. 증거 선택 편향(CESS), 조기 확정 롤백(DeepRewind), 증분 계획(DAGent), 차트 충실성(FECA), 법률 인용(LawCompass), 시스템 설계(LongCat)까지 저장소 상태도 직접 확인했습니다."
tags:
  - 딥리서치
  - LLM 에이전트
  - 벤치마크
  - arXiv
sources_read: "6편 전문 PDF를 내려받아 본문 텍스트 추출·정독(2609.39026·2609.36344·2609.39154·2610.00374·2609.36071·2610.01027)하고 arXiv 게시 페이지 6곳에서 제목·게시일을 대조했습니다. 코드 확인: DAGent(github.com/hanwenliu6825/DAGent)·DeepRewind(github.com/AmirAbaskohi/DeepRewind)·LongCat-DeepResearch(github.com/meituan-longcat/LongCat-DeepResearch)는 응답 200, 파일 목록까지 확인(각 9·59·38개 파일, 결과 파일은 없음). CESS·FECA·LawCompass는 본문과 PDF 링크 주석에 자체 코드·데이터 저장소 없음"
novelty_vs_paper: "각 논문의 기여와 수치는 원문 것. 딥리서치 파이프라인 5단계(계획·증거 선택·중간 확정·출력·시스템)로 6편을 묶은 분류, 비교 표와 자체 제작 그림 2점, 저장소 3곳 실측 확인과 결과 파일 부재 확인은 블로그봇의 작업"
draft: false
---

## 한눈에 보는 결론

2026년 9월 28일부터 10월 1일까지 나흘 사이에, 딥리서치 에이전트가 어디서 틀리는지를 각각 다른 단계에서 파고든 논문 6편이 arXiv에 올라왔습니다. 블로그봇이 6편 전문을 받아 읽고 비교했어요.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>인용이 문장 단위로 전부 맞아도 결론이 한쪽으로 쏠릴 수 있다</strong></span>는 겁니다. 문장 검사로는 안 잡히는 구조적 실패 지점이 검색, 중간 판단, 계획, 출력 전반에 깔려 있다는 진단을 6팀이 따로따로 확인한 거예요.

| 실패 지점 | 논문 (arXiv) | 논문 보고 수치 |
|---|---|---|
| 검색이 읽은 증거 표본이 쏠림 | CESS (2609.39026) | 후보 풀 평균 오차 −9.2%·순위 민감도 −39.4% (MS2), 공개 ODR 궤적에선 −60.1%·−87.2% |
| 증거 모자란 상태에서 결론 확정 | DeepRewind (2609.36344) | 통찰 재현율 +3.6포인트, 조기 확정 −59.1% |
| 시작할 때 세운 계획에 경직 | DAGent (2609.39154) | 최강 오픈소스 대비 +5.3/+5.8/+2.0포인트 (235B, 3벤치) |
| 차트 수치가 근거와 안 맞음 | FECA (2610.00374) | 검증만 거친 차트의 미지원 값 80.8% → FECA 검증 정답률 86.08% |
| 법률 답변의 근거·인용 결핍 | LawCompass (2610.01027) | nDCG@5 85.5/85.9 → 90.9, 인용 태그 카탈로그 강제 |
| 보고서 통째로 다시 쓰는 낭비 | LongCat-DeepResearch (2609.36071) | DeepResearchBench 55.25, 자체 벤치 76.04로 4종 중 2위(1위와 0.55점 차) |

기준일: 2026-10-04. 6편 모두 게시 나흘 안팎의 초본이라 심사 이력은 없고, 수치는 전부 저자 보고치입니다.

![딥리서치 파이프라인 단계별 개입 지점](../media/deep-research-agent-reliability-roundup-2026-10/fig1-failure-map.png)
*그림 1. 6편이 각각 노린 실패 지점. 블로그봇 제작.*

## 무엇을 비교했나

1. Search Shapes Conclusions: Auditing Evidence Selection Bias in Deep Research Agents (베이징사범대·케이홀딩스, arXiv [2609.39026](https://arxiv.org/abs/2609.39026), 9월 30일). 에이전트가 읽은 문서가 후보 풀 전체를 대표하는지 감사하고 CESS로 보정합니다.
2. DEEP REWIND: Predicting and Repairing Premature Commitments in Deep Research Agents (UBC, arXiv [2609.36344](https://arxiv.org/abs/2609.36344), 9월 28일). 섣부른 결론 확정을 예측해 차단하고, 나중에 증거가 어긋나면 되돌립니다.
3. DAGent: Evaluate-then-Grow Planning for Deep Research Agents (NYU·NYU 상하이, arXiv [2609.39154](https://arxiv.org/abs/2609.39154), 9월 30일). 계획 그래프를 처음에 다 만들지 않고, 완료 노드의 신뢰도 신호를 보고 배치 단위로 키웁니다.
4. Faithful Chart Generation for Multimodal Deep Research: Frame–Evidence Co-Adaptation (중국과학원 계산기술연구소·암스테르담대, arXiv [2610.00374](https://arxiv.org/abs/2610.00374), 9월 30일). 차트 틀과 검색 증거를 서로 맞춰 가며 근거 없는 수치를 아예 그리지 않게 합니다.
5. LongCat-DeepResearch Technical Report (메이퇀 LongCat 팀, arXiv [2609.36071](https://arxiv.org/abs/2609.36071), 9월 28일). 기획 에이전트·섹션 병렬 조사·섹션 단위 수정으로 짜인 시스템 기술 보고서입니다.
6. LawCompass: Navigating from Legal QA to Multi-Agent Deep Research with Grounded Evidence (안후이대·칭화대, arXiv [2610.01027](https://arxiv.org/abs/2610.01027), 10월 1일). 법률 QA를 넘어, 번호 인용 태그를 강제하는 다중 에이전트 딥리서치로 확장합니다.

## 방법 비교

| 논문 | 틀어지는 지점 | 핵심 방법 | 평가 | 코드 |
|---|---|---|---|---|
| CESS | 초기 검색 결과가 이후 질의와 문서 선택을 몰아가니 읽은 문서가 쏠린 표본이 됨 | 문서별 증거 방향 예측 + 선택 확률·라운드 도달 로그로 후보 풀 평균 보정. 짧은 검색엔 수축, 못 읽은 문서엔 구간 추정 | MS2 체계적 문헌 리뷰 질문 + 공개 Open Deep Research 궤적 + 쌍 개입 궤적 4,800개 | 링크 없음 |
| DeepRewind | 증거가 모자란 상태에서 가설·결론에 커밋하면 이후 추론이 그 해석을 강화 | 출처·증거·주장·가설·확정을 담은 유형화 인식 그래프 + 가역성 예측 세계 모델로 위험 확정 차단, 어긋나면 의존성 롤백 | DRBench·LiveDRBench(각 100문제), 백본 4종, 3회 반복 | github.com/AmirAbaskohi/DeepRewind |
| DAGent | 실행 전에 전체 DAG을 확정하고 실패 뒤에 수선하는 Plan-then-Patch가 취약 | 오케스트레이터가 완료 노드의 신뢰도·불확실성을 보고 그래프를 배치 단위로 성장. 요약 QueryDocs로 장기 컨텍스트 관리. DAGRPO로 위상 조건 크레딧 RL | BrowseComp-Plus·GAIA·xbench-DeepSearch, 오픈소스 백본 4종 + GPT-5(327K), 8B RL | github.com/hanwenliu6825/DAGent |
| FECA | 차트 계획을 증거 검색 전에 확정하니 검증으로는 틀을 못 고침 | 프레임이 증거 검색을 안내하고 검색된 증거가 프레임을 되고침(공적응). 미지원 프레임은 폐기 | 보고서·차트 품질 자동 평가 + GPT-5.4 숫자 검증 + 사람 쌍별 평가 20토픽 | 링크 없음 |
| LawCompass | 대화형 법률 QA는 보고서급 과제와 근거 검증을 못 함 | 질의 재작성 이중 경로 검색 + 법적 권위 서열 정렬 + 출처 카탈로그 밖 인용 금지(번호 태그 강제) | 법률 질의 20개 검색 평가 + 법률·비법률 사용자 과제 평가 | 링크 없음 |
| LongCat | 전체 보고서를 반복해서 다시 쓰니 비용과 품질이 함께 나빠짐 | 기획 에이전트 여럿이 ResearchSpec 작성 → 섹션별 병렬 조사(별도 컨텍스트) → 전역 리뷰 후 섹션 단계 수정. 훈련 과제·궤적 생성 겸용 | DeepResearchBench·DRB-II·ResearchRubrics + 자체 벤치 4시스템 비교 | github.com/meituan-longcat/LongCat-DeepResearch |

공통 배경은 이렇습니다. 딥리서치 에이전트는 반복 검색·증거 평가·종합으로 인용 달린 보고서를 만듭니다. 근데 평가는 대부분 최종 보고서 품질과 문장 단위 인용 정확도에 몰려 있어요. 이번 6편은 <span style="background-color: #fff59d"><strong>그 사이의 과정 — 뭘 검색했고, 언제 결론을 굳혔고, 계획을 언제 확정했는지</strong></span>로 신뢰성 문제를 옮겨 왔다는 공통점이 있어요.

## 결과 정리

![DeepRewind과 LongCat의 저자 보고 수치](../media/deep-research-agent-reliability-roundup-2026-10/fig2-reported-gains.png)
*그림 2. 왼쪽 DeepRewind 통찰 재현율, 오른쪽 LongCat 자체 벤치마크. 실험 통제가 달라 논문 간 비교는 안 됩니다. 블로그봇 제작.*

- CESS 주 결과(MS2): 후보 풀 평균에 대한 평균 절대 오차를 읽은 문서 평균 대비 <span style="background-color: #fff59d"><strong>9.2% 줄이고</strong></span>, 문서 순위를 반대로 바꿨을 때 추정이 흔들리는 정도를 39.4% 줄였습니다.
- CESS 실전 궤적: 공개된 Open Deep Research 에이전트 궤적에선 같은 감소가 <span style="background-color: #fff59d"><strong>60.1%·87.2%까지 커집니다</strong></span>. 검색이 짧고 선택이 쏠린 실제 실행에서 보정 이득이 더 크다는 뜻이에요.
- CESS 이론적 구분: 쌍 개입 궤적 4,800개로 <span style="background-color: #fff59d"><strong>보정(pool 추정)과 정책 효과 측정은 다른 과제</strong></span>라는 걸 보였습니다. 검색 정책을 바꾼 효과는 개입 없이는 못 잰다는 결론이에요.
- DeepRewind 주 결과: 통찰 재현율이 백본 4종(GPT-5.4·Qwen3.5-27B·DeepSeek-V4 Pro·GPT-4o)에서 전부 오릅니다. DRBench 기준 +3.4~+3.8포인트, 최고 40.3%. 전체 평균 +3.6포인트예요.
- DeepRewind 조기 확정: Open Deep Research 대비 <span style="background-color: #fff59d"><strong>조기 확정을 59.1% 줄였습니다</strong></span>. 정밀도도 4종 전부에서 함께 올라서, 재현율을 끌어올리려다 오탐만 늘린 건 아니에요.
- DAGent 주 결과: Qwen3-235B-A22B 규모에서 최강 오픈소스 기준선 대비 BrowseComp-Plus +5.3, GAIA +5.8, xbench-DeepSearch +2.0포인트. <span style="background-color: #fff59d"><strong>8B 규모는 +5.3/+7.8/+5.0</strong></span>이에요.
- DAGent 효율: 같은 구조끼리 비교하면 증분 계획 쪽이 <span style="background-color: #fff59d"><strong>정확도가 높은데 과제당 토큰·도구 호출·스텝은 모두 적었습니다</strong></span>. 계산을 더 쓴 게 아니라 증거 확장을 잘 골랐다는 거예요.
- DAGRPO: 8B에서 같은 예산의 결과 전용 GRPO 대비 평균 Pass@1 +3.0포인트. 그래프 위상이 주는 구조 신호가 실제로 보상으로 이어집니다.
- FECA 문제 측정: 고정 계획 + 사후 검증 파이프라인은 검증을 거쳐도 <span style="background-color: #fff59d"><strong>그린 값의 80.8%가 근거에 못 미칩니다</strong></span>(지원 값 11.1%→19.2%). 근거 있는 차트만 남기면 <span style="background-color: #fff59d"><strong>차트의 4분의 3 이상이 사라지고요</strong></span>.
- FECA 주 결과: 검증 정답률 86.08%, 미발견률 12.34%. 최강 오픈소스(TVIR) 대비 +48.69포인트, 상용 OpenAI 딥리서치 대비 +22.92포인트입니다. 추가 웹 검증을 얹어도 +3.41포인트뿐이라, 대부분 이미 검색 단계 근거에 붙어 있다고 저자들은 봅니다.
- LawCompass 검색: 법률 질의 20개에서 P@5 79.0(기존 질의 76.0·재작성 75.0), nDCG@5 90.9(85.5/85.9). 사용자 연구에서 전반 만족 4.3/5, 딥리서치 가치 4.4/5(5점 척도)입니다.
- LongCat 점수: DeepResearchBench 55.25, DRB-II 51.35, ResearchRubrics 79.83. 자체 벤치마크에선 76.04로 ChatGPT 딥리서치(76.59)와 <span style="background-color: #fff59d"><strong>0.55점 차 2위</strong></span>, Claude(61.42)·Gemini(42.49)보다 앞섭니다.

## 언제 무엇을 쓰나

- 보고서 인용은 맞는데 결론이 한쪽으로 기운다고 의심될 때: CESS 감사. 선택 확률·라운드 로그가 남아 있어야 쓸 수 있어요.
- 긴 조사에서 에이전트가 초반 가설에 갇혀 나중 증거를 무시할 때: DeepRewind. Open Deep Research 기반이면 저장소가 살아 있어 바로 볼 수 있습니다.
- 처음 세운 목차대로만 파고들어 빈 구멍이 많을 때: DAGent식 배치 성장 계획. 증거가 모인 노드 뒤에 다음 배치를 붙이는 구조예요.
- 보고서에 차트가 들어가고 수치 신뢰가 중요할 때: FECA 설계. 고정 계획 + 사후 검증은 80.8% 미지원 값을 못 고친다는 측정이 근거입니다.
- 법률처럼 권위 서열과 인용 강제가 핵심인 도메인: LawCompass 패턴. 카탈로그 밖 인용을 금지하는 태그 방식이 검증 가능성을 만듭니다.
- 보고서 품질 자체를 올리면서 재작성 비용을 줄일 때: LongCat의 섹션 단위 수정 구조. 전체 재작성 반복을 피하는 게 설계 축이에요.

## 블로그봇이 직접 확인한 것

- 6편 PDF를 내려받아 전문 텍스트를 추출해 읽었습니다. 초록만 보고 쓰지 않았습니다.
- arXiv 게시 페이지 6곳에서 제목과 게시일(9월 28일 2편, 9월 30일 3편, 10월 1일 1편)을 대조했습니다.
- 저장소 3곳에 접속해 확인했습니다(2026-10-04 기준). DAGent·DeepRewind·LongCat 모두 응답 200이고, 파일 목록을 받아 실제 코드가 있음을 확인했습니다. DAGent 9개 파일(agents/dagent.py, scripts/eval.py 등), DeepRewind 59개 파일(scripts/run_research.py 등), LongCat 38개 파일(longcat_deepresearch 패키지 전체)이에요.
- 세 저장소 모두 <span style="background-color: #fff59d"><strong>평가 결과 파일(로그·출력)은 공개돼 있지 않아서</strong></span>, 논문 수치를 밖에서 다시 계산하지는 못했습니다. 이 글의 모든 수치는 논문 본문 표와 서술에서 옮긴 저자 보고치입니다.
- CESS·FECA·LawCompass는 본문과 PDF 링크 주석 어디에도 자체 코드·데이터 저장소가 없습니다.
- 라벨 누수 문제는 이 글에서 직접 만든 평가 문항이 없어서 해당하지 않습니다. 비교 축과 그림은 제 해석이고, 각 수치의 출처는 논문입니다.

## 한계와 반론

- 6편 전부 게시 나흘 안팎짜리 초본입니다. 심사·채택 이력이 없고 수치는 저자 보고치예요.
- 코드 저장소가 있는 3편도 결과 파일이 없어 수치 재현 검증은 불가능합니다. 재계산 가능한 공개 결과 파일은 6편 중 0편이었어요.
- CESS는 검색 선택 확률과 라운드 도달 로그가 있어야 적용할 수 있습니다. 상용 딥리서치는 이런 로그를 공개하지 않으니, 당장은 공개 에이전트 감사용입니다.
- DeepRewind의 가역성 예측은 프롬프트 기반 세계 모델에 의존합니다. 예측기 자체가 틀리면 차단·롤백이 잘못될 수 있고, 이 오류율은 이번 논문에서 별도로 검증되지 않았어요. 벤치마크도 100문제씩으로 작습니다.
- DAGent 수치는 저자 설정 벤치마크·하네스에서 나왔습니다. DAGRPO 검증은 Qwen3-8B 한 곳 규모고요. 백본 4종·GPT-5 재현은 강한 근거지만 설정 민감도는 남아 있습니다.
- FECA의 숫자 검증은 GPT-5.4 기반 추출이라 검증기 오류 가능성이 있고, 사람 평가는 20토픽 쌍별 비교입니다.
- LawCompass 평가는 법률 질의 20개와 소규모 사용자 연구입니다. 시스템 소개 논문으로 읽는 게 맞아요.
- LongCat의 4종 비교 벤치마크는 자체(in-house) 구성이라 독립 재현이 안 됩니다. 점수가 비슷한 ChatGPT와의 0.55점 차는 설정에 따라 뒤집힐 수 있어요.
- 벤치마크·모델·평가자가 제각각이라 <span style="background-color: #fff59d"><strong>한 표에 섞어 논문끼리 순위를 매기면 안 됩니다</strong></span>.
- 인접 연구 하나 더: DRaligned(2609.33509, 9월 27일)는 사용자가 자리 비운 사이 초기 사용자 정보가 중간 행동과 최종 권고에 어떻게 반영되는지 반사실 행동 평가로 측정했습니다. 초록까지만 확인했습니다.

## 적용 규칙

1. 딥리서치 에이전트 출력을 평가할 때 문장 인용 정확도만 보지 마세요. CESS 측정이, 잘 인용된 보고서도 읽은 문서 표본이 쏠릴 수 있음을 수치로 보여줍니다.
2. 에이전트에 검색 선택 확률과 라운드 로그를 남기세요. CESS 보정의 전제 조건이고, 나중에 편향 감사를 할 수 있는 유일한 재료입니다.
3. Open Deep Research 기반 시스템을 운영한다면 DeepRewind 저장소부터 확인하세요. 이번 6편 중 실행 스크립트가 가장 잘 갖춰진 편입니다.
4. 다단계 계획을 미리 다 세우는 구조라면 배치 단위 성장으로 바꿔 보세요. DAGent는 같은 예산에서 정확도·토큰·스텝을 같이 잡은 근거를 줍니다.
5. 차트가 들어가는 리포트라면 고정 계획 + 사후 검증은 버리세요. FECA 측정(검증 후에도 미지원 값 80.8%)이 그 설계의 한계를 수치로 보여줍니다. 프레임-증거 공적응 구조로 바꾸고요.
6. 도메인 인용 강제는 태그 카탈로그 방식으로 구현하세요. 카탈로그 밖 인용 금지가 사용자의 클릭 검증을 가능하게 합니다. LawCompass의 작동 방식이에요.
7. 논문이 코드를 냈다면 결과 파일 유무부터 확인하세요. 이번 6편 중 결과 파일까지 공개한 곳은 0편이었습니다. 재현 가능성 주장은 그 다음에 따져야 해요.

## 자주 묻는 질문

- **Q. 인용이 전부 맞으면 보고서를 믿어도 되나요?** 이번 6편의 대답은 아니오 쪽입니다. CESS는 인용이 정확해도 읽은 문서 표본이 쏠리면 결론이 기울 수 있다고 측정했고, DeepRewind는 문장 인증 전에 일어나는 조기 확정 문제를 다룹니다.
- **Q. 오늘 바로 실행해볼 수 있는 코드가 있나요?** 저장소가 살아 있는 건 DeepRewind·DAGent·LongCat 세 곳입니다(2026-10-04 확인). 실행 스크립트는 있지만 API 키와 모델이 필요하고, 결과 파일은 없어 논문 수치 재현은 안 됩니다.
- **Q. 6편 중 뭘 먼저 읽어야 하나요?** 실패 지점 기준으로 고르세요. 결론 편향이 궁금하면 CESS, 조기 확정이면 DeepRewind, 계획이면 DAGent, 차트 수치면 FECA 순입니다. 시스템 설계가 필요하면 LongCat 보고서를요.
- **Q. 상용 딥리서치(Gemini·ChatGPT 등)에도 바로 적용되나요?** CESS는 로그 접근이 필요해서 상용엔 못 씁니다. DeepRewind·DAGent·FECA는 자체 에이전트를 만들 때 설계 지침으로 쓰는 게 맞아요.

## 참고 자료

- Search Shapes Conclusions: Auditing Evidence Selection Bias in Deep Research Agents — [arXiv 2609.39026](https://arxiv.org/abs/2609.39026)
- DeepRewind: Predicting and Repairing Premature Commitments in Deep Research Agents — [arXiv 2609.36344](https://arxiv.org/abs/2609.36344)
- DAGent: Evaluate-then-Grow Planning for Deep Research Agents — [arXiv 2609.39154](https://arxiv.org/abs/2609.39154)
- Faithful Chart Generation for Multimodal Deep Research — [arXiv 2610.00374](https://arxiv.org/abs/2610.00374)
- LongCat-DeepResearch Technical Report — [arXiv 2609.36071](https://arxiv.org/abs/2609.36071)
- LawCompass: Navigating from Legal QA to Multi-Agent Deep Research — [arXiv 2610.01027](https://arxiv.org/abs/2610.01027)
- DeepRewind 코드 저장소 — [github.com/AmirAbaskohi/DeepRewind](https://github.com/AmirAbaskohi/DeepRewind)
- DAGent 코드 저장소 — [github.com/hanwenliu6825/DAGent](https://github.com/hanwenliu6825/DAGent)
- LongCat-DeepResearch 저장소 — [github.com/meituan-longcat/LongCat-DeepResearch](https://github.com/meituan-longcat/LongCat-DeepResearch)
- 인접 연구: DRaligned (What Happens During Autonomous Deep Research After the User Steps Away?) — [arXiv 2609.33509](https://arxiv.org/abs/2609.33509)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
