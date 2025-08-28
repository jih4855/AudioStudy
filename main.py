import os
import datetime
import json
import glob
from module.tool import Tool
from module.llm_agent import LLM_Agent
import yaml
import re
from dotenv import load_dotenv
from rich.progress import track
from rich.console import Console

console = Console()

def main():

    load_dotenv()

    # config.yaml 먼저 읽기
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # provider에 따라 환경변수에서 API 키 가져오기 (.env 우선순위)
    provider = config['llm']['provider']

    if provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
    elif provider == 'genai':
        api_key = os.getenv('GOOGLE_API_KEY')
    else:  # ollama
        api_key = None  # ollama는 API 키 불필요

    llm = LLM_Agent(config['llm']['model_name'], provider, api_key)
    tool = Tool(text_output=config['folders']['text_output'],
                source_file=config['folders']['source_file'],
                result_folder=config['folders']['result_folder'],
                urls=config['urls'],
                chunk_size=config['split_text']['chunk_size'],
                overlap=config['split_text']['overlap'],
                whisper_model=config['whisper']['model'],
                audio_extensions=config['audio']['extensions'],
                max_length=config.get('max_length', 50)
            )
    tool.download_youtube_audio()
    tool.transcribe_audio()
    json_file = glob.glob(os.path.join(config['folders']['text_output'], "*.json"))

    try:
          for json_path in track(json_file, description="📁 파일 처리 중..."):
            if not json_path:
                console.print("No json files found.")
            else:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_content = json.load(f)

                json_filename = os.path.basename(json_path)
                result_json_path = os.path.join(config['folders']['result_folder'], json_filename)

                # 같은 이름의 JSON 파일이 이미 있는지 확인
                if os.path.exists(result_json_path):
                    console.print(f"이미 존재함: {json_filename} (건너뛰기)")
                    continue  # 다음 파일로 넘어감
                text_chunks = tool.split_text_with_overlap(json_content['text'])
                for i, chunk in enumerate(track(text_chunks, description="📝 청크 처리 중...")):
                    # 청크별 파일명 생성
                    base_filename = tool.safe_filename(os.path.splitext(os.path.basename(json_path))[0])
                    chunk_filename = f"{base_filename}_chunk_{i+1:03d}.json"
                    chunk_path = os.path.join(config['folders']['result_folder'], chunk_filename)

                    # 이미 처리된 청크는 건너뛰기
                    if os.path.exists(chunk_path):
                        console.print(f"이미 존재함: {chunk_filename} (건너뛰기)")
                        continue
                    용어분석_response = llm.generate_response(config['prompts']['용어분석_에이전트'], str(f'원본데이터: {chunk}'))
                    console.print(f"용어분석 결과: {용어분석_response}")
                    개념분석_response = llm.generate_response(config['prompts']['개념분석_에이전트'], str(f'원본데이터: {chunk}'), data=f'오표기 수정용어 : {용어분석_response}')
                    console.print(f"개념분석 결과: {개념분석_response}")
                    문제출제_response = llm.generate_response(config['prompts']['문제출제_에이전트'], str(f'원본데이터: {chunk}'), data=f'생성해야할 개념 데이터 : {개념분석_response}')
                    console.print(f"문제출제 결과: {문제출제_response}")

                    # 각 청크별 결과 저장
                    chunk_questions = []
                    try:
                        if isinstance(문제출제_response, str):
                            json_match = re.search(r'\{.*\}', 문제출제_response, re.DOTALL)
                            if json_match:
                                json_str = json_match.group()
                                parsed_response = json.loads(json_str)
                                chunk_questions.extend(parsed_response['questions'])
                            else:
                                console.print("JSON 형식을 찾을 수 없습니다.")
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        console.print(f"문제 생성 응답 파싱 오류: {e}")

                    # 청크별 결과 파일 저장
                    chunk_result = {
                        "chunk_info": {
                            "original_file": json_content['file_name'],
                            "chunk_number": i + 1,
                            "total_chunks": len(text_chunks),
                            "processed_time": datetime.datetime.now().isoformat()
                        },
                        "term_analysis": 용어분석_response,
                        "concept_analysis": 개념분석_response,
                        "questions": chunk_questions
                    }

                    with open(chunk_path, "w", encoding="utf-8") as f:
                        json.dump(chunk_result, f, ensure_ascii=False, indent=4)

                    console.print(f"청크 {i+1} 처리 완료: {chunk_filename}")

                console.print(f"모든 청크 처리 완료: {base_filename}")
    except Exception as e:
        console.print(f"Error: {e}")

if __name__ == "__main__":
    main()