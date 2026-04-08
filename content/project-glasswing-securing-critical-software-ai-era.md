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

Anthropic의 **Project Glasswing**은 단순한 신기능 발표가 아닙니다. 원문은 첫 화면부터 한 가지 사실을 정면으로 밀어붙입니다. **프런티어 AI가 취약점 탐지와 익스플로잇 개발에서 상위권 인간 보안 연구자 수준에 거의 도달했다.** 그래서 이 글도 요약이 아니라, 원문에 쓰인 영상·아이콘·로고를 따라가며 **왜 Anthropic이 이 프로젝트를 지금 꺼냈는지** 한국어로 다시 읽는 구성으로 썼습니다.

원문 도입의 분위기를 가장 잘 전달하는 건 정지 이미지가 아니라 hero 영상입니다. "지금 행동하지 않으면 공격자가 먼저 이 능력을 가져간다"는 위기감이 이 한 장면에 압축돼 있습니다.

<video controls preload="metadata" poster="./images/project-glasswing-securing-critical-software-ai-era/hero-video-frame.jpg" style="width:100%;border-radius:16px;">
  <source src="./images/project-glasswing-securing-critical-software-ai-era/hero-video.webm" type="video/webm" />
  브라우저가 hero 영상을 지원하지 않으면 <a href="./images/project-glasswing-securing-critical-software-ai-era/hero-video.webm">여기</a>에서 확인할 수 있습니다.
</video>

*Glasswing 발표의 출발점을 압축한 영상이다. AI의 코딩 능력이 보안 임계점을 넘는 순간, 방어 체계도 보도자료가 아니라 실전 프로젝트로 전환돼야 한다는 선언.*

## 왜 하필 지금인가

원문 서두의 메시지는 짧고 날카롭습니다.

- **Claude Mythos Preview**는 아직 일반 공개되지 않은 범용 프런티어 모델이다.
- 그런데 이미 **모든 주요 운영체제와 브라우저를 포함한 핵심 소프트웨어에서 수천 건의 고위험 취약점**을 찾아냈다.
- 일부는 인간이 방향을 잡아주지 않아도 **취약점 확인에서 익스플로잇 개발까지 자율적으로 연결**했다.
- 그래서 Anthropic은 공개 경쟁보다 먼저 **방어적 사용을 위한 협력망**을 만들었다.

핵심은 이겁니다. Glasswing은 "AI를 보안에 써보자"가 아닙니다. **AI가 이미 공격 효율을 뒤집어놓을 수 있으니, 방어 측이 먼저 배치해야 한다**는 문제 정의입니다. 프로젝트의 본질은 모델이 아니라 운영 체계에 있습니다.

## 바뀐 건 보안이 아니라 시간표다

원문은 이어서 "소프트웨어에는 원래 결함이 있었지만, 그 결함을 찾는 비용 구조가 바뀌었다"고 설명합니다. 아래 아이콘은 장식이 아니라, 지금부터 읽을 내용의 범위—공격 표면이 얼마나 넓은지—를 먼저 잡아주는 시각 앵커입니다.

<div style="display:grid;grid-template-columns:120px 1fr;gap:20px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/cybersecurity-icon.png" alt="사이버 보안 영역을 상징하는 원문 아이콘" style="width:120px;height:auto;" />
  <div>
    <strong>Anthropic이 짚는 네 가지 변화:</strong>
    <ul>
      <li><strong>탐지 비용 하락</strong> — 숙련 연구자의 수작업 일부가 모델 추론 비용으로 대체된다.</li>
      <li><strong>공격 전문성의 하향 평준화</strong> — 상위권 연구자만 할 수 있던 분석이 더 넓게 복제 가능해진다.</li>
      <li><strong>방어 시간의 붕괴</strong> — 취약점 발견에서 악용까지 걸리는 시간이 급격히 줄어든다.</li>
      <li><strong>핵심 인프라 동시 노출</strong> — OS, 브라우저, 커널, 미디어 라이브러리 같은 기반 계층이 한꺼번에 위험해진다.</li>
    </ul>
  </div>
