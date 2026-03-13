"""
Юнит тесты для UserService
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.services.user_service import UserService
from Backend.app.models.user import User
from Backend.app.schemas.user import UserUpdate, ChangePasswordRequest


class TestUserService:
    """Тесты для UserService"""

    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Мок сессии базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest_asyncio.fixture
    async def sample_user(self):
        """Образец пользователя для тестов"""
        return User(
            id=1,
            email="test@example.com",
            name="Test User",
            hashed_password="hashed_password",
            phone="+1234567890",
            is_active=True,
            is_verified=True,
            avatar=None
        )

    @patch('Backend.app.services.user_service.select')
    async def test_get_user_by_id_success(
        self, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешного получения пользователя по ID"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await UserService.get_user_by_id(mock_db_session, 1)
        
        # Проверки
        assert result == sample_user
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.user_service.select')
    async def test_get_user_by_id_not_found(
        self, 
        mock_select, 
        mock_db_session
    ):
        """Тест получения несуществующего пользователя по ID"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста и проверка исключения
        with pytest.raises(ValueError, match="User not found"):
            await UserService.get_user_by_id(mock_db_session, 999)
        
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    async def test_get_user_profile(
        self, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест получения профиля пользователя"""
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        
        # Выполнение теста
        result = await UserService.get_user_profile(mock_db_session, 1)
        
        # Проверки
        assert result == sample_user
        mock_get_user_by_id.assert_called_once_with(mock_db_session, 1)

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.select')
    @patch('Backend.app.services.user_service.func')
    async def test_update_user_profile_success(
        self, 
        mock_func,
        mock_select, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешного обновления профиля пользователя"""
        # Подготовка данных
        update_data = UserUpdate(
            name="Updated Name",
            phone="+9876543210"
        )
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        mock_func.now.return_value = "mocked_timestamp"
        
        # Выполнение теста
        result = await UserService.update_user_profile(
            mock_db_session, 
            1, 
            update_data
        )
        
        # Проверки
        assert result.name == "Updated Name"
        assert result.phone == "+9876543210"
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.select')
    async def test_update_user_profile_email_conflict(
        self, 
        mock_select,
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест обновления профиля с конфликтом email"""
        # Подготовка данных
        update_data = UserUpdate(email="existing@example.com")
        
        # Создаем другого пользователя с таким же email
        existing_user = User(
            id=2,
            email="existing@example.com",
            name="Existing User"
        )
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста и проверка исключения
        with pytest.raises(ValueError, match="Email already registered"):
            await UserService.update_user_profile(
                mock_db_session, 
                1, 
                update_data
            )

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.select')
    async def test_update_user_profile_same_email(
        self, 
        mock_select,
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест обновления профиля с тем же email"""
        # Подготовка данных - тот же email
        update_data = UserUpdate(
            email="test@example.com",  # тот же email
            name="Updated Name"
        )
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await UserService.update_user_profile(
            mock_db_session, 
            1, 
            update_data
        )
        
        # Проверки - email не должен проверяться на уникальность
        assert result.name == "Updated Name"
        mock_db_session.commit.assert_called_once()
        # select не должен вызываться для проверки email
        mock_db_session.execute.assert_not_called()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.verify_password')
    @patch('Backend.app.services.user_service.get_password_hash')
    @patch('Backend.app.services.user_service.func')
    async def test_change_password_success(
        self, 
        mock_func,
        mock_get_password_hash,
        mock_verify_password, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешной смены пароля"""
        # Подготовка данных
        password_data = ChangePasswordRequest(
            current_password="old_password",
            new_password="new_password"
        )
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_verify_password.return_value = True
        mock_get_password_hash.return_value = "new_hashed_password"
        mock_func.now.return_value = "mocked_timestamp"
        mock_db_session.commit = AsyncMock()
        
        # Выполнение теста
        await UserService.change_password(
            mock_db_session, 
            1, 
            password_data
        )
        
        # Проверки
        assert sample_user.hashed_password == "new_hashed_password"
        mock_verify_password.assert_called_once_with(
            "old_password", 
            "hashed_password"
        )
        mock_get_password_hash.assert_called_once_with("new_password")
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.verify_password')
    async def test_change_password_wrong_current(
        self, 
        mock_verify_password, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест смены пароля с неправильным текущим паролем"""
        # Подготовка данных
        password_data = ChangePasswordRequest(
            current_password="wrong_password",
            new_password="new_password"
        )
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_verify_password.return_value = False
        
        # Выполнение теста и проверка исключения
        with pytest.raises(ValueError, match="Current password is incorrect"):
            await UserService.change_password(
                mock_db_session, 
                1, 
                password_data
            )
        
        mock_verify_password.assert_called_once()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.file_service')
    @patch('Backend.app.services.user_service.func')
    async def test_upload_avatar_success(
        self, 
        mock_func,
        mock_file_service, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешной загрузки аватара"""
        # Подготовка данных
        mock_file = Mock()
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_file_service.save_avatar.return_value = "/path/to/new_avatar.jpg"
        mock_func.now.return_value = "mocked_timestamp"
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await UserService.upload_avatar(
            mock_db_session, 
            1, 
            mock_file
        )
        
        # Проверки
        assert result.avatar == "/path/to/new_avatar.jpg"
        mock_file_service.save_avatar.assert_called_once_with(mock_file, 1)
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.file_service')
    @patch('Backend.app.services.user_service.func')
    async def test_upload_avatar_replace_existing(
        self, 
        mock_func,
        mock_file_service, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест загрузки аватара с заменой существующего"""
        # Настройка пользователя с существующим аватаром
        sample_user.avatar = "/path/to/old_avatar.jpg"
        
        # Подготовка данных
        mock_file = Mock()
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_file_service.save_avatar.return_value = "/path/to/new_avatar.jpg"
        mock_func.now.return_value = "mocked_timestamp"
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await UserService.upload_avatar(
            mock_db_session, 
            1, 
            mock_file
        )
        
        # Проверки
        assert result.avatar == "/path/to/new_avatar.jpg"
        mock_file_service.delete_avatar.assert_called_once_with("/path/to/old_avatar.jpg")
        mock_file_service.save_avatar.assert_called_once_with(mock_file, 1)

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.file_service')
    @patch('Backend.app.services.user_service.func')
    async def test_delete_avatar_success(
        self, 
        mock_func,
        mock_file_service, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешного удаления аватара"""
        # Настройка пользователя с аватаром
        sample_user.avatar = "/path/to/avatar.jpg"
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_func.now.return_value = "mocked_timestamp"
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Выполнение теста
        result = await UserService.delete_avatar(mock_db_session, 1)
        
        # Проверки
        assert result.avatar is None
        mock_file_service.delete_avatar.assert_called_once_with("/path/to/avatar.jpg")
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    async def test_delete_avatar_not_found(
        self, 
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест удаления несуществующего аватара"""
        # Настройка пользователя без аватара
        sample_user.avatar = None
        
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        
        # Выполнение теста и проверка исключения
        with pytest.raises(ValueError, match="Avatar not found"):
            await UserService.delete_avatar(mock_db_session, 1)

    @patch('Backend.app.services.user_service.UserService.get_user_by_id')
    @patch('Backend.app.services.user_service.func')
    async def test_deactivate_user(
        self, 
        mock_func,
        mock_get_user_by_id, 
        mock_db_session, 
        sample_user
    ):
        """Тест деактивации пользователя"""
        # Настройка моков
        mock_get_user_by_id.return_value = sample_user
        mock_func.now.return_value = "mocked_timestamp"
        mock_db_session.commit = AsyncMock()
        
        # Выполнение теста
        await UserService.deactivate_user(mock_db_session, 1)
        
        # Проверки
        assert sample_user.is_active is False
        mock_db_session.commit.assert_called_once()

    @patch('Backend.app.services.user_service.select')
    async def test_get_user_by_email_success(
        self, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешного получения пользователя по email"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await UserService.get_user_by_email(
            mock_db_session, 
            "test@example.com"
        )
        
        # Проверки
        assert result == sample_user
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.user_service.select')
    async def test_get_user_by_email_not_found(
        self, 
        mock_select, 
        mock_db_session
    ):
        """Тест получения несуществующего пользователя по email"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста и проверка исключения
        with pytest.raises(ValueError, match="User not found"):
            await UserService.get_user_by_email(
                mock_db_session, 
                "nonexistent@example.com"
            )
        
        mock_db_session.execute.assert_called_once()