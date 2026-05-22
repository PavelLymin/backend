import json
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.db_helper import db_helper
from models.tables import Recipe, Cuisine, Allergen, Ingredient, RecipeAllergens, RecipeIngredients, MeasurementEnum
from models.recipe_generation import GeneratedRecipeSchema
from openai import AsyncOpenAI

from task_queue.broker import broker


logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.api.router_key,
    base_url="https://openrouter.ai/api/v1",
)


def get_json_schema():
    schema = GeneratedRecipeSchema.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "Recipe",
            "schema": schema,
            "strict": True,
        },
    }


async def generate_recipe_with_llm(prompt: str) -> dict:
    try:
        response = await client.beta.chat.completions.parse(
            model="openrouter/auto",
            messages=[
                {
                    "role": "system",
                    "content": """Ты - профессиональный шеф-повар. Создавай рецепты на основе пожеланий пользователя.
                    Всегда возвращай полный рецепт с названием, описанием, списком ингредиентов с точными количествами и единицами измерения, временем готовки и сложностью.
                    Определи кухню (например, итальянская, русская, азиатская и т.д.).
                    Укажи потенциальные аллергены (молочные продукты, орехи, глютен, морепродукты и т.д.).""",
                }
                ,
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format=get_json_schema(),
            temperature=0.7,
        )
        
        recipe_data = json.loads(response.choices[0].message.content)
        logger.info(f"Успешно сгенерирован рецепт: {recipe_data.get('title')}")
        return recipe_data
    except Exception as e:
        logger.error(f"Ошибка при генерации рецепта через LLM: {e}")
        raise


async def get_or_create_cuisine(session: AsyncSession, cuisine_name: str) -> int:
    stmt = select(Cuisine).where(Cuisine.name == cuisine_name)
    result = await session.execute(stmt)
    cuisine = result.scalar_one_or_none()
    
    if not cuisine:
        cuisine = Cuisine(name=cuisine_name)
        session.add(cuisine)
        await session.flush()
        logger.info(f"Создана новая кухня: {cuisine_name}")
    
    return cuisine.id


async def get_or_create_ingredient(session: AsyncSession, ingredient_name: str) -> int:
    stmt = select(Ingredient).where(Ingredient.name == ingredient_name)
    result = await session.execute(stmt)
    ingredient = result.scalar_one_or_none()
    
    if not ingredient:
        ingredient = Ingredient(name=ingredient_name)
        session.add(ingredient)
        await session.flush()
        logger.info(f"Создан новый ингредиент: {ingredient_name}")
    
    return ingredient.id


async def get_or_create_allergen(session: AsyncSession, allergen_name: str) -> int:
    stmt = select(Allergen).where(Allergen.name == allergen_name)
    result = await session.execute(stmt)
    allergen = result.scalar_one_or_none()
    
    if not allergen:
        allergen = Allergen(name=allergen_name)
        session.add(allergen)
        await session.flush()
        logger.info(f"Создан новый аллерген: {allergen_name}")
    
    return allergen.id


@broker.task(retry_on_error=True)
async def generate_recipe_task(
    prompt: str,
    user_id: int,
) -> None:
        recipe_data = await generate_recipe_with_llm(prompt)
        generated_recipe = GeneratedRecipeSchema(**recipe_data)
        
        async with db_helper.session_factory() as session:
            cuisine_id = await get_or_create_cuisine(session, generated_recipe.cuisine_name)
            recipe = Recipe(
                cuisine_id=cuisine_id,
                title=generated_recipe.title,
                description=generated_recipe.description,
                cooking_time=generated_recipe.cooking_time,
                difficulty=generated_recipe.difficulty,
                author_id=user_id,
            )
            session.add(recipe)
            await session.flush()
            
            for ingredient_data in generated_recipe.ingredients:
                ingredient_id = await get_or_create_ingredient(session, ingredient_data.name)
                measurement_map = {
                    "GRAMS": MeasurementEnum.GRAMS,
                    "PIECES": MeasurementEnum.PIECES,
                    "MILLILITERS": MeasurementEnum.MILLILITERS,
                }
                measurement = measurement_map.get(ingredient_data.measurement.value, MeasurementEnum.GRAMS)
                session.add(
                        RecipeIngredients(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient_id,
                        quantity=ingredient_data.quantity,
                        measurement=measurement,
                    )
                )
            
            for allergen_name in generated_recipe.allergens:
                allergen_id = await get_or_create_allergen(session, allergen_name)
                allergen = await session.get(Allergen, allergen_id)
                session.add(
                    RecipeAllergens(
                        recipe_id=recipe.id,
                        allergen_id=allergen.id,
                    )
                )
            
            await session.commit()
            
            logger.info(f"Рецепт успешно сохранен в БД с ID: {recipe.id}")
            
            return {
                "success": True,
                "recipe_id": recipe.id,
                "title": recipe.title,
                "message": f"Рецепт '{recipe.title}' успешно создан",
            }
