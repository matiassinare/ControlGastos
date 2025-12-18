-- =========================================
-- EXPENSE TRACKER - SCHEMA SIMPLIFICADO
-- =========================================
-- PostgreSQL (Supabase) - Uso personal
-- SIN autenticación, SIN RLS, SIN multi-usuario

-- =========================================
-- TABLA: transactions
-- =========================================
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,

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
    category TEXT,                         -- 'Subscripciones', 'Comida', etc.
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Evitar duplicados
    CONSTRAINT unique_transaction UNIQUE(bank, card_name, date, description, amount)
);

-- =========================================
-- TABLA: budget
-- =========================================
CREATE TABLE IF NOT EXISTS budget (
    id BIGSERIAL PRIMARY KEY,

    -- Período
    year_month TEXT NOT NULL UNIQUE,       -- '2024-12', '2025-01'

    -- Ingresos
    gross_salary NUMERIC(10,2),
    net_salary NUMERIC(10,2),

    -- Límite de gastos
    budget_limit NUMERIC(10,2) NOT NULL,

    -- Notas
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================
-- TABLA: categories
-- =========================================
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,

    name TEXT NOT NULL UNIQUE,
    color TEXT,                            -- '#FF5733'
    icon TEXT,                             -- '🍔', '🚗'

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================
-- INDEXES
-- =========================================
CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(date DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_year_month
ON transactions(EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date));

CREATE INDEX IF NOT EXISTS idx_transactions_category
ON transactions(category) WHERE category IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_year_month
ON budget(year_month);

-- =========================================
-- TRIGGERS
-- =========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_transactions_updated_at
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_updated_at
BEFORE UPDATE ON budget
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- =========================================
-- COMENTARIOS
-- =========================================
COMMENT ON TABLE transactions IS 'Transacciones de tarjetas (scrapeadas y manuales)';
COMMENT ON TABLE budget IS 'Presupuesto mensual';
COMMENT ON TABLE categories IS 'Categorías para clasificar gastos';