</div>

원문이 병원·학교·금융·물류·에너지까지 언급하는 이유가 여기 있습니다. AI가 바꾸는 건 보안팀의 생산성이 아니라, **사회 기반 소프트웨어의 노출 속도와 악용 속도** 그 자체입니다.

## Mythos Preview가 실제로 보여준 것

원문은 여기서 곧바로 "말이 아니라 증거"로 넘어갑니다. 이 글도 같은 흐름을 따릅니다. 취약점 사례, 성능 비교, 평가 수치를 한 묶음으로 읽겠습니다.

### 오래된 결함을 다시 끌어올린 사례

아래 아이콘은 원문에서 가장 직접적으로 쓰인 시각 자료입니다. 지금부터 읽을 내용이 성능 홍보가 아니라 **실제 취약점 발굴 기록**이라는 걸 미리 알려줍니다.

<div style="display:grid;grid-template-columns:120px 1fr;gap:20px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/vulnerability-icon.png" alt="취약점 발굴 사례를 상징하는 원문 아이콘" style="width:120px;height:auto;" />
  <div>
    <strong>원문이 예시로 든 대표 사례:</strong>
    <ul>
      <li><strong>OpenBSD 27년 된 취약점</strong> — 보안으로 이름난 OS에서도 오래 묻힌 약점을 다시 찾아냈다.</li>
      <li><strong>FFmpeg 16년 된 취약점</strong> — 수백만 번 자동 테스트를 통과한 코드에서 문제를 잡았다.</li>
      <li><strong>Linux kernel 취약점 체인</strong> — 일반 권한에서 시스템 장악까지 이어지는 경로를 스스로 조합했다.</li>
    </ul>
  </div>
</div>

"취약점이 있었다"보다 중요한 건, **인간 리뷰와 자동화 테스트를 수십 년간 통과해 온 결함을 다시 끌어냈다**는 사실입니다. 이 능력이 이론에서 실전으로 넘어왔기 때문에 Glasswing이 만들어진 겁니다.

### 발견에서 익스플로잇까지, 한 흐름으로

원문 중반의 두 번째 영상은 첫 hero 영상보다 더 실무적인 긴장감을 줍니다. 앞 영상이 "문제가 시작됐다"였다면, 이 영상은 **발견→검증→익스플로잇→방어 대응이 하나의 파이프라인으로 압축되는 시대**를 보여줍니다.

<video controls preload="metadata" poster="./images/project-glasswing-securing-critical-software-ai-era/secondary-video-frame.jpg" style="width:100%;border-radius:16px;">
  <source src="./images/project-glasswing-securing-critical-software-ai-era/secondary-video.webm" type="video/webm" />
  브라우저가 secondary 영상을 지원하지 않으면 <a href="./images/project-glasswing-securing-critical-software-ai-era/secondary-video.webm">여기</a>에서 확인할 수 있습니다.
</video>

*단순 코드 리뷰 보조가 아니다. 취약점 확인에서 익스플로잇 개발까지 거의 자율적으로 이어진 사례를 원문은 이 영상으로 강조한다.*

이게 중요한 이유는, 앞으로의 보안 경쟁력이 "스캐너를 잘 돌리느냐"에 있지 않기 때문입니다. 이제는 다른 역량이 필요합니다.

- 코드베이스 전체를 읽고 **공격 경로 우선순위**를 정하는 능력
- 취약점과 환경 조건을 연결해 **재현 가능한 시나리오**를 만드는 능력
- 패치 후보와 회귀 위험을 함께 보는 **수정 판단 능력**
- 공개 전 대량 triage를 조용히 처리하는 **운영 파이프라인**

### 벤치마크 수치도 같은 이야기를 한다

평가 아이콘과 함께 보면 원문의 의도가 더 분명해집니다. Anthropic은 보안 성능을 따로 떼지 않고, 강한 에이전트형 코딩 능력이 왜 강한 보안 능력으로 이어지는지 수치로 보여주려 합니다.

