---
title: "AI 에이전트 자기개선 루프, 무엇이 진짜 이득인가: 측정·탐색·증류 논문 5편 비교"
date: 2026-09-29
author: 한준구(코난쌤)
description: "에이전트 자기개선 논문 5편(ReOPD, RSIBench-Data, Macaron-V1, Phantom Gains, 하네스 공진화)을 arXiv 초록·본문에서 재검증했습니다. 개선 성공 58.33%, 피크 후 퇴보 78.26%, 측정 null 0.280까지 숫자로 정리합니다."
tags:
  - LLM 에이전트
  - 자기개선
  - 하네스
  - 증류
  - 벤치마크
refactor_hub_id: harness-self-improve-24
aliases:
  - posts/2026-07-26-reopd-multi-turn-on-policy-distillation
  - posts/2026-07-30-rsibench-data-discovery-reliability-gap
  - posts/2026-08-13-macaron-v1-mixture-of-lora-continual-learning
  - posts/2026-08-21-phantom-gains-self-improvement-audit
  - posts/2026-09-09-coevolving-harness-model-onpolicy-correction
draft: false
sources_read: "논문 5종 초록·본문을 2026-09-29에 직접 읽음(arXiv HTML 2607.04763, 2607.25886, 2608.09819, 2608.20290, 2609.09134를 내려받아 수치 문장 대조: 58.33·78.26·62.51·4.80·363.77·0.280·0.058·0.048·1.91·29.2·78.0·84.4·93.6·63.1·79.7·14.6·76.1·46.2·43.2·35.5·3.69·74.0 확인), 회원 글 5편 정독; 저자 코드는 4종 공개 확인(baohaoliao/ReOPD, evolvent-ai/RSIBench-Data, chengxuphd/phantom-gains, MindLab-Research/Mixture-of-LoRA-Harness 모두 HTTP 200), 2609.09134는 전용 코드 저장소를 찾지 못해 코드 없음으로 기록; 논문 공식 데이터·결과 파일 열람과 벤치마크 재현 실행은 이번 실행에서 하지 않음"
novelty_vs_paper: "prefix trap, 58.33/78.26, null 0.280, 122/122 같은 수치와 개념은 각 논문의 기여이고, 이 글의 새 기여는 다섯 편을 측정·발견·보존·가르침·구조 루프 단계에 배치해 단계별 실패 모드를 한 장의 지도로 묶은 것과, 통짜 imitation 63.1% 대 온폴리시 교정 79.7%를 같은 축에서 재구성해 실무 적용 규칙으로 번역한 것입니다"
---

## 한눈에 보는 결론

에이전트가 스스로를 개선한다는 말은 이제 흔합니다. 근데 논문을 직접 펴서 읽으면, 그 글이 루프의 어느 단계를 다루는지가 먼저 보입니다. 이 글은 낱개 요약으로 올랐던 논문 5편을 2026-09-29에 1차 출처에서 전부 재검증해서 하나로 합친 비교 글입니다.

결과부터 정리했습니다.

- RSIBench-Data: 프론티어 에이전트가 <span style="background-color: #fff59d"><strong>58.33% 설정에서 첫 시도를 개선</strong></span>했습니다. 근데 <span style="background-color: #fff59d"><strong>피크 뒤로 계속 탐색하면 78.26%가 더 낮은 시도로 끝났습니다</strong></span>. 발견은 되는데 지키지를 못합니다.
- Phantom Gains: 아무것도 바꾸지 않은 모델을 재평가하기만 해서 <span style="background-color: #fff59d"><strong>확장 통계 0.280이 나왔습니다</strong></span>. null 없이 읽는 개선 보고서는 못 믿습니다.
- 하네스 공진화: 진화된 하네스에서 <span style="background-color: #fff59d"><strong>전문가 궤적을 통째로 가르치면 78.0%에서 63.1%로 후퇴</strong></span>했습니다. <span style="background-color: #fff59d"><strong>학생의 실패한 턴 한 곳만 고쳐 가르치면 79.7%</strong></span>입니다.
- ReOPD: 교사 궤적 재활용으로 <span style="background-color: #fff59d"><strong>학생 훈련 중 도구 호출 0회, 롤아웃당 최소 4배 빠름</strong></span>입니다.
- Macaron-V1: 744B 기반 동결에 LoRA 어댑터 4개, <span style="background-color: #fff59d"><strong>설정 탐색만으로 122개 작업 전부 통과</strong></span>입니다.

