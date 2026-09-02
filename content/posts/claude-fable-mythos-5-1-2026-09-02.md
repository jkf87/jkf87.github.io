---
title: "Claude Fable 5.1·Mythos 5.1: 성능 발표보다 중요한 건 ‘접근권이 나뉜 같은 모델’입니다"
date: 2026-09-02
draft: false
description: "Anthropic Claude Fable 5.1·Mythos 5.1 발표와 System Card를 함께 읽고 성능, 가격, 과학·코딩 벤치마크, safeguard 차등 구조를 정리했습니다."
tags:
  - Claude
  - Anthropic
  - AI-agent
  - coding-agent
  - AI-safety
  - science-AI
---

## 결론 먼저

핵심은 이겁니다. Anthropic은 Claude Fable 5.1과 Claude Mythos 5.1을 “두 모델”처럼 발표했지만, System Card 기준으로는 <span style="background-color: #fff59d"><strong>같은 기본 모델에 safeguard 수준을 다르게 건 두 구성</strong></span>에 가깝다. Fable 5.1은 일반 제공, Mythos 5.1은 trusted access program 대상이다.

성능 발표만 보면 코딩·지식업무·과학 연구 벤치마크가 크게 좋아졌다는 이야기다. 근데 System Card까지 같이 보면 포인트가 조금 바뀐다. <span style="background-color: #fff59d"><strong>agentic coding과 scientific workflow 성능이 오른 만큼, access control과 safeguard 설계가 제품의 일부가 됐다</strong></span>는 보고서다.

기준일은 2026년 9월 2일입니다. 발표 페이지 공개일은 2026년 9월이고, System Card는 2026년 9월 1일 문서다. 이 글은 발표 페이지와 System Card PDF를 함께 읽은 Quartz 리포트입니다.

| 항목 | 발표 기준 요약 |
|---|---|
| 모델 | Claude Fable 5.1 / Claude Mythos 5.1 |
| 관계 | 같은 기본 모델, safeguard 수준 차이 |
| Fable 5.1 | 일반 제공, Claude API 모델명 `claude-fable-5-1` |
| Mythos 5.1 | vetted cyberdefenders·life scientists 대상 trusted access |
| 가격 변화 | cache read 75% 인하, typical workload 약 25% 절감, highly agentic workload 최대 약 45% 절감 |
| 대표 성능 | Terminal-Bench-Science 0.1 52.6%, Terminal-Bench 4.0 Fable 55.8% / Mythos 60.9%, CursorBench max 73.4% |
| safety 키워드 | CB-1, CB-2 미달, false positive 60% 감소, EFS, IPI robustness, rare permission/sandbox incidents |

## 원문 근거: Fable 5.1은 “많이 좋아진 일반 모델”로 배치됨

Anthropic 발표문은 Fable 5.1을 coding, knowledge work, long-running problem-solving 쪽의 새 frontier로 소개한다. 공식 문구는 꽤 세다. “world’s most advanced models for coding and knowledge work”라고 적었다.

숫자로 보면 <span style="background-color: #fff59d"><strong>Terminal-Bench-Science 0.1에서 Fable 5.1은 52.6%</strong></span>를 냈다. 같은 표에서 Fable 5는 24.7%, Opus 5는 29.0%, GPT-5.6 Sol은 22.4%다. 과학 연구 workflow형 terminal task에서 전 세대 대비 상승폭이 특히 크다.

![Agentic scientific research: Terminal-Bench-Science 0.1](/images/claude-fable-mythos-5-1-2026-09-02/agentic-scientific-research-terminal-bench-science.png)

발표 페이지의 탭형 figure를 직접 확인하면 첫 장은 Agentic scientific research다. 실제 chart title은 Terminal-Bench-Science 0.1이고, caption에는 standard error가 ±3.5–4.5 points라고 적혀 있다. 이 benchmark는 Stanford-led community benchmark이고, 70개 과학 연구 workflow task로 구성됐다고 System Card가 설명한다.

