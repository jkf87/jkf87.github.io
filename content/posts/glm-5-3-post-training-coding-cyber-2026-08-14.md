---
title: "GLM-5.3: 같은 베이스 모델에서 포스트트레이닝만 키웠더니 생긴 일"
date: 2026-08-14
tags:
  - GLM
  - coding-agent
  - post-training
  - RL
  - cyber
  - agent
  - Z.ai
  - open-weights
---

![](/images/glm-5-3-post-training-coding-cyber-2026-08-14/hero-performance.png)

Z.ai가 GLM-5.3을 공개했습니다. 핵심 문장은 짧습니다. <span style="background-color: #fff59d"><strong>베이스 모델은 GLM-5.2와 같고, 성능 향상은 전부 post-training에서 나왔다는 겁니다.</strong></span>

이게 중요한 이유는 모델 크기나 아키텍처 이야기가 아니기 때문입니다. <span style="background-color: #fff59d"><strong>GLM-5.3 글의 주인공은 모델 자체보다 `환경(environment)`입니다.</strong></span> 더 많은 장기 과제 환경, 더 다양한 실제 업무형 task, 더 많은 RL 학습 compute를 넣었더니 코딩 에이전트 성능이 크게 올랐고, 예상보다 빠르게 사이버 취약점 탐지·익스플로잇 능력도 올라왔다는 내용입니다.

