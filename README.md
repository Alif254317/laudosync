# LaudoSync - Sistema de Auditoria Comparativa de Laudos

Sistema para comparação automatizada de laudos médicos usando IA (Gemini).

## Estrutura do Projeto

```
laudosync/
├── backend/          # API FastAPI (Python)
├── frontend/         # Interface Nuxt 3
└── supabase/         # Migrations SQL
```

## Pré-requisitos

- Python 3.10+
- Node.js 18+
- Conta no Google AI Studio (Gemini API)
- Projeto no Supabase

## Configuração

### 1. Supabase

1. Acesse o [Supabase Dashboard](https://supabase.com/dashboard)
2. Execute o SQL em `supabase/migrations/001_initial_schema.sql` no SQL Editor
3. Crie um bucket de Storage chamado `laudos` (público)

### 2. Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp ../.env.example .env
# Edite o .env com sua GEMINI_API_KEY
```

### 3. Frontend

```bash
cd frontend

# Instalar dependências
npm install
```

## Executando

### Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

API disponível em: http://localhost:8000
Docs: http://localhost:8000/docs

### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

App disponível em: http://localhost:3000

## Uso

1. Acesse http://localhost:3000
2. Faça upload de 2 PDFs de laudos (Oficial + Auditor)
3. Preencha os dados do paciente (opcional)
4. Clique em "Analisar Laudos"
5. Veja o resultado com classificação colorida
6. Baixe o relatório PDF

## Variáveis de Ambiente

### Backend (.env)

```
GEMINI_API_KEY=sua_chave_gemini
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=sua_chave_anon
```

### Frontend (.env)

```
NUXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/audits | Criar nova auditoria |
| GET | /api/audits | Listar auditorias |
| GET | /api/audits/{id} | Detalhes de uma auditoria |
| GET | /api/audits/{id}/report | Download do relatório PDF |

## Tecnologias

- **Frontend**: Nuxt 3, Vue 3, Tailwind CSS, Nuxt UI
- **Backend**: FastAPI, Python
- **IA**: Google Gemini 2.0 Flash
- **Banco**: Supabase (PostgreSQL)
- **PDF**: pdfplumber (extração), reportlab (geração)

---

Desenvolvido por Elo System
