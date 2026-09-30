---
title: "Laws of UX 기억 법칙 3개 한줄 정리: 7±2에서 4±1까지, 청킹·밀러의 법칙·작업 기억의 원전 기준"
date: 2026-09-30
author: 한준구(코난쌤)
description: "청킹, 밀러의 법칙, 작업 기억을 원전 논문 본문 숫자로 다시 검증했습니다. 7±2는 절대판단과 즉시기억이 우연히 겹친 숫자였고, 리허설을 막으면 한계는 4±1로 내려옵니다. 화면·문서·강의 자료 설계 기준으로 정리했습니다."
tags: [UX, UX심리학, "Laws of UX", 작업기억, 청킹]
refactor_hub_id: ux-laws-03
aliases: [laws-of-ux/03-chunking, laws-of-ux/18-millers-law, laws-of-ux/22-working-memory]
draft: false
sources_read: "Miller 1956 본문 전문(psychclassics), Chase & Simon 1973 본문(게재본 스캔+CMU CIP #182 원고), Simon & Chase 1973 Skill in Chess 본문, lawsofux.com 3개 페이지, 대학 리더 재수록 작업기억 교재 챕터를 읽었습니다. Cowan 2001은 공개 PDF를 찾지 못해 PubMed 초록과 2차 문헌(교재 챕터, Morra et al. 2023 JOC 오픈액세스 본문)으로 대조했고, Baddeley & Hitch 1974 원본 챕터도 공개 본문이 없어 재수록 판본으로 대조했습니다. 1956·1973·1974년 고전 문헌에는 공개된 저자 코드·원시데이터가 없습니다"
novelty_vs_paper: "원전 숫자로 그린 용량 비교 차트 2장, 7±2와 4±1의 측정 조건 구분표, 옛 글 주장 검증 결과(교정 1건·삭제 3건)는 이 블로그의 작업입니다. 절대판단 2.5/2.3/1.9비트, 스팬 9/8/5, 재부호화 24/36/40자리, 체스 16/8/4·81/49/33%, 6초 50%·18초 소진은 각 원전과 재수록 문헌이 제시한 값입니다"
---

## 한눈에 보는 결론

옛 Laws of UX 시리즈 중 기억에 관한 글 3편(청킹, 밀러의 법칙, 작업 기억)을 이 페이지 하나로 합쳤습니다. 원전 논문 본문을 직접 받아 읽고 숫자를 확인해서, 화면·문서·강의 자료를 만들 때 쓸 기준으로 다시 정리했습니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>7±2는 서로 다른 두 실험의 한계가 7 근처에서 우연히 겹친 숫자입니다</strong></span>.

밀러 자신이 1956년 논문에서 절대판단과 즉시기억을 구별해 뒀구요, 그 구분을 지운 건 후대의 요약이었습니다. "한 번에 7개까지 기억한다"는 요약에는 이 구분이 빠져 있습니다.

조건에 따라 숫자는 달라집니다. <span style="background-color: #fff59d"><strong>리허설과 그룹핑을 막으면 성인의 즉시기억은 약 4±1 덩어리로 내려오고(Cowan 2001), 의미 있는 덩어리로 재조직하면 9자리 2진수가 40자리까지 늘어납니다(Miller 1956 본문의 Smith 실험)</strong></span>.

| 개념 | 한줄 요약 | 원전 근거 | 자료에 적용하면 |
|---|---|---|---|
| 밀러의 법칙 | 스팬은 약 7±2 항목, 조건이 붙는 상한 | Miller 1956 본문 | 항목 개수보다 덩어리 수 |
| 청킹 | 의미 있는 덩어리로 묶으면 담는 양이 늘어난다 | Smith 실험 9→40자리 | 그룹핑 + 묶음에 이름 |
| 작업 기억 | 보관하면서 조작, 리허설 막히면 초 단위 감쇠 | Baddeley & Hitch 1974, Brown-Peterson | 외우게 두지 말고 화면에 남김 |

근데 옛 글 세 편에는 문제가 있었습니다. 밀러를 '프린스턴 대학'으로 소개한 건 논문 표지(Harvard University)와 다르고요, <span style="background-color: #fff59d"><strong>"카드 번호 4-4-4-4 폼이 오류율이 낮다", "지시사항이 7개를 넘으면 AI 성능이 떨어진다"는 근거를 찾지 못했습니다</strong></span>.

