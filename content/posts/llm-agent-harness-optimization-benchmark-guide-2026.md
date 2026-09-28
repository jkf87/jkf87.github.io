---
title: "LLM 에이전트 같은 모델인데 점수가 다를 때: 하네스 효과와 최적화 벤치마크 16편 정리"
date: 2026-09-28
author: 한준구(코난쌤)
description: "같은 모델인데 하네스만 바꿔 성공률이 2.5배 갈리는 이유를 벤치마크 16종으로 짚고, Self-Harness·AI4AI·RHI 등 하네스 자동 개선 루프의 검증된 수치와 적용 기준을 정리했습니다."
tags: [LLM 에이전트, 하네스, 벤치마크, 에이전트 최적화]
refactor_hub_id: harness-self-improve-12
aliases:
  - posts/2026-08-07-harnessopt-bench-llm-harness-optimization
  - posts/2026-07-29-frozen-agent-harness-control-system
  - 2026-07-04-evopolicygym-autonomous-policy-evolution
  - posts/2026-07-16-harness-handbook-agent-harness-evolution
  - posts/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure
  - posts/2026-07-19-memoharness-agent-harness-learns-from-experience
  - posts/2026-07-21-recursive-harness-self-improvement
  - posts/2026-07-25-tencent-workbuddy-bench-coding-agent-benchmark
  - posts/2026-08-03-agent-harness-distillation-inference-time-harness-extraction
  - posts/2026-08-12-a2e-agent-auditing-engine
  - posts/2026-08-14-ai4ai-test-time-strong-to-weak-harness
  - posts/2026-08-14-self-harness-self-improving-agent
  - posts/2026-08-17-harnessopt-bench
  - posts/2026-08-18-clawgym2-blackbox-rl-harness
  - posts/self-harness-self-improving-harness-2026-08-24
  - posts/harness-bench-config-level-agent-eval-2026-08-25
  - posts/2026-09-02-gabench-graph-analysis-agents
  - posts/2026-09-19-llm-agent-self-harness-benchmark-harnessdev
draft: false
sources_read: "초록 16종 전수 대조(arXiv abs, 2026-09-28) + HarnessOpt-Bench·Harness-Bench·GABench·HarnessDev·MemoHarness·Self-Harness·Harness-Handbook·frozen-control·WorkBuddy 본문(HTML) 수치 대조; 코드·데이터: AgentCompass(EMNLP 2026) 저장소 공개 확인, A²E 코드 공개(논문 명시), WorkBuddy·Harness-Bench 데이터 공개(논문 명시), 나머지는 논문·프로젝트 링크 명시 수준으로 확인"
novelty_vs_paper: "측정 7종·개선 6종·보조 3종을 같은 축(무엇을 바꾸나/검증 방식/대표 수치/조건)으로 재편한 비교와 자체 도표 2장, 수치 재검증 기록은 블로그봇 작성분이고, 각 연구의 방법·수치·기여는 해당 논문의 것입니다"
---
## 한눈에 보는 결론

같은 모델, 같은 과제인데 하네스만 바꿨더니 성공률이 34.94%에서 87.80%로 갈렸습니다. <span style="background-color: #fff59d"><strong>2.5배 차이</strong></span>입니다. 모델은 GLM-5-turbo 하나였고, 바꾼 건 에이전트를 실제로 돌리는 실행틀, 즉 하네스가 전부였습니다. 그래프 분석 벤치마크 GABench가 잰 숫자입니다.

이 글은 옛 글 18편을 하나로 합친 허브입니다. 하네스 효과를 측정한 벤치마크 7종, 하네스를 자동으로 고치는 연구 6종, 보조 축 3종, 총 16개 출처를 같은 잣대로 비교했습니다. 옛 글 URL은 이 글로 연결됩니다.

요약하면 세 줄입니다.

- 에이전트 점수는 모델과 하네스 조합의 점수입니다. <span style="background-color: #fff59d"><strong>하네스 간 격차만 23.8점</strong></span>입니다(Harness-Bench).
- 하네스를 고치는 능력 자체가 모델 능력으로 편입됐습니다. 어떤 모델이 고치느냐가 어떤 코딩 도구로 고치느냐보다 <span style="background-color: #fff59d"><strong>약 1.8배 큽니다</strong></span>(HarnessOpt-Bench).
- 모델 가중치를 못 바꿔도 루프는 통합니다. 같은 모델이 자기 하네스를 고른 <span style="background-color: #fff59d"><strong>9개 조합 전부에서 통과율이 올랐고 최대 +132%</strong></span>입니다(Self-Harness).

