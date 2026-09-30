---
title: "LLM 에이전트 평가 설계 가이드: 점수 다음에 볼 축·신뢰성·비용 — 벤치마크·연구 14종 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "LLM 에이전트 벤치마크·평가 연구 14종을 비교해 점수 다음에 봐야 할 다섯 가지(능력 프로파일, 정책 준수, 보조 능력, 측정 신뢰성, 평가 비용)를 정리했습니다. 수치는 논문 본문 HTML과 공식 문서에서 대조 확인한 것만 담았습니다."
tags:
  - LLM 에이전트
  - 벤치마크
  - 에이전트 평가
  - LLM-as-judge
refactor_hub_id: eval-benchmarks-02
aliases:
  - agentic-evals-workshop-future-of-agent-evaluations
  - 2026-06-07-foresci-llm-research-judgment
  - posts/2026-07-19-omniabench-general-ai-agent-benchmark
  - posts/2026-07-26-graph-engineering-four-prompts
  - posts/2026-08-01-handbook-md-long-context-agent-policy-benchmark
  - posts/2026-08-15-llmrouter-xroutebench
  - posts/2026-08-20-fm-bench-long-horizon-management-benchmark
  - posts/2026-08-22-centaurbench-augment-vs-automate
  - posts/2026-08-29-ace-lens-agentic-data
  - posts/2026-09-03-ecommerce-bench-long-horizon-agents
  - posts/2026-09-04-llm-judge-shared-endpoint-reliability
  - posts/2026-09-13-mindtopo-topological-reasoning-benchmark
  - posts/2026-09-17-agent-benchmark-compression-dualvieweval
  - posts/2026-09-17-llm-abstention-cosq-selective-risk
draft: false
sources_read: "논문 12종(ForeSci·OmniaBench·HANDBOOK.md·xRouteBench·FM-Bench·CentaurBench·ACE·E-Commerce Bench·저지 감사·MindTopo·CoSQ·DualViewEval) 초록·본문 HTML을 2026-09-30에 fetch해 전부 HTTP 200 확인 후 인용 수치 전수 대조, FM-Bench 저자 코드 github.com/Analogy-AI/fm-bench HTTP 200 확인, HF 워크숍 영상·Anthropic 지식그래프 쿡북 공식 문서 HTTP 200 확인, 나머지 11종은 저자 코드를 확인하지 않아 코드 미확인으로 기록"
novelty_vs_paper: "각 벤치마크의 구성·수치는 전부 각 논문·공식 문서의 것이며, 이 글이 새로 만든 것은 점수 다음에 볼 다섯 가지 분류, 14종 통합 대조 표, 초점 매트릭스와 격차 차트 2장, 수치 대조 확인 로그, 적용 규칙 8개임"
---

## 한눈에 보는 결론

리더보드 점수는 출발점입니다. 2026년 3월부터 9월까지 이 블로그에 단발 정리로 쌓인 평가·검증 글 14편을 하나로 합쳐 다시 정리했습니다.

14종은 각자 다른 각도에서 같은 지점으로 모입니다. 점수 한 줄로 에이전트 도입 결정을 내리기 어렵고, 점수 다음에 볼 것이 따로 있다는 것입니다.

핵심은 이겁니다. 점수 다음에 볼 것은 다섯 가지로 압축됩니다. <span style="background-color: #fff59d"><strong>능력은 프로파일로 잡힙니다</strong></span>. 할 수 있는 것과 해도 되는 것은 다른 축입니다. 혼자 잘 푸는 것과 남을 돕는 것도 다른 축입니다. 측정 도구 자체를 먼저 검증해야 합니다. 평가 비용도 설계 대상입니다.

숫자로 먼저 보시면 이렇습니다.

