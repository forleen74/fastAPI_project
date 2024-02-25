from pydantic import BaseModel, EmailStr

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerWithBooks"]

from src.schemas import ReturnedBookWithoutSellerId


# Базовый класс "Продавец", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):
    id: int


# Класс, также валидирующий исходящие данные. Он содержит books
class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBookWithoutSellerId]


# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
