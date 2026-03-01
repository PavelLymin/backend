from fastapi import APIRouter, Path, Query, Form
from typing import Annotated
from models import  Item, FilterParams
from config import settings

router = APIRouter(
    tags=["Item"],
    prefix=settings.url.items,
)

# Request Body
@router.post('')
async def create_item(item: Item):
    return item

# Query Parameters and String Validations
@router.get('')
async def read_items(q: Annotated[str, Query(min_length=3, max_length=50)] = 'fixedquery'):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# Query Parameter Models
@router.get('/filters')
async def read_items_with_filters(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

# Path Parameters and Numeric Validations¶
@router.get('/{item_id}')
async def read_items(
    *,
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=100)],
    q: Annotated[str | None, Query(alias="item-query")] = None,
    size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    results.update({"size": size})
    return results

# Body - Nested Models
@router.put('{item_id}')
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

