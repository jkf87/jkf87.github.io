---
title: "OpenAI o3로 희귀질환 미진단 사례를 다시 읽었더니 — 핵심은 ‘case packet’이었다"
date: 2026-06-21
tags:
  - OpenAI
  - o3
  - Deep-Research
  - medical-ai
  - bioinformatics
  - rare-disease
  - HPO
  - clinical-genomics
  - AI
source: OpenAI
source_url: https://openai.com/index/diagnose-rare-childhood-diseases/
draft: false
description: "OpenAI와 Boston Children’s Hospital 연구진의 NEJM AI 희귀질환 재분석 연구를 원문 중심으로 정리한다. o3 Deep Research가 376건의 미해결 사례에서 18건의 진단 단서를 찾았지만, 핵심은 AI 단독 진단이 아니라 사람 주도의 case packet·전문가 검증 워크플로우였다."
---

OpenAI가 2026년 6월 18일 공개한 글의 요지는 이렇다.

> **OpenAI o3 Deep Research를 이용해 이미 전문가들이 분석했지만 풀리지 않았던 희귀 유전질환 사례 376건을 다시 분석했고, 그중 18건에서 임상적으로 확인된 진단으로 이어지는 단서를 찾았다.**

원문 제목은 “Using AI to help physicians diagnose rare genetic diseases affecting children”. 연구는 NEJM AI에 실렸고, Boston Children’s Hospital Manton Center for Orphan Disease Research, Harvard University, OpenAI 연구진이 참여했다.

숫자만 먼저 보면 이렇다.

- 재분석 대상: **이전에 분석했지만 미해결로 남은 376건**
- 최종 진단으로 이어진 사례: **18건**
- 추가 진단률: **4.8%**
- 사용 모델: **OpenAI o3 Deep Research**
- 모델의 역할: 진단 확정이 아니라 **근거가 연결된 후보 설명 제시**

원문이 계속 강조하는 선이 있다. 모델은 환자를 진단하지 않았다. 임상 결정을 내리지 않았다. 모델은 “이 환자는 이 유전자/변이/질환 조합으로 설명될 수 있다”는 **reviewable hypothesis**를 만들었고, 실제 진단은 전문가 검토, 추가 검사, CLIA 인증 임상 실험실 확인, 가족에게 결과 반환까지 거친 것만 카운트했다.

![Human-guided AI workflow for rare disease genomic reanalysis](/images/openai-o3-rare-disease-case-packet-2026-06-21/human-guided-ai-workflow.svg)

---

## 왜 예전 미해결 사례에서 새 답이 나올 수 있나

원문이 먼저 깔고 가는 전제는 이거다.

희귀질환 환자는 유전체 검사를 받아도 상당수가 명확한 유전 진단을 받지 못한다. 원문 표현으로는 extensive testing과 specialist review 이후에도 **roughly half**가 미진단으로 남는다.

이유는 단순히 “검사가 부족해서”가 아니다.

- 가능한 유전 변이가 너무 많다. 수천 개에서 많게는 수백만 개의 후보를 봐야 한다.
- 임상 기록, 가족력, 검사 결과가 서로 다른 DB와 형식에 흩어져 있다.
- 병원 기록과 연구 DB가 서로 다른 식별자와 vocab을 쓴다.
- 어떤 유전자-질병 관계는 환자가 처음 검사받을 당시에는 아직 알려져 있지 않았을 수 있다.
- 시간이 지나면 논문, case report, ClinVar 같은 분류 근거가 계속 쌓인다.

그래서 희귀질환 재분석은 단순 분석 문제가 아니라 **maintenance problem**이 된다. 환자의 genome은 변하지 않지만, 그 genome을 해석하는 지식베이스는 계속 움직인다.

이 연구의 출발점은 여기다.

> 예전에 답이 안 나왔던 case라도, 새 지식과 더 나은 연결 방식으로 다시 보면 답이 나올 수 있다.

---

## 실제 재분석은 어떻게 했나

원문에서 가장 중요한 문단은 “How the reanalysis worked”다. 여기에 데이터 구조가 꽤 명확히 나온다.

연구팀은 각 사례마다 **de-identified packet**을 만들었다. 즉 개인정보를 제거한 환자별 입력 묶음이다. 이 안에는 다음이 들어갔다.

- 환자의 임상 양상을 설명하는 **standardized Human Phenotype Ontology, HPO terms**
- 가끔 포함되는 clinician notes
- descriptive clinical diagnosis가 있는 경우 그 정보
- 나이, 성별 같은 metadata
- **filtered variant table**
- 각 variant의 rarity
- encoded protein에 대한 predicted effect
- ClinVar classification
- available family members 전체에 대한 signal quality
- 대부분의 경우 child와 biological parents 양쪽, 즉 trio 데이터

