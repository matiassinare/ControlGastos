-- =========================================
-- FIX: Hacer columnas opcionales
-- =========================================
-- Fecha: 2024-12-17
-- Propósito: Permitir que card_type y card_name sean NULL
-- porque los PDFs importados solo tienen el campo "bank"

-- Hacer card_type opcional (permitir NULL)
ALTER TABLE transactions
ALTER COLUMN card_type DROP NOT NULL;

-- Hacer card_name opcional (permitir NULL)
ALTER TABLE transactions
ALTER COLUMN card_name DROP NOT NULL;

-- También podemos hacer bank opcional si es necesario
-- (aunque generalmente siempre lo tenemos)
-- ALTER TABLE transactions
-- ALTER COLUMN bank DROP NOT NULL;

-- Comentarios
COMMENT ON COLUMN transactions.card_type IS 'Tipo de tarjeta (Visa, Amex, etc.) - Opcional';
COMMENT ON COLUMN transactions.card_name IS 'Nombre completo de la tarjeta (Visa BBVA, etc.) - Opcional';
