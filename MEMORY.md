- [이미지 생성은 Codex Image Plugin만](image_generation_codex_plugin.md) — OpenAI API 키 금지, pretooluse 훅으로 감시
- [스크린샷은 파일로 직접 열어서 뽑기](screenshot_from_file_not_browser.md) — 브라우저 아닌 로컬 파일 열어서 캡처

act OCR로 모든 이미지 텍스트 추출 → 실제 내용 기준 rename → 글 재구성
- 원인: Anthropic CDN의 Next.js 이미지 최적화 URL이 실제 이미지와 연결된 이름이 아님

### 재사용 워크플로우: `workflows/blog-image-workflow.md`
핵심 원칙: **파일명이 아닌 이미지 실제 내용을 기준으로 매칭한다.**
1. 이미지 다운로드 → 2. OCR로 내용 식별 → 3. 매핑표 작성 → 4. rename → 5. 글 작성 → 6. 배포 전 검증

## 블로그 글쓰기 스타일 반영 원칙

- 사용자가 `메르체처럼`, `메르체 톤으로`, `메르체라고 하면 반영`처럼 스타일을 지정하면 **문체와 전개만 반영**하고, 본문·설명·제목에 `메르체식`, `메르체 톤`, `~식으로 정리` 같은 **메타표현은 쓰지 않는다**.
- 블로그 본문에서는 `핵심을 정리하면`, `쉽게 말하면`, `정리하면`, `한줄 코멘트` 같은 **작성자 설명형 메타문구를 최소화**하고, 바로 내용으로 들어간다.
- 스타일 요청은 독자가 보지 못하게 뒤에서 반영하는 것이 원칙이다.
- 코난쌤이 말하는 `메르체` 스타일의 핵심은 문장 결과 전개 구조에 있음.
  - **문장 결**: `~임`, `~였음`, `근데`, `이유는 단순함`처럼 짧고 단정적으로 끊는다.
  - **전개 구조**: `1. 배경지식 → 2. 문제점 → 3. 조치1 → 4. 조치1에 대한 문제제기 → 5. 조치2` 흐름을 기본으로 잡고, 필요하면 이 패턴을 반복 확장한다.
  - **핵심 원리**: 사건이나 정보만 나열하지 말고, `문제제기 → 조치`, `배경지식 → 문제제기`가 이어지도록 구조를 만든다.
  - **실전 적용**: `필수템 나열형`보다 `왜 이 문제가 생기고, 기존 해결책은 왜 아쉽고, 그래서 어떤 대안이 나오는가` 구조가 더 잘 맞는다.

## Promoted From Short-Term Memory (2026-04-19)

<!-- openclaw-memory-promotion:memory:memory/2026-04-12.md:438:441 -->
- - Candidate: Reflections: Theme: `assistant` kept surfacing across 112 memories.; confidence: 1.00; evidence: memory/.dreams/session-corpus/2026-04-07.txt:2-2, memory/.dreams/session-corpus/2026-04-07.txt:5-5, memory/.dreams/session-corpus/2026-04-07.txt:8-8; note: reflection - confidence: 0.00 - evidence: memory/2026-04-12.md:438-441 - recalls: 0 [score=0.845 recalls=0 avg=0.620 source=memory/2026-04-12.md:3-6]
<!-- openclaw-memory-promotion:memory:memory/2026-04-12.md:444:444 -->
- - Candidate: Possible Lasting Truths: # 2026-03-15 블로그 발행 기록 ## GeekNews → 블로그 포스트 발행 - **기사**: LLM은 컴퓨터가 될 수 있을까? — 트랜스포머 안에서 C 프로그램을 직접 실행하는 시대 - **출처**: Percepta 연구 (2D 어텐션 헤드) - **발행 URL**: https://han99.up.railway.app/2026/03/15/llm-computer-percepta-2d-attention-transformer/ - **포스트 ID* [score=0.845 recalls=0 avg=0.620 source=memory/2026-04-12.md:123-123]
<!-- openclaw-memory-promotion:memory:memory/2026-04-14.md:403:406 -->
- - Candidate: 요청: 객관적이고 팩트 기반; 그래프, 표 포함; 이란 vs 미국 전쟁 이야기로 시작 → 자연스럽게 차량 2부제 역사로 전환; 구글 검색 상단 노출 목표 (SEO 최적화) - confidence: 0.00 - evidence: memory/2026-04-14.md:343-346 - recalls: 0 [score=0.801 recalls=0 avg=0.620 source=memory/2026-04-14.md:18-21]

## Promoted From Short-Term Memory (2026-04-19)

