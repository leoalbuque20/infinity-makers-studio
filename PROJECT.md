# Projeto — Infinity Makers Studio

Objetivo: criar um software desktop para gerar modelos 3D personalizados (placas decorativas, chaveiros, luminárias e outros), exportando arquivos prontos para impressão FDM.

## Stack atual

- **Python + CustomTkinter** — interface desktop dark mode, executável via PyInstaller
- **OpenSCAD** — motor CAD paramétrico, geração de `.scad` e `.stl`

## Stack planejada

- **Python / FastAPI** — backend API para versão web
- **React** — frontend web
- **Three.js** — preview 3D inline
- **OpenSCAD** — mantido como motor CAD

## Versão atual (v0.2)

### Placa decorativa
- Texto personalizado em relevo
- Cantos arredondados (raio configurável)
- Borda em relevo (largura configurável)
- Furo para pendurar com:
  - Posição escolhível: superior, inferior, esquerdo, direito
  - Opção de dois furos simétricos para placas grandes
  - Margem do furo em relação à borda configurável (4–30 mm)
  - Raio do furo configurável (1–8 mm)

### Chaveiro
- Texto em relevo
- Argola integrada com furo (raio configurável)
- Cantos arredondados

### Luminária
- Formatos: cilíndrica, hexagonal, quadrada
- Texto frontal em relevo

### Interface
- Dark mode com accent laranja
- Spinners com botões +/−
- Log de saída em tempo real com timestamps
- Indicador de OpenSCAD instalado/ausente
- Botão para abrir pasta de exports

### Exportação
- `.scad` — sempre disponível
- `.stl` — requer OpenSCAD instalado
- Arquivos salvos em `exports/` com nome e timestamp automáticos
