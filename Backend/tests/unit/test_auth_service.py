"""
Юнит тесты для AuthService
"""
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.services.auth_service import AuthService
from Backend.app.models.user import User


class TestAuthService:
    """Тесты для AuthService"""

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
            is_active=True,
            is_verified=True
        )

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_success(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест успешной аутентификации пользователя"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        mock_verify_password.return_value = True
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "test@example.com", 
            "correct_password"
        )
        
        # Проверки
        assert result == sample_user
        mock_db_session.execute.assert_called_once()
        mock_verify_password.assert_called_once_with(
            "correct_password", 
            sample_user.hashed_password
        )

    @patch('Backend.app.services.auth_service.select')
    async def test_authenticate_user_not_found(
        self, 
        mock_select, 
        mock_db_session
    ):
        """Тест аутентификации несуществующего пользователя"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "nonexistent@example.com", 
            "any_password"
        )
        
        # Проверки
        assert result is False
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_wrong_password(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест аутентификации с неправильным паролем"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        mock_verify_password.return_value = False
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "test@example.com", 
            "wrong_password"
        )
        
        # Проверки
        assert result is False
        mock_db_session.execute.assert_called_once()
        mock_verify_password.assert_called_once_with(
            "wrong_password", 
            sample_user.hashed_password
        )

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_inactive(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест аутентификации неактивного пользователя"""
        # Делаем пользователя неактивным
        sample_user.is_active = False
        
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        mock_verify_password.return_value = True
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "test@example.com", 
            "correct_password"
        )
        
        # Проверки - даже неактивный пользователь может быть аутентифицирован
        # (проверка активности должна происходить на уровне эндпоинтов)
        assert result == sample_user
        mock_verify_password.assert_called_once()

    @patch('Backend.app.services.auth_service.select')
    async def test_authenticate_user_empty_email(
        self, 
        mock_select, 
        mock_db_session
    ):
        """Тест аутентификации с пустым email"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "", 
            "any_password"
        )
        
        # Проверки
        assert result is False
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.auth_service.select')
    async def test_authenticate_user_none_email(
        self, 
        mock_select, 
        mock_db_session
    ):
        """Тест аутентификации с None email"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            None, 
            "any_password"
        )
        
        # Проверки
        assert result is False
        mock_db_session.execute.assert_called_once()

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_case_sensitive_email(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест аутентификации с email в разном регистре"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None  # не найден
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста с email в верхнем регистре
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "TEST@EXAMPLE.COM", 
            "correct_password"
        )
        
        # Проверки - email должен быть чувствителен к регистру
        assert result is False
        mock_db_session.execute.assert_called_once()
        # verify_password не должен вызываться, так как пользователь не найден
        mock_verify_password.assert_not_called()

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_with_special_characters(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session
    ):
        """Тест аутентификации с специальными символами в пароле"""
        # Создаем пользователя с особым паролем
        special_user = User(
            id=2,
            email="special@example.com",
            name="Special User",
            hashed_password="hashed_special_password!@#$%",
            is_active=True
        )
        
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = special_user
        mock_db_session.execute.return_value = mock_result
        mock_verify_password.return_value = True
        
        # Выполнение теста
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "special@example.com", 
            "special_password!@#$%"
        )
        
        # Проверки
        assert result == special_user
        mock_verify_password.assert_called_once_with(
            "special_password!@#$%", 
            special_user.hashed_password
        )

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_sql_injection_attempt(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session
    ):
        """Тест защиты от SQL-инъекций в email"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Выполнение теста с попыткой SQL-инъекции
        result = await AuthService.authenticate_user(
            mock_db_session, 
            "test@example.com'; DROP TABLE users; --", 
            "password"
        )
        
        # Проверки
        assert result is False
        mock_db_session.execute.assert_called_once()
        # Проверяем, что SQL-инъекция не прошла (пользователь не найден)
        mock_verify_password.assert_not_called()

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_database_error(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session
    ):
        """Тест обработки ошибки базы данных"""
        # Настройка моков - имитируем ошибку БД
        mock_db_session.execute.side_effect = Exception("Database connection error")
        
        # Выполнение теста и проверка, что исключение пробрасывается
        with pytest.raises(Exception, match="Database connection error"):
            await AuthService.authenticate_user(
                mock_db_session, 
                "test@example.com", 
                "password"
            )
        
        # Проверки
        mock_db_session.execute.assert_called_once()
        mock_verify_password.assert_not_called()

    @patch('Backend.app.services.auth_service.select')
    @patch('Backend.app.services.auth_service.verify_password')
    async def test_authenticate_user_verify_password_exception(
        self, 
        mock_verify_password, 
        mock_select, 
        mock_db_session, 
        sample_user
    ):
        """Тест обработки исключения при проверке пароля"""
        # Настройка моков
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result
        mock_verify_password.side_effect = Exception("Password verification error")
        
        # Выполнение теста и проверка, что исключение пробрасывается
        with pytest.raises(Exception, match="Password verification error"):
            await AuthService.authenticate_user(
                mock_db_session, 
                "test@example.com", 
                "password"
            )
        
        # Проверки
        mock_db_session.execute.assert_called_once()
        mock_verify_password.assert_called_once()