# Infinity Makers Studio

Gerador de modelos 3D personalizados para impressoras FDM — placas decorativas, chaveiros e luminárias.

## Como usar

### Opção 1 — Direto com Python (desenvolvimento)

```bash
pip install customtkinter Pillow
python infinity_makers_studio.py
```

### Opção 2 — Executável Windows (.exe)

1. Certifique-se de ter Python instalado em python.org
2. Execute `build_windows.bat` com duplo clique
3. O `.exe` gerado estará em `dist\InfinityMakersStudio.exe`
4. Copie o `.exe` para qualquer pasta e execute — sem precisar instalar Python

## Funcionalidades

### Placa decorativa
- Texto personalizado em relevo
- Cantos arredondados configuráveis
- Borda em relevo opcional
- Furo para pendurar com posição escolhível (superior, inferior, esquerdo ou direito)
- Opção de dois furos para placas grandes — posição simétrica automática
- Margem do furo em relação à borda configurável (4–30 mm)
- Raio do furo configurável (1–8 mm)

### Chaveiro
- Corpo com texto em relevo
- Argola integrada com furo (raio configurável)
- Cantos arredondados configuráveis

### Luminária
- Três formatos: cilíndrica, hexagonal e quadrada
- Texto frontal em relevo

## Saída

- `.scad` — editável no OpenSCAD
- `.stl` — pronto para fatiar (requer OpenSCAD instalado)

Os arquivos são salvos na pasta `exports/`, com nome e timestamp automáticos.

## Requisitos

| Componente   | Obrigatório    | Uso                        |
|---|---|---|
| Python 3.10+ | Sim (modo script) | Executar o app          |
| customtkinter | Sim           | Interface gráfica          |
| Pillow        | Sim           | Dependência da interface   |
| OpenSCAD      | Não           | Exportar STL diretamente   |

## Roadmap

- [x] Interface moderna dark mode
- [x] Placa com cantos arredondados e borda
- [x] Chaveiro com argola configurável
- [x] Luminária cilíndrica/hexagonal/quadrada
- [x] Log de saída em tempo real
- [x] Furo com posição e quantidade configuráveis
- [x] Margem e raio do furo configuráveis
- [ ] Preview 3D inline
- [ ] Biblioteca de temas/templates
- [ ] Suporte a múltiplas linhas de texto
- [ ] Exportação OBJ
- [ ] Ícones e logo customizados no .exe