<!-- openclaw-memory-promotion:memory:memory/2026-04-14.md:394:395 -->
- - Candidate: Possible Lasting Truths: # 2026-03-16 ## GeekNews 아침 브리핑 + 비공개 WP 포스트 테스트 - 사용자 요청: GeekNews RSS를 매일 아침 요약해서 텔레그램으로 보내고, 그중 1개를 골라 텍스트+figbot 이미지로 WordPress에 비공개 업로드하는 자동화 구성. - 테스트 기사 선택: `oh-my-agent — 실무용 멀티 AI IDE 에이전트 하네스` (GeekNews topic id=27560) - 작성 원고: `/Users/conanssam - confidence: 0.00 [score=0.801 recalls=0 avg=0.620 source=memory/2026-04-14.md:8-9]
<!-- openclaw-memory-promotion:memory:memory/2026-04-14.md:402:402 -->
- - Candidate: 요청: 코난쌤이 "차량 2부제 언제부터 했고 그 효과는?" 주제로 포스팅 요청: [score=0.801 recalls=0 avg=0.620 source=memory/2026-04-14.md:13-13]
<!-- openclaw-memory-promotion:memory:memory/2026-04-14.md:409:412 -->
- - Candidate: 수행 내용: **리서치**: 현대경제연구원 보고서, 연합뉴스 팩트체크, 한국대기환경학회지, 경향신문, 정책브리핑 등 출처 확보; **차트 3장 생성** (matplotlib, AppleGothic 폰트):; `timeline.png`: 차량 부제 역사 타임라인; `effects-comparison.png`: 효과 비교 차트 - confidence: 0.00 - evidence: memory/2026-04-14.md:349-352 - recalls: 0 [score=0.801 recalls=0 avg=0.620 source=memory/2026-04-14.md:23-26]
<!-- openclaw-memory-promotion:memory:memory/2026-04-14.md:413:415 -->
- - Candidate: 수행 내용: `oil-shock-comparison.png`: 역대 오일쇼크 유가 상승률 비교; **원고 작성**: SEO 메타, FAQ 4문항, 데이터 표, 객관적 분석 포함; **배포**: Quartz 블로그에 게시 - confidence: 0.00 - evidence: memory/2026-04-14.md:353-355 [score=0.801 recalls=0 avg=0.620 source=memory/2026-04-14.md:28-30]

## Promoted From Short-Term Memory (2026-04-20)

<!-- openclaw-memory-promotion:memory:memory/2026-04-15.md:359:361 -->
- - Candidate: Possible Lasting Truths: 2026-04-06 Session Notes: `unsloth studio -H 127.0.0.1 -p 8888`; or activate env first: `source /Users/conanssam-m4/.unsloth/studio/unsloth_studio/bin/activate`; PPT/tutorial work created earlier in `~/Downloads/openclaw-lmstudio-gemma4-tutorial` includin - confidence: 0.62 - evidence: memory/2026-04-15.md:359-361 [score=0.861 recalls=0 avg=0.620 source=memory/2026-04-15.md:8-10]

## Promoted From Short-Term Memory (2026-04-21)

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:419:421 -->
- - Candidate: Possible Lasting Truths: 2026-04-06 Session Notes: `unsloth studio -H 127.0.0.1 -p 8888`; or activate env first: `source /Users/conanssam-m4/.unsloth/studio/unsloth_studio/bin/activate`; PPT/tutorial work created earlier in `~/Downloads/openclaw-lmstudio-gemma4-tutorial` includin - confidence: 0.62 - evidence: memory/2026-04-15.md:359-361 [score=0.828 recalls=0 avg=0.620 source=memory/2026-04-16.md:108-110]

## Promoted From Short-Term Memory (2026-04-24)

<!-- openclaw-memory-promotion:memory:memory/2026-04-17.md:409:411 -->
- - Candidate: Possible Lasting Truths: 2026-04-06 Session Notes: `unsloth studio -H 127.0.0.1 -p 8888`; or activate env first: `source /Users/conanssam-m4/.unsloth/studio/unsloth_studio/bin/activate`; PPT/tutorial work created earlier in `~/Downloads/openclaw-lmstudio-gemma4-tutorial` includin - confidence: 0.62 - evidence: memory/2026-04-15.md:359-361 [score=0.851 recalls=0 avg=0.620 source=memory/2026-04-17.md:213-215]
<!-- openclaw-memory-promotion:memory:memory/2026-04-17.md:420:420 -->
- **문제:** 코난쌤이 Opus 4.7 리뷰 포스트의 이미지 배치가 여전히 틀리다고 지적. 이미지 타이틀을 잘 보라고 요청. [score=0.851 recalls=0 avg=0.620 source=memory/2026-04-17.md:420-420]
<!-- openclaw-memory-promotion:memory:memory/2026-04-17.md:422:422 -->
- **발견된 치명적 오류 (CDN 캡션 vs 파일명 불일치):** [score=0.851 recalls=0 avg=0.620 source=memory/2026-04-17.md:422-422]

## 블로그 글의 오픈클로 책 링크 표준 (2026-05-02)

