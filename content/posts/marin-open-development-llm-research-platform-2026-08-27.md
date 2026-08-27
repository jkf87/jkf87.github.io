---
title: "Marin 살펴보기: 모델 파일보다 모델을 만든 과정을 공개하는 LLM 연구 플랫폼"
date: 2026-08-27
draft: false
tags:
  - Marin
  - open-development
  - foundation-model
  - LLM-training
  - JAX
  - Levanter
  - agent-infra
categories:
  - AI
  - LLM
description: "Marin은 데이터 수집부터 학습, 평가, 실패 기록까지 공개하려는 LLM 연구 플랫폼이다. 설치와 lazy artifact 구조를 함께 정리했다."
aliases:
  - /posts/marin-open-development-llm-research-platform-2026-08-27
---

![코난쌤 캐릭터가 배를 타고 데이터와 모델 블록 사이를 항해하는 그림. Marin을 볼 때 중요한 건 완성된 모델 하나가 아니라, 그 모델이 만들어지는 항로 전체라는 점이다.](/images/marin-open-development-llm-research-platform-2026-08-27/hero.png)

Marin 저장소를 읽어봤습니다.

한 줄로 말하면 이겁니다. <span style="background-color: #fff59d"><strong>Marin은 모델 하나를 공개하는 프로젝트라기보다, foundation model을 만드는 과정을 코드와 기록으로 남기는 연구 플랫폼</strong></span>입니다.

요즘 오픈 모델 얘기를 하면 보통 checkpoint, benchmark score, license부터 봅니다. 물론 중요합니다. 그런데 실제로 모델을 만들려면 그 앞에 훨씬 지저분한 과정이 있습니다. 데이터를 어디서 가져왔는지, 어떻게 변환했는지, 무엇을 버렸는지, 어떤 tokenizer를 썼는지, pretraining과 posttraining을 어떻게 연결했는지, 실패한 실험은 왜 실패했는지. Marin은 이 과정을 한 저장소 안에서 보이게 만들려는 쪽에 가깝습니다.

그래서 이 글은 “Marin으로 당장 앱 하나 만들어보자”보다 “LLM 연구실에서는 모델 만드는 파이프라인을 어떻게 코드화하려고 하는가”에 가깝게 읽으시면 됩니다.

## 이 글에서 볼 내용

질문은 네 개입니다.

1. Marin은 그냥 training script 모음인가, 아니면 더 큰 연구 운영체제인가?
2. 로컬에서 설치하고 작은 TinyStories 모델을 돌리려면 뭘 해야 하나?
3. lazy artifact와 `StepRunner`는 왜 필요한가?
4. 이 저장소를 공부하면 LLM 개발의 어느 부분이 보이나?

## Marin은 research program + software platform + community입니다

README 첫 부분에서 Marin은 자신을 세 가지로 설명합니다. foundation model 연구·개발을 위한 research program, software platform, community.

관심 영역은 large language model training입니다. 범위가 넓습니다.

- data curation
- transformation
- filtering
- tokenization
- pretraining
- posttraining
- evaluation

즉 “학습 코드 있습니다” 정도가 아닙니다. 원천 데이터에서 최종 모델까지 가는 길을 최대한 남기겠다는 쪽입니다.

README에서 가장 눈에 띄는 단어는 <span style="background-color: #fff59d"><strong>open development</strong></span>입니다. Marin은 raw data부터 final model까지의 step, process, experiment, decision을 기록한다고 말합니다. 실패한 실험도 기록의 일부라고 적습니다.

이게 꽤 중요합니다. 모델 공개는 결과 공개입니다. 그런데 open development는 과정 공개입니다. 연구자가 실제로 재현하고 싶은 건 checkpoint 하나가 아니라 “왜 이 mixture를 썼는지”, “왜 이 scaling 설정을 택했는지”, “어떤 실패를 보고 다음 실험으로 갔는지”입니다.

![코난쌤 캐릭터가 문서, 필터, 데이터 블록, 서버, 성능 계기판으로 이어지는 파이프라인을 가리키는 그림. Marin의 핵심은 데이터 처리부터 학습과 평가까지 끊어진 스크립트가 아니라 하나의 실험 흐름으로 표현한다는 데 있다.](/images/marin-open-development-llm-research-platform-2026-08-27/pipeline-map.png)

