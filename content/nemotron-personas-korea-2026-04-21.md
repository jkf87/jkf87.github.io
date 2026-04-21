---
title: "한국인 700만 명을 데이터로 찍어낸 회사 — NVIDIA Nemotron-Personas-Korea"
date: 2026-04-21
tags:
  - NVIDIA
  - Nemotron
  - Korea
  - LLM
  - Persona
  - Synthetic
  - Agent
description: NVIDIA가 KOSIS·건보공단·법원 통계에 묶인 합성 한국인 페르소나 700만 명을 공개함. 26개 필드, 17개 시·도, 2천 개 직업. LLM 에이전트가 "Hi, I'm your AI"가 아니라 "안녕하세요, 보건소로 가시면 됩니다" 하게 만드는 재료임.
---

한국어 에이전트 만든다고 LLM 기본값에 "너는 한국인이야" 한 줄 넣으면 끝나는 줄 알았음. 근데 물어보면 *"Hi, I'm your AI assistant"* 식 영어 답이 돌아오거나, 독감 예방접종을 CDC 기준으로 설명해줌. NVIDIA가 그 공백을 메우려고 내놓은 게 Nemotron-Personas-Korea임.

1. LLM이 기본으로 내는 페르소나는 평균 시민임. 평균 시민은 미국인임. 그래서 한국 서비스 앞단에 LLM을 그대로 붙이면 어색해짐.

2. 한국 특화를 하려면 **인구통계에 기반한 페르소나** 가 필요함. 나이, 성, 지역, 직업, 학력, 소득, 가족 구성, 취미, 건강 관심사까지. 이걸 통계에 맞게 찍어놔야 LLM이 반말/존댓말을 언제 쓰는지 같은 것까지 흉내를 냄.

![](./images/nemotron-personas-korea-2026-04-21/hero-korea-data.gif)

3. NVIDIA가 2026년 4월에 **Nemotron-Personas-Korea** 를 공개함. 합성 한국인 페르소나 **700만 명** 짜리 데이터셋임. 레코드 100만 건 × 페르소나 7종류.

4. 필드가 **26개**. 이름, 나이, 성별, 시·도, 시·군·구, 거주 유형, 가족 구성, 학력, 직업, 산업, 소득 대역, 정치 성향 비슷한 value orientation, 취미, 좋아하는 브랜드, 건강 관심사, 디지털 사용 성향, 그리고 자유 서술형 `persona` 한 덩어리.

5. 지역 커버가 넓음. 17개 광역 시·도 전부 + 서울 25개 자치구까지 세분화돼 있음. 이름도 **약 20만 9천 개 고유값** 으로 흩어놔서 같은 이름이 몰리지 않게 잡아놨음. 직업은 **2천 개 이상** 버킷.

6. 중요한 포인트는 이 숫자들이 **통계에 묶여 있다** 는 거임. 임의 생성이 아님. 소스로 KOSIS(국가통계포털), 대법원, 국민건강보험공단, 한국농촌경제연구원, NAVER Cloud 데이터가 들어감.

7. 그래서 시·도별 인구 비율, 연령 분포, 직업 분포, 학력 분포가 실제 공공 통계와 맞게 찍힘. 서울 거주자를 수도권 인구 비율대로 뽑고, 60대 여성이면 그 연령대 건강 관심사(고혈압/관절/건강검진) 비율에 맞춰 필드를 맞춰줌.

![](./images/nemotron-personas-korea-2026-04-21/census-grid.gif)

8. 생성 스택은 **NeMo Data Designer**. 그 안에 **Probabilistic Graphical Model** 로 필드 간 조건부 확률을 건 뒤, 자유 서술 `persona` 필드만 **Gemma-4-31B** 로 풀어 써줌. 그래픽 모델이 뼈대, LLM이 살.

9. 라이선스는 **CC BY 4.0**. 상업 사용 가능, 출처 표기만 하면 됨. 그리고 전 과정이 **합성**이라 실제 개인정보가 들어가 있지 않음. PIPA(개인정보보호법) 적합.

10. 체감이 어떻게 바뀌는지는 예시 하나로 갈림. *"독감 예방접종 받으려면 어디 가야 해?"* 한 번 던져봤을 때.

11. 페르소나 없이 LLM 단독: *"You can get a flu shot at your nearest pharmacy or clinic. The CDC recommends…"* 영어 + 미국 기관 레퍼런스 + 존댓말 없음.

12. Nemotron-Personas-Korea 로 시스템 프롬프트 채운 뒤: *"가까운 **보건소** 에 가시면 됩니다. 매년 가을에 **국가예방접종사업** 으로 65세 이상 어르신과 임산부는 무료로 맞으실 수 있어요."* 존댓말, 보건소, 국가예방접종사업. 세 단어가 다 바뀜.

13. 이 차이를 만드는 게 **persona 필드 + 연령·거주지 조합** 임. 프롬프트에 "당신은 55세 여성, 경기도 수원시 거주, 직업은 간호사" 라고 밀어넣으면, 모델이 해당 페르소나가 실제로 쓸 법한 어휘로 말을 맞춰줌.

![](./images/nemotron-personas-korea-2026-04-21/persona-flow.gif)

