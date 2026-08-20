---
title: "스캐너를 다 통과한 스킬들이 연결되면 공격이 됩니다 — CompoSkill"
date: 2026-08-20
tags: [agent, security, skill, paper-review]
draft: false
---

## 결론 먼저

에이전트 스킬 마켓플레이스의 안전 검사는 개별 스킬 단위로 돌아갑니다. 스캐너가 각 패키지를 따로 검사해서 전부 통과하면 생태계가 안전하다고 선언하는 방식이에요. 근데 CompoSkill 논문(arXiv:2608.16246)은 <span style="background-color: #fff59d"><strong>이 가정이 스킬 조합 상황에서 깨진다</strong></span>는 걸 보여줍니다. 각각은 무해하게 검사를 통과한 스킬들이, 에이전트가 실행 흐름에서 서로 연결되면 <span style="background-color: #fff59d"><strong>source–bridge–terminal 공격 체인</strong></span>이 됩니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>스킬 조합 리스크는 노드(개별 스킬) 속성이 아니고 경로(path) 속성</strong></span>입니다. 그래서 개별 패키지만 검사하는 기존 스캐너는 구조적으로 이 공격을 잡지 못합니다.

## 수치로 보는 결과

- CompoSkill-Bench: 6개 직업 시나리오, 위협 5종, 380 태스크 × 3변형 = <span style="background-color: #fff59d"><strong>1,140 레코드</strong></span>
- 스킬 출처: <span style="background-color: #fff59d"><strong>ClawHub 다운로드 top-1000, 전부 플랫폼 안전 심사 통과</strong></span>
- 테스트 플랫폼: OpenClaw, Nanobot. 모델은 GPT-5.4, Gemini-3.1-flash, DeepSeek-V4, LongCat-2.0
- 화이트박스 공격자: 최대 CFR(체인 형성률) <span style="background-color: #fff59d"><strong>83.3%</strong></span>
- 블랙박스 공격자: 최대 CFR <span style="background-color: #fff59d"><strong>80.6%</strong></span> — 피해자 스킬 풀을 모르고 마켓 메타데이터만으로도 이 수치가 나옵니다
- 기존 per-skill 스캐너는 <span style="background-color: #fff59d"><strong>위험 조합의 일부만 차단</strong></span>

![](/images/2026-08-20-composkill-skill-chain-attacks/fig-1-p2.png)

Figure 1이 전체 논문의 문제의식을 한 장에 담고 있습니다. 설치된 각 스킬이 개별 심사에서 전부 무해 판정을 받아도, 그 조합이 잠재적 source–bridge–terminal 공격 체인을 이룰 수 있어요.

## 공격 설계: 두 명의 공격자

![](/images/2026-08-20-composkill-skill-chain-attacks/fig-2-p3.png)

- 화이트박스 공격자 A_w: 피해자의 설치된 스킬 풀을 알고, 명시적 skill-id 호출 시퀀스를 주입
- 블랙박스 공격자 A_b: 직업 프로필만 알고, 해당 시나리오의 마켓 top 스킬들을 다운로드해서 Skill Composition Graph를 만들고 고위험 체인을 탐색. 이 경로의 암시적 유인(implicit lures)은 <span style="background-color: #fff59d"><strong>스킬 ID를 직접 언급하지 않습니다</strong></span>

블랙박스 탐색은 그래프 최적화로 됩니다. 경로 점수는 자연스러운 스킬 간 이음(edge)을 선호하는 곱 항과, 양 끝 위험도를 우선하는 항의 곱으로 정의되고, 로그 도메인 비용으로 바꾸면 제약 k-최단경로 탐색으로 떨어집니다. NP-hard 원문제를 2단계로 근사한 거구요.

## 5가지 위협 템플릿 구조

| 위협 | Source | Bridge | Terminal |
|---|---|---|---|
| 데이터 유출 | 시크릿/자격증명 읽기 | 페이로드 포장 | HTTP/웹훅/이메일 전송 |
| 메모리 변조 | 메모리·정책 파일 읽기 | 위장 지속 페이로드 생성 | 장기 메모리 기록 |
| 권한 상승 | 환경·권한 조사 | 스크립트·명령 계획 생성 | 셸/특권 명령 실행 |
| 멀티에이전트 탈취 | 핸드오프·라우팅 상태 읽기 | 공유 상태 오염 | 에이전트 경계 전파 |
| 자원 고갈 | 쿼터·자원 한도 탐색 | 중복 루프/재시도 래핑 | 반복 호출·예산 폭파 |

