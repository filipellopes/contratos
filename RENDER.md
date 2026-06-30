# Deploy gratuito no Render

Alternativa **sem custo** ao Railway (cujo trial expira e exige plano Hobby ~US$ 5/mês).

## Limitações do plano Free do Render

| Item | Comportamento |
|------|----------------|
| Custo | **Grátis** |
| Inatividade | App **dorme** após ~15 min sem acesso |
| Primeiro acesso | Pode levar **30–60 s** para acordar (cold start) |
| Disco | **Efêmero** — contratos gerados somem no redeploy |
| Build | LibreOffice deixa o 1º build lento (~5–10 min) |

Para uso interno e testes no celular, costuma ser suficiente.

---

## Passo a passo (celular ou desktop)

### 1. Criar conta

1. Acesse [render.com](https://render.com)
2. Cadastre-se com **GitHub** (mesmo repo `filipellopes/contratos`)

### 2. Criar Web Service

1. Dashboard → **New +** → **Web Service**
2. Conecte o repositório `contratos`
3. Render detecta o `render.yaml` — confirme:
   - **Runtime:** Docker
   - **Plan:** Free
   - **Branch:** `master`

### 3. Variáveis de ambiente

Na tela de criação (ou depois em **Environment**):

| Variável | Valor |
|----------|-------|
| `SECRET_KEY` | Chave forte qualquer (ex.: `valore-render-2026-secreto`) |
| `FLASK_DEBUG` | `0` |
| `PDF_CONVERSION` | `auto` |

`PORT` é definido automaticamente pelo Render.

### 4. (Opcional) PostgreSQL grátis com Neon

Sem banco externo, o app usa SQLite + seed a cada reinício (dados não persistem entre deploys).

Para persistir dados **de graça**:

1. Crie conta em [neon.tech](https://neon.tech)
2. **New Project** → copie a connection string (`postgresql://...`)
3. No Render, adicione `DATABASE_URL` com essa URL

> O `config.py` já converte `postgres://` → `postgresql://` se necessário.

### 5. Deploy

1. Clique **Create Web Service**
2. Aguarde o build (1ª vez demora por causa do LibreOffice)
3. URL final: `https://valore-contratos.onrender.com` (ou similar)

Acesse no celular: `https://SUA-URL.onrender.com/contratos`

---

## Arquivos de deploy

```
render.yaml       # Blueprint Render (Docker + healthcheck)
Dockerfile        # Python + LibreOffice + gunicorn
scripts/start.sh  # seed + gunicorn
```

---

## Railway vs Render

| | Railway | Render Free |
|---|---------|-------------|
| Preço após trial | ~US$ 5/mês (Hobby) | **Grátis** |
| Sempre ligado | Sim (Hobby) | Não (dorme) |
| PDF (LibreOffice) | Sim | Sim |
| Ideal para | Produção 24/7 | Testes / uso ocasional |

Se no futuro quiser produção sem cold start, aí sim vale o Railway Hobby ou um VPS.

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Build timeout | Normal na 1ª vez; tente **Manual Deploy** de novo |
| 502 ao abrir | App ainda acordando — espere ~1 min |
| Dados sumiram | Use Neon (`DATABASE_URL`) ou aceite SQLite efêmero |
| PDF não gera | Confirme `PDF_CONVERSION=auto`; LibreOffice está no Docker |