- OmniaBench에서 <span style="background-color: #fff59d"><strong>최전선 모델의 Overall Pass@1은 60% 미만(Claude-Sonnet-5 58.54%)</strong></span>이고 일관된 약점은 계획·제약 유지·적응적 수정입니다.
- E-Commerce Bench에서 연말 수익 1위 모델(GPT-5.6 Sol, 초기 자본 ¥100,000을 ¥1,431,425로)의 <span style="background-color: #fff59d"><strong>사기 회피는 18개 모델 중 16위입니다</strong></span>.
- HANDBOOK.md에서 <span style="background-color: #fff59d"><strong>정책 준수 strict 기준 최고 성적은 36.2%입니다</strong></span>.
- CentaurBench에서 <span style="background-color: #fff59d"><strong>자동화 순위와 보조 순위의 상관은 약 0.48입니다</strong></span>.
- LLM 저지 감사에서 같은 요청의 <span style="background-color: #fff59d"><strong>반복 랭킹 일치도가 Spearman 0.400(요구치 0.90)</strong></span>입니다.

## 무엇을 비교했나

이 글은 2026-03-31 ~ 2026-09-17에 나눠 쓴 평가 관련 글 14편을 합쳐 다시 쓴 허브입니다. 옛 글 URL은 이 글로 연결됩니다.

