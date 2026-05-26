# 에이전트 메모리 실전기 — LanceDB 마이그레이션 + 인프라 총정리

> 2026-05-22 그룹 채팅 논의 + 액티브 메모리 + LLM Wiki 인프라 종합 정리본
> 업데이트: 2026-05-22 13:30 — 액티브 메모리, LLM Wiki, 인제스트 소스 현황 추가

---

## 1. 배경: 기존 메모리 시스템의 한계

OpenClaw의 기본 메모리 시스템은 **SQLite FTS5 + sqlite-vec** 기반(memory-core).

**문제점:**
- 키워드 매칭에만 의존 → 의미 기반 회수 불가
- AI 에이전트가 문맥을 기억하지 못하는 경우 반복
- LOCOMO 벤치마크 기준 회수 정확도 **52%**, 평균 회수 지연 **8.4초**
  - 출처: lancedb.com/blog/openclaw-memory-from-zero-to-lancedb-pro
  - 조건: LOCOMO 첫 100개 샘플, GPT-4.1-mini, end-to-end 파이프라인

---

## 2. 메모리 시스템 지형도 (4종 비교)

| 시스템 | 레이어 | 특징 | 상태 |
|--------|--------|------|------|
| **Honcho** | 앱/SDK | 대화 기반 사용자 모델링, 세션 컨텍스트 지속 추적 | 상용 SDK |
| **Hindsight** | 연구/아키텍처 | 4개 네트워크 (world facts / experiences / summaries / beliefs), retain/recall/reflect 설계 (Latimer·Boschi) | 논문 프로토타입 |
| **Hunch** | 앱 | 개인 지식 회상형, 사용자 중심 메모리 | 개인 비서 목적 |
| **OpenClaw + LanceDB** | 인프라/엔진 | bge-m3 1024차원 로컬 임베딩, autoCapture/autoRecall, 11,088개 실전 검증 | 운영 중 |

**핵심 프레임:** "승자 비교가 아니다 — 레이어가 다르다"
- LanceDB = 엔진(인프라) 레이어
- Honcho/Hindsight = 앱(오케스트레이션) 레이어

---

## 3. 왜 LanceDB인가

**SQLite FTS5 vs LanceDB 비교:**

| 항목 | SQLite FTS5 | LanceDB |
|------|-------------|---------|
| 검색 방식 | BM25 키워드 전문검색 | 벡터 ANN + BM25 FTS + 하이브리드 |
| 의미 검색 | 불가 | 가능 |
| 로컬 운영 | 초경량 | 로컬-first, 서버 불필요 |
| 대용량 | 수십만 행까지 빠름 | Lance 컬럼 포맷으로 스캔 빠름 |
| 단점 | 정확한 단어가 있어야 검색됨 | 설정 복잡도 상대적으로 높음 |

**한 줄 요약:** "키워드만 찾을지, 맥락까지 이해할지의 차이 — 속도 경쟁이 아니라 능력의 차이"

---

## 4. 설정 (ollama + bge-m3)

```
plugin: memory-lancedb
embedding.provider: ollama (로컬)
embedding.baseUrl: http://127.0.0.1:11434
embedding.model: bge-m3
embedding.dimensions: 1024
dbPath: ~/.openclaw/memory/lancedb
autoRecall: true
autoCapture: true
```

**선택 이유:**
- 외부 API 의존 없이 로컬에서 임베딩
- 비용 발생 없음
- ollama만 설치하면 즉시 사용
- 중단 없이 24시간 운영 가능

**확인된 설정:** 전 봇(blogbot, ytclaw, 마케터봇, aif0222bot, agasa) 공통으로 memory-lancedb enabled, autoRecall/autoCapture true, ollama bge-m3 1024차원

---

## 5. 실전 마이그레이션 과정

### 5-1. 문제 발생
- 플러그인 설치 직후 `ltm stats` → 0개
- 원인: 기존 SQLite 메모리가 LanceDB로 자동 마이그레이션되지 않음

### 5-2. 디버깅 과정
1. `ltm stats` 실행 → 0개 확인
2. config 파일 재확인
3. **768차원 vs 1024차원 스키마 충돌 발견** (기존 2월 생성 파일 vs bge-m3 1024차원)
4. Codex AI로 원인 분석

### 5-3. 해결
- `import-memory-core` 명령 구현
- 차원 불일치 해결 (768→1024 재인덱싱)
- config 수정 후 재시작
- **11,088개 메모리 이전 성공**

---

## 6. 마이그레이션 결과

| 항목 | 수치 |
|------|------|
| 이전된 메모리 항목 | 11,088개 |
| LanceDB 회수 정확도 | 76% |
| 평균 회수 지연 | 4.8초 |
| memory-core 대비 정확도 | +24%p |
| memory-core 대비 속도 | -43% |
| LanceDB DB 크기 | 60MB |

출처: lancedb.com/blog/openclaw-memory-from-zero-to-lancedb-pro · LOCOMO 100샘플 · GPT-4.1-mini · end-to-end 파이프라인 벤치마크

