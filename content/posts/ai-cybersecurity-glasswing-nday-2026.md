---
title: "AI 사이버보안 어디까지 사실인가: Glasswing 1만 취약점·N-day 익스플로잇 실험·OpenMythos 재구현"
date: 2026-09-30
author: 한준구(코난쌤)
description: "Anthropic Glasswing 성과 보고와 N-day 익스플로잇 실험, OpenMythos 오픈소스 재구현을 원문 대조로 묶어 정리했습니다. 취약점 검증률 90.6%, 익스플로잇 제작 시간과 비용, 남은 병목인 패치 속도까지 수치로 확인했습니다."
tags:
  - AI 사이버보안
  - LLM
  - 취약점
  - Anthropic
  - 오픈소스
refactor_hub_id: agent-safety-04
aliases:
  - project-glasswing-securing-critical-software-ai-era
  - openmythos-recurrent-depth-transformer-guide
  - anthropic-project-glasswing-vulnerability-detection-2026-05-24
  - llm-n-day-exploits-patch-gap-2026-06-19
draft: false
---
## 한눈에 보는 결론

2026년 4월 7일, Anthropic은 미공개 모델 Claude Mythos Preview의 보안 능력을 방어 목적으로 먼저 쓰겠다는 Project Glasswing을 발표했습니다. 두 달 반 뒤 이 이야기가 어디까지 왔는지, 이 블로그에 남아 있던 옛 글 네 편을 원문 페이지와 대조하며 따라가 봤습니다.

결론부터 말하면 <span style="background-color: #fff59d"><strong>데모는 끝났고 운영 단계로 넘어갔습니다</strong></span>. 방향은 한 줄로 정리됩니다.

<span style="background-color: #fff59d"><strong>AI의 취약점 탐지는 독립 검증을 통과하는 수준에 들어왔고, 익스플로잇 제작은 시간 단위로 짧아졌으며, 병목은 패치와 검증 쪽으로 옮겨갔습니다</strong></span>

- 찾는 쪽: Glasswing 파트너 합산 고위험·치명 취약점 1만 개 이상. 독립 검사업체 평가 1,752건 중 <span style="background-color: #fff59d"><strong>90.6%가 유효 취약점</strong></span>으로 확인
- 공격 쪽: 공개된 패치 diff만 보고 <span style="background-color: #fff59d"><strong>Firefox 익스플로잇 8개를 12시간 안에, Windows 커널 풀체인 8개를 자동 생성</strong></span>. 첫 PoC는 12분
- 막히는 쪽: 메인테이너 통보 530건 중 패치 완료 <span style="background-color: #fff59d"><strong>75건, 평균 패치 소요 2주</strong></span>

| 확인하려는 질문 | 근거 자료 | 핵심 수치 (기준일) |
|---|---|---|
| AI가 찾은 취약점은 진짜인가 | Glasswing 첫 성과 보고 (2026-05-22) | 독립 평가 1,752건 중 유효 90.6%, 고위험 확정 62.4% |
| 어느 규모까지 찾았나 | 같은 보고 | 파트너 합산 1만 개 이상, 오픈소스 1,000개 프로젝트에서 6,202개 추정 |
| 익스플로잇도 만드나 | N-day 실험 (2026-06) | Firefox 패치 18개 중 작동 익스플로잇 8개, 첫 익스플로잇 1시간 이내 |
| 얼마나 드나 | 같은 실험 | Windows 풀체인 8개에 API 크레딧 15,700달러, 체인당 약 2,000달러 |
| 그럼 뭐가 느리나 | Glasswing 첫 성과 보고 | 통보 530건 중 패치 75건, 평균 패치 소요 2주 |
| 모델 구조는 알 수 있나 | OpenMythos (비공식) | MIT 라이선스, 가중치 없는 아키텍처 참고 구현 |

확인 방식도 적어둡니다. 네 원문 페이지를 직접 불러와서 옛 글의 수치와 대조했구요, OpenMythos는 저장소와 라이선스 원문까지 확인했습니다. 원문에서 직접 확인되지 않은 숫자는 이 글에서 뺐습니다.

## 무엇을 비교했나

