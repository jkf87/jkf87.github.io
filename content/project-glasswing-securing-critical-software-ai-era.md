---
title: "Anthropic Project Glasswing, AI 시대 핵심 소프트웨어 보안 전략 정리"
date: 2026-04-08
tags:
  - anthropic
  - security
  - cybersecurity
  - ai
  - opensource
  - quartz
description: "Anthropic의 Project Glasswing 발표를 바탕으로, 원문 시각 자료 흐름을 따라 Mythos Preview의 보안 역량과 핵심 인프라 방어 전략을 한국어로 재해설했다."
---

> 원문: [Project Glasswing: Securing critical software for the AI era](https://www.anthropic.com/glasswing)

Anthropic의 **Project Glasswing**은 단순한 신기능 발표가 아닙니다. 원문은 첫 화면부터, 이제 프런티어 AI가 **취약점 탐지와 익스플로잇 개발에서 상위권 인간 보안 연구자 수준에 거의 도달했다**는 긴장감을 시각적으로 밀어붙입니다. 그래서 이번 글도 요약 위주가 아니라, **원문에 쓰인 영상과 아이콘, 로고를 따라가며 왜 Anthropic이 이 프로젝트를 급하게 꺼냈는지**를 한국어로 다시 읽는 방식으로 구성했습니다.

먼저 원문 도입의 분위기를 가장 잘 전달하는 자산은 정지 이미지가 아니라 hero 영상입니다. 발표문이 말하는 “지금 행동하지 않으면 공격자가 먼저 이 능력을 가져간다”는 위기감이 이 첫 시각 자료와 가장 잘 맞물립니다.

<video controls preload="metadata" poster="./images/project-glasswing-securing-critical-software-ai-era/hero-video-frame.jpg" style="width:100%;border-radius:16px;">
  <source src="./images/project-glasswing-securing-critical-software-ai-era/hero-video.webm" type="video/webm" />
  브라우저가 hero 영상을 지원하지 않으면 <a href="./images/project-glasswing-securing-critical-software-ai-era/hero-video.webm">여기</a>에서 확인할 수 있습니다.
</video>

*이 hero 영상은 Glasswing 발표의 출발점을 압축한다. Anthropic은 AI의 코딩 능력이 보안 임계점을 넘는 순간, 방어 체계도 발표문이 아니라 실제 운용 프로젝트로 전환돼야 한다고 주장한다.*

## 원문 도입부가 먼저 보여주는 것, 왜 지금 Glasswing인가

원문 서두의 메시지는 명확합니다.

- **Claude Mythos Preview**는 아직 일반 공개되지 않은 범용 프런티어 모델이다.
- 그런데 이미 **모든 주요 운영체제와 주요 브라우저를 포함한 핵심 소프트웨어에서 수천 건의 고위험 취약점**을 찾아냈다고 한다.
- 일부는 인간이 방향을 잡아주지 않아도 **취약점 확인과 익스플로잇 개발까지 자율적으로 연결**했다.
- 그래서 Anthropic은 공개 경쟁보다 먼저 **방어적 사용을 위한 협력망**을 묶었다.

이 지점이 중요합니다. Glasswing은 “AI를 보안에 써보자”가 아니라, **AI가 이미 공격 효율을 너무 크게 바꿔버릴 수 있으니 방어 측이 먼저 배치해야 한다**는 문제 정의입니다. 즉 프로젝트의 본질은 모델보다 운영 체계입니다.

## 사이버 보안 시대가 아니라, AI가 보안 시간표를 바꾼 시대

원문 본문은 이어서 “소프트웨어에는 원래 결함이 있었지만, 이제 그 결함을 찾는 비용 구조가 바뀌었다”는 사실을 설명합니다. 여기서는 텍스트만 읽기보다, 원문이 배치한 보안 아이콘과 함께 보는 편이 더 직관적입니다. 이 아이콘은 추상적인 장식이 아니라, 공격 표면이 얼마나 넓은지와 보안 논의의 중심이 어디인지 시선을 고정하는 역할을 합니다.

<div style="display:grid;grid-template-columns:120px 1fr;gap:20px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/cybersecurity-icon.png" alt="사이버 보안 영역을 상징하는 원문 아이콘" style="width:120px;height:auto;" />
  <div>
    <strong>Anthropic이 보는 변화는 네 가지입니다.</strong>
    <ul>
      <li><strong>취약점 탐지 비용 하락</strong>: 숙련 연구자의 수작업 일부가 모델 추론 비용으로 대체된다.</li>
      <li><strong>공격 전문성의 하향 평준화</strong>: 상위권 연구자만 수행하던 분석 흐름이 더 넓게 복제될 수 있다.</li>
      <li><strong>방어 시간의 붕괴</strong>: 취약점 발견에서 악용까지 걸리는 시간이 크게 줄어든다.</li>
      <li><strong>핵심 인프라 집중 리스크</strong>: 운영체제, 브라우저, 커널, 미디어 라이브러리 같은 기반 계층이 동시에 위험해진다.</li>
    </ul>
  </div>
</div>

원문이 병원, 학교, 금융 시스템, 물류, 에너지 인프라까지 언급하는 이유도 여기 있습니다. AI가 바꾸는 것은 단지 보안팀의 생산성이 아니라, **사회적으로 중요한 소프트웨어의 노출 속도와 악용 속도**입니다.

## Mythos Preview가 실제로 무엇을 보여줬는가

원문은 여기서 바로 “말뿐이 아니다”라는 증거로 넘어갑니다. 그 흐름에 맞춰 이번 글도 취약점 사례, 성능 비교, 그리고 평가 메시지를 같은 묶음으로 읽도록 재배치했습니다.

### 1) 오래된 취약점을 다시 끌어올린 사례

아래 취약점 아이콘은 원문에서 가장 직접적으로 쓰인 시각 자료 중 하나입니다. 그래서 이 구간에 배치하는 것이 자연스럽습니다. 독자가 지금부터 읽을 내용이 단순 성능 홍보가 아니라, **실제 취약점 발굴 사례**라는 점을 먼저 알려주기 때문입니다.

<div style="display:grid;grid-template-columns:120px 1fr;gap:20px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/vulnerability-icon.png" alt="취약점 발굴 사례를 상징하는 원문 아이콘" style="width:120px;height:auto;" />
  <div>
    <strong>원문이 예시로 든 대표 사례</strong>
    <ul>
      <li><strong>OpenBSD 27년 된 취약점</strong>: 보안으로 명성이 높은 운영체제에서도 오래된 약점을 다시 찾아냈다.</li>
      <li><strong>FFmpeg 16년 된 취약점</strong>: 수백만 번 자동 테스트가 지나간 코드에서도 문제를 잡아냈다.</li>
      <li><strong>Linux kernel 취약점 체인</strong>: 일반 권한에서 시스템 장악까지 이어지는 경로를 스스로 조합했다.</li>
    </ul>
  </div>
</div>

여기서 핵심은 “취약점이 있었다”보다, **오랫동안 인간 검토와 자동화 테스트를 통과한 결함을 다시 끌어냈다**는 점입니다. Anthropic이 Glasswing을 만든 이유는 바로 이 능력이 이제 이론이 아니라 실전형 역량으로 보이기 시작했기 때문입니다.

### 2) 자율적인 익스플로잇 단계, 그래서 영상이 한 번 더 필요하다

원문 중반의 두 번째 영상 자산은, 첫 hero 영상보다 더 실무적인 긴장감을 담는 데 어울립니다. 앞의 영상이 “문제가 시작됐다”를 보여줬다면, 이 두 번째 영상은 **발견, 검증, 익스플로잇, 방어 대응이 한 흐름으로 이어지는 시대**를 떠올리게 합니다.

<video controls preload="metadata" poster="./images/project-glasswing-securing-critical-software-ai-era/secondary-video-frame.jpg" style="width:100%;border-radius:16px;">
  <source src="./images/project-glasswing-securing-critical-software-ai-era/secondary-video.webm" type="video/webm" />
  브라우저가 secondary 영상을 지원하지 않으면 <a href="./images/project-glasswing-securing-critical-software-ai-era/secondary-video.webm">여기</a>에서 확인할 수 있습니다.
</video>

*이 secondary 영상은 Mythos Preview의 의미를 더 구체적으로 읽게 해준다. 원문은 단순 코드 리뷰 보조가 아니라, 취약점 확인과 관련 익스플로잇 개발까지 거의 자율적으로 이어진 사례를 강조한다.*

이 설명이 중요한 이유는, 앞으로의 보안 경쟁력이 더 이상 “스캐너를 잘 돌리느냐”에만 있지 않기 때문입니다. 이제는 아래 역량이 더 중요해집니다.

- 코드베이스 전체를 읽고 **공격 경로 우선순위**를 정하는 능력
- 취약점과 환경 조건을 연결해 **재현 가능한 시나리오**를 만드는 능력
- 패치 후보와 회귀 위험을 함께 보는 **수정 판단 능력**
- 공개 전 대량 triage를 조용히 처리하는 **운영 파이프라인**

### 3) 평가 수치도 결국 같은 이야기를 한다

이제 평가 아이콘을 붙이면 원문 의도가 더 잘 살아납니다. Anthropic은 보안 성능을 따로 떼어놓지 않고, 강한 에이전트형 코딩 능력이 왜 강한 보안 능력으로 이어지는지 보여주려 합니다.

<div style="display:grid;grid-template-columns:120px 1fr;gap:20px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/evaluation-icon.png" alt="성능 평가와 벤치마크를 상징하는 원문 아이콘" style="width:120px;height:auto;" />
  <div>
    <strong>원문에 실린 대표 수치</strong>
    <ul>
      <li><strong>Cybersecurity Vulnerability Reproduction</strong>: Mythos Preview 83.1%, Opus 4.6 66.6%</li>
      <li><strong>BrowseComp</strong>: Mythos Preview가 더 높은 점수를 기록하면서도 토큰 사용량은 4.9배 적음</li>
      <li><strong>SWE-bench, Terminal-Bench 2.0, Humanity’s Last Exam</strong> 등에서도 전반적으로 높은 성능 제시</li>
    </ul>
  </div>
</div>

이 수치들을 그대로 받아들일지 여부와 별개로, Anthropic이 전달하려는 메시지는 분명합니다. **코딩 에이전트가 강해질수록 사이버 역량도 함께 올라간다**는 것입니다. 따라서 보안은 더 이상 모델 출시 후 부가 검토 항목이 아니라, 모델 경쟁 그 자체의 일부가 됩니다.

## 원문 시각 자료가 묶어 보여주는 세 가지 해석

여기까지의 영상, 아이콘, 성능 수치를 한 덩어리로 읽으면 원문이 말하는 핵심 해석도 정리됩니다.

### 1) 이것은 “보안 특화 모델”보다 “범용 모델의 임계 돌파” 이야기다

Glasswing이 무서운 이유는, 별도의 특수 장비가 아니라 **범용 프런티어 모델이 보안에서 위험한 수준의 역량을 보였기 때문**입니다. 이 말은 곧 코딩 모델 경쟁, 에이전트 경쟁, 안전장치 경쟁이 같은 문제라는 뜻입니다.

### 2) 기업의 병목은 전문가 수보다 워크플로 설계가 된다

모델이 더 많이 찾아낼수록 부족해지는 것은 취약점 후보가 아니라, **검증, 우선순위화, 패치, 공개 프로세스**입니다. 그래서 보안팀은 이제 탐지보다 운영 설계를 먼저 고도화해야 합니다.

### 3) 오픈소스 보안이 가장 중요한 전장이 된다

Anthropic이 Linux Foundation, Apache Software Foundation, OpenSSF, Alpha-Omega를 함께 언급하는 이유도 이것입니다. 현대 소프트웨어와 AI 에이전트 모두 오픈소스 위에 서 있기 때문에, **오픈소스 취약점은 곧 전체 공급망 취약점**이 됩니다.

관련해서 공급망 방어 관점은 [[PyPI 공급망 공격 이후 — 오픈소스 보안의 새로운 전략과 현실적인 방어법]]도 함께 보면 맥락이 잘 이어집니다.

## 협업 구조는 텍스트보다 로고가 더 많은 것을 말해준다

원문에서 로고 묶음은 장식이 아닙니다. 어느 산업 레이어가 Glasswing에 참여하는지, 그리고 Anthropic이 어디를 “핵심 소프트웨어”로 보고 있는지 가장 압축적으로 보여줍니다. 그래서 이 글에서도 로고 구간은 그대로 유지하고, 바로 앞뒤 설명만 한국어 맥락에 맞게 다시 배치했습니다.

<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-aws.svg" alt="AWS 로고, Glasswing 협력 클라우드 사업자" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-apple.svg" alt="Apple 로고, Glasswing 협력 플랫폼 사업자" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-broadcom.svg" alt="Broadcom 로고, Glasswing 협력 하드웨어 기업" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-cisco.svg" alt="Cisco 로고, Glasswing 협력 보안 기업" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-crowdstrike.svg" alt="CrowdStrike 로고, Glasswing 협력 보안 기업" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-google.svg" alt="Google 로고, Glasswing 협력 클라우드 사업자" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-jpmorganchase.svg" alt="JPMorganChase 로고, Glasswing 협력 금융 기업" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-linux-foundation.svg" alt="Linux Foundation 로고, Glasswing 협력 오픈소스 거버넌스 조직" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-microsoft.svg" alt="Microsoft 로고, Glasswing 협력 클라우드 사업자" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-nvidia.svg" alt="NVIDIA 로고, Glasswing 협력 하드웨어 기업" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-palo-alto-networks.svg" alt="Palo Alto Networks 로고, Glasswing 협력 보안 기업" />
  <img src="./images/project-glasswing-securing-critical-software-ai-era/logo-anthropic.svg" alt="Anthropic 로고, Project Glasswing 주도 조직" />
</div>

*이 로고 묶음은 Glasswing의 범위를 설명하는 핵심 근거다. 클라우드, 플랫폼, 칩, 보안 벤더, 금융권, 오픈소스 거버넌스가 동시에 들어간다는 점이 곧 “세계의 공유 공격 표면”이라는 원문 표현을 구체화한다.*

이 구성은 다음처럼 읽는 것이 가장 자연스럽습니다.

- **클라우드 사업자**: AWS, Google, Microsoft
- **플랫폼·하드웨어**: Apple, Broadcom, NVIDIA
- **보안 전문 기업**: Cisco, CrowdStrike, Palo Alto Networks
- **대형 산업 사용자**: JPMorganChase
- **오픈소스 거버넌스**: Linux Foundation
- **모델 제공자**: Anthropic

즉 Glasswing은 Anthropic 혼자 만든 연구 쇼케이스가 아니라, **실제 핵심 시스템을 운영하거나 보호하는 조직과 함께 방어 워크플로를 시험하는 구조**입니다.

## 운영 계획도 시각 자료 흐름 뒤에 놓일 때 더 잘 이해된다

원문은 영상과 사례, 파트너 소개 뒤에야 운영 계획을 설명합니다. 이 순서가 합리적인 이유는, 먼저 “왜 긴급한가”와 “누가 참여하는가”를 보여준 다음에야 **어떻게 굴릴 것인가**가 설득력을 얻기 때문입니다.

Anthropic이 약속한 운영 포인트는 다음과 같습니다.

- 참여 조직과 추가 40여 개 기관에 **Claude Mythos Preview 접근권** 제공
- 연구 프리뷰 기간 동안 **최대 1억 달러 규모 사용 크레딧** 지원
- 오픈소스 보안 조직에 **직접 기부 400만 달러** 집행
- **90일 이내** 배운 내용과 공개 가능한 수정 결과를 대외 보고
- 보안 기관과 함께 **AI 시대 실무 권고안** 작성

원문이 예고한 권고안 범위도 꽤 넓습니다.

- 취약점 공개 절차
- 소프트웨어 업데이트 프로세스
- 오픈소스 및 공급망 보안
- secure-by-design 개발 수명주기
- 규제 산업용 기준
- triage 자동화
- 패치 자동화

결국 Glasswing의 승부처는 모델 데모가 아니라, 이런 운영 권고가 실제 산업 표준으로 연결되느냐에 있습니다.

## 그래서 실무자는 무엇을 준비해야 하나

### 기업 보안팀

- 탐지 결과보다 **검증 파이프라인 자동화**를 먼저 준비할 것
- AI가 만든 PoC를 **격리된 환경**에서 재현할 것
- 패치 우선순위를 CVSS 숫자보다 **실제 악용 가능성** 중심으로 재설계할 것
- 법무, PR, 개발팀을 포함한 **비공개 공개 절차**를 점검할 것

### 플랫폼·인프라 팀

- 운영체제, 브라우저, 커널, 미디어 라이브러리 같은 **기반 계층 의존성**을 우선 점검할 것
- AI 코드 감사 결과를 **CI 및 릴리스 흐름**과 연결할 것
- 서드파티 코드와 내부 코드의 triage 창구를 분리할 것

### 오픈소스 유지보수자

- 보안 보고 채널과 비공개 공개 절차를 문서화할 것
- AI가 제안한 패치를 검증할 테스트 체계를 확보할 것
- provenance, 서명, 공급망 검증 도구를 기본값으로 가져갈 것

## 남는 의문도 분명하다

원문은 강력하지만, 아직 확인해야 할 한계도 있습니다.

1. **세부 재현 데이터의 제한**
   - 어떤 조건에서 얼마나 자율적으로 성공했는지 공개 범위가 제한적입니다.
2. **벤치마크와 실전 사이 간극**
   - 높은 점수가 곧 실제 조직의 운영 성과를 보장하지는 않습니다.
3. **방어 우선 접근의 지속 가능성**
   - 지금은 통제된 배포지만, 유사 역량은 결국 더 넓게 확산될 가능성이 큽니다.
4. **안전장치 경쟁의 중요성**
   - 성능 향상만으로는 부족하고, 위험한 출력 차단과 감사 체계가 같이 발전해야 합니다.

## 마무리

이번 재구성에서 중요한 것은, 원문 시각 자료가 단순 장식이 아니라는 점을 살리는 것이었습니다. **hero 영상은 왜 지금 움직여야 하는지**, **secondary 영상은 발견에서 익스플로잇까지 이어지는 압축된 시간표를**, **세 개의 PNG 아이콘은 위험, 취약점, 평가의 세 층위를**, **로고 묶음은 실제 방어 연합의 범위**를 보여줍니다.

그래서 Project Glasswing의 핵심 메시지도 더 선명해집니다. AI 시대 보안의 승부는 “더 똑똑한 모델” 하나로 끝나지 않습니다.

- 누가 이 능력에 먼저 접근하는가
- 어떤 코드베이스에 우선 적용하는가
- 어떻게 검증하고 패치하는가
- 오픈소스와 산업 전반에 어떻게 환류하는가

이 질문에 답할 수 있어야만, 강한 모델이 리스크가 아니라 방어 우위가 됩니다. Glasswing은 바로 그 운영 실험을, 원문 시각 자료 전체를 동원해 선언한 프로젝트라고 보는 편이 가장 정확합니다.