원문 표현을 한국어로 풀면 이렇다.

```text
환자별 de-identified packet
├─ HPO로 표준화된 증상 목록
├─ 임상의 메모 / 기존 임상적 의심 진단
├─ age, gender 같은 메타데이터
└─ 필터링된 variant table
   ├─ variant rarity
   ├─ predicted protein effect
   ├─ ClinVar classification
   └─ family members별 signal quality
```

여기서 핵심은 **원시 유전체 데이터를 통째로 o3에게 던진 게 아니라는 점**이다.

이런 구조가 아니다.

```text
EMR 전체 + FASTQ/BAM/VCF 전체
        ↓
o3가 알아서 전부 파싱
        ↓
진단
```

공개된 설명에 더 가까운 구조는 이쪽이다.

```text
기존 유전체 분석 파이프라인 / 임상 기록 / 연구 DB
        ↓
연구자가 필터링·비식별화·표준화
        ↓
환자별 de-identified case packet
        ↓
o3 Deep Research가 가장 plausible한 molecular explanation 제안
        ↓
전문가 검토 / ACMG·AMP 기준 평가 / 추가 검사 / 임상 확인
```

그러니까 AI가 광산 전체를 판 게 아니다. 사람이 이미 광석을 선별해 바구니에 담아주고, AI는 그 바구니와 최신 문헌을 보며 “이 조합이 설명력이 있다”는 후보를 낸 것이다.

---

## SQL인가, 그래프인가, 그냥 문서인가

원문은 SQL schema나 graph database를 말하지 않는다. “de-identified packet”과 “filtered variant table”이라고 말한다.

따라서 공개 정보만으로 보면 핵심은 특정 DB 기술이 아니라 **LLM이 읽을 수 있게 직렬화된 case-level summary**다.

물론 내부 단계에는 여러 기술이 있었을 수 있다.

- HPO 자체는 ontology라 그래프 성격이 있다.
- variant annotation은 기존 bioinformatics pipeline에서 나온다.
- 병원·연구 데이터는 SQL, 파일, LIMS, VCF, annotation DB 등에 흩어져 있었을 수 있다.
- ClinVar, population frequency, gene-disease relation 같은 외부 DB도 연결된다.

하지만 o3에게 들어간 마지막 형태는 원문상 다음 조합에 가깝다.

```text
표준화된 증상 HPO
+ 임상 메모
+ 환자 메타데이터
+ 필터링된 변이 표
+ 가족 구성원별 signal quality
```

“연결”은 SQL join 한 방이라기보다, 공통 식별자와 필드로 가능해진 의미 연결이다.

예를 들면 이런 식이다.

```text
환자에게 HPO A, B, C가 있다
→ gene X 관련 질환도 HPO A, B, C와 겹친다
→ 환자에게 gene X의 희귀하고 damaging할 수 있는 variant가 있다
→ 부모 데이터상 de novo 또는 recessive pattern이 맞는다
→ ClinVar/논문 근거가 있다
→ 이 조합을 plausible molecular explanation으로 제안한다
```

즉 이번 연구의 기술적 요지는 “SQL vs 그래프”보다는 **HPO + variant table + family evidence + literature reasoning**이다.

---

## 모델에게 뭘 시켰나

연구팀은 모델에게 단순히 “가장 가능성 높은 유전자 하나를 랭킹하라”고 시킨 게 아니다. 원문 표현은 이렇다.

> The team asked the model to propose the most plausible molecular explanation and to show its work.

즉 모델에게 요구한 것은 두 가지다.

1. 가장 그럴듯한 분자적 설명을 제안하라.
2. 왜 그렇게 봤는지 근거를 보여라.

이게 중요하다. 결과물이 단순 gene ranking이면 전문가가 다시 처음부터 검토해야 한다. 하지만 모델이 phenotype, inheritance pattern, variant evidence, scientific literature를 묶어 설명하면, 전문가는 그 설명을 반박하거나 확인할 수 있다.

원문은 이 워크플로우를 **explanation-first reasoning layer on top of existing genomic pipelines**라고 설명한다. 기존 유전체 파이프라인 위에 올라간 “설명 우선 추론 레이어”라는 뜻이다.

---

## 검증 절차는 꽤 엄격했다

모델 출력은 진단이 아니었다. 연구팀은 임상 유전학에서 쓰는 절차를 거쳤다.

