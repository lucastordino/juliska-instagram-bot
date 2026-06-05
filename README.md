# juliska-instagram-bot

Publica carrosséis no Instagram da Juliska Tordino (@juliska.imoveis) via Meta Graph API, agendados por GitHub Actions.

## Estrutura

```
.
├── .github/workflows/      # cron jobs (1 yml por post)
├── lib/publish_carousel.py # publisher genérico
└── posts/<bairro>/         # slides + caption por post
    ├── slide_1.png
    ├── slide_2.png
    └── caption.txt
```

## Adicionar um novo post

1. Crie `posts/<nome>/` com `slide_1.png` ... `slide_N.png` + `caption.txt`
2. Crie `.github/workflows/publicar-<nome>.yml` baseado no existente
3. Ajuste o cron (lembrar: UTC, não BR)
4. Commit + push → GitHub Actions agenda automaticamente

## Disparo manual

GitHub → Actions → escolher workflow → "Run workflow"

## Secrets necessários

- `INSTAGRAM_BUSINESS_ID`
- `INSTAGRAM_ACCESS_TOKEN` (renovar ~julho/2026)

Configurar em: Settings → Secrets and variables → Actions
