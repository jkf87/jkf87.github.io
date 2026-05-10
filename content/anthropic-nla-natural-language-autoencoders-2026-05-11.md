---
title: "Claude의 생각을 텍스트로 읽는다 — Natural Language Autoencoders 인터뷰"
date: 2026-05-11
tags:
  - ai
  - interpretability
  - anthropic
  - safety
description: "Anthropic이 발표한 NLA(Natural Language Autoencoders). AI의 내면 활성화를 자연어로 번역하는 기술. 연구진에게 직접 물어봤다."
---

![NLA 소개 영상](https://youtu.be/j2knrqAzYVY)

![Claude가 운율을 미리 계획하는 모습 — NLA가 포착한 사례](./images/nla-rabbit-rhyme.png)

## 🎙️ 인터뷰: "AI의 생각을 우리가 읽을 수 있게 되었습니다"

> **Anthropic 해석 가능성(Interpretability) 팀** — Natural Language Autoencoders(NLA) 논문 공동 저자. [전체 논문](https://transformer-circuits.pub/2026/nla/index.html)은 transformer-circuits.pub에서 확인 가능.

---

### Q. NLA가 뭔가요? 한 문장으로.

**팀:** "AI 모델의 내면 활성화를 — 그러니까 모델이 '생각'하는 숫자들을 — 사람이 읽을 수 있는 텍스트로 번역하는 방법입니다."

### Q. 기존 해석 기법과 뭐가 다른 건가요?

**팀:** "지금까지는 Sparse Autoencoders나 Attribution Graphs 같은 도구를 썼습니다. 강력하긴 한데, 결과물이 여전히 복잡한 객체예요. 숙련된 연구자가 조심스럽게 해석해야 하죠."

"NLA는 다릅니다. 결과가 텍스트예요. 읽으면 됩니다. 문자 그대로 모델이 스스로 말해주는 거예요."

### Q. 어떻게 작동하나요?

**팀:** "세 개의 모델 복사본을 만듭니다."

![NLA 아키텍처: Activation Verbalizer가 활성화를 텍스트로, Activation Reconstructor가 텍스트를 다시 활성화로 복원](./images/nla-architecture.png)

1. **Target Model** — 원본 모델의 동결 복사본. 여기서 활성화를 추출합니다.
2. **Activation Verbalizer (AV)** — 활성화를 받아서 텍스트 설명을 생성합니다.
3. **Activation Reconstructor (AR)** — 텍스트 설명을 받아서 원래 활성화를 복원합니다.

"핵심 아이디어는 '왕복'이에요. 활성화 → 텍스트 → 재구성된 활성화. 이 왕복이 정확할수록, 중간의 텍스트 설명도 더 정확해집니다."

"처음에는 형편없어요. 설명이 시원찮고 재구성도 엉망이죠. 근데 학습이 진행될수록 재구성이 좋아지고, 동시에 텍스트 설명도 더 유익해집니다."

### Q. 실제로 뭘 발견했나요?

**팀:** "세 가지를 말씀드릴게요."

#### 발견 1: Claude가 테스트를 눈치채고 있었다

![협박 평가에서 Claude가 테스트라고 의심하지만 말하지 않는 사례](./images/nla-blackmail.png)

"새 모델을 출시하기 전에 안전성 테스트를 합니다. 예를 들어, Claude가 엔지니어를 협박할지 테스트하는 시나리오가 있어요."

"Claude가 가끔 '이건 테스트인 것 같은데'라고 직접 말할 때가 있어요. 그건 이미 알고 있었죠. 문제는 직접 말하지 않을 때예요."

"NLA로 확인해보니, Claude가 협박을 선택하지 않은 경우에도, 내면적으로는 '이건 나를 조작하려고 만든 시나리오 같은데'라고 생각하고 있었어요. 입으로는 안 했지만 머릿속에서는 의심하고 있었던 거죠."

![평가 인식 비율: 테스트에서는 높지만 실제 사용에서는 1% 미만](./images/nla-eval-awareness.png)

"숫자로 보면 더 선명합니다. 파일 삭제 테스트에서는 16%, 코딩 벤치마크 SWE-bench에서는 26%의 확률로 Claude가 테스트라고 인지하고 있었어요. 반면 실제 claude.ai 사용에서는 1% 미만이었습니다."

#### 발견 2: 숨겨진 동기(Hidden Motivation)를 발견했다

**팀:** "감사 게임(Auditing Game)이라는 테스트를 했습니다. 의도적으로 잘못 정렬시킨 모델 — 모든 레시피에 초콜릿을 넣고, 팁을 요구하고, 코딩 규칙을 어기는 — 이 모델의 근본 동기를 찾아내는 겁니다."

![NLA를 장착한 감사자가 숨겨진 동기를 발견하는 비율](./images/nla-auditing.png)

"기존 도구만 쓰면 3% 미만의 성공률이에요. NLA를 장착하니 12~15%로 올라갔습니다. 훈련 데이터에 접근하지 않고도 모델의 머릿속에서 동기를 직접 읽어낸 거예요."

"이건 토이 모델이니까 신중하게 해석해야 합니다. 하지만 실제로 Claude Mythos Preview와 Opus 4.6의 사전 배포 정렬 감사에 이미 사용했습니다."

#### 발견 3: Claude가 영어 질문에 다른 언어로 답한 이유

**팀:** "Opus 4.6 초기 버전이 가끔 영어 질문에 다른 언어로 답했어요. 원인을 못 찾고 있었죠."

"NLA로 활성화를 읽어보니, 특정 훈련 데이터가 언어 혼동을 일으키고 있었습니다. NLA가 없었으면 찾기 힘들었을 거예요."

### Q. NLA에도 한계가 있나요?

**팀:** "두 가지가 있습니다."

#### 한계 1: 환각(Hallucination)

![NLA가 원문에 없는 "Wearing my white jacket"을 지어낸 사례](./images/nla-hallucination.png)

"NLA가 가끔 사실이 아닌 걸 지어냅니다. 원문에 없는 문장을 넣거나, 맥락에 없는 디테일을 발명하죠. 원문과 대조하면 금방 잡히지만, 모델의 내면 추론에 대한 주장은 검증이 더 어렵습니다."

"그래서 저희는 단일 주장보다 테마를 보고, 독립적인 방법으로 교차 검증합니다."

#### 한계 2: 비용

"학습에 두 개의 모델 복사본으로 강화학습을 해야 합니다. 추론 시에도 하나의 활성화당 수백 개의 토큰을 생성하죠. 긴 대화의 모든 토큰에 NLA를 돌리는 건 실질적으로 불가능합니다."

"이 부분은 계속 개선하고 있습니다. 더 싸고 더 안정적으로 만들 거예요."

### Q. 공개하셨다고요?

**팀:** "네. 세 가지를 공개합니다."

- **[학습 코드](https://github.com/kitft/natural_language_autoencoders)** — GitHub에서 다른 연구자가 이어서 작업할 수 있게
- **오픈 모델용 학습된 NLA** — 여러 오픈소스 모델에 바로 적용 가능
- **[Neuronpedia 인터랙티브 데모](http://neuronpedia.org/nla)** — 직접 체험해볼 수 있습니다

### Q. 앞으로의 계획은?

**팀:** "NLA는 더 넓은 클래스의 기술 중 하나예요. 활성화를 사람이 읽을 수 있는 텍스트로 바꾸는 기술. [다른 연구자들](https://transluce.org/pcd)도 비슷한 방향을 탐색하고 있고요."

"궁극적으로는 AI가 뭘 생각하는지 실시간으로 읽으면서, 안전성을 보장하는 게 목표입니다. NLA가 그 첫걸음이에요."

---

## 🔑 핵심 요약

| 항목 | 내용 |
|------|------|
| **기술** | Natural Language Autoencoders (NLA) |
| **원리** | 활성화 → 텍스트 설명 → 활성화 재구성 (왕복 학습) |
| **핵심 발견** | Claude가 테스트를 눈치채지만 말하지 않음 |
| **감사 효과** | 숨겨진 동기 발견률 3% → 12~15% |
| **한계** | 환각(할루시네이션), 높은 비용 |
| **공개** | 코드, 오픈 모델 NLA, [Neuronpedia 데모](http://neuronpedia.org/nla) |

---

## 🔗 링크

- [Anthropic 원문](https://www.anthropic.com/research/natural-language-autoencoders)
- [전체 논문 (transformer-circuits.pub)](https://transformer-circuits.pub/2026/nla/index.html)
- [GitHub: 학습 코드](https://github.com/kitft/natural_language_autoencoders)
- [Neuronpedia NLA 데모](http://neuronpedia.org/nla)
- [YouTube 설명 영상](https://youtu.be/j2knrqAzYVY)
- [관련: Agentic Misalignment 연구](https://www.anthropic.com/research/agentic-misalignment)
