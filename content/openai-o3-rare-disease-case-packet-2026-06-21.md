---
title: "OpenAI o3가 희귀질환을 ‘진단’했다? 실제로는 case packet을 다시 읽은 것이다"
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
description: "OpenAI o3 Deep Research가 희귀질환 미진단 사례 376건에서 18건의 추가 진단 단서를 찾았다는 연구를 데이터 구조 관점에서 해석한다. 핵심은 AI 단독 진단이 아니라, 사람이 만든 case packet 위에서 증상·변이·문헌 근거를 재조합한 것이다."
---

OpenAI가 Boston Children’s Hospital, Harvard 연구진과 함께 발표한 희귀질환 연구가 있다. 제목만 보면 꽤 세다. **o3 Deep Research가 기존에 풀리지 않던 소아 희귀 유전질환 사례를 다시 분석해서 18건의 진단으로 이어지는 단서를 찾았다**는 내용이다.

숫자로 보면 이렇다.

- 기존 전문가 분석에서도 해결되지 않은 사례: **376건**
- AI가 후보 설명을 제시한 뒤 전문가 검증과 추가 검사를 거쳐 진단된 사례: **18건**
- 추가 진단률: **4.8%**

4.8%만 보면 작아 보일 수 있다. 그런데 이건 처음 보는 환자들이 아니라, 이미 유전체 검사와 전문가 리뷰를 거쳤는데도 답이 안 나온 케이스들이다. 그런 backlog에서 18가족이 답을 얻었다면 의미가 작지 않다.

하지만 여기서 중요한 질문은 따로 있다.

> o3가 뭘 어떻게 봤길래 기존 사람이 못 찾은 걸 찾았나?

단순히 “AI가 의료 데이터를 통째로 뒤졌다”는 식으로 이해하면 틀린다. 이 연구의 핵심은 **AI 진단기**가 아니라 **사람이 구조화한 case packet 위에서 작동한 근거 연결 엔진**에 가깝다.

---

## 원시 데이터를 통째로 던진 게 아니다

가장 먼저 오해를 걷어내야 한다.

이런 구조가 아니다.

```text
병원 EMR 전체 + 원시 FASTQ/BAM/VCF 전체
        ↓
o3가 알아서 파싱
        ↓
진단
```

실제로는 훨씬 통제된 구조였을 가능성이 높다.

```text
기존 유전체 분석 파이프라인 / 연구 DB / 임상 기록
        ↓
연구자와 시스템이 필터링·표준화
        ↓
환자별 de-identified case packet 생성
        ↓
o3 Deep Research가 증상·변이·문헌 근거를 연결
        ↓
전문가 검토 / 추가 검사 / 임상 확인
```

즉 AI가 광산에서 원석을 직접 캔 게 아니다. 이미 선별된 광석 더미와 지질지도, 최신 논문을 같이 보고 “여기 금맥 가능성 있음”이라고 표시한 쪽에 가깝다.

---

## case packet은 무엇이었나

OpenAI 글에서는 각 사례마다 **de-identified packet**을 만들었다고 설명한다. 이 패킷에는 대략 다음 정보가 들어갔다.

- 환자의 임상 표현형: **Human Phenotype Ontology, HPO** 용어
- 나이, 성별 같은 메타데이터
- 임상의 메모나 기존 의심 진단
- 필터링된 유전 변이 테이블
- 각 변이의 희귀도
- 단백질 영향 예측
- ClinVar 분류
- 가족 구성원, 특히 child + mother + father trio 정보
- sequencing quality 신호

이걸 아주 단순화하면 이런 모양이다.

```text
Case ID: de-identified

Patient metadata:
- sex: female
- age: 7
- sequencing: proband + mother + father

Phenotypes / HPO:
- HP:0001263 Global developmental delay
- HP:0001250 Seizure
- HP:0001627 Abnormal heart morphology

Clinical notes:
- early hypotonia
- recurrent infections
- prior suspected diagnosis: ...

Candidate variants:
| gene  | variant | zygosity | inheritance | frequency | consequence | ClinVar | quality | mother | father |
| FOXP1 | ...     | het      | de novo     | rare      | LoF         | VUS     | high    | absent | absent |
| LAMA2 | ...     | comp het | recessive   | rare      | damaging    | VUS     | high    | carrier| carrier|
```

이게 핵심이다. o3가 무한한 병원 데이터베이스를 헤맨 게 아니라, **환자별로 정리된 요약 리포트와 변이 표를 읽었다**고 보는 게 맞다.

---

## SQL이었나, 그래프였나