현재 Marin의 큰 작업도 이 관점에서 보면 이해가 됩니다. README 기준 현재 초점은 <span style="background-color: #fff59d"><strong>5e24 model-FLOPs, 500B+ total parameter 규모의 large mixture-of-experts 모델을 scratch pretraining하고 posttraining하는 것</strong></span>입니다. 또 Delphi라는 scaling suite도 소개합니다. 3e18부터 1e23 FLOPs까지 recipe, suite, scaling law를 공개하는 흐름이고, Pythia에서 영감을 받았다고 설명합니다.

숫자만 보면 거창한데, 블로그 독자 입장에서는 이렇게 받아들이면 됩니다. Marin은 “나도 노트북에서 frontier MoE를 바로 학습하겠다”가 아닙니다. <span style="background-color: #fff59d"><strong>작은 튜토리얼부터 큰 TPU/GPU 실험까지 같은 실험 표현으로 묶으려는 시도</strong></span>입니다.

## 설치는 `uv sync`, 첫 실행은 TinyStories가 출발점입니다

설치 문서는 `docs/tutorials/installation.md`에 있습니다. 기본 요구사항은 아래 정도입니다.

- Python 3.12 이상
- `uv`
- Git
- Rust toolchain은 Rust crate를 source build할 때 필요. 기본은 pre-built wheel 사용
- macOS에서는 SentencePiece 빌드 도구로 `cmake`, `pkg-config`, `coreutils` 필요

macOS라면 먼저 이 정도를 준비합니다.

```bash
brew install cmake pkg-config coreutils
```

그리고 저장소를 받습니다.

```bash
git clone https://github.com/marin-community/marin.git
cd marin
uv venv --python 3.12
source .venv/bin/activate
uv sync --all-packages
```

GPU나 TPU 환경이면 extra를 나눠 설치합니다.

```bash
uv sync --all-packages --extra=cpu
uv sync --all-packages --extra=gpu
uv sync --all-packages --extra=tpu
```

실험 추적과 gated model/tokenizer 접근을 위해 문서에서는 W&B와 Hugging Face token도 안내합니다.

```bash
export WANDB_API_KEY=...
export HF_TOKEN=...
export MARIN_PREFIX=local_store
```

여기서 `MARIN_PREFIX`가 중요합니다. Marin이 만든 tokenized cache, checkpoint 같은 산출물이 저장되는 루트입니다. 로컬 디렉터리일 수도 있고, fsspec이 이해하는 GCS/S3 계열 경로일 수도 있습니다.

설치 확인용 첫 실행은 TinyStories tiny model입니다.

```bash
wandb offline
uv run python experiments/tutorials/train_tiny_model.py \
  --device cpu --dataset tinystories --version dev --run
```

주의할 점 하나. <span style="background-color: #fff59d"><strong>`--run`이 없으면 실제 실행이 아니라 plan만 출력합니다.</strong></span> 튜토리얼 문서가 이 부분을 명시합니다. 처음 돌렸는데 아무 일도 안 일어나는 것처럼 보이면 `--run`을 먼저 확인하면 됩니다.

실행 후에는 대략 이런 구조가 생깁니다.

```text
local_store/
  tokenized/tinystories/dev/
  checkpoints/marin-nano-tinystories/dev/
```

캐시와 checkpoint가 `MARIN_PREFIX` 아래에 쌓입니다. 이 단순한 예제가 뒤에서 설명할 lazy artifact 구조를 그대로 보여줍니다.

## 핵심 추상화는 `name@version`으로 부르는 lazy artifact입니다

Marin 문서를 읽으면서 가장 Marin다운 부분은 lazy artifact였습니다. 문서는 `docs/explanations/lazy-artifacts.md`에 있습니다.