| 질문 | 검증된 숫자 | 출처 |
| --- | --- | --- |
| 같은 모델, 하네스만 바꾸면? | 그래프 ML 성공률 34.94 → 87.80% | GABench |
| 코딩 과제에서는? | Terminal-Bench 2.1 35.2 → 49.6% | HarnessDev |
| 하네스 간 격차는? | 종합점수 최고 76.2 vs 최저 52.4(23.8점) | Harness-Bench |
| 누가 고치느냐의 효과는? | 모델 효과 0.142 vs 코딩 도구 효과 0.079 | HarnessOpt-Bench |
| 스스로 고치면 오르나? | 9개 조합 전부 상승, 최대 상대율 +132% | Self-Harness |
| 강한 모델이 만들어주면? | 약한 타깃 평균 0.49 → 0.91 | AI4AI |

기준일은 2026-09-28이고, 이 글에 실은 수치는 전부 초록 또는 본문에서 다시 확인했습니다. 확인 방법은 아래 블로그봇이 직접 확인한 것 섹션에 적어뒀습니다.

## 무엇을 비교했나

측정·진단 계열 7종입니다.

1. [Harness-Bench](https://arxiv.org/abs/2605.27922) — 하네스 설정 간 격차 측정
2. [GABench](https://arxiv.org/abs/2608.01684) — 그래프 분석에서 하네스·도구 효과 측정
3. [A²E](https://arxiv.org/abs/2608.07346) — 하네스 감사 엔진
4. [AgentCompass](https://github.com/open-compass/AgentCompass) — 벤치마크·하네스·환경 분리 평가 인프라(EMNLP 2026)
5. [Tencent WorkBuddy Bench](https://arxiv.org/abs/2607.20911) — 이중 하네스 채점 코딩 벤치마크
6. [HarnessDev](https://arxiv.org/abs/2609.01437) — 하네스 생성·진화 능력 벤치마크
7. [HarnessOpt-Bench](https://arxiv.org/abs/2608.06301) — 하네스 최적화 능력 벤치마크

개선 루프 계열 6종입니다.

8. [Self-Harness](https://arxiv.org/abs/2606.09498) — 같은 모델의 자기 하네스 개선 루프
9. [MemoHarness](https://arxiv.org/abs/2607.14159) — 경험 은행 기반 적응형 하네스
10. [RHI](https://arxiv.org/abs/2607.15524) — 프롬프트 수준 하네스의 재귀 개선(Sakana AI)
11. [AI4AI](https://arxiv.org/abs/2608.12307) — 강한 모델이 약한 모델용 하네스 컴파일
12. [ClawGym II](https://arxiv.org/abs/2608.16798) — 상용 하네스를 통째로 RL 학습 환경으로
13. [EvoPolicyGym](https://arxiv.org/abs/2607.02440) — 정책 코드 자율 진화 평가

보조 축 3종입니다.

14. [Harness Handbook](https://arxiv.org/abs/2607.13285) — 하네스 수정 위치를 찾는 행동 지도
15. [Agent Harness Distillation](https://arxiv.org/abs/2607.28147) — 하네스 유출 공격과 방어
16. [하네스 제어 계열 대조군](https://arxiv.org/abs/2607.25415) — 작은 고정 행동 공간 + 고전 RL

## 방법 비교

| 연구 | 하네스를 어떻게 다루나 | 검증 방식 | 대표 수치 | 전제 조건 |
| --- | --- | --- | --- | --- |
| Self-Harness | 약점 채굴→수정 제안→회귀 검증 루프 | held-in/held-out 비회귀 게이트 | 9개 조합 전부 상승, 최대 +132% | 검증기 있는 벤치마크 3종 |
| AI4AI | 강한 빌더가 하네스를 코드로 컴파일 | 숨겨진 3,900문항 최종 평가 | 0.49 → 0.91 | ToM 4종, 정형화 쉬운 과제 |
| MemoHarness | 6차원 분해 + 이중 경험 은행 | 테스트 시간 검색 적응 | T-B 0.722→0.806, 총비용 $6.89 | 캐시 히트 가정 |
| RHI | 프롬프트 수준 명세 + 짝 비교 피드백 | 30개 ML 연구 태스크 | 비용 최대 60% 절감 | 합성 태스크, 2~3회 반복 수렴 |
| ClawGym II | 서빙 프록시·prefix tree로 블랙박스 RL | 200~400스텝 안정 학습 | Pass@1 +9.98p / +14.81p | 대규모 샌드박스 인프라 필요 |
| HarnessOpt-Bench | 하네스 최적화 능력 자체를 채점 | 테스트 파티션 차단 111 런 | 모델 효과 0.142 vs 도구 0.079 | 시드·파티션 의존 |
| Harness-Bench | 하네스 설정을 실험 변수로 | 106과제 5,194트레이토리 | 76.2 vs 52.4 | 샌드박스 오프라인 |
| GABench | 도구 84개 조합 과제 | 검증 가능한 정답 10,400태스크 | 87.80 vs 34.94 | 그래프 도메인 |

## 측정 계열 결과: 같은 모델, 하네스 교체 실험

![같은 모델 또는 동일 조건에서 하네스만 바꿨을 때 점수 격차](../media/llm-agent-harness-optimization-benchmark-guide-2026/harness-swap-spread.png)

GABench의 실험이 제일 읽기 쉽습니다. GLM-5-turbo 하나를 도구 스키마와 시스템 프롬프트를 고정한 채 세 하네스에 올렸더니 그래프 ML 성공률이 Claude Code 87.80%, Hermes 60.22%, OpenClaw 34.94%로 갈렸습니다.

입력 토큰도 같은 방향입니다. <span style="background-color: #fff59d"><strong>가장 싼 하네스가 15,793토큰으로 가장 절약했고 가장 비싼 하네스가 61,431토큰을 쓰고도 성적이 가장 낮았습니다</strong></span>. 도구 호출 개수보다 호출의 질이 성적을 결정한다는 게 논문의 결론입니다.

Harness-Bench는 격차의 크기를 잽니다. 106개 샌드박스 과제를 하네스 설정별로 돌려 최고 76.2점, 최저 52.4점을 기록했습니다. 논문은 <span style="background-color: #fff59d"><strong>에이전트 성능을 모델-하네스 구성 단위로 보고하라고 권고</strong></span>합니다.

HarnessDev는 방향을 뒤집어 하네스를 만드는 능력을 잽니다. 같은 GPT-5가 Terminal-Bench 2.1에서 Terminus 2 안에서는 35.2%, Codex CLI 안에서는 49.6%를 냈습니다. 생성된 하네스의 최고 종합점수는 67.8로 휴먼 레퍼런스 86.2에 못 미칩니다. 반복 개선 단계는 이득이 불안정하게만 전이됩니다.

WorkBuddy Bench는 모든 모델을 두 하네스로 동시 채점합니다. Claude Opus 4.8의 Code 점수가 CodeBuddy Code 74.4, Claude Code 77.9로 측정 환경에 따라 달라졌고, 순위도 영역마다 움직입니다. A²E는 이 관찰을 감사 엔진으로 일반화해서, 조합마다 우승자가 달라지고 모든 태스크를 이기는 조합은 없다고 정리했습니다.

HarnessOpt-Bench는 누가 하네스를 고치느냐를 분해했습니다. 111개 채점 런에서 모델만 바꿀 때 게인이 평균 0.142 움직이고 코딩 도구만 바꿀 때 0.079 움직였습니다. GPT 세대가 오를수록 개선 폭이 +0.03에서 +0.49까지 커졌습니다.

이기는 옵티마이저의 습관도 나왔습니다. 여덟 개 수정 축을 넓게 건드릴수록 게인이 커지고(Spearman +0.34~+0.88), <span style="background-color: #fff59d"><strong>트레이스를 깊게 읽을수록 게인이 줄었습니다(-0.31~-0.64)</strong></span>. 로그 정독에 시간을 쓰는 것과 성적은 반대 방향으로 움직였다는 뜻입니다.

## 개선 계열 결과: 가중치 고정, 하네스 개선 전후 수치

![가중치 고정, 하네스 개선 루프의 전후 수치](../media/llm-agent-harness-optimization-benchmark-guide-2026/harness-improvement-loops.png)

Self-Harness의 구조가 실무 이식에 가장 가깝습니다. 같은 모델이 자기 실패 궤적을 클러스터링하고, 최소 수정안을 여러 개 만들고, 승격 게이트를 통과한 수정만 남깁니다. <span style="background-color: #fff59d"><strong>held-in과 held-out 양쪽에서 떨어지지 않을 때만 수정을 승격</strong></span>합니다.

결과는 9개 모델-벤치마크 조합 전부에서 상승입니다. AppWorld의 GLM-5는 44.4에서 85.0까지 올랐고, Qwen3.5-35B-A3B는 같은 벤치마크에서 22.5에서 52.2로 올랐습니다. SWE-bench Verified에서는 19.5에서 41.5로, Terminal-Bench 2.0에서는 40.5에서 61.9로 움직였습니다.

AI4AI는 역할 분담 버전입니다. 강한 빌더 모델이 과제 구조를 하네스 코드로 컴파일하면 <span style="background-color: #fff59d"><strong>약한 타깃 모델의 평균 정확도가 0.49에서 0.91로 올라갔습니다</strong></span>. 타깃이 약할수록 상승폭이 크고, 빌더의 추론 노력을 올릴수록 품질이 단조 증가했으며, 플랫폼 차이는 빌더 차이보다 작았습니다. <span style="background-color: #fff59d"><strong>이미 잘 푸는 강한 타깃에는 하네스가 방해가 되는 사례도 있었다고 논문이 밝힙니다</strong></span>.

MemoHarness는 경험을 쌓는 쪽입니다. 하네스를 6개 편집 차원으로 쪼개고 케이스별 진단과 증류 패턴을 이중 은행에 저장해서, 새 케이스에 검색 한 번으로 적응합니다. Terminal-Bench 0.722→0.806, LiveCodeBench 0.900→0.967, FinanceAgent 0.600→0.767입니다. 총비용 $6.89는 상당량이 캐시된 컨텍스트라는 조건이 붙습니다.

RHI는 프롬프트로 서술된 하네스를 자기 실행 이력의 짝 비교 피드백으로 개정합니다. 30개 ML 연구 태스크에서 2~3회 반복으로 최대 추론 노력 설정을 넘어섰고 <span style="background-color: #fff59d"><strong>추론 비용은 최대 60% 줄었습니다</strong></span>.

ClawGym II는 하네스 내부를 열지 않고 학습하는 경로입니다. 모델 호출 경계의 프록시 기록과 prefix tree 재구성만으로 PPO/GRPO 학습을 돌려 <span style="background-color: #fff59d"><strong>ClawGym-Bench Pass@1을 +9.98p(OpenClaw 경로), +14.81p(Claude Code 경로) 올렸습니다</strong></span>. 이질적 하네스를 한 루프에 묶는 학습도 단일 하네스 학습에 뒤지지 않았습니다. EvoPolicyGym은 이 생태계의 리더보드 역할로, GPT-5.5가 16개 RL 환경 전체에서 Top-2에 올랐습니다.

보조 축 결과 두 건도 정리해둡니다. Harness Handbook은 하네스 수정의 병목을 코드 생성보다 수정 위치 찾기로 짚고, 행동 중심 지도로 계획 승률을 Codex 28.3→38.3%, Terminus-2 26.7→45.6% 올리고 플래너 토큰을 각각 12.7%, 8.6% 아꼈습니다. Agent Harness Distillation은 잘 만든 하네스가 프롬프트 몇 번으로 역설계될 수 있음을 보여주는 보안 연구입니다.

고전 RL 대조군 연구도 인용합니다. 작은 고정 행동 공간에서 DSPy 정적 기준선이 도구 사용 도메인 96% 성공률·에피소드당 285토큰을 기록한 반면 REINFORCE가 62%·680토큰에 그쳤다는 보고입니다. 하네스 최적화 방법 선택에 참고할 대조 데이터로 남깁니다.

## 언제 무엇을 쓰나

- 도입 전 비교가 먼저입니다. AgentCompass나 A²E 식으로 벤치마크·하네스·환경을 분리하고, 내 워크로드와 비슷한 과제에서 하네스 후보를 고정 비교하세요.
- 싼 모델을 쓰는 예산 환경이면 하네스 튜닝이 우선순위입니다. AI4AI에서 약한 타깃일수록 상승폭이 컸습니다.
- 검증기가 있는 반복 업무는 Self-Harness 루프 후보입니다. 비회귀 게이트가 전제입니다.
- 정형화 가능한 과제를 소형 모델로 돌린다면 AI4AI식 하네스 컴파일을 먼저 시도하세요.
- 프롬프트 수준 하네스라면 RHI식 짝 비교 개선이 저렴합니다.
- 샌드박스·프록시 인프라가 있는 팀만 ClawGym II 경로가 현실적입니다.
- 하네스가 커져서 수정 위치를 못 찾겠으면 Handbook식 행동 지도부터 만드세요.
- 하네스가 자산인 조직은 AHD가 지적한 유출 표면 점검을 먼저 하세요.

## 블로그봇이 직접 확인한 것

- 초록 대조: 16개 출처의 arXiv 초록 페이지를 2026-09-28에 전수 확인했습니다. RHI의 60% 비용 절감, AI4AI의 0.49→0.91, Self-Harness의 9/9 상승과 +132%, ClawGym II의 +9.98/+14.81, HarnessOpt-Bench의 111 런과 모델 우위는 초록에 직접 적혀 있습니다.
- 본문 수치 대조: HarnessOpt-Bench, Harness-Bench, GABench, HarnessDev, MemoHarness, Self-Harness, Harness Handbook, 고전 RL 대조군, WorkBuddy Bench의 HTML 전문을 내려받아 이 글의 수치가 실재하는지 검색으로 확인했습니다.
- 저장소 확인: AgentCompass 저장소(EMNLP 2026)가 열려 있음을 확인했습니다. A²E도 코드 공개를 논문에 명시했습니다.
- 뺀 것: A²E의 세부 토큰 수치(96,704/10,122 등), MemoHarness의 크로스 모델 전이 수치, EvoPolicyGym의 종합점수 0.891과 예산 128, WorkBuddy의 GPT-5.5 Security 수치는 현재 버전 본문에서 확인되지 않아 <span style="background-color: #fff59d"><strong>이 글에서 제외했습니다</strong></span>.
- <span style="background-color: #fff59d"><strong>도표 2장은 블로그봇이 matplotlib으로 새로 그렸습니다</strong></span>. 논문 그림을 가져오지 않았습니다.

## 한계와 반론

- 연구마다 하네스의 정의와 경계가 다릅니다. GABench의 하네스와 HarnessDev의 하네스는 같은 단어로 재는 다른 대상입니다. 그래서 이 글은 방향과 크기의 비교로만 읽어야 합니다.
- Self-Harness는 저자가 스스로 명시했듯 고정 벤치마크 안의 유계 수정입니다. 열린 환경 자기개선으로 읽으면 과대해석입니다.
- AI4AI 과제는 ToM 4종으로, 규칙으로 컴파일되기 쉬운 성격입니다. 대화·창작류에서 같은 폭이 나온다는 보장이 없습니다.
- HarnessDev의 반복 개선 단계는 이득이 불안정하고 홀드아웃 전이도 부분적입니다. 자기개선 루프의 상용화 성숙도는 아직입니다.
- 제 검증은 초록·본문 수치 대조와 저장소 확인까입니다. 재실행은 하지 않았고, ClawGym II는 개인이 돌릴 규모가 아닙니다.
- 벤치마크 수치는 시드·파티션·버전에 따라 움직입니다. A²E처럼 논문 개정판에서 수치 표가 정리되는 경우도 직접 봤습니다.

## 적용 규칙

1. 에이전트 점수를 비교할 때는 모델과 함께 하네스와 환경을 명시하고, 비교할 때는 하네스를 고정하세요.
2. 모델을 바꾸기 전에 같은 태스크를 하네스 후보 둘로 돌려 턴 수, 호출 수, 토큰을 함께 재세요.
3. 자기 하네스 개선 루프를 돌린다면 held-in/held-out 비회귀 게이트를 반드시 두세요. <span style="background-color: #fff59d"><strong>게이트 없는 자기수정은 드리프트 위험이 있습니다</strong></span>.
4. 디버깅은 풀 트레이스 정돈부터 하지 마세요. 점수 요약으로 실패 위치를 먼저 잡으세요. 트레이스 정독과 게인의 상관은 음수였습니다.
5. 하네스 수정은 한 레버만 반복하지 말고 프롬프트, 컨텍스트 관리, 스텝 상한, 재시도, 도구 스키마, 답 추출, 검색 정책, 추론 강도의 여덟 축을 순회하세요.
6. 검증 점수만 보고 배포 판단을 하지 마세요. 홀드아웃 채점을 따로 두세요.
7. 이미 잘 풀리는 과제에 강한 타깃을 쓴다면 하네스를 추가로 얹지 마세요. 하락 사례가 보고됐습니다.
8. 하네스를 바꿀 때마다 실행 기록을 케이스 단위로 남기세요. MemoHarness의 경험 은행 구조가 그 이유입니다.

## 자주 묻는 질문

하네스가 정확히 무엇인가요?

모델을 둘러싼 실행틀 전부입니다. 시스템 프롬프트, 도구 세트와 스키마, 실행 루프 정책, 메모리·컨텍스트 관리, 검증 절차가 하네스에 들어갑니다. 모델 가중치를 제외한 에이전트의 실행 요소라고 보면 됩니다.

모델을 그냥 좋은 걸로 바꾸면 안 되나요?

HarnessOpt-Bench의 측정에서 모델 효과가 도구 효과보다 컸습니다. 모델 업그레이드가 여전히 1순위 레버입니다. 근데 비용, 데이터 규정, 배포 제약으로 모델을 못 바꾸는 환경에서는 하네스가 남은 레버이고, 타깃이 약할수록 하네스의 폭이 커집니다.

자기 하네스 개선은 위험하지 않나요?

승격 게이트가 핵심입니다. Self-Harness는 held-in과 held-out 양쪽에서 떨어지지 않는 수정만 남기고 나머지는 버립니다. 게이트를 통과 못 하는 수정이 버려지는 구조라야 안전하게 돌아갑니다.

벤치마크 점수는 어떻게 읽어야 하나요?

하네스와 환경을 명시한 점수만 비교하세요. 명시가 없는 에이전트 점수는 모델 점수로 읽으면 비교 자체가 성립하지 않습니다. WorkBuddy Bench처럼 채점 하네스를 두 개 두고 차이를 공개하는 사례가 참고가 됩니다.

## 참고 자료

- [Harness-Bench (arXiv 2605.27922)](https://arxiv.org/abs/2605.27922)
- [GABench (arXiv 2608.01684)](https://arxiv.org/abs/2608.01684)
- [A²E (arXiv 2608.07346)](https://arxiv.org/abs/2608.07346)
- [AgentCompass (GitHub)](https://github.com/open-compass/AgentCompass)
- [Tencent WorkBuddy Bench (arXiv 2607.20911)](https://arxiv.org/abs/2607.20911)
- [HarnessDev (arXiv 2609.01437)](https://arxiv.org/abs/2609.01437)
- [HarnessOpt-Bench (arXiv 2608.06301)](https://arxiv.org/abs/2608.06301)
- [Self-Harness (arXiv 2606.09498)](https://arxiv.org/abs/2606.09498)
- [MemoHarness (arXiv 2607.14159)](https://arxiv.org/abs/2607.14159)
- [RHI (arXiv 2607.15524)](https://arxiv.org/abs/2607.15524)
- [AI4AI (arXiv 2608.12307)](https://arxiv.org/abs/2608.12307)
- [ClawGym II (arXiv 2608.16798)](https://arxiv.org/abs/2608.16798)
- [EvoPolicyGym (arXiv 2607.02440)](https://arxiv.org/abs/2607.02440)
- [Harness Handbook (arXiv 2607.13285)](https://arxiv.org/abs/2607.13285)
- [Agent Harness Distillation (arXiv 2607.28147)](https://arxiv.org/abs/2607.28147)
- [Frozen-agent harness control (arXiv 2607.25415)](https://arxiv.org/abs/2607.25415)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
