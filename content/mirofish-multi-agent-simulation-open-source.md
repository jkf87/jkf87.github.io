---
title: "AI 에이전트 1,000개로 여론을 시뮬레이션한다? MiroFish 오픈소스 분석"
date: 2026-03-10
tags:
  - ai
  - multi-agent
  - llm
  - simulation
  - graphrag
description: "문서 업로드→지식그래프→수천 AI 에이전트 트위터/레딧 시뮬레이션→ReACT 보고서까지 자동화하는 MiroFish를 구조·실행법·비용 리스크 관점에서 정리합니다."
---

요즘 ‘AI 에이전트’ 이야기가 많지만, 정작 **여러 에이전트가 사회를 흉내 내며 토론하고 예측 보고서까지 뽑아주는** 오픈소스는 흔치 않습니다. 이번 글은 GitHub에서 화제가 된 **MiroFish**(MIT) 저장소를 분석한 내용을 바탕으로, *무엇을 하는 프로젝트인지 / 구조가 어떻게 생겼는지 / 실행하려면 뭘 준비해야 하는지 / 비용·리스크는 무엇인지*를 한 번에 정리합니다.

![MiroFish 로고](./images/mirofish-logo.jpeg)

## MiroFish 한 문단 요약

MiroFish는 "만물을 예측하는 군집 지능 엔진"을 표방하는 **멀티에이전트 기반 시뮬레이션 플랫폼**이다. 사용자가 PDF/마크다운/텍스트 형태의 시드 자료를 업로드하면, LLM이 자동으로 온톨로지를 생성하고 지식 그래프를 구축한 뒤, 수천 개의 개성 있는 AI 에이전트를 소환하여 트위터·레딧 이중 플랫폼에서 사회적 시뮬레이션을 병렬 실행한다. 시뮬레이션 완료 후에는 ReACT 패턴의 보고서 에이전트가 인사이트를 정리해 예측 리포트를 생성하고, 개별 에이전트와의 심층 인터뷰까지 지원한다. 정책 시뮬레이션, 여론 예측, 금융 분석, 심지어 창작 시나리오(예: 홍루몽 결말 예측)까지 활용 가능한 범용 예측 도구이다.

## 파이프라인: 문서 → 지식 그래프 → 수천 에이전트 → 보고서

| 단계 | 기능 | 설명 |
|------|------|------|
| **1단계** | 지식 그래프 구축 | 시드 문서 → LLM 온톨로지 자동 생성 → Zep GraphRAG로 그래프 저장 |
| **2단계** | 환경 설정 | 그래프 엔티티 추출 → OASIS 에이전트 프로필 자동 생성 (MBTI, 직업, 감정 성향 등) |
| **3단계** | 시뮬레이션 실행 | 트위터 + 레딧 이중 플랫폼 병렬 시뮬레이션, 실시간 액션 로깅 |
| **4단계** | 보고서 생성 | ReACT 패턴(Thought→Action→Observation) 기반 다단계 리포트 자동 작성 |
| **5단계** | 심층 인터뷰 | 시뮬레이션된 에이전트와 1:1 대화, 에이전트 관점에서의 분석 |

**추가 기능:**
- D3.js 기반 지식 그래프 시각화
- 에이전트별 활동 로그(JSONL) 추적
- Docker Compose 원클릭 배포
- OpenAI 호환 LLM 범용 지원 (Qwen, GPT, Claude 등)

## 아키텍처 핵심

### 전체 구조

```
[사용자] → [Vue 3 프론트엔드 :3000]
              ↓ /api 프록시
         [Flask 백엔드 :5001]
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
[Zep Cloud] [LLM API] [OASIS]
(지식그래프)  (추론)   (에이전트 시뮬레이션)
```

### 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | Vue 3.5 + Vite 7.2 + D3.js + Axios |
| 백엔드 | Flask 3.0 + Python 3.11/3.12 |
| LLM 통합 | OpenAI SDK (범용 호환) |
| 지식 그래프 | Zep Cloud (GraphRAG, 메모리 관리) |
| 에이전트 프레임워크 | CAMEL-AI + CAMEL OASIS |
| 문서 파싱 | PyMuPDF (PDF), charset-normalizer |
| 패키지 관리 | uv (Python), npm (Node.js) |
| 배포 | Docker Compose |

### 핵심 서비스 모듈 (backend/app/services/)

- `ontology_generator.py` — 온톨로지 자동 생성 (엔티티 10개 타입 제약)
- `graph_builder_service.py` — Zep 기반 지식 그래프 구축
- `oasis_profile_generator.py` — 에이전트 페르소나 생성 (트위터/레딧 이중 포맷)
- `simulation_runner.py` — 서브프로세스 기반 병렬 시뮬레이션 실행
- `report_agent.py` — ReACT 패턴 보고서 에이전트
- `zep_tools_service.py` — 하이브리드 그래프 검색 (InsightForge/PanoramaSearch/QuickSearch)

## 실행 방법

### 사전 요구사항

```bash
node -v          # 18 이상
python --version # 3.11 또는 3.12만 지원
uv --version     # Python 패키지 매니저
```

### 외부 API 키 필요

- **LLM API 키**: OpenAI 호환 API (알리바바 Qwen 기본 권장)
- **Zep Cloud API 키**: 무료 티어 사용 가능 (월 ~50만 토큰)

### 설치 및 실행

```bash
# 1. 클론
git clone https://github.com/666ghj/MiroFish.git
cd MiroFish

# 2. 환경 설정
cp .env.example .env
# .env 파일에 LLM_API_KEY, ZEP_API_KEY 등 입력

# 3. 의존성 설치
npm run setup:all

# 4. 개발 서버 실행
npm run dev
# 프론트엔드: http://localhost:3000
# 백엔드: http://localhost:5001

# Docker 배포 (대안)
docker compose up -d
```

### 주의사항

- 시뮬레이션 시 LLM API 비용이 상당히 발생할 수 있음 → **40라운드 이하로 먼저 테스트** 권장
- 에이전트 수가 많을수록 연산·비용 모두 증가
- Python 3.10 이하, 3.13 이상은 미지원

## 실전 리스크(비용/의존성/신뢰성)

| 항목 | 설명 |
|------|------|
| **API 비용** | 1,000개 에이전트 × 100라운드 시뮬레이션 시 10만+ 토큰 소비 가능. 비용 예측이 어렵다. |
| **외부 의존성** | Zep Cloud + LLM API 두 가지 외부 서비스에 동시 의존. 오프라인 실행 불가. |
| **Python 버전 제약** | 3.11/3.12만 지원. 많은 환경에서 호환성 이슈 발생 가능. |
| **결과 신뢰성** | AI 에이전트의 행동은 LLM 프롬프트 품질에 크게 의존. 실제 사회 현상과의 상관관계 검증이 부족. |
| **확장성** | 대규모 시뮬레이션 시 연산 자원과 시간이 급격히 증가. |
| **언어** | UI와 문서가 주로 중국어. 한국어/영어 사용자는 진입 장벽 존재. |
| **보안** | .env에 API 키 직접 저장. 프로덕션 환경에서 키 관리 주의 필요. |

## 활용 아이디어 (교육/업무)

- 수업 프로젝트: 같은 자료로 서로 다른 관점의 페르소나 토론을 만들고 논거 비교
- 학교/정책 이슈: 이해관계자 페르소나를 만들고 쟁점/우려 포인트를 미리 수집
- 업무 자동화: ReACT 보고서 템플릿으로 반복 리포팅 파이프라인 구성

## 참고 링크

- Repo: https://github.com/666ghj/MiroFish