아이디어는 단순합니다. 실험 스크립트가 실행되자마자 데이터를 다운로드하고 학습을 시작하지 않습니다. 먼저 <span style="background-color: #fff59d"><strong>`ArtifactStep[T]`라는 typed handle을 만듭니다.</strong></span> 이 handle은 “무엇을 만들 것인가”를 설명합니다. 실제 일은 나중에 `lower()`와 `StepRunner().run(...)`에서 일어납니다.

TinyStories 예시를 줄이면 이런 모양입니다.

```python
from fray.cluster import ResourceConfig
from levanter.optim import AdamConfig
from marin.execution.lazy import lower
from marin.execution.step_runner import StepRunner
from marin.experiment.data import tokenized
from marin.experiment.train import train_lm

tinystories_tokenized = tokenized(
    name="tokenized/tinystories",
    source="roneneldan/TinyStories",
    tokenizer=marin_tokenizer,
    sample_count=1000,
)

nano_tinystories_model = train_lm(
    name="checkpoints/marin-nano-tinystories",
    version="v1",
    model=llama_nano,
    optimizer=AdamConfig(learning_rate=6e-4, weight_decay=0.1),
    datasets={tinystories_tokenized: 1.0},
    batch_size=4,
    seq_len=2048,
    num_train_steps=100,
    z_loss_weight=None,
    evals=None,
    resources=ResourceConfig.with_cpu(),
)

if __name__ == "__main__":
    StepRunner().run([lower(nano_tinystories_model)])
```

여기서 중요한 건 dependency입니다. checkpoint는 tokenized dataset에 의존합니다. `lower()`는 이 handle graph를 실행 가능한 step graph로 낮춥니다. `StepRunner`는 DAG 순서대로 필요한 step만 실행합니다.

![코난쌤 캐릭터가 큐브와 노드로 된 DAG를 조립하는 그림. Marin의 lazy artifact는 실험을 즉시 실행하지 않고, name@version으로 부르는 결과물 그래프를 먼저 만든 뒤 필요한 step만 실행하게 한다.](/images/marin-open-development-llm-research-platform-2026-08-27/artifact-dag.png)

Artifact 주소는 `{MARIN_PREFIX}/{name}/{version}`입니다. 문서에서는 사람이 읽을 수 있는 `name@version` handle을 강조합니다. hash가 path에 직접 들어가는 방식이 아닙니다. 대신 fingerprint가 config drift를 감지합니다.

이 설계의 장점은 세 가지입니다.

장점은 세 가지입니다.

- 결과물 주소가 사람이 읽을 수 있습니다. `checkpoints/marin-nano-tinystories/2026.06.28` 같은 식입니다.
- 이미 성공한 step은 cache hit로 건너뜁니다. 실패한 step은 다음 실행에서 다시 시도할 수 있습니다.
- 무엇이 실험의 정체성이고 무엇이 실행 환경인지 분리합니다. 문서의 `StepContext` 설명을 보면 model architecture, optimizer, dataset mixture, token budget 같은 값은 artifact identity에 들어가고, prefix, region, resource 같은 값은 runtime choice로 분리됩니다.

이게 왜 중요하냐면, 연구 인프라에서는 “같은 실험을 다른 TPU에서 돌렸다”와 “실험 설정 자체가 바뀌었다”를 구분해야 하기 때문입니다. Marin은 이 선을 코드 구조로 강제하려고 합니다.

## `train_lm`은 학습 결정을 한곳에 모으는 접착제입니다

`lib/marin/src/marin/experiment/train.py`의 `train_lm`도 볼 만합니다. 함수가 받는 인자를 보면 Marin이 무엇을 실험 결정으로 보는지 드러납니다.

대략 이런 것들입니다.

- `model`
- `optimizer`
- `datasets`
- `batch_size`
- `seq_len`
- `num_train_steps` 또는 `num_train_epochs`
- `evals`
- `resources`
- `version`
- `init_from`

문서 주석에서 `train_lm`은 language-model training run을 `ArtifactStep[LevanterCheckpoint]`로 조립한다고 설명합니다. `datasets`는 tokenized dataset handle과 mixture weight의 mapping입니다. `evals=None`이면 평가 suite를 명시적으로 끄는 것이고, 암묵적 기본값은 없습니다.