<div style="display:grid;grid-template-columns:120px 1fr;gap:20px;align-items:center;">
  <img src="./images/project-glasswing-securing-critical-software-ai-era/evaluation-icon.png" alt="성능 평가와 벤치마크를 상징하는 원문 아이콘" style="width:120px;height:auto;" />
  <div>
    <strong>원문에 실린 대표 수치:</strong>
    <ul>
      <li><strong>Cybersecurity Vulnerability Reproduction</strong> — Mythos Preview 83.1% vs Opus 4.6 66.6%</li>
      <li><strong>BrowseComp</strong> — Mythos Preview가 더 높은 점수를 기록하면서 토큰 사용량은 4.9배 적음</li>
      <li><strong>SWE-bench, Terminal-Bench 2.0, Humanity's Last Exam</strong> 등에서도 전반적으로 높은 성능</li>
    </ul>
  </div>
</div>

이 수치를 그대로 받아들일지는 별개의 문제입니다. 하지만 Anthropic이 전달하려는 메시지는 명확합니다. **코딩 에이전트가 강해질수록 사이버 역량도 같이 올라간다.** 보안은 이제 모델 출시 후 부가 검토 항목이 아니라, 모델 경쟁 그 자체의 일부입니다.

## 영상·아이콘·수치가 함께 말하는 세 가지

여기까지의 시각 자료를 한 덩어리로 읽으면, 원문의 핵심 해석 세 가지가 선명하게 드러납니다.

**첫째, "보안 특화 모델"이 아니라 "범용 모델의 임계 돌파"다.** Glasswing이 무서운 이유는 별도의 특수 장비가 아니라 범용 프런티어 모델이 이 수준을 보여줬기 때문입니다. 코딩 모델 경쟁, 에이전트 경쟁, 안전장치 경쟁이 사실상 같은 전장이라는 뜻입니다.

**둘째, 병목은 전문가 수가 아니라 워크플로 설계다.** 모델이 더 많이 찾아낼수록 부족해지는 건 취약점 후보가 아니라 **검증→우선순위화→패치→공개 프로세스**입니다. 보안팀은 탐지보다 운영 설계를 먼저 고도화해야 합니다.

**셋째, 오픈소스가 가장 중요한 전장이 된다.** Anthropic이 Linux Foundation, Apache Software Foundation, OpenSSF, Alpha-Omega를 함께 언급하는 이유입니다. 현대 소프트웨어와 AI 에이전트 모두 오픈소스 위에 서 있으므로, **오픈소스 취약점은 곧 전체 공급망 취약점**입니다.

관련 맥락은 [[PyPI 공급망 공격 이후 — 오픈소스 보안의 새로운 전략과 현실적인 방어법]]에서도 이어집니다.

## 로고가 텍스트보다 많은 것을 말해준다

원문의 로고 묶음은 장식이 아닙니다. 어떤 산업 레이어가 Glasswing에 참여하는지, Anthropic이 어디를 "핵심 소프트웨어"로 보는지 가장 압축적으로 보여줍니다.

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

*클라우드·플랫폼·칩·보안 벤더·금융권·오픈소스 거버넌스가 한자리에 모였다. "세계의 공유 공격 표면"이라는 원문 표현이 이 로고 한 줄로 구체화된다.*

레이어별로 정리하면 이렇습니다.

- **클라우드**: AWS, Google, Microsoft
- **플랫폼·하드웨어**: Apple, Broadcom, NVIDIA
- **보안 전문**: Cisco, CrowdStrike, Palo Alto Networks
- **산업 사용자**: JPMorganChase
- **오픈소스 거버넌스**: Linux Foundation
- **모델 제공자**: Anthropic

Glasswing은 Anthropic 혼자 만든 연구 쇼케이스가 아닙니다. **실제 핵심 시스템을 운영하거나 보호하는 조직과 함께 방어 워크플로를 시험하는 구조**입니다.

