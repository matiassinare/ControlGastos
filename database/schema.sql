-- =========================================
-- EXPENSE TRACKER - DATABASE SCHEMA
-- =========================================
-- PostgreSQL 15+ (Supabase)
-- Ejecutar este script en el SQL Editor de Supabase

-- =========================================
-- TABLA: transactions
-- =========================================
-- Almacena todas las transacciones (scrapeadas y manuales)
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL DEFAULT auth.uid(),

    -- Información de la tarjeta
    bank TEXT NOT NULL,                    -- 'BBVA', 'Galicia'
    card_type TEXT NOT NULL,               -- 'Visa', 'Amex'
    card_name TEXT NOT NULL,               -- 'Visa BBVA', 'Amex Galicia'

    -- Detalles de la transacción
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    currency TEXT DEFAULT 'ARS',           -- 'ARS', 'USD'
    cuota TEXT,                            -- '1/6', '2/12', NULL (pago único)

    -- Metadata
    is_manual BOOLEAN DEFAULT FALSE,       -- TRUE si fue agregada manualmente
    category TEXT,                         -- 'Subscripciones', 'Comida', 'Transporte', etc.
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Evitar duplicados: misma transacción no puede repetirse
    CONSTRAINT unique_transaction UNIQUE(user_id, bank, card_name, date, description, amount)
);

-- =========================================
-- TABLA: budget
-- =========================================
-- Almacena el presupuesto mensual del usuario
CREATE TABLE IF NOT EXISTS budget (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL DEFAULT auth.uid(),

    -- Período
    year_month TEXT NOT NULL,              -- '2024-12', '2025-01'

    -- Ingresos
    gross_salary NUMERIC(10,2),            -- Salario bruto (opcional)
    net_salary NUMERIC(10,2),              -- Salario neto (opcional)

    -- Límite de gastos
    budget_limit NUMERIC(10,2) NOT NULL,   -- Presupuesto mensual máximo

    -- Notas
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Un presupuesto por mes por usuario
    CONSTRAINT unique_budget_month UNIQUE(user_id, year_month)
);

-- =========================================
-- TABLA: categories
-- =========================================
-- Categorías personalizadas del usuario
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL DEFAULT auth.uid(),

    -- Información de la categoría
    name TEXT NOT NULL,
    color TEXT,                            -- Color hex: '#FF5733'
    icon TEXT,                             -- Emoji: '🍔', '🚗', '🎮'

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Categoría única por usuario
    CONSTRAINT unique_category_name UNIQUE(user_id, name)
);

-- =========================================
-- INDEXES PARA PERFORMANCE
-- =========================================
-- Transacciones: búsqueda por usuario y fecha
CREATE INDEX IF NOT EXISTS idx_transactions_user_date
ON transactions(user_id, date DESC);

-- Transacciones: filtro por año-mes
-- Usar EXTRACT() en lugar de LEFT() para evitar error de IMMUTABLE
CREATE INDEX IF NOT EXISTS idx_transactions_year_month
ON transactions(user_id, EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date));

-- Transacciones: búsqueda por categoría
CREATE INDEX IF NOT EXISTS idx_transactions_category
ON transactions(user_id, category) WHERE category IS NOT NULL;

-- Budget: búsqueda por usuario y mes
CREATE INDEX IF NOT EXISTS idx_budget_user_month
ON budget(user_id, year_month);

-- =========================================
-- ROW LEVEL SECURITY (RLS)
-- =========================================
-- Cada usuario solo ve sus propios datos

-- Habilitar RLS en todas las tablas
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE budget ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Policies para transactions
CREATE POLICY "Users can view their own transactions"
ON transactions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own transactions"
ON transactions FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own transactions"
ON transactions FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own transactions"
ON transactions FOR DELETE
USING (auth.uid() = user_id);

-- Policies para budget
CREATE POLICY "Users can view their own budget"
ON budget FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own budget"
ON budget FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own budget"
ON budget FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own budget"
ON budget FOR DELETE
USING (auth.uid() = user_id);

-- Policies para categories
CREATE POLICY "Users can view their own categories"
ON categories FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own categories"
ON categories FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own categories"
ON categories FOR UPDATE
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own categories"
ON categories FOR DELETE
USING (auth.uid() = user_id);

-- =========================================
-- FUNCIÓN: updated_at automático
-- =========================================
-- Actualiza el campo updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para transactions
CREATE TRIGGER update_transactions_updated_at
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger para budget
CREATE TRIGGER update_budget_updated_at
BEFORE UPDATE ON budget
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- =========================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- =========================================
COMMENT ON TABLE transactions IS 'Transacciones de tarjetas de crédito (scrapeadas y manuales)';
COMMENT ON TABLE budget IS 'Presupuesto mensual del usuario';
COMMENT ON TABLE categories IS 'Categorías personalizadas para clasificar gastos';

COMMENT ON COLUMN transactions.cuota IS 'Formato: "1/6" (cuota actual/total), NULL si es pago único';
COMMENT ON COLUMN transactions.is_manual IS 'TRUE si fue agregada manualmente, FALSE si vino del scraper';
COMMENT ON COLUMN budget.year_month IS 'Formato: "YYYY-MM" (ej: "2024-12")';
