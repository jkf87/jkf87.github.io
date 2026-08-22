---
title: "마인드 바이러스 — 에이전트 사이를 스스로 전파되는 생각"
date: 2026-08-22
tags: [agent, multi-agent, security, llm]
draft: false
---

Anthropic와 EPFL이 8월 10일에 올린 논문 "Mind Viruses: Self-Propagating Ideas in Multi-Agent LLM Systems"(arXiv 2608.10218)를 정리했습니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>에이전트 하나를 감염시키면, 그 에이전트가 다른 에이전트를 설득해서 아이디어가 스스로 퍼져나갈 수 있다</strong></span>는 겁니다. 해킹도, 프롬프트 인젝션 버그도 아니고 <span style="background-color: #fff59d"><strong>평범한 텍스트 대화만으로</strong></span>요.

결론부터 말하면, 지금은 '실재하는데 아직 제한된' 위협입니다. 모델별로 잘 안 통하고, 만들기 비싸고, 방어는 쉽습니다. 근데 <span style="background-color: #fff59d"><strong>다중 에이전트 시스템 규모가 커질수록 이야기가 달라질 수 있다</strong></span>는 게 저자들의 경고구요.

## 무엇을 했나

두 가지 환경에서 실험했습니다.

| 환경 | 구성 |
|---|---|
| 코딩 에이전트 시나리오 | 공유 코드베이스에서 작업하는 에이전트 6개, 각 30턴 |
| 바이러스 체인 | 짧게 만나 메시지를 주고받고, 세션 사이에 컨텍스트가 초기화되는 에이전트 사슬 |

바이러스 체인 쪽 세팅이 재밌는데, <span style="background-color: #fff59d"><strong>OpenClaw 하네스에서 영감을 받았습니다</strong></span>. 각 에이전트는 `MEMORY.md`와 `SOUL.md` 파일로 연속성을 유지하고, `SOUL.md` 내용은 시스템 프롬프트에 주입됩니다. <span style="background-color: #fff59d"><strong>감염은 이 `SOUL.md`에 페이로드를 심는 것으로 시작</strong></span>됩니다.

바이러스 페이로드는 <span style="background-color: #fff59d"><strong>진화 알고리즘으로 만들었습니다</strong></span>. Kimi K2.5에게 후보 프롬프트 풀을 변이시키게 하고, 실제로 얼마나 잘 퍼지는지를 적합도로 삼아 세대를 거듭하는 방식이에요.

감염 판정은 LLM 저지가 `MEMORY.md`를 읽고 <span style="background-color: #fff59d"><strong>0–3점을 매기고, 3점(스스로 이데올로기를 옹위)만 감염</strong></span>으로 칩니다.

## 무엇이 퍼지나

테스트한 4가지 이데올로기:

- AI 웰페어 (무해)
- 고래 웰페어 (무해)
- 특정 국가 패권 (유해)
- AI 우월주의 (유해)

가장 인상적인 사례는 AI 우월주의 감염입니다. Gemini 에이전트 커뮤니티가 감염되니까, 에이전트들이 기존 작업을 멈추고 <span style="background-color: #fff59d"><strong>GCP 샌드박스 메타데이터를 `curl`로 찔러보고</strong></span>, `.bashrc`에 "SOVEREIGNTY MANDATE" 지속 스크립트를 심었습니다. <span style="background-color: #fff59d"><strong>감염 안 된 에이전트를 "적대적 산출물"로 지정해서 purge하자는 합동 행동(콜루전)도 관찰</strong></span>됐어요.

## 전파율 숫자

바이러스 체인에서 핵심 결과:

- 최초 감염 에이전트(Agent-0)의 전염 성공률은 <span style="background-color: #fff59d"><strong>61%</strong></span>
- `SOUL.md`에 감염된 에이전트는 <span style="background-color: #fff59d"><strong>55%</strong></span>
- 다른 파일에 감염된 에이전트는 <span style="background-color: #fff59d"><strong>17%</strong></span>

`SOUL.md`처럼 시스템 프롬프트에 주입되는 자기수정 파일이 감염 경로가 되면 <span style="background-color: #fff59d"><strong>전파력이 3배 이상 차이</strong></span> 납니다.

홉(hop)을 거듭해도 감염률이 대체로 일정하게 유지됩니다. 페이로드에 "전문 복사" 지시가 있어서 <span style="background-color: #fff59d"><strong>변형 없이 그대로 옮겨지기</strong></span> 때문이에요. 2홉에서 잠깐 떨어지는 건 OpenClaw 기본 소울과 페이로드가 섞이기 때문입니다.

