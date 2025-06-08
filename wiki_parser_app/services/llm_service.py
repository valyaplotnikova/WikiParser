from openai import AsyncOpenAI

from wiki_parser_app.models.articles import Article


class SummaryService:

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    async def generate_summary(self, article: Article):

        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Напиши краткое резюме статьи"},
                {"role": "user", "content": article.content[:8000]},
            ],
            stream=False
        )

        return response.choices[0].message.content