여기서 재미있는 부분은 `resources`입니다. CPU, GPU, TPU 같은 자원 선택은 중요하지만, 그것이 항상 실험의 정체성은 아닙니다. Marin은 resource를 runtime arg로 다루고 checkpoint fingerprint에는 넣지 않는 방향을 택합니다.

이 구조는 실험 로그를 읽을 때 꽤 편합니다. “이 모델은 어떤 데이터 mixture로, 어떤 optimizer와 token budget으로 만들어졌나?”와 “어느 클러스터에서 실행됐나?”를 섞지 않게 해줍니다.

## 내부는 Marin 하나가 아니라 작은 연구 인프라 패키지 묶음입니다

저장소 구조를 보면 `lib/marin` 하나만 있는 게 아닙니다. 여러 패키지가 workspace처럼 붙어 있습니다.

| 패키지/폴더 | 역할 |
|---|---|
| `lib/marin` | lazy artifact, experiment API, data/eval/train glue |
| `lib/iris` | cluster job orchestration |
| `lib/fray` | resource config, remote dispatch |
| `lib/levanter` | JAX 기반 LLM training |
| `lib/haliax` | named array / partitioning 기반 |
| `experiments/` | 실제 실험 recipe와 튜토리얼 |
| `docs/` | 설치, 첫 실험, pipeline, report 문서 |

`docs/explanations/lm-pipeline.md`는 Marin이 보는 언어모델 파이프라인을 더 직접적으로 보여줍니다. raw source curating, web crawling, text conversion, quality classifier, filtering, deduplication, tokenization, training, evaluation이 순서대로 나옵니다.

학습은 Levanter를 사용합니다. JAX 기반이고, scalable/reproducible한 framework로 설명됩니다. Evaluation에는 EleutherAI의 `lm-evaluation-harness`가 언급됩니다. 데이터 format은 가능한 곳에서는 Dolma와 맞추고, 아니면 그 정신에 맞는 natural extension을 쓴다고 되어 있습니다.

이쯤 되면 Marin을 “pip install해서 간단히 쓰는 라이브러리”로 보면 좀 어긋납니다. 더 정확히는 <span style="background-color: #fff59d"><strong>foundation model 연구실용 운영체제에 가까운 코드베이스</strong></span>입니다. 작은 실험도 가능하지만, 설계의 방향은 대규모 실험의 기록성, 재현성, 운영성을 향하고 있습니다.

## 흥미로운 건 실패까지 남기려는 태도입니다

오픈소스 AI에서 자주 빠지는 부분이 있습니다. 성공한 모델은 공개됩니다. 예쁜 리더보드도 공개됩니다. 근데 실패한 데이터 mixture, 애매했던 preprocessing decision, 잘 안 맞았던 scaling heuristic은 잘 안 남습니다.

Marin README는 failed experiments도 record의 일부라고 말합니다. 저는 이 문장이 가장 좋았습니다.

실패 기록이 있어야 연구가 누적됩니다. 똑같은 함정을 다른 팀이 다시 밟지 않을 수 있고, 작은 모델에서 본 scaling signal이 큰 모델로 어떻게 이어졌는지도 볼 수 있습니다. Marin의 Delphi scaling suite가 흥미로운 이유도 여기에 있습니다. 3e18~1e23 FLOPs 범위의 작은 모델들을 통해 더 큰 모델을 예측하려는 시도인데, 이건 checkpoint 하나만으로는 설명되지 않습니다. recipe, run, log, decision이 같이 있어야 보입니다.

![코난쌤 캐릭터와 사람들이 지도 위에서 성공·실패 카드를 놓고 경로를 고르는 그림. Open development의 가치는 성공한 checkpoint만 남기는 게 아니라, 선택과 실패가 다음 실험의 지도가 된다는 데 있다.](/images/marin-open-development-llm-research-platform-2026-08-27/open-development.png)

Marin은 이미 8B, 32B 모델 retrospective와 training script도 연결합니다. 현재는 더 큰 MoE pretraining/posttraining으로 가고 있습니다. 이 흐름을 따라가면 “모델을 만드는 조직은 어떤 실험 기록을 남겨야 하나”라는 질문을 꽤 구체적으로 볼 수 있습니다.

