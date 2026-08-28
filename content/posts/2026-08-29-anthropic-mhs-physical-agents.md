---
title: "Anthropic MHS 공개: AI 에이전트가 이제 실험실 장비를 직접 잡기 시작했다"
date: 2026-08-29
draft: false
tags:
  - ai-agents
  - anthropic
  - mcp
  - lab-automation
  - robotics
categories:
  - AI
  - Agent
description: "Anthropic과 HHMI Janelia가 공개한 Model Hardware Standard 연구 프리뷰를 정리했다. MCP·CLI·API로 실험실 장비를 연결하는 표준이고, 아직 오픈소스는 아니다."
aliases:
  - /posts/2026-08-29-anthropic-mhs-physical-agents
---

## 결론 먼저

Anthropic이 공개한 Model Hardware Standard, MHS의 핵심은 간단합니다. <span style="background-color: #fff59d"><strong>AI 에이전트가 현미경, 액체 핸들러, 로봇팔, 플레이트 리더 같은 물리 장비를 공통 방식으로 발견하고 제어하게 만드는 표준</strong></span>입니다.

아직 오픈소스는 아닙니다. Anthropic은 이걸 <span style="background-color: #fff59d"><strong>research preview</strong></span>로 먼저 공개했고, 첫 파트너 그룹은 과학 연구소와 고급 제조 현장입니다. 시작점은 Anthropic과 HHMI Janelia Research Campus의 협업이었습니다.

| 항목 | 내용 |
|---|---|
| 공개 형태 | Research preview, 오픈소스 전 단계 |
| 시작 협업 | Anthropic + HHMI Janelia Research Campus |
| 제어 경로 | MCP, command line interface, code API |
| 대상 장비 | 현미경, 액체 핸들러, 로봇팔, 플레이트 리더, 레이저 시스템 등 |
| 초기 사례 | Genentech BCA assay, CMU serial dilution 3배 속도, QuEra 레이저 lock 99.3% 복구 등 |
| 기준일 | Anthropic 공식 글, 2026-08-27 공개 기준 |

