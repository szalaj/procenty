# CLAUDE.md

Szczegółowy opis projektu, architektury i znanych problemów: [AGENTS.md](./AGENTS.md)

## Zasady pracy z kodem

- Nazewnictwo polskie - zachowuj konwencję istniejącego kodu
- Kwoty pieniężne: Decimal z zaokrągleniem do groszy (ROUND_HALF_UP)
- Stopy procentowe: mogą być float (w interpolacji) lub Decimal (w kredycie)
- Testy: `pytest tests/ -v`
- Formatowanie: `black .` i `isort .`
