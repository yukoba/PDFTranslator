import base64
import io
from typing import Optional, Literal

from PIL import Image
from google import genai  # type: ignore
from openai import OpenAI

ModelType = Literal["gemini-3-flash-preview", "gpt-5-mini"]


class Translator:
    def __init__(self, model_type: ModelType, api_key: str):
        self.model_type = model_type
        self.api_key = api_key

        if model_type == "gpt-5-mini":
            self.client = OpenAI(api_key=api_key)
        elif model_type == "gemini-3-flash-preview":
            self.client = genai.Client(api_key=api_key)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def _image_to_base64(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _get_prompt(
            self, target_language: str, previous_context: Optional[str] = None
    ) -> str:
        base_prompt = (
            f"提供された画像（学術論文のページ）の内容を読み取り、指定された翻訳先の言語（{target_language}）に翻訳してください。"
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
            image: Image.Image,
            target_language: str,
            previous_context: Optional[str] = None,
    ) -> str:
        prompt = self._get_prompt(target_language, previous_context)

        if self.model_type == "gpt-5-mini":
            return self._translate_with_openai(image, prompt)
        elif self.model_type == "gemini-3-flash-preview":
            return self._translate_with_gemini(image, prompt)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def _translate_with_openai(self, image: Image.Image, prompt: str) -> str:
        base64_image = self._image_to_base64(image)

        response = self.client.chat.completions.create(  # type: ignore
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_completion_tokens=20_000,
        )
        return str(response.choices[0].message.content or "")

    def _translate_with_gemini(self, image: Image.Image, prompt: str) -> str:
        response = self.client.models.generate_content(  # type: ignore  # type: ignore
            model="gemini-3-flash-preview", contents=[prompt, image]
        )
        return str(response.text)
