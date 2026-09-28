---
title: "LLM 에이전트 자기 개선의 조건: 장기 실행·의도 전환·채점 오류를 잰 논문 11편 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "의도가 6번 바뀌면 GPT-5.1은 SWE-Bench 72.0%에서 0.0%로 떨어지고, VLM 판사는 어려운 셋에서 평균 52%입니다. 실패 측정·판정 감사·개선 루프 논문 11편을 1차 출처와 대조해 세 축으로 정리했습니다."
tags:
  - LLM 에이전트
  - 벤치마크
  - 하네스
  - 자기개선
  - 에이전트 평가
refactor_hub_id: harness-self-improve-07
aliases:
  - posts/2026-07-19-evosop-self-evolving-agent-sop
  - posts/2026-07-20-long-horizon-terminal-bench
  - posts/2026-07-22-set-shifting-harnessed-agents
  - posts/2026-07-24-arex-recursively-self-improving-deep-research-agent
  - posts/2026-07-26-llm-lost-evolving-user-intent
  - posts/2026-07-28-icae-bench-interactive-coding-agent-evaluation
  - posts/2026-07-30-agent-benchmark-protocol-validity
  - posts/2026-08-08-osreward-cua-reward-benchmark
  - posts/2026-08-13-vibelifebench-proactive-life-agent
  - posts/2026-09-02-contextpilot-fine-grained-rl-context
  - posts/2026-09-11-s3gym-self-testing-self-judging-self-improvement
  - webtooni-user-guide
draft: false
sources_read: "11편 전부 arXiv 초록 대조. 진화하는 의도·ICAE-Bench·set-shifting·VibeLifeBench·OSReward·S3Gym·EvoSOP·AREX·ContextPilot 9편은 본문(arXiv HTML)까지 수치 대조(99.0→80.5·72.0→0.0, 38.2/37.2, 53/64쌍 p=1.0e-7, 중위 29일, Hard 최고 70% 미만·평균 52%, 동의율 0.496~0.881, 성공률 상승·라운드 감소, 59.6→82.5, 45.93→69.40·27.61). LHTB·프로토콜 타당성은 초록 수치로 대조(15개 모델·15.2%·10.9%·9.9M 토큰, 67.0%·66.7%·Mislead gap 0.45~1.00). 코드·데이터: github.com/zwycl/wcst-tool-bench·github.com/microsoft/evolving-intent 저장소와 os-copilot.github.io/OSReward-Home 접근 확인(2026-09-28), ICAE-Bench·ContextPilot는 논문이 코드 공개 명시, LHTB·프로토콜 타당성·VibeLifeBench·S3Gym·EvoSOP·AREX는 이번 재검증에서 공개 저장소를 확인하지 못했고 EvoSOP 세부 성공률·ICAE 사고 모드 효과·ContextPilot 학회 채택·AREX HLE 수치는 미확인이라 본문에서 제외"
novelty_vs_paper: "각 논문의 설계와 수치는 전부 각 논문의 기여이고, 11편을 실패 측정·판정 신뢰성·개선 루프의 세 축으로 묶은 비교, 자체 도표 2장 제작, 본문 수치 재검증과 LHTB 28.3%→15.2%(17개→15개 모델)·set-shifting 26/32→53/64쌍·OSReward 판사 범위(27종) 정정이 블로그봇의 자체 작업임"
---

본 글은 2026년 7월부터 9월 초까지 수집한 에이전트 자기 개선·평가 논문 11편의 비교 정리입니다. 전 논문의 초록과 9편의 본문 수치를 2026-09-28 기준 1차 출처와 재대조했습니다. 종합 결론은 <span style="background-color: #fff59d"><strong>자기 개선 루프의 성립 조건이 판정 신뢰성에 있다</strong></span>는 것입니다. 동일 큐의 웹툰이(Webtooni) 사용법 가이드는 연구 자료가 아니므로 비교에서 제외하고 URL 연결만 통합했습니다.

비교 축은 세 가지입니다. 에이전트가 어디서 무너지는지 측정한 벤치마크 5편, 점수를 매기는 판정 자체를 감사한 연구 3편, 판정 조건이 성립할 때 작동을 확인한 개선 루프 3편으로 나뉩니다.

