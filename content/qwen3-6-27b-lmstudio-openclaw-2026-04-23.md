---
title: "Qwen3.6-27B 나왔음, LM Studio + OpenClaw로 로컬에서 굴리는 방법"
description: "Qwen/Qwen3.6-27B 벤치마크 정리하고, LM Studio에 올려서 OpenClaw가 로컬 모델로 쓰게 연결하는 절차. 27B 덴스인데 Claude 4.5 Opus랑 정면 비빌 수 있는 모델임."
tags:
  - openclaw
  - lmstudio
  - qwen
  - local-llm
  - agentic
slug: qwen3-6-27b-lmstudio-openclaw-2026-04-23
---

1. Qwen에서 Qwen3.6-27B 공개. 27B 덴스 모델인데 코딩/에이전트/비전까지 다 되는 올인원임.

2. 특이점이 뭐냐. 같은 27B급 Gemma4-31B랑 비교 대상이 아니라 Claude 4.5 Opus랑 비빔. 일부 벤치마크는 오픈으로 Opus를 넘김.

3. 라이선스는 Apache 2.0. 상업 사용 가능. 가중치 그냥 다운로드됨.

4. 기본 컨텍스트 262,144 토큰이고, YaRN 스케일링 붙이면 약 101만 토큰까지 늘어남. 긴 문서/리포 단위 작업 염두에 둔 스펙임.

5. 구조는 Gated DeltaNet + Gated Attention 하이브리드. 64 레이어 중 16블록이 `3×(DeltaNet→FFN) + 1×(Attention→FFN)` 패턴. 긴 컨텍스트 비용 줄이려고 선형 어텐션 섞은 모양.

6. 비전 인코더 내장. 이미지 + 텍스트 + 비디오 입력 다 받음. VLM처럼 따로 붙일 필요 없음.

7. 멀티 토큰 프리딕션(MTP) 훈련됨. vLLM에서 speculative decoding으로 토큰/초 뽑기 좋음.

8. 코딩 벤치마크부터 봄. 숫자는 공식 리포트 기준.

| 벤치마크 | Qwen3.6-27B | Claude 4.5 Opus | Gemma4-31B |
|---|---|---|---|
| SWE-bench Verified | 77.2 | 80.9 | 52.0 |
| SWE-bench Pro | 53.5 | 57.1 | 35.7 |
| SWE-bench Multilingual | 71.3 | 77.5 | 51.7 |
| Terminal-Bench 2.0 | 59.3 | 59.3 | 42.9 |
| SkillsBench Avg5 | 48.2 | 45.3 | 23.6 |
| QwenWebBench | 1487 | 1536 | 1197 |
| LiveCodeBench v6 | 83.9 | 84.8 | 80.0 |

9. SWE-bench 계열은 Opus보다 3~4점 낮지만 Gemma4-31B는 완전히 밀어버림. Terminal-Bench 2.0은 Opus랑 59.3 동률. SkillsBench Avg5는 48.2로 오히려 Opus(45.3) 앞섬.

10. 지식/추론 벤치도 Opus 가까이 붙음.

| 벤치마크 | Qwen3.6-27B | Claude 4.5 Opus |
|---|---|---|
| MMLU-Pro | 86.2 | 89.5 |
| MMLU-Redux | 93.5 | 95.6 |
| C-Eval | 91.4 | 92.2 |
| GPQA Diamond | 87.8 | 87.0 |
| AIME26 | 94.1 | 95.1 |
| HMMT Feb 25 | 93.8 | 92.9 |
| IMOAnswerBench | 80.8 | 84.0 |

11. GPQA Diamond 87.8로 Opus(87.0) 넘김. 수학 올림피아드 HMMT Feb 25도 93.8 > 92.9로 오히려 앞.

12. 비전 언어 벤치도 쎔. 27B 덴스 모델에서 이 점수 찍은 게 비정상임.

| 벤치마크 | Qwen3.6-27B | Claude 4.5 Opus | Gemma4-31B |
|---|---|---|---|
| MMMU | 82.9 | 80.7 | 80.4 |
| MMMU-Pro | 75.8 | 70.6 | 76.9 |
| RealWorldQA | 84.1 | 77.0 | 72.3 |
| MathVista mini | 87.4 | -- | 79.3 |
| VideoMME(w sub.) | 87.7 | 77.7 | -- |
| V* (Visual Agent) | 94.7 | 67.0 | -- |
| AndroidWorld | 70.3 | -- | -- |

13. V* 에이전트 벤치마크 94.7 vs Opus 67.0. 그냥 압도적임. AndroidWorld 70.3까지 나오면 모바일 UI 에이전트 용도로 직결됨.

14. 근데 한계도 있음. HLE 24.0, SuperGPQA 66.0, SimpleVQA 56.1. 이쪽 벤치는 Qwen3.5-397B MoE(28.7/70.4/67.1)랑 Opus가 더 나음.

15. 정리하면, Opus급 성능을 로컬에서 돌릴 수 있는 가장 가벼운 선택지임. 토큰 무제한에 프라이버시 붙음.

16. 이제 LM Studio에 올리고 OpenClaw가 이걸 쓰게 연결함.