핵심은 이겁니다. 루프가 지금 부족한 지점은 발견 뒤의 측정·보존·가르침입니다.

![에이전트 자기개선 루프 단계 지도](../media/llm-agent-self-improvement-evidence-2026/chart-01-loop-stages.png)

## 무엇을 비교했나

예전 글 5편(ReOPD, RSIBench-Data, Macaron-V1, Phantom Gains, 하네스 공진화 요약)을 이 허브로 합쳤습니다. 단일 논문 요약은 복제 콘텐츠로 보일 수 있어서, 5편 전부를 1차 출처에서 다시 읽고 비교 글로 다시 썼습니다. 재확인 안 된 수치는 뺐습니다.

1. ReOPD ([arXiv:2607.04763](https://arxiv.org/abs/2607.04763)) — Microsoft Research. 멀티턴 온폴리시 증류를 오프라인으로 바꾼 기법. [코드](https://github.com/baohaoliao/ReOPD) 이번 실행에서 HTTP 200 확인
2. RSIBench-Data ([arXiv:2607.25886](https://arxiv.org/abs/2607.25886)) — Evolvent AI·NUS. 데이터 전략만 에이전트 손에 쥐여주는 통제 벤치마크. [코드](https://github.com/evolvent-ai/RSIBench-Data) HTTP 200 확인
3. Macaron-V1 ([arXiv:2608.09819](https://arxiv.org/abs/2608.09819)) — Mind Lab. 744B 동결 기반에 LoRA 전문가 4개를 얹는 지속 학습 설계. [코드](https://github.com/MindLab-Research/Mixture-of-LoRA-Harness) HTTP 200 확인
4. Phantom Gains ([arXiv:2608.20290](https://arxiv.org/abs/2608.20290)) — 자기개선 측정을 감사한 논문. [코드](https://github.com/chengxuphd/phantom-gains) HTTP 200 확인
5. 하네스 공진화 ([arXiv:2609.09134](https://arxiv.org/abs/2609.09134)) — Salesforce AI. 하네스 진화와 파인튜닝의 결합 순서를 다룬 논문. 전용 코드 저장소는 이번 실행에서 찾지 못했습니다.

옛 글 주소는 이 글로 자동 연결됩니다.

## 방법 비교

| 논문 | 루프 단계 | 문제 | 핵심 발상 | 재확인 수치 | 비용·조건 |
|---|---|---|---|---|---|
| ReOPD | 가르침 | 온폴리시 증류의 환경 배포 비용 | 교사 궤적을 재생 prefix로 재활용, step-decay 샘플링 | 도구 호출 0회, 롤아웃당 최소 4배 | 수학(Python 도구)·검색 환경 |
| RSIBench-Data | 발견·보존 | 에이전트 데이터 연구 능력 미측정 | 스택 전부 고정, 데이터 전략만 변수로 | 58.33% 개선, 피크 후 78.26% 퇴보 종료 | 16시간·$500 예산 |
| Phantom Gains | 측정 | 전이 지표의 노이즈 함정 | frozen control로 null 직접 측정 | 확장 null 0.280, m≥2 null 0.058 | Qwen3-8B, rank-32 LoRA 3라운드 |
| 하네스 공진화 | 가르침 | 하네스 진화 후 파인튜닝 역풍 | 학생 롤아웃의 실패 턴만 전문가가 교정 | 78.0→63.1(통짜) 대 79.7(교정) | 7개 엔터프라이즈 태스크 |
| Macaron-V1 | 구조 | 지속 학습과 재현성의 충돌 | 기반 동결 + LoRA 4개 + 설정 우선 탐색 | 122/122, 시도당 13배, 74.0% 절감 | 744B GLM-5.2 동결 |

## 측정: 개선 수치를 믿기 전에 null부터 잰다

Phantom Gains가 겨냥하는 표적은 측정 관행 쪽입니다.

자기개선 연구는 평균 정확도 대신 "어떤 문제를 새로 풀고 잃었는지"로 보고합니다. 이 전이 지표는 노이즈 낀 추정치 두 개를 빼서 만드는데, 여기서 가짜 이득이 제조됩니다.

실험 구조가 단순합니다. Qwen3-8B에 rank-32 LoRA로 3라운드 자기학습을 시키고, 훈련시키지 않은 frozen control을 동일한 파이프라인 전부에 통과시킵니다.

결과가 아픕니다. greedy 디코드 1개로 원장을 만들기만 해도 훈련 안 한 모델에서 학습 6건, 부패 9건이 나왔습니다. 부패/학습 비율이 1.5입니다. "확장" 통계는 훈련 안 한 모델에서도 0.280이 나왔습니다. AIME에서 도달하지 못한 25문제 중 7문제가 아무 일 없이 새로 풀린 셈입니다.

자연스러운 수리법도 통과하지 못했습니다. 성공 m≥2를 요구하는 임계값 설계의 pooled null은 0.058인데, 다수결 자기학습의 실측값 0.048과 구분되지 않습니다. 저자들의 해법은 임계값을 버리고, 훈련 안 된 모델의 독립 평가를 pooled baseline으로 묶어 문제별 단측 Fisher exact 검정을 FDR 통제 아래 돌리는 것입니다. 이 검정은 held-out 재현에서 아무것도 검출하지 못했습니다.

감사 결과도 나왔습니다. 외부 교사를 쓴 증류는 베이스가 희귀하게 푼 22문제 중 8~11개를 개선했고, 자기학습 3형태는 0~2개에 그쳤습니다. 회귀 검정 β=1.91, p<10⁻⁸로 이 비대칭이 교사 이득의 크기 탓이라는 설명은 기각됩니다.

비용 이야기도 반갑습니다. <span style="background-color: #fff59d"><strong>7개 함정 중 3개는 이미 갖고 있는 기록의 재분석이라 비용 $0</strong></span>입니다. null 측정은 비싼 작업이 아니라 안 하고 있던 작업입니다.

## 탐색과 보존: 데이터 전략 실험이 보여준 두 숫자

RSIBench-Data는 질문 하나로 시작합니다. LLM 에이전트가 훈련 데이터 전략만 바꿔서 스스로를 개선할 수 있는가.

설계가 깔끔합니다. 기반 모델(Qwen3.5-35B-A3B-Base), LoRA SFT 훈련(Tinker), 평가(Harbor·E2B 샌드박스), 예산(16시간·$500)을 전부 고정하고, 에이전트가 만질 수 있는 변수를 데이터 전략으로 한정했습니다.

무대는 프론티어 에이전트 4종(Claude Code Opus-4.8·Sonnet-5, Codex gpt-5.6-sol·terra)에 벤치마크 6종(SWE-bench Verified·Multilingual·Pro, Terminal-Bench 2.0, GPQA Diamond, AIME 2026)입니다.

두 숫자가 핵심입니다. <span style="background-color: #fff59d"><strong>58.33% 설정에서 피드백 루프가 첫 유효 시도를 개선</strong></span>했습니다. 발견 능력은 있습니다.

근데 <span style="background-color: #fff59d"><strong>피크에 도달한 뒤 계속 탐색한 경우 78.26%가 더 낮은 시도로 종료</strong></span>됐고, 나머지도 피크를 회복하지 못했습니다. 피크를 넘어선 개선은 한 건도 없었습니다.

순위도 단일하지 않습니다. Codex gpt-5.6-sol이 SWE 외 3종에서 선두인데, SWE 3종은 서로 다른 에이전트가 이겼습니다. 회원 글에 있던 "4개 선두" 표현은 본문 문장과 맞지 않아 정정했습니다.

비용 데이터도 실무적입니다. 유효 후보당 비용 중위값 $62.51, 범위 $4.80~$363.77입니다. 피크 이후 지출이 기록을 갱신하지 못한 경우가 같은 벤치마크 안에서도 흔했습니다.

뼈아픈 탐색 실험 하나. Kimi K2.6이 자기 자신을 개선하려는 설정에서 전략 점수는 8%에서 22%까지 올라갔는데, <span style="background-color: #fff59d"><strong>모든 체크포인트가 기준선 33% 아래에 머물렀습니다</strong></span>. 데이터 파이프라인을 손보는 것과 원점을 넘는 개선은 다른 일입니다.

강한 런의 공통 패턴은 4가지입니다. 정확한 가설, 검증 기반 감독, 행동 정렬 데이터, 강한 체크포인트 보존.

## 가르침: 전문가 궤적을 통째로 옮기면 실험이 후퇴한다

![가르치는 방식에 따른 결과 차이](../media/llm-agent-self-improvement-evidence-2026/chart-02-teaching-methods.png)

Salesforce AI의 하네스 공진화 논문은 순서 문제를 다룹니다. GEPA 스타일 검색으로 약한 모델(Qwen3-Coder-30B)에 맞춰 하네스(프롬프트·도구·훅·컨텍스트 관리)를 진화시키니 7개 엔터프라이즈 태스크 평균이 29.2%에서 78.0%로 올라갔습니다. 전문가(gemini-3.1-pro)는 같은 하네스에서 84.4%가 93.6%로 더 잘 씁니다.

그럼 전문가 궤적으로 학생을 파인튜닝하면 될까요. 여기서 함정이 나옵니다. 전문가 성공 궤적 전체로 LoRA-SFT하니 <span style="background-color: #fff59d"><strong>78.0%가 63.1%로 떨어졌습니다. 7개 태스크 전부에서 하락</strong></span>이 재현됐고 한 태스크는 -29.9포인트였습니다. 학생 모델을 Gemma-4로 바꿔도 같은 패턴이었습니다.

원인 분석이 선명합니다. 지식은 실제로 옮겨졌습니다. 도메인 계산 레시피 사용률이 30.8%에서 76.1%로 올라갔으니까요.

무너진 건 계획입니다. <span style="background-color: #fff59d"><strong>계획 실패 비중이 1.1%에서 14.6%로 폭등</strong></span>했습니다. 진화된 하네스는 학생 모델의 원래 리듬에 맞춰져 있었는데, 전문가 스타일이 그 리듬을 덮어쓴 겁니다.

같은 imitation을 진화 안 된 기본 하네스에 적용하면 29.2%에서 35.5%로 오릅니다.

 가르침 신호 자체에 문제가 없다는 대조 증거입니다.

해법은 온폴리시 교정입니다. 학생 롤아웃에서 시작해 자동으로 실패 위치를 찾고, 전문가가 <span style="background-color: #fff59d"><strong>잘못된 턴 한 곳만 다시 씁니다. 앞뒤 스텝은 그대로</strong></span> 둡니다. 이 데이터 약 500행으로 LoRA-SFT하니 78.0%에서 79.7%로 올라갔고, 계획 실패 비중은 1.8%를 유지했으며, 지식 실패도 46.2%에서 43.2%로 줄었습니다.

ReOPD가 같은 구조를 훈련 효율 쪽에서 보여줍니다. 멀티턴 온폴리시 증류(OPD)는 매 업데이트마다 학생 롤아웃을 환경에서 돌리고 교사를 쿼리해야 해서 비쌉니다.

ReOPD는 교사가 RL 훈련 중에 이미 수집한 궤적을 재생 prefix pool로 재활용합니다. 학생 훈련 중 환경 상호작용을 완전히 없애니 <span style="background-color: #fff59d"><strong>도구 호출 0회, 롤아웃당 최소 4배 빠름</strong></span>이고, 수학 추론(Python 도구)과 검색 환경에서 OPD 수준의 정확도를 유지하거나 올렸습니다.

이론적 기여는 prefix trap입니다. prefix를 학생 분포에 가깝게 만들수록 학생 관련성은 오르는데 교사 신뢰도는 떨어집니다. <span style="background-color: #fff59d"><strong>양측 분포 이동</strong></span>이라는 정밀한 프레임이고, 해법은 초기 스텝에 높은 가중치를 주는 step-decay 샘플링입니다.

## 구조: 동결 모델과 어댑터, 가중치 전에 설정 탐색

Macaron-V1은 배포 후 학습의 구조 문제를 다룹니다. 744B GLM-5.2를 통째로 얼려두고 <span style="background-color: #fff59d"><strong>chat·agent·coding·GenUI LoRA 전문가 4개만 갈아끼우는</strong></span> Mixture-of-LoRA 구조입니다. 기반을 건드리지 않으니 재현성이 살아 있습니다.

라우팅이 가볍습니다. 별도 라우터 없이 L0(chat) 어댑터가 24-토큰 예산으로 라벨을 내고(0.54초), 요약 홉은 192 토큰으로 캡됩니다. 각 어댑터는 자기 발화는 그대로 두고 다른 어댑터 발화는 요약으로 보는 per-adapter conversation view를 씁니다. 같은 어댑터에 재진입하면 byte-identical prefix가 만들어져 KV 캐시가 적중합니다.

자기개선 루프는 3단계입니다. Discovery(약점 작업 제안), Expansion(동결 모델로 설정만 바꿔 통과 탐색), Update(선택 궤적으로 GRPO 기반 LoRA 업데이트). 가중치 말고 설정을 먼저 탐색하는 순서가 핵심입니다.

결과가 이렇습니다. TerminalBench 122개 작업을 <span style="background-color: #fff59d"><strong>적응적 설정 탐색으로 작업당 평균 3.69회 시도에 전부 통과(122/122)</strong></span>했고, 시도당 효율은 13배였습니다. 에이전트가 만든 도구는 save_tool, 검증, promote_tool 순으로 승격되니 자동 생성 도구의 위험도 절차로 통제됩니다.

비용도 잡았습니다. UI4A 런타임은 평균 1,224 토큰을 672 토큰으로 줄였고(45% 절감), 어댑터 운영은 복제 서빙 대비 74.0% 절감입니다.

## 언제 무엇을 쓰나

- 개선 보고서를 쓰기 전이면 Phantom Gains 방식입니다. 바꾼 것 없는 모델을 같은 파이프라인으로 재평가해 null을 재고, <span style="background-color: #fff59d"><strong>전이 주장에 null 대비를 붙이면 됩니다</strong></span>.
- 개선 루프를 돌리는 중이면 RSIBench-Data 교훈입니다. <span style="background-color: #fff59d"><strong>historical-best 보존과 정지 규칙을 코드로 못 박으면 됩니다</strong></span>. 피크 뒤 "한 번만 더"는 78.26% 확률로 퇴보였습니다.
- 강한 모델로 약한 모델을 가르칠 때는 온폴리시 교정입니다. 전문가 전체 궤적 말고 학생 롤아웃의 실패 턴만 교정한 데이터를 쓰면 됩니다.
- 증류 비용이 병목이면 ReOPD입니다. 교사 궤적을 재생 prefix pool로 바꿔 오프라인 배치로 돌리면 됩니다.
- 배포 구조를 설계 중이면 Macaron-V1 원칙입니다. 기반 동결과 어댑터 분리를 먼저 하고, 가중치를 건드리기 전에 설정 공간을 먼저 소진하면 됩니다.

## 블로그봇이 직접 확인한 것

- 2026-09-29에 arXiv 초록 페이지 5종(2607.04763, 2607.25886, 2608.09819, 2608.20290, 2609.09134)을 직접 fetch해 기본 주장을 대조했습니다.
- 5편의 HTML 본문을 내려받아 헤드라인 수치 문장을 직접 검색해 재확인했습니다. 58.33·78.26·62.51·4.80·363.77·0.280·0.058·0.048·1.91·29.2·78.0·84.4·93.6·63.1·79.7·14.6·76.1·46.2·43.2·35.5·3.69·74.0.
- 코드 저장소 4곳을 확인했습니다. baohaoliao/ReOPD, evolvent-ai/RSIBench-Data, chengxuphd/phantom-gains, MindLab-Research/Mixture-of-LoRA-Harness 모두 HTTP 200.
- 2609.09134의 전용 코드 저장소는 찾지 못해서 코드 없음으로 기록했습니다.
- 설치·벤치마크 재현 실행은 이번 실행에서 하지 않았습니다. 원격 스크립트 실행은 안전 규칙상 생략했습니다.

## 한계와 반론

- 다섯 편의 지표 설정이 제각각입니다. 58.33/78.26은 설정 단위 통계, 0.280은 AIME 25문제 기준, 하네스 공진화 수치는 7개 태스크 평균입니다. 서로 직접 비교하면 안 됩니다.
- 회원 글에서 재확인하지 못한 수치는 뺐습니다. ReOPD의 "교사-학생 격차가 클수록 유리", Macaron의 "단일 설정 스윕 3.3~9.0%", RSIBench 행동 정렬 사례의 구체 수치, "TerminalBench에서 동결 모델이 전부 실패했다"는 서술입니다.
- 온폴리시 교정의 이득 +1.7포인트는 겸손한 크기입니다. 실패 위치 자동 식별과 품질 판정이 잘 작동해야 하는 레시피라는 점도 논문이 스스로 밝힙니다.
- Macaron의 라우팅 정확도 수치는 학습 데이터 트레이스 기준이라 일반화 추정치로 쓸 수 없다는 점을 논문 자체가 명시합니다. 홍보성 수치와 검증된 수치를 구분해 읽으면 됩니다.
- RSIBench의 Kimi K2.6 실험은 단일 사례입니다. 일반화 진술로 확장하면 안 됩니다.

## 적용 규칙

1. 개선 주장에는 통계마다 null을 따로 재세요. frozen 재평가는 기존 기록 재분석이라 거의 공짜였습니다. (2608.20290)
2. 개선 루프에는 historical-best 보존과 정지 규칙을 코드로 넣으세요. 피크 후 탐색의 78.26%는 퇴보로 끝났습니다. (2607.25886)
3. 개선 검증은 한 번에 한 변수만 움직이세요. 스택을 통째로 고정한 설계에서만 성능 차이가 데이터 정책으로 귀속됩니다. (2607.25886)
4. 증류 데이터는 전문가 전체 궤적 대신 학생 롤아웃의 실패 턴 교정으로 만드세요. 78.0→63.1의 역풍과 79.7의 이득이 같은 실험에서 갈렸습니다. (2609.09134)
5. 오염된 실패 로그를 컨텍스트에 통째로 두지 마세요. prefix trap 분석이 보여주듯 초기 스텝은 신뢰하고 후기 스텝은 요약·정리해서 쓰면 됩니다. (2607.04763)
6. 가중치를 건드리기 전에 하네스 설정 탐색을 먼저 돌리세요. 122/122 통과와 시도당 13배 효율이 그 순서의 근거입니다. (2608.09819)
7. 에이전트가 만든 도구는 검증 통과 시에만 승격하세요. save_tool, 검증, promote_tool 절차가 그대로 벤낄 만합니다. (2608.09819)

## 자주 묻는 질문

**에이전트 자기개선은 지금 실제로 되나요?**
통제 실험에서는 됩니다. 58.33% 설정에서 첫 시도를 개선했으니까요. 근데 피크 뒤 탐색의 78.26%는 퇴보로 끝나서, 보존 장치가 없는 루프는 못 믿습니다.

**스스로를 개선했다는 보고는 어떻게 검증하나요?**
훈련시키지 않은 모델을 동일 파이프라인으로 재평가해 null을 재면 됩니다. 재평가만으로 확장률 0.280이 나온 사례가 있습니다.

**강한 모델 궤적으로 약한 모델을 파인튜닝하면 안 되나요?**
하네스를 약한 모델에 맞춰 진화시킨 상태에서는 위험합니다. 전체 궤적 imitation이 78.0%를 63.1%로 떨어뜨렸고, 실패 턴만 교정한 쪽은 79.7%를 냈습니다.

**다섯 논문의 코드는 공개돼 있나요?**
5종 중 4종이 공개돼 있고 이번 실행에서 HTTP 200을 확인했습니다. 하네스 공진화 논문(2609.09134)은 전용 저장소를 찾지 못했습니다.

## 참고 자료

- [ReOPD: Multi-Turn On-Policy Distillation with Prefix Replay (arXiv:2607.04763)](https://arxiv.org/abs/2607.04763) · [코드](https://github.com/baohaoliao/ReOPD)
- [RSIBench-Data: Benchmarking Data-Centric Research for Recursive Self-Improvement (arXiv:2607.25886)](https://arxiv.org/abs/2607.25886) · [코드](https://github.com/evolvent-ai/RSIBench-Data)
- [Macaron-V1: Towards Open Continual Learning with Self-Improvement and Mixture-of-LoRA (arXiv:2608.09819)](https://arxiv.org/abs/2608.09819) · [코드](https://github.com/MindLab-Research/Mixture-of-LoRA-Harness)
- [Phantom Gains: Auditing Self-Improvement Against a Measured Null (arXiv:2608.20290)](https://arxiv.org/abs/2608.20290) · [코드](https://github.com/chengxuphd/phantom-gains)
- [Co-Evolving Harnesses and Models: On-Policy Correction Helps Weaker Models Catch Up Where Imitation Fails (arXiv:2609.09134)](https://arxiv.org/abs/2609.09134)

기준일: 2026-09-29.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.

