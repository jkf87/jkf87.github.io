---
title: "OpenAI가 PII 마스킹 모델 풀었음 - Privacy Filter 정리"
description: "OpenAI가 openai/privacy-filter 공개. 1.5B MoE인데 활성 50M, 브라우저에서도 돌아가는 개인정보 탐지 전용 모델. Apache 2.0이고 학생 정보/민감 데이터 다룰 때 바로 쓸 수 있음."
date: 2026-04-23
tags:
  - openai
  - privacy
  - pii
  - opensource
  - ai-education
slug: openai-privacy-filter-pii-detection-2026-04-23
---

1. OpenAI가 `openai/privacy-filter`를 Hugging Face에 공개함. 텍스트에서 개인정보(PII)를 자동 탐지해서 마스킹하는 전용 모델임.

2. 라이선스는 Apache 2.0. 상업 배포 자유. GPT-OSS 계열로 자체 서버에서 그냥 돌릴 수 있음.

3. 파라미터 규모가 좀 특이함. 총 1.5B인데 스파스 MoE(전문가 128개) 구조라서 **활성 파라미터는 50M**밖에 안 됨. 브라우저/노트북에서 돌리는 걸 상정한 크기임.

4. 왜 이런 모델을 따로 풀었냐. 이유는 단순함. PII 필터링은 LLM 본체한테 맡기면 비싸고 느리고 과탐/미탐이 들쭉날쭉함. 이 작업만 전담하는 작은 모델이 훨씬 현실적임.

5. 탐지하는 개인정보 카테고리는 8종임.

| 카테고리 | 예시 |
|---|---|
| private_person | 이름, 이니셜 |
| private_email | 이메일 주소 |
| private_phone | 전화번호 |
| private_address | 주소 |
| private_url | 개인 URL |
| private_date | 개인 관련 날짜 |
| account_number | 계좌/카드번호 |
| secret | 비밀번호, 토큰, 자격증명 |

6. 컨텍스트 윈도우가 128,000 토큰. 긴 문서 청킹 안 하고 한 번에 밀어 넣어도 됨. 이게 실무에선 꽤 큰 차이임.

7. 구조는 트랜스포머 블록 8개, Grouped Query Attention(쿼리 14/ KV 2), MoE 128 전문가. 띠형 어텐션(banded attention, 대역 128)을 써서 긴 시퀀스에서도 한 번의 forward pass로 모든 토큰을 분류함.

8. 출력은 BIOES 태깅(33개 클래스)으로 나오고, 제약된 Viterbi 디코딩으로 스팬 경계를 강제함. 그러니까 `Harry`만 이름으로 잡고 `Potter`는 놓치는 식의 경계 오류가 줄어듦.

9. 사용법이 진짜 간단함. Transformers 파이프라인 기준.

```python
from transformers import pipeline

classifier = pipeline(
    task="token-classification",
    model="openai/privacy-filter",
)
result = classifier("My name is Alice Smith")
```

10. 브라우저에서도 돎. Transformers.js + WebGPU로 클라이언트 쪽에서 PII를 아예 서버로 보내기 전에 필터링할 수 있음. 이게 프라이버시 설계 관점에서 꽤 중요함.

```javascript
import { pipeline } from "@huggingface/transformers";

const classifier = await pipeline(
  "token-classification",
  "openai/privacy-filter",
  { device: "webgpu", dtype: "q4" }
);

const out = await classifier(
  "My name is Harry Potter and my email is harry.potter@hogwarts.edu.",
  { aggregation_strategy: "simple" }
);
```

11. 실제 결과는 이렇게 나옴.

```
[
  { entity_group: 'private_person', score: 0.99999, word: ' Harry Potter' },
  { entity_group: 'private_email',  score: 0.99999, word: ' harry.potter@hogwarts.edu' }
]
```

12. 근데 OpenAI가 모델 카드에서 강하게 못 박은 게 있음. **이건 익명화 솔루션이 아님**. 미탐지/과탐지가 항상 있음. 다층 방어의 한 축으로만 써야 함.

13. 구체적인 실패 패턴이 공개돼 있는데 이것도 꼼꼼함.

- **놓치는 경우**: 흔치 않은 성씨, 지역별 명명 관례, 이니셜·경칭, 도메인 특화 ID, 새로운 자격증명 형식
- **잘못 잡는 경우**: 공공 인물/조직명, 모호한 공용어, 복합 포맷 텍스트, 샘플 자격증명, 엔트로피 높은 문자열

14. 언어/지역 편향도 솔직하게 적어둠. 영어 중심이고, 비라틴 스크립트(한글 포함)는 성능이 떨어짐. 한국어 이름을 이 모델에만 맡기면 안 됨.

15. 그래서 프로덕션에 쓰려면 순서가 정해짐. (1) 도메인 내 데이터로 평가 먼저, (2) 정책 차이 있으면 파인튜닝, (3) 고민감 워크플로우엔 사람 검토 유지, (4) 다른 보안 계층과 같이 배포.

16. 교육 현장에서 어디에 쓸 수 있는지 고민해봤음. 학생 과제 피드백을 AI로 돌릴 때, 생활기록부 초안 정리할 때, 상담 기록을 검색용으로 인덱싱할 때. 지금까지는 이런 걸 클라우드 LLM에 그대로 올리기 찜찜해서 손으로 지우거나 포기했는데, 이 모델 하나만 앞단에 두면 원본을 노출 안 하고 처리할 수 있음.

17. 특히 브라우저에서 WebGPU로 돌아간다는 점이 교사한테 실용적임. 학교 PC 브라우저에서 바로 돌리면 PII가 서버로 빠져나가지 않음. 업무에 자연스럽게 녹일 수 있는 구조임.

18. 파인튜닝은 거의 필수로 봐야 함. 한국 학교 맥락의 이름/학번/학년반 포맷을 기본 모델이 다 잡아주진 않음. 소규모 라벨링 데이터로 토큰 분류 헤드만 더 학습시키면 됨.

19. 정리하면, PII 필터 단독으로는 부족하지만 "앞단 필터 + 본 LLM + 사람 검토" 파이프라인의 앞단으로는 거의 완성품에 가까움. 이 역할을 Apache 2.0 작은 모델로 풀어준 건 꽤 큰 일임.

20. 원본 리소스 모음.

- 모델: https://huggingface.co/openai/privacy-filter
- 데모 스페이스: https://huggingface.co/spaces/openai/privacy-filter
- 저장소: https://github.com/openai/privacy-filter
- 모델 카드(PDF): https://cdn.openai.com/pdf/c66281ed-b638-456a-8ce1-97e9f5264a90/OpenAI-Privacy-Filter-Model-Card.pdf
