from typing import TYPE_CHECKING
from .base import Base

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from .order import Order
    from .order_product_association import OrderProductAssociation


class Product(Base):

    name: Mapped[str]
    price: Mapped[int]
    description: Mapped[str]

    # orders: Mapped[list["Order"]] = relationship(
    #     back_populates="products",
    #     secondary="order_product_association",
    # )

    orders_details: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="product",
    )
