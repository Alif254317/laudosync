-- LaudoSync - Schema Inicial
-- Execute este SQL no Supabase SQL Editor

-- Tabela de Auditorias
CREATE TABLE IF NOT EXISTS audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_name TEXT,
    exam_type TEXT,
    exam_date DATE,
    official_pdf_url TEXT,
    auditor_pdf_url TEXT,
    official_text TEXT,
    auditor_text TEXT,
    classification TEXT CHECK (classification IN (
        'CONCORDÂNCIA TOTAL',
        'CONCORDÂNCIA PARCIAL',
        'DISCORDÂNCIA'
    )),
    analysis_summary TEXT,
    concordant_findings JSONB DEFAULT '[]',
    discrepancies JSONB DEFAULT '[]',
    has_critical_alert BOOLEAN DEFAULT FALSE,
    critical_alert_text TEXT,
    technical_note TEXT,
    report_pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_audits_classification ON audits(classification);
CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audits_patient_name ON audits(patient_name);
CREATE INDEX IF NOT EXISTS idx_audits_exam_type ON audits(exam_type);

-- Habilitar RLS (Row Level Security) - desabilitado para MVP sem auth
-- ALTER TABLE audits ENABLE ROW LEVEL SECURITY;

-- Policy para permitir tudo (MVP sem autenticação)
-- Em produção, criar policies adequadas

-- Storage: Criar bucket para os PDFs
-- Execute no Dashboard do Supabase: Storage > New Bucket
-- Nome: laudos
-- Public: true (ou configure signed URLs)

COMMENT ON TABLE audits IS 'Tabela de auditorias comparativas de laudos médicos';
COMMENT ON COLUMN audits.classification IS 'Resultado da comparação: CONCORDÂNCIA TOTAL, PARCIAL ou DISCORDÂNCIA';
COMMENT ON COLUMN audits.concordant_findings IS 'Array JSON com achados que concordam entre os laudos';
COMMENT ON COLUMN audits.discrepancies IS 'Array JSON com discrepâncias encontradas';
