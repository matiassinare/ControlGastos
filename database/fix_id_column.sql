-- =========================================
-- FIX: Cambiar columna ID de BIGSERIAL a UUID
-- =========================================
-- Fecha: 2024-12-17
-- Propósito: Permitir usar UUIDs como identificadores únicos

-- Paso 1: Borrar todas las transacciones existentes (temporal)
TRUNCATE TABLE transactions;

-- Paso 2: Eliminar la columna id actual
ALTER TABLE transactions DROP COLUMN id;

-- Paso 3: Agregar nueva columna id como UUID con valor por defecto
ALTER TABLE transactions ADD COLUMN id UUID DEFAULT gen_random_uuid() PRIMARY KEY;

-- Paso 4: Reordenar columnas (mover id al principio)
-- PostgreSQL no permite reordenar directamente, pero está bien que esté al final

-- Comentario
COMMENT ON COLUMN transactions.id IS 'Identificador único UUID de la transacción';
