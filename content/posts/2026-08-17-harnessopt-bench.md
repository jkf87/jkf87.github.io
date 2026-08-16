---
title: "HarnessOpt-Bench: LLM이 에이전트 하네스를 고치는 능력을 측정했더니 모델 선택이 도구 선택보다 1.8배 컸다"
date: 2026-08-17
tags:
  - agent
  - LLM-agent
  - harness
  - benchmark
  - evaluation
  - loop
  - coding-agent
  - Scale-AI
source: arxiv
source_url: https://arxiv.org/abs/2608.06301
authors:
  - conanssam
draft: false
---

arXiv:2608.06301 (2026-08, Scale AI) 정리했습니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>LLM이 다른 에이전트의 하네스를 자동으로 고치는 능력을 처음으로 공통 프로토콜로 측정</strong></span>했고, 그 결과가 예상과 다르게 <span style="background-color: #fff59d"><strong>코딩 도구 선택보다 모델 선택이 1.8배 크게 갈렸다</strong></span>는 것.

같은 모델을 써도 하네스(프롬프트, 도구, 컨트롤 플로우, 메모리, 오케스트레이션 코드)에 따라 성능이 크게 달라집니다. 그래서 하네스를 고치는 작업 자체를 벤치마크화한 겁니다.

## 벤치마크가 측정하는 능력

설정은 이렇습니다.

- 옵티마이저(LLM + 코딩 에이전트)에게 과제용 에이전트의 시드 하네스를 줍니다
- 개발/검증 피드백과 고정된 평가 예산을 주고, 하네스를 수정하게 합니다
- 최종 후보를 지명하면 서버가 옵티마이저가 못 본 테스트 파티션에서 채점합니다

점수는 시드 대비 normalized gain입니다. 수식으로는 (후보 점수 − 시드 점수) ÷ (1 − 시드 점수). 남은 여유(headroom) 중 얼마를 가져왔는지를 재는 값이라 과제 간 비교가 됩니다.

핵심 조건이 하나 더 있습니다. <span style="background-color: #fff59d"><strong>옵티마이저는 자기가 최대화하는 점수를 끝까지 못 봅니다</strong></span>. 테스트 파티션은 지명 후에만 서버가 평가합니다. 보이는 점수에 맞춘 과적합을 구조적으로 차단한 거예요.

## 평가가 조작으로 새지 않게 하는 구조

![신뢰 실행 환경 구조](/images/2026-08-17-harnessopt-bench/fig-1-p2.png)
그림 출처: arXiv:2608.06301 Fig. 1

Fig. 1이 이 벤치마크의 실체를 잘 보여줍니다.

- 옵티마이저는 타깃 에이전트의 하네스 파일만 쓸 수 있습니다
- 평가 결과와 과제 데이터는 읽기만 가능하고 수정은 불가입니다
- 타깃 모델, 환경, 검증기 변경은 금지. 바꾸면 다른 과제가 됩니다
- 모든 평가는 격리된 샌드박스에서, 모델 호출은 게이트웨이를 통과합니다
- 후보는 전부 git 커밋으로 보존되어 감사가 가능합니다

이 경계는 프롬프트로 부탁하지 않고 실행 환경 자체가 강제합니다. 지킬 수 없게 권한이 원래 없는 거예요.

## 실험 구성: 모델 5개와 과제 4개

| 구성 | 값 |
|---|---|
| 옵티마이저 모델 | claude-opus-5, claude-sonnet-5, gpt-5.6-sol, gpt-5.6-terra, kimi-k3 |
| 공유 코딩 하네스 | opencode (전 모델 공통) |
| 네이티브 하네스 | claude-code, codex, kimi-cli |
| 추가 하네스 | goose, mini-swe-agent (GAIA만) |
| 과제 | GAIA, OfficeQA Pro, BrowseComp-Plus, Terminal-Bench 2.0 |
| 데이터 분할 | dev/val/test = 20/40/40, 겹침 없음 |
| 채점 | 테스트 파티션에서 케이스당 3회 평균 |

시드 하네스는 일부러 대충 만든 겁니다. OfficeQA 시드는 OpenAI API 기반 약 130줄, 도구 3개, 24턴 루프짜리 에이전트예요. GAIA 시드는 아예 동작하지 않는 스텁이라 바닥 점수가 0으로 측정됩니다. 개선 여유를 만들어두려는 설계입니다.

## 결과 1: 모델 효과가 하네스 효과보다 1.8배 큽니다

![모델이 하네스보다 크게 갈림](/images/2026-08-17-harnessopt-bench/fig-2-p4.png)
그림 출처: arXiv:2608.06301 Fig. 2

111개 채점 런의 결과입니다.

- 과제와 하네스를 고정하고 모델만 바꾸면 게인이 평균 0.142 움직입니다
- 모델을 고정하고 코딩 하네스만 바꾸면 0.079 움직입니다
- <span style="background-color: #fff59d"><strong>모델 효과가 약 1.8배 큽니다</strong></span>. 둘 다 해상도 밴드보다 큽니다

최강 조합은 <span style="background-color: #fff59d"><strong>OfficeQA 헤드룸의 약 3분의 2, BrowseComp-Plus 헤드룸의 절반</strong></span>을 가져갔습니다. 반대 급부로 최약 조합은 BrowseComp-Plus와 Terminal-Bench에서 0과 구분되지 않았어요. 중간권은 라운드 간 변동보다 차이가 작아서 순위를 매기기 어렵고, 티어로 묶는 게 맞다는 결론입니다.

