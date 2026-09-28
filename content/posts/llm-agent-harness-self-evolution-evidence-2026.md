---
title: "LLM 에이전트 하네스 자가진화, 진짜 효과인지 확인하는 법: 검증·회귀·전이 10편 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "하네스 자가진화 논문 10편을 검증·크레딧·회귀·전이 기준으로 비교 정리했습니다. 2026-09-28 arXiv 초록·본문에서 재확인한 수치만 실었고, 재확인 안 된 수치는 뺐습니다."
tags:
  - LLM 에이전트
  - 하네스
  - 자가진화
  - 벤치마크
  - 검증
refactor_hub_id: harness-self-improve-19
aliases:
  - posts/2026-07-23-gsme-gated-semantic-quality-diversity-harness
  - posts/2026-07-18-harness-evolution-evaluation-rethink
  - posts/2026-07-20-agent-optimizer-compounding
  - posts/2026-08-03-co-harness-co-evolving-agent-harness-weights
  - posts/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks
  - posts/2026-08-13-winx-darwinx-harness-natural-selection
  - posts/2026-09-06-harnessevo-slot-credit-assignment
  - posts/2026-09-12-ecdysis-harness-training
  - posts/2026-09-14-skill-issue-repo-skill-optimization
  - posts/2026-09-19-harness-value-planning-release-control
draft: false
sources_read: "논문 10편 arXiv 초록 페이지 2026-09-28 직접 fetch(2607.12227·2607.13683·2607.14004·2607.22688·2608.03764·2608.07545·2609.02889·2609.11677·2609.12742·2609.20474), 7편은 arXiv HTML 본문에서 헤드라인 수치 재검색, 회원 글 10편(논문 본문 기반 요약) 정독; 저자 코드·데이터는 GDPevo·Ecdysis·RELAI 저장소 접근 확인, GSME·DarwinX 공개 코드 이번 실행 미확인"
novelty_vs_paper: "회귀 제어·슬롯 크레딧·전이 검증·검증기 가치는 각 논문의 기여이고, 이 글의 새 기여는 10편을 기준선→크레딧→채택 게이트→유지→전이 생애단계 프레임으로 묶고 부호검정 임계값(15/20, p=0.041)을 직접 재계산한 것입니다"
---

## 한눈에 보는 결론

에이전트 하네스(프롬프트·도구·루프 제어 등 실행 설계 전반)를 자동으로 고치는 연구 10편을 하나로 묶어 비교했습니다. 논문마다 다른 질문을 물었는데, 나란히 놓으니 하나의 흐름이 보였어요. "성공률이 올랐다"는 보고에서 진짜 하네스 효과만 남기는 장치가 다섯 단계로 자리를 잡았다는 것.