14. 써먹는 흐름은 네 단계로 끊김. 하나, **load_dataset** 으로 700만 페르소나 로드. 둘, 타겟 주제에 맞게 **필터** (헬스케어 챗봇이면 `health_interests` 필드로 서브셋). 셋, 해당 페르소나를 **system_prompt** 에 꽂음. 넷, NVIDIA API 나 로컬 Nemotron 모델로 배포.

15. 코드 자체는 Hugging Face datasets 한 줄 + 파이썬 필터 + OpenAI 호환 API 호출. *"from datasets import load_dataset; ds = load_dataset('nvidia/Nemotron-Personas-Korea')"* 이 한 줄이 시작점임.

16. 근데 합성 데이터라 **완벽한 통계 일치는 아님**. 모델 편향이 남을 수 있고, 특정 소수 지역·직업은 샘플이 얇음. NVIDIA도 문서에 "통계적 근사(grounding)지 복제가 아니다" 라고 박아놨음.

17. 그래서 실제 서비스에 붙이려면 **목적별 서브셋** 을 직접 뽑아 검증해야 함. 예: 금융 상담 봇이면 소득 대역×연령대 교차 분포를 KOSIS 원본이랑 다시 대조.

18. 짚어야 할 지점 세 개.

19. **하나, 국가별 컬렉션.** Nemotron-Personas 시리즈는 미국, 일본, 인도, 싱가포르, 브라질, 프랑스, 한국으로 확장 중. NVIDIA가 각 나라 공공 통계와 엮어서 찍어내고 있음. 한국은 상대적으로 늦게 들어갔지만 필드 구성(반말/존댓말 플래그, 보건소 같은 공공 인프라)이 한국 특화로 맞물려 있음.

20. **둘, 정치 성향 필드의 실체.** `value_orientation` 같은 필드는 보수/진보 이분법이 아니라 개방성·전통성·물질주의 같은 **가치 축** 으로 들어가 있음. 선거 여론조사 대체용으로 쓰면 안 됨. 서비스 톤 조정용 시그널로 써야 함.

21. **셋, 에이전트에 꽂을 때 톤 폭주 주의.** 페르소나 하나만 풀로 밀어넣으면 모델이 그 역할극에 너무 몰입해서 민감 주제(의료 진단, 법률 판단)에서 오버핏 될 수 있음. 시스템 프롬프트 끝에 "의학적 조언 대체 금지" 같은 가드를 같이 넣어야 안전함.

22. 이 데이터셋이 중요한 이유는 **한국어 에이전트 벤치마크의 출발선이 옮겨졌기** 때문임. 지금까지 한국어 LLM 평가는 번역체, 반말/존댓말 혼용, 지역 맥락 없는 답변을 암묵적으로 허용해왔음.

23. 이제 "서울 강남구 40대 남성 회사원 페르소나 1,000명에 동일 질문을 던졌을 때 어휘 분포가 얼마나 자연스러운가" 같은 정량 지표를 만들 수 있는 재료가 생김. RAG/Agent 평가 툴킷들이 이걸 안 물고 가면 한 세대 뒤처짐.

![](./images/nemotron-personas-korea-2026-04-21/agent-deployment.gif)

24. NVIDIA가 이걸 공개한 타이밍도 의도적임. **Nemotron Developer Days Seoul** 이 2026년 4월 21–22일에 열림. 한국 개발자들한테 "너희 통계 기반 페르소나 줄 테니 이걸로 Korean agent 만들어라" 라는 포지셔닝.

25. 국내 LLM 진영(업스테이지 솔라, 네이버 하이퍼클로바X, 카카오 Kanana) 입장에서도 선택지가 하나 늘어남. 자체 페르소나 생성 파이프라인 돌리지 않고도 26개 필드 짜여진 합성 데이터를 곧바로 파인튜닝/RAG 소스로 먹일 수 있음.

26. 그리고 또 하나. 합성 페르소나는 **개인정보 없이 통계 속성만 보존** 함. 금융·보험·의료처럼 실제 고객 데이터로 LLM 튜닝하기 어려운 규제 산업에서, PIPA 위반 걱정 없이 시작점으로 쓸 수 있음. 이게 실무적으로 제일 큰 지점임.

27. 근데 결국 페르소나는 **재료**지 **제품**이 아님. 이 데이터로 무엇을 뽑아내느냐는 모델 설계자 몫. 700만 명을 그대로 붓는다고 한국어 에이전트가 저절로 똑똑해지지는 않음.

28. 1996년엔 까치네가 한국어 검색을 시작점으로 삼았고, 2026년엔 NVIDIA가 한국인 페르소나 700만 명을 시작점으로 깔아놨음. 재료가 깔린 위에 뭘 세우는지는 다음 라운드 문제임.

---

**출처**

- [How to Ground a Korean AI Agent in Real Demographics with Synthetic Personas — NVIDIA Blog](https://huggingface.co/blog/nvidia/build-korean-agents-with-nemotron-personas)
- [Nemotron-Personas-Korea — Hugging Face Dataset](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
- [Nemotron-Personas Collection](https://huggingface.co/collections/nvidia/nemotron-personas)
- [NeMo Data Designer](https://docs.nvidia.com/nemo/)
- [KOSIS 국가통계포털](https://kosis.kr/)
