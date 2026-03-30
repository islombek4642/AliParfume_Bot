import pandas as pd
import io
from sqlalchemy import select
from database.models import User, Order, OrderItem
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple

class ExportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def export_users_to_excel(self) -> io.BytesIO:
        query = select(User)
        result = await self.session.execute(query)
        users = result.scalars().all()
        
        data = []
        for u in users:
            data.append({
                "ID": u.telegram_id,
                "Ism": u.full_name,
                "Telefon": u.phone,
                "Til": u.language,
                "Admin": "Ha" if u.is_admin else "Yo'q",
                "Sana": u.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Foydalanuvchilar')
        output.seek(0)
        return output

    async def export_orders_to_excel(self) -> io.BytesIO:
        # Joining for better data
        query = select(Order).order_by(Order.created_at.desc())
        result = await self.session.execute(query)
        orders = result.scalars().all()
        
        data = []
        for o in orders:
            data.append({
                "Buyurtma ID": o.id,
                "User ID": o.user_id,
                "Summa": o.total_price,
                "Status": o.status,
                "Manzil": o.address,
                "Sana": o.created_at.strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Buyurtmalar')
        output.seek(0)
        return output