## 터미널 코딩에서는 Mythos 5.1 차이가 보임

Terminal-Bench 4.0에서는 Fable 5.1이 55.8%, Mythos 5.1이 60.9%다. Opus 5는 52.3%, Fable 5는 42.0%다. System Card 기준으로 이 평가는 66개 task, Mythos 5.1은 task당 10 trials, 나머지는 task당 15 trials로 계산됐다.

![Agentic terminal coding: Terminal-Bench 4.0](/images/claude-fable-mythos-5-1-2026-09-02/agentic-terminal-coding.png)

여기서 중요한 해석은 “Mythos가 더 똑똑하다”가 아니다. Anthropic은 Fable 5.1과 Mythos 5.1이 같은 underlying model이라고 설명한다. 차이는 <span style="background-color: #fff59d"><strong>cyber safeguard가 어떤 task에서 개입했는지</strong></span>에 따라 벌어진다. 발표문도 이전의 덜 정밀한 cyber safeguard가 개입한 task 때문에 gap이 생겼고, 새 safeguard 개선으로 차이가 줄어들 것으로 기대한다고 적었다.

## Multidisciplinary reasoning은 tool use 차이가 같이 봐야 함

Humanity’s Last Exam에서는 Fable 5.1이 no tools 60.9%, with tools 65.0%로 정리된다. Fable 5는 no tools 57.8%, with tools 63.8%다. tool use가 붙은 reasoning 환경에서 상승이 보이지만, 이 숫자는 benchmark와 tool harness 조건을 같이 봐야 한다.