아마 많은 사람이 궁금한 지점이 이거다.

> 연결을 뭘로 했나? SQL join인가? 그래프DB인가?

기사와 공개 설명만 보면, SQL이나 그래프DB가 핵심이었다고 보기는 어렵다. 물론 내부 저장소나 분석 파이프라인 어딘가에는 SQL DB, 파일, variant annotation tool, ontology graph가 있었을 수 있다. 하지만 o3에게 들어간 최종 입력은 **LLM이 읽을 수 있는 텍스트 + 표 형태의 case packet**이었을 가능성이 높다.

여기서 “연결”은 DB join이라기보다 **표준 식별자 기반의 의미 연결**이다.

주요 연결 키는 이런 것들이다.

- **HPO ID**: 증상을 표준화하는 코드
- **gene symbol / gene ID**: FOXP1, LAMA2, TTN 같은 유전자 식별자
- **variant notation / genomic coordinate**: 변이 위치와 표기
- **inheritance label**: de novo, recessive, compound heterozygous 등
- **family relation**: proband, mother, father
- **ClinVar classification**: pathogenic, likely pathogenic, VUS 등
- **문헌 근거**: gene-disease, variant-phenotype 관계

즉 연결은 이런 식이다.

```text
이 환자는 HPO A, B, C를 가진다
→ gene X 관련 질환도 HPO A, B, C와 겹친다
→ 환자에게 gene X의 희귀 damaging variant가 있다
→ 부모에게 없으므로 de novo 패턴이다
→ gene X 질환은 dominant/de novo와 맞는다
→ ClinVar나 문헌 근거도 있다
→ 후보 진단으로 제시한다
```

그래프DB가 아니라는 뜻은 아니다. HPO 자체가 ontology이고, gene-disease-phenotype 관계도 사실상 그래프 구조다. 다만 이 연구의 공개 설명에서 핵심은 “Neo4j 같은 그래프DB를 구축해서 탐색했다”가 아니라, **표준화된 임상·유전 데이터와 LLM reasoning을 결합했다**는 쪽이다.

---

## 정식 규격이 있었나

“case packet”이라는 말이 정식 표준명처럼 보일 수 있는데, 공개된 글만 보면 이번 연구에서 쓴 패킷 컨테이너가 어떤 공식 스키마였는지는 명확하지 않다.

의료유전체 분야에는 실제로 **GA4GH Phenopacket Schema**라는 표준이 있다. 환자, 표현형, 질환, 유전 변이, 해석 결과를 JSON/Protobuf 형태로 담는 규격이다. 예를 들면 이런 느낌이다.

```json
{
  "subject": {
    "id": "case-001",
    "sex": "FEMALE"
  },
  "phenotypicFeatures": [
    {
      "type": {
        "id": "HP:0001263",
        "label": "Global developmental delay"
      }
    }
  ],
  "interpretations": []
}
```

하지만 이번 OpenAI/Boston Children’s 연구가 Phenopacket을 그대로 썼다고 확인되지는 않는다. 더 안전한 표현은 이거다.

> 패킷 컨테이너는 연구팀이 만든 LLM용 입력 묶음일 가능성이 높고, 그 안의 구성요소는 HPO, ClinVar, ACMG/AMP, variant annotation 같은 기존 의료유전체 표준을 조합했다.

즉 “완전 임의”도 아니고 “공개 표준 하나를 그대로 넣었다”도 아니다. **표준 필드를 연구 목적에 맞게 직렬화한 case summary**에 가깝다.

---

## o3가 실제로 한 일

그럼 o3는 뭘 했나.

단순 랭킹 모델처럼 “유전자 하나 골라”가 아니었다. 연구팀은 모델에게 **가장 그럴듯한 molecular explanation을 제안하고, 근거를 설명하라**고 시킨 것으로 보인다.

모델의 역할은 대략 이렇다.

1. 환자의 HPO 증상 조합을 읽는다.
2. 후보 변이 테이블을 본다.
3. 변이의 희귀도, 단백질 영향, 유전 패턴을 본다.
4. gene-disease 문헌과 phenotype overlap을 찾는다.
5. 설명 가능한 후보 진단을 만든다.
6. 불확실성과 확인 필요 사항을 적는다.

결과물은 이런 evidence memo에 가까웠을 것이다.

```text
Candidate explanation:
- Gene: FOXP1
- Variant: ...
- Disease association: ...
- Inheritance fit: de novo dominant
- Phenotype match: developmental delay, speech delay, seizures
- Supporting evidence: ClinVar / literature / case reports
- Remaining uncertainty: ...
- Recommended confirmation: clinical lab validation / CNV testing / segregation check
```

