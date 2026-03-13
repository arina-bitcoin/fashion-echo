"""
Юнит тесты для AdService
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.services.ad_service import AdService
from Backend.app.models.ad import Ad, AdImage, FavoriteAd, AdStatus
from Backend.app.models.user import User
from Backend.app.schemas.ad import AdCreate, AdUpdate, AdSearch, SortBy


class TestAdService:
    """Тесты для AdService"""

    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Мок сессии базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest_asyncio.fixture
    async def sample_ad(self):
        """Образец объявления для тестов"""
        return Ad(
            id=1,
            title="Тестовая куртка",
            description="Отличная куртка в хорошем состоянии",
            price=1500.0,
            type="sell",
            main_category="clothes",
            sub_category="outerwear",
            season="winter",
            condition="good",
            size="M",
            colors=["black", "blue"],
            tags="куртка зимняя теплая",
            user_id=1,
            status=AdStatus.ACTIVE,
            view_count=10,
            favorite_count=2,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest_asyncio.fixture
    async def sample_user(self):
        """Образец пользователя для тестов"""
        return User(
            id=1,
            email="test@example.com",
            name="Test User",
            hashed_password="hashed_password",
            is_active=True
        )

    async def test_process_ad_images(self, sample_ad):
        """Тест обработки изображений объявления"""
        # Создаем мок изображений
        mock_image1 = Mock()
        mock_image1.file_path = "/path/to/image1.jpg"
        mock_image2 = Mock()
        mock_image2.file_path = "/path/to/image2.jpg"
        
        sample_ad.images = [mock_image1, mock_image2]
        
        # Тестируем обработку
        result = AdService._process_ad_images(sample_ad)
        
        assert hasattr(result, '_image_urls')
        assert result._image_urls == ["/path/to/image1.jpg", "/path/to/image2.jpg"]

    async def test_process_ad_images_empty(self, sample_ad):
        """Тест обработки объявления без изображений"""
        sample_ad.images = []
        
        result = AdService._process_ad_images(sample_ad)
        
        assert hasattr(result, '_image_urls')
        assert result._image_urls == []

    @patch('Backend.app.services.ad_service.select')
    async def test_get_ad_by_id(self, mock_select, mock_db_session, sample_ad):
        """Тест получения объявления по ID"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_ad
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.get_ad(mock_db_session, 1)
        
        # Проверки
        assert result == sample_ad
        assert hasattr(result, '_image_urls')
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.ad_service.select')
    async def test_get_ad_not_found(self, mock_select, mock_db_session):
        """Тест получения несуществующего объявления"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.get_ad(mock_db_session, 999)
        
        # Проверки
        assert result is None
        mock_db_session.execute.assert_called_once()

    async def test_create_ad(self, mock_db_session, sample_user):
        """Тест создания объявления"""
        # Подготовка данных
        ad_data = AdCreate(
            title="Новая куртка",
            description="Описание куртки",
            price=2000.0,
            type="sell",
            main_category="clothes",
            sub_category="outerwear",
            season="winter",
            condition="new",
            size="L",
            colors=["red"],
            tags="куртка новая"
        )
        
        # Настройка моков
        mock_db_session.add = Mock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await AdService.create_ad(mock_db_session, ad_data, sample_user.id)
        
        # Проверки
        assert isinstance(result, Ad)
        assert result.title == ad_data.title
        assert result.user_id == sample_user.id
        assert result.status == AdStatus.ACTIVE
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.ad_service.select')
    async def test_update_ad_success(self, mock_select, mock_db_session, sample_ad):
        """Тест успешного обновления объявления"""
        # Подготовка данных
        update_data = AdUpdate(
            title="Обновленная куртка",
            price=1800.0,
            description="Обновленное описание"
        )
        
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_ad
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await AdService.update_ad(
            mock_db_session, 
            sample_ad.id, 
            sample_ad.user_id, 
            update_data
        )
        
        # Проверки
        assert result is not None
        assert result.title == "Обновленная куртка"
        assert result.price == 1800.0
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.ad_service.select')
    async def test_update_ad_unauthorized(self, mock_select, mock_db_session):
        """Тест обновления объявления неавторизованным пользователем"""
        # Настройка моков - объявление не найдено для данного пользователя
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        update_data = AdUpdate(title="Попытка обновления")
        
        # Выполнение теста
        result = await AdService.update_ad(
            mock_db_session, 
            1, 
            999,  # неправильный user_id
            update_data
        )
        
        # Проверки
        assert result is None

    @patch('Backend.app.services.ad_service.select')
    async def test_delete_ad_soft(self, mock_select, mock_db_session, sample_ad):
        """Тест мягкого удаления объявления"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_ad
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()
        
        # Выполнение теста
        result = await AdService.delete_ad(
            mock_db_session, 
            sample_ad.id, 
            sample_ad.user_id, 
            soft_delete=True
        )
        
        # Проверки
        assert result is True
        assert sample_ad.status == AdStatus.INACTIVE

    async def test_increment_view_count(self, mock_db_session):
        """Тест увеличения счетчика просмотров"""
        # Настройка моков
        mock_db_session.execute = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        # Выполнение теста
        await AdService.increment_view_count(mock_db_session, 1)
        
        # Проверки
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.ad_service.select')
    async def test_add_to_favorites_success(self, mock_select, mock_db_session, sample_ad):
        """Тест успешного добавления в избранное"""
        # Настройка моков
        mock_result_check = Mock()
        mock_result_check.scalar_one_or_none.return_value = None  # не в избранном
        
        mock_result_ad = Mock()
        mock_result_ad.scalar_one_or_none.return_value = sample_ad
        
        mock_db_session.execute.side_effect = [mock_result_check, mock_result_ad]
        mock_db_session.add = Mock()
        mock_db_session.commit = AsyncMock()
        
        # Выполнение теста
        result = await AdService.add_to_favorites(mock_db_session, 1, 1)
        
        # Проверки
        assert result is True
        mock_db_session.add.assert_called_once()

    @patch('Backend.app.services.ad_service.select')
    async def test_add_to_favorites_already_exists(self, mock_select, mock_db_session):
        """Тест добавления в избранное уже существующего объявления"""
        # Настройка моков - объявление уже в избранном
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = Mock()  # уже существует
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.add_to_favorites(mock_db_session, 1, 1)
        
        # Проверки
        assert result is False

    @patch('Backend.app.services.ad_service.select')
    async def test_remove_from_favorites_success(self, mock_select, mock_db_session):
        """Тест успешного удаления из избранного"""
        # Создаем мок избранного объявления
        mock_favorite = Mock()
        
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_favorite
        mock_db_session.execute.return_value = mock_result
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        # Выполнение теста
        result = await AdService.remove_from_favorites(mock_db_session, 1, 1)
        
        # Проверки
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_favorite)

    @patch('Backend.app.services.ad_service.select')
    async def test_is_favorite_true(self, mock_select, mock_db_session):
        """Тест проверки - объявление в избранном"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = Mock()  # найдено
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.is_favorite(mock_db_session, 1, 1)
        
        # Проверки
        assert result is True

    @patch('Backend.app.services.ad_service.select')
    async def test_is_favorite_false(self, mock_select, mock_db_session):
        """Тест проверки - объявление не в избранном"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None  # не найдено
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.is_favorite(mock_db_session, 1, 1)
        
        # Проверки
        assert result is False

    @patch('Backend.app.services.ad_service.select')
    async def test_get_ads_with_filters(self, mock_select, mock_db_session, sample_ad):
        """Тест получения объявлений с фильтрами"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_ad]
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.get_ads(
            mock_db_session,
            skip=0,
            limit=10,
            status="active",
            type="sell",
            main_category="clothes",
            min_price=1000.0,
            max_price=2000.0
        )
        
        # Проверки
        assert len(result) == 1
        assert result[0] == sample_ad
        assert hasattr(result[0], '_image_urls')

    async def test_get_ad_stats(self, mock_db_session, sample_ad):
        """Тест получения статистики объявления"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_ad
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AdService.get_ad_stats(
            mock_db_session, 
            sample_ad.id, 
            sample_ad.user_id
        )
        
        # Проверки
        assert result is not None
        assert result["views"] == 10
        assert result["favorites"] == 2
        assert "created_at" in result
        assert "updated_at" in result
        assert "status" in result

    async def test_toggle_ad_status_activate(self, mock_db_session, sample_ad):
        """Тест активации объявления"""
        # Настройка объявления как неактивного
        sample_ad.status = AdStatus.INACTIVE
        
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_ad
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await AdService.toggle_ad_status(
            mock_db_session, 
            sample_ad.id, 
            sample_ad.user_id, 
            activate=True
        )
        
        # Проверки
        assert result is not None
        assert result.status == AdStatus.ACTIVE

    async def test_toggle_ad_status_deactivate(self, mock_db_session, sample_ad):
        """Тест деактивации объявления"""
        # Настройка объявления как активного
        sample_ad.status = AdStatus.ACTIVE
        
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_ad
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await AdService.toggle_ad_status(
            mock_db_session, 
            sample_ad.id, 
            sample_ad.user_id, 
            activate=False
        )
        
        # Проверки
        assert result is not None
        assert result.status == AdStatus.INACTIVE