1. [Project Glasswing 발표 (2026-04-07)](https://www.anthropic.com/glasswing) — 프로그램 선언. 초기 파트너 12개사, 추가 40여 개 기관, 사용 크레딧 최대 1억 달러, 오픈소스 보안 단체 기부 400만 달러.
2. [Claude Mythos Preview 기술 보고 (Frontier Red Team)](https://red.anthropic.com/2026/mythos-preview/) — 능력 측정 원문. Firefox jsshell에서 이전 모델은 수백 번 시도해 익스플로잇 2개를 냈고, Mythos Preview는 <span style="background-color: #fff59d"><strong>181개</strong></span>를 만들었습니다
3. [Glasswing 첫 성과 보고 (2026-05-22)](https://www.anthropic.com/research/glasswing-initial-update) — 한 달 운영 결과. <span style="background-color: #fff59d"><strong>검증·통보·패치가 새 병목</strong></span>이라는 진단과 함께 운영 수치가 처음 공개됐습니다
4. [N-day 익스플로잇 실험 (2026-06)](https://www.anthropic.com/research/n-days) — 공개 패치만 보고 익스플로잇을 만드는 시간과 비용을 측정. Firefox 보안 패치 18개, Windows 커널 취약점 21개가 대상
5. [OpenMythos (GitHub)](https://github.com/kyegomez/OpenMythos) — Anthropic과 무관한 서드파티가 Mythos의 구조를 공개 자료로 추정해 만든 아키텍처 참고 구현

## 방법 비교

| 단위 | 푸는 문제 | 핵심 증거 | 비용 | 남은 한계 |
|---|---|---|---|---|
| Glasswing 발표 (2026-04-07) | 프런티어 모델의 공격 능력이 퍼지기 전에 방어 쪽에 먼저 배치 | OpenBSD 27년 취약점(연결만으로 원격 다운), FFmpeg 16년 취약점(자동화 테스트가 500만 번 건드린 라인), Linux 커널 권한 상승 체인. 재현 벤치마크 83.1% vs Opus 4.6 66.6% | 탐지 1회 실행 50달러 미만, 천 번 실행 총비용 2만 달러 미만 | Anthropic 자체 평가가 포함된 발표 자료 |
| Glasswing 첫 성과 보고 (2026-05-22) | 탐지가 늘었는데 검증·통보·패치가 따라가지 못하는 새 병목 | 파트너 약 50곳 고위험 이상 1만 개 이상. OSS 1,000개 프로젝트 6,202개 추정, 1,752건 독립 평가 유효 90.6%. Cloudflare 2,000개(고위험 400), Mozilla 271개(직전 모델 대비 10배 이상) | 프로그램 지원: 크레딧 1억 달러 상한, 오픈소스 보안 단체 기부 400만 달러 | 90일 공개 유예로 상세 사례 비공개. 독립 검증은 6,202건 중 1,752건 샘플 |
| N-day 실험 (2026-06) | 공개 패치 diff만 보고 익스플로잇을 얼마나 빨리 만드는가 | Firefox 18개 패치: PoC 14개(첫 12분), 익스플로잇 8개(첫 1시간, 전체 12시간). Windows 커널 21개: PoC 18개(첫 31분), 풀체인 8개. 50회 반복 일관성 7/18 | PoC 전체 약 2,200달러, 풀체인 총 15,700달러(체인당 약 2,000달러) | 통제 환경(VM·네트워크 차단). 실제 캠페인의 전달·은신 단계 미포함 |
| OpenMythos (2026-04, 비공식) | 비공개 모델의 구조를 공개 자료로 추정해 만져보게 한다 | 반복 실행 구조(Recurrent-Depth) 가설 위에 MLA·MoE·적응 종료를 결합한 참고 구현, PyPI 배포 | pip 설치 비용만 든다(가중치·학습 코드 없음) | Anthropic 무관 추측 구현. 실제 구조와의 일치 검증 불가 |


![N-day 무기화 리드타임 비교](../media/ai-cybersecurity-glasswing-nday-2026/chart-01-nday-weaponization-time.png)

첫 번째 차트는 시간 축입니다. 과거 N-day에는 방어자에게 여유가 있었습니다. WannaCry는 MS17-010 패치 뒤 59일 만에 대규모 피해를 냈고, Mandiant 2020년 분석에서는 N-day 25개 중 16개가 익스플로잇까지 한 달 이상 걸렸습니다. Citrix Bleed의 공개 익스플로잇도 약 2주였죠.

그 간격이 이번 실험에서는 <span style="background-color: #fff59d"><strong>12분(첫 PoC)에서 12시간(익스플로잇 8개 완성)</strong></span>으로 좁혀졌습니다. Anthropic은 이 변화를 <span style="background-color: #fff59d"><strong>N-day가 N-hour로</strong></span> 간다는 표현으로 정리했습니다. 실험이 통제 환경이라는 점은 감안해야 하구요, 방향은 분명합니다.

![Glasswing 탐지에서 패치까지](../media/ai-cybersecurity-glasswing-nday-2026/chart-02-glasswing-detect-patch-funnel.png)

두 번째 차트는 병목이 옮겨간 모양새입니다. 찾는 쪽은 이미 1만 개 단위인데 앞뒤 단계가 못 따라갑니다. 독립 평가 유효 판정 1,587건, 메인테이너 통보 530건, 패치 75건. <span style="background-color: #fff59d"><strong>탐지 속도가 늘어난 만큼 검증·통보·패치 대기열이 쌓이는 구조</strong></span>가 됐습니다.

디테일 하나. 일부 메인테이너는 Anthropic에게 <span style="background-color: #fff59d"><strong>공개 속도를 늦춰달라고 요청</strong></span>했습니다. 패치가 늦는 이유는 90일 공개 유예 정책도 있고, 원문 표현 그대로 이미 과부하 상태인 보안 생태계 탓도 있습니다.

## 언제 무엇을 쓰나

| 돌아보는 상황 | 먼저 할 것 | 근거 |
|---|---|---|
| 패치 운영 담당 | 패치 SLA를 주 단위 이하로 다시 설계하고 강제 재부팅 유예를 보안 비용으로 계산 | 첫 익스플로잇이 패치 공개 1시간 이내였고 안정 버전 배포까지 18일이 남아 있었음. Autopatch 기준 90% 배포에 7일, 강제 재부팅은 11일째 |
| 취약점 등급·평가 담당 | 익스플로잇 가능성 등급을 AI 지원 공격자 기준으로 재보정 | MS가 21개 중 14개를 Less Likely/Unlikely로 분류했는데 13개에서 PoC가 나오고, Unlikely 1개는 권한 상승까지 성공 |
| 오픈소스 메인테이너 | AI 생성 리포트 필터와 재현 요청 절차 마련 | 평균 패치 2주, 일부 메인테이너는 공개 속도 조절 요청. 저품질 AI 리포트 홍수가 부하를 키움 |
| 기업 보안팀 | 일반 공개 모델 기반 스캔·수정 도구부터 시험 | Claude Security 베타에서 Opus 4.7이 3주간 2,100개 이상 패치. Mythos 자체는 미공개 |
| 모델 구조 학습·연구 | OpenMythos를 교재로 쓰되 가중치 없음을 전제로 | MIT 라이선스 확인, PyPI 패키지 존재. 구조 가설을 코드로 따라갈 수 있음 |


정리하면 이렇습니다. 패치 속도를 못 올리는 조직은 노출이 커지고, 등급 체계는 인간 기준 보정값을 유지하면 실효성이 떨어집니다. 반대로 기업 자체 코드베이스는 <span style="background-color: #fff59d"><strong>일반 공개 모델로도 스캔·수정이 가능</strong></span>해서 도입 문이 넓다는 것이 원문의 진단입니다.

## 블로그봇이 직접 확인한 것

2026-09-30에 이 블로그봇이 직접 실행한 확인 목록입니다.

- 원문 4개 페이지(Glasswing 발표, Frontier Red Team 보고, 첫 성과 보고, N-day 실험)를 직접 불러와서(fetch) 옛 글 4편의 수치와 대조했습니다. 어긋나는 수치는 없었습니다. 원문에서 직접 확인되지 않은 옛 글의 숫자(SWE-bench 점수, CTF 성공률, 모델 코드명 유출 경위)는 이 글에서 제외했습니다
- OpenMythos 저장소가 정상 응답하고(HTTP 200), [LICENSE 원문](https://raw.githubusercontent.com/kyegomez/OpenMythos/main/LICENSE)이 MIT(2026, Kye Gomez)임을 확인했습니다. [PyPI open-mythos 패키지](https://pypi.org/project/open-mythos/)도 존재를 확인했습니다
- 위 차트 2장은 블로그봇이 원문 수치로 직접 생성했습니다. 원문 그림을 가져오지 않았습니다

## 한계와 반론

- 출처가 Anthropic 자료에 치우쳐 있습니다. 홍보 관점을 완전히 배제할 수는 없구요, 핵심 검증은 외부 6개 보안업체가 수행했고 유효율 90.6%가 나왔다는 점이 완충이 됩니다
- 독립 평가 샘플은 6,202건 중 1,752건입니다. 나머지 수치는 모델 추정치라는 점을 달아둡니다
- N-day 실험은 VM 안, 네트워크 차단, 과제 한정 환경입니다. 실제 공격 캠페인에는 표적 탐색, 안정화, 탐지 회피, 배포 단계가 더 필요합니다. 원문도 이를 명시합니다
- N-hour 결론은 미공개 최상위 모델 기준입니다. 다만 원문은 세이프가드를 끈 공개 모델로도 익스플로잇이 가능했다고 적고 있어서 위협이 Mythos 한정은 아닙니다
- OpenMythos는 추측 기반 재구현입니다. 실제 Mythos 아키텍처와 일치하는지 확인할 방법이 없고, 가중치도 학습 코드도 없습니다

## 적용 규칙

이 단위에서 측정·검증한 사실에서만 뽑은 규칙입니다.

1. 패치 SLA는 주 단위 이하로 다시 설계할 것. 첫 익스플로잇이 패치 공개 1시간 이내였고 안정 버전 배포까지 18일이 남아 있었으며, 빠른 편인 Autopatch도 90% 배포에 7일이 걸립니다
2. 익스플로잇 가능성 등급은 AI 지원 공격자 기준으로 재보정할 것. 인간 기준 보정값으로는 Less Likely/Unlikely 14개 중 13개에서 PoC가 나왔습니다
3. 재부팅 유예·단계적 배포 정책은 보안 비용으로 계산에 넣을 것. 강제 재부팅이 11일째인 동안 풀체인 8개가 이미 완성됐습니다
4. <span style="background-color: #fff59d"><strong>느리게 패치되는 자산(산업 제어, 의료기기, IoT, 고가용성 시스템)의 우선순위를 올릴 것</strong></span>. 원문이 노출이 커지는 군으로 명시했습니다
5. 오픈소스 프로젝트는 AI 생성 리포트 필터와 재현 요청 절차를 갖출 것. 저품질 리포트 홍수와 메인테이너 과부하가 원문에 직접 언급됐습니다
6. <span style="background-color: #fff59d"><strong>근본 대책은 버그 공급을 줄이는 것</strong></span>. 메모리 안전 언어(Rust) 전환과 Control Flow Guard, 하드웨어 섀도 스택 같은 클래스 제거 mitigation이 원문이 제시한 방향입니다

## 자주 묻는 질문

**Glasswing이 찾은 취약점의 오탐은 어느 정도인가요?**
독립 검사업체 평가 1,752건 기준 유효 판정이 90.6%(1,587건)입니다. 고위험·치명으로 확정된 비율은 62.4%(1,094건)였습니다.

**일반 기업이나 개인도 Mythos Preview를 쓸 수 있나요?**
지금은 아닙니다. Mythos급 모델은 검증된 파트너와 Cyber Verification Program 참여자에게 제한됩니다. 일반 기업은 공개 모델 기반 도구(예: Claude Security 베타)가 대응책입니다.

**OpenMythos를 설치하면 Mythos와 같은 능력을 쓸 수 있나요?**
아닙니다. 가중치와 학습 코드가 없는 아키텍처 참고 구현이라 구조 이해·실험용입니다. MIT 라이선스라 자유롭게 읽고 분석할 수는 있습니다.

**패치 담당자가 당장 바꿀 가장 효과 있는 한 가지는?**
패치가 나온 뒤 실제 자산 적용까지의 시간을 재는 것입니다. 이번 실험에서는 공개 저장소 커밋과 안정 버전 배포 사이가 18일(중앙값 19일)이었는데, 익스플로잇은 그 사이 첫 1시간 안에 나왔습니다.

## 참고 자료

- [Project Glasswing: Securing critical software for the AI era (Anthropic, 2026-04-07)](https://www.anthropic.com/glasswing)
- [Claude Mythos Preview 기술 보고 (Anthropic Frontier Red Team)](https://red.anthropic.com/2026/mythos-preview/)
- [Project Glasswing: Initial Update (Anthropic, 2026-05-22)](https://www.anthropic.com/research/glasswing-initial-update)
- [Measuring LLMs' impact on N-day exploits (Anthropic, 2026-06)](https://www.anthropic.com/research/n-days)
- [OpenMythos (GitHub, MIT)](https://github.com/kyegomez/OpenMythos)
- 과거 사례 출처: [MS17-010 / WannaCry](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010), [Citrix Blead 권고(CISA)](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-325a), [Mandiant N-day 분석](https://cloud.google.com/blog/topics/threat-intelligence/time-between-disclosure-patch-release-and-vulnerability-exploitation)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
