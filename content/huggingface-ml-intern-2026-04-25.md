---
title: "Hugging Face가 공개한 'ML Intern' — 논문 읽고 모델 학습/배포까지 하는 오픈소스 AI 엔지니어"
date: 2026-04-25
tags:
  - HuggingFace
  - AIAgent
  - 오픈소스
  - smolagents
  - MLOps
  - Claude
description: "허깅페이스가 공개한 ml-intern 레포 분석. CLI에서 'fine-tune llama on my dataset' 한 줄로 논문 검색→데이터셋 준비→학습 잡 실행→HF 허브 배포까지 자동화하는 오픈소스 ML 엔지니어 에이전트의 구조와 의의."
aliases:
  - huggingface-ml-intern-2026-04-25/index
---

허깅페이스가 [ml-intern](https://github.com/huggingface/ml-intern) 레포를 공개했다. 논문 읽고, 데이터셋 준비하고, 모델 학습시키고, 허브에 배포하는 흐름을 자동으로 처리하는 오픈소스 ML 엔지니어 에이전트다. 공개 6개월 만에 별 5,500개, 포크 485개를 찍었다.

![smolagents 로고](images/huggingface-ml-intern-2026-04-25/smolagents-logo.webp)

## 한 줄 요약

```bash
ml-intern "fine-tune llama on my dataset"
```

이 한 줄이면 끝이다. 헤드리스 모드에서는 자동 승인까지 들어간다. 인터랙티브 모드면 채팅 세션에서 단계별로 확인하며 진행한다.

레포 설명을 그대로 옮기면 이렇다.

> An ML intern that autonomously researches, writes, and ships good quality ML related code using the Hugging Face ecosystem — with deep access to docs, papers, datasets, and cloud compute.

키워드는 셋이다. HF 생태계 깊게 통합, 클라우드 컴퓨트 직접 호출, 처음부터 끝까지 배포까지.

## 설치와 사용

```bash
git clone git@github.com:huggingface/ml-intern.git
cd ml-intern
uv sync
uv tool install -e .
```

설정은 `.env`에 토큰 3개를 넣는다.

```bash
ANTHROPIC_API_KEY=<your-anthropic-api-key>
HF_TOKEN=<your-hugging-face-token>
GITHUB_TOKEN=<github-personal-access-token>
```

`HF_TOKEN`이 없으면 첫 실행 때 CLI가 페이스트 프롬프트로 받아준다.

기본 모델은 `bedrock/us.anthropic.claude-opus-4-6-v1`. 옵션으로 다른 모델로 바꿀 수도 있다.

```bash
ml-intern --model anthropic/claude-opus-4-6 "your prompt"
ml-intern --max-iterations 100 "your prompt"
```

## 아키텍처 — 6개의 도구 그룹

ml-intern은 LiteLLM 위에 얹은 에이전트 루프다. `submission_loop → handlers.run_agent → 에이전트 루프(최대 300 iteration)`의 단순 구조이고, 핵심은 ToolRouter가 가진 6개 그룹이다.

```
ToolRouter
  ├─ HF docs & research          (papers_tool, research_tool, docs_tools)
  ├─ HF repos / datasets / jobs  (hf_repo_files_tool, dataset_tools, jobs_tool, ...)
  ├─ GitHub code search          (github_find_examples, github_list_repos, github_read_file)
  ├─ Sandbox & local tools       (sandbox_tool, sandbox_client, local_tools)
  ├─ Planning                    (plan_tool)
  └─ MCP server tools            (외부 MCP 서버, 기본 hf-mcp-server)
```

이 6개 그룹의 조합이 핵심이다. "논문 찾고 → 코드 예시 검색 → 데이터셋 가져오고 → 샌드박스에서 시범 실행 → 잘 되면 HF Jobs에 학습 잡 던지고 → 결과를 다시 허브에 푸시" — 이 흐름을 한 에이전트가 한 컨텍스트에서 처리한다.

### Context Manager — 170k 토큰에서 자동 압축

긴 작업은 컨텍스트가 터진다. ml-intern의 `ContextManager`는 메시지 히스토리(litellm.Message[])를 관리하면서 170k 토큰 도달 시 자동 압축(compaction)을 돌리고, 세션 자체를 HF 데이터셋(`smolagents/ml-intern-sessions`)으로 업로드한다.

자동 압축은 Claude Code의 `/compact`와 같은 발상이다. 작업 내용을 요약해서 컨텍스트를 줄이고 작업을 계속한다.

### Doom Loop Detector

긴 에이전트 루프에서 가장 흔한 실패 모드는 같은 도구를 같은 인자로 반복 호출하는 무한 루프다. ml-intern은 이걸 명시적으로 잡는 `Doom Loop Detector`를 둔다. 반복되는 tool call 패턴을 감지하면 corrective prompt를 LLM 컨텍스트에 주입한다.

이건 실전 운영에서 꼭 필요하다. 단순 max-iteration 컷오프와 달리 반복 패턴을 감지하는 순간 모델한테 "너 같은 거 반복하고 있어, 다른 접근 시도해"라고 알려주는 구조다.

## 에이전틱 루프 흐름

```
User Message
  ↓
[Add to ContextManager]
  ↓
Iteration Loop (max 300):
  1. litellm.acompletion()
  2. Has tool_calls? → No → Done
  3. Doom loop check
  4. For each tool_call:
       • 승인 필요? → 사용자 컨펌 대기
       • ToolRouter.execute_tool()
       • 결과를 ContextManager에 추가
  5. Repeat
```

승인이 필요한 경우는 HF Jobs 실행, 샌드박스 명령, 파괴적 작업이다. yolo mode가 아닌 한 사용자 컨펌을 받는다.

## 16개의 이벤트로 외부 통신

에이전트는 `event_queue`로 16개 이벤트를 emit한다. 프론트엔드/CLI가 이걸 듣고 UI를 업데이트하는 구조다.

```
processing, ready, assistant_chunk, assistant_message, assistant_stream_end,
tool_call, tool_output, tool_log, tool_state_change, approval_required,
turn_complete, error, interrupted, compacted, undo_complete, shutdown
```

UI 측면에서 중요한 건 셋이다. `streaming chunk`가 별도 이벤트라서 Claude 스타일 토큰 스트리밍이 가능하고, `approval_required`로 사용자 컨펌 시점을 명확히 분리하며, `compacted`/`undo_complete`로 자동 압축이나 undo가 발생했음을 외부에 알린다.

## 도구 추가하는 법

새 빌트인 툴은 `agent/core/tools.py`에 ToolSpec 한 개 추가하면 끝이다.

```python
def create_builtin_tools() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="your_tool",
            description="What your tool does",
            parameters={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "..."}
                },
                "required": ["param"]
            },
            handler=your_async_handler
        ),
    ]
```

MCP 서버 추가는 `configs/main_agent_config.json` 한 곳에서 한다.

```json
{
  "model_name": "anthropic/claude-sonnet-4-5-20250929",
  "mcpServers": {
    "your-server-name": {
      "transport": "http",
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer ${YOUR_TOKEN}" }
    }
  }
}
```

`${YOUR_TOKEN}`은 `.env`에서 자동 치환된다.

## REVIEW.md — 셀프 호스팅 AI 코드 리뷰 룰

이 레포에서 가장 흥미로운 건 본체보다도 `REVIEW.md`다. `claude` 봇이 PR을 리뷰할 때 따라야 할 룰을 명문화해놓은 파일이다. 핵심 규칙은 이렇다.

- P0 / P1 / P2 세 단계 심각도
- 기본 편향은 "rigor, not speed". 작은 메인테이너 팀이 외부 PR을 받기 때문이다
- P0는 절대 양보하지 않는다. 컨트리뷰터가 정중히 푸시백해도 근거 없으면 그대로 유지
- P1 발견은 최대 3개로 캡. 핵심에 집중하라는 룰
- 이미 Claude가 리뷰한 PR이면 새 P1을 올리지 않는다 (재리뷰 수렴)
- 모든 finding은 `file:line` 인용이 필수다 (검증 바)
- 요약은 `2 P0, 3 P1` / `Verdict: changes requested` 한 줄로 시작한다

대부분의 회사에서 AI 코드 리뷰가 시끄러워지는 이유는 "P1을 끝없이 던지기 때문"이다. P1 캡 3개가 그 답이다. 신호 대 잡음비를 강제로 끌어올린다.

## 의의 — Hugging Face가 그리는 "에이전트 SDK"

ml-intern을 단순한 자동화 툴로 보면 평범하다. 하지만 몇 가지 관점에서는 의미가 있다.

1. HF가 직접 보여주는 Reference Architecture. ToolRouter 6개 그룹, ContextManager의 170k 압축, Doom Loop Detector 같은 패턴은 다른 ML 에이전트도 그대로 가져다 쓸 청사진이다.

2. HF MCP 서버를 일급 클라이언트로 사용. `https://huggingface.co/mcp?login` — 허브 자체가 MCP로 노출됐고, ml-intern은 이걸 첫 번째 시민으로 쓴다. 다른 도구도 이 패턴을 따라야 한다는 신호다.

3. 세션을 데이터셋으로 업로드. 모든 세션 로그가 `smolagents/ml-intern-sessions` 데이터셋에 자동 적재된다. 에이전트 행동 데이터 자체가 다음 모델 학습 자산이 된다는 발상이다.

4. "AI가 ML 모델을 ship한다"는 명제의 실증. PR 리뷰, 학습 잡 실행, 모델 푸시까지 한 루프 안에서 처리한다. 라벨러, 데이터엔지니어, MLE를 한 에이전트가 흉내 내는 첫 본격 사례다.

## 정리 — 따라가야 할 것

- 에이전트 루프의 표준 컴포넌트가 보인다: 컨텍스트 압축, Doom Loop Detector, Approval Gate, Event Queue
- MCP를 외부 도구 표준으로. 빌트인 툴 외에는 다 MCP로 빼는 방향
- 세션을 자산으로. 학습·추론·운영 데이터의 루프를 닫는 설계
- AI 리뷰 룰 명문화. REVIEW.md 같은 파일이 앞으로 표준이 될 가능성

레포 자체가 잘 정돈된 참고 구현(reference implementation)이라 직접 클론해서 코드를 따라가 보는 게 가장 빠르다.

## 링크

- 레포: <https://github.com/huggingface/ml-intern>
- 메인 설정: `configs/main_agent_config.json`
- 핵심 코드: `agent/core/agent_loop.py`, `agent/core/doom_loop.py`, `agent/core/session.py`
- 리뷰 룰: [REVIEW.md](https://github.com/huggingface/ml-intern/blob/main/REVIEW.md)
- 세션 데이터셋: <https://huggingface.co/datasets/smolagents/ml-intern-sessions>

---

*작성: 2026-04-25 · 별 5,500 / 포크 485 / Python 기반 / 라이선스 미지정 (확인 필요).*
