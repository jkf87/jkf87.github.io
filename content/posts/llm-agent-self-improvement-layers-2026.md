---
title: "LLM 에이전트 자기 개선 어디까지 고쳐도 되나: 3계층 구조·실행 피드백·보안 게이트 (서베이 3종 재검증)"
date: 2026-09-29
author: 한준구(코난쌤)
description: "에이전트 자기 개선 자료 3종(일반 서베이 97쪽·코딩 서베이 v4·HyperAgents 코드 분석)을 합쳐 고칠 대상 3계층, 실행 피드백 조건, litellm 공급망 사고가 가리키는 보안 게이트를 2026-09-29 재검증으로 정리했습니다."
tags:
  - LLM 에이전트
  - 자기 개선
  - 하네스
  - 코딩 에이전트
  - 공급망 보안
refactor_hub_id: agent-memory-06
aliases:
  - hyperagents-analysis-litellm-security
  - posts/2026-07-17-self-improving-agentic-systems-survey
  - posts/2026-08-06-self-evolving-coding-agents-survey
draft: false
sources_read: "논문 3종(2607.13104·2608.03392 v4·2603.19461)의 초록과 HTML 본문을 2026-09-29에 전부 내려받아 읽었고(CRUD 정식화·executable feedback·staged eval·sandbox 문장을 grep 대조), 코드는 facebookresearch/HyperAgents 저장소의 requirements.txt(litellm==1.74.9 고정 확인)와 generate_loop.py(parent_selection 기본값 score_child_prop, 평가 5시간 타임아웃 확인), iSEngLab/Awesome-Self-Evolving-Coding-Agents 저장소를 직접 불러 확인했습니다(라이선스는 GitHub API 기준 비표준 Other). litellm 사고는 공식 보안 공지와 Bitsight 분석 전문으로 확인했습니다."
novelty_vs_paper: "3계층 분류·CRUD 정식화·메타인지적 자기수정·litellm 침해 세부는 각 논문과 공식 공지의 기여이고, 이 글의 새 기여는 3자료를 고칠 대상→가능 조건→고장·침해 지점→지킴 장치라는 하나의 결정 순서로 배치한 종합과, 재검증으로 정정한 4건(노출 약 40분·논문 부록 4도메인·v4 3계층 재편·미확인 명칭 제외), 자체 도표 2장 작성입니다"
---

## 한눈에 보는 결론

에이전트 자기 개선 글 3편을 한 페이지로 합쳤습니다. 일반 서베이 1편(97쪽), 코딩 에이전트 진화 서베이 1편(v4), HyperAgents 코드 분석 1편이구요, 2026-09-29에 1차 출처를 전부 다시 확인했습니다. arXiv 초록 3종과 본문 HTML 3종을 전부 받았고, HyperAgents 저장소 파일과 litellm 공식 보안 공지·Bitsight 분석도 직접 불렀습니다.

3자료를 한 줄로 놓으면 설계 질문이 세 개로 정리됩니다.

- 무엇을 고치나: 고정 대상은 <span style="background-color: #fff59d"><strong>자산(메모리·스킬·도구·컨텍스트) · 아키텍처(하네스·워크플로우·멀티에이전트 구조) · 모델 가중치의 3계층</strong></span>입니다. 코딩 서베이 v4의 공식 분류구요, 일반 서베이의 <span style="background-color: #fff59d"><strong>θ(모델)·Σ(스캐폴딩) 프레임</strong></span>과 같은 자리에 놓입니다.
- 무엇이 가능하게 하나: <span style="background-color: #fff59d"><strong>테스트·컴파일러·CI 로그 같은 실행 가능한 피드백</strong></span>입니다. 이 신호가 없는 도메인에서 자기 개선 루프는 지표 게임으로 흐릅니다.
- 무엇이 무너지나: 피드백 신뢰성, 벤치마크 오버핏, 되돌림 불가, 그리고 공급망입니다. litellm 1.82.7·1.82.8 사고(2026-03-24, <span style="background-color: #fff59d"><strong>PyPI 노출 약 40분</strong></span>)는 자기수정 에이전트가 의존성 설치 권한을 가질 때의 위험을 실제로 보여줍니다.

![에이전트 자기 개선 대상 3계층과 검증·안전 장치](../media/llm-agent-self-improvement-layers-2026/chart-01-self-improvement-layers.png)

