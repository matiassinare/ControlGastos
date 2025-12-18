-- =========================================
-- MIGRACIÓN: Agregar campo statement_period
-- =========================================
-- Fecha: 2024-12-17
-- Propósito: Agregar campo para organizar transacciones por mes de resumen

-- Agregar columna statement_period si no existe
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS statement_period TEXT;

-- Crear índice para búsquedas por período
CREATE INDEX IF NOT EXISTS idx_transactions_statement_period
ON transactions(statement_period);

-- Renombrar columna 'cuota' a 'installments' si existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'transactions'
        AND column_name = 'cuota'
    ) THEN
        ALTER TABLE transactions RENAME COLUMN cuota TO installments;
    END IF;
END $$;

-- Agregar columna installments si no existe (por si la tabla es nueva)
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS installments TEXT;

-- Comentarios
COMMENT ON COLUMN transactions.statement_period IS 'Período del resumen en formato YYYY-MM (ej: 2024-12)';
COMMENT ON COLUMN transactions.installments IS 'Cuotas en formato X/Y (ej: 3/12)';

-- Actualizar transacciones existentes sin statement_period
-- Usar el año-mes de la fecha de transacción como fallback
UPDATE transactions
SET statement_period = TO_CHAR(date, 'YYYY-MM')
WHERE statement_period IS NULL;
