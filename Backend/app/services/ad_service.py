from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from Backend.app.models.ad import Ad
from Backend.app.schemas.ad import AdCreate

class AdService:
    @staticmethod
    async def get_ads(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        type: Optional[str] = None,
        category: Optional[str] = None
    ) -> list[Ad]:
        # Создаем базовый запрос
        stmt = select(Ad).filter(Ad.is_active == True)
        
        if type:
            stmt = stmt.filter(Ad.type == type)
        if category:
            stmt = stmt.filter(Ad.category == category)
        
        # Применяем пагинацию
        stmt = stmt.offset(skip).limit(limit)
        
        # Выполняем запрос
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def create_ad(db: AsyncSession, ad_data: AdCreate, user_id: int) -> Ad:
        db_ad = Ad(**ad_data.dict(), user_id=user_id)
        db.add(db_ad)
        await db.commit()
        await db.refresh(db_ad)
        return db_ad
    
    @staticmethod
    async def get_ad(db: AsyncSession, ad_id: int) -> Optional[Ad]:
        """Получить объявление по ID"""
        stmt = select(Ad).filter(Ad.id == ad_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_ads(db: AsyncSession, user_id: int) -> List[Ad]:
        stmt = select(Ad).filter(Ad.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