원문은 Anthropic 공식 글입니다. 제목은 [Previewing the Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview)입니다. 연구 프리뷰 신청 페이지는 [modelhardwarestandard.com](https://www.modelhardwarestandard.com/)입니다.

![MHS는 여러 실험 장비를 공통 드라이버와 제어 경로로 묶는 표준이다. 출처: Anthropic 공식 글](/images/2026-08-29-anthropic-mhs-physical-agents/official-01.png)

## 실험실 통합 시간을 몇 주에서 몇 분으로 줄이겠다는 제안

Anthropic이 문제로 잡은 건 모델 성능보다 앞에 있는 병목은 장비 통합입니다.

실험실이나 제조 현장에는 장비가 많습니다. 현미경은 자기 프로그램이 있고, 액체 핸들러는 다른 인터페이스를 쓰고, 로봇팔은 또 다른 API를 씁니다. 장비끼리 말을 못 하니 사람이 중간에서 붙입니다. 원문 표현대로면 통합에 <span style="background-color: #fff59d"><strong>weeks, if not months</strong></span>가 걸릴 수 있습니다.

MHS는 여기에 공통 드라이버를 놓습니다. 드라이버가 장비와 운영체제 사이에서 번역기 역할을 하고, `read`, `write` 같은 단순한 primitive로 장비를 다룹니다. 예를 들어 온도를 읽거나, 온도를 설정하거나, 특정 축을 움직이는 식입니다.

중요한 건 발견(discovery)입니다. 장비가 네트워크 안에서 자기 자신을 표준 형식으로 드러내고, 에이전트는 그 정보를 읽고 "내가 무엇을 조작할 수 있는지"를 파악합니다. 여기에는 장비의 측정 항목, 조정 가능한 값, 안전 제한, 특성 메타데이터가 들어갑니다.

![기존 실험실, 자동화 실험실, MHS 기반 실험실의 차이를 보여주는 Anthropic 공식 도식. 출처: Anthropic](/images/2026-08-29-anthropic-mhs-physical-agents/official-03.png)

## 에이전트는 MCP, CLI, 코드 API로 장비를 잡는다

MHS가 에이전트에게 주는 제어 경로는 3개입니다. <span style="background-color: #fff59d"><strong>MCP, CLI, code files/API</strong></span>입니다.

MCP는 에이전트가 장비를 도구처럼 호출하는 경로입니다. CLI는 사람이 터미널에서 다루는 방식과 가깝습니다. 코드 API는 장시간 작업이나 빠른 반복 작업을 스크립트로 묶을 때 중요합니다.

Anthropic은 Claude가 레이저를 조정하는 사례를 들었습니다. Claude가 카메라로 결과를 보고, 레이저 빔이 어떻게 움직였는지 확인하고, 다시 조정합니다. 그리고 배운 절차를 deterministic script로 패키징합니다. 매 단계마다 온라인 추론을 하지 않아도, 한 번의 명령으로 정렬 작업을 돌릴 수 있게 되는 구조입니다.

이 대목이 꽤 중요합니다. 물리 세계의 에이전트는 "말로 계획하는 모델"만으로는 느리고 위험합니다. 반복 가능하고 검증 가능한 부분은 코드로 내려야 합니다. MHS는 그 경계를 표준화하려는 시도에 가깝습니다.

## 초기 사례는 바이오, 현미경, 양자 레이저까지 넓다

Anthropic이 공개한 초기 사례는 생각보다 넓습니다.

Genentech는 BCA protein assay 자동화 proof-of-concept를 구현했습니다. 전체 단백질 농도를 측정하는 절차이고, 액체 핸들러, 로봇팔, 플레이트 리더를 함께 조율해야 합니다.

University of Washington Baker/Pinglay labs의 Zihao Song은 장비 원격 모니터링 대시보드, qPCR 증폭 곡선을 보다가 적절한 순간에 절차를 멈추는 에이전트 감독 qPCR, 로봇팔과 액체 핸들러 사이의 collision-free plate handoff를 만들었습니다.

Carnegie Mellon University는 serial dilution dose-response 실험을 <span style="background-color: #fff59d"><strong>기존보다 약 3배 빠르게</strong></span> 돌렸다고 합니다. 액체 핸들러, 플레이트 리더, 로봇팔, 모니터링 카메라가 3대의 컴퓨터에 흩어져 있고 인터페이스도 달랐는데, 에이전트가 이를 조율했다는 설명입니다.

HHMI Janelia는 현미경 연구에 MHS를 쓰고 있습니다. Virginie Ruetten이 사용한 rig는 예전에는 <span style="background-color: #fff59d"><strong>서로 공유 인터페이스가 없는 7개의 vendor program</strong></span>을 엮어야 했습니다.

QuEra Computing 사례도 눈에 띕니다. 중성 원자 기반 양자컴퓨터 안의 레이저 시스템 일부를 에이전트가 제어했고, 레이저의 lock을 <span style="background-color: #fff59d"><strong>99.3% 확률로 사람 개입 없이 복구</strong></span>하는 controller를 만들었다고 합니다.

![CMU 사례에 나온 자동화 실험 장비 사진. 액체 핸들러와 플레이트 리더 같은 장비가 MHS의 실제 대상이다. 출처: Anthropic](/images/2026-08-29-anthropic-mhs-physical-agents/official-06.png)

## 이건 MCP의 물리 세계 확장판에 가깝다

MCP가 파일, 브라우저, DB, SaaS를 에이전트에게 연결했다면 MHS는 그 생각을 물리 장비로 밀어 넣습니다. 그래서 단순한 lab automation 발표로만 보면 아깝습니다.

핵심은 <span style="background-color: #fff59d"><strong>장비가 자기 사용법과 안전 한계를 자연어 태그와 참조 파일로 설명한다</strong></span>는 점입니다. 예전에는 매뉴얼, 로컬 PC, 연구자의 암묵지에 흩어져 있던 정보가 드라이버 안으로 들어갑니다. 에이전트는 그걸 읽고 "이 장비는 무엇을 측정하고, 무엇을 조정할 수 있고, 어느 선을 넘으면 안 되는지"를 압니다.

이 구조가 잘 되면 연구실 자동화의 병목이 바뀝니다. 예전 병목은 장비를 붙이는 일이었습니다. 다음 병목은 장비를 안전하게 운용할 수 있는 정책, 평가, 관찰, 복구 절차가 됩니다.

![가설, 실행, 하드웨어 제어, 결과 수집, 분석으로 이어지는 자율 실험 루프. 출처: Anthropic](/images/2026-08-29-anthropic-mhs-physical-agents/official-14.png)

## 안전 문제는 아직 남아 있다

Anthropic도 이 부분을 숨기지 않습니다. Claude는 텍스트와 이미지로 물리 세계를 배웁니다. 그래서 공간 추론과 물리 추론에는 한계가 있고, 전문가 감독이 필요합니다.

원문에 나온 Genentech 사례가 좋습니다. 단백질 샘플에서 거품 때문에 생긴 오류를 Claude가 처음부터 물리적 실패로 이해한 것은 아니었습니다. 연구자들이 문제의 성격은 소프트웨어 버그보다 <span style="background-color: #fff59d"><strong>physical failure</strong></span>에 가까웠고, 물리적 교정이 필요하다는 걸 연구자들이 안내해야 했습니다.

또 하나의 제한도 있습니다. MHS는 <span style="background-color: #fff59d"><strong>programmable interface가 있는 장비</strong></span>에서 작동합니다. 프로그래밍 인터페이스가 없는 장비는 제조사가 드라이버를 만들어야 합니다. 그래서 Anthropic은 제조사와 함께 MHS driver를 넣는 방향으로 확장하려고 합니다.

공개된 vendor/support 목록에는 AWS Strands Robots, Automata LINQ, Danaher, Doosan Robotics, MBF Bioscience ScanImage, QIAGEN, Tecan Fluent, Universal Robots가 들어갑니다. 다음 단계 초기 채택자로 Hugging Face LeRobot과 Raspberry Pi도 언급됩니다.

## 더 실습해보고 싶은 분들께

이 글의 주제는 에이전트, MCP, tool use, 자동화 루프와 직접 연결됩니다. 손으로 직접 만들어보면 훨씬 빨리 감이 옵니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트에게 실제 도구를 쥐여주고 루프를 만드는 쪽에 가깝습니다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 관찰, 실행, 검증, 재시도 구조를 어떻게 설계할지 다룹니다.

## 정리하면

MHS는 아직 완성된 공개 표준이 아닙니다. 지금은 Anthropic과 파트너들이 안전 평가와 best practice를 만들기 위해 먼저 돌려보는 research preview입니다.

그래도 방향은 선명합니다. <span style="background-color: #fff59d"><strong>AI 에이전트의 다음 작업장은 브라우저와 코드 저장소를 넘어 실험실과 제조 라인으로 넓어지고 있습니다</strong></span>. 이때 필요한 건 장비가 자신을 설명하고, 에이전트가 안전 한계 안에서 조작하고, 결과를 보고 다시 조정하게 만드는 공통 표준입니다.

저는 MHS 쪽이 "AI 과학자"라는 표현보다 훨씬 현실적인 신호라고 느꼈습니다. 과장된 미래상보다, 드라이버·메타데이터·MCP·CLI·API 같은 지루한 연결부가 먼저 움직이고 있습니다. 실무에서는 보통 이런 지루한 부분이 진짜 변화를 만듭니다.

## FAQ

- **MHS는 지금 오픈소스인가요?**  
  아닙니다. Anthropic은 MHS를 research preview로 먼저 공개했고, 오픈소스 공개에 앞서 파트너들과 안전 평가와 best practice를 만들겠다고 설명했습니다.

- **MHS는 어떤 장비를 제어할 수 있나요?**  
  programmable interface가 있는 장비가 대상입니다. Anthropic 공식 글에는 현미경, 액체 핸들러, 로봇팔, 플레이트 리더, 레이저 시스템 등이 예시로 나옵니다.

- **MHS와 MCP는 어떤 관계인가요?**  
  MHS는 장비 드라이버, discovery, metadata, 안전 제한을 표준화하고, 에이전트가 장비를 제어하는 경로 중 하나로 MCP를 사용합니다. CLI와 code API도 함께 제공합니다.

- **왜 연구실 자동화에서 중요한가요?**  
  장비마다 인터페이스가 달라 통합에 몇 주에서 몇 달이 걸릴 수 있습니다. MHS의 목표는 이 통합 시간을 몇 시간 또는 몇 분 수준으로 줄이는 것입니다.

- **지금 바로 일반 개발자가 쓸 수 있나요?**  
  공식 글 기준으로는 waitlist 기반 research preview입니다. 관심 있는 연구소, 제조사, 개발자는 modelhardwarestandard.com에서 신청할 수 있습니다.
