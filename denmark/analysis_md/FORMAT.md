# 해설서 원고 형식 (analysis_md)

파일: `denmark/analysis_md/partN/epXX.md` — 원본 `denmark/episodes/partN/epXX.md`와 1:1.

```
# 1부 1화 — Mandag på Jægersborggade
## 예게르스보르가데의 월요일

> **장면 1** (원본 장면 설명을 그대로 복사)

### 1. Inger: Godmorgen, Jonas! Du er tidligt på den i dag.
번역: 좋은 아침, 요나스! 오늘은 일찍 나왔네.
■ 주요 단어
| godmorgen | godmorgen (감탄사) | 좋은 아침, 아침 인사 |
| tidligt | tidlig (형용사) → tidligt (부사형, -t) | 일찍 |
■ 문법
- Du er … : være 동사 현재형 er는 모든 인칭에 동일(jeg/du/han/vi … er).
- 형용사에 -t를 붙여 부사로 쓰는 규칙: tidlig → tidligt.
■ 표현
- være tidligt på den — '일찍 나서다, 서두르다'. 구어 관용구, den은 특정 대상 없이 쓰이는 관용적 대명사.
■ 시제·어순
- 현재형(er). 평서문 V2 어순: 주어 Du + 동사 er.
```

규칙
- `### N. 화자: 대사` 헤딩은 원본 대사 줄(번호 포함)을 **글자 그대로** 복사. 120턴 모두, 순서대로.
- 장면 설명(`> **장면 N** …`)은 해당 턴 앞에 원본 그대로 복사.
- `번역:` 자연스러운 한국어 구어 번역. 지문 [ ]도 번역에 [ ]로 포함.
- `■ 주요 단어`: 표 행 `| 단어(본문 형태) | 기본형 (품사, 명사는 en/et 성·복수형 가능하면) | 뜻 |` 2~6행. 표 머리행은 쓰지 않음(변환 시 자동 추가).
- `■ 문법`: 1~3개 bullet. 성·한정형, 형용사 일치, 대명사, 전치사, 종속절 어순, 분리동사, 수동태 등.
- `■ 표현`: 1~2개 bullet. 관용구, 구어 뉘앙스, 양태불변화사(jo, nu, da, vel, nok, sgu, altså, lige) 설명. 없으면 `- (특별한 관용 표현 없음)`.
- `■ 시제·어순`: 1~2개 bullet. 시제(현재/과거/현재완료/과거완료/미래 표현/명령형/부정사/수동), har/er 선택, V2·도치·종속절에서 부사 위치.
- 같은 설명이 계속 반복되면 짧게 줄이고 "(1화 3번 참고)"처럼 앞 설명을 가리켜도 됨. 단 새 요소는 반드시 설명.
- 원본 대사·학습 노트는 수정하지 않는다. 원본 덴마크어에 명백한 오류를 발견하면 `analysis_md/errata.md`에 `epXX 턴N: 문제 → 제안` 한 줄로 기록.
- 검증: `python3 denmark/tools/check_analysis.py XX` → `OK`가 나와야 함.