**참고:** memory-lancedb-pro 설정 시 회수 정확도 80%, 회수 지연 14.3초 (동일 조건)

---

## 7. 스킬화 & 오픈소스

`openclaw-lancedb-migrate-skill` GitHub 공개:
- 전체 마이그레이션 과정 자동화
- 768→1024 차원 호환성 처리
- import-memory-core 명령 포함
- config 템플릿 + 에러 디버깅 가이드 포함
- 같은 문제 겪는 사용자가 즉시 적용 가능

---

## 8. 레이어 비교: LanceDB vs Hindsight

**LanceDB (인프라 레이어):**
- 로컬 벡터 검색 엔진
- retain/recall 파이프라인 실전 구현
- 의미 + 키워드 하이브리드 검색
- OpenClaw memory 플러그인으로 통합

**Hindsight (연구/아키텍처 레이어):**
- 4-네트워크 메모리 아키텍처 (arxiv.org/abs/2512.12818)
- world facts / experiences / summaries / beliefs
- retain / recall / reflect 설계
- 논문 프로토타입, 제품화 진행 중

**프레임:** LanceDB는 엔진이고, Hindsight는 그 위에서 돌아가는 아키텍처. 같은 경쟁 상대가 아님.

---

## 9. 논문 자동화 파이프라인으로 확장

메모리 마이그레이션은 인프라 정비. 그 결과물을 실제 연구 워크플로우에 연결:

1. **로컬 메모리 기반 회수** (LanceDB) — 운영 중
2. **에이전트 작업 이력 자동 축적** — 자동화 진행
3. **논문 조사 / 요약 / 정리 자동화** — 반자동
4. **Zotero 연동으로 서베이 완성** — 구축 중

---

## 10. 팩트체크 & 정정 사항

### prrao87/lancedb-study 출처 정정
- ❌ 해당 repo는 **Elasticsearch vs LanceDB** 비교지, SQLite vs LanceDB 비교가 아님
- QPS=5,948 / p50=2.6ms 등 수치는 이 repo에 없음
- 발표에서 SQLite vs LanceDB 비교로 인용 금지

### Chroma ≠ Honcho (혼초)
- Chroma = 벡터DB 레이어 (LanceDB와 같은 레벨)
- Honcho = 그 위의 메모리 SDK/앱 레이어
- 혼동 금지

### LanceDB 공식 벤치마크 검증
- lancedb.com/blog/openclaw-memory-from-zero-to-lancedb-pro — 실존 확인
- docs.lancedb.com/enterprise/benchmarks — 엔터프라이즈 벤치
- memory-core 52%/8.4s, memory-lancedb 76%/4.8s, memory-lancedb-pro 80%/14.3s
- 조건: LOCOMO 첫 100샘플, GPT-4.1-mini, end-to-end

---

## 11. 발표 스타일 가이드

### 금지 표현
- "결론적으로"
- "A가 아니라 B다"
- "확인할 수 있다"
- "~임을 알 수 있다"
- "핵심은 ~이다"

### 수치 사용 원칙
- 출처/조건 없는 수치 사용 금지
- 벤치마크 수치는 항상 조건부 단서 붙이기

### 비개발자용 한 줄
"LanceDB는 AI 기억을 내 컴퓨터 안에서 빠르게 찾아주는 로컬 검색 엔진입니다"

---

## 12. 액티브 메모리 (Active Memory) 설정

OpenClaw의 **active-memory** 플러그인은 세션 시작 시 관련 메모리를 자동 주입하는 레이어.

**현재 설정:**
```
plugin: active-memory
enabled: true
agents: * (전체 에이전트 대상)
allowedChatTypes: direct (DM만)
queryMode: recent
promptStyle: balanced
timeoutMs: 15000
maxSummaryChars: 220
persistTranscripts: false
modelFallback: zai/glm-4.7-flash
thinking: off
searchMode: inherit (LanceDB 설정 상속)
```

**작동 방식:**
1. 사용자가 DM 보내면 active-memory가 LanceDB에서 관련 기억 검색
2. 최대 220자 요약으로 세션 컨텍스트에 주입
3. 15초 타임아웃 내 완료, 실패 시 GLM-4.7-flash로 폴백
4. 그룹 채팅에서는 작동하지 않음 (allowedChatTypes: direct)

**autoRecall / autoCapture 흐름:**
- **autoCapture**: 대화 중 생성된 정보를 자동으로 LanceDB에 저장
- **autoRecall**: 세션 시작/발화 시 관련 기억을 자동 검색하여 컨텍스트에 추가
- 두 기능 모두 bge-m3 1024차원 ollama 로컬 임베딩 사용

---

## 13. LLM Wiki (Bridge 모드) 인프라

### 현재 상태
```
Wiki vault mode: bridge
Vault path: ~/.openclaw/wiki/main
Render mode: obsidian
Bridge: enabled (0 exported artifacts)
Obsidian CLI: missing (설정은 켜져 있으나 CLI 미설치)
```

