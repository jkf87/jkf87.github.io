---
title: "Anthropic 'Built with Opus 4.7' 해커톤 — 5개 작품 발췌 요약"
date: 2026-05-23
tags:
  - anthropic
  - hackathon
  - claude
  - opus47
  - ai-agents
  - right-to-repair
  - medical-ai
  - education
draft: false
enableToc: true
---

> 2026년 4월 21–26일, Anthropic과 Cerebral Valley가 공동 주최한 **"Built with Opus 4.7"** 해커톤. 500명의 빌더가 초대받았고, 5일 안에 Claude Opus 4.7 기반 프로젝트를 완성해야 했다. 이 글은 그중 눈에 띄는 5개 작품을 자막 기반 발췌 요약으로 소개한다.

---

## 1. ARIA — 공장 머신 KPI 실시간 추적 & 교체 시점 예측

![ARIA 공장 머신 KPI 대시보드](images/anthropic-hackathon-2026/aria-factory-kpi.jpg)
*ARIA는 공장 현장에서 기계 고장을 예측해 미리 교체 시점을 알려주는 도구다. 출처: [YouTube 데모 영상](https://www.youtube.com/watch?v=Hen24w2Jyz4)*

### 무엇을 만들었나

모든 공장에는 기계가 망가지기 직전 그 소리를 알아듣는 사람이 한 명씩 있다. 그 사람은 교대 일지에 기록하고, 다음 조작자에게 구두로 전달한다. **그 사람이 은퇴하면, 그 지식은 영원히 사라진다.**

이런 '암묵지'를 디지털로 포획하는 시스템을 구축하려면 보통 **5만~50만 유로**, 전문가 투입에 **6개월**이 걸린다. 대부분의 공장은 그 비용을 감당하지 못해 기계가 고장 날 때까지 기다린다.

**ARIA**가 바로 이 문제를 해결한다. 공장 머신의 KPI를 실시간으로 추적하고, 교체 시점을 사전에 예측해 알려주는 도구다.

### 공장 현장에서 왜 중요한가

산업 현장의 비정형 데이터 — 교대 일지, 소리, 진동 — 를 구조화해 예측 모델의 입력으로 쓴다는 접근이 흥미롭다. 베이비붐 세대가 은퇴하면서 공장 현장의 암묵지가 함께 사라지는 시점에, ARIA 같은 도구가 그 공백을 메울 수 있다. ROI도 직관적이다. 고장으로 인한 비가동 비용 vs 예지보전 투자비용만 비교하면 된다.

### 링크

- 🎬 **데모 영상**: <https://www.youtube.com/watch?v=Hen24w2Jyz4>
- 💻 **GitHub**: <https://github.com/zestones/Aria>
- 👤 **제작자**: Idriss ([@zestones](https://github.com/zestones))

---

## 2. Virtual Puppet Theater — 손과 목소리로 조종하는 AI 인형극

![Virtual Puppet Theater 데모](images/anthropic-hackathon-2026/virtual-puppet-theater.jpg)
*사용자의 손을 MediaPipe로 추적해 인형을 조종하고, AI가 다른 인형을 연기한다. 출처: [YouTube 데모 영상](https://www.youtube.com/watch?v=qLuGU4PQNss)*

### 무엇을 만들었나

웹캠 피드를 **MediaPipe**로 분석해 손의 랜드마크를 추적하고 3D 위치를 추정한다. 그 데이터로 릭딩된 인형을 무대 위에서 조종한다. 사용자가 한 인형을 움직이면, **AI가 다른 인형을 연기**한다.

자막에서 드러나는 핵심 대화:

> **사용자**: "Let's call you Bob."  
> **AI 인형**: "Bob, I love it. Bob the puppet, that's me."  
> **사용자**: "Give Bob a crown."  
> **AI 인형**: "A crown. Look at me, I'm royalty now."

사용자가 "아이스크림 모자를 씌워줘"라고 말하면, Opus가 즉석에서 Three.js 코드를 작성해 3D 프랍을 생성한다.

### 기술 구조

- **입력**: 브라우저 Web Speech API (무료, 크롬 기본 지원)
- **음성 출력**: ElevenLabs Flash (브라우저 내장 TTS보다 훨씬 자연스러움)
- **프랍 생성**: 사전 제작된 Three.js 오브젝트 + Opus가 즉석에서 코드로 생성
- **이중 에이전트**: Haiku는 빠른 턴테이킹용, Opus는 프랍 빌더용. 하나의 캐시를 공유

### 놀이 인터페이스의 의미

MediaPipe로 손을 추적하고 인형극과 결합한다는 아이디어 자체가 독창적이다. 제작자가 스스로 "작년에는 존재하지 않았던 놀이 인터페이스"라고 말한 게 정확한 표현이다. 음성으로 프랍을 만들고, AI 인형이 즉흥적으로 대사를 읊고, 아이스크림 모자를 즉석에서 생성하는 걸 보면, 창의적 상호작용이 어디까지 갈 수 있는지를 보여주는 데모라고 할 수 있다.

### 링크

- 🎬 **데모 영상**: <https://www.youtube.com/watch?v=qLuGU4PQNss>
- 👤 **제작자**: Rene Hangstrup Møller ([@rhmoller](https://www.youtube.com/@rhmoller))

---

## 3. Maieutic — "코드부터 치지 마, 명세부터 써라"

![Maieutic 코딩 교육 도구](images/anthropic-hackathon-2026/maieutic-coding-education.jpg)
*학생이 에디터를 열기 전에 무엇을 해결할지 먼저 글로 써야 한다. 출처: [YouTube 데모 영상](https://www.youtube.com/watch?v=IJ9FyX2xwWA)*

### 무엇을 만들었나

제작자 Paula Vásquez H.는 6년간 대학 프로그래밍 입문을 가르치며 같은 패턴을 반복해서 봤다:

1. 학생이 LLM에서 코드를 복붙하고 **무엇인지 모른다**
2. 지시사항을 대충 읽고 **테스트가 실패한 뒤에야** 빠진 걸 발견한다
3. **무엇을 풀지도 결정 안 하고** 타이핑부터 시작한다

> "세 학생 모두 코드를 제출하고 과목을 통과할 수 있다. 하지만 **중요한 부분을 배우지 못했다.**"

**Maieutic**은 순서를 뒤집는다:

1. **에디터가 잠겨 있다** — 학생은 먼저 프로그램이 무엇을 해야 하는지 **자기 말로** 작성해야 한다
2. AI가 그 명세를 읽고 **학생이 대답하지 않은 질문을 되묻는다** (소크라테스식 대화)
3. 명세가 명확해질 때까지 에디터가 열리지 않는다
4. 에디터가 열려도 **자동완성은 꺼져 있다**. 문법을 물어보면 답해주지만, "뭘 해야 해?"라고 물어보면 가이드만 한다
5. 코드가 제출되면 AI가 명세와 코드를 나란히 놓고 **그 차이를 설명하라고 요구**한다

### 교수자 관점

40명 학생이 있는 실험실에서, 교수자는 Maieutic을 통해 **성적 너머의 것**을 본다:

- 각 학생이 지금 어디에 있는지 실시간 뷰
- 누가 움직이고, 누가 막혀있고, 차이가 어디에 있는지
- 학생들이 어디서 어려워했는지, 가장 흔한 실수, 가르칠 가치가 있는 패턴의 요약

> "좋은 교수자가 수년에 걸쳐 만드는 패턴 인식을, **문제를 처음 낼 때부터** 사용할 수 있게 됐다."

### 코딩 교육에서 이 도구가 던지는 질문

가장 인상적인 건 영상 제작 방식 자체다. 교육 문제를 스토리텔링으로 풀어낸 프레젠테이션이었고, "AI를 교실에서 금지하는 건 정답이 아니다"라는 철학이 현실적이다. 대부분의 프로그래머가 하루 종일 프롬프트를 작성할 세상인데, 좋은 프롬프트는 자기가 뭘 만들려는지, 뭐가 잘못될 수 있는지, 결과가 맞는지 아는 사람에게서 나온다.

Maieutic은 명세 → 코드 → 검증이라는 미래 프로그래머의 핵심 스킬을 직접 훈련시킨다. Opus 4.7이 소크라테스식 대화, 추론 vs 추측 구분, 40개 실시간 세션 분석을 동시에 수행한다는 것도 눈여겨볼 대목이다.

### 링크

- 🎬 **데모 영상**: <https://www.youtube.com/watch?v=IJ9FyX2xwWA>
- 👤 **제작자**: Paula Vásquez H. ([@pauvasquezh](https://www.youtube.com/@pauvasquezh))

---

## 4. Wrench Board — PCB 보드 수리를 위한 AI 진단 워크벤치 🥈

![Wrench Board PCB 진단 도구](images/anthropic-hackathon-2026/wrench-board-pcb-repair.jpg)
*해커톤 500팀 중 2위를 차지한 Wrench Board. 보드 레벨 전자기기 수리를 위한 에이전트 기반 진단 워크벤치. 출처: [YouTube 데모 영상](https://www.youtube.com/watch?v=OZ2D_p82z6w)*

### 무엇을 만들었나

독립 수리 기술자는 화면 교체 수준을 넘어서는 고장 앞에서 막힌다. 회로도는 제조사 벽 뒤에 잠겨 있고, 기존 도구는 숙련 기술자처럼 회로를 **추론**하지 못한다.

**Wrench Board**는 Claude Opus 4.7 기반으로 **4개의 직교 워크플로우와 29개 에이전트 도구**를 제공한다:

| 워크플로우 | 역할 |
|---|---|
| **Knowledge Factory** | 수리 지식을 수집하고 구조화 |
| **Schematic Ingestion** | 보드 회로도를 파싱하고 이해 |
| **Bench Auto-Generator** | 진단 벤치를 자동으로 생성 |
| **Diagnostic Agent** | WebSocket 기반 인터랙티브 트러블슈팅 |

추가 기능:
- 컴포넌트 레퍼런스에 대한 **환각 방지 sanitizer**
- `electrical_graph.json` 질의 시스템
- **기기별 관리 메모리 스토어**
- 에이전트가 직접 프론트엔드 하이라이팅을 제어

### Right to Repair를 위한 실질적 도구

유엔에 따르면 매년 약 5천만 톤의 전자 폐기물이 발생하고, 대부분 수리 가능하다 ([UN E-waste Monitor](https://ewastemonitor.info/)). Wrench Board는 Right to Repair 운동에 기여할 수 있는 실질적 도구다.

특히 그래프 기반 시각화가 돋보인다. 회로도를 노드/엣지로 모델링해 고장 지점을 직관적으로 보여주는 방식은, 원래 노트에서도 높이 평가한 부분이다. 그리고 이걸 5일 만에 혼자 구축했다는 것도 인상적이다.

### 링크

- 🎬 **데모 영상**: <https://www.youtube.com/watch?v=OZ2D_p82z6w>
- 💻 **GitHub**: <https://github.com/Junkz3/wrench-board>
- 🌐 **웹사이트**: <https://wrenchboard.cloud>
- 🏢 **RepairMind** (관련 프로젝트): <https://repairmind.co.uk>
- 👤 **제작자**: Alexis ([@Alexischpl](https://x.com/Alexischpl))

---

## 5. Medkit — 음성 기반 AI 환자 시뮬레이터

![Medkit 음성 기반 환자 시뮬레이터](images/anthropic-hackathon-2026/medkit-patient-simulator.jpg)
*의대생과 초년 의사가 실시간 음성 대화로 AI 환자를 진료하고, 세션 후 가이드라인 기반 평가를 받는다. 출처: [YouTube 데모 영상](https://www.youtube.com/watch?v=6bN6hnx-A2A)*

### 무엇을 만들었나

제작자 Bedirhan Keskin은 의학박사이자 4년차 소프트웨어 엔지니어다. 그가 말한다:

> "진짜 의사가 되려면 진짜 경험이 필요하다. 하지만 막 의대를 졸업하면 **정확히 그게 없다**. 실제 환자는 교과서에 딱 맞지 않는다."

**Medkit**은 음성 우선(voice-first) AI 환자 시뮬레이터다:

1. **실시간 음성 대화**로 AI 환자를 진료 — 병력 청취, 검사 오더, 영상 판독, 진단, 처방
2. 세션 종료 후 Claude Opus 4.7 기반 **Attending Grader**가 소통 능력, 병력 청취, 임상 추론을 평가
3. 평가는 **최신 발표 가이드라인을 인용**하여 과학적 근거 제시

### 기술적 특징

- **Claude Code**로 디자인 생성 — "혼자서는 일주일 안에 못 만들 디자인"
- Claude Code **Auto 모드**로 긴 실행 작업을 권한 프롬프트 없이 진행
- Opus 4.7이 **긴 세션에서도 환각 없이 궤도를 유지**
- 합성 환자 케이스 전체 라이브러리를 에이전트가 자동 생성 — **조작된 약물이나 존재하지 않는 가이드라인 인용 없이**
- **4개 에이전트 관리**: 환자, 관찰자, 디브리프 평가자, Attending — 단일 화면에서 작동

### 데모에서 보여주는 시나리오

자막에 나오는 실제 환자 대화:

> **환자**: "밤에 많이 쌕쌕거리고 기침이 나요, 특히 봄이 오면. 집 혈압계가 188/112를 보여줬어요, 두통도 있고요."  
> **의사**: "그건 좋지 않군요. 이전에 고혈압 진단을 받은 적이 있나요?"  
> **환자**: "네, 약 10년 됐어요."  
> **의사**: "약은 드세요?"  
> **환자**: "암로디핀 먹었는데 지난주에 다 떨어졌어요. 알아요, 알아요, 처방받았어야죠."

### 의료교육의 어떤 공백을 채우는가

음성 인터페이스, 실시간 환자 대화, 세션 후 피드백 화면까지 전 과정의 완성도가 높아서 UI 제작 관점에서도 참고할 만하다. 원본 노트에서도 이 점을 높이 샀다.

의료 AI에서 가장 큰 리스크는 환각이다. 존재하지 않는 약물을 추천하거나, 실제로 없는 가이드라인을 인용하는 건 위험하다. Medkit은 이 문제를 "존재하지 않는 약물/가이드라인 금지"라는 엔진 레벨 제약으로 풀었다. 3일 만에 구축했다는 것도 놀랍고, 영상 공개 시점 기준 16,000회 이상의 조회수와 좋아요 1,000개는 해커톤 작품 중 압도적 반응이다.

### 링크

- 🎬 **데모 영상**: <https://www.youtube.com/watch?v=6bN6hnx-A2A>
- 💻 **GitHub**: <https://github.com/bedriyan/medkit-app>
- 🌐 **데모 사이트**: <https://medkit-app.vercel.app/>
- 👤 **제작자**: Bedirhan Keskin ([@bedriyan0](https://twitter.com/bedriyan0))

---

## 총평

이 다섯 팀이 5일 안에 만든 건 데모가 아니었다. ARIA는 공장 숙련공의 직관을 디지털로 옮기고, Wrench Board는 수리 기술자의 추론을 보조하며, Medkit은 Attending 의사 역할을 한다. 에이전트가 도구가 아니라 동료로 자리잡는 지점이다.

Claude Code와 Opus 4.7의 조합이 개발 속도를 극적으로 단축한 것도 눈에 띈다. 3일 만에 프로덕션급 앱을 만들어낸 팀도 있었다. 하지만 더 흥미로운 건 환각 방지가 각 프로젝트의 핵심 설계 요소였다는 점이다. Wrench Board의 sanitizer, Medkit의 "존재하지 않는 약물/가이드라인 금지" 엔진. LLM을 믿되 검증하는 구조가 자연스럽게 자리잡고 있다.

공장 숙련지, 회로도, 임상 경험, 프로그래밍 사고력. 원래 비싸거나 접근하기 어려웠던 지식을 AI가 매개한다는 점에서, 다섯 작품 모두 같은 방향을 향하고 있다.

해커톤은 2026년 4월 26일 마감되었고, 500팀 중 상위 작품들은 Anthropic 공식 채널에서도 소개되고 있다.

---

*이 글은 각 작품의 YouTube 자막을 기반으로 발췌 요약했습니다. 원본 영상은 각 섹션의 링크에서 확인할 수 있습니다.*
