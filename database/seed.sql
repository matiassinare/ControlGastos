-- =========================================
-- SEED DATA (OPCIONAL)
-- =========================================
-- Datos de ejemplo para testing
-- ADVERTENCIA: Solo ejecutar en entorno de desarrollo
-- NO ejecutar en producción

-- =========================================
-- CATEGORÍAS DE EJEMPLO
-- =========================================
-- Insertar categorías comunes (requiere estar autenticado)
INSERT INTO categories (name, color, icon) VALUES
    ('Comida', '#FF6B6B', '🍔'),
    ('Transporte', '#4ECDC4', '🚗'),
    ('Entretenimiento', '#95E1D3', '🎮'),
    ('Subscripciones', '#F38181', '💳'),
    ('Salud', '#AA96DA', '🏥'),
    ('Educación', '#FCBAD3', '📚'),
    ('Hogar', '#A8E6CF', '🏠'),
    ('Ropa', '#FFD3B6', '👕'),
    ('Viajes', '#FFAAA5', '✈️'),
    ('Otros', '#C7CEEA', '📦')
ON CONFLICT (user_id, name) DO NOTHING;

-- =========================================
-- PRESUPUESTO DE EJEMPLO
-- =========================================
-- Presupuesto para el mes actual
INSERT INTO budget (year_month, gross_salary, net_salary, budget_limit, notes) VALUES
    (TO_CHAR(CURRENT_DATE, 'YYYY-MM'), 500000.00, 350000.00, 200000.00, 'Presupuesto de ejemplo')
ON CONFLICT (user_id, year_month) DO NOTHING;

-- =========================================
-- TRANSACCIONES DE EJEMPLO
-- =========================================
-- Algunas transacciones para visualizar el dashboard
INSERT INTO transactions (bank, card_type, card_name, date, description, amount, currency, cuota, is_manual, category) VALUES
    -- BBVA Visa
    ('BBVA', 'Visa', 'Visa BBVA', CURRENT_DATE - 5, 'MERCADOPAGO*RAPPI', 15420.50, 'ARS', NULL, FALSE, 'Comida'),
    ('BBVA', 'Visa', 'Visa BBVA', CURRENT_DATE - 4, 'SPOTIFY INDIVIDUAL', 5990.00, 'ARS', NULL, FALSE, 'Subscripciones'),
    ('BBVA', 'Visa', 'Visa BBVA', CURRENT_DATE - 3, 'YPF AUTOSERVICIO', 45000.00, 'ARS', '1/3', FALSE, 'Transporte'),

    -- Galicia Visa
    ('Galicia', 'Visa', 'Visa Galicia', CURRENT_DATE - 6, 'MERCADOLIBRE*NOTEBOOK', 180000.00, 'ARS', '2/12', FALSE, 'Tecnología'),
    ('Galicia', 'Visa', 'Visa Galicia', CURRENT_DATE - 2, 'NETFLIX PREMIUM', 8999.00, 'ARS', NULL, FALSE, 'Subscripciones'),

    -- Amex Galicia
    ('Galicia', 'Amex', 'Amex Galicia', CURRENT_DATE - 7, 'AMAZON WEB SERVICES', 125.50, 'USD', NULL, FALSE, 'Tecnología'),
    ('Galicia', 'Amex', 'Amex Galicia', CURRENT_DATE - 1, 'STARBUCKS COFFEE', 12400.00, 'ARS', NULL, FALSE, 'Comida'),

    -- Gastos manuales
    ('Manual', 'Efectivo', 'Efectivo', CURRENT_DATE, 'Almacén del barrio', 8500.00, 'ARS', NULL, TRUE, 'Comida'),
    ('Manual', 'Transferencia', 'Transferencia', CURRENT_DATE - 8, 'Alquiler departamento', 120000.00, 'ARS', NULL, TRUE, 'Hogar')
ON CONFLICT (user_id, bank, card_name, date, description, amount) DO NOTHING;

-- =========================================
-- VERIFICACIÓN
-- =========================================
-- Consultas para verificar que los datos se insertaron correctamente

-- SELECT * FROM categories ORDER BY name;
-- SELECT * FROM budget ORDER BY year_month DESC;
-- SELECT * FROM transactions ORDER BY date DESC;
