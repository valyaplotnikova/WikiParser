from openai import AsyncOpenAI

from wiki_parser_app.models.articles import Article


class SummaryService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    async def generate_summary(self, article: Article) -> str:
        if not article.content:
            raise ValueError("Article content is empty")

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "Напиши краткое резюме статьи на русском языке"
                    },
                    {
                        "role": "user",
                        "content": article.content[:8000]
                    }
                ],
                temperature=0.5,
                max_tokens=512,
                stream=False
            )

            summary = response.choices[0].message.content.strip()
            if not summary:
                raise ValueError("LLM вернул пустой ответ")
            return summary

        except Exception as e:
            raise RuntimeError(f"Ошибка генерации summary: {str(e)}")
