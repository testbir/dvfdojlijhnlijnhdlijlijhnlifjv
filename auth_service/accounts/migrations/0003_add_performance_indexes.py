# auth_service/accounts/migrations/0003_add_performance_indexes.py

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_emailchangerequest'),
    ]

    operations = [
        # Индекс на email (нормализованный к нижнему регистру)
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customuser_email_lower ON accounts_customuser (LOWER(email));",
            reverse_sql="DROP INDEX IF EXISTS idx_customuser_email_lower;"
        ),
        
        # Композитный индекс для быстрого поиска активных пользователей
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customuser_active_confirmed ON accounts_customuser (is_active, is_email_confirmed);",
            reverse_sql="DROP INDEX IF EXISTS idx_customuser_active_confirmed;"
        ),
        
        # Критичный индекс для поиска кодов подтверждения
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_confirmation_user_purpose_created ON accounts_emailconfirmationcode (user_id, purpose, created_at DESC);",
            reverse_sql="DROP INDEX IF EXISTS idx_confirmation_user_purpose_created;"
        ),
        
        # Индекс для очистки старых кодов
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_confirmation_created_at ON accounts_emailconfirmationcode (created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_confirmation_created_at;"
        ),
    ]