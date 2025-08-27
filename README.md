# STT 음성 텍스트 변환 및 문제 생성 시스템

AI 기반 음성-텍스트 변환 후 자동 문제 생성을 수행하는 Python 애플리케이션입니다.

## 주요 기능

-  음성 파일 변환 : Whisper를 사용한 고품질 STT(Speech-to-Text)
-  YouTube 다운로드 : yt-dlp를 통한 YouTube 음성 추출
-  다중 LLM 지원 : OpenAI GPT, Google Gemini, Ollama 지원
-  자동 문제 생성 : 변환된 텍스트를 기반으로 시험 문제 자동 생성
-  용어 교정 : STT 오인식 용어 자동 교정
-  개념 분석 : 핵심 개념 추출 및 분석
-  진행률 표시 : Rich 라이브러리 기반 시각적 진행률

## 설치 방법

### 1. 저장소 클론
```bash
git clone 
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. FFmpeg 설치 (음성 처리용)
 Windows: 
```bash
choco install ffmpeg
```

 macOS: 
```bash
brew install ffmpeg
```

 Ubuntu/Debian: 
```bash
sudo apt update
sudo apt install ffmpeg
```

## 사용법

### 1. 환경 설정

 .env 파일 생성: 
```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. 설정 파일 수정

 config.yaml에서 사용할 LLM 선택: 

 Ollama 사용 (무료, 로컬): 
```yaml
llm:
  model_name: "llama3.1"
  provider: "ollama"
```

 OpenAI 사용: 
```yaml
llm:
  model_name: "gpt-3.5-turbo"
  provider: "openai"
```

 Google Gemini 사용: 
```yaml
llm:
  model_name: "gemini-1.5-flash"
  provider: "genai"
```

### 3. 음성 파일 준비

`source_file/` 폴더에 음성 파일을 넣습니다.
지원 형식: mp3, wav, m4a, flac, aac, ogg, wma

### 4. 실행

```bash
python main.py
```

### 5. 결과 확인

-  텍스트 변환 결과 : `text/` 폴더
-  생성된 문제 : `result/` 폴더

## 설정 옵션

### config.yaml 주요 설정

```yaml
# LLM 설정
llm:
  model_name: "llama3.1"
  provider: "ollama"

# Whisper 모델 설정
whisper:
  model: "large-v3"  # tiny, base, small, medium, large-v3

# 텍스트 분할 설정
split_text:
  chunk_size: 1500  # 청크 크기
  overlap: 50       # 겹침 범위

# 폴더 설정
folders:
  text_output: "text"
  source_file: "source_file"
  result_folder: "result"

# 오디오 확장자 설정
audio:
  extensions: ["mp3", "wav", "m4a", "flac", "aac", "ogg", "wma"]

# YouTube 다운로드 설정
youtube:
  codec: "m4a"
  quality: "192"
```

## 지원되는 provider

### Google Gemini (추천) : "gemini-2.5-flash"
### OpenAI

### Ollama (무료 - 로컬)
```bash
# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 모델 다운로드
ollama pull llama3.1
ollama pull gemma2
```

### 모델 선택 가이드

 추천 설정: 
```yaml
llm:
  model_name: "gemini-2.5-flash"
  provider: "genai"
```

 추천:  30B 이하의 로컬 모델들은 STT 텍스트의 오타 및 오인식 교정에서 만족스러운 성능을 보이지 않았습니다. 정확한 용어 교정과 문제 생성을 위해서는  Gemini나 OpenAI의 경량 모델 사용을 강력히 권장 합니다.

## 출력 형식

### 텍스트 변환 결과
```json
{
  "file_name": "audio.mp3",
  "text": "변환된 텍스트 내용...",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 생성된 문제
```json
{
  "chunk_info": {
    "original_file": "audio.mp3",
    "chunk_number": 1,
    "total_chunks": 3,
    "processed_time": "2024-01-01T12:00:00"
  },
  "term_analysis": "용어 분석 결과...",
  "concept_analysis": "개념 분석 결과...",
  "questions": [
    {
      "question_id": 1,
      "question": "문제 내용",
      "choices": {
        "A": "선택지 1",
        "B": "선택지 2",
        "C": "선택지 3",
        "D": "선택지 4"
      },
      "answer": "A",
      "explanation": "상세한 해설..."
    }
  ]
}
```

## 문제 해결

### 자주 발생하는 오류

 1. API 키 오류 
```
Error: API key not valid
```
- .env 파일의 API 키 확인
- 해당 서비스의 API 키 발급 상태 확인

 2. 음성 파일을 찾을 수 없음 
```
No audio files found
```
- source_file 폴더에 음성 파일 존재 여부 확인
- 지원되는 파일 형식인지 확인

 3. Whisper 모델 다운로드 오류 
- 네트워크 연결 확인
- 디스크 용량 확인 (large-v3는 약 3GB)

 4. FFmpeg 관련 오류 
- FFmpeg 설치 확인: `ffmpeg -version`
- 시스템 PATH 환경변수 확인

## 개발 환경

### 필요 환경
-  Python : 3.9+ (테스트된 버전: 3.13.5)
-  운영체제 : Windows, macOS, Linux
-  메모리 : 최소 8GB RAM (Whisper large-v3 모델 사용시)
-  저장공간 : 최소 5GB (Whisper 모델 + 의존성)

### 주요 의존성
-  PyTorch : 2.8.0+ (딥러닝 프레임워크)
-  OpenAI Whisper : 20250625+ (음성-텍스트 변환)
-  Rich : 14.1.0+ (터미널 UI)
-  yt-dlp : 2025.8.22+ (YouTube 다운로드)
-  OpenAI API : 1.102.0+ (GPT 모델 접근)
-  Google Generative AI : 0.8.0+ (Gemini 모델 접근)
-  Ollama : 0.3.0+ (로컬 LLM 실행)

## 프로젝트 목적
이 프로젝트는  자격증 등 학습 목적 으로 개발되었습니다.

### 주요 활용 분야
-  자격증 시험 준비 : 음성 강의를 문제집으로 변환
-  학습 콘텐츠 제작 : STT → 개념 분석 → 문제 생성 파이프라인
-  회의 및 강의 음성파일 텍스트 변환 및 재가공(프롬프트 변경 후)
