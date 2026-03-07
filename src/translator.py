import base64
from typing import Optional, Literal

from google import genai
from google.genai.types import ThinkingLevel, Part
from openai import OpenAI

ModelType = Literal["gemini-3-flash-preview", "gpt-5-mini"]


class Translator:
    def __init__(self, model_type: ModelType, api_key: str):
        self.model_type = model_type
        self.api_key = api_key

        if model_type.startswith("gpt-"):
            self.client = OpenAI(api_key=api_key)
        elif model_type.startswith("gemini-"):
            self.client = genai.Client(api_key=api_key)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def _get_prompt(
            self, target_language: str, previous_context: Optional[str] = None
    ) -> str:
        base_prompt = (
            f"提供されたPDFページの内容を読み取り、指定された翻訳先の言語（{target_language}）に翻訳してください。"
            "出力はMarkdown形式とし、見出し、段落、箇条書き、数式、表などの論理構造を可能な限り維持してください。"
            "応答には翻訳結果だけを含めてください。"
        )

        if previous_context:
            base_prompt += (
                f"\n\n前のページからの続きです。以下の文脈を考慮して翻訳してください：\n"
                f"{previous_context}"
            )

        return base_prompt

    def translate_page(
            self,
            pdf_bytes: bytes,
            target_language: str,
            previous_context: Optional[str] = None,
    ) -> str:
        prompt = self._get_prompt(target_language, previous_context)

        if self.model_type.startswith("gpt-"):
            return self._translate_with_openai(pdf_bytes, prompt)
        elif self.model_type.startswith("gemini-"):
            return self._translate_with_gemini(pdf_bytes, prompt)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def _translate_with_openai(self, pdf_bytes: bytes, prompt: str) -> str:
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        response = self.client.chat.completions.create(  # type: ignore
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "file",
                            "file": {
                                "filename": "input.pdf",
                                "file_data": f"data:application/pdf;base64,{base64_pdf}",
                            },
                        },
                    ],
                }
            ],
            max_completion_tokens=20_000,
        )
        return str(response.choices[0].message.content or "")

    def _translate_with_gemini(self, pdf_bytes: bytes, prompt: str) -> str:
        pdf_part = Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        response = self.client.models.generate_content(  # type: ignore
            model="gemini-3-flash-preview",
            contents=[prompt, pdf_part],
            config=genai.types.GenerateContentConfig(
                thinking_config=genai.types.ThinkingConfig(
                    thinking_level=ThinkingLevel.LOW
                )
            ),
        )
        return str(response.text)
