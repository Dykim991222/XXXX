# XXXX

YouTube에서 댓글과 오디오를 추출하는 Python 프로그램입니다.

## 프로젝트 구조

```text
C:\dev\XXXX\
  ├─ .venv\              ← 가상환경(커밋 금지)
  ├─ src\                ← 코드
  │   └─ main.py         ← 메인 프로그램
  ├─ .env                ← YouTube API 키 (커밋 금지)
  ├─ extract_comments\   ← 댓글 저장 폴더 (자동 생성)
  ├─ audio\              ← 오디오 저장 폴더 (자동 생성)
  ├─ requirements.txt
  └─ README.md
```

## 준비 (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

만약 실행 정책으로 인해 활성화가 막히면 다음을 관리자 권한 PowerShell에서 한 번 실행하세요.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 실행

```powershell
python .\src\main.py
```

## 주요 기능

1. **YouTube 댓글 추출**: 비디오의 모든 댓글과 답글을 추출하여 `extract_comments` 폴더에 저장
2. **YouTube 오디오 추출**: 비디오의 오디오를 MP3/m4a 형식으로 추출하여 `audio` 폴더에 저장
3. **오디오 스크립트 생성**: Whisper AI를 사용하여 오디오에서 자동으로 스크립트 생성하여 `script` 폴더에 저장
4. **YouTube API 키 필요**: `.env` 파일에 `YOUTUBE_DATA_API_KEY`를 설정해야 합니다

## 사용 방법

1. `.env` 파일에 YouTube Data API 키를 추가합니다:
   ```
   YOUTUBE_DATA_API_KEY=your_api_key_here
   ```

2. 프로그램을 실행합니다:
   ```powershell
   python .\src\main.py
   ```

3. YouTube URL을 입력합니다 (예: `https://youtube.com/watch?v=VIDEO_ID`)

4. 댓글 추출이 완료되면 오디오 추출 여부를 선택할 수 있습니다.

## 출력 파일

- **댓글**: `extract_comments/VIDEO_ID_TIMESTAMP.txt`
- **오디오**: `audio/VIDEO_TITLE.m4a` (또는 webm, opus 등)
- **스크립트**: `script/VIDEO_ID_TIMESTAMP.txt`

## 주의사항

- FFmpeg가 설치되어 있지 않으면 오디오가 MP3 대신 m4a, webm 등의 원본 형식으로 저장됩니다
- Whisper가 설치되지 않은 경우 자동으로 설치됩니다 (최초 실행 시 시간이 걸릴 수 있음)
  - Whisper는 OpenAI의 음성 인식 모델로, 오디오를 텍스트로 변환합니다


