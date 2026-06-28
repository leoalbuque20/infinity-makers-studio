# Arquitetura — Infinity Makers Studio

## Visão geral

```
Interface (CustomTkinter)
    │
    ├── Coleta de parâmetros (_collect_params)
    │       └── tipo, texto, fonte, dimensões, acabamento, furos
    │
    ├── Gerador SCAD (gen_plate / gen_keychain / gen_lamp)
    │       └── Produz código OpenSCAD parametrizado
    │
    └── Exportador STL
            └── Invoca OpenSCAD CLI: openscad -o arquivo.stl arquivo.scad
```

## Módulos principais

### `infinity_makers_studio.py`

Arquivo único que contém toda a aplicação.

**Funções de geração SCAD**

| Função | Modelo | Parâmetros notáveis |
|---|---|---|
| `gen_plate` | Placa decorativa | corner_r, hole, hole_pos, double_hole, hole_margin, hole_radius, border |
| `gen_keychain` | Chaveiro | corner_r, ring_r |
| `gen_lamp` | Luminária | shape (cilíndrica / hexagonal / quadrada) |

**Classes de interface**

| Classe | Responsabilidade |
|---|---|
| `App` | Janela principal, layout, eventos |
| `StatusBar` | Barra de status inferior |
| `SectionLabel` | Label de seção com estilo accent |
| `FieldLabel` | Label de campo secundário |

**Utilitários**

| Função | Uso |
|---|---|
| `_scad_str` | Escapa texto para inserção em código SCAD |
| `_scad_corners` | Gera módulo `rounded_cube` via Minkowski |
| `safe_filename` | Remove caracteres inválidos de nomes de arquivo |
| `find_openscad` | Localiza executável do OpenSCAD no sistema |

## Fluxo de geração de um modelo

1. Usuário preenche os campos e clica em **Gerar SCAD** ou **Gerar STL**
2. `_collect_params()` lê todos os widgets e retorna um dicionário de parâmetros
3. `_build_scad(p)` despacha para a função geradora correta
4. A função gera uma string de código OpenSCAD válido
5. O arquivo `.scad` é salvo em `exports/` com timestamp
6. Se STL: OpenSCAD CLI é chamado via `subprocess.run` para converter

## Stack atual

| Camada | Tecnologia |
|---|---|
| Interface desktop | Python + CustomTkinter (dark mode) |
| Motor CAD | OpenSCAD (via CLI e arquivos .scad) |
| Empacotamento | PyInstaller → `.exe` Windows |

## Stack planejada (próximas versões)

| Camada | Tecnologia |
|---|---|
| Backend API | Python / FastAPI |
| Frontend web | React + Three.js |
| Preview 3D inline | Three.js (STLLoader) ou VTK.js |
