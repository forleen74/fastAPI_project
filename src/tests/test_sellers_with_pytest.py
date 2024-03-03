import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


# Тест на ручку создающую Продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Иван", "last_name": "Иванов", "email": "user@example.com", "password": "password"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert "id" in result_data
    assert result_data["first_name"] == "Иван"
    assert result_data["last_name"] == "Иванов"
    assert result_data["email"] == "user@example.com"
    assert "password" not in result_data


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="Иван", last_name="Иванов", email="user@example.com", password="password")
    seller_2 = sellers.Seller(first_name="Петр", last_name="Петров", email="user_2@example.com", password="password")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Иван", "last_name": "Иванов", "email": "user@example.com", "id": seller.id},
            {"first_name": "Петр", "last_name": "Петров", "email": "user_2@example.com", "id": seller_2.id},
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="Иван", last_name="Иванов", email="user@example.com", password="password")
    seller_2 = sellers.Seller(first_name="Петр", last_name="Петров", email="user_2@example.com", password="password")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_2.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "id": seller.id,
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "user@example.com",
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "count_pages": 104,
                "id": book.id,
            }
        ],
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="Иван", last_name="Иванов", email="user@example.com", password="password")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name="Иван", last_name="Иванов", email="user@example.com", password="password")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"first_name": "Петр", "last_name": "Петров", "email": "user_2@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Петр"
    assert res.last_name == "Петров"
    assert res.email == "user_2@example.com"
    assert res.id == seller.id
