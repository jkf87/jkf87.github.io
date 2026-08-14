---
title: "EvoX Genesis: 에이전트를 갈아치우며 25만 줄 C 컴파일러를 완성한 지속형 재귀 월드"
date: 2026-08-15
tags:
  - agent
  - coding-agent
  - harness
  - LLM
  - long-horizon
  - software-engineering
  - MESA
  - Rust
  - evolution
  - loop
---

결론부터. 홍콩이공대(PolyU) 연구팀의 EvoX Genesis는 <span style="background-color: #fff59d"><strong>긴 소프트웨어 개발의 연속성 주체를 에이전트에서 프로젝트로 옮긴</strong></span> 시스템입니다. 에이전트는 유한하게 살다 끝나도, 승인된 프로젝트 상태와 히스토리는 남아서 다음 에이전트를 받아줍니다.

이 구조로 실물 결과를 냈습니다. 구현 없는 저장소에서 시작해 <span style="background-color: #fff59d"><strong>Rust 기반 C 컴파일러 248,989줄</strong></span>을 만들었습니다.

실행 시간 <span style="background-color: #fff59d"><strong>123.4시간</strong></span>, 아카이브된 에피소드 <span style="background-color: #fff59d"><strong>1,019개</strong></span>, 모델 토큰 비용 <span style="background-color: #fff59d"><strong>US$44.38</strong></span>이 전부입니다.

논문: Persistent Recursive Worlds Enable Autonomous Software Evolution (arXiv 2608.10450, v2 2026-08-12). 프로젝트 페이지는 genesis.evox.group 입니다.

## 핵심 구조: 버전과 경로

![지속형 재귀 월드 개념도](/images/2026-08-15-genesis-persistent-recursive-worlds/fig-1-p4.png)

기존 장기 과제 시스템은 연속성을 긴 컨텍스트, 영구 메모리, 상주 매니저, 공유 스크래치패드로 유지해요. Genesis는 연속성의 자리를 프로젝트로 옮깁니다.

에이전트는 항상 두 좌표로 자리 잡습니다. 승인된 버전 v, 저장소 상대 경로 p. 이 쌍 (v, p)이 하나의 로컬 월드고, 에이전트는 전체 프로젝트를 읽을 수 있어도 책임과 수정 범위는 자기 경로에서 시작합니다.

작동 규칙은 세 개입니다.

- 유한 에이전트: 에피소드 목표를 받아 후보 변경을 제안하고 종료
- 재귀 위임: (v, p) ⇝ (v, q)로 자식 에이전트를 더 깊은 경로에 배치. 버전 v는 그대로 둔다
- 승인 게이트: 부모가 테스트·제약·통합 증거로 검수하고 <span style="background-color: #fff59d"><strong>승인된 변경만 버전 히스토리를 진전</strong></span>시킨다

핵심은 이겁니다. 거부된 변경은 히스토리에 남지 않아요. 유용한 실패 기록을 컨텍스트나 제약에 명시적으로 저장하면 그 기록만 별도 경로로 이후 버전에 들어갑니다.

구현은 경로별 CONTEXT.md, Git 커밋과 보호 아카이브, 에이전트별 브랜치·워크트리 격리로 되어 있구요. 스케줄러는 BEAM 프로세스 기반이라고 합니다.

## 실험 1: 빈 저장소에서 C 컴파일러 형성

시작 커밋엔 .gitignore와 genesis.toml뿐이었어요. 모델은 DeepSeek V4 Flash, 추론 강도 xhigh, 컨텍스트 압축 임계값 150,000 토큰.

![C 컴파일러 형성 결과](/images/2026-08-15-genesis-persistent-recursive-worlds/fig-2-p6.png)

형성은 한 번의 대량 생성으로 진행되지 않고 재귀 누적으로 진행됐습니다. 5.14일 동안 최대 28~29개 에이전트가 동시에 돌았고, 입력 토큰 4.13B에 캐시 적중률 97.4%.

| 검증 | 결과 |
|---|---|
| c-testsuite | <span style="background-color: #fff59d"><strong>220/220 (100%)</strong></span> |
| LLVM 평가 36건 | <span style="background-color: #fff59d"><strong>32/36 (88.9%)</strong></span> |
| Csmith 실행 93건 | 93/93 (100%) |
| LZ4 | 8/8 통과 |
| SQLite | 컴파일 + SQL 새니티 통과 |
| Rust 워크스페이스 테스트 | 2,904 통과 |

에피소드 1,015개 중 <span style="background-color: #fff59d"><strong>929개가 최종 저장소 히스토리에 남는 기여</strong></span>였습니다. 위임 깊이는 5까지 관찰됐어요.

컴파일러는 앞단 선택이 타입 검사를, IR이 최적화와 코드생성을 묶는 의존 구조라 한 에피소드로 담기 어렵습니다. 근데 여기선 이전 승인 변경이 다음 에이전트의 시작점이 되는 방식으로 누적이 관찰됐다.

