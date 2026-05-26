# PokeRL 스레드 (Threads용)

## Thread 1: 포켓몬 레드를 RL로 클리어하기

포켓몬 레드(1996)를 강화학습으로 플레이하는 방법을 정리했다 🎮🤖

PyBoy 에뮬레이터 위에서 PPO 에이전트를 학습시키는 시스템부터, 실제로 어떻게 돌리는지까지.

블로그: [링크]

---

## Thread 2: 왜 포켓몬이 RL 벤치마크인가

Atari보다 어려운 이유:
• 25시간 플레이타임 (긴 호라이즌)
• 희소 보상 (체육관 리더 격파해야 의미있는 보상)
• 부분 관측 (맵이 다 안 보임)
• 전투/탐험/아이템 관리 동시에
• 비선형 월드 (여러 경로 가능)

현실 세계 에이전트 문제와 놀라울 정도로 닮아 있다.

---

## Thread 3: PokeRL의 핵심 — 커리큘럼 러닝

게임 전체를 한번에 학습하면 실패한다.

대신 3단계로 나눈다:
1️⃣ House Exit — 집에서 탈출 (1시간, 70% 성공)
2️⃣ Exploration — 태초마을 탐험, 풀숲 도달 (2시간, 60%)
3️⃣ Battle — 라이벌(그린) 전투 승리 (2시간, 50%)

각 단계마다 자체 보상함수 + 세이브 상태 + 학습 설정.

---

## Thread 4: 가장 큰 적은 "루프"

RL 에이전트가 포켓몬에서 가장 많이 실패하는 패턴:

🔄 같은 위치를 왔다갔다 (루프)
📋 A/B 버튼 무한 반복 (메뉴 스팸)
🚶 목적 없이 배회 (wandering)

PokeRL은 3겹 안티루프 시스템으로 해결:
• 위치 기반 루프 감지
• 액션 패턴 분석
• 시간 기반 탐험 보상 감소

---

## Thread 5: 놀라운 파라미터 효율성

David Rubinstein팀이 포켓몬 레드 전체를 클리어한 정책:

파라미터: <10M
DeepSeekV3 대비 60,500배 작음.

5년 연구 끝에 달성. 큰 모델이 필요한 게 아니라, 좋은 보상 설계와 환경 래핑이 핵심.

---

## Thread 6: 직접 돌려보기

```bash
git clone https://github.com/reddheeraj/PokemonRL
conda create -n pokemonred python=3.10
pip install -r requirements.txt
# ROM을 roms/에 배치
python scripts/test_env.py  # 테스트
python scripts/train_sequence1_house_exit.py --timesteps 500000 --envs 4
```

M1/M2 Mac에서도 잘 돈다. 시퀀스 1은 1시간이면 학습 완료.

---

## Thread 7: 더 보기

세 가지 주요 프로젝트:
• PokeRL (초반): github.com/reddheeraj/PokemonRL
• Whidden (체육관 2개): github.com/PWhiddy/PokemonRedExperiments
• Rubinstein (전체 클리어): github.com/drubinstein/pokemonred_puffer

논문: arxiv.org/abs/2604.10812