출처를 못 찾은 주장은 이번에 전부 걷었고, 검증 기록은 아래에 남겼습니다.

## 무엇을 비교했나

이 허브로 합쳐진 옛 글은 3편입니다. 청킹, 밀러의 법칙, 작업 기억이요. 옛 URL은 이 페이지로 넘어옵니다.

법칙 이름은 [Laws of UX](https://lawsofux.com/)를 따랐구요, 숫자와 결론은 아래 원전을 직접 받아 읽은 값입니다(기준일 2026-09-30).

1. [Laws of UX — Chunking](https://lawsofux.com/chunking/)
2. [Laws of UX — Miller's Law](https://lawsofux.com/millers-law/)
3. [Laws of UX — Working Memory](https://lawsofux.com/working-memory/)
4. [Miller, G. A. 1956, The Magical Number Seven, Plus or Minus Two, Psychological Review 63, 81-97 — 전문](http://psychclassics.yorku.ca/Miller/)
5. [Chase, W. G., & Simon, H. A. 1973, Perception in Chess, Cognitive Psychology 4, 55-81 — 게재본 스캔](https://gwern.net/doc/psychology/expertise/1973-chase.pdf) / [CMU CIP #182 원고](https://iiif.library.cmu.edu/file/Simon_box00005_fld00354_bdl0001_doc0001/Simon_box00005_fld00354_bdl0001_doc0001.pdf)
6. [Simon, H. A., & Chase, W. G. 1973, Skill in Chess, American Scientist 61(4) 394-403 — 재인쇄본](https://gwern.net/doc/psychology/chess/1973-simon.pdf)
7. [Cowan, N. 2001, The magical number 4 in short-term memory, BBS 24(1) 87-114 — PubMed](https://pubmed.ncbi.nlm.nih.gov/11515286/)
8. [Morra, Patella & Muscella 2023, Journal of Cognition — 4 vs 7 비교 실험](https://journalofcognition.org/articles/10.5334/joc.387)
9. [Baddeley & Hitch 1974, Working Memory, Psychology of Learning and Motivation VIII 47-89 — 서지](https://www.sciencedirect.com/science/chapter/bookseries/pii/S0079742108604521) / [대학 리더 재수록 작업기억 챕터](https://web.uvic.ca/~dbub/Cognition_Action/Cog_Psych_Readings_files/Workingmemory.pdf)
10. [Gobet, F. — Memory for the Meaningless(체스 무작위 기국 리뷰)](http://chrest.info/fg/papers/Meaningless/Meaningless.html)

## 방법 비교

세 개념을 같은 축(문제, 핵심 숫자, 근거 강도, 남용 주의)으로 놓고 비교했습니다.

| 개념 | 문제 | 핵심 숫자 | 근거 강도 | 남용 주의 |
|---|---|---|---|---|
| 밀러의 법칙 | 한 번에 몇 개까지 담나 | 스팬 7±2(본문: 2진수 9, 10진수 8, 단어 5) | 70년 재현된 고전 + 조건 논쟁 | "7개까지는 괜찮다"는 근거로 쓰면 안 됨 |
| 청킹 | 덩어리로 묶으면 얼마나 늘어나나 | 재부호화 후 9→40자리(2진수) | 본문 실험 + 체스 전문가 데이터 | 학습 안 된 묶음은 증가폭이 작음 |
| 작업 기억 | 저장과 조작이 겹칠 때 한계 | 리허설 차단 시 6초 50%, 18초 거의 0 | 이중과제 실험 + 감쇠 곡선 | "20-30초 버퍼"로 쓰면 느긋한 셈 |

### 7±2의 정체: 서로 다른 두 실험

밀러의 논문은 두 이야기를 담고 있습니다. 하나는 절대판단입니다. 소리의 음높이를 구별하는 실험(Pollack)에서 채널용량은 2.5비트, 약 6개. 음량은 2.3비트(약 5개), 염분 농도는 1.9비트(약 4개). 단일차원 평균은 약 6.5개 범주고요, 범위는 4~10개였습니다.

다른 하나는 즉시기억 스팬입니다. Hayes의 실험에서 2진수는 약 9개, 10진수는 약 8개, 1,000단어 단음절 집에서 뽑은 단어는 약 5개를 외웠습니다.

<span style="background-color: #fff59d"><strong>밀러의 결론은 "절대판단은 비트 수로 제한되고, 즉시기억은 덩어리 수로 제한된다"는 구분이었습니다. 7이 두 실험에 겹쳐 나온 건 우연이고, 같은 메커니즘이 아니라고요</strong></span>. UX에서 "항목이 7개 이하여야 한다"고 쓸 때 이 구분은 사라져 있습니다.

### 현대의 숫자: 4±1은 어떤 조건의 값인가

코완의 2001년 리뷰는 리허설이나 그룹핑을 막은 조건에서 용량을 다시 계산했습니다. <span style="background-color: #fff59d"><strong>초점 주의에 담기는 덩어리는 성인 기준 약 3~5개(4±1)</strong></span>이라는 결론입니다. 7±2는 소리 내어 되뇌거 묶음을 만들 수 있는 이상적 조건의 상한에 가깝습니다.

이 논쟁은 아직 열려 있습니다. 2023년 Journal of Cognition 실험(5편)은 짧은 노출로 재는 시각 과제에서는 4 근처가 나오고, <span style="background-color: #fff59d"><strong>긴 노출 조건에서는 재부호화·청킹으로 추정 용량 k가 더 높게 측정된다</strong></span>고 정리했습니다. 정답은 고정되지 않고, 재는 조건의 함수로 결정됩니다.

![측정 조건별 기억 용량 추정치](../media/laws-of-ux-3-memory-capacity-laws-guide/chart-capacity-estimates.png)

### 청킹: 9자리에서 40자리로

Miller 본문이 소개하는 스미스의 실험이 청킹의 원전 데이터입니다. 참가자 20명의 2진수 스팬은 9자리, 8진수 스팬은 7자리였습니다. 여기서 2진수 세 자리를 8진수 한 자리로 바꾸는 재부호화를 가르치니 스팬이 늘었습니다.

5~10분 학습으로는 기대만큼 늘지 않았습니다. <span style="background-color: #fff59d"><strong>묶음 번역이 반자동이 되기 전엔 앞 덩어리를 고민하는 사이 다음 덩어리를 놓친다</strong></span>는 겁니다. 스미스가 에빙하우스식으로 자신을 드릴하자 12개의 8진수 스팬이 그대로 2진수 24자리(2:1), 36자리(3:1), 약 40자리(4:1, 5:1)로 환산됐습니다.

전화번호 010-1234-5678이 세 덩어리로 읽히는 것도 같은 원리구요. <span style="background-color: #fff59d"><strong>묶음에 이름(라벨)을 붙이는 게 청킹의 핵심입니다</strong></span>.

### 체스: 아는 사람의 덩어리는 더 크다

Chase & Simon(1973)은 마스터(M), A급(A), 입문자(B) 세 사람에게 실전 기국을 5초 보여주고 재구성하게 했습니다. 중반 기국 1차 시도에 <span style="background-color: #fff59d"><strong>M은 약 16개, A는 약 8개, B는 약 4개의 기물을 정확히 놓았습니다</strong></span>. 전술 기국 9개를 5초에 한 번씩 보여주자 정확도는 M 81%, A 49%, B 33%였습니다.

그런데 말을 무작위로 섞은 기국에서는 격차가 사라졌습니다. <span style="background-color: #fff59d"><strong>세 실력 모두 실전 기국에서의 입문자보다 아래로 떨어졌다</strong></span>는 게 본문 서술입니다.

드그루트가 관찰한 그랜드마스터의 23~24/25 기록과 비교해도 같은 그림입니다. <span style="background-color: #fff59d"><strong>기억 차이를 만드는 건 기보 덩어리의 크기입니다</strong></span>.

![재부호화 실험과 체스 기억 데이터](../media/laws-of-ux-3-memory-capacity-laws-guide/chart-recoding-chess.png)

### 작업 기억: 보관하고 조작하는 시스템

배들리와 히치(1974)는 "B A" 참거짓 판단 과제에 6~8자리 숫자를 미리 외우게 하는 이중과제를 돌렸습니다. 저장과 조작이 하나의 창고라면 숫자 외우기가 판단을 무너뜨려야 하는데, 부분적으로만 무너졌습니다. 여기서 <span style="background-color: #fff59d"><strong>중앙집행기, 음운루프, 시각공간 스케치패드의 3요소 모델</strong></span>이 나왔고, 2000년에 에피소드 버퍼가 추가됐습니다.

감쇠 속도도 재현됩니다. Brown-Peterson 과제에서 리허설을 막으면 <span style="background-color: #fff59d"><strong>자음 3개 회상이 6초에 약 50%, 18초에 거의 0</strong></span>으로 떨어졌습니다(Peterson & Peterson 1959).

Laws of UX의 working-memory 페이지는 "청크가 20-30초 후 페이드"라고 쓰는데, 원전 기준으로는 절반 가까이 느긋한 숫자입니다.

## 언제 무엇을 쓰나

| 만드는 것 | 우선 적용 | 하지 말 것 | 근거 |
|---|---|---|---|
| 앱·사이트 첫 화면 | 새 독립 항목 3~5개 묶음 | 7개를 '허용치'로 해석 | Cowan 4±1 |
| 문서·강의 자료 목차 | 장당 덩어리 3~5개, 단계 분해 | 전체 색인을 첫 장에 | 4±1 + 청킹 |
| 학습지·체크리스트 | 항목 그룹핑 + 그룹 이름 | 항목만 평면 나열 | Smith 재부호화 |
| 폼·카드 입력 | 실제 인쇄 형식과 같은 그룹(4-4-4-4) | 16자리를 한 칸에 | 청킹 원리 |
| 진행 상황 요약 | 담은 내용을 화면에 상시 노출 | "기억해서" 다음 단계 | 작업기억 외부화 |
| 이동 중 음성 안내 | 다음 지시까지 6초 이내 재확인 | 한 번 안내 후 긴 침묵 | Brown-Peterson |
| 전문가용 레퍼런스 | 익숙한 덩어리 단위로 밀도 완화 | 입문자용과 같은 밀도 | 체스 16 vs 4 |

## 블로그봇이 직접 확인한 것

- 원전 본문 세 종을 직접 받아 읽었습니다. Miller 1956 전문(psychclassics), Chase & Simon 1973(게재본 스캔 + CMU CIP #182 원고 병행), Simon & Chase 1973(American Scientist 재인쇄).
- 본문에서 숫자를 다시 뽑았습니다. 절대판단 2.5/2.3/1.9비트(단일차원 평균 약 6.5개 범주), Hayes 스팬 2진수 9·10진수 8·단어 5, Smith 재부호화 24/36/40자리, 체스 16/8/4개와 81/49/33%, 무작위 기국 붕괴 서술.
- Cowan 2001은 공개 PDF를 찾지 못해서 PubMed 초록과 두 개의 2차 문헌(대학 리더 재수록 교재 챕터, Morra et al. 2023 오픈액세스 본문)으로 클레임을 대조했습니다.
- 옛 글 오류를 교정·삭제했습니다. '프린스턴' → 논문 표지 기준 Harvard로 교정. 카드 폼 오류율 수치, AI 프롬프트 7개 주장, 중국어가 섞인 지도 안내 예시는 출처 미확인이라 삭제.
- 용량 비교 차트 2장을 원전 숫자로 직접 그렸습니다. 스크립트와 검증 노트는 sandbox-lane-c에 보관했습니다.
- 1956·1973·1974년 고전 문헌에 공개된 저자 코드·원시데이터는 없습니다. 숫자는 논문 본문 문장과 표에서 확인했습니다.

## 한계와 반론

- Cowan 2001 본문을 직접 읽지 못했습니다. 4±1 클레임은 초록과 2차 문헌 대조이고, 본문 세부 논증(측정법별 근거)은 확인하지 못했습니다.
- 4 vs 7은 진행형 논쟁입니다. Morra et al. 2023은 과제와 노출 시간에 따라 k가 갈린다고 보고했고, 7을 지지하는 이론(Pascual-Leone 계열)도 여전히 경쟁 중입니다.
- 체스 데이터는 1973년 참가자 3인(M/A/B)입니다. 숫자는 방향을 보여주지만 표본이 작고, 무작위 기국 수치는 본문 서술로만 확인했습니다(그림 값 아님).
- Baddeley & Hitch 1974 원본 챕터는 Elsevier 서지로 공개 본문이 없습니다. 재수록 교재 챕터와 lawsofux 페이지로 대조했고, 실험 세부는 재수록 판본 기준입니다.
- 이번 실행에서 새로운 사용자 테스트는 하지 않았습니다. 적용 규칙은 원전 숫자의 재해석입니다.

## 적용 규칙

1. 한 화면·한 장에 새로 등장하는 독립 항목은 3~5개로 묶어 제시합니다(4±1 기준, 방어적 설계).
2. 더 담아야 하면 개수를 늘리지 말고 의미 있는 묶음으로 재조직하고, 묶음에 이름을 붙입니다(Smith 재부호화).
3. 청중이 안 익숙한 고밀도 압축(4:1, 5:1)은 학습 시간을 주거나 풀어 씁니다. 5~10분 학습으로는 증가폭이 기대보다 작았습니다.
4. 기억해야 할 정보는 화면에 남겨 외부화합니다. 다음 단계로 넘어갈 때 앞 정보를 치우지 않습니다(작업기억 우회).
5. 리허설이 어려운 연속 안내에서는 6초 안에 다음 확인을 겹칩니다. 18초 후에는 거의 남지 않는다고 봅니다(Brown-Peterson).
6. 전문가 독자에게는 익숙한 덩어리 단위로 밀도를 올려도 됩니다. 같은 5초에 마스터는 입문자의 4배를 담습니다(체스).

## 자주 묻는 질문

메뉴를 꼭 7개 이하로 맞춰야 하나요?

아니오. 7은 절대판단의 한계와 즉시기억 스팬이 우연히 겹친 숫자일 뿐 허용치가 아닙니다. 메뉴는 덩어리 수와 스캔 구조로 판단하고, 새 항목은 화면당 3~5개를 우선합니다.

7±2와 4±1 중 어느 쪽을 설계 기준으로 쓰나요?

방어적으로는 4±1입니다. 7±2는 리허설·그룹핑이 가능한 이상적 조건의 상한으로 이해하면 됩니다. 두 숫자의 조건 차이를 표로 남겨 두면 나중에 혼동이 줄어듭니다.

청킹은 언제나 효과가 있나요?

묶음이 의미 있고 그 매핑이 학습되어 있어야 합니다. 5~10분 학습으로는 증가폭이 기대보다 작았고, 번역이 반자동이 된 뒤에야 9자리에서 40자리까지 늘었습니다.

기억은 20~30초 뒤에 사라지나요?

리허설을 막으면 그보다 빠릅니다. 6초에 절반, 18초에 거의 0입니다. 20-30초는 여유 있게 잡은 셈이고, 안전한 설계 기준은 아닙니다.

## 참고 자료

1. [Laws of UX — Chunking](https://lawsofux.com/chunking/)
2. [Laws of UX — Miller's Law](https://lawsofux.com/millers-law/)
3. [Laws of UX — Working Memory](https://lawsofux.com/working-memory/)
4. [Miller, G. A. (1956). The Magical Number Seven, Plus or Minus Two. Psychological Review, 63, 81-97 — 전문](http://psychclassics.yorku.ca/Miller/)
5. [Chase, W. G., & Simon, H. A. (1973). Perception in Chess. Cognitive Psychology, 4, 55-81 — 스캔](https://gwern.net/doc/psychology/expertise/1973-chase.pdf)
6. [Simon, H. A., & Chase, W. G. (1973). Skill in Chess. American Scientist, 61(4), 394-403 — 재인쇄](https://gwern.net/doc/psychology/chess/1973-simon.pdf)
7. [Cowan, N. (2001). The magical number 4 in short-term memory. Behavioral and Brain Sciences, 24(1), 87-114 — PubMed](https://pubmed.ncbi.nlm.nih.gov/11515286/)
8. [Morra, S., Patella, P., & Muscella, L. (2023). Modelling Working Memory Capacity. Journal of Cognition](https://journalofcognition.org/articles/10.5334/joc.387)
9. [Baddeley, A. D., & Hitch, G. J. (1974). Working Memory. In Psychology of Learning and Motivation, VIII, 47-89 — 서지](https://www.sciencedirect.com/science/chapter/bookseries/pii/S0079742108604521)
10. [Peterson, L. R., & Peterson, M. J. (1959). Short-term retention of individual verbal items — 재수록 챕터로 대조](https://web.uvic.ca/~dbub/Cognition_Action/Cog_Psych_Readings_files/Workingmemory.pdf)
11. [Gobet, F. — Memory for the Meaningless(체스 무작위 기국 리뷰)](http://chrest.info/fg/papers/Meaningless/Meaningless.html)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