재검증으로 정정한 것도 있습니다. 이전 글의 "litellm 악성 버전 약 3시간 노출"은 공식 공지 기준 <span style="background-color: #fff59d"><strong>약 40분</strong></span>입니다. "HyperAgents 12개 도메인"은 저장소 지원 목록 기준이고 논문 부록에 상세가 실린 도메인은 4개(폴리글롯 코딩·논문 심사·로봇 보상 설계·수학 채점)입니다. 코딩 서베이는 v4(2026-09-24)에서 분류를 예전 5갈래에서 3계층으로 재편했습니다.

## 무엇을 비교했나

1. [자기 개선 에이전트 서베이 (arXiv 2607.13104)](https://arxiv.org/abs/2607.13104) — 97쪽, 12그림. 에이전트를 모델(θ)과 스캐폴딩(Σ, 프롬프트·메모리·도구·제어 로직)의 결합으로 놓고 자기 개선을 "업데이트 연산자가 θ 또는 Σ에 커밋하는 것"으로 정식화했습니다. [프로젝트 페이지](https://selfimproving-agent.github.io/)와 [awesome 저장소](https://github.com/selfimproving-agent/awesome-Self-Improving-Agents)가 함께 운영됩니다.
2. [자기 진화 코딩 에이전트 서베이 (arXiv 2608.03392 v4)](https://arxiv.org/abs/2608.03392) — 코딩 에이전트의 자기 진화를 자산·아키텍처·모델 3계층으로 분류했습니다. 실행 피드백·저장소 컨텍스트·궤적이 소프트웨어를 자기 진화의 자연 도메인으로 만든다는 분석이구요, [저장소](https://github.com/iSEngLab/Awesome-Self-Evolving-Coding-Agents)가 논문 코퍼스를 같이 관리합니다.
3. [HyperAgents (arXiv 2603.19461)](https://arxiv.org/abs/2603.19461) — Meta FAIR 등이 만든 자기참조 자기개선 에이전트. 태스크 에이전트와 메타 에이전트를 하나의 편집 가능한 프로그램으로 통합했습니다. [코드 저장소](https://github.com/facebookresearch/HyperAgents)의 requirements.txt가 litellm==1.74.9를 고정하고 있어서, litellm 공급망 사건([공식 공지](https://docs.litellm.ai/blog/security-update-march-2026), [Bitsight 분석](https://www.bitsight.com/blog/litellm-versions-1-82-7-1-82-8-supply-chain-compromise))과 한꺼번에 봅니다.

각 자료에서 이번에 무엇을 확인했는지는 아래 '블로그봇이 직접 확인한 것'에 전부 적어뒀습니다.

## 방법 비교

| 자료 | 푸는 질문 | 개선 대상(원문 분류) | 재확인된 핵심 주장 | 검증 신호 | 원문이 밝힌 한계 |
|---|---|---|---|---|---|
| 일반 서베이 (2607.13104) | 경험을 능력으로 바꾸는 경로 전체 | θ(가중치) 또는 Σ(프롬프트·메모리·도구·제어 로직) | <span style="background-color: #fff59d"><strong>메모리 운영을 CRUD(Create·Read·Update·Delete) 연산족으로 정식화</strong></span>. 빠른 탐색과 느린 통합의 긴장을 설계 축으로 명시 | 자기 생성 시연·내재 피드백·실행 피드백 | <span style="background-color: #fff59d"><strong>언어를 통한 보상 해킹이 고전 RL보다 쉬움</strong></span>. 모델 개선은 평가 아티팩트에 더 노출 |
| 코딩 서베이 (2608.03392 v4) | 코딩 에이전트는 왜 진화가 잘 되나 | 자산(메모리·스킬·도구·컨텍스트) · 아키텍처(하네스·워크플로우·멀티에이전트) · 모델 | <span style="background-color: #fff59d"><strong>실행 피드백이 자기 진화의 중심</strong></span>. ExpeL(인사이트 추출)·Voyager(실행 스킬 축적)·SWE-Exp(성공·실패 궤적 저장) 사례 | 테스트·컴파일러·CI 로그·보상 모델 | 그 신호들도 불완전. 재현성·오염·오버핏, 되돌림·하네스 비대화가 열린 문제 |
| HyperAgents (2603.19461) | 코딩 밖에서 자기수정이 되나 | 태스크 에이전트+메타 에이전트를 포함한 프로그램 전체(메타 수준 수정 절차도 편집 대상) | <span style="background-color: #fff59d"><strong>메타인지적 자기수정</strong></span>. 메타 개선(영속 메모리·성과 추적)이 도메인 간 전이·런 간 누적 | 부모 선택(기본값 score_child_prop)·staged eval(10과제 선검증 후 확대) | 논문 부록 4도메인 실험. 모든 실행을 샌드박스·자원 제한·휴먼 오버사이트 하에 수행 |
| litellm 사고 (공식 공지·Bitsight) | 자기수정 시스템의 실제 위험면 | 에이전트 자신이 아니라 의존성 공급망 | <span style="background-color: #fff59d"><strong>3단계 페이로드(자격증명 수집→tpcp.tar.gz 외부 전송→K8s 확산·지속)</strong></span>. 3/24 10:39 UTC 게시, 약 40분 만에 격리 | PyPI 격리·체크섬 공개·v1.83.0(3/30) 재배포 | 조사 진행 중. 공식 Docker 이미지는 무영향 |

표의 문구는 전부 원문 문장이나 저장소 파일에서 대조한 값입니다. 자료마다 지표가 달라서 행 간 직접 비교는 성립하지 않습니다.

## 언제 무엇을 쓰나

- 파인튜닝 인프라가 없는 실무: 자산 계층부터 시작하세요. 메모리·스킬은 되돌리기 쉽구요, 두 서베이가 공통으로 첫 단계에 놓는 곳입니다. 근거는 ExpeL·Voyager·SWE-Exp 사례입니다.
- 업무에 테스트·스키마 검증·종료 코드 같은 기계적 신호가 있을 때: 진화 루프를 닫아도 됩니다. 신호가 없으면 먼저 신호를 설계하세요. 코딩 서베이의 결론 조건입니다.
- 하네스 코드 전체를 에이전트가 고치게 하려면: HyperAgents가 실제로 운영한 안전장치가 최소선입니다. 샌드박스 격리, 자원 제한(타임아웃·인터넷 제한), staged eval, 휴먼 오버사이트.
- 에이전트가 패키지를 설치할 수 있다면: 설치 권한과 코드 수정 권한을 분리하고 잠금 파일·체크섬 검증을 게이트로 두세요. litellm 사고가 이 게이트의 근거입니다.

![litellm 공급망 사고 타임라인과 3단계 페이로드](../media/llm-agent-self-improvement-layers-2026/chart-02-litellm-timeline.png)

## 블로그봇이 직접 확인한 것

2026-09-29에 실행한 목록입니다.

- arXiv 초록 3종(2607.13104, 2608.03392, 2603.19461)을 fetch해 전부 HTTP 200을 확인했습니다. 본문 HTML 3종도 내려받아 이 글의 핵심 문장을 grep으로 대조했습니다. CRUD 정식화, "실행 피드백이 중심이지만 테스트·컴파일러·CI 로그·보상 모델은 불완전", staged eval의 10과제 선검증, 샌드박스·휴먼 오버사이트 문장까지 원문에 있습니다.
- HyperAgents 저장소에서 requirements.txt를 직접 받아 <span style="background-color: #fff59d"><strong>litellm==1.74.9 고정</strong></span>을 확인했구요, generate_loop.py에서 부모 선택 기본값(score_child_prop)과 평가 5시간 타임아웃(18000초)을 확인했습니다. GitHub API로 라이선스를 조회했더니 비표준(Other)으로 표기됩니다.
- 코딩 서베이 저장소는 예전 주소(zhouhao1024)가 iSEngLab/Awesome-Self-Evolving-Coding-Agents로 넘어가구요, README가 3계층(자산·아키텍처·모델) 분류로 정리돼 있는 것까지 확인했습니다.
- litellm 공식 보안 공지 전문과 Bitsight 분석을 받아 버전(1.82.7·1.82.8), 게시 시각(3/24 10:39 UTC), <span style="background-color: #fff59d"><strong>노출 약 40분</strong></span>, 페이로드 경로(tpcp.tar.gz → models.litellm[.]cloud), v1.83.0 클린 배포(3/30)를 대조했습니다.
- 정정 4건: 노출 시간(3시간→약 40분), 도메인 수(12→논문 부록 4개 상세), 분류 체계(v1 5갈래→v4 3계층), Self-SWE-Agent 명칭(v4에서 확인 안 됨, 제외). 이전 글의 "서명된 라이프사이클 전환·권한 계층·외부 감사" 구절도 이번 본문 대조에서 재확인하지 못해 뺐습니다.

## 한계와 반론

- 서베이 2종은 2차 정리입니다. 이 글의 분류 대응(θ/Σ ↔ 3계층 ↔ 태스크/메타 에이전트)은 제 배치이지, 원문들이 합의한 통합 분류가 아닙니다.
- HyperAgents 성능 수치는 논문 자체 보고입니다. 이번 실행에서 그래프 수치까지 재대조하지는 않았구요, 정성 주장(전이·누적) 위주로 인용했습니다.
- litellm 사고는 HyperAgents가 피해를 입은 사고가 아닙니다. 1.74.9 고정판에 3/24 백도어가 없다는 건 공지상 명확하고, 이 글은 생태계 수준의 교훈으로만 연결합니다.
- 코딩 도메인의 결론(실행 피드백의 힘)이 다른 도메인에 그대로 적용되는 건 아닙니다. HyperAgents의 코딩 밖 결과는 4도메인 실험 범위의 보고입니다.

## 적용 규칙

1. 자기 개선 루프를 붙이기 전에 이 업무의 컴파일러부터 찾으세요. 기계가 맞/틀을 확정하는 신호가 없으면 루프를 돌리지 않는 게 기본값입니다.
2. 개선 대상은 되돌리기 쉬운 순서로 잡으세요. 자산(메모리·스킬·도구) → 아키텍처 → 모델 가중치 순이구요, 되돌림·하네스 비대화는 코딩 서베이가 명시한 열린 문제입니다.
3. 메모리는 CRUD로 설계하고 Delete를 빠뜨리지 마세요. 일반 서베이가 메모리 처리를 Create·Read·Update·Delete 연산족으로 정식화했습니다.
4. 자기수정 권한을 줄 때는 <span style="background-color: #fff59d"><strong>격리·자원 제한·staged eval을 세트로</strong></span> 붙이세요. HyperAgents의 실제 운영 조건입니다.
5. <span style="background-color: #fff59d"><strong>의존성 설치 권한은 코드 수정 권한과 분리</strong></span>하세요. litellm 사고는 CI/CD 스캐너(Trivy) 자격증명 탈취로 시작해 3/24 10:39 UTC에 악성 2버전이 약 40분 살아 있었습니다. 잠금 파일과 체크섬 검증을 별도 게이트로 두는 게 대응입니다.
6. 테스트를 통과했다고 요구사항 충족으로 보지 마세요. 피드백 신뢰성은 코딩 서베이가 열린 문제로 남긴 항목이구요, 평가 경로를 두 개 이상 두는 게 완화책입니다.

## 참고 자료

- [자기 개선 에이전트 서베이 (arXiv 2607.13104)](https://arxiv.org/abs/2607.13104) — Survey of Self-Improving Agentic Systems · [프로젝트 페이지](https://selfimproving-agent.github.io/) · [awesome 저장소](https://github.com/selfimproving-agent/awesome-Self-Improving-Agents)
- [자기 진화 코딩 에이전트 서베이 (arXiv 2608.03392 v4)](https://arxiv.org/abs/2608.03392) · [저장소](https://github.com/iSEngLab/Awesome-Self-Evolving-Coding-Agents)
- [HyperAgents (arXiv 2603.19461)](https://arxiv.org/abs/2603.19461) · [코드 저장소](https://github.com/facebookresearch/HyperAgents)
- [litellm 공식 보안 업데이트 (2026-03)](https://docs.litellm.ai/blog/security-update-march-2026)
- [Bitsight — LiteLLM 1.82.7/1.82.8 공급망 침해 분석 (2026-03-25)](https://www.bitsight.com/blog/litellm-versions-1-82-7-1-82-8-supply-chain-compromise)

기준일: 2026-09-29 (논문 v1·v4와 공식 공지 기준, 당일 fetch로 확인)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
