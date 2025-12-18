-- Migration: Add adjusted_amount column to transactions table

ALTER TABLE public.transactions
ADD COLUMN IF NOT EXISTS adjusted_amount numeric(20, 2);

COMMENT ON COLUMN public.transactions.adjusted_amount IS 'Monto ajustado manualmente para gastos compartidos o anulados (0)';