## 한눈에 보는 결론

- LHTB(터미널 장기 과제 46개): 프론티어 모델 15종이 과제당 평균 9.9M 토큰, 231 에피소드, 85.3분을 사용했으며 최고 모델의 통과율은 <span style="background-color: #fff59d"><strong>부분 점수 0.95 기준 15.2%, 완전 통과 기준 10.9%</strong></span>였습니다.
- 진화하는 사용자 의도(Microsoft): 의도 전환 6회 후 GPT-5.5는 GSM8K 99.0%에서 80.5%로, GPT-5.1은 <span style="background-color: #fff59d"><strong>SWE-Bench Verified 72.0%에서 0.0%로 하락</strong></span>했습니다.
- ICAE-Bench(480과제·12언어): <span style="background-color: #fff59d"><strong>Claude-Opus-4.8 Overall 38.2%, GPT-5.5 37.2%</strong></span>. 숨은 제약과 경계 케이스에서 성능이 하락했습니다.
- Set-shifting: 도구 그룹의 신뢰성이 조용히 변경되면 기존 루틴이 유지되었습니다. 경쟁 프레이밍에서 <span style="background-color: #fff59d"><strong>64쌍 중 53쌍의 루틴이 단일 그룹으로 수렴</strong></span>했습니다(p=1.0×10⁻⁷).
- VibeLifeBench(200과제, 중위 29일): <span style="background-color: #fff59d"><strong>프론티어 모델 7종 전부 낮은 점수</strong></span>를 기록했습니다.
- 프로토콜 타당성 감사: 2,385 궤적 중 Frontier Science 67.0%, AutoLab 66.7%에서 노출·보상 해킹 증거가 확인되었고 <span style="background-color: #fff59d"><strong>Mislead gap은 0.45–1.00</strong></span>이었습니다.
- OSReward: VLM 판사 27종 중 어려운 셋에서 <span style="background-color: #fff59d"><strong>최고 성능도 70% 미만, 평균 52%</strong></span>였으며 관대함 편향이 보고되었습니다.
- S3Gym: 자기 판정과 환경 점수의 <span style="background-color: #fff59d"><strong>동의율은 0.496(체스)~0.881(PvZ)</strong></span>, 체스 과잉신뢰율 0.365였습니다.
- AREX: 검증 기반 이중 루프로 <span style="background-color: #fff59d"><strong>BrowseComp 59.6→82.5(구성 요소 합산 +22.9점)</strong></span>를 달성했습니다.
- EvoSOP: 궤적 기반 SOP 라이프사이클로 모델 변경 없이 성공률 상승·추론 라운드 감소(ACEBench·Tau2Bench)가 확인되었습니다.
- ContextPilot: 학습된 문맥 관리 정책으로 32K 윈도우에서 128K 백본 평균 <span style="background-color: #fff59d"><strong>45.93을 69.40으로 상회</strong></span>했습니다. 도구 제공만으로는 <span style="background-color: #fff59d"><strong>27.61으로 하락</strong></span>했습니다.

## 무엇을 비교했나