## 다만 가볍게 쓰는 도구는 아닙니다

주의점도 분명합니다.

주의점도 세 가지입니다.

- Marin은 초보자용 LLM 앱 프레임워크가 아닙니다. LangChain처럼 API 몇 개 붙여서 챗봇 만드는 느낌으로 접근하면 당황할 수 있습니다. Python 3.12, `uv`, JAX, W&B, Hugging Face, GPU/TPU, GCS/S3 계열 스토리지 감각이 어느 정도 필요합니다.
- 로컬 CPU 튜토리얼은 시작점일 뿐입니다. TinyStories tiny model은 전체 구조를 이해하기 위한 smoke test에 가깝습니다. Marin이 진짜 보여주려는 건 데이터 파이프라인과 대규모 학습 운영입니다.
- lazy artifact의 `name@version` 규칙은 편하지만, 연구자가 version bump와 drift warning을 이해해야 합니다. 기존 artifact와 다른 config를 같은 name/version으로 만들면 fingerprint drift가 advisory warning으로 남고 cache를 계속 쓸 수 있습니다. 실험 문화가 같이 따라와야 안전한 구조입니다.

## 그래서 누가 보면 좋을까요

저는 세 부류에게 추천하고 싶습니다.

- 오픈 모델을 “사용”하는 단계를 넘어, 모델이 만들어지는 과정을 공부하고 싶은 분
- 데이터 curation → tokenization → pretraining → evaluation까지 이어지는 실험 파이프라인을 보고 싶은 분
- agent/harness 쪽에서 재현 가능한 실험 기록, cache, artifact identity 설계에 관심 있는 분

특히 세 번째가 생각보다 중요합니다. 요즘 agent 연구도 결국 “어떤 task, harness, verifier, rollout log로 개선했는가”를 남겨야 합니다. Marin의 lazy artifact와 open development 태도는 LLM pretraining뿐 아니라 agent 실험 인프라에도 힌트를 줍니다.

Marin을 읽고 나면 모델 공개의 기준이 조금 달라집니다. “가중치가 공개됐나?”에서 끝나지 않고, “그 가중치가 만들어진 항로도 공개됐나?”를 묻게 됩니다.

그 질문을 던지게 만드는 저장소라면, 한 번쯤 깊게 읽어볼 만합니다.

## 자주 묻는 질문

**Marin은 모델 학습 프레임워크인가요?**  
부분적으로는 맞지만, 더 넓게는 데이터 처리, 학습, 평가, 실험 기록을 묶는 foundation model 연구 플랫폼에 가깝습니다.

**노트북에서 바로 써볼 수 있나요?**  
TinyStories tiny model 튜토리얼은 CPU에서도 시작할 수 있습니다. 다만 Marin의 주된 설계는 큰 GPU/TPU 실험까지 이어지는 연구 인프라 쪽입니다.

**가장 먼저 봐야 할 문서는 뭔가요?**  
`docs/tutorials/installation.md`, `docs/tutorials/first-experiment.md`, `docs/explanations/lazy-artifacts.md` 순서가 좋습니다. 설치, 첫 실행, 실행 모델이 차례로 잡힙니다.

## 참고한 자료

- Marin GitHub README: [github.com/marin-community/marin](https://github.com/marin-community/marin)
- Installation: [`docs/tutorials/installation.md`](https://github.com/marin-community/marin/blob/main/docs/tutorials/installation.md)
- First experiment: [`docs/tutorials/first-experiment.md`](https://github.com/marin-community/marin/blob/main/docs/tutorials/first-experiment.md)
- Lazy artifacts: [`docs/explanations/lazy-artifacts.md`](https://github.com/marin-community/marin/blob/main/docs/explanations/lazy-artifacts.md)
- LM pipeline: [`docs/explanations/lm-pipeline.md`](https://github.com/marin-community/marin/blob/main/docs/explanations/lm-pipeline.md)
- `train_lm`: [`lib/marin/src/marin/experiment/train.py`](https://github.com/marin-community/marin/blob/main/lib/marin/src/marin/experiment/train.py)