## 실험 2: 모델을 바꿔도 개발은 이어진다

GLM 5.2로 완성한 별도 컴파일러 월드(117.0k 줄)에서 두 갈래로 나눠서 연속성을 테스트했습니다. 한 갈래는 GLM 5.2 연속, 다른 갈래는 DeepSeek V4 Flash로 모델을 교체.

![모델 교체 후 연속 개발 결과](/images/2026-08-15-genesis-persistent-recursive-worlds/fig-3-p7.png)

| 항목 | GLM 5.2 연속 | DeepSeek V4 Flash 연속 |
|---|---|---|
| 에이전트 수 | 98 | 178 |
| 위임 깊이 | 4 | 8 |
| 유지된 LLVM SingleSource | 1,445/1,448 | <span style="background-color: #fff59d"><strong>1,820/1,820</strong></span> |
| 코드 증감 | 순 +10.0k 줄 | 순 +23.2k 줄 |
| 입력 토큰 | 543.6M | 902.8M |
| 토큰 비용 | 약 $168.35 | $7.49 |

c-testsuite는 세 스냅샷 전부 220/220을 유지했습니다. <span style="background-color: #fff59d"><strong>모델 교체 후에도 두 갈래 모두 상속받은 컴파일러를 처음부터 다시 짜지 않고 이어서 개발</strong></span>했다는 게 요점입니다.

근데 갈래마다 에이전트 수, 깊이, 코드 증감이 다르게 갈렸어요. 유지된 LLVM 테스트 세트가 스냅샷마다 달라서 정면 비교는 불가능하고, 기술적 관찰로 읽으면 됩니다.

## 실험 3: MESA 포트란을 러스트로

천체물리 코드 MESA를 읽기 전용 참조로 두고 13개 모듈 디렉터리를 Rust 크레이트로 재구현했습니다. 대상은 물리줄 139,414줄. star, astero, binary 같은 상위 엔진은 제외 구간입니다.

![MESA 모듈의 러스트 재개발 결과](/images/2026-08-15-genesis-persistent-recursive-worlds/fig-4-p8.png)

33.22시간, 272 에이전트, 결과물은 물리줄 89,946줄짜리 Rust 워크스페이스. <span style="background-color: #fff59d"><strong>1,052개 테스트 통과에 실패 0</strong></span>, 토큰 비용 <span style="background-color: #fff59d"><strong>US$10.64</strong></span>였습니다.

6개 수치 워크로드에서 러스트가 전부 더 빨랐고 <span style="background-color: #fff59d"><strong>중앙값 기준 1.55~6.87배</strong></span> 가속이 나왔어요. 체크섬도 함께 봐야 합니다.

| 워크로드 | 가속 | 체크섬 차이 |
|---|---|---|
| 엔드투엔드 번 | 1.55× | 3.1e-9 |
| EOS 룩업 | 1.60× | 비트 일치 |
| 불투명도 룩업 | 1.98× | 1.3e-13 |
| 2차원 보간 | 1.58× | 4.9e-12 |
| ROS2 적분 | 5.30× | 5.1e-15 |
| 뉴턴 솔버 | 6.87× | 비트 일치 |

<span style="background-color: #fff59d"><strong>EOS 룩업과 뉴턴 솔버는 비트 단위로 동일</strong></span>했고 나머지 네 개는 상대 차이 5.1e-15에서 3.1e-9 사이. 각 수치는 워밍업 후 25회 측정의 중앙값이라고 논문에 명시되어 있습니다. 런타임 비교는 보고된 빌드·호스트·벤치마크 하니스 기준이라는 한계도 같이 적혀 있어요.

## 내 해석과 주의점

- 재귀 위임이 모든 런에서 깊이 4~8로 쓰이긴 했는데 <span style="background-color: #fff59d"><strong>재귀가 원인이라는 통제 실험은 아직 없습니다</strong></span>. 논문도 인과 분해를 다음 단계 과제로 밝혀요
- 각 설정이 단일 런이라 성공률 추정은 불가능합니다. 관찰적 증거로 읽으면 됩니다
- 비용 수치는 토큰 요금만 포함이에요. 하드웨어, 저장, 네트워크, 사람 노동은 빠져 있습니다
- 인간이 목표, 도구, 검증 소스, 컨트롤러 한도를 지정하는 bounded autonomy 구간이라 자율 무한 진화와는 다릅니다
- 승인 게이트가 테스트와 제약 신뢰성에 의존하므로 검증기가 약한 도메인에선 통제가 흐려질 수 있습니다 (여기서부터 내 판단)

정리했습니다. 이 논문의 실용 교훈은 소박한 데 있어요. <span style="background-color: #fff59d"><strong>검증 게이트가 붙은 버전 히스토리를 에이전트 수명과 분리해서 보관하는 설계</strong></span>가 핵심입니다. 코딩 에이전트를 실무에 두고 돌리는 분이라면 이 지점부터 벤치마킹하면 됩니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