여기서 중요한 건 “정답”이 아니라 **검토 가능한 가설**이라는 점이다.

---

## 기존에 못 찾던 결과를 어떻게 찾았나

이 연구를 가장 간단히 요약하면 이렇다.

> 사람이 재료와 구조를 만들고, AI가 조합 가능한 설명을 넓게 탐색했고, 의사가 검증했다.

AI가 새 데이터를 창조한 게 아니다. 이미 있던 환자 데이터와 최신 지식 사이의 **놓친 연결**을 다시 찾은 것이다.

추론 방식도 순수한 연역만은 아니다.

- **연역**: 이 유전자는 이런 질환을 일으킨다 → 이 환자 증상과 맞다 → 변이도 병적일 수 있다
- **귀납/패턴매칭**: 문헌 속 환자들과 phenotype 조합이 비슷하다
- **유추**: 품질 낮은 특정 genomic region과 증상 조합이 구조변이를 암시한다
- **가설 생성**: 단일 유전자보다 두 유전자 조합이 더 설명력이 있다
- **근거 묶기**: 증상, 변이, inheritance, ClinVar, 논문을 하나의 설명으로 정리한다

기사에 나온 22q11.2 deletion 사례가 딱 그렇다. 입력 데이터에 그 deletion이 명시적으로 들어있지 않았지만, 모델은 22번 염색체의 낮은 품질 call 패턴과 심장·면역·신경발달·정신과적 증상 조합을 연결해 DiGeorge syndrome 가능성을 제안했다. 이후 후속 genome sequencing으로 확인됐다.

이건 “AI가 마법처럼 진단했다”기보다, **표에 들어 있는 이상 신호와 phenotype pattern을 사람이 미처 연결하지 못한 방식으로 묶었다**고 보는 게 더 정확하다.

---

## 최종 판정은 AI가 하지 않았다

이 부분은 매우 중요하다.

OpenAI 글도 분명히 선을 긋는다. 모델은 어떤 환자도 진단하지 않았다. 임상 결정을 하지 않았다. 모델 출력은 후보 가설이었고, 진단으로 인정되려면 다음 과정을 거쳐야 했다.

```text
AI 후보 설명
    ↓
전문가 최소 2명 이상 검토
    ↓
ACMG/AMP 기준으로 변이 병원성 평가
    ↓
추가 검사
    ↓
CLIA 인증 임상 실험실 확인
    ↓
임상팀이 가족에게 반환 가능한 진단으로 확정
```

즉 이 연구의 주장은 “ChatGPT로 진단하자”가 아니다.

오히려 더 정확한 주장은 이거다.

> 희귀질환 유전체 재분석은 지식 업데이트 문제다. 환자의 genome은 그대로지만, gene-disease 지식과 variant classification은 계속 바뀐다. AI는 이 움직이는 지식베이스와 오래된 미해결 사례를 주기적으로 다시 맞춰보는 copilot이 될 수 있다.

---

## 내가 보는 핵심

이 연구에서 진짜 중요한 건 o3라는 모델명보다 **입력 구조**다.

모델이 아무리 좋아도 원시 의료기록이 엉켜 있으면 쓸모가 떨어진다. 반대로 데이터를 이렇게 정리하면 LLM이 꽤 강력해진다.

```text
표준화된 증상 HPO
+ 필터링된 후보 변이 테이블
+ 가족 유전 패턴
+ ClinVar / population frequency / protein effect annotation
+ 짧은 clinical note
+ 최신 문헌 검색과 reasoning
```

이 조합이 되면 LLM은 단순 챗봇이 아니라 **case-level evidence synthesizer**가 된다.

그래서 이 연구를 한 줄로 정리하면 이렇게 말할 수 있다.

> o3가 희귀질환을 독자적으로 진단한 것이 아니라, 사람이 만든 구조화된 case packet을 바탕으로 증상·변이·문헌 근거를 재조합해 전문가가 검토할 만한 후보 설명을 찾아냈다.

그리고 이게 오히려 더 현실적이고 강하다. 의료 AI의 실전은 “모델 하나가 의사가 된다”가 아니라, **데이터를 AI가 읽을 수 있게 구조화하고, AI가 놓친 연결을 제안하고, 인간 전문가가 검증하는 워크플로우** 쪽으로 갈 가능성이 높다.

출처: [OpenAI — Using AI to help physicians diagnose rare genetic diseases affecting children](https://openai.com/index/diagnose-rare-childhood-diseases/)