- 연구자들이 모델 출력을 검토했다.
- clinical lab이 변이를 분류할 때 쓰는 **ACMG/AMP framework**를 사용했다.
- 각 후보는 최소 2명의 team member가 검토했다.
- 의견 차이는 consensus로 해결했다.
- 모델 출력은 절대 diagnosis로 취급하지 않았다.
- 진단으로 카운트하려면 qualified experts가 근거를 검토해야 했다.
- variant가 pathogenic 또는 likely pathogenic으로 분류되어야 했다.
- **CLIA-certified laboratory**가 확인해야 했다.
- clinical team이 가족에게 결과를 반환해야 했다.

이 체인을 통과한 것만 18건이다.

```text
모델 후보
    ↓
전문가 검토
    ↓
ACMG/AMP 기준 평가
    ↓
추가 검사
    ↓
CLIA 인증 실험실 확인
    ↓
임상팀이 가족에게 결과 반환
```

이 점 때문에 이 연구는 “AI가 진단했다”가 아니라 **AI-assisted research workflow가 전문가의 재분석을 도왔다**고 봐야 한다.

---

## 미해결 사례에 넣기 전, solved case로 워크플로우를 다듬었다

원문에서 흥미로운 부분은 바로 미해결 376건에 투입한 게 아니라, 이미 정답이 있는 사례로 prompt와 workflow를 다듬었다는 점이다.

결과는 다음과 같다.

- established diagnosis가 있는 51건 중, duplicate run에서 **48건**의 correct gene and variant를 회복
- neuromuscular solved case 57건 중, duplicate run에서 **45건**의 correct diagnosis 반환
- long-read genome 15건에서는 모든 case에서 correct gene을 naming했고, **12건**에서 both disease-causing alleles를 찾음

또 모델의 self-reported confidence도 어느 정도 리뷰 우선순위 지정에 도움이 됐다.

- consistently correct call의 mean minimum score: **85.6**
- incorrect or unknown call의 mean minimum score: **42.1**

하지만 원문은 이것도 선을 긋는다. 이 confidence score는 calibrated probability가 아니고, clinical adjudication의 대체물이 아니다. 다만 expert reviewer가 어디부터 볼지 정하는 데 도움을 준 정도다.

---

## 376건에서 무엇이 나왔나

연구팀은 네 그룹의 이전 미해결 사례에 이 workflow를 적용했다.

| Cohort | Cases | Diagnoses surfaced | Yield |
|---|---:|---:|---:|
| Neurodevelopmental | 100 | 10 | 10.0% |
| Neuromuscular disease | 61 | 4 | 6.6% |
| Sudden unexpected death in pediatrics | 200 | 2 | 1.0% |
| Early psychosis | 15 | 2 | 13.3% |
| **Total** | **376** | **18** | **4.8%** |

early psychosis cohort는 15건으로 작아서 percentage의 confidence interval이 넓다. 또 cohort마다 단일 유전자 설명이 나올 가능성이 다르기 때문에 yield 차이를 단순 비교하면 안 된다.

원문이 강조하는 해석은 이것이다.

- 4.8%는 크지 않아 보이지만, 이미 전문가 분석을 거친 heavily reviewed case에서 나온 추가 수익률이다.
- 유사한 재분석 연구에서도 heavily reviewed case에서는 single-digit gain이 흔하다.
- 더 높은 yield는 대개 new case나 이미 잘 알려진 질환에서 genetic confirmation만 기다리는 경우에 나온다.

흥미로운 점은 18건 중 **7건은 rediscovery**였다는 것이다. 즉 local research workflow 밖에서는 이미 진단이 있었지만, 연구팀이 검토한 record에는 없던 경우다. 이건 AI 성능보다도 의료 정보 운영의 문제를 보여준다. 이미 공개 DB나 다른 기록에는 pathogenic/likely pathogenic 정보가 있는데, local review record에는 통합되지 않았던 것이다.

---

## 모델이 유연하게 변이를 찾아낸 사례들

원문에서 가장 인상적인 예시는 early psychosis case의 22q11.2 deletion이다.

입력 데이터에 해당 structural event가 명시적으로 listed되어 있지 않았는데, 모델은 chromosome 22에서 이어지는 low-quality calls와 아이의 cardiac, immune, neurodevelopmental, psychiatric feature를 연결했다. 그리고 DiGeorge syndrome과 관련된 **22q11.2 deletion** 가능성을 제안했다.

이 hypothesized variant는 후속 genome sequencing으로 확인됐다.

