
# catalog_service/scripts/init_db_async.py



import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from catalog_service.core.base import Base
from catalog_service.core.config import settings

from urllib.parse import urlparse, urlunparse

def get_async_pg_url(url: str) -> str:
    parsed = urlparse(url)
    if '+asyncpg' in parsed.scheme:
        return url
    async_scheme = parsed.scheme + '+asyncpg'
    return urlunparse(parsed._replace(scheme=async_scheme))

DATABASE_URL = get_async_pg_url(settings.DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)

async def sync_table_schema():
    """Синхронизирует схему таблиц - добавляет недостающие колонки"""
    async with engine.begin() as conn:
        print("🔄 Синхронизируем схему базы данных...")
        
        # Получаем информацию о существующих таблицах и колонках
        result = await conn.execute(text("""
            SELECT table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """))
        
        existing_schema = {}
        for row in result:
            table_name = row.table_name
            if table_name not in existing_schema:
                existing_schema[table_name] = {}
            existing_schema[table_name][row.column_name] = {
                'data_type': row.data_type,
                'is_nullable': row.is_nullable,
                'column_default': row.column_default
            }
        
        # Проходим по всем моделям SQLAlchemy
        for table_name, table in Base.metadata.tables.items():
            print(f"📋 Проверяем таблицу: {table_name}")
            
            # Если таблица не существует, создадим её целиком
            if table_name not in existing_schema:
                print(f"➕ Создаем новую таблицу: {table_name}")
                await conn.run_sync(lambda sync_conn: table.create(sync_conn, checkfirst=True))
                continue
            
            # Проверяем каждую колонку в модели
            for column in table.columns:
                column_name = column.name
                
                if column_name not in existing_schema[table_name]:
                    print(f"➕ Добавляем колонку {table_name}.{column_name}")
                    
                    # Определяем тип колонки
                    column_type = column.type.compile(dialect=conn.dialect)
                    
                    # Определяем nullable
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    
                    # Определяем default значение
                    default_clause = ""
                    if column.default is not None:
                        if column.default.is_scalar:
                            default_value = column.default.arg
                            if isinstance(default_value, str):
                                default_clause = f"DEFAULT '{default_value}'"
                            else:
                                default_clause = f"DEFAULT {default_value}"
                        elif hasattr(column.default, 'arg'):
                            default_clause = f"DEFAULT '{column.default.arg}'"
                    
                    # Создаем SQL для добавления колонки
                    add_column_sql = f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} {column_type} {default_clause} {nullable}
                    """
                    
                    try:
                        await conn.execute(text(add_column_sql))
                        print(f"✅ Колонка {table_name}.{column_name} успешно добавлена!")
                    except Exception as e:
                        print(f"❌ Ошибка при добавлении колонки {table_name}.{column_name}: {e}")
                        # Продолжаем выполнение несмотря на ошибку
                        continue
                else:
                    print(f"✅ Колонка {table_name}.{column_name} уже существует")
        
        print("🎉 Синхронизация схемы завершена!")

async def create_missing_tables():
    """Создает отсутствующие таблицы"""
    async with engine.begin() as conn:
        print("📋 Создаем недостающие таблицы...")
        await conn.run_sync(Base.metadata.create_all)

async def init_db():
    """Инициализация базы данных с автоматической синхронизацией схемы"""
    try:
        print("🚀 Начинаем инициализацию базы данных...")
        
        # Сначала создаем недостающие таблицы
        await create_missing_tables()
        
        # Затем синхронизируем схему (добавляем недостающие колонки)
        await sync_table_schema()
        
        print("✅ Инициализация базы данных завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())