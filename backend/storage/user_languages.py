import aiosqlite


class UserLanguageStorage:
    def __init__(self, database_path: str) -> None:
        self._database_path = database_path

    async def get(self, user_id: int) -> str | None:
        async with aiosqlite.connect(self._database_path) as connection:
            async with connection.execute(
                "SELECT locale FROM user_languages WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
        return str(row[0]) if row else None

    async def set(self, user_id: int, locale: str) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            await connection.execute(
                """
                INSERT INTO user_languages (user_id, locale) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET locale = excluded.locale
                """,
                (user_id, locale),
            )
            await connection.commit()