## 결과 2: 네이티브 코딩 도구의 우위는 일관되지 않습니다

자기 전용 도구를 쓰면 더 잘 고칠 것 같은데, 그렇지 않았습니다.

- 모델별로 공유 하네스(opencode)와 네이티브 하네스를 비교한 20쌍 중 <span style="background-color: #fff59d"><strong>공유 하네스가 11승, 네이티브가 9승</strong></span>입니다
- 방향이 모델별로 갈립니다. GAIA에서 GPT 두 모델은 codex 하에서 <span style="background-color: #fff59d"><strong>4~5개 밴드만큼 낫습니다 (+0.179, +0.131)</strong></span>
- Claude 두 모델과 Kimi는 어느 쪽이든 밴드 1~2개 차이입니다

그래서 특정 모델의 전용 도구만으로 하네스 최적화 능력을 평가하면 편향된 측정이 됩니다. 저자들의 결론도 그렇고요.

## 결과 3: 모델 세대가 올라가면 개선 폭도 커집니다

![세대별 게인 변화](/images/2026-08-17-harnessopt-bench/fig-3-p8.png)
그림 출처: arXiv:2608.06301 Fig. 3

OfficeQA에서 타깃, 시드, 예산, 코딩 도구를 고정하고 옵티마이저 모델 세대만 바꾼 실험입니다.

- GPT 5개 세대: <span style="background-color: #fff59d"><strong>게인이 +0.03에서 +0.49까지 단조 상승</strong></span>. 4계단 중 3계단이 해상도 밴드(±0.045) 초과
- Claude Opus 5개 세대: +0.37에서 +0.59. 비단조지만 첫세대와 마지막 세대 격차는 밴드 초과

즉 <span style="background-color: #fff59d"><strong>하네스 최적화 능력이 모델 릴리스를 따라 잡히는 능력</strong></span>이라는 걸 벤치마크가 실제로 분해해 보여줍니다.

## 이기는 옵티마이저의 행동 패턴

![탐색 폭과 게인의 관계](/images/2026-08-17-harnessopt-bench/fig-4-p9.png)
그림 출처: arXiv:2608.06301 Fig. 4

트레이스 계측으로 찾은 패턴입니다.

- 사전 정의된 8개 레버(프롬프트, 컨텍스트 관리, 스텝 상한, 재시도 정책, 도구 스키마, 답 추출, 검색 정책, 추론 강도) 중 많이 건드릸수록 게인이 커집니다. <span style="background-color: #fff59d"><strong>스피어만 ρ가 4개 과제 전부에서 +0.34~+0.88</strong></span>
- 근데 트레이스 정독은 게인과 음수 관계(<span style="background-color: #fff59d"><strong>-0.31~-0.64</strong></span>)입니다. 상세 트레이스 조회는 <span style="background-color: #fff59d"><strong>111개 셀 중 7개가 통합 16회</strong></span> 썼어요. 케이스별 점수 요약만으로 실패 위치가 잡히니 풀 트레이스는 컨텍스트 비용 낭비였던 겁니다
- 예산은 평가 호출보다 케이스 패스가 먼저 바닥납니다. 중앙값 옵티마이저는 평가 호출을 8회(상한의 4%)만 쓰고 케이스 패스 예산은 82%를 소진. 100개 셀 중 55개가 한 파티션 예산을 끝까지 닳았습니다
- 검증 점수는 낙관적입니다. <span style="background-color: #fff59d"><strong>대부분 셀에서 최종 후보의 테스트 점수가 탐색 중 최고 검증 점수보다 낮습니다</strong></span>

하나 더. 레버 4분의 3을 만지고 수정 7개를 해놓고 원본 시드를 그대로 제출한 조합도 있습니다. 탐색 폭과 최종 반영은 다른 얘기라는 거죠.

## 한계

- 후보는 Python 한정이고 과제마다 타깃 모델이 1개로 고정입니다
- 시드가 과제별 사전 지식입니다. 성숙한 에이전트 고치기와 스텁에서 만들기가 섞여 있어 복잡도를 체계적으로 바꾸진 않았습니다
- 반복된 피드백이 고정 검증기의 아티팩트를 파고들 가능성은 남아 있습니다. 저자들도 인지하고 다음 버전 과제로 적어뒀구요

## 실무에서 가져갈 부분

- 하네스 최적화가 인프라 작업에서 <span style="background-color: #fff59d"><strong>모델 능력의 영역으로 넘어오고 있다</strong></span>는 관측. 모델 업그레이드가 에이전트 개선의 1순위 레버가 됩니다
- 코딩 도구를 바꿔치기하는 실험은 효과가 일관되지 않으니, 그 예산을 모델 비교에 쓰는 게 낫습니다
- 자체 평가 루프를 만들 때 <span style="background-color: #fff59d"><strong>호출 상한보다 케이스 패스 예산이 먼저 바닥난다</strong></span>는 점을 반영하면 됩니다
- 검증 점수를 보고 배포 판단하면 실제보다 좋게 봅니다. <span style="background-color: #fff59d"><strong>홀드아웃 채점을 두는 게 정확합니다</strong></span>

## 더 실습해보고 싶은 분들께

에이전트 하네스와 루프 설계를 더 다뤄보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

원문: https://arxiv.org/abs/2608.06301