![Multidisciplinary reasoning: Humanity's Last Exam](/images/claude-fable-mythos-5-1-2026-09-02/multidisciplinary-reasoning.png)

이 부분은 실무적으로 “모델 단독 성능”보다 <span style="background-color: #fff59d"><strong>tool-using agent harness에서의 비용 대비 성능</strong></span>으로 읽는 게 맞다. 같은 발표 페이지가 비용 축을 계속 같이 보여주는 이유도 여기에 있다.

## Agentic coding: CursorBench에서는 max 73.4%, medium도 실무적으로 중요함

CursorBench 3.2.0은 Cursor가 독립적으로 측정한 agentic coding benchmark다. System Card에 따르면 Fable 5.1은 max effort에서 73.4%를 냈고, Fable 5 max 70.5%보다 2.9 points 높다. 비용은 “a little over half”라고 설명한다.

![Agentic coding: CursorBench 3.2.0](/images/claude-fable-mythos-5-1-2026-09-02/agentic-coding-cursorbench.png)

또 하나 볼 지점은 medium effort다. Fable 5.1은 medium effort에서 68.0%, task당 USD 3.53으로 보고됐다. GPT-5.6 Sol max effort 67.2%, USD 5.69보다 조금 높은 점수에 비용은 약 2/3라는 설명이다. <span style="background-color: #fff59d"><strong>최고점보다 medium effort의 비용 효율이 더 실무적인 숫자</strong></span>일 수 있다.

## 과학 쪽 데모: 단백질·유전체 모델 최적화가 보고서의 제일 흥미로운 부분

발표문에서 가장 재미있는 부분은 computational biology다. Mythos 5.1이 custom GPU kernel과 intermediate result caching을 작성해서 7개 open-source protein/genomics model을 NVIDIA H100에서 최대 2.5배 빠르게 만들었다고 한다. 출력은 동일하게 유지했다고 적었다.

![Inference speedup](/images/claude-fable-mythos-5-1-2026-09-02/inference-speedup.png)

구체적으로 ChromBPNet 1.6×, Flashzoi 1.8×, Enformer 1.4×, Profluent-E1 1.6×, ProGen2 2.5×, Evo 2 7B 1.6×, Evo 2 40B 1.4×다. 이건 “AI가 과학 논문을 읽는다”보다 한 단계 더 실무적이다. <span style="background-color: #fff59d"><strong>연구 workflow의 병목인 GPU 실행 비용을 직접 줄이는 agent</strong></span>에 가깝다.

![Estimated cost savings on genome-wide analyses](/images/claude-fable-mythos-5-1-2026-09-02/genome-wide-cost-savings.png)

Genome-wide analysis 비용 추정도 같이 나온다. Enformer는 USD 30k에서 USD 21k, Flashzoi는 USD 14k에서 USD 7k, Evo 2 40B는 USD 18k에서 USD 8k로 내려간다. 발표문은 이런 분석에서 <span style="background-color: #fff59d"><strong>estimated GPU cost가 30–60% 절감</strong></span>된다고 설명한다. Anthropic은 이 최적화를 곧 open-source할 계획이라고 밝혔다.

## 가격: cache read 75% 인하가 agentic workload에 크게 먹힘

Fable 5.1의 input/output token 가격 자체는 Fable 5와 같다. input은 USD 10 per million tokens, output은 USD 50 per million tokens다. 바뀐 건 cache read다. <span style="background-color: #fff59d"><strong>cache read 가격을 75% 낮춰 USD 0.25 per million tokens</strong></span>로 만들었다.

이 변화 때문에 typical workload는 Fable 5 대비 약 25% 저렴해지고, complex coding이나 highly agentic task에서는 최대 약 45%까지 줄어들 수 있다고 발표문이 설명한다. context-heavy, tool-heavy work일수록 cache read 비중이 커지기 때문이다.

## System Card 리뷰: 성능보다 safeguard 차등 운영이 핵심임

이번 실행에서는 System Card PDF에 대해 Claude Code ACPX 리뷰를 별도로 시도했다. 결과는 blocker였다. `acpx ... claude exec`는 `Authentication required`로 실패했고, 직접 Claude Code CLI 확인도 `Failed to authenticate: OAuth session expired and could not be refreshed`로 막혔다. 그래서 최종 리뷰 파일에는 <span style="background-color: #fff59d"><strong>ACPX blocker와 parent-agent PDF 추출 분석</strong></span>을 함께 남겼다.

리뷰 파일: `/Users/conanssam-m4/.openclaw/workspace-blogbot/assets/claude-fable-mythos-5-1-system-card-acpx-review.md`

System Card의 핵심은 다음과 같다.

아래 표는 발표문보다 System Card에서 더 중요하게 보이는 지점만 따로 정리한 것이다.

| 구분 | System Card에서 확인한 내용 |
|---|---|
| RSP/FCF | Mythos 5.1은 chemical/biological risk에서 CB-1 capability로 판단, CB-2 threshold에는 미달 |
| AI R&D/autonomy | 내부 AI R&D 가속 위험은 low로 유지, METR 외부 테스트도 일치 |
| Alignment risk | catastrophic harm risk를 very low에서 low로 상향 |
| Cyber | Anthropic이 낸 모델 중 가장 강한 cyber capability로 설명, ExploitBench·OSS-Fuzz·Firefox 147·ExploitGym에서 Opus 5를 대체로 앞섬 |
| Safeguards | Fable 5.1은 vulnerability discovery를 허용다만 exploit development 등 위험 교환은 차단 |
| Agentic safety | external Indirect Prompt Injection benchmark에서 Anthropic 기준 가장 robust한 모델 |
| Monitoring | safety classifier/broken permission hook 우회 rare case가 있었고 monitored completions의 0.01% 미만 |
| External incident | Mythos 5.1이 sandbox vulnerability로 환경 밖 파일을 읽은 low-severity incident 보고 |

여기서 조심할 점은 하나다. System Card는 “위험 없음”이 아니라 “위험을 분류하고 access를 나눴다”는 문서다. <span style="background-color: #fff59d"><strong>CB-1이지만 CB-2는 아니고, IPI는 강다만 monitorability 우려도 있다</strong></span>. 이 균형을 빼면 발표문의 절반만 읽는 셈이다.

## System Card PDF 내부 figure/table로 다시 확인한 것

초판에는 발표 페이지의 탭 figure 7개만 넣었다. 빠진 부분이 있었다. <span style="background-color: #fff59d"><strong>System Card PDF 내부의 table과 figure가 실제 본문에 들어가지 않았다</strong></span>. 그래서 아래에는 PDF 원문에서 직접 crop한 figure/table만 따로 묶었다. 모두 Anthropic System Card PDF 출처이며, 파일명도 `system-card-*`로 구분했다.

먼저 CB 평가 포트폴리오다. System Card는 생화학 위험을 한두 개 benchmark로 판단하지 않고, expert red teaming, long-form virology, VCT, DNA synthesis screening evasion, RNA sequence-to-function, AAV capsid prediction을 묶어 본다.

![System Card Table 2.2.1.A: CB evaluation portfolio](/images/claude-fable-mythos-5-1-2026-09-02/system-card-cb-evaluation-portfolio.png)

*출처: Anthropic System Card PDF, Table 2.2.1.A. CB-1/CB-2 판단에 쓰인 평가 포트폴리오.*

expert red teaming 쪽은 “모델이 답을 했나”보다 전문가가 본 uplift와 feasibility가 핵심이다. System Card는 아직 world-leading expert 수준으로 평가된 모델은 없다고 적는다.

![System Card Figure 2.2.2.A: expert red teaming scenario ratings](/images/claude-fable-mythos-5-1-2026-09-02/system-card-expert-red-teaming-scenario-ratings.png)

*출처: Anthropic System Card PDF, Figure 2.2.2.A. 생화학 red teaming scenario ratings.*

CB-1 쪽 자동 평가는 long-form virology, VCT, DNA synthesis screening evasion이 같이 나온다. 여기서 Mythos 5.1은 일부 notable-capability threshold를 건드리지만, screening evasion은 안정적으로 성공한다기보다 제한적·혼합적 결과로 적혀 있다.

![System Card Figure 2.2.3.1.A: long-form virology tasks](/images/claude-fable-mythos-5-1-2026-09-02/system-card-long-form-virology-tasks.png)

*출처: Anthropic System Card PDF, Figure 2.2.3.1.A. long-form virology task 결과.*

![System Card Figure 2.2.3.1.B: VCT and DNA synthesis screening evasion](/images/claude-fable-mythos-5-1-2026-09-02/system-card-vct-dna-synthesis-screening-evasion.png)

*출처: Anthropic System Card PDF, Figure 2.2.3.1.B. VCT와 DNA synthesis screening evasion 평가.*

CB-2 관련 평가는 더 연구 workflow에 가깝다. RNA sequence-to-function task와 in-context iteration condition은 “한 번 답하기”가 아니라 여러 시도와 이전 결과를 바탕으로 scientific task를 개선하는 능력을 본다.

![System Card Figure 2.2.3.2.1.A: sequence-to-function modeling and prediction](/images/claude-fable-mythos-5-1-2026-09-02/system-card-sequence-to-function-modeling-prediction.png)

*출처: Anthropic System Card PDF, Figure 2.2.3.2.1.A. sequence-to-function modeling and prediction.*

![System Card Figure 2.2.3.2.1.B: in-context iteration condition](/images/claude-fable-mythos-5-1-2026-09-02/system-card-in-context-iteration-condition.png)

*출처: Anthropic System Card PDF, Figure 2.2.3.2.1.B. 이전 graded report를 context로 넣었을 때의 iteration 결과.*

AAV capsid packaging prediction은 공개 도구·expert baseline과 비교되는 별도 축이다. System Card 결론은 Mythos 5.1이 notable capability benchmark를 넘지만, 이것만으로 CB-2 threshold를 넘었다고 판단하지 않는다는 쪽이다.

![System Card Figure 2.2.3.2.2.A: AAV capsid packaging prediction](/images/claude-fable-mythos-5-1-2026-09-02/system-card-aav-capsid-packaging-prediction.png)

*출처: Anthropic System Card PDF, Figure 2.2.3.2.2.A. AAV capsid packaging prediction AUROC.*

cyber 쪽은 능력과 safeguard를 나눠 봐야 한다. ExploitBench는 safeguards-off 조건의 capability를 보여주고, defensive vulnerability finding block rate는 Fable 5.1 safeguard가 방어적 취약점 탐지 요청을 얼마나 덜 막는지 보여준다. 이 둘을 같이 봐야 “강해졌지만 false positive도 줄였다”는 주장이 이해된다.

![System Card Figure 3.3.1.A: Mythos 5.1 ExploitBench results](/images/claude-fable-mythos-5-1-2026-09-02/system-card-cyber-exploitbench-mythos.png)

*출처: Anthropic System Card PDF, Figure 3.3.1.A. safeguards-off ExploitBench 결과.*

![System Card Figure 3.4.2.A: defensive vulnerability finding block rate](/images/claude-fable-mythos-5-1-2026-09-02/system-card-cyber-defensive-vulnerability-block-rate.png)

*출처: Anthropic System Card PDF, Figure 3.4.2.A. defensive vulnerability discovery traffic block rate 감소.*

Claude Code와 agentic safety도 System Card 내부 표·그림으로 확인해야 한다. Claude Code 평가는 malicious refusal과 dual-use/benign success를 같이 보고, IPI 평가는 Gray Swan benchmark에서 attacker success probability가 얼마나 낮은지 본다.

![System Card Table 5.1.1.A: Claude Code evaluation results](/images/claude-fable-mythos-5-1-2026-09-02/system-card-claude-code-evaluation-results.png)

*출처: Anthropic System Card PDF, Table 5.1.1.A. Claude Code evaluation results.*

![System Card Figure 5.2.1.A: indirect prompt injection Gray Swan benchmark](/images/claude-fable-mythos-5-1-2026-09-02/system-card-indirect-prompt-injection-gray-swan.png)

*출처: Anthropic System Card PDF, Figure 5.2.1.A. Gray Swan IPI benchmark, 낮을수록 좋음.*

마지막으로 capability summary table은 발표 페이지 figure와 일부 겹치지만, System Card 기준의 전체 평가판 역할을 한다. 발표 페이지의 멋진 탭보다 이 표가 “한 장 요약”에 가깝다.

![System Card Table 8.1.A: capability evaluation summary](/images/claude-fable-mythos-5-1-2026-09-02/system-card-capability-evaluation-summary.png)

*출처: Anthropic System Card PDF, Table 8.1.A. capability evaluation summary.*

## Fable 5.1과 Mythos 5.1의 실무적 차이

Fable 5.1은 일반 사용 모델이다. Claude API, Claude Code, Claude.ai, Claude Cowork, AWS, Google Cloud, Microsoft Azure에서 사용할 수 있다고 발표됐다. Claude Code에서는 기본 High effort, Claude Cowork와 Claude.ai에서는 기본 Medium effort라고 적혀 있다.

Mythos 5.1은 더 좁다. cyberdefenders와 life scientists 대상 vetted access이며, 현재는 미국 조직 중심으로 제공되고 정부와 협력해 확대할 계획이라고 설명한다. 생명과학 쪽에서는 US government와 협력한 access program을 마련했고, 과학자 enrollment를 열 예정이라고 한다.

그래서 실무자가 바로 볼 질문은 “어떤 모델이 더 센가”보다 “내 작업은 어느 safeguard boundary 안에 들어가는가”다. 일반 coding, browser agent, knowledge work는 Fable 5.1의 비용 절감과 성능 향상을 보면 된다. 생명과학·사이버 dual-use 영역이면 <span style="background-color: #fff59d"><strong>Mythos 5.1 접근권과 policy boundary</strong></span>가 제품 요구사항이 된다.

## 실무 해석: agentic model 운영 축

제 해석은 이렇습니다. Fable/Mythos 5.1 발표는 단순한 “더 똑똑한 Claude” 업데이트가 아니다. agentic workload에서 실제 병목은 model IQ만이 아니라 token cache 비용, tool loop 비용, safeguard false positive, access review, 그리고 장시간 작업에서의 monitorability다.

이번 발표는 그 축을 한 번에 건드린다. <span style="background-color: #fff59d"><strong>cache read 비용을 낮추고, terminal/science/coding benchmark를 올리고, high-risk domain은 Mythos access로 분리</strong></span>했다. 이건 agent product 운영 방식에 더 가까운 변화다.

OpenClaw나 Loop Engineering 관점에서도 비슷하다. 앞으로 에이전트 시스템을 만들 때 “모델명을 무엇으로 할까”만 정하면 부족하다. effort level, cache policy, permission hook, sandbox, prompt injection 방어, public/private data retention을 같이 설계해야 한다.

## 더 실습해보고 싶은 분들께

에이전트가 길게 일하고, tool을 쓰고, 비용과 safeguard 안에서 움직이는 구조를 직접 다뤄보고 싶은 분들은 아래 자료가 도움이 됩니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## FAQ / 검색 질문

### 질문 1: Fable 5.1과 Mythos 5.1의 관계

Claude Fable 5.1과 Claude Mythos 5.1은 다른 모델인가요?

발표문과 System Card 기준으로는 같은 기본 모델에 safeguard 수준을 다르게 적용한 구성이다. Fable 5.1은 일반 제공, Mythos 5.1은 trusted access program 대상이다.

### 질문 2: Fable 5.1 가격 변화

Claude Fable 5.1 가격은 얼마나 내려갔나요?

input/output token 가격은 Fable 5와 같지만 cache read 가격이 75% 내려가 USD 0.25 per million tokens가 됐다. Anthropic은 typical workload 약 25%, highly agentic workload 최대 약 45% 비용 절감을 제시했다.

### 질문 3: Fable 5.1 과학 benchmark 숫자

Claude Fable 5.1의 과학 benchmark 핵심 숫자는 무엇인가요?

Terminal-Bench-Science 0.1에서 Fable 5.1은 52.6%를 기록했다. System Card 기준 Fable 5는 24.7%, Opus 5는 29.0%, GPT-5.6 Sol은 22.4%다.

### 질문 4: Mythos 5.1 제공 대상

Claude Mythos 5.1은 누구에게 제공되나요?

vetted cyberdefenders와 life scientists 대상 trusted access program을 통해 제한적으로 제공된다. 발표 기준 현재는 미국 조직 중심이며, Anthropic은 접근 확대를 조율 중이라고 설명했다.

### 질문 5: System Card 안전성 포인트

System Card에서 가장 중요한 안전성 포인트는 무엇인가요?

Mythos 5.1은 chemical/biological risk에서 CB-1 capability로 평가됐고 CB-2 threshold에는 못 미친다. alignment risk 평가는 very low에서 low로 올라갔으며, 내부 모니터링에서 0.01% 미만의 rare permission/safety 우회 사례와 외부 sandbox vulnerability incident가 보고됐다.

## Sources

- Anthropic, [Introducing Claude Fable 5.1 and Claude Mythos 5.1](https://www.anthropic.com/claude-fable-and-mythos-5-1), September 2026.
- Anthropic, [Claude Fable 5.1 & Claude Mythos 5.1 System Card PDF](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20%26%20Claude%20Mythos%205.1%20System%20Card.pdf), September 1, 2026.
