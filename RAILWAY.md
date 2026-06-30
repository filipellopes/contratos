# Deploy no Railway

Guia para publicar o **Valore Contratos** com URL pública acessível do celular.

> **Trial expirou?** O Railway passa a exigir plano Hobby (~US$ 5/mês). Para uso gratuito, veja **[RENDER.md](RENDER.md)**.

## Pré-requisitos

- Conta em [railway.com](https://railway.com)
- Repositório no GitHub: `filipellopes/contratos`
- Branch com as alterações de deploy (`master` ou PR mergeada)

## Passo a passo (≈ 5 minutos)

### 1. Criar projeto

1. Acesse [railway.com/new](https://railway.com/new)
2. **Deploy from GitHub repo** → autorize o GitHub → selecione `contratos`
3. Railway detecta o `Dockerfile` automaticamente (LibreOffice + PDF inclusos)

### 2. Adicionar PostgreSQL (recomendado)

1. No projeto Railway: **+ New** → **Database** → **PostgreSQL**
2. Clique no serviço da app → aba **Variables**
3. Clique em **Add Reference** → selecione `DATABASE_URL` do Postgres

> Sem Postgres, a app usa SQLite no disco efêmero — dados se perdem a cada redeploy.

### 3. Variáveis de ambiente

Na aba **Variables** do serviço web, configure:

| Variável | Valor |
|----------|-------|
| `SECRET_KEY` | Gere uma chave forte (ex.: `openssl rand -hex 32`) |
| `DATABASE_URL` | Referência ao Postgres (passo 2) |
| `PDF_CONVERSION` | `auto` |
| `FLASK_DEBUG` | `0` |

Railway define `PORT` automaticamente — não precisa configurar.

### 4. Volume para contratos gerados (opcional mas recomendado)

Arquivos Word/PDF ficam em `app/generated_contracts/`. Sem volume, somem no redeploy.

1. No serviço web: **Settings** → **Volumes** → **Add Volume**
2. Mount path: `/app/app/generated_contracts`

### 5. Deploy

1. Railway faz deploy automaticamente após conectar o repo
2. Aba **Settings** → **Networking** → **Generate Domain**
3. Copie a URL (ex.: `https://contratos-production-xxxx.up.railway.app`)

Na primeira subida, o `seed.py` roda automaticamente (opções + empresa Valore).

### 6. Testar

Abra no celular:

- `https://SUA-URL.up.railway.app/contratos`
- `https://SUA-URL.up.railway.app/contratos/novo`

---

## Estrutura de arquivos de deploy

```
Dockerfile          # Python + LibreOffice + gunicorn
railway.toml        # Config Railway (healthcheck, builder)
scripts/start.sh    # seed + gunicorn na porta $PORT
```

## Healthcheck

Railway verifica `GET /contratos` — a listagem deve responder 200.

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Build lento | Normal na 1ª vez (instala LibreOffice ~300 MB) |
| 502 no deploy | Aguarde o seed terminar; healthcheck timeout é 300s |
| PDF não gera | Confirme `PDF_CONVERSION=auto`; LibreOffice já está no Docker |
| Dados sumiram | Adicione Postgres + volume conforme passos 2 e 4 |
| `postgres://` error | Já corrigido em `config.py` (converte para `postgresql://`) |

## Custo estimado

- **Hobby plan**: ~$5/mês de crédito incluído
- App + Postgres pequeno costuma caber no plano gratuito inicial

## Atualizações

Cada push na branch conectada dispara redeploy automático.