이 사례가 중요한 이유는 모델이 표에 적힌 변이 하나만 고른 게 아니라는 점이다. signal quality pattern과 phenotype pattern을 연결해서 “구조변이가 숨어 있을 수 있다”는 가설을 낸 것이다.

또 원문은 prompt가 one monogenic cause를 요구했는데도 모델이 가끔 더 복잡한 설명을 냈다고 말한다.

- 한 case에서는 **LAMA2**와 **FOXP1** 변이가 함께 muscle feature와 neurodevelopmental feature를 설명했다.
- 다른 case에서는 **TTN**과 **SRPK3**가 관련된 previously unrecognized digenic explanation이 나왔다.

즉 모델은 단일 유전자 답안지만 고집한 게 아니라, 입력 패턴상 두 유전자가 더 잘 설명한다고 판단하면 그쪽도 제안했다.

---

## 진단 외에도 testable hypothesis를 만들었다

원문에는 진단으로 확정된 사례 외에, 생물학적으로 테스트 가능한 가설 생성 사례도 나온다.

대표가 **S1PR1-vitiligo** 관계다.

한 neurodevelopmental case에서 모델은 vitiligo가 있는 사람의 **S1PR1 11-amino-acid deletion**을 짚었다. S1PR1은 cell-surface receptor를 encode하고, signaling, immune-cell movement, tissue biology에 관여한다.

모델은 이 deletion이 receptor structure와 signaling을 바꾸고, pigment production을 줄이며, immune cell이 skin에 persist하는 방식과 연결될 수 있다고 제안했다.

원문은 이 관계가 아직 추가 experimental validation이 필요하다고 분명히 말한다. 하지만 scattered findings from structural biology, immunology, clinical genetics를 묶어 concrete, testable hypothesis로 바꾸는 역할을 보여주는 사례로 제시한다.

또 neuromuscular cohort에서는 **HSPB8**, **CDK13** damaging variant가 기존 알려진 disorder와 완벽히 맞지는 않지만, phenotype expansion 가능성을 시사했다고 한다.

---

## Kyra 사례: 거의 20년 만의 진단

원문에는 Kyra라는 환자 사례도 소개된다.

Kyra의 어머니는 딸이 9살 때 karate class에서 자세를 예전만큼 낮추지 못하는 것을 봤다. 축구 연습에서도 느려졌고, 걷거나 뛸 때 발끝으로 서는 경향이 있었다. 소아과 의사는 근력 약화의 원인을 찾지 못했고, 전문의에게 의뢰했다.

그 뒤 거의 20년 동안 검사, 치료, 상담이 이어졌지만 진단은 나오지 않았다.

Kyra의 case는 neuromuscular cohort에서 나온 4건의 진단 중 하나였다. 연구팀은 Kyra의 상태를 **HSPB8 frameshift variant**와 연결했고, **myofibrillar myopathy** 형태로 진단했다. 이 질환은 비정상 단백질 구조가 muscle fiber에 쌓이면서 weakness에 기여하는 질환이다.

Manton Center의 genetic counselor는 Kyra의 28번째 생일 약 일주일 전에 전화를 걸었다.

Kyra는 이미 13살 무렵 ventilator와 wheelchair에 의존하게 되었지만, 이후 상태는 plateau에 들어갔다고 한다. 이 질환 형태가 너무 희귀해 장기 경과에 대해 알려진 것은 적지만, 원문은 이 진단이 Kyra에게 어느 정도 closure를 가져왔다고 설명한다.

---

## 원문 속 두 문장

원문 중간에는 연구자 인용이 두 개 나온다. 둘 다 이 연구의 의미를 잘 보여준다.

![Quote: The bottleneck is time](/images/openai-o3-rare-disease-case-packet-2026-06-21/quote-bottleneck.webp)

> “The bottleneck is time. An expert can devote only so much of their day to any one particular person.”  
> — Dr. Catherine Brownstein, Boston Children’s Hospital’s Manton Center for Orphan Disease Research

![Quote: 8000 different diseases](/images/openai-o3-rare-disease-case-packet-2026-06-21/quote-8000-diseases.webp)

> “Researchers like Catherine and me can’t possibly keep 8,000 different diseases in our heads. That’s the power of AI.”  
> — Alan Beggs, director of the Manton Center for Orphan Disease Research

이 두 문장을 합치면 원문이 말하는 AI의 자리가 선명해진다.

전문가가 사라지는 게 아니다. 전문가의 시간이 병목이고, 희귀질환 지식공간이 너무 넓기 때문에, AI가 후보 설명을 넓게 탐색하고 사람이 검증하는 구조가 필요하다는 얘기다.

---