## 운영 계획, 영상과 사례 뒤에 놓인 이유

원문은 영상·사례·파트너 소개를 전부 보여준 뒤에야 운영 계획을 꺼냅니다. "왜 긴급한가"와 "누가 참여하는가"를 먼저 보여줘야 **어떻게 굴릴 것인가**에 설득력이 붙기 때문입니다.

Anthropic이 약속한 운영 포인트:

- 참여 조직 및 추가 40여 개 기관에 **Claude Mythos Preview 접근권** 제공
- 연구 프리뷰 기간 동안 **최대 1억 달러 규모 사용 크레딧** 지원
- 오픈소스 보안 조직에 **직접 기부 400만 달러** 집행
- **90일 이내** 학습 내용과 수정 결과를 대외 보고
- 보안 기관과 함께 **AI 시대 실무 권고안** 작성

권고안이 다루겠다고 예고한 범위도 넓습니다.

- 취약점 공개 절차 · 소프트웨어 업데이트 프로세스
- 오픈소스 및 공급망 보안 · secure-by-design 개발 수명주기
- 규제 산업용 기준 · triage 자동화 · 패치 자동화

결국 Glasswing의 승부처는 모델 데모가 아니라, 이런 권고가 **실제 산업 표준으로 연결되느냐**에 달려 있습니다.

## 실무자가 지금 준비해야 할 것

### 기업 보안팀

- 탐지 결과보다 **검증 파이프라인 자동화**를 먼저 준비할 것
- AI가 만든 PoC를 **격리 환경**에서 재현할 것
- 패치 우선순위를 CVSS 숫자보다 **실제 악용 가능성** 중심으로 재설계할 것
- 법무·PR·개발팀을 포함한 **비공개 공개 절차**를 점검할 것

### 플랫폼·인프라 팀

- OS, 브라우저, 커널, 미디어 라이브러리 같은 **기반 계층 의존성**을 우선 점검할 것
- AI 코드 감사 결과를 **CI/릴리스 흐름**에 연결할 것
- 서드파티 코드와 내부 코드의 triage 창구를 분리할 것

### 오픈소스 유지보수자

- 보안 보고 채널과 비공개 공개 절차를 문서화할 것
- AI가 제안한 패치를 검증할 테스트 체계를 확보할 것
- provenance, 서명, 공급망 검증 도구를 기본값으로 갖출 것

## 아직 남은 의문

원문은 강력하지만, 확인해야 할 한계도 분명합니다.

1. **재현 데이터 제한** — 어떤 조건에서, 얼마나 자율적으로 성공했는지 공개 범위가 좁다.
2. **벤치마크 ≠ 실전** — 높은 점수가 실제 조직의 운영 성과를 보장하지는 않는다.
3. **방어 우선 접근의 유통기한** — 지금은 통제된 배포지만, 유사 역량은 결국 더 넓게 퍼질 수밖에 없다.
4. **안전장치 경쟁** — 성능 향상만으로는 부족하고, 위험한 출력 차단과 감사 체계가 같이 발전해야 한다.

## 마무리

원문 시각 자료는 장식이 아니었습니다. **hero 영상은 왜 지금 움직여야 하는지**, **secondary 영상은 발견에서 익스플로잇까지 압축되는 시간표를**, **세 개의 아이콘은 위험·취약점·평가의 층위를**, **로고 묶음은 방어 연합의 실제 범위**를 보여줍니다.

그래서 Project Glasswing의 핵심 메시지도 선명해집니다. AI 시대 보안의 승부는 "더 똑똑한 모델" 하나로 끝나지 않습니다.

- 누가 이 능력에 먼저 접근하는가
- 어떤 코드베이스에 우선 적용하는가
- 어떻게 검증하고 패치하는가
- 오픈소스와 산업 전반에 어떻게 환류하는가

이 질문에 답할 수 있어야, 강한 모델이 리스크가 아니라 방어 우위가 됩니다. Glasswing은 바로 그 운영 실험을 선언한 프로젝트입니다.
