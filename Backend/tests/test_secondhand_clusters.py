# Backend/tests/test_secondhand_clusters.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from Backend.app.models.user import Base  # Base общий для всех моделей
from Backend.app.models.secondhand import Secondhand
from Backend.app.services.secondhand_service import SecondhandService

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture
def db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def secondhand_service():
    return SecondhandService()


def create_secondhand(
    db,
    name: str,
    lat: float,
    lng: float,
    address: str = "Test address",
):
    sh = Secondhand(
        name=name,
        address=address,
        latitude=lat,
        longitude=lng,
        phone=None,
        email=None,
        website=None,
        description=None,
        opening_hours=None,
        is_active=True,
    )
    db.add(sh)
    db.commit()
    db.refresh(sh)
    return sh


def test_clusters_group_nearby_points(db, secondhand_service):
    """
    Две точки, находящиеся близко друг к другу, должны попадать в один кластер
    при среднем zoom.
    """
    # Две близкие точки в Москве
    create_secondhand(db, "Shop 1", 55.7558, 37.6173)
    create_secondhand(db, "Shop 2", 55.7560, 37.6175)
    # Одна дальняя точка в СПб
    create_secondhand(db, "Shop 3", 59.9311, 30.3609)

    zoom = 10  # радиус кластера ~15 км по нашей логике
    clusters = secondhand_service.get_clusters_in_bounds(
        db=db,
        zoom=zoom,
        ne_lat=60.0,
        ne_lng=40.0,
        sw_lat=50.0,
        sw_lng=20.0,
    )

    # Должно быть два кластера: один для 2 московских точек, один для Питера
    assert len(clusters) == 2

    counts = sorted(c["count"] for c in clusters)
    assert counts == [1, 2]


def test_clusters_split_on_high_zoom(db, secondhand_service):
    """
    При высоком zoom радиус малого кластера должен быть меньше,
    и точки могут разойтись по разным кластерам.
    """
    # Две точки чуть дальше друг от друга (несколько км)
    create_secondhand(db, "Shop 1", 55.7558, 37.6173)
    create_secondhand(db, "Shop 2", 55.8000, 37.6200)

    zoom = 16  # радиус ~1 км
    clusters = secondhand_service.get_clusters_in_bounds(
        db=db,
        zoom=zoom,
        ne_lat=56.0,
        ne_lng=38.0,
        sw_lat=55.0,
        sw_lng=37.0,
    )

    # Ожидаем два отдельных кластера
    assert len(clusters) == 2
    assert sorted(c["count"] for c in clusters) == [1, 1]


def test_clusters_respect_bounds(db, secondhand_service):
    """
    Проверяем, что точки вне заданных границ карты не попадают в кластеризацию.
    """
    # Москва
    create_secondhand(db, "Moscow Shop", 55.7558, 37.6173)
    # СПб
    create_secondhand(db, "SPB Shop", 59.9311, 30.3609)

    # Границы только вокруг Москвы
    zoom = 10
    clusters = secondhand_service.get_clusters_in_bounds(
        db=db,
        zoom=zoom,
        ne_lat=56.0,
        ne_lng=38.0,
        sw_lat=55.0,
        sw_lng=37.0,
    )

    # Должен быть только один кластер (только Москва)
    assert len(clusters) == 1
    assert clusters[0]["count"] == 1
