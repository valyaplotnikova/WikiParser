from fastapi import APIRouter, Depends, HTTPException

from wiki_parser_app.dependencies.article_sevice_dep import get_article_repo
from wiki_parser_app.repositories.article_repo import ArticleRepository
from wiki_parser_app.schemas.article import ArticleSummarySchema

router = APIRouter()


@router.get('/summary', response_model=ArticleSummarySchema)
async def get_summary(
        url: str,
        article_repo: ArticleRepository = Depends(get_article_repo)
):
    article = await article_repo.get_by_url(url)
    if not article or not article.summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return ArticleSummarySchema(
        article_id=article.id,
        content=article.summary.content
    )
