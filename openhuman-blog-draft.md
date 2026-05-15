# OpenHuman — 당신의 데이터를 기억하는 오픈소스 AI 에이전트

> 2026년 5월, tinyhumans.ai가 공개한 **OpenHuman**은 "AI가 나에 대해 뭘 알고 있나?"라는 근본적인 질문에서 출발한다. 118개 이상의 서비스와 원클릭 연동, 20분마다 자동 동기화, 로컬 기반 메모리 트리. Karpathy의 Obsidian 위키 워크플로에서 영감받은 이 프로젝트가 왜 주목받는지 정리했다.

![OpenHuman Demo](https://github.com/tinyhumansai/openhuman/blob/main/gitbooks/.gitbook/assets/demo.png?raw=true)

---

## 왜 "또" AI 에이전트인가

현재 AI 에이전트 시장은 두 가지 극단에 있다. 한쪽은 Claude, ChatGPT 같은 **챗봇** — 대화는 잘하지만 당신에 대해 아무것도 모른다. 매 대화가 새 시작이다. 다른 한쪽은 OpenClaw, Hermes 같은 **개발자 도구** — 강력하지만 설정이 복잡하고, 플러그인 생태계에 의존하며, 에이전트가 "당신"을 이해하는 데 몇 주가 걸린다.

OpenHuman이 노리는 지점은 명확하다. **설치 후 몇 분 만에 당신의 전체 맥락을 이해하는 에이전트**를 만드는 것.

> "Most agents start cold. OpenHuman skips the wait."

---

## 핵심 아키텍처: 메모리가 먼저다

OpenHuman의 설계 철학은 한 줄로 요약된다: **모델이 똑똑한 게 아니라, 맥락이 풍부한 게 중요하다.**

### Memory Tree — 로컬 지식 그래프

OpenHuman의 심장은 **Memory Tree**다. Gmail, Slack, GitHub, Notion, 캘린더 — 연결된 모든 데이터가 하나의 파이프라인을 통과한다:

1. **정규화**: 모든 소스를 마크다운으로 변환
2. **청킹**: 3,000토큰 이하로 압축
3. **스코어링**: 중요도에 따라 점수 부여
4. **계층화**: 소스별/주제별/날짜별 요약 트리로 구조화
5. **저장**: 로컬 SQLite에 저장 (벡터 블랙박스가 아니다)

이 구조의 장점은 **추론 가능성**이다. 벡터 유사도 검색이 "어렴풋이 비슷한 것"을 찾는다면, Memory Tree는 "이 이메일이 이 프로젝트와 연결되어 있고, 이 사람이 관여했다"를 그래프 순회로 답한다.

### Obsidian 위키 — 읽을 수 있는 메모리

"믿을 수 없는 메모리는 메모리가 아니다." OpenHuman은 Memory Tree의 모든 청크를 `.md` 파일로 Obsidian 호환 볼트에 저장한다. Obsidian에서 열어보고, 편집하고, 링크를 직접 연결할 수 있다.

이건 Karpathy가 [자신의 Obsidian 위키 워크플로](https://x.com/karpathy/status/2039805659525644595)에서 제안한 방식과 같은 맥락이다. AI가 만든 지식 베이스를 인간이 검증하고 보완하는 루프.

### Auto-fetch — 20분마다 자동 동기화

대부분의 에이전트가 "질문할 때만" 데이터를 가져온다. OpenHuman은 **20분마다** 연결된 모든 서비스에서 새 데이터를 끌어와서 Memory Tree에 반영한다. 아침에 일어나면 에이전트가 이미 어젯밤 이메일과 오늘 일정을 알고 있다.

---

## 118개 이상의 원클릭 연동

Gmail, Notion, GitHub, Slack, Stripe, Google Calendar, Drive, Linear, Jira… API 키를 수동으로 설정할 필요 없이 **원클릭 OAuth**로 연결된다. 연결된 모든 서비스는 에이전트에게 typed tool로 노출된다.

현재 AI 에이전트 시장에서 이 정도 연동을 기본 제공하는 경우는 드물다. 대부분 BYO(Bring Your Own) 방식으로, 사용자가 직접 플러그인을 찾고 설치하고 설정해야 한다.

---

## TokenJuice — 토큰 비용 80% 절감

AI 에이전트의 현실적인 문제: **토큰이 비싸다.** 이메일 본문, 검색 결과, 스크래핑 내용, 도구 호출 결과 — 이 모든 게 LLM 컨텍스트를 잡아먹는다.

OpenHuman은 **TokenJuice**라는 토큰 압축 레이어를 모든 도구 출력 앞에 둔다:

- HTML → 마크다운 변환
- 긴 URL 단축
- 비 ASCII 문자 제거
- 중복 정보 압축

결과: **동일한 정보를 최대 80% 적은 토큰으로 전달**. 최근 6개월 이메일을 스윕해도 한 자릿수 달러면 충분하다.

---

## 모델 라우팅 — 하나의 구독으로

OpenHuman은 작업 특성에 따라 자동으로 모델을 선택한다:

| 작업 | 모델 |
|------|------|
| 복잡한 추론 | `hint:reasoning` → 프론티어 모델 |
| 빠른 응답 | `hint:fast` → 경량 모델 |
| 이미지 처리 | 비전 모델 |

하나의 구독으로 모든 라우팅을 처리한다. 여러 API 키를 관리하거나, 모델별로 요금을 추적할 필요가 없다.

선택적으로 **Ollama**를 통한 로컬 AI도 지원한다. 임베딩과 요약을 온디바이스에서 실행하고 싶은 사용자를 위한 옵션.

---

## 데스크톱 마스코트 — 에이전트에 얼굴이 있다

OpenHuman은 단순한 터미널 도구가 아니다. **데스크톱 마스코트**가 있다.

- 말을 하고, 반응하고, 주변 환경에 반응한다
- **Google Meet에 실제 참가자로 참석**해서 회의를 녹취하고, 당신을 대신해 발언할 수도 있다
- 타이핑을 멈춰도 **백그라운드에서 계속 생각**한다
- 주에 걸쳐 당신을 기억한다

이건 "챗봇에 아바타 붙이기"가 아니다. 에이전트가 지속적으로 당신의 맥락을 유지하면서, 언제든 대화형으로 개입할 수 있다는 의미다.

---

## 경쟁사 비교

OpenHuman의 GitHub README에 있는 비교표를 정리하면:

|  | Claude Cowork | OpenClaw | Hermes | **OpenHuman** |
|--|---------------|----------|--------|---------------|
| 오픈소스 | ❌ | ✅ MIT | ✅ MIT | ✅ GNU |
| 시작 난이도 | ✅ | ⚠️ 터미널 필수 | ⚠️ 터미널 필수 | ✅ UI |
| 비용 | 구독+애드온 | BYO 모델 | BYO 모델 | **1구독 + TokenJuice** |
| 메모리 | 채팅 범위 | 플러그인 의존 | 자기학습 | **Memory Tree + Obsidian** |
| 연동 | 소수 | BYO | BYO | **118+ OAuth** |
| 자동 동기화 | ❌ | ❌ | ❌ | **20분 주기** |
| 모델 라우팅 | 단일 | 수동 | 수동 | **자동** |
| 기본 도구 | 코드만 | 코드만 | 코드만 | **코드+검색+스크래퍼+음성** |

---

## 기술 스택

- **런타임**: Rust + Tauri (Tauri/CEF 내장)
- **프론트엔드**: 웹 UI
- **로컬 DB**: SQLite
- **로컬 AI**: Ollama (선택)
- **음성**: STT 인 + ElevenLabs TTS 아웃 + 마스코트 립싱크
- **라이선스**: GNU GPL-3.0

개발 환경 세팅: Node.js 24+, pnpm 10.10.0, Rust 1.93.0, CMake 필요.

---

## 설치

```bash
# macOS / Linux x64
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
```

또는 [tinyhumans.ai/openhuman](https://tinyhumans.ai/openhuman)에서 DMG/EXE 다운로드.

> ⚠️ 현재 **Early Beta** 상태. "거친 부분"이 있을 수 있다고 명시되어 있다.

---

## 생각할 점

### 가능성

- **"Cold start" 문제의 실질적 해결**: 대부분의 AI 에이전트가 "몇 주 쓰면 좋아져요"라고 말하지만, OpenHuman은 연동 즉시 맥락을 확보한다
- **로컬 우선 설계**: 데이터가 내 기기에 있고, 암호화되어 있고, 내가 읽을 수 있다
- **비용 효율**: TokenJuice + 자동 모델 라우팅으로 실제 사용 비용을 크게 낮춘다

### 아쉬운 점

- **GNU GPL-3.0 라이선스**: MIT에 비해 상업적 활용 제약이 있다. 기여한 코드도 동일 라이선스로 공개해야 한다
- **Early Beta**: 실제 안정성과 에지 케이스는 직접 써봐야 알 수 있다
- **구독 모델 불명확**: "One sub"라고 하지만 정확한 가격 구조가 아직 명확하지 않다
- **의존성**: 118개 연동이 장점이지만, OAuth 토큰 관리와 서비스 정책 변경에 대한 대비가 필요하다

---

## 링크

- **GitHub**: [github.com/tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman)
- **공식 사이트**: [tinyhumans.ai/openhuman](https://tinyhumans.ai/openhuman)
- **문서**: [tinyhumans.gitbook.io/openhuman](https://tinyhumans.gitbook.io/openhuman/)
- **Discord**: [discord.tinyhumans.ai](https://discord.tinyhumans.ai/)
- **크리에이터**: [@senamakel](https://x.com/senamakel) (X/Twitter)

---

OpenHuman은 "더 똑똑한 챗봇"이 아니라 **"당신의 모든 데이터를 소화하고 기억하는 로컬 에이전트"**를 지향한다. AI가 당신에 대해 아는 것이 포스트잇 몇 장이 아니라, 구조화된 지식 그래프가 되는 것. 그 방향성이 당연해 보이면서도, 아직 아무도 제대로 해내지 못한 일이다.

Early Beta지만, 방향과 아키텍처는 확실히 주목할 만하다.
