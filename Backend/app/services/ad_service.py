from sqlalchemy.orm import Session
from typing import List, Optional
from Backend.app.models.ad import Ad
from Backend.app.schemas.ad import AdCreate

class AdService:
    @staticmethod
    def get_ads(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Ad]:
        query = db.query(Ad).filter(Ad.is_active == True)
        
        if type:
            query = query.filter(Ad.type == type)
        if category:
            query = query.filter(Ad.category == category)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_ad(db: Session, ad_data: AdCreate, user_id: int) -> Ad:
        db_ad = Ad(**ad_data.dict(), user_id=user_id)
        db.add(db_ad)
        db.commit()
        db.refresh(db_ad)
        return db_ad
    
    @staticmethod
    def get_user_ads(db: Session, user_id: int) -> List[Ad]:
        return db.query(Ad).filter(Ad.user_id == user_id).all()