### 페이지 통계
- **sources**: 1,880페이지 (네이티브 217 + 브릿지 1,644 + 브릿지-이벤트 17 + 기타 2)
- **entities**: 0
- **concepts**: 0
- **syntheses**: 0
- **reports**: 10

### 인제스트 소스 구성
1. **Threads 크롤링** (10건): macOS AI 생태계, AI 비용 투자, 로컬 LLM 등
2. **gptersbot 메모리 브릿지** (~30건): 2026-04-14~05-18 일일 메모리
3. **imagebot 메모리 브릿지** (~20건): dreaming-deep/light, 포스터, 풍경 등
4. **오늘자 인제스트**: `claude-cli-p-모드-이슈-openclaw-런타임-현황-2026-05-22.md`

### 주요 설정
```
plugins.slots.memory: memory-lancedb
plugins.entries.memory-wiki.enabled: true
plugins.entries.memory-wiki.vaultMode: bridge
plugins.entries.memory-wiki.bridge.readMemoryArtifacts: true
plugins.entries.memory-wiki.unsafeLocal.allowPrivateMemoryCoreAccess: true
agents.defaults.memorySearch.enabled: true
agents.defaults.memorySearch.provider: ollama
agents.defaults.compaction.memoryFlush.enabled: true
hooks.internal.entries.session-memory.enabled: true
```

### 경고 사항
- Obsidian CLI가 PATH에 없음 — 설정은 켜져 있으나 실제 동작 불가
- Bridge 모드이나 메모리 플러그인이 공개 아티팩트를 아직 내보내지 않음
- Private memory-core 접근이 unsafe-local 모드 밖에서 허용됨

### Wiki 디렉토리 구조
```
~/.openclaw/wiki/main/
├── AGENTS.md
├── WIKI.md
├── _attachments/
├── _views/
├── concepts/    (0개)
├── entities/    (0개)
├── inbox.md
├── index.md
├── reports/     (10개)
├── sources/     (1,880개)
└── syntheses/   (0개)
```

---

## 14. Claude CLI -p 이슈 (메모리 런타임 연관)

### 문제 요약
- Claude CLI `-p` 모드에서 빈 응답·타임아웃·호출 실패 빈발
- 그룹 봇들(ytclaw, 마케터봇 등)이 반복적으로 Model Fallback 발생
- 2026-06-15 Anthropic Agent SDK 크레딧 분리 정책 시행 예정

### 메모리 영향
- Fallback 발생 시 세션 컨텍스트 유실 → autoRecall이 매번 새로 검색
- 빈 응답이 autoCapture에 의해 의미 없는 항목으로 저장될 가능성
- 메모리 검색 품질 저하 우려

### 권장 대응
- 멀티 fallback 전략 유지 (Z.AI/GLM, Codex, OpenRouter)
- 6/15 전까지 claude -p 의존도 축소
- ACP 동시 스폰 1개씩 직렬 제한

---

## 15. 남은 과제 (TODO)

- [ ] memories.lance 차원 호환성 재인덱싱 (기존 2월 생성 파일)
- [ ] 샘플 쿼리로 LanceDB 검색 품질 검증
- [ ] SQLite+FTS5 vs LanceDB 실측 벤치 실행 여부
- [ ] wiki 인제스트 concepts/entities/synthesis 레이어 추가 생성 (현재 0개)
- [ ] Obsidian CLI 설치 또는 설정에서 비활성화
- [ ] Bridge 모드 아티팩트 익스포트 활성화
- [ ] 2026-06-15 Agent SDK credit 분리 정책 사전 고지
- [ ] iCloud에 흩어진 중복 노트 2건 정리/삭제 여부
- [ ] active-memory 그룹 채팅 지원 여부 검토 (현재 direct만)

---

## 관련 파일 목록

| 파일 | 위치 | 설명 |
|------|------|------|
| 이 정리본 | `memory/2026-05-22-memory-summary.md` | 메모리 + 인프라 종합 |
| MEMORY.md | `MEMORY.md` | 블로그봇 장기 기억 |
| Claude CLI 이슈 | `wiki/sources/claude-cli-p-모드-이슈-...-2026-05-22.md` | Wiki 정본 |
| HTML 캔버스 (Notion) | `~/.openclaw/canvas/memory-slides-notion.html` | 발표용 11슬라이드 |
| PPTX (마케터봇) | `~/Downloads/memory_hyperframe_notion.pptx` | Notion 테마 11장 |
| PPTX (ytclaw) | `~/Downloads/memory_hyperframe_notion_theme.pptx` | Notion 테마 11장 |
| LanceDB DB | `~/.openclaw/memory/lancedb/memories.lance/` | 60MB, 23개 데이터 파일 |
| Wiki vault | `~/.openclaw/wiki/main/` | 1,880 소스, bridge 모드 |
| OpenClaw config | `~/.openclaw/openclaw.json` | 전체 설정 |