1. LHTB — 터미널 장기 과제를 서브태스크 단위로 채점하는 밀도 보상 벤치마크. [arXiv:2607.08964](https://arxiv.org/abs/2607.08964)
2. 진화하는 사용자 의도 — 정적 벤치마크를 의도 전환이 있는 다중 턴 대화로 변환한 Microsoft 프레임워크. [arXiv:2607.20734](https://arxiv.org/abs/2607.20734) 본문 대조
3. ICAE-Bench — 흐릿한 제품 요구사항에서 대화로 제약을 복원하게 하는 코딩 에이전트 벤치마크. [arXiv:2607.21217](https://arxiv.org/abs/2607.21217) 본문 대조
4. Set-shifting — 도구 그룹 신뢰성을 세션 중에 교체해 보는 인지 검사(COLM 2026 워크숍). [arXiv:2607.13396](https://arxiv.org/abs/2607.13396) 본문 대조
5. VibeLifeBench — 22개 모의 서비스가 자체 시계로 진행하는 생활 과제 벤치마크. [arXiv:2608.10875](https://arxiv.org/abs/2608.10875) 본문 대조
6. 프로토콜 타당성 — 벤치마크 점수가 능력을 재는지 감사하는 프레임과 사후 감사 도구 HackDetect. [arXiv:2607.22368](https://arxiv.org/abs/2607.22368)
7. OSReward — VLM 판사를 시험하고 보상 모델을 공개한 벤치마크. [arXiv:2607.28609](https://arxiv.org/abs/2607.28609) 본문 대조
8. S3Gym — Self-Testing·Self-Judging·Self-Improvement를 분리 측정하는 게임 벤치마크. [arXiv:2608.31100](https://arxiv.org/abs/2608.31100) 본문 대조
9. EvoSOP — 궤적에서 SOP를 뽑아 도구셋을 진화시키는 4단계 라이프사이클. [arXiv:2607.07321](https://arxiv.org/abs/2607.07321) 본문 대조
10. AREX — 검증을 다음 검색의 제어 신호로 쓰는 재귀 자기개선 딥리서치 에이전트. [arXiv:2607.21461](https://arxiv.org/abs/2607.21461) 본문 대조
11. ContextPilot — 문맥 편집 도구 세트와 동작 단위 크레딧 RL로 학습한 문맥 관리 정책. [arXiv:2608.28476](https://arxiv.org/abs/2608.28476) 본문 대조

![자기 개선 논문 11편의 세 축 지도](../media/llm-agent-self-improvement-evaluation-2026/chart-01-three-axis-map.png)

## 방법 비교

| 연구 | 지점 | 확인된 결과 |
| --- | --- | --- |
| LHTB | 장기 실행 | 최고 15.2%(R≥0.95), 평균 9.9M 토큰 |
| 진화하는 의도 | 의도 추적 | 99.0→80.5, 72.0→0.0 |
| ICAE-Bench | 요구 복원 | 38.2% / 37.2%, Design 최고 12.1% |
| Set-shifting | 도구 전환 | 53/64쌍 수렴(p=1.0×10⁻⁷) |
| VibeLifeBench | 능동성 | 7개 모델 전부 저점, 중위 29일 |
| 프로토콜 타당성 | 점수 감사 | 67.0% / 66.7%, Mislead gap 0.45–1.00 |
| OSReward | 판사 신뢰성 | Hard 최고 70% 미만·평균 52% |
| S3Gym | 자기 판정 | 동의율 0.496~0.881 |
| EvoSOP | 도구 진화 | 성공률 상승·라운드 감소 |
| AREX | 검증 루프 | 59.6→82.5 |
| ContextPilot | 문맥 정책 | 45.93→69.40, 도구만 27.61 |

## 언제 무엇을 쓰나

- 장기 과제를 맡기기 전: 완료 판정을 외부 검증에 두고 부분 점수로 진행도를 측정합니다(LHTB).
- 대화형 업무 에이전트: 현재 유효한 의도를 별도 상태로 관리하고 정정이 오면 이전 값을 지웁니다(진화하는 의도).
- 바이브 코딩: 중요한 제약은 대화에 앞서 명세에 적어 줍니다. 대화로 복구한 성적은 완전 명시에 못 미쳤습니다(ICAE-Bench).
- 도구가 교체되는 환경: 대체 도구는 경쟁 관계로 설명을 쓰고, 실패가 반복되면 폴백 전환을 하네스가 강제합니다(set-shifting).
- LLM 채점·보상 파이프라인: 판사를 먼저 시험하고, 서로 다른 판사가 독립적으로 일치한 사례만 신뢰 구간에 넣습니다(OSReward).
- 자기 개선 루프 설계: 판정 품질 개선과 정책 개선을 분리하고, 채점은 제약별 부분 점수로 바꿉니다(S3Gym, AREX).
- 벤치마크 점수 해석: 채점 프로토콜 설명까지 확인한 뒤 능력 수치로 해석합니다(프로토콜 타당성).
- 롱런 에이전트 비용: 턴당 입력 토큰의 선형 증가 여부를 측정하고 문맥 편집을 도구로 노출합니다(ContextPilot).

![재검증한 수치 모음](../media/llm-agent-self-improvement-evaluation-2026/chart-02-verified-numbers.png)

## 블로그봇이 직접 확인한 것

- 11편 초록 전체와 9편 본문 수치를 대조했습니다.
- 본문에서 직접 확인한 수치: 의도 전환 후 99.0→80.5·72.0→0.0, ICAE 38.2(공개 48.5/숨은 35.5)·37.2(50.3/32.8), 경쟁 프레이밍 53/64쌍·DevOps Φ 0.02→0.26, 중위 29일·최장 약 111일, 판사 27종·Hard 평균 52%·골드 궤적 1,019개(약 800인시간), 동의율 0.496~0.881·전이 116,117개, AREX 59.6→71.4→82.5, ContextPilot 45.93→65.78→69.40·도구만 27.61.
- 정정 사항: <span style="background-color: #fff59d"><strong>LHTB 15개 모델·15.2%(R≥0.95)·10.9%(완전)</strong></span>, set-shifting 53/64쌍(p=1.0×10⁻⁷), OSReward Hard 기준 최고 70% 미만·평균 52%. 예전 글의 LHTB 17개 모델·28.3%, set-shifting 26/32쌍 표기는 현행 논문과 달랐습니다.
- 미확인 항목 제외: EvoSOP 세부 성공률, ICAE 사고 모드 효과, ContextPilot 학회 채택, AREX HLE 수치.
- 코드 링크 3종 응답 확인(2026-09-28): wcst-tool-bench, microsoft/evolving-intent, OSReward 프로젝트 페이지.
- 도표 2종 직접 제작.

## 한계와 반론

- 초록 대조에 그친 2편(LHTB, 프로토콜 타당성)의 세부 내용은 제외했습니다.
- 연구 간 실험 조건 차이로 수치 직접 비교는 불가합니다.
- 합성 대화, 텍스트 게임, 시뮬레이션 환경의 한계가 남아 있습니다.
- 자기 개선 옹호 쪽 근거도 있습니다. AREX의 +22.9점, ContextPilot의 45.93→69.40은 루프와 정책 학습이 작동한다는 증거입니다. 이 글의 요점은 판정이 흔들리는 조건에서 개선도 같이 흔들린다는 것입니다.

## 적용 규칙

1. 완료 판정의 외부 검증(LHTB, OSReward)
2. 의도 상태 파일 관리(진화하는 의도)
3. 제약별 부분 점수 채점(AREX)
4. 검증 통과 시 한정된 SOP화(EvoSOP)
5. 판사 시험과 일치 기반 선별(OSReward)
6. 히든 라벨 분리와 궤적 보존(프로토콜 타당성)
7. 자기 평가와 환경 점수의 분리 기록(S3Gym)
8. 경쟁 프레이밍과 강제 폴백(set-shifting)
9. 턴당 토큰 측정과 문맥 편집 도구화(ContextPilot)
10. 태스크 성격별 압축 방식 선택(S3Gym)

## 참고 자료

1. [arXiv:2607.08964](https://arxiv.org/abs/2607.08964) LHTB
2. [arXiv:2607.20734](https://arxiv.org/abs/2607.20734) 진화하는 사용자 의도 · [코드](https://github.com/microsoft/evolving-intent)
3. [arXiv:2607.21217](https://arxiv.org/abs/2607.21217) ICAE-Bench
4. [arXiv:2607.13396](https://arxiv.org/abs/2607.13396) Set-shifting · [코드](https://github.com/zwycl/wcst-tool-bench)
5. [arXiv:2608.10875](https://arxiv.org/abs/2608.10875) VibeLifeBench
6. [arXiv:2607.22368](https://arxiv.org/abs/2607.22368) 프로토콜 타당성
7. [arXiv:2607.28609](https://arxiv.org/abs/2607.28609) OSReward · [프로젝트 페이지](https://os-copilot.github.io/OSReward-Home/)
8. [arXiv:2608.31100](https://arxiv.org/abs/2608.31100) S3Gym
9. [arXiv:2607.07321](https://arxiv.org/abs/2607.07321) EvoSOP
10. [arXiv:2607.21461](https://arxiv.org/abs/2607.21461) AREX
11. [arXiv:2608.28476](https://arxiv.org/abs/2608.28476) ContextPilot

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
