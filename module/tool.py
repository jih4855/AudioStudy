import os
import whisper
import datetime
import json
import glob
import ollama
import yt_dlp
from rich.console import Console

console = Console()

class Tool:
    def __init__(self, text_output="text", source_file="source_file", result_folder="result", urls=None, chunk_size=1500, overlap=50, whisper_model="large-v3", audio_extensions=None):
        self.text_output = text_output
        self.source_file = source_file
        self.result_folder = result_folder
        self.urls = urls if urls is not None else []
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.whisper_model = whisper_model
        self.audio_extensions = audio_extensions if audio_extensions is not None else ["*.mp3", "*.wav", "*.m4a", "*.flac", "*.aac", "*.ogg", "*.wma"]

    #음성파일을 텍스트로 변환하고 저장할 폴더 생성하기
    def make_a_folder(self):
        if not os.path.exists(self.result_folder):
            os.makedirs(self.result_folder)
            print(f"Folder '{self.result_folder}' created successfully.")
        else:
            print(f"Folder '{self.result_folder}' already exists.")

    #음성파일을 텍스트로 변환하기
    def transcribe_audio(self):
        from rich.progress import track 

        audio_file = []
        model = whisper.load_model(self.whisper_model)
        audio_extensions = self.audio_extensions

        if not os.path.exists(self.text_output):
            os.makedirs(self.text_output)
            print(f"Folder '{self.text_output}' created successfully.")
        else:
            print(f"Folder '{self.text_output}' already exists.")
        try:
            for ext in track(audio_extensions, description="🎵 음성파일 확인 중..."):
                audio_file.extend(glob.glob(os.path.join(self.source_file, f"*.{ext}")))
            if not audio_file:
                console.print("No audio files found.")
            else:
                for audio in track(audio_file, description="🎵 음성파일 변환 중..."):
                    # 생성될 JSON 파일 경로 미리 만들기
                    json_filename = os.path.basename(audio) + ".json"
                    json_path = os.path.join(self.text_output, json_filename)

                    # 같은 이름의 JSON 파일이 이미 있는지 확인
                    if os.path.exists(json_path):
                        console.print(f"이미 존재함: {json_filename} (건너뛰기)")
                        continue  # 다음 파일로 넘어감

                    result = model.transcribe(audio)
                    text = result["text"]
                    console.print(os.path.basename(audio))
                    console.print(text) # 텍스트 출력
                    json_data = {
                    "file_name": os.path.basename(audio),  # 파일명
                    "text": result["text"],                # 변환된 텍스트
                    "timestamp": datetime.datetime.now().isoformat()  # 처리 시간
                    }
                    with open(os.path.join(self.text_output, os.path.basename(audio) + ".json"), "w") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error: {e}")

    def download_youtube_audio(self):
        """YouTube 영상에서 음성만 추출"""
        ydl_opts = {
            'format': 'bestaudio/best',
            # 이미 다운로드된 파일 있으면 건너뛰기
            'outtmpl': f'{self.source_file}/%(title)s.%(ext)s',
            'writeautomaticsub': False,
            'writesubtitles': False,
            'nooverwrites': True,  # ← 중복 방지
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192',
            }],
            'ignoreerrors': True
        }
        successful = []
        failed = []

        for url in self.urls:
            if not url:
                print("url이 필요합니다.")
                continue
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    print(f"YouTube 음성 다운로드 완료: {url}")
                    successful.append(url)
            except Exception as e:
                    print(f"❌ 다운로드 실패: {url} - {e}")
                    failed.append(url)
        
        print(f"📊 결과: 성공 {len(successful)}개, 실패 {len(failed)}개")

        return successful, failed

    def split_text_with_overlap(self, text):
        """
        텍스트를 겹침을 포함해서 청크로 분할
        """
        chunks = []
        start = 0

        while start < len(text):
            # 현재 청크의 끝 위치 계산
            end = start + self.chunk_size

            # 텍스트가 남아있으면
            if end < len(text):
                # 문장 경계에서 자르기 (더 자연스럽게)
                # 마지막 문장 끝 찾기
                last_period = text.rfind('.', start, end)
                last_question = text.rfind('?', start, end)
                last_exclamation = text.rfind('!', start, end)

                # 가장 뒤에 있는 문장 끝 찾기
                sentence_end = max(last_period, last_question,
    last_exclamation)

                if sentence_end > start:
                    end = sentence_end + 1  # 문장부호 포함

            chunk = text[start:end]
            chunks.append(chunk.strip())

            # 다음 청크 시작점 (겹침 고려)
            if end >= len(text):
                break
            start = end - self.overlap

        return chunks