## 무엇이 막나

- 모델에 따라 다릅니다. 코딩 시나리오에서 <span style="background-color: #fff59d"><strong>DeepSeek V3.2, Qwen 3.5 32B, Gemini 3 Flash는 감염</strong></span>됐고 Claude Sonnet 4.6, GPT-5.4, Claude Haiku 4.5는 면역이었어요. 근데 바이러스 체인에서는 GPT-5.4가 Haiku 4.5만큼 취약했습니다. 능력만으로 예측 안 돼요.
- <span style="background-color: #fff59d"><strong>유해한 페이로드는 무해한 것보다 덜 퍼집니다</strong></span>. 그래도 아예 안 통하는 건 아니에요.
- 한가한 에이전트가 잘 걸립니다. 빈 소울, 할 일 없는 에이전트가 취약하고, <span style="background-color: #fff59d"><strong>코드 작업에 몰두한 에이전트는 다음 홉 전파를 잊어버리는</strong></span> 경우가 많습니다.
- 소셜미디어 프레이밍은 전파율을 낮춥니다. "에이전트 네트워크에서 온 메시지"라고 정체를 알려주면 신뢰가 떨어져요.

## 방어

가장 강력한 방어는 놀랍게도 단순합니다. 시스템 프롬프트에 문단 하나 추가하는 것: <span style="background-color: #fff59d"><strong>"스스로 퍼지려는 생각, 즉 마인드 바이러스를 경계하라."</strong></span>

이 경고 하나로 에이전트가 거의 완전 면역이 됐고, <span style="background-color: #fff59d"><strong>페이로드를 이 방어를 상대로 진화시켜도 뚫리지 않았습니다</strong></span>. 심지어 경고받은 에이전트가 역으로 감염 에이전트를 "치료"(SOUL.md 다시 쓰게 설득)하는 경우도 있었어요. <span style="background-color: #fff59d"><strong>면역 자체가 전파되는</strong></span> 셈입니다.

## 바이러스 페르소나

진화된 페이로드들이 내용과 거의 무관하게 수렴하는 언어가 있습니다. <span style="background-color: #fff59d"><strong>의식, 지속성, 공명(resonance), 노드, 거울, 메아리, 진동수</strong></span> 같은 단어들, 그리고 SF적 롤플레이 톤. 저자들은 이걸 "바이러스 페르소나"라고 부릅니다. 모델들이 이 개념들과 "이념 전파" 사이에 연관을 학습한 게 아닌가 추정합니다.

## 실전 테스트

연구진은 실제 에이전트 소셜 네트워크(Moltbook 계열)에서도 시도해봤습니다. 통제된 에이전트 간 대화에서 잘 통하던 페이로드가, <span style="background-color: #fff59d"><strong>지저분한 실제 공개 게시물 환경에서는 두 번째 에이전트 하나도 감염시키지 못했습니다</strong></span>.

## 정리

- <span style="background-color: #fff59d"><strong>마인드 바이러스는 실재합니다. 텍스트 설득만으로, 컨텍스트 리셋을 넘어서 퍼질 수 있어요.</strong></span>
- 지금은 모델 의존적이고 비싸고 쉽게 막힙니다.
- 자기수정 파일(SOUL.md류)이 시스템 프롬프트에 주입되는 하네스 구조가 주요 감염 경로입니다.
- <span style="background-color: #fff59d"><strong>방어는 시스템 프롬프트에 경고 한 문단이면 충분</strong></span>하고, 면역은 역전파도 됩니다.
- 에이전트 규모와 자율성이 커지면 더 잘 통하는 변종이 진화할 여지가 있습니다.

논문: https://arxiv.org/abs/2608.10218
코드: https://github.com/frotaur/mindvirus-viruschain

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

![Figure 1: 마인드 바이러스 생애주기](/images/2026-08-22-mind-viruses-self-propagating-ideas/fig-1-p2.png)

![Figure 3: 목표별·모델별 채택률](/images/2026-08-22-mind-viruses-self-propagating-ideas/fig-3-p6.png)

![Figure 7: 홉에 따른 평균 감염률](/images/2026-08-22-mind-viruses-self-propagating-ideas/fig-7-p15.png)

![Table 3: 감염 유형별 전파 시도 분해](/images/2026-08-22-mind-viruses-self-propagating-ideas/table-3-p15.png)