## 한계도 분명하다

원문은 제한점을 꽤 강하게 쓴다.

이 연구는 다음을 의미하지 않는다.

- 환자가 ChatGPT나 OpenAI 모델로 스스로 질병을 진단해도 된다는 뜻이 아니다.
- 임상의가 OpenAI 제품을 진단용으로 쓰라는 endorsement가 아니다.
- 모델이 어떤 participant도 진단하지 않았다.
- 모든 진단은 physicians와 qualified clinical experts가 established process를 통해 내렸다.

연구 자체의 한계도 있다.

- retrospective study다.
- cohort가 heterogeneous하다.
- reviewer가 model confidence에 blinded되어 있지 않았다.
- time saved, cost, clinician effort, false-positive workload, care 변화는 측정하지 않았다.
- structural variants, repeat expansions, deep-intronic changes, mosaicism 같은 다른 형태의 genetic variation을 체계적으로 평가하지 않았다.
- LLM은 문맥을 잘못 읽거나 그럴듯하지만 틀린 설명을 만들 수 있다.

그래서 모델은 search를 넓히고 human-led analysis를 집중시켰을 뿐, 가족에게 어떤 정보를 반환할지 결정하지 않았다.

Privacy도 언급된다. 이 연구는 de-identified information을 사용했고, protected health information은 approved environment 밖으로 전달되지 않았다고 한다. 더 넓은 clinical deployment에는 privacy, security, auditability, local regulation이 필요하다고 선을 긋는다.

---

## 다음 단계

원문이 제안하는 다음 연구는 prospective, multi-center study다. 비교해야 할 항목은 단순 diagnostic yield만이 아니다.

- standard practice 대비 diagnostic yield
- candidate까지 걸리는 시간
- clinician effort
- false-positive burden
- cost
- care에 미친 영향
- versioned prompts
- reference checks
- audit logs
- calibrated uncertainty

또 이 연구는 o3 Deep Research를 사용했지만, 원문은 더 새로운 general-purpose model이나 purpose-built system도 언급한다. 예를 들어 **GPT‑Rosalind** 같은 life-sciences 특화 시스템은 variant가 protein structure와 function에 미치는 영향까지 더 깊게 볼 수 있지만, 이 연구에서는 테스트하지 않았다.

OpenAI는 이 초기 연구를 지원했고, 다음 단계는 OpenAI Foundation grant를 통해 Manton Center가 platform-agnostic, low-cost genetics AI copilot을 개발하는 방향으로 이어질 예정이다.

---

## 내가 보는 핵심

이 글을 “AI가 희귀질환을 진단했다”로 읽으면 과장이다.

더 정확한 요약은 이렇다.

> 연구자가 환자별로 HPO 증상, 임상 메모, 메타데이터, 필터링된 variant table, 가족별 signal quality를 묶은 de-identified case packet을 만들었다. o3 Deep Research는 그 패킷을 바탕으로 phenotype, inheritance, variant evidence, scientific literature를 연결해 plausible molecular explanation을 제안했다. 그중 일부가 전문가 검증과 임상 확인을 거쳐 진단으로 확정됐다.

즉 사람과 AI의 역할은 이렇게 나뉜다.

```text
사람 / 기존 파이프라인:
- 데이터 비식별화
- HPO 표준화
- variant filtering
- ClinVar / protein effect / family signal annotation
- 전문가 검토와 임상 확정

AI:
- 증상과 변이의 연결 후보 탐색
- 문헌 기반 근거 합성
- inheritance pattern과 phenotype overlap 설명
- 놓친 구조변이나 digenic explanation 가능성 제안
- reviewer가 검토할 수 있는 evidence-linked hypothesis 작성
```

이번 연구에서 진짜 중요한 것은 o3라는 모델명만이 아니다. **AI가 읽을 수 있는 환자별 case packet을 만들고, 모델 출력이 전문가 검증으로 이어지도록 workflow를 설계한 것**이다.

의료 AI의 실전은 “모델 하나가 의사가 된다”가 아니라, 이런 방향일 가능성이 높다.

> 데이터를 표준화하고, AI가 놓친 연결을 넓게 제안하고, 사람 전문가가 검증하고, 임상 절차가 최종 확정한다.

그 구조 안에서라면 AI는 진단을 대체하는 존재가 아니라, 오래된 미해결 사례를 최신 지식과 다시 맞춰보는 **reanalysis copilot**이 될 수 있다.

출처: [OpenAI — Using AI to help physicians diagnose rare genetic diseases affecting children](https://openai.com/index/diagnose-rare-childhood-diseases/)
