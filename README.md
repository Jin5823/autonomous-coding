# autonomous-coding

Claude Agent SDK를 사용한 **무중단 자율 코딩 에이전트**입니다.

Rate limit 자동 처리, 세션 자동 이어하기를 통해 사람의 개입 없이 프롬프트 기반으로 프로젝트를 끝까지 생성합니다.

## Prerequisites

이 프로젝트는 **Claude Code CLI**가 필요합니다.

### Claude Code 설치 확인

```bash
claude --version
```

버전이 출력되면 설치되어 있는 것입니다. 설치되어 있지 않다면 [Claude Code 설치 가이드](https://docs.anthropic.com/en/docs/claude-code)를 참고하세요.

### Claude Code 로그인 확인

```bash
claude
```

위 명령어 실행 후 정상적으로 대화가 시작되면 인증이 완료된 것입니다. 로그인이 안 되어 있다면 자동으로 로그인 프로세스가 시작됩니다.

## Installation

```bash
# 저장소 클론
git clone <repository-url>
cd autonomous-coding

# 의존성 설치
pip install -e .
```

## Usage

### 기본 실행

```bash
python src/cmd/autonomous_coding.py \
  --project-dir ./generations/my_project \
  --prompts-dir ./prompts
```

### 옵션

| 옵션 | 설명 |
|------|------|
| `--project-dir` | 프로젝트가 생성될 디렉토리 (필수) |
| `--prompts-dir` | 프롬프트 템플릿이 있는 디렉토리 (필수) |
| `--max-iterations` | 최대 반복 횟수 (기본값: 무제한) |

### 예시

```bash
# 반복 횟수 제한
python src/cmd/autonomous_coding.py \
  --project-dir ./generations/my_project \
  --prompts-dir ./prompts \
  --max-iterations 5
```

## Prompts SDD (Software Design Documents)

이 섹션이 핵심입니다. 자율 코딩 에이전트는 3개의 프롬프트 파일을 기반으로 동작합니다.

```
prompts/
├── app_spec.txt           # 무엇을 만들 것인가
├── initializer_prompt.md  # 첫 번째 에이전트의 행동 지침
└── coding_prompt.md       # 이후 에이전트들의 행동 지침
```

### 1. app_spec.txt - 프로젝트 명세서

**역할:** 만들고자 하는 애플리케이션의 완전한 설계 문서

**포함해야 할 내용:**
- 프로젝트 개요 및 목표
- 기술 스택 (프론트엔드, 백엔드, DB 등)
- 핵심 기능 목록 및 상세 설명
- 데이터베이스 스키마
- API 엔드포인트 정의
- UI/UX 레이아웃 및 디자인 시스템
- 구현 단계별 계획
- 성공 기준

**커스터마이징 팁:**
```xml
<project_specification>
  <project_name>나의 프로젝트</project_name>
  <overview>프로젝트에 대한 상세 설명...</overview>
  <technology_stack>...</technology_stack>
  <core_features>...</core_features>
  <!-- 더 상세할수록 에이전트가 정확하게 구현합니다 -->
</project_specification>
```

> 이 파일이 상세할수록 에이전트의 결과물 품질이 높아집니다. 모호한 요구사항은 모호한 결과를 만듭니다.

---

### 2. initializer_prompt.md - 초기화 에이전트 프롬프트

**역할:** 프로젝트의 첫 번째 에이전트가 수행할 작업 정의

**기본 동작:**
1. `app_spec.txt` 읽고 이해
2. `feature_list.json` 생성 (200개의 테스트 케이스)
3. `init.sh` 생성 (환경 설정 스크립트)
4. Git 저장소 초기화
5. 프로젝트 기본 구조 생성

**커스터마이징 포인트:**
- 테스트 케이스 개수 조정 (기본 200개)
- 초기 설정 스크립트 요구사항 변경
- 프로젝트 구조 커스터마이징

**주의:** 이 프롬프트는 "한 번만" 실행됩니다. 프로젝트의 뼈대를 잡는 역할이므로 신중하게 작성하세요.

---

### 3. coding_prompt.md - 코딩 에이전트 프롬프트

**역할:** 초기화 이후 반복 실행되는 에이전트의 행동 지침

**기본 동작 (매 세션마다):**
1. 현재 상태 파악 (파일 구조, 진행 상황 확인)
2. 서버 실행 (`init.sh`)
3. 기존 기능 검증 테스트 (회귀 방지)
4. `feature_list.json`에서 미완료 기능 선택
5. 기능 구현 및 브라우저 테스트
6. 테스트 통과 시 `passes: true`로 업데이트
7. Git 커밋 및 진행 상황 기록

**핵심 원칙:**
- 한 세션에 하나의 기능에 집중
- 브라우저 자동화로 실제 UI 테스트 필수
- `feature_list.json`은 `passes` 필드만 수정 가능 (기능 삭제/수정 금지)
- 세션 종료 전 반드시 clean state 유지

**커스터마이징 포인트:**
- 테스트 방법론 변경 (puppeteer 외 다른 도구)
- 커밋 메시지 형식
- 진행 상황 기록 방식

---

### 나만의 프로젝트 만들기

1. **app_spec.txt 작성**: 가장 중요합니다. 원하는 앱을 최대한 상세하게 기술하세요.
2. **initializer_prompt.md**: 대부분 그대로 사용 가능. 테스트 케이스 수만 조정하세요.
3. **coding_prompt.md**: 대부분 그대로 사용 가능. 테스트 도구가 다르면 수정하세요.

```bash
# 새 프로젝트 시작
mkdir -p prompts/my_app
cp prompts/initializer_prompt.md prompts/my_app/
cp prompts/coding_prompt.md prompts/my_app/

# app_spec.txt만 새로 작성
vim prompts/my_app/app_spec.txt

# 실행
python src/cmd/autonomous_coding.py \
  --project-dir ./generations/my_app \
  --prompts-dir ./prompts/my_app
```

## 중단 및 재개

`Ctrl+C`로 중단할 수 있으며, 동일한 명령어로 다시 실행하면 이어서 진행됩니다.