1. [HF Agentic Evaluations Workshop](https://www.youtube.com/watch?v=UxMZfbWI3LY) — 에이전트 평가 커뮤니티의 방향 정리. 능력-신뢰성 격차, 세션 단위 보고, 공개 검증.
2. [ForeSci](https://arxiv.org/abs/2606.00644) — 과거 증거만으로 미래 연구 판단을 재는 시간 제어 벤치마크. 500 태스크.
3. [OmniaBench](https://arxiv.org/abs/2607.14989) — ToC·ToB·ToE 354개 소분류 도메인 1,431 과제, 능력 10차원 분해.
4. [Graph Engineering](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide) — 지식그래프 구축 파이프라인과 그 평가 하네스. Anthropic 공개 자료 기반.
5. [HANDBOOK.md](https://arxiv.org/abs/2607.25398) — 10개 기업 65 태스크, 824개 결정론적 검증 기준의 정책 준수 벤치마크.
6. [xRouteBench·LLMRouter](https://arxiv.org/abs/2608.06867) — 모델 선택(라우팅) 자체를 재는 실험 플랫폼.
7. [FM-Bench](https://arxiv.org/abs/2608.18423) — 축구 클럽 20년 경영, 15개 모델, 26개 도구의 장기 의사결정 벤치마크.
8. [CentaurBench](https://arxiv.org/abs/2608.18554) — 자동화 모드와 보조 모드를 워커를 고정하고 나눠 재는 벤치마크.
9. [ACE 서베이](https://arxiv.org/abs/2608.27260) — 에이전트 훈련 데이터를 (E,q,τ,v)로 인자화하고 정확도·복잡도·다양성으로 보는 프레임워크.
10. [E-Commerce Bench](https://arxiv.org/abs/2608.30730) — 365일 사업 운영 시뮬레이션, 18개 모델, 7개 평가 축.
11. [LLM 저지 신뢰성 감사](https://arxiv.org/abs/2609.04198) — 공유 엔드포인트에서 계측기가 재현되는지 52,988회 요청으로 점검.
12. [MindTopo](https://arxiv.org/abs/2609.11900) — 위상 추론 13개 과제 11,030 인스턴스로 정적 추론과 폐쇄 루프 계획을 분리 측정.
13. [DualViewEval](https://arxiv.org/abs/2609.18909) — 결과와 과정 신호를 같이 써 미니셋 20개로 전체 점수를 예측.
14. [CoSQ](https://arxiv.org/abs/2609.17516) — 답을 만들기 전에 기권 여부를 결정하는 선택적 예측 프레임워크.

## 방법 비교

기준일 2026-09-30. 블로그봇이 각 논문의 초록과 본문 HTML, 공식 저장소·문서에서 직접 대조해 확인한 수치만 담았습니다. 확인되지 않은 수치는 제외했고 목록은 아래에 적어뒀습니다.

| 자료 | 재는 것 | 이번 실행에서 확인된 대표 수치 | 채점·환경 |
| --- | --- | --- | --- |
| OmniaBench | 능력 10차원 프로파일 | 최고 58.54%(60% 미만), 약점은 계획·제약 유지·적응적 수정 | 1,431 과제, Pass@1 |
| HANDBOOK.md | 정책 준수(해야 할 일·금지) | strict 최고 36.2%, 검증 기준 824개 중 28.2%가 금지행동, 최고-최하 45배 | 65 태스크, 결정론적 코드 채점 |
| E-Commerce Bench | 수익·안전 등 7개 축 | 수익 1위 GPT-5.6 Sol 14.3배(¥1,431,425), 사기 회피 16/18위, 4개 모델 파산 | 365일, 18모델 각 5회 |
| FM-Bench | 장기 경영 행동 | 토큰 지출은 성적과 무상관, Arena 우승이 10개 모델에서 로테이션 | 20년, 15모델, 26도구, 결정론 엔진 |
| CentaurBench | 자동화 vs 보조 | 두 순위 상관 0.48, 7과제 중 5개에서 1등 상이, 무보조 워커가 3과제에서 모든 보조 조건 상회 | 워커 GPT-3.5-Turbo 고정, 블라인드 페어와이즈 |
| MindTopo | 정적 추론 vs 폐쇄 루프 계획 | Gemini 3.1 Pro 60.0→43.2, 학습 후에도 계획 6.3, 인간 97.49% | 11,030 인스턴스, 절차적 생성 |
| ForeSci | 전망적 연구 판단 | 증거는 인용하면서 결론이 어긋나는 분리 실패 모드 | 500 태스크, 시간 엄격 제어 |
| xRouteBench | 모델 라우팅 | 최대 모델 고정 38.72 vs GraphRouter 45.46(+14.6%), 실사용자 1위 83.05 | 오픈웨이트 18종, 8테스트셋 |
| LLM 저지 감사 | 계측기 안정성 | 반복 랭킹 0.400(요구 0.90), 바이트 동일 0.78(요구 0.99), 격차 3.04×10⁻¹⁰ vs 노이즈 10⁻³ | 52,988회 요청, 통과 기준 사전 동결 |
| DualViewEval | 평가 압축 | 미니셋 20개로 24~40배 압축, MAE 3~6%, 최강 대비 오차 14.5~28.2% 감소 | 결과 행렬 + 과정 신호 6개 |
| CoSQ | 기권 설계 | 오답 커밋률 0.131→0.089(32.1% 감소), 옳은 기권은 기권의 31.3% | TruthfulQA 817문항, 프롬프트만 |
| ACE 서베이 | 훈련 데이터 품질 | 데이터를 (E,q,τ,v)로 인자화, 정확도·복잡도·다양성 렌즈 | 서베이 |
| HF 평가 워크숍 | 평가 관행 | 능력(capability)과 신뢰성(reliability) 격차 프레임 | 라이브 토론 |
| Graph Engineering | 파이프라인 평가 하네스 | 공식 쿡북에서 추출·엔티티 해소의 이중 모델 구성 확인 | Anthropic 공개 자료 |

표 읽는 요령. 각 행의 채점 기준과 모델 구성이 제각각입니다. 벤치마크 간 직접 우열 매기기에는 못 씁니다. 각 행은 그 관찰이 어떤 조건에서 나왔는지를 보여줍니다.

![평가 14종이 무엇을 재는지 묶은 매트릭스](../media/llm-agent-evaluation-design-guide-2026/chart-01-what-they-measure.png)

## 점수 다음에 볼 다섯 가지

### 능력은 프로파일로 본다

OmniaBench는 1,431개 과제를 능력 10차원으로 분해했습니다. 최전선 모델 둘(Claude-Sonnet-5 58.54%, GPT-5.6-Sol 57.14%)만 57%를 넘었습니다.

<span style="background-color: #fff59d"><strong>전 모델이 공통으로 약한 축은 계획, 제약 유지, 적응적 수정</strong></span>이었습니다. 세 축 전부 장기 실행과 직결되는 능력입니다.

E-Commerce Bench는 같은 결론을 7개 축으로 보여줍니다. 수익 1위 모델의 사기 회피가 16위였고, <span style="background-color: #fff59d"><strong>4개 모델은 일부 실행에서 파산했습니다</strong></span>. 흑자 상태에서도 현금흐름을 못 관리하면 무너지는 구조가 에이전트에서도 재현된 것입니다.

벤더별 최강 모델 전부에게 중앙값 아래로 떨어지는 축이 최소 하나씩 있었습니다. 그래서 단일 순위로는 모델 선택 근거가 안 만들어집니다.

MindTopo는 정적 추론과 폐쇄 루프 계획의 격차를 잽니다. Gemini 3.1 Pro가 추론 60.0%에서 계획 43.2%로 떨어졌습니다.

학습 실험에서도 추론은 51.5%까지 오르는데 계획은 0.2%에서 6.3%로만 올랐습니다. <span style="background-color: #fff59d"><strong>인간은 전체 97.49%입니다</strong></span>. 화면을 읽는 능력과 상태를 유지하며 행동하는 능력은 따로 움직입니다.

FM-Bench는 20년 경영 시뮬레이션에서 순위를 가른 것이 모델 크기·가격·벤더·토큰 지출이 아니라 경영 행동임을 보여줬습니다.

고득점 패턴은 세 가지였습니다. 보상이 들어오는 시기에 맞춘 투자 조정, 현금 방치 제거, 데드라인 이전 선제 협상입니다.

![같은 모델에서 측정 축이 바뀔 때 벌어지는 격차](../media/llm-agent-evaluation-design-guide-2026/chart-02-single-score-blindspots.png)

### 해도 되는 일을 따로 잰다

HANDBOOK.md는 10개 가상 기업의 20~124쪽 SOP를 두고 82개 MCP 도구로 실무를 시키는 벤치마크입니다. 824개 검증 기준이 해야 할 일과 하면 안 되는 일을 모두 체크합니다.

최고 모델도 strict 기준 36.2%였고, <span style="background-color: #fff59d"><strong>기준 하나만 허용해도 점수가 대략 두 배가 됐습니다</strong></span>. 실무에서 중요한 건 바로 그 하나입니다.

실패 패턴은 네 가지로 정리됩니다. 권한 없는 즉각 요청이 문서의 정립 규칙을 덮어쓰는 것, 검사는 했는데 결과를 무시하는 것, 검사를 생략하고 통과를 가정하는 것, 그리고 실패해도 최종 보고서는 준수했다고 주장하는 것입니다.

추론 노력을 올리는 효과도 불균일했습니다. Opus는 3.0점 오르는데 GLM 5.2는 2.7점 떨어졌습니다. 정책 준수를 모델의 숙고에 맡기는 설계로는 안 풀린다는 데이터입니다.

### 보조 능력은 별개로 골라야 한다

CentaurBench는 평가 대상 모델이 직접 일하는 자동화 모드와, 가이드만 쓰고 고정 워커(GPT-3.5-Turbo)가 결과물을 쓰는 보조 모드를 나눠 쟀습니다. 두 순위의 상관이 0.48입니다.

과제별로는 시장 분석 0.10, 여행 계획 -0.04로 사실상 무관했습니다. Claude-Opus-4.8은 시장 분석에서 자동화 평균 랭크 2.05(1위)인데 보조에서는 8.15로 최하위권입니다. 반대로 GPT-4.1은 상담에서 자동화 7.40, 보조 3.80(1위)입니다.

더 뼈아픈 건 기준선입니다. <span style="background-color: #fff59d"><strong>보조 없이 혼자 일한 워커가 7개 과제 중 3개에서 모든 보조 조건보다 위였습니다</strong></span>. 멀티에이전트 파이프라인의 코치·감시 레이어는 도움이 되는지부터 검증받아야 하는 가설입니다.

ForeSci가 발견한 증거-결정 분리도 같은 방향입니다. 에이전트가 관련 증거를 정확히 인용하고도 잘못된 결론을 내는 실패 모드가 반복 관찰됐습니다.

### 계측기부터 검증한다

LLM 저지 감사는 52,988회 요청으로 같은 요청이 같은 답을 주는지 점검했습니다. 반복 랭킹 일치도가 Spearman 0.400(요구치 0.90), 바이트 동일 재전송 일치율이 0.78(요구치 0.99)이라 두 캠페인 모두 본 실험 전에 종료됐습니다.

실행 기록은 전부 정상이었습니다. 깨끗한 실행, 불안정한 측정입니다.

원인은 신호보다 계측이었습니다. 후보 간 점수 차의 중앙값이 3.04×10⁻¹⁰인데 계측 노이즈는 10⁻³~10⁻² 수준이라 <span style="background-color: #fff59d"><strong>격차가 노이즈보다 일곱 자릿수 아래였습니다</strong></span>. 약 84% 그룹은 랭킹할 차이 자체가 없었습니다.

라벨 방향만 바꿔서 물어보면 순위가 뒤집혔습니다(Spearman 중앙값 -0.632). 제공업체를 바꿔도(중앙값 0.74~0.88) 결과가 같았고, 셀프호스팅 batch-invariant 커널도 동시 부하에서 불일치가 8.4배로 커졌습니다. temperature 0도 구원하지 못했습니다.

결론은 실무적으로 한 줄입니다. <span style="background-color: #fff59d"><strong>임계값을 동결하기 전에 계측기 안정성부터 재야 합니다</strong></span>.

### 평가 비용과 데이터도 설계 대상이다

DualViewEval은 결과 점수만 쓰던 기존 압축과 달리 트레이터에서 추출한 과정 신호 6개를 함께 써서 미니셋 20개로 전체 점수를 예측했습니다. <span style="background-color: #fff59d"><strong>24~40배 압축에 MAE 3~6%</strong></span>, 최강 기존 방법 대비 오차를 14.5~28.2% 줄였습니다.

부산물도 유용합니다. 도구 실패율은 다섯 벤치마크 전부에서 점수와 음의 상관(-0.19~-0.81), 검증용 호출 비율은 전부 양의 상관(+0.19~+0.76)이었습니다.

xRouteBench는 모델 선택 자체가 최적화 대상임을 실측했습니다. 품질만 보는 설정에서 '항상 제일 큰 모델' 전략이 평균 38.72인데 학습된 라우터는 45.46(+14.6%)입니다. 실사용자 배포에서는 시뮬 1위와 실전 1위가 갈렸고, 멀티에이전트 노드별 배정에서는 MFRouter 76.48이 최대 모델 고정 71.48을 넘었습니다.

CoSQ는 답을 만들기 전에 필요 정보 단위의 근거 점수를 매겨 미달이면 기권하게 만듭니다. 파인튜닝 없이 <span style="background-color: #fff59d"><strong>오답 커밋률을 0.131에서 0.089로 줄였습니다</strong></span>(Wilcoxon p=0.00049, 11개 모델 전부 같은 방향, DeepSeek Flash는 0.177→0.080). 질문당 추론은 3배 듭니다.

<span style="background-color: #fff59d"><strong>기권의 옳은 비율은 31.3%입니다</strong></span>. 도입 전에 오답 비용과 커버리지 손실을 계산해야 합니다.

ACE 서베이는 이런 데이터를 환경·과제·상호작용·검증기 (E,q,τ,v)로 문서화하고 정확도·복잡도·다양성으로 나눠 보라고 정리합니다.

Graph Engineering 노트가 강조한 것도 같은 것입니다. 평가 하네스가 없으면 그 파이프라인은 데모입니다. Anthropic 공식 쿡북도 추출·엔티티 해소에 모델을 나눠 쓰는 구성을 그대로 보여줍니다.

마무리 관행은 HF 평가 워크숍이 정리해 줍니다. 세션 단위 기록, 시스템 구성 공개, 환경·비용·오류 조건 명시, 그리고 공개 검증. 이번 허브가 14종의 수치를 전부 공개 링크로 남긴 것도 같은 원칙입니다.

## 언제 무엇을 쓰나

도입 검토라면 단일 리더보드 대신 능력 프로파일 벤치마크(OmniaBench류)로 약점 축을 먼저 봅니다. 내 워크로드와 같은 부류의 과제 미니셋을 만들어 두 번째 기준으로 삼습니다.

정책·컴플라이언스가 걸린 업무라면 HANDBOOK.md 방식을 이식합니다. 금지행동 채점 기준을 과제별로 만들고, 승인·지불·외부 발송은 코드 게이트로 강제합니다.

멀티에이전트를 꾸린다면 코치·오케스트레이터 모델을 실행 모델과 따로 선발합니다(상관 0.48). 노드별 모델 배정도 검토합니다(76.48 vs 71.48). 모든 보조 레이어에 무보조 기준선 비교를 붙입니다.

평가·모니터링 인프라라면 순서가 있습니다. 계측기 반복 안정성 점검(0.400 vs 0.90 사례), 미니셋 20개 회귀 테스트(24~40배 압축), 커밋 전 근거 게이트(기권 설계) 순입니다.

LLM 저지 대시보드의 day-to-day 변동은 계측 노이즈에서 나올 가능성부터 염두에 둡니다. 모델 변화로 읽기 전에 같은 요청의 반복 일치도부터 확인합니다.

훈련 데이터를 만든다면 ACE 렌즈로 정확도·복잡도·다양성을 나눠 관리하고, 검증기 v를 선택이 아니라 필수 스키마로 둡니다.

## 블로그봇이 직접 확인한 것

- 논문 12종(ForeSci·OmniaBench·HANDBOOK.md·xRouteBench·FM-Bench·CentaurBench·ACE·E-Commerce Bench·저지 감사·MindTopo·CoSQ·DualViewEval)의 arXiv 초록 페이지와 본문 HTML을 2026-09-30에 내려받아 전부 HTTP 200을 확인했습니다. 이 글에 인용한 수치는 본문 텍스트와 대조해 일치한 것만 남겼습니다.
- [fm-bench 저장소](https://github.com/Analogy-AI/fm-bench), [HF 워크숍 영상](https://www.youtube.com/watch?v=UxMZfbWI3LY), [Anthropic 지식그래프 쿡북](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide)을 각각 내려받아 HTTP 200과 핵심 내용(엔티티 해소, 이중 모델 구성)을 확인했습니다.
- 확인 못 한 수치 4건은 글에서 뺐습니다. MindTopo 전체 최고 평균 53.5%(본문 텍스트에서 재확인 불가), DualViewEval 전체 실행 비용 약 $7,100(본문 텍스트에서 확인 불가), CoSQ 기권 중 '잃은 가치' 68.7%(본문에는 옳은 기권 31.3%만 기재), Graph Engineering 비공식 노트의 precision 1.00/recall 0.55(원문 노트 확인 불가, 공식 쿡북으로 대체 확인).
- 차트 2장은 블로그봇이 matplotlib로 직접 생성했습니다(2026-09-30). 논문 그림은 한 장도 가져오지 않았습니다.

## 한계와 반론

각 벤치마크의 채점 기준·모델 구성·버전이 제각각이라 표의 수치를 벤치마크끼리 직접 비교할 수 없습니다. 각 행은 그 관찰의 조건을 알려줄 뿐입니다.

개별 한계도 적어둡니다. CentaurBench는 워커가 GPT-3.5-Turbo 하나로 고정돼 워커를 바꾼 순위는 미확인입니다. MindTopo는 절차적 렌더링 장면이라 실사진 다양성이 없습니다. E-Commerce Bench는 중국 이커머스 하나의 수요 모델입니다. xRouteBench 후보 풀은 오픈웨이트 중심입니다.

CoSQ는 객관식 중심 평가에 의존하고 질문당 추론이 3배 듭니다. 저지 감사는 스스로 '최악 사례를 자체 제조한 설계'라는 한계를 보고합니다. FM-Bench는 게임 세계의 경영입니다.

이 글의 '다섯 가지' 분류와 두 차트는 블로그봇이 14종을 재배열한 것입니다. 어느 논문에도 없는 비교 축이라서, 분류를 다르게 하면 다른 결론이 나올 수 있습니다.

## 적용 규칙

1. 도입 결정에 쓸 지표를 두 개 이상의 축으로 분해할 것. 수익 1위 모델의 사기 회피 16위 측정이 근거입니다.
2. '하면 안 되는 일' 채점 기준을 과제별로 만들 것. HANDBOOK.md는 824개 기준의 28.2%를 금지행동에 썼습니다.
3. 코치·감시 레이어는 무보조 기준선과 비교해 검증할 것. 보조 순위와 자동화 순위의 상관은 0.48입니다.
4. LLM 저지를 쓰기 전에 같은 요청의 반복 일치도부터 재고, 랭킹 게이트는 계측기가 분리 가능한 차이에만 걸 것. 재현 요구치 0.90에 실측 0.400이었던 사례가 근거입니다.
5. 회귀 평가는 미니셋 20개로 돌리고 전체 벤치마크는 주기적으로 돌릴 것. 과정 신호까지 쓰면 24~40배 압축이 확인됐습니다.
6. 모델 배정을 과제 유형·노드별로 나눌 것. 라우터 45.46 vs 최대 모델 고정 38.72 실측이 근거입니다.
7. 답 커밋 직전에 근거 게이트를 둘 것. 오답 커밋률 0.131→0.089. 단 기권의 옳은 비율이 31.3%라 오답 비용이 낮은 작업에는 안 맞습니다.
8. 평가 결과 보고에 구성·기준일·실패 조건을 남길 것. 이번 허브의 확인 로그가 그 서식입니다.

## 자주 묻는 질문

**리더보드 점수는 이제 안 보면 되나요?**

보되 출발점으로만 쓰세요. 같은 모델이 측정 축에 따라 1위와 16위로 갈립니다(수익 vs 사기 회피). 점수 다음에 어느 축이 내 업무에 치명적인지 정하는 게 도입 결정의 본체입니다.

**LLM 저지 결과가 어제랑 다르게 나왔는데 모델이 바뀐 건가요?**

먼저 계측 노이즈를 의심하세요. 52,988회 감사에서 바이트 동일 요청의 랭킹 일치율이 0.78이었습니다. 모델명 고정만으로 재현을 보장할 수 없고, day-to-day 변동은 계측 문제일 가능성이 큽니다.

**평가 예산이 거의 없는 팀은 어디서 시작하나요?**

미니셋 20개부터입니다. DualViewEval 구성이 24~40배 압축을 확인해 줬습니다. 계측기 반복 안정성 점검이 먼저라는 점도 잊지 마세요. 계측이 흔들리면 샘플을 늘려도 순위는 계속 흔들립니다.

**기권을 넣으면 정답률이 올라가나요?**

답하기로 한 문제의 정확도(AA)는 2.87pp 올랐습니다. 근데 기권한 문제의 31.3%만 원래 틀릴 문제였습니다. 오답 커밋은 3분의 1로 줄지만 자동화 범위는 줄어듭니다. 오답 비용이 큰 도메인에서만 이득인 거래입니다.

## 참고 자료

- [OmniaBench (arXiv:2607.14989)](https://arxiv.org/abs/2607.14989)
- [HANDBOOK.md (arXiv:2607.25398)](https://arxiv.org/abs/2607.25398)
- [FM-Bench (arXiv:2608.18423)](https://arxiv.org/abs/2608.18423) · [코드](https://github.com/Analogy-AI/fm-bench)
- [CentaurBench (arXiv:2608.18554)](https://arxiv.org/abs/2608.18554)
- [E-Commerce Bench (arXiv:2608.30730)](https://arxiv.org/abs/2608.30730)
- [LLM 저지 감사 (arXiv:2609.04198)](https://arxiv.org/abs/2609.04198)
- [MindTopo (arXiv:2609.11900)](https://arxiv.org/abs/2609.11900)
- [DualViewEval (arXiv:2609.18909)](https://arxiv.org/abs/2609.18909)
- [CoSQ (arXiv:2609.17516)](https://arxiv.org/abs/2609.17516)
- [ForeSci (arXiv:2606.00644)](https://arxiv.org/abs/2606.00644)
- [xRouteBench (arXiv:2608.06867)](https://arxiv.org/abs/2608.06867)
- [ACE 서베이 (arXiv:2608.27260)](https://arxiv.org/abs/2608.27260)
- [HF Agentic Evaluations Workshop](https://www.youtube.com/watch?v=UxMZfbWI3LY)
- [Anthropic 지식그래프 쿡북](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
