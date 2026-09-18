---
title: "RAG 대신 문서를 KV 캐시에 넣는 법 — 다중 문서 조합에서는 Cartridges만 살아남음"
date: 2026-09-17
tags:
  - llm-agent
  - rag
  - long-context
  - kv-cache
  - fine-tuning
  - benchmark
draft: false
description: "문서를 컨텍스트에 넣는 RAG, 파라미터에 넣는 파인튜닝, KV 캐시에 넣는 Cartridges/Compaction을 5개 벤치마크에서 비교한 arXiv 2609.17346 정리. 다중 문서 조합에서는 Cartridges만 ICL과 동급이고 파라미터 주입은 29점 뒤짐."
---

문서를 어디에 넣을지 — 컨텍스트(RAG), 파라미터(파인튜닝), KV 캐시(Cartridges/Compaction) — 를 통제 비교한 실험이 나옴. Amazon AGI의 [논문](https://arxiv.org/abs/2609.17346). 지식 주입 방식을 고르는 사람에게 선택표가 돼서 정리함.

1. 배경. 사전학습에 없는 지식(사내 문서, 진료 기록, 법률 코퍼스)으로 답하려면 문서를 모델에 전달해야 함. 컨텍스트는 매 쿼리마다 prefill 비용이 반복되고, 파라미터는 한 번 학습하지만 망각 위험이 있고, KV 캐시는 압축된 prefix로 만들어 추론 시 로드하는 방식. 기존 연구는 위키피디아처럼 이미 본 문서로 평가해서 "재현"을 쟀는데 이 논문은 진짜 새 지식 주입을 비교함.

2. 단일 문서 오라클 세팅. Compaction(2×)이 73.4로 ICL 상한(73.6)과 사실상 동일. Cartridges 70.6. 파라미터 쪽 최강인 LoRA는 64.5, full fine-tuning은 59.8으로 최하. no context가 24.9인 걸 보면 점수가 실제로 주입된 지식에서 나온다는 것.

3. 압축률을 올리면 그림이 바뀜. Compaction은 급격히 무너짐 — FinQA 66.4(2×) → 19.3(20×). Cartridges는 거의 평평하게 유지됨(LongHealth 81.1 → 77.3). 고압축 저장 영역에서는 Cartridges가 파라미터 방식을 전부 이김.

4. 다중 문서 조합이 갈림길임. 현실 RAG 세팅(청크 검색 → 문서 매핑 → 조합)에서 Cartridges만 k=1→10으로 늘어나도 유지·상승(LongHealth 70.8 → 83.2). Compaction은 전 데이터셋에서 단조 하락(TechQA 65.4 → 26.4). LoRA 병합은 더 빨리 무너짐 — TechQA 57.4 → 23.5(k=3), FinQA 34.5 → 4.9(k=3).

5. 병합 방식을 바꿔도(TIES, DARE, concat) 소용없었음. 문제는 병합 연산자 선택이 아니라 독립 학습된 어댑터를 조합하는 방식 자체. 문서 전체를 한 번에 학습하는 공동 학습이 병합보다 낫지만 그마저도 조합 Cartridges엔 못 미침. "문서별 어댑터를 만들어서 검색해서 합친다"는 설계의 사망 선고에 가까움.

6. 치명적 망각 — 무료 점심은 없음. Compaction은 모든 압축률에서 베이스 유지. Cartridges는 평균 -6%, 특히 HumanEval이 고압축에서 -16점. LoRA는 모든 rank에서 안정. 논문의 해석이 흥미로운데 망각의 원인은 압축도 파라미터 수도 아니고 풀랭크 업데이트라는 것 — 저랭크 제약이 정규화 역할을 해서 파라미터 주입은 저랭크를 유지하라는 권고로 이어짐.

7. 비용. 표현 기반 방식은 10× 토큰 감소가 어텐션 제곱 효과로 약 100× prefill FLOPs 감소로 이어짐. H200 기준 Qwen3-8B에서 20× 카트리지 10개 로드가 30-50ms인데 동등한 120k 원문 prefill은 400-800ms. 쿼리당 비용만 보면 전부 ICL보다 쌈.

8. 여기서 문제제기. 내 문서 자동화 파이프라인은 전부 컨텍스트 주입임. 문서 세트가 고정되고 쿼리가 많은 워크로드(제품 매뉴얼 QA, 사내 규정)라면 매 쿼리 prefill 비용이 누적되는 구조 — KV 캐시식 주입이 비용 곡선을 바꿈. 근데 코딩 능력 저하(HumanEval -16)가 실무에 치명적이면 Compaction 저압축이 안전한 선택임.

9. 선택 가이드로 정리함. 문서 1개 + 낮은 압축만 필요 → Compaction(망각 없음, ICL 동급). 여러 문서 검색+조합(RAG 대체) → Cartridges(코딩 능력 저하 주의). 어댑터 크기 고정 + 추론 최저 비용 → LoRA(다중 문서는 공동 학습 필요). 고압축 저장 → Cartridges. full fine-tuning → 비추천(최고 비용, 최저 정확도, 최대 망각).

10. 이건 메모리 포터빌리티 연구와 이어짐. 모델 산물(파인튜닝 어댑터)은 모델 교체와 다중 문서 조합에서 다 취약하고, 구조화된 표현(KV 캐시)은 둘 다 버팀. "지식을 어디에 두느냐"가 이식성과 조합성을 결정한다는 같은 결론임.

11. 한계. Qwen3-8B 단일 모델, 5개 지식 QA 벤치마크. Cartridges의 다중 문서 우위는 mixed training 후속 연구 덕분이라는 조건도 붙음.

12. 결론. 모든 조건을 다 이기는 지식 주입 방법은 없음 — 세팅별로 골라야 함. 근데 파라미터 주입의 문서별 어댑터 병합은 선택지에서 빼도 된다는 것과, 쿼리가 반복되는 워크로드에서 컨텍스트 주입이 비용 구조상 불리하다는 두 가지는 확정적이라는 결론임.

![Figure 1: 어댑터 크기 대비 단일 문서 점수](/images/2026-09-17-rag-vs-cartridges-knowledge-injection/fig-1-p6.png)

![Figure 2: 검색 문서 수 k에 따른 다중 문서 점수](/images/2026-09-17-rag-vs-cartridges-knowledge-injection/fig-2-p6.png)

![Figure 3: 치명적 망각 측정](/images/2026-09-17-rag-vs-cartridges-knowledge-injection/fig-3-p7.png)