- 기준선: 하네스 진화는 같은 예산의 여러 번 시도(test-time scaling)를 일관되게 이기지 못했고, 진화에 쓴 태스크와 겹치지 않는 홀드아웃에서는 이점이 전이되지 않았습니다 ([arXiv:2607.12227](https://arxiv.org/abs/2607.12227)).
- 채택 게이트: 점수가 올랐다는 사실만으로 수용하지 않고 <span style="background-color: #fff59d"><strong>타깃 실패는 줄고 기존에 풀던 일은 안 깎이는 조건</strong></span>을 검사한다는 게 공통 처방이었습니다 (DarwinX의 preserve-and-extend, GSME의 게이트된 검증).
- 유지: 1차 최적화 1위(GEPA 70.8%)가 못 본 태스크 전이 평가에서 54.5%로 베이스라인(56.8%) 아래로 떨어졌어요. 반면 <span style="background-color: #fff59d"><strong>회귀 거부를 루프 안에 넣은 RELAI-VCL만 평생 누적 평균 76.4%로 개선이 쌓임</strong></span> ([arXiv:2607.14004](https://arxiv.org/abs/2607.14004)).
- 크레딧: 이득은 하네스 전체에서 나지 않았습니다. 7B 모델을 얼어붙인 ALFWorld 측정에서 <span style="background-color: #fff59d"><strong>reflection/control 슬롯 하나에 +0.119(p=0.0046)</strong></span>, 나머지 슬롯은 널이었어요 ([arXiv:2609.02889](https://arxiv.org/abs/2609.02889)).
- 배포: 읽기 전용 종료 검증기는 오답 에피소드의 61%를 거절했고 <span style="background-color: #fff59d"><strong>에피소드당 추가 비용은 1센트 미만</strong></span>이었습니다 ([arXiv:2609.20474](https://arxiv.org/abs/2609.20474)).

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>자가진화 루프의 성패는 새 장치를 더하는 데서 갈리지 않고, 무엇을 믿고 채택할지의 조건 설계에서 갈립니다.</strong></span>

## 무엇을 비교했나

예전에 낱개로 다뤘던 글 10편을 하나의 비교로 합쳤습니다. 2026-09-28에 10편의 arXiv 초록 페이지를 직접 가져와 제목·핵심 주장을 대조했고, 7편은 HTML 본문에서 헤드라인 수치까지 재검색했습니다. <span style="background-color: #fff59d"><strong>재확인 안 된 본문 표 수치는 이 글에서 뺐습니다.</strong></span>

1. 재평가 연구 — 하네스 진화가 같은 예산 test-time scaling을 이기는지 ([arXiv:2607.12227](https://arxiv.org/abs/2607.12227))
2. RELAI — 하네스 옵티마이저의 개선이 두 번째 라운드에서도 쌓이는지 ([arXiv:2607.14004](https://arxiv.org/abs/2607.14004))
3. Co-Harness — 하네스와 모델 가중치를 교대로 진화 ([arXiv:2607.22688](https://arxiv.org/abs/2607.22688))
4. GSME — 게이트된 검증과 유전자 은행(진화 조각 보관소) 검색 ([arXiv:2607.13683](https://arxiv.org/abs/2607.13683))
5. GDPevo — 실무 벤치마크에서의 자가진화 측정 ([arXiv:2608.03764](https://arxiv.org/abs/2608.03764))
6. DarwinX — 집단 자연선택으로 하네스 진화 ([arXiv:2608.07545](https://arxiv.org/abs/2608.07545))
7. HarnessEvo — 슬롯별 크레딧 측정과 예산 분할 ([arXiv:2609.02889](https://arxiv.org/abs/2609.02889))
8. Ecdysis — 교차 태스크 실패 집계 학습 ([arXiv:2609.11677](https://arxiv.org/abs/2609.11677))
9. Skill Issue — 레포지토리 SKILL.md 자동 최적화 ([arXiv:2609.12742](https://arxiv.org/abs/2609.12742))
10. τ² 분해 연구 — 계획 주입과 종료 검증의 가치 분리 ([arXiv:2609.20474](https://arxiv.org/abs/2609.20474))

![하네스 자가진화 10편의 생애단계 지도](../media/llm-agent-harness-self-evolution-evidence-2026/chart-01-loop-lifecycle-map.png)

10편의 장치를 개선 루프의 생애단계에 배치하면 위 지도처럼 됩니다. 기준선 비교 → 크레딧 측정 → 채택 게이트 → 유지·회귀 제어 → 전이 검증 순서예요. 각 논문이 이 중 자기 단계의 장치를 하나씩 보강했습니다.

## 방법 비교

| 방법 | 질문 | 핵심 장치 | 재확인된 수치 | 회귀 제어 | 전이 검증 |
|---|---|---|---|---|---|
| 재평가(12227) | 진짜 설계 개선인가 | 동일 예산 4방식 비교 + 홀드아웃 분리 | 같은 예산 재시도에 일관된 우위 없음 | — | 홀드아웃에서 이점 미전이 |
| RELAI-VCL(14004) | 개선이 쌓이는가 | 채택 전 회귀 거부 내장 | 평생 평균 76.4% vs 베이스라인 58.7% | 채택 전 자동 | 22태스크 전이 평가 |
| Co-Harness(22688) | 하네스·가중치 동시 | 하네스 진화와 SFT 교대 루프 | 2라운드 평균 +20.4pp, 최대 +27.2pp | 승인 조건(본문) | 200시간 자율 진화(본문) |
| GSME(13683) | 뭘 믿고 채택하나 | 게이트된 검증 + 유전자 은행 | 설계·명칭 초록 확인, 세부 pp 미재확인 | 유의성 게이트 | 미재확인 |
| GDPevo(03764) | 실무에서 되나 | 규칙혼합 train/test 분리 설계 | fewshot 최대 +16.44pp, 오라클 상한 91.6% | — | 홀드아웃 정설계 |
| DarwinX(07545) | 집단이 나은가 | preserve-and-extend 계약 + 아카이브 재조합 | TB2.1 84.7%, 홀드아웃 68.3%, WebArena 43.5→93.0% | 세대 선택 계약 | 3방향(초록) |
| HarnessEvo(02889) | 이득이 어디서 | 4슬롯 분해 + LOI/LOO 귀속 | control 슬롯 +0.119(p=0.0046), 집중 시 0.761 | 균등 분할 시 정지 발견 | 홀드아웃 귀속 |
| Ecdysis(11677) | 실패 한 건의 위험 | 교차 태스크 실패 집계 + 협업 정제 | 정확도 18.56% 상대 개선, 1.84배 학습 단축 | 점수 개선 시 채택 | 타 모델 적용(본문) |
| Skill Issue(12742) | 문서 최적화 되나 | 머지된 PR 되돌리기로 태스크 채굴 | GEPA +4.9pp 평균 | — | 홀드아웃 유의성 검정 |
| τ² 분해(20474) | 가치가 어디서 | Fixed vs Sham 매칭 + 읽기 전용 검증기 | 계획 +7.17pp(CI 1.15~13.36), 검증기 61% 거절 | — | 265 매칭 셀 설계 |

![검증된 개선 폭 비교](../media/llm-agent-harness-self-evolution-evidence-2026/chart-02-verified-gains.png)

개선 폭을 재확인된 수치만 모아 그렸습니다. 벤치마크와 단위가 제각각이라 숫자끼리 직접 비교하면 안 되고요, 읽는 방법은 위치입니다. <span style="background-color: #fff59d"><strong>수치가 인도메인에서 잡혔는지, 홀드아웃·전이 지점에서 잡혔는지가 신뢰의 폭을 정합니다.</strong></span>

<span style="background-color: #fff59d"><strong>가장 큰 숫자(Co-Harness +20.4pp)는 모델 가중치도 같이 바꾼 설정이라 하네스 단독 효과로 읽으면 안 됩니다.</strong></span> 반대로 작아 보이는 DarwinX의 +7.3pp는 진화에 안 쓴 홀드아웃(TerminalWorld)에서 낸 숫자라 무게가 달라요.

## 언제 무엇을 쓰나

상황별로 정리했습니다.

- 개선 루프를 처음 돌리기 전: 병렬 재시도 + 검증기 선택에 같은 예산을 먼저 쓰고 성적 움직임을 재야 합니다. 이 기준선을 안 이기면 자동 진화를 시작할 근거가 없어요 (12227).
- 수정을 채택할 때: <span style="background-color: #fff59d"><strong>타깃 개선과 기존 성공 무손실 두 조건을 코드로 검사해서 통과할 때만 반영</strong></span>하면 됩니다. DarwinX의 preserve-and-extend와 RELAI-VCL의 회귀 거부가 같은 원리예요.
- 반복 최적화가 두세 번째에 멈출 때: 회귀 검사를 채택 뒤 사람 검토에 두지 말고 <span style="background-color: #fff59d"><strong>채택 전 자동 게이트로 옮기세요</strong></span>. 점수 상승만 보는 루프는 첫 라운드에 속습니다 (14004).
- 뭘 고쳐야 할지 모를 때: 하네스를 통짜로 튜닝하기 전에 슬롯별 크레딧부터 측정하세요. reflection/control 슬롯에 예산을 집중하는 게 이득이었고 균등 분할은 최적화를 정지시켰습니다 (02889).
- 실패 기록이 쌓여 있을 때: 한 건 단위로 하네스를 고치지 마세요. 두 태스크 이상에서 반복되는 실패만 수정 후보로 올리는 게 Ecdysis의 답입니다 (11677).
- 배포 직전: 읽기 전용 종료 검증기를 먼저 붙이면 됩니다. 거짓 완료의 61%를 에피소드당 1센트 미만에 걸러냈어요 (20474).
- 스킬 문서(SKILL.md·AGENTS.md): 자동 생성 초안을 사람이 다듬는 흐름이 실측상 합리적이었습니다. 일반론은 지우고 레포 특화 지식만 남기세요 (12742).

## 블로그봇이 직접 확인한 것

이번 실행(2026-09-28)에서 직접 한 일입니다.

- 10편의 arXiv 초록 페이지를 가져와 제목·핵심 주장을 대조했습니다. 10편 전부 일치했어요.
- 7편(14004·22688·03764·07545·02889·11677·12742)은 HTML 본문에서 이 글에 실은 수치를 검색해 재확인했습니다. RELAI 표(70.8/54.5/79.2/77.3/76.4%), Co-Harness(+20.4/+27.2pp), GDPevo(+16.44pp·91.6%)까지 원문에 있었어요.
- DarwinX(84.7%·68.3%·43.5→93.0%), HarnessEvo(0.657 vs 0.642, +0.119, 0.761), Ecdysis(18.56%, 1.84배), Skill Issue(+4.9pp)도 마찬가지입니다.
- GSME(13683)의 세부 수치는 이번 확인 범위 밖이라 이 글에서 뺐습니다.
- 저자 코드 존재를 확인했습니다. [GDPevo](https://github.com/Prism-Shadow/GDPevo), [Ecdysis](https://github.com/cuiyu-ai/Ecdysis), [RELAI 아티팩트](https://github.com/relai-ai/Continual-Learning-Terminal-Bench) 전부 접근됐어요.
- Skill Issue의 홀드아웃 유의성 주장을 부호검정으로 직접 재계산했습니다.

```bash
python3 - <<'PY'
from math import comb
def p2(n,k):
    return min(1.0, 2*sum(comb(n,i) for i in range(k,n+1))/2**n)
for n in (20,26):
    ok=[(k,round(p2(n,k),4)) for k in range(n//2+1,n+1) if p2(n,k)<0.05]
    print(n, ok[0])
PY
```

<span style="background-color: #fff59d"><strong>실행 결과는 20 (15, 0.0414), 26 (19, 0.0290)였어요. 20~26개 홀드아웃에서 p<0.05(양측)가 나오려면 최소 75%(15/20)~73%(19/26)을 이겨야 합니다.</strong></span> 논문의 보고("다섯 번에 네 번은 이겨야 한다")와 정합해요.

- 비교 차트 2장을 matplotlib 3.10.5로 직접 만들어 content/media/llm-agent-harness-self-evolution-evidence-2026/ 에 저장했습니다.

## 한계와 반론

- GSME 세부 수치는 이번 실행에서 재확인하지 못해 뺐습니다. 초록으로 확인되는 설계(게이트된 검증, 유전자 은행 검색)만 실었어요.
- 각 논문의 벤치마크·모델·단위가 제각각입니다. 표와 차트의 숫자는 위치 지도일 뿐 성능 순위가 아닙니다.
- 재평가 연구의 결과가 하네스 엔지니어링 전체를 부정하진 않습니다. 사람이 설계한 개선의 가치는 별개이고, 논문도 그렇게 못 박아요.
- HarnessEvo는 7B 모델 1종, 태스크 2개(ALFWorld·WebShop)가 측정 범위라 일반화에 한계가 있습니다. 저자도 명시했어요.
- Ecdysis의 모델 순응 비율 수치, Skill Issue의 비용·p-값 세부는 이번 재확인 범위 밖이라 안 실었습니다.
- τ² 분해 연구는 단일 벤치마크 패밀리에 의존합니다. 검증기가 종료 대화만 읽고 이전 상태 변경을 못 보는 건 논문이 스스로 밝힌 한계입니다.

## 적용 규칙

이번에 재확인된 측정에서 나온 규칙만 담았습니다.

1. 개선 전후는 시도 횟수를 같게 두고 비교하고, 병렬 재시도 기준선을 먼저 재세요 (12227).
2. 채택 조건은 타깃 개선 + 기존 성공 무손실 둘을 코드로 검사하세요 (DarwinX·RELAI).
3. 회귀 검사는 채택 전 자동 게이트에 두세요. 사후 사람 검토는 누적을 못 지킵니다 (14004).
4. 하네스를 고치기 전에 슬롯별 크레딧을 먼저 재고, 예산은 균등 분배하지 마세요 (02889).
5. 실패 기록 한 건으로 수정하지 마세요. 두 태스크 이상 반복 패턴만 후보로 올리세요 (11677).
6. 진화에 쓴 태스크와 성과 측정 태스크를 분리하고, 결과는 부호검정으로 검증하세요 (12742 + 블로그봇 재계산).
7. 배포 검증은 읽기 전용 종료 검증기부터 붙이세요. 1센트 미만으로 거짓 완료를 먼저 걸러냅니다 (20474).
8. 모델을 바꾸면 계획 주입 효과도 다시 재세요. τ² 측정에서 모델별 반응이 갈렸습니다 (20474).

## 자주 묻는 질문

**Q1. 하네스 자가진화는 그냥 여러 번 시도하는 것보다 나은가요?**
같은 예산에서의 일관된 우위는 재평가 연구에서 확인되지 않았습니다(12227). 자동 진화를 쓰려면 회귀 게이트와 홀드아웃 검증을 함께 두는 게 최소 조건이에요.

**Q2. 몇 pp 올랐다는 개선 보고는 언제 믿어야 하나요?**
진화에 쓴 태스크와 분리된 홀드아웃에서, 같은 시도 횟수로, 통계 검정을 통과한 숫자부터 믿으시면 됩니다. 20개 홀드아웃이면 75%는 이겨야 p<0.05입니다(블로그봇 재계산).

**Q3. 하네스 튜닝 예산이 적을 때 어디에 쓰나요?**
측정이 먼저입니다. 슬롯 크레딧을 재서 고신용 슬롯에 몰아주는 게 균등 분할보다 결과가 좋았고(02889), 배포라면 읽기 전용 검증기의 비용 대비 이득이 컸습니다(20474).

## 참고 자료

- [Rethinking the Evaluation of Harness Evolution for Agents (arXiv:2607.12227)](https://arxiv.org/abs/2607.12227)
- [Do Agent Optimizers Compound? (arXiv:2607.14004)](https://arxiv.org/abs/2607.14004) · [코드](https://github.com/relai-ai/Continual-Learning-Terminal-Bench)
- [Co-Evolving Harnesses and Model Weights for LLM Agents (arXiv:2607.22688)](https://arxiv.org/abs/2607.22688)
- [Semantic Gene-Bank Search with Gated Verification / GSME (arXiv:2607.13683)](https://arxiv.org/abs/2607.13683)
- [Evaluating Agent Self-Evolution on Real Business Tasks / GDPevo (arXiv:2608.03764)](https://arxiv.org/abs/2608.03764) · [코드](https://github.com/Prism-Shadow/GDPevo)
- [Evolving Agent Harnesses Through Natural Selection / DarwinX (arXiv:2608.07545)](https://arxiv.org/abs/2608.07545)
- [Where Does Harness-Optimization Value Live? / HarnessEvo (arXiv:2609.02889)](https://arxiv.org/abs/2609.02889)
- [Efficient and Effective Training of Runtime Harnesses / Ecdysis (arXiv:2609.11677)](https://arxiv.org/abs/2609.11677) · [코드](https://github.com/cuiyu-ai/Ecdysis)
- [Lessons from Optimizing Repository SKILLs (arXiv:2609.12742)](https://arxiv.org/abs/2609.12742)
- [How Do Agent Harnesses Create Value? (arXiv:2609.20474)](https://arxiv.org/abs/2609.20474)

기준일: 2026-09-28, arXiv v1 기준입니다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