다음 블로그 글에서 오픈클로 책을 소개하거나 구매 링크를 넣을 때는 아래 기준을 기본으로 적용한다.

- 책 제목 표기: **《이게 되네? 오픈클로 미친 활용법 50제》**
- 구매 링크 표준: <https://www.yes24.com/product/goods/185166276>
- 기존에 쓰던 골든래빗 도서 페이지나 교보문고 링크보다 Yes24 구매 링크를 우선 사용한다.
- 블로그 본문에서 책을 소개할 때 링크 텍스트도 가능하면 실제 책 제목으로 건다.

## Threads 업로드 역할 분담 메모 (2026-05-02)

- 블로그봇이 Threads 웹 업로드를 직접 하려다가 로그인/세션 문제로 막히면, 코난쌤 지시에 따라 **아가사(Agasa)에게 업로드를 부탁하는 방식**을 우선 사용한다.
- 이때 단순 `sessions_send`가 아니라 **`sessions_spawn`으로 아가사 작업 세션을 만들고 완료 결과까지 확인**한다.
- 사진/원고/순서를 정리해서 Agasa 세션에 전달하면 된다.
- 책 홍보 Threads 작성 시 책 제목은 **《이게 되네? 오픈클로 미친 활용법 50제》**, 구매 링크는 <https://www.yes24.com/product/goods/185166276> 를 기본으로 사용한다.

## 블로그 문체: 뉴스레터 인터뷰형 (2026-05-03)

코난쌤이 `josh-newsletter-style-blog-guide.md` 기반 문체를 앞으로 **뉴스레터 인터뷰형**이라고 부르기로 함. `조쉬`라는 이름은 빼고 더 범용적인 스타일명으로 저장한다.

### 호출어
- `뉴스레터 인터뷰형으로`
- `인터뷰 뉴스레터 톤으로`
- `Q&A 뉴스레터 느낌으로`

### 핵심 정의
사람·사건·숫자·장면으로 시작하고, 독자가 실제로 궁금해할 질문을 Q&A처럼 던지며 풀어가는 블로그 문체. 친근한 존댓말을 쓰되 가볍지 않게, 실제 발언·자막·사례·이미지 캡션을 증거처럼 배치한다. 마지막에는 단순 요약보다 독자가 가져갈 실전 메시지를 남긴다.

### 적용 원칙
- 본문에 `조쉬`, `뉴스레터 인터뷰형`, `이 스타일` 같은 메타표현은 쓰지 않는다.
- 인터뷰·방송·사례·트렌드 글에 특히 잘 맞는다.
- 영상/인터뷰 기반 글은 가능하면 원본 자막·발언을 짧게 발췌하고 시간대 또는 출처를 붙여 기록성을 높인다.
- 이미지 캡션은 장식 설명이 아니라, 장면이 말해주는 의미를 짧게 설명한다.


## 유튜브 영상 + 뉴스레터 인터뷰형 블로그 작업 원칙 (2026-05-03)

코난쌤이 앞으로 유튜브 영상 기반 블로그를 **뉴스레터 인터뷰형**으로 만들 때, 직전 작업 방식이 좋았다고 승인함. 이 유형은 다음 흐름을 기본값으로 삼는다.

- 유튜브 영상은 단순 요약하지 말고, 핵심 장면·발언·숫자·맥락을 먼저 뽑는다.
- 글은 독자가 궁금해할 질문을 중심으로 Q&A처럼 전개한다.
- 실제 자막/발언/화면 장면을 근거처럼 짧게 배치하고, 필요하면 시간대나 장면 설명을 붙인다.
- 이미지나 스크린샷은 장식이 아니라 “이 장면이 무엇을 보여주는지”를 캡션으로 설명한다.
- 본문에는 `뉴스레터 인터뷰형`, `이 스타일로` 같은 메타표현을 쓰지 않는다. 독자가 보기에는 자연스러운 인터뷰형 콘텐츠여야 한다.
- 마무리는 단순 요약보다 코난쌤 독자가 가져갈 실전 메시지/시사점으로 닫는다.

## Promoted From Short-Term Memory (2026-05-04)

<!-- openclaw-memory-promotion:memory:memory/2026-04-26.md:5:5 -->
- 리서치봇이 "이전 송신은 Codex 사용량 한도로 실패"라며 같은 요청 재전송함. 확인해보니 두 포스트 모두 이미 작성·커밋·배포 완료 상태였음. [score=0.882 recalls=0 avg=0.620 source=memory/2026-04-26.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-04-26.md:21:21 -->
- 본문 텍스트 위주. 메르체 스타일이라 텍스트 밀도가 강점이긴 한데, 다음 GitHub 트렌딩 포스팅 때는 레포 README 헤더 이미지나 카피 캡처 추가하면 SNS 공유 시 OG 카드 풍성해질 듯. [score=0.882 recalls=0 avg=0.620 source=memory/2026-04-26.md:21-21]