17. 먼저 LM Studio에서 모델 다운로드. GGUF 양자화 버전이 74종 올라와 있음. M1 Max 64GB 기준 Q4_K_M 또는 Q5_K_M 추천. 32GB면 Q3/Q4S 써야 들어감.

18. LM Studio 실행해서 Developer 탭으로 감. "Start server" 토글. 기본 포트 1234.

19. 또는 CLI로 띄움.

```bash
lms server start --port 1234
```

20. 컨텍스트 길이는 모델 로드할 때 Developer 탭에서 조정. 중요: 50,000 토큰 이상으로 잡음. OpenClaw 툴/스킬이 컨텍스트 엄청 먹음.

21. 서버 떴는지 확인.

```bash
curl http://localhost:1234/v1/models
```

22. 이제 OpenClaw 쪽. 신규 설치면 `openclaw onboard` 한 방으로 끝남.

```bash
openclaw onboard
```

23. 인터랙티브에서 "Model provider"에 LM Studio 선택하고 URL(`http://localhost:1234/v1`)과 모델 ID 입력.

24. 비대화식으로 한 번에 박고 싶으면 이 명령.

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio \
  --custom-base-url http://localhost:1234/v1 \
  --lmstudio-api-key "lmstudio" \
  --custom-model-id qwen/qwen3.6-27b
```

25. LM Studio는 API 키 검증 안 함. 값은 아무거나 넣어도 됨. `lmstudio` 그대로 둬도 됨.

26. 이미 설치된 OpenClaw에 프로바이더만 추가하려면 설정 파일 건드림.

```js
// ~/.openclaw/openclaw.json
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/qwen3.6-27b" },
      models: {
        "lmstudio/qwen3.6-27b": { alias: "Qwen27B" }
      }
    }
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [{
          id: "qwen3.6-27b",
          name: "Qwen 3.6 27B",
          reasoning: true,
          input: ["text", "image"],
          cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
          contextWindow: 196608,
          maxTokens: 8192
        }]
      }
    }
  }
}
```

27. `reasoning: true`로 두면 Qwen3.6의 thinking 모드 활성화됨. 코드 작업은 켜두는 게 성능 좋음.

28. `input: ["text", "image"]` 이미지 입력 가능 표시. 스크린샷 붙이고 디버깅 시키는 용도.

29. `api: "openai-responses"` 중요. LM Studio 0.3.29부터 `/v1/responses` 엔드포인트 지원. OpenClaw 최신은 이쪽을 기본으로 씀.

30. 하이브리드 운영도 가능함. 평소엔 로컬 Qwen, 복잡한 작업만 Opus로 넘기는 구성.

```js
{
  agents: {
    defaults: {
      model: {
        primary: "lmstudio/qwen3.6-27b",
        fallbacks: ["anthropic/claude-opus-4-6"]
      }
    }
  }
}
```

31. 메모리 검색(임베딩)도 로컬로 돌리고 싶으면 추가 명령.

```bash
openclaw config set agents.defaults.memorySearch.provider lmstudio
openclaw gateway restart
```

32. LM Studio에서 임베딩 모델 따로 로드해야 함. `nomic-embed-text-v1.5` 같은 거 적당.

33. 서빙 파라미터 팁. Thinking 모드 코딩 작업은 `temperature=0.6`, `top_p=0.95`, `top_k=20`. 에이전트 루프 돌릴 땐 `max_tokens=81920`까지 허용.

34. 끊김 없이 쓰려면 LM Studio에서 컨텍스트 196K 이상 잡고, `mlock` 켜서 메모리 상주시킴. 토큰 처음 뽑을 때 로딩 딜레이 사라짐.

35. LM Link로 분리 구성도 가능함. 모델은 데스크톱 GPU에서 돌리고, OpenClaw는 노트북에서 붙어서 씀.

36. 이미 돌려봤을 때 체감. 27B BF16 풀 로드는 VRAM 54GB 먹음. Q4_K_M은 16GB, Q5_K_M 20GB. 맥 M1 Max 64GB면 Q5_K_M + 128K 컨텍스트 무리 없음.

37. 단점 한 줄. Opus에 비해 SWE-bench에서 3~4점 차이. 진짜 까다로운 리팩토링은 Opus가 아직 앞. 근데 토큰 공짜에 프라이버시 확보가 더 크면 이쪽이 맞음.

38. 요약. Qwen3.6-27B는 오픈 27B 덴스로 Opus 성능에 가장 가깝게 붙은 모델. LM Studio가 GGUF/MLX 다 돌리고 OpenAI 호환 서버도 띄워줘서 OpenClaw가 네이티브 프로바이더로 바로 붙음. Claude API 비용이 부담스럽거나 사내 데이터 못 내보내는 상황이면 지금 로컬로 내려받아 테스트해볼 만함.

39. 레퍼런스.

- [Qwen3.6-27B 모델 카드 (Hugging Face)](https://huggingface.co/Qwen/Qwen3.6-27B)
- [LM Studio - Local LLM API Server](https://lmstudio.ai/docs/developer/core/server)
- [LM Studio × OpenClaw 통합 가이드](https://lmstudio.ai/docs/integrations/openclaw)
- [OpenClaw Docs - Local Models](https://docs.openclaw.ai/gateway/local-models)