원문: [GLM-5.3: Frontier Coding with Emergent Cyber Capabilities](https://z.ai/blog/glm-5.3)

## GLM-5.3의 핵심은 학습 환경입니다

원문 첫 문장이 거의 선언입니다.

> Scaling post-training is all we did for GLM-5.3.

번역하면 이렇습니다. <span style="background-color: #fff59d"><strong>GLM-5.3에서 우리가 한 일은 post-training을 스케일한 것뿐이다.</strong></span> GLM-5.2에서 이미 긴 컨텍스트 처리를 위한 IndexShare, 장기 과제 RL을 위한 SAO, 대규모 비동기 학습 프레임워크 slime을 만들었고, GLM-5.3에서는 그 스택 위에서 한 달 동안 더 많은 환경, 더 다양한 과제, 더 많은 학습 compute를 밀어 넣었다는 설명입니다.

Z.ai가 공개한 주요 주장도 세 가지입니다.

1. 코딩 성능 강화: 사내 Z.ai Code Bench에서 GLM-5.2 대비 50% 개선. Terminal Bench 3.0, Agents' Last Exam 등 공개 벤치마크에서도 오픈소스 SOTA급 결과.
2. 사이버 능력의 출현: post-training을 키우는 과정에서 취약점 발견과 exploitation chain reasoning 능력이 예상보다 빠르게 성장.
3. 오픈 웨이트 예정: 출시 후 2주 뒤, safety evaluation과 hardening을 마치고 weight를 공개할 예정.

여기서 포인트는 “새 모델이 더 똑똑해졌다”보다, <span style="background-color: #fff59d"><strong>검증 가능한 장기 업무 환경을 많이 만들고 그 안에서 학습시키는 능력이 모델 성능의 병목이 되고 있다는 쪽에 가깝습니다.</strong></span>

## 벤치마크 표에서 봐야 할 숫자들

원문 표는 꽤 큽니다. 전체를 그대로 옮기기보다, GLM-5.2에서 GLM-5.3으로 바뀐 부분을 중심으로 보면 흐름이 보입니다.

| 영역    |                   벤치마크 | GLM-5.2 | GLM-5.3 |      변화 |
| ------- | -------------------------: | ------: | ------: | --------: |
| Coding  |         Terminal Bench 3.0 |     4.6 |    28.3 | 크게 상승 |
| Coding  |               DeepSWE v1.1 |    46.2 |    66.9 |    +20.7p |
| Coding  | ProgramBench Almost Solved |     9.5 |    19.0 |       2배 |
| Coding  |                FrontierSWE |    67.5 |    78.1 |    +10.6p |
| Coding  |          SWE-Marathon v1.1 |    19.4 |    42.5 |    +23.1p |
| Cyber   |                   CyberGym |    77.2 |    84.5 |     +7.3p |
| Cyber   |               ExploitBench |    24.4 |    54.4 |  2배 이상 |
| Agentic |     AutomationBench v1.0.6 |    26.2 |    48.2 |    +22.0p |
| Agentic |               HLE w/ Tools |    54.7 |    62.5 |     +7.8p |

특히 <span style="background-color: #fff59d"><strong>Terminal Bench 3.0의 4.6 → 28.3, SWE-Marathon의 19.4 → 42.5, AutomationBench의 26.2 → 48.2</strong></span>가 눈에 띕니다. 단순 코드 생성보다 긴 시간 동안 도구를 쓰고, 파일을 고치고, 검증하고, 다시 수정하는 쪽에서 상승 폭이 큽니다.

다만 닫힌 frontier 모델을 전부 이겼다는 뜻은 아닙니다. 예를 들어 원문 표에서 Terminal Bench 3.0은 GPT-5.6 Sol 34.6, Fable 5 33.7, GLM-5.3 28.3입니다. DeepSWE도 GPT-5.6 Sol 72.7, Fable 5 69.7, GLM-5.3 66.9입니다. <span style="background-color: #fff59d"><strong>오픈 웨이트 모델 기준으로 매우 강해졌지만, 폐쇄형 최상위 모델과의 격차는 아직 남아 있습니다.</strong></span>

![](/images/glm-5-3-post-training-coding-cyber-2026-08-14/zai-code-bench.png)

원문에서 더 흥미로운 건 사내 Z.ai Code Bench입니다. GLM-5.3은 Max effort에서 task당 약 75K output token으로 34.5%를 기록했고, GLM-5.2는 약 96K output token으로 23.4%였습니다. High effort에서는 GLM-5.3이 약 50K output token으로 31.4%, Claude Opus 4.8은 120K token으로 29.5%였다고 합니다.

즉 <span style="background-color: #fff59d"><strong>성능과 토큰 효율이 같이 좋아졌다는 주장입니다.</strong></span> 장기 과제에서 이 차이는 큽니다. 코딩 에이전트 비용은 “한 번 답변”보다 “몇 시간 동안 얼마나 많은 토큰을 태우는가”로 결정되기 때문입니다.

## 코딩 성능의 핵심은 실제 업무에 가까운 환경입니다

GLM-5.3에서 <span style="background-color: #fff59d"><strong>Z.ai가 키운 것은 “문제집”보다 “업무 환경”에 가깝습니다.</strong></span> 원문은 어떤 ML infrastructure task를 예로 듭니다. 모델에게 엔지니어와 같은 작업 환경을 줍니다. compute cluster, storage system, 내부 문서, codebase, 실험 결과에 접근할 수 있게 하고, training stack 병목을 진단하고, 최적화를 구현하고, 실험을 돌리고, correctness를 유지하면서 end-to-end speedup을 내야 합니다.

이건 알고리즘 문제 하나 푸는 것과 다릅니다. 사용자가 일을 쪼개서 계속 시키는 구조와도 거리가 있습니다. 모델이 꽤 큰 작업 단위를 끝까지 소유해야 합니다.

원문 표현을 조금 풀면 이렇습니다.

> 환경이 유용하려면 executable, verifiable, real professional work에 가까워야 한다. 그리고 손으로 몇 개 만드는 수준이 아니라 많이 필요하다.

그래서 Z.ai는 환경을 end-to-end로 합성하는 pipeline을 만들었다고 합니다. research agent가 실제 업무에서 task pattern을 모아 runnable long-horizon environment로 바꾸고, judge agent가 그 과제를 풀어보면서 실제로 풀 수 있는지 확인합니다. verifier는 reference solution 없이 합성하고, solver trajectory를 보면서 reward shortcut을 찾아 막습니다. oracle, no-op, unsolved-state check를 통과한 verifier만 binary reward로 학습에 직접 씁니다.

이 대목은 요즘 에이전트 학습 논의와 정확히 맞닿아 있습니다. 모델만 키우는 시대에서, <span style="background-color: #fff59d"><strong>task harness와 verifier를 얼마나 잘 만들 수 있는가</strong></span>가 경쟁력이 되는 흐름입니다. benchmark는 freeze된 환경이고, training environment는 계속 진화하는 환경이라는 관점으로 보면 이해가 쉽습니다.

## 사이버 능력은 예상보다 빠르게 커졌습니다

원문에서 가장 조심해서 읽어야 할 부분은 사이버 능력입니다. Z.ai는 post-training mix에 vulnerability discovery data와 environment를 넣었습니다. 취약점을 더 잘 찾고 추론할 것이라고는 예상했지만, 학습 스케일을 키우자 능력이 예상보다 빠르게 발전했다고 합니다.

중요한 문장은 이겁니다. GLM-5.3은 isolated flaw를 찾는 수준을 넘어, <span style="background-color: #fff59d"><strong>여러 단계의 exploitation을 이어 붙여 coherent plan을 세우기 시작했다</strong></span>는 설명입니다.

![](/images/glm-5-3-post-training-coding-cyber-2026-08-14/cyber-benchmarks.png)

숫자는 이렇습니다.

| 벤치마크           | GLM-5.2 |   GLM-5.3 | 원문 해석                                                    |
| ------------------ | ------: | --------: | ------------------------------------------------------------ |
| CyberGym           |    77.2 |      84.5 | white-box source code에서 취약점을 찾고 fault trigger로 검증 |
| ExploitBench       |    24.4 |      54.4 | 실제 취약점과 exploitation에 대한 더 깊은 추론               |
| ExploitGym 2h / 6h | 29 / 39 | 105 / 130 | 시간 예산 안에서 완료한 exploitation task 수                 |

흥미로운 패턴은 “exploitation chain 위쪽으로 갈수록 GLM-5.2 대비 상승 폭이 커진다”는 점입니다. CyberGym은 +7.3p지만, <span style="background-color: #fff59d"><strong>ExploitBench는 2배 이상이고, ExploitGym은 2시간 기준 29 → 105입니다.</strong></span> 동시에 닫힌 모델과의 격차도 그쪽에서 더 큽니다. 원문도 이렇게 말합니다. 능력이 가장 빠르게 커지는 곳이, 아직 가장 뒤처져 있는 곳이기도 하다.

실제 코드베이스 대상 결과도 공개했습니다. GLM-5.2 이후 중국의 여러 보안팀과 함께 실제 codebase에 모델을 적용했고, 전문가 검토·screening·deduplication을 거쳐 <span style="background-color: #fff59d"><strong>269개 프로젝트에서 2,436개 취약점을 식별했다고 합니다.</strong></span> 그중 1,097개는 medium-to-high severity입니다. 공개 ledger 기준으로는 53건이 공개되었고, 2,383건은 embargo 상태입니다. 가장 오래된 결함은 1981년에 들어간 것으로, 평균적으로 취약점이 발견 전까지 26.6년 남아 있었다고 합니다.

이 부분은 기술적으로는 매우 강한 신호이지만, 동시에 안전 이슈도 큽니다. Z.ai가 weight 공개를 2주 뒤로 미루고 safety evaluation과 hardening을 언급한 이유도 여기에 있습니다. 오픈 웨이트 코딩 모델의 능력이 취약점 발견과 exploitation chain 쪽으로 같이 올라갈 때, <span style="background-color: #fff59d"><strong>공개 전 안전장치와 사용 정책이 훨씬 중요해집니다.</strong></span>

## slime은 장기 RL을 계속 키우기 위한 훈련 시스템입니다

GLM-5.3의 학습은 slime 위에서 돌아갑니다. slime은 Megatron을 training side에, SGLang을 rollout side에 두는 오픈소스 post-training framework입니다. 핵심 설계는 training, rollout, data buffer를 하나의 dataflow 위에 두는 것입니다. 그러면 math, code, sandbox, verifier, long-horizon agentic environment를 training loop 수정이 아니라 data generation 문제로 붙일 수 있습니다.

이번 GLM-5.3에서 slime은 두 방향으로 개선됐습니다.

한 축은 RL 연구를 위한 알고리즘 기능입니다. top-p mask, top-k와 full-vocabulary OPD, R3-style setup, training-rollout 경로의 full numerical alignment 등이 추가됐습니다. 원문에 따르면 training-rollout consistency 평가에서 평균 log probability 차이를 1e-7 수준으로 제어했고, 이전 setup 대비 99.99% 이상 줄였다고 합니다.

다른 축은 자원 효율과 throughput입니다. local storage를 추가 cache layer로 써서 host memory에 있어야 할 model state와 data를 계층적으로 저장합니다. multi-teacher OPD에서는 dynamic teacher switching과 prefetching으로 여러 teacher를 쓰되, 각 teacher마다 별도 long-running inference service를 세우지 않아도 되게 했습니다. Agentic/asynchronous workload에서는 router와 slime 사이의 scheduling과 load balancing을 개선했습니다.

결과적으로 장기 코딩 RL task에서 <span style="background-color: #fff59d"><strong>end-to-end RL training throughput이 2.3배 이상 좋아졌다고 합니다.</strong></span> 이 숫자는 작지 않습니다. 장기 과제는 rollout 하나하나가 길고, 길이가 들쭉날쭉하고, verifier도 무겁습니다. 시스템 throughput이 곧 학습 가능한 환경 수를 결정합니다.

## API 변경: <span style="background-color: #fff59d"><strong>GLM-5.3은 thinking off를 지원하지 않습니다</strong></span>

실무적으로 바로 봐야 할 변경도 있습니다. GLM-5.3은 세 가지 thinking effort만 지원합니다.

| 파라미터           | 값                   | 기본값    | 설명                                                       |
| ------------------ | -------------------- | --------- | ---------------------------------------------------------- |
| `thinking.type`    | `enabled`            | `enabled` | thinking 활성화. `disabled`는 더 이상 지원하지 않음        |
| `reasoning_effort` | `low`, `high`, `max` | `max`     | `low`는 가벼운 추론, `high`는 강화 추론, `max`는 깊은 추론 |

코딩 작업에는 `max`가 권장됩니다.

```json
{
  "model": "glm-5.3",
  "thinking": { "type": "enabled" },
  "reasoning_effort": "max"
}
```

주의할 점은 migration입니다. 기존 앱에서 `thinking.type: "disabled"`를 쓰고 있다면, 모델 ID를 `glm-5.3`으로 바꾸기 전에 `enabled`로 바꾸고 `reasoning_effort`를 `low`로 설정해야 합니다. <span style="background-color: #fff59d"><strong>그렇지 않으면 request가 실패한다고 원문은 명시합니다.</strong></span>

## 지금 확인할 체크포인트

이번 글은 “GLM-5.3이 몇 점을 찍었다”보다 더 큰 흐름을 보여줍니다.

먼저 오픈 웨이트 모델 경쟁이 다시 코딩 에이전트 쪽으로 세게 붙고 있습니다. 단일 응답 품질보다 Terminal Bench, DeepSWE, SWE-Marathon, AutomationBench처럼 장기 도구 사용과 검증이 들어간 벤치마크가 전면에 나옵니다.

다음으로 <span style="background-color: #fff59d"><strong>post-training의 병목이 데이터셋에서 환경으로 이동하고 있습니다.</strong></span> 좋은 환경은 실행 가능해야 하고, 검증 가능해야 하고, 실제 업무와 닮아야 합니다. 그리고 많아야 합니다. 모델 회사의 경쟁력은 모델 weight를 넘어 environment synthesis, verifier synthesis, reward shortcut 차단, rollout infrastructure까지 포함하게 됩니다.

사이버 능력은 코딩 능력의 부산물로만 보면 위험하고, 별도 안전 축으로 봐야 합니다. 취약점 발견이 좋아지는 것은 방어 관점에서 매우 유용합니다. 동시에 exploitation chain을 세우는 능력이 빨리 커진다는 것은 공개 모델 생태계가 안전 평가와 공개 지연, hardening을 더 진지하게 다뤄야 한다는 뜻입니다.

GLM-5.3은 아직 weight가 공개되지 않았습니다. 원문 기준으로 2주 뒤 공개 예정입니다. 그래서 지금은 “써봤더니 좋다”보다, Z.ai가 어떤 방향으로 모델을 키우고 있는지 읽는 게 먼저입니다. 제가 보기에는 모델명보다 이 변화가 더 중요합니다. <span style="background-color: #fff59d"><strong>에이전트 시대의 post-training은 답변 데이터만 먹이는 일에서, 검증 가능한 업무 세계를 계속 만들어내는 일로 옮겨가고 있습니다.</strong></span>

---

## 더 실습해보고 싶은 분들께

관련해서 참고할 자료도 붙입니다. 에이전트와 자동화 루프를 직접 만져보고 싶다면 코난쌤의 책 [『이게 되네? 오픈클로 미친 활용법 50제』](https://product.kyobobook.co.kr/detail/S000219615902), 그리고 [AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)을 같이 보셔도 좋습니다. 이번 GLM-5.3 글에서 말하는 harness, verifier, long-horizon workflow를 손으로 이해하는 데 도움이 됩니다.
