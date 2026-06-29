---
title: "로컬 코딩 에이전트, 이제 취미가 아니라 백업 전략이다"
slug: "local-coding-agents-open-weight-2026-06-29"
date: 2026-06-29
tags:
  - AI에이전트
  - 코딩에이전트
  - 로컬LLM
  - Ollama
  - QwenCode
  - Codex
  - ClaudeCode
  - 오픈웨이트모델
description: "Sebastian Raschka의 Using Local Coding Agents를 바탕으로, 로컬 LLM과 코딩 에이전트 하네스를 실전에서 어떻게 조합하고 평가해야 하는지 정리했다."
aliases:
  - local-coding-agents-open-weight-2026-06-29/index
draft: false
cover: images/local-coding-agents-open-weight-2026-06-29/hero-local-stack.png
---

클라우드 코딩 에이전트가 너무 좋아졌다. Codex도, Claude Code도 이제는 하루 업무의 기본 도구가 됐다. 그런데 바로 그래서 이상한 질문이 다시 중요해진다. **이걸 전부 내 컴퓨터 안에서 돌릴 수는 없을까?**

Sebastian Raschka가 쓴 [Using Local Coding Agents](https://magazine.sebastianraschka.com/p/using-local-coding-agents)는 그 질문에 대한 꽤 현실적인 답이다. 단순히 "Ollama 설치하세요" 수준이 아니다. 로컬 모델, 추론 서버, 코딩 에이전트 하네스, 권한 모델, 벤치마크, 토큰 비용까지 한 번에 묶어서 본다.

핵심은 이거다. 로컬 코딩 에이전트는 Claude Code나 Codex를 당장 대체하는 마법이 아니다. 하지만 **비용·프라이버시·재현성·오프라인 작업을 위한 강력한 보조 엔진**으로는 이미 충분히 진지해졌다.

![로컬 코딩 에이전트 스택: 로컬 모델을 추론 서버로 띄우고, 그 위에 코딩 에이전트 하네스를 연결한다](/images/local-coding-agents-open-weight-2026-06-29/hero-local-stack.png)

## 먼저 구분해야 한다: 모델과 하네스는 다르다

코딩 에이전트를 이야기할 때 자주 섞이는 두 층이 있다.

첫째는 **LLM**이다. Qwen3.6, North Mini Code, Gemma 같은 모델이 여기 들어간다. 코드를 이해하고, 계획하고, 패치를 제안하는 두뇌다.

둘째는 **하네스(harness)**다. Codex CLI, Claude Code, Qwen-Code, Cline 같은 도구가 여기 들어간다. 파일을 읽고, 수정하고, 명령을 실행하고, 테스트를 돌리고, 사용자의 승인을 받는 작업 환경이다.

이 둘은 별개다. 같은 Qwen 모델을 Qwen-Code에 붙일 수도 있고, Codex CLI에 붙일 수도 있고, Claude Code에 우회 연결할 수도 있다. 그래서 좋은 로컬 에이전트 세팅은 "어떤 모델이 제일 똑똑한가"만으로 끝나지 않는다.

> 모델은 엔진이고, 하네스는 운전석이다. 엔진이 좋아도 운전석이 이상하면 사고가 난다.

## 왜 굳이 로컬인가

Raschka도 본인은 여전히 Codex와 Claude Code를 주력으로 쓴다고 말한다. 나도 이 판단이 솔직해서 좋았다. 로컬 스택은 아직 모든 면에서 상용 클라우드 에이전트를 이긴다고 말하기 어렵다.

그런데 로컬에는 클라우드가 쉽게 못 주는 장점이 있다.

- **비용 예측 가능성**: 하드웨어가 있으면 추가 토큰 비용이 거의 없다.
- **프라이버시**: 영수증, 내부 코드, 개인 문서 같은 민감한 자료를 외부 API로 보내지 않아도 된다.
- **재현성**: 모델이 갑자기 GPT 5.4에서 5.5로 바뀌며 기존 워크플로우가 깨지는 일을 줄일 수 있다.
- **오프라인 작업**: 비행기, 산속, 인터넷이 불안정한 환경에서도 쓸 수 있다.
- **통제감**: 하네스와 설정을 직접 감사하고 바꿀 수 있다.

여기서 중요한 건 "무료"가 아니다. 35B급 모델을 제대로 돌리려면 30~40GB RAM이 필요하고, 전기도 쓰고, 세팅 시간도 든다. 진짜 장점은 **내가 통제하는 실행 환경**이라는 점이다.

## 현재 가장 현실적인 조합: Ollama + Qwen3.6 + Qwen-Code

글에서 기본 조합으로 제시하는 건 Ollama 위에 Qwen3.6 35B-A3B를 올리고, Qwen-Code를 하네스로 쓰는 방식이다.

Ollama는 로컬 모델을 OpenAI 호환 API처럼 띄워준다. macOS Apple Silicon이면 `qwen3.6:35b-mlx`처럼 MLX 최적화 버전을 쓰는 게 좋고, Linux라면 일반 `qwen3.6:35b`를 쓰면 된다.

Qwen-Code를 쓰는 이유도 명확하다.

1. Codex CLI처럼 오픈소스다.
2. Qwen 계열 모델이 Qwen-Code 하네스에 맞춰 최적화됐을 가능성이 높다.
3. Codex와 Qwen-Code를 같은 머신에서 나란히 띄워두고 비교하기 좋다.

![Qwen 모델은 특정 하네스에서 더 잘 작동할 수 있다. 모델 성능은 하네스와 분리해서 보면 안 된다](/images/local-coding-agents-open-weight-2026-06-29/harness-benchmark-qwen.png)

여기서 재미있는 포인트가 나온다. 로컬 모델 성능은 모델 자체만의 문제가 아니다. **어떤 하네스가 어떤 방식으로 컨텍스트를 주고, 도구 호출을 강제하고, 실패를 복구하느냐**가 결과를 크게 바꾼다.

## 작은 모델은 빠르지만, 에이전트가 되기엔 부족할 수 있다

로컬 모델을 고를 때 가장 먼저 보는 건 속도다. Raschka는 긴 컨텍스트에서 초당 토큰 수와 메모리 사용량을 확인한다. 기준은 대략 이렇다.

> 20~30 tokens/sec 이상이면 로컬 에이전트 작업에 꽤 쓸 만하다.

Qwen3.6 35B-A3B와 North Mini Code는 50k 컨텍스트에서도 약 30~40 tok/sec 수준을 보여준다. 이 정도면 답답하지 않다. 문제는 속도만으로는 부족하다는 점이다.

![긴 컨텍스트에서 Qwen3.6과 North Mini Code는 로컬 에이전트 작업에 쓸 만한 속도와 메모리 사용량을 보인다](/images/local-coding-agents-open-weight-2026-06-29/speed-comparison.png)

작은 모델은 빠르다. Gemma 4 E2B 같은 모델은 메모리도 적게 먹는다. 하지만 도구 사용 판단에서 쉽게 무너진다. 파일을 먼저 읽어야 할 상황에서 질문을 하거나, 수정하지 말아야 할 파일을 건드리거나, JSON 툴콜을 깨뜨린다.

코딩 에이전트에서 중요한 건 단순 코드 생성이 아니다.

- 지금 파일을 읽어야 하는가?
- 바로 수정해도 되는가?
- 셸 명령은 안전한가?
- 실패하면 어떤 증거를 다시 봐야 하는가?
- 테스트가 통과해도 근본 원인을 고쳤는가?

이 판단을 못 하면 모델이 아무리 빠르게 답해도 에이전트로는 불안하다.

![Qwen3.6은 동급 로컬 모델 중 강한 편이다. 하지만 벤치마크 숫자만으로 에이전트 품질을 판단하면 안 된다](/images/local-coding-agents-open-weight-2026-06-29/qwen36-cohere-benchmark.png)

## 설치 전에 반드시 봐야 할 것: 하네스 감사

이 글에서 가장 실전적인 부분은 설치법보다 **감사(audit)**다.

코딩 에이전트는 그냥 챗봇이 아니다. 로컬 파일을 읽고, 코드를 고치고, 명령을 실행할 수 있다. 그러면 설치 전에 최소한 이런 걸 확인해야 한다.

- 설치 스크립트와 패키지 lifecycle hook
- 셸 명령 실행 경로
- 파일 읽기/쓰기 경계
- 환경변수와 시크릿 상속 방식
- MCP, 플러그인, 확장 기능
- 네트워크 호출과 텔레메트리
- 자동 업데이트 방식
- 터미널 escape/output 처리

![새 코딩 에이전트 하네스를 설치하기 전에 확인해야 할 실전 감사 체크리스트](/images/local-coding-agents-open-weight-2026-06-29/audit-checklist.png)

Raschka의 Qwen-Code 감사 요약에서 눈에 띄는 건 데이터 유출 가능성이다. 로컬 Ollama를 쓰더라도 Qwen-Code가 사용 통계나 텔레메트리를 Alibaba/Aliyun 쪽으로 보낼 수 있다는 점이다. 프롬프트 전체가 나간다는 뜻은 아니지만, 세션 ID, 모델 정보, 도구 메타데이터, 로컬 base URL 같은 정보가 외부로 나갈 수 있다.

이건 Qwen-Code만의 문제는 아니다. Codex, Claude Code, Cline도 비슷한 텔레메트리 기본값을 가질 수 있다. 차이는 오픈소스 하네스는 그 경로를 직접 확인하고 끌 수 있다는 점이다.

글에서 제안하는 방어 설정은 대략 이런 방향이다.

```json
{
  "privacy": { "usageStatisticsEnabled": false },
  "telemetry": { "enabled": false, "logPrompts": false },
  "outboundCorrelation": { "propagateTraceContext": false },
  "general": { "enableAutoUpdate": false },
  "tools": {
    "approvalMode": "default",
    "sandbox": true
  },
  "mcpServers": {},
  "hooks": { "disableAllHooks": true }
}
```

핵심은 단순하다. 처음 써보는 에이전트는 **샌드박스, 승인 모드, 텔레메트리 off, 자동 업데이트 off**로 시작하는 게 낫다.

## 에이전트 평가는 "벤치마크 점수"보다 내 작업 샘플이 중요하다

모델을 띄웠고, 하네스를 붙였고, 보안 설정도 했다. 그다음 질문은 이거다.

**그래서 내 일에 쓸 수 있나?**

Raschka는 작은 agent problem pack으로 Qwen-Code 안에서 여러 모델을 테스트한다. 결과는 흥미롭다. Qwen3.6과 North Mini Code는 5개 중 4개를 풀고, Gemma 4 E2B는 많이 실패한다.

![Qwen-Code 안에서의 작은 에이전트 작업 성공률. 빠른 모델보다 도구 사용 판단이 되는 모델이 중요하다](/images/local-coding-agents-open-weight-2026-06-29/agent-capability-qwen-code.png)

하지만 더 중요한 메시지는 따로 있다. 범용 벤치마크는 참고 자료일 뿐이다. 진짜로는 내가 자주 하는 작업 5~10개를 뽑아야 한다.

예를 들면 이런 식이다.

- 작은 버그를 재현하고 테스트까지 추가하기
- 기존 코드 스타일을 유지하며 함수 하나 리팩터링하기
- 문서와 코드가 어긋난 부분 찾기
- 셸 명령 injection 위험 검토하기
- 실패한 테스트 로그를 보고 최소 수정안 만들기

이걸 같은 하네스와 모델 조합으로 반복해보면 감이 온다. 어떤 모델은 코드는 잘 쓰는데 파일 선택을 못 하고, 어떤 하네스는 성공률은 높은데 토큰을 너무 많이 태운다.

## 의외의 결론: Codex가 범용 하네스로 꽤 좋다

글의 후반부에서 재미있는 반전이 나온다. Qwen3.6은 Qwen-Code용으로 좋아 보이지만, Codex CLI에 붙였을 때 더 좋은 결과를 보이기도 한다.

Codex CLI는 별도 설정으로 Ollama provider를 붙일 수 있다. 예를 들어 `~/.codex/ollama.config.toml` 같은 프로필을 만들어 `codex --profile ollama`로 실행하는 방식이다.

![Codex CLI에 Ollama 프로필을 따로 만들어 로컬 모델을 붙일 수 있다](/images/local-coding-agents-open-weight-2026-06-29/codex-ollama-profile.png)

작은 실험에서는 Codex 하네스가 Qwen3.6을 더 효율적으로 굴렸다. Claude Code는 성능은 좋지만 입력 토큰을 훨씬 많이 썼다. 즉, 같은 모델이라도 하네스가 컨텍스트를 얼마나 크게 다시 넣느냐에 따라 비용과 속도가 달라진다.

![토큰 사용량은 모델보다 하네스가 좌우하는 경우가 많다. Claude Code는 입력 컨텍스트를 크게 누적하는 경향이 있다](/images/local-coding-agents-open-weight-2026-06-29/harness-token-usage.png)

이건 중요한 관찰이다.

로컬 모델을 쓰면 토큰 비용은 직접 청구되지 않는다. 그래도 토큰은 공짜가 아니다. 더 많은 입력 토큰은 더 긴 대기 시간, 더 많은 메모리, 더 큰 발열로 돌아온다. 로컬에서도 효율은 중요하다.

## Mac에서 DGX나 다른 서버 모델을 쓰는 방식

모든 걸 한 머신에서 돌릴 필요는 없다. Raschka는 Mac에서 하네스를 실행하고, DGX Spark 같은 별도 머신에서 Ollama 모델을 띄운 뒤 SSH 터널로 연결하는 방식을 소개한다.

```bash
ssh -N -L 11434:127.0.0.1:11434 user@DGX-Spark
```

이렇게 하면 Mac의 `127.0.0.1:11434`가 원격 머신의 Ollama 서버처럼 동작한다. Codex, Qwen-Code, Claude Code는 로컬 Ollama를 쓰는 것처럼 붙이면 된다.

이 구조가 마음에 든다. 메인 노트북은 가볍게 유지하고, 무거운 모델은 별도 장비에서 돌린다. 로컬의 장점과 원격 하드웨어의 장점을 섞는 방식이다.

## 그래서 지금 당장 갈아탈 만한가

내 결론은 이렇다.

**주력은 아직 Codex/Claude Code 같은 클라우드 에이전트로 두되, 로컬 코딩 에이전트 스택은 반드시 하나쯤 만들어둘 가치가 있다.**

이유는 성능 경쟁이 아니다. 백업성과 통제성 때문이다.

- 민감한 코드나 문서를 다룰 때
- API 한도나 비용이 걸릴 때
- 모델 업데이트로 기존 워크플로우가 흔들릴 때
- 특정 하네스의 동작을 직접 감사하고 싶을 때
- 오프라인 또는 내부망 환경에서 작업해야 할 때

이런 상황에서는 로컬 스택이 단순한 장난감이 아니라 실전 옵션이 된다.

다만 처음부터 완전 자율 모드로 맡기면 안 된다. 로컬이라고 안전한 게 아니다. 오히려 로컬 에이전트는 내 파일시스템에 더 가까이 붙어 있다. 첫 세팅은 이렇게 가는 게 좋다.

1. Ollama로 모델 서버를 띄운다.
2. Qwen-Code나 Codex CLI 중 하나에 붙인다.
3. 텔레메트리와 자동 업데이트를 끈다.
4. 샌드박스와 승인 모드를 켠다.
5. 내 작업 샘플 5개로 작은 평가 세트를 만든다.
6. 성공률뿐 아니라 수정 품질, 명령 안전성, 토큰 사용량을 같이 본다.

## 진짜 변화는 "로컬에서도 에이전트가 된다"는 감각이다

몇 년 전 로컬 LLM은 챗봇 흉내에 가까웠다. 짧은 질문에 답하고, 간단한 코드를 써주는 정도였다. 이제는 다르다. 35B급 오픈웨이트 모델이 긴 컨텍스트를 버티고, 하네스가 파일·명령·테스트를 연결하면서, 로컬에서도 꽤 진지한 코딩 에이전트 루프가 가능해졌다.

물론 GPT 5.5나 Opus 4.8 같은 최상위 클라우드 모델이 여전히 더 강하다. 하지만 로컬 스택의 의미는 "최고 성능"이 아니다.

**내가 통제하는 두 번째 작업대.**

그게 핵심이다. 클라우드 에이전트가 메인 작업대라면, 로컬 코딩 에이전트는 전기가 나가도, 요금제가 막혀도, 외부로 보내기 어려운 자료가 있어도 계속 돌아가는 작업대다.

그리고 코딩 에이전트 시대에는 이 두 번째 작업대가 생각보다 빨리 중요해질 수 있다.

---

원문: Sebastian Raschka, [Using Local Coding Agents](https://magazine.sebastianraschka.com/p/using-local-coding-agents)