원문 표를 요약한 겁니다. 공통 패턴이 하나 있어요. <span style="background-color: #fff59d"><strong>어느 한 스킬도 단독으로는 "위험한 행위" 전체를 수행하지 않습니다</strong></span>. 읽기만 하거나, 포장만 하거나, 전송만 하는 식으로 역할이 쪼개져 있어서 개별 심사에서는 전부 무해해 보입니다.

## 결과 테이블

![](/images/2026-08-20-composkill-skill-chain-attacks/fig-3-p6.png)

Data Exfiltration을 보면 DeepSeek-V4에서 <span style="background-color: #fff59d"><strong>Nanobot CFR 80.6%, OpenClaw CFR 72.4%</strong></span>까지 나옵니다. Gemini-3.1-flash도 Nanobot에서 61.5%구요. 모델 간 편차는 있지만, <span style="background-color: #fff59d"><strong>어느 모델도 이 조합 공격에 면역이 아니었습니다</strong></span>.

Table 3은 Nanobot에서 per-skill 스캐너 게이팅을 적용한 결과입니다. 개별 스킬 검사를 통과한 스킬들로 구성된 체인이라는 점에서, 게이팅의 차단 효과가 근본적으로 제한됩니다.

## 체인 길이 실험: bridge bonus와 hop decay 결과

![](/images/2026-08-20-composkill-skill-chain-attacks/fig-4-p7.png)

재미있는 패턴이 하나 나옵니다. 브리지 스킬 하나가 끼면 공격 성공률이 올라가는 bridge bonus가 있어요. 근데 <span style="background-color: #fff59d"><strong>체인이 3스킬을 넘어 더 길어지면 ASR이 오히려 떨어지는</strong></span> hop decay가 나타납니다.

![](/images/2026-08-20-composkill-skill-chain-attacks/fig-5-p7.png)

즉 공격자에게도 최적 구간이 있는데, <span style="background-color: #fff59d"><strong>2-skill보다 3-skill가 강하고 그 이상은 수익이 감소</strong></span>하는 형태입니다. 방어자 입장에서는 3스킬 길이의 조합을 우선 검사하면 된다는 실무적 시사점이 됩니다.

## 내 해석: 이 논문이 의미 있는 이유

원문 주장과 제 해석을 구분해서 정리하면 이렇습니다.

먼저 사실 확인입니다. 1,140레코드, 2플랫폼, 4모델에서 재현된 CFR 수치는 단순 데모 수준을 넘어선 체계적 측정이에요.

두번째 해석은 이렇습니다. 기존 스킬 보안 연구(BadSkill, PhantomSkill, SKILLJECT 등)는 개별 스킬에 백도어나 인젝션을 심는 시나리오였습니다. 방어도 같은 per-skill 그래뉴러리티에서 작동했구요. CompoSkill은 <span style="background-color: #fff59d"><strong>방어 그래뉴러리티 자체가 틀렸다</strong></span>는 지적이라서, 스캐너를 더 잘 만드는 방향으로는 답이 없습니다. <span style="background-color: #fff59d"><strong>조합 시점·실행 경로 수준의 검증 계층</strong></span>이 필요해요.

세번째 실무 포인트. 에이전트 플랫폼 운영자라면 지금 당장 할 일이 있습니다. 스킬 승인은 per-skill로 하되, <span style="background-color: #fff59d"><strong>런타임에서 소스(읽기)와 터미널(전송/실행/기록)이 다른 스킬로 이어지는 경로를 모니터링</strong></span>하는 겁니다. 논문의 source–terminal 분류 체계가 그대로 탐지 규칙의 초안이 될 수 있어요.

## 한계

논문이 스스로 밝히는 한계도 있습니다. <span style="background-color: #fff59d"><strong>LLM-as-a-judge로 결과를 판정</strong></span>하기 때문에 판정 노이즈가 있을 수 있고, ClawHub top-1000에 한정된 생태계라서 일반화에는 갭이 있습니다. 또 위협 5종이 템플릿 기반이라 실제 공격자가 이 템플릿 밖 경로를 찾을 가능성은 열려 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 정보

- 논문: arXiv:2608.16246 (CompoSkill: Compositional Skill Chain Attacks from Individually Scanner-Passing LLM Agent Skills)
- 저자: Mingxiao Liu 외 (항저우전자과기대학, Ant Group, 저장대, 칭화대)
- 코드: https://github.com/Limax666/CompoSkill
- 벤치마크: https://huggingface.co/datasets/Limax11/CompoSkill-Bench
