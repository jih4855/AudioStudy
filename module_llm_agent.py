import ollama
import google.generativeai as genai
from openai import OpenAI

class LLM_Agent:
    def __init__(self, model_name, provider='ollama', api_key=None):
        self.model_name = model_name
        self.provider = provider.lower()
        self.api_key = api_key
        if self.provider not in ['ollama', 'genai', 'openai']:
            raise ValueError("Provider must be either 'ollama', 'genai' or 'openai'")

    def generate_response(self, system_prompt, user_message, data=None):
        if self.provider == 'ollama':
            return self._generate_ollama_response(system_prompt, user_message, data)
        elif self.provider == 'genai':
            return self._generate_genai_response(system_prompt, user_message, data)
        elif self.provider == 'openai':
            return self._generate_openai_response(system_prompt, user_message, data)

    def _generate_ollama_response(self, system_prompt, user_message, data=None):
        try:
            # messages 리스트 먼저 구성
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # data가 있으면 추가
            if data:
                messages.append({"role": "user", "content": str(data)})

            # 한 번만 호출
            response = ollama.chat(model=self.model_name, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            return f"Error generating response with Ollama: {e}"


    def _generate_genai_response(self, system_prompt, user_message, data=None):
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)

            # 모든 내용을 하나의 문자열로 결합
            combined_prompt = system_prompt
            if user_message:
                combined_prompt += f"\n\n{user_message}"
            if data:
                combined_prompt += f"\n\n데이터: {data}"

            # 문자열 하나만 전달!
            response = model.generate_content(combined_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response with GenAI: {e}"
        
    def _generate_openai_response(self, system_prompt, user_message, data=None):
      try:
          client = OpenAI(api_key=self.api_key)

          # messages 리스트 구성 (Ollama와 유사한 방식)
          messages = [
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_message}
          ]

          # data가 있으면 추가
          if data:
              messages.append({"role": "user", "content": str(data)})

          response = client.chat.completions.create(
              model=self.model_name,
              messages=messages
          )

          return response.choices[0].message.content

      except Exception as e:
          return f"Error generating response with OpenAI: {e}"