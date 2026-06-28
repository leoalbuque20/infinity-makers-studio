"""
Infinity Makers Studio
Gerador de modelos 3D para impressoras FDM — placas, chaveiros e luminárias.
"""

import customtkinter as ctk
from tkinter import messagebox
import subprocess
import shutil
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Configuração global do tema ──────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ACCENT      = "#F5A623"   # laranja filamento aquecido
ACCENT_DIM  = "#C07A0A"
BG_DEEP     = "#111318"   # fundo principal quase-preto
BG_PANEL    = "#1A1D26"   # painéis laterais
BG_CARD     = "#22263A"   # cards / inputs
BORDER      = "#2E3350"
TEXT_PRI    = "#EAEDF5"
TEXT_SEC    = "#7A7F99"
SUCCESS     = "#3DBA7E"
ERROR_CLR   = "#E05C5C"

FONTS = {
    "title":   ("Segoe UI", 22, "bold"),
    "section": ("Segoe UI", 11, "bold"),
    "label":   ("Segoe UI", 10),
    "body":    ("Segoe UI", 10),
    "mono":    ("Consolas", 9),
    "small":   ("Segoe UI", 9),
    "badge":   ("Segoe UI", 8, "bold"),
}

# ── Geração de código OpenSCAD ───────────────────────────────────────────────

def _scad_str(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

def _scad_corners(r: float) -> str:
    """Cubo com cantos arredondados via minkowski."""
    if r <= 0:
        return ""
    return f"""
module rounded_cube(w, h, d, r) {{
    minkowski() {{
        cube([w - r*2, h - r*2, d - 0.01], center=true);
        cylinder(r=r, h=0.01, $fn=32, center=true);
    }}
}}"""

def gen_plate(text, font, width, height, thickness, text_h,
              corner_r, hole, hole_pos, double_hole, hole_margin, hole_radius, border):
    safe_text = _scad_str(text)
    safe_font = _scad_str(font)
    corners = _scad_corners(corner_r)

    if corner_r > 0:
        base_shape = f"rounded_cube({width}, {height}, {thickness}, {corner_r});"
    else:
        base_shape = f"cube([{width}, {height}, {thickness}], center=true);"

    def _hole_at(hx, hy):
        return f"""
        translate([{hx}, {hy}, -{thickness}])
            cylinder(h={thickness*2+2}, r={hole_radius}, $fn=48);"""

    hole_code = ""
    if hole:
        # Margem do furo em relação à borda
        m = hole_margin
        if hole_pos == "Superior":
            if double_hole:
                # dois furos nas extremidades superiores
                hole_code  = _hole_at(f"-{width}/2 + {m}", f"{height}/2 - {m}")
                hole_code += _hole_at(f" {width}/2 - {m}", f"{height}/2 - {m}")
            else:
                hole_code = _hole_at(0, f"{height}/2 - {m}")
        elif hole_pos == "Inferior":
            if double_hole:
                hole_code  = _hole_at(f"-{width}/2 + {m}", f"-{height}/2 + {m}")
                hole_code += _hole_at(f" {width}/2 - {m}", f"-{height}/2 + {m}")
            else:
                hole_code = _hole_at(0, f"-{height}/2 + {m}")
        elif hole_pos == "Esquerdo":
            if double_hole:
                hole_code  = _hole_at(f"-{width}/2 + {m}", f" {height}/2 - {m}")
                hole_code += _hole_at(f"-{width}/2 + {m}", f"-{height}/2 + {m}")
            else:
                hole_code = _hole_at(f"-{width}/2 + {m}", 0)
        else:  # Direito
            if double_hole:
                hole_code  = _hole_at(f"{width}/2 - {m}", f" {height}/2 - {m}")
                hole_code += _hole_at(f"{width}/2 - {m}", f"-{height}/2 + {m}")
            else:
                hole_code = _hole_at(f"{width}/2 - {m}", 0)

    border_code = ""
    if border > 0:
        if corner_r > 0:
            border_code = f"""
    difference() {{
        translate([0, 0, {thickness}])
            rounded_cube({width}, {height}, {border}, {corner_r});
        translate([0, 0, {thickness} - 0.1])
            rounded_cube({width - border*2}, {height - border*2}, {border + 0.2}, max(0, {corner_r} - {border}));
    }}"""
        else:
            border_code = f"""
    difference() {{
        translate([0, 0, {thickness}])
            cube([{width}, {height}, {border}], center=true);
        translate([0, 0, {thickness} - 0.1])
            cube([{width - border*2}, {height - border*2}, {border + 0.2}], center=true);
    }}"""

    return f"""// Infinity Makers Studio — Placa decorativa
// Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M")}
{corners}

module placa() {{
    difference() {{
        translate([0, 0, {thickness}/2])
            {base_shape}
{hole_code}
    }}
{border_code}
    // Texto em relevo
    translate([0, 0, {thickness}])
        linear_extrude(height={text_h})
            text("{safe_text}",
                 size=min({width},{height}) * 0.22,
                 font="{safe_font}",
                 halign="center", valign="center");
}}

placa();
"""

def gen_keychain(text, font, width, height, thickness, text_h, corner_r, ring_r):
    safe_text = _scad_str(text)
    safe_font = _scad_str(font)
    corners = _scad_corners(corner_r)

    if corner_r > 0:
        body_shape = f"rounded_cube({width}, {height}, {thickness}, {corner_r});"
    else:
        body_shape = f"cube([{width}, {height}, {thickness}], center=true);"

    return f"""// Infinity Makers Studio — Chaveiro
// Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M")}
{corners}

module chaveiro() {{
    union() {{
        difference() {{
            union() {{
                translate([0, 0, {thickness}/2])
                    {body_shape}
                // Argola
                translate([-{width}/2 - {ring_r}, 0, {thickness}/2])
                    cylinder(h={thickness}, r={ring_r}, center=true, $fn=64);
            }}
            // Furo da argola
            translate([-{width}/2 - {ring_r}, 0, 0])
                cylinder(h={thickness + 4}, r={ring_r * 0.45:.1f}, center=true, $fn=48);
        }}
        // Texto em relevo
        translate([0, 0, {thickness}])
            linear_extrude(height={text_h})
                text("{safe_text}",
                     size=min({width},{height}) * 0.24,
                     font="{safe_font}",
                     halign="center", valign="center");
    }}
}}

chaveiro();
"""

def gen_lamp(text, font, radius, height, wall, text_h, shape):
    safe_text = _scad_str(text)
    safe_font = _scad_str(font)

    if shape == "Hexagonal":
        outer = f"cylinder(h={height}, r={radius}, $fn=6);"
        inner = f"cylinder(h={height}, r={radius - wall}, $fn=6);"
    elif shape == "Quadrada":
        outer = f"translate([-{radius}, -{radius}, 0]) cube([{radius*2}, {radius*2}, {height}]);"
        inner = f"translate([-{radius-wall}, -{radius-wall}, {wall}]) cube([{(radius-wall)*2}, {(radius-wall)*2}, {height}]);"
    else:  # Cilíndrica
        outer = f"cylinder(h={height}, r={radius}, $fn=96);"
        inner = f"cylinder(h={height}, r={radius - wall}, $fn=96);"

    return f"""// Infinity Makers Studio — Luminária
// Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M")}

module luminaria() {{
    difference() {{
        {outer}
        translate([0, 0, {wall}])
            {inner}
    }}
    // Texto frontal
    translate([0, -{radius} - {text_h} + 0.2, {height} * 0.52])
        rotate([90, 0, 0])
            linear_extrude(height={text_h})
                text("{safe_text}",
                     size={radius} * 0.28,
                     font="{safe_font}",
                     halign="center", valign="center");
}}

luminaria();
"""

# ── Utilitários ───────────────────────────────────────────────────────────────

def safe_filename(name: str) -> str:
    clean = re.sub(r'[\\/:*?"<>|]', "-", name).strip()
    return clean or "modelo"

def find_openscad() -> str | None:
    if cmd := shutil.which("openscad"):
        return cmd
    candidates = [
        r"C:\Program Files\OpenSCAD\openscad.exe",
        r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
        "/usr/bin/openscad",
        "/usr/local/bin/openscad",
        "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

# ── Interface ─────────────────────────────────────────────────────────────────

class StatusBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_DEEP, corner_radius=0, height=36)
        self.label = ctk.CTkLabel(self, text="Pronto.", font=FONTS["small"],
                                  text_color=TEXT_SEC, anchor="w")
        self.label.pack(fill="x", padx=16, pady=8)

    def set(self, msg: str, color=TEXT_SEC):
        self.label.configure(text=msg, text_color=color)
        self.update_idletasks()

class SectionLabel(ctk.CTkLabel):
    def __init__(self, master, text):
        super().__init__(master, text=text.upper(), font=FONTS["badge"],
                         text_color=ACCENT, anchor="w")

class FieldLabel(ctk.CTkLabel):
    def __init__(self, master, text):
        super().__init__(master, text=text, font=FONTS["label"],
                         text_color=TEXT_SEC, anchor="w")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Infinity Makers Studio")
        self.geometry("900x660")
        self.minsize(820, 600)
        self.configure(fg_color=BG_DEEP)

        # Pasta de exports ao lado do script
        base = Path(sys.argv[0]).parent if getattr(sys, "frozen", False) else Path(__file__).parent
        self.export_dir = base / "exports"
        self.export_dir.mkdir(exist_ok=True)

        self._build_ui()

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="⬡  Infinity Makers Studio",
                     font=FONTS["title"], text_color=ACCENT).pack(side="left", padx=20, pady=12)
        ctk.CTkLabel(header, text="Gerador de modelos 3D · OpenSCAD",
                     font=FONTS["small"], text_color=TEXT_SEC).pack(side="left", padx=4)

        # Corpo
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=0, pady=0)
        body.columnconfigure(0, weight=0, minsize=300)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Coluna esquerda — controles
        left = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=0, width=300)
        left.grid(row=0, column=0, sticky="nsew")
        left.pack_propagate(False)
        self._build_controls(left)

        # Coluna direita — log / ações
        right = ctk.CTkFrame(body, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=0)
        self._build_right(right)

        # Barra de status
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom")

    # ── Controles (esquerda) ──────────────────────────────────────────────────

    def _build_controls(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                        scrollbar_button_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        p = scroll

        # ── Tipo de modelo
        SectionLabel(p, "Tipo de modelo").pack(anchor="w", padx=18, pady=(18, 2))
        self.model_type = ctk.CTkSegmentedButton(
            p, values=["Placa", "Chaveiro", "Luminária"],
            fg_color=BG_CARD, selected_color=ACCENT,
            selected_hover_color=ACCENT_DIM,
            unselected_color=BG_CARD, unselected_hover_color=BORDER,
            text_color=TEXT_PRI, font=FONTS["body"],
            command=self._on_type_change)
        self.model_type.set("Placa")
        self.model_type.pack(fill="x", padx=18, pady=(0, 12))

        # ── Texto
        SectionLabel(p, "Conteúdo").pack(anchor="w", padx=18, pady=(4, 2))
        FieldLabel(p, "Texto").pack(anchor="w", padx=18)
        self.txt_text = ctk.CTkEntry(p, placeholder_text="Seu texto aqui",
                                      fg_color=BG_CARD, border_color=BORDER,
                                      text_color=TEXT_PRI, font=FONTS["body"])
        self.txt_text.insert(0, "Infinity Makers")
        self.txt_text.pack(fill="x", padx=18, pady=(2, 8))

        FieldLabel(p, "Fonte OpenSCAD").pack(anchor="w", padx=18)
        self.font_var = ctk.StringVar(value="Liberation Sans:style=Bold")
        font_menu = ctk.CTkOptionMenu(
            p, variable=self.font_var,
            values=["Liberation Sans:style=Bold", "Liberation Sans",
                    "Liberation Mono:style=Bold", "Arial:style=Bold",
                    "Courier New", "Times New Roman:style=Bold"],
            fg_color=BG_CARD, button_color=ACCENT, button_hover_color=ACCENT_DIM,
            text_color=TEXT_PRI, font=FONTS["body"])
        font_menu.pack(fill="x", padx=18, pady=(2, 12))

        # ── Dimensões
        SectionLabel(p, "Dimensões (mm)").pack(anchor="w", padx=18, pady=(4, 2))

        self.lbl_width = FieldLabel(p, "Largura")
        self.lbl_width.pack(anchor="w", padx=18)
        self.spn_width = self._spinner(p, 20, 300, 90)

        self.lbl_height = FieldLabel(p, "Altura")
        self.lbl_height.pack(anchor="w", padx=18)
        self.spn_height = self._spinner(p, 10, 300, 35)

        self.lbl_thick = FieldLabel(p, "Espessura")
        self.lbl_thick.pack(anchor="w", padx=18)
        self.spn_thick = self._spinner(p, 1, 30, 4)

        self.lbl_texth = FieldLabel(p, "Relevo do texto")
        self.lbl_texth.pack(anchor="w", padx=18)
        self.spn_texth = self._spinner(p, 1, 15, 2)

        # ── Opções extras (Placa / Chaveiro)
        self.frame_plate = ctk.CTkFrame(p, fg_color="transparent")
        self.frame_plate.pack(fill="x")

        SectionLabel(self.frame_plate, "Acabamento").pack(anchor="w", padx=18, pady=(4, 2))

        FieldLabel(self.frame_plate, "Raio dos cantos").pack(anchor="w", padx=18)
        self.spn_corner = self._spinner(self.frame_plate, 0, 20, 4)

        FieldLabel(self.frame_plate, "Largura da borda").pack(anchor="w", padx=18)
        self.spn_border = self._spinner(self.frame_plate, 0, 10, 0)

        self.hole_var = ctk.BooleanVar(value=True)
        self.chk_hole = ctk.CTkCheckBox(self.frame_plate, text="Furo para pendurar",
                                         variable=self.hole_var,
                                         fg_color=ACCENT, hover_color=ACCENT_DIM,
                                         border_color=BORDER, checkmark_color=BG_DEEP,
                                         text_color=TEXT_PRI, font=FONTS["body"],
                                         command=self._on_hole_change)
        self.chk_hole.pack(anchor="w", padx=18, pady=(4, 2))

        self.double_hole_var = ctk.BooleanVar(value=False)
        self.chk_double_hole = ctk.CTkCheckBox(self.frame_plate, text="Dois furos (placa grande)",
                                                variable=self.double_hole_var,
                                                fg_color=ACCENT, hover_color=ACCENT_DIM,
                                                border_color=BORDER, checkmark_color=BG_DEEP,
                                                text_color=TEXT_SEC, font=FONTS["body"])
        self.chk_double_hole.pack(anchor="w", padx=34, pady=(0, 4))

        self.hole_pos_var = ctk.StringVar(value="Superior")
        self.frame_hole_pos = ctk.CTkFrame(self.frame_plate, fg_color="transparent")
        self.frame_hole_pos.pack(fill="x", padx=18, pady=(2, 4))
        FieldLabel(self.frame_hole_pos, "Posição:").pack(side="left")
        ctk.CTkOptionMenu(self.frame_hole_pos, variable=self.hole_pos_var,
                          values=["Superior", "Inferior", "Esquerdo", "Direito"],
                          width=130, fg_color=BG_CARD,
                          button_color=ACCENT, button_hover_color=ACCENT_DIM,
                          text_color=TEXT_PRI, font=FONTS["body"]).pack(side="left", padx=8)

        FieldLabel(self.frame_plate, "Margem do furo da borda (mm)").pack(anchor="w", padx=18)
        self.spn_hole_margin = self._spinner(self.frame_plate, 4, 30, 8)

        FieldLabel(self.frame_plate, "Raio do furo (mm)").pack(anchor="w", padx=18)
        self.spn_hole_radius = self._spinner(self.frame_plate, 1, 8, 3)

        # ── Opções extras (Chaveiro)
        self.frame_key = ctk.CTkFrame(p, fg_color="transparent")

        SectionLabel(self.frame_key, "Acabamento").pack(anchor="w", padx=18, pady=(4, 2))
        FieldLabel(self.frame_key, "Raio dos cantos").pack(anchor="w", padx=18)
        self.spn_key_corner = self._spinner(self.frame_key, 0, 15, 3)
        FieldLabel(self.frame_key, "Raio da argola").pack(anchor="w", padx=18)
        self.spn_ring = self._spinner(self.frame_key, 4, 20, 8)

        # ── Opções extras (Luminária)
        self.frame_lamp = ctk.CTkFrame(p, fg_color="transparent")

        SectionLabel(self.frame_lamp, "Formato").pack(anchor="w", padx=18, pady=(4, 2))
        self.lamp_shape_var = ctk.StringVar(value="Cilíndrica")
        ctk.CTkOptionMenu(self.frame_lamp, variable=self.lamp_shape_var,
                          values=["Cilíndrica", "Hexagonal", "Quadrada"],
                          fg_color=BG_CARD, button_color=ACCENT,
                          button_hover_color=ACCENT_DIM,
                          text_color=TEXT_PRI, font=FONTS["body"]).pack(fill="x", padx=18, pady=(0, 8))

        FieldLabel(p, "").pack()  # espaço

    def _spinner(self, parent, min_v, max_v, default):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=18, pady=(0, 8))
        var = ctk.IntVar(value=default)

        def dec():
            v = var.get()
            if v > min_v:
                var.set(v - 1)

        def inc():
            v = var.get()
            if v < max_v:
                var.set(v + 1)

        btn_style = dict(width=28, height=28, fg_color=BG_CARD,
                         hover_color=BORDER, text_color=ACCENT,
                         font=("Segoe UI", 13, "bold"), corner_radius=4)
        ctk.CTkButton(frame, text="−", command=dec, **btn_style).pack(side="left")
        entry = ctk.CTkEntry(frame, textvariable=var, width=64, justify="center",
                             fg_color=BG_CARD, border_color=BORDER,
                             text_color=TEXT_PRI, font=FONTS["body"])
        entry.pack(side="left", padx=4)
        ctk.CTkButton(frame, text="+", command=inc, **btn_style).pack(side="left")
        ctk.CTkLabel(frame, text=f"  ({min_v}–{max_v})",
                     font=FONTS["small"], text_color=TEXT_SEC).pack(side="left")
        return var

    # ── Painel direito ────────────────────────────────────────────────────────

    def _build_right(self, parent):
        parent.configure(fg_color="transparent")
        parent.rowconfigure(0, weight=0)
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        # Botões de ação
        btn_frame = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=0, height=72)
        btn_frame.grid(row=0, column=0, sticky="ew")
        btn_frame.pack_propagate(False)

        btn_cfg = dict(font=FONTS["section"], corner_radius=6, height=44)

        self.btn_scad = ctk.CTkButton(
            btn_frame, text="⬡  Gerar SCAD",
            fg_color=ACCENT, hover_color=ACCENT_DIM, text_color="#111",
            command=self._gen_scad, **btn_cfg)
        self.btn_scad.pack(side="left", padx=(20, 8), pady=14)

        self.btn_stl = ctk.CTkButton(
            btn_frame, text="⬡  Gerar STL",
            fg_color=BG_CARD, hover_color=BORDER, text_color=ACCENT,
            border_width=1, border_color=ACCENT,
            command=self._gen_stl, **btn_cfg)
        self.btn_stl.pack(side="left", padx=4, pady=14)

        ctk.CTkButton(
            btn_frame, text="📁  Abrir pasta",
            fg_color=BG_CARD, hover_color=BORDER, text_color=TEXT_SEC,
            width=120, command=self._open_exports, **btn_cfg).pack(side="left", padx=8, pady=14)

        # Log de saída
        log_wrap = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=0)
        log_wrap.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        log_wrap.rowconfigure(1, weight=1)
        log_wrap.columnconfigure(0, weight=1)

        ctk.CTkLabel(log_wrap, text="LOG DE SAÍDA", font=FONTS["badge"],
                     text_color=TEXT_SEC, anchor="w").grid(row=0, column=0, padx=18, pady=(14, 4), sticky="w")

        self.log = ctk.CTkTextbox(log_wrap, fg_color=BG_DEEP, text_color=TEXT_PRI,
                                   font=FONTS["mono"], corner_radius=8,
                                   border_color=BORDER, border_width=1)
        self.log.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.log.configure(state="disabled")

        # Info OpenSCAD
        info_frame = ctk.CTkFrame(log_wrap, fg_color=BG_CARD, corner_radius=6)
        info_frame.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        oscad = find_openscad()
        if oscad:
            icon, msg, color = "✔", f"OpenSCAD encontrado: {oscad}", SUCCESS
        else:
            icon, msg, color = "✘", "OpenSCAD não encontrado — apenas .scad disponível.", ERROR_CLR
        ctk.CTkLabel(info_frame, text=f"  {icon}  {msg}",
                     font=FONTS["small"], text_color=color,
                     anchor="w").pack(anchor="w", padx=8, pady=6)

    # ── Eventos ───────────────────────────────────────────────────────────────

    def _on_type_change(self, value):
        self.frame_plate.pack_forget()
        self.frame_key.pack_forget()
        self.frame_lamp.pack_forget()

        if value == "Placa":
            self.frame_plate.pack(fill="x", after=self.spn_texth.master)
            self.lbl_width.configure(text="Largura")
            self.lbl_height.configure(text="Altura")
            self.lbl_thick.configure(text="Espessura")
            self.spn_width.set(90); self.spn_height.set(35); self.spn_thick.set(4)
        elif value == "Chaveiro":
            self.frame_key.pack(fill="x", after=self.spn_texth.master)
            self.lbl_width.configure(text="Largura")
            self.lbl_height.configure(text="Altura")
            self.lbl_thick.configure(text="Espessura")
            self.spn_width.set(60); self.spn_height.set(30); self.spn_thick.set(4)
        else:  # Luminária
            self.frame_lamp.pack(fill="x", after=self.spn_texth.master)
            self.lbl_width.configure(text="Raio")
            self.lbl_height.configure(text="Altura")
            self.lbl_thick.configure(text="Espessura da parede")
            self.spn_width.set(40); self.spn_height.set(120); self.spn_thick.set(2)

    def _on_hole_change(self):
        enabled = self.hole_var.get()
        if enabled:
            self.frame_hole_pos.pack(fill="x", padx=18, pady=(2, 4))
            self.spn_hole_margin.master.pack(fill="x", padx=18, pady=(0, 8))
            self.spn_hole_radius.master.pack(fill="x", padx=18, pady=(0, 8))
            self.chk_double_hole.configure(state="normal")
        else:
            self.frame_hole_pos.pack_forget()
            self.spn_hole_margin.master.pack_forget()
            self.spn_hole_radius.master.pack_forget()
            self.double_hole_var.set(False)
            self.chk_double_hole.configure(state="disabled")

    # ── Geração ───────────────────────────────────────────────────────────────

    def _collect_params(self):
        return {
            "type":     self.model_type.get(),
            "text":     self.txt_text.get().strip() or "Texto",
            "font":     self.font_var.get(),
            "width":    self.spn_width.get(),
            "height":   self.spn_height.get(),
            "thick":    self.spn_thick.get(),
            "text_h":   self.spn_texth.get(),
            "corner":   self.spn_corner.get() if self.model_type.get() == "Placa" else 0,
            "border":   self.spn_border.get() if self.model_type.get() == "Placa" else 0,
            "hole":        self.hole_var.get() if self.model_type.get() == "Placa" else False,
            "double_hole": self.double_hole_var.get() if self.model_type.get() == "Placa" else False,
            "hole_pos":    self.hole_pos_var.get(),
            "hole_margin": self.spn_hole_margin.get() if self.model_type.get() == "Placa" else 8,
            "hole_radius": self.spn_hole_radius.get() if self.model_type.get() == "Placa" else 3,
            "key_corner": self.spn_key_corner.get() if self.model_type.get() == "Chaveiro" else 0,
            "ring_r":   self.spn_ring.get() if self.model_type.get() == "Chaveiro" else 8,
            "lamp_shape": self.lamp_shape_var.get(),
        }

    def _build_scad(self, p) -> str:
        t = p["type"]
        if t == "Placa":
            return gen_plate(p["text"], p["font"], p["width"], p["height"],
                             p["thick"], p["text_h"], p["corner"],
                             p["hole"], p["hole_pos"], p["double_hole"],
                             p["hole_margin"], p["hole_radius"], p["border"])
        elif t == "Chaveiro":
            return gen_keychain(p["text"], p["font"], p["width"], p["height"],
                                p["thick"], p["text_h"], p["key_corner"], p["ring_r"])
        else:
            return gen_lamp(p["text"], p["font"], p["width"], p["height"],
                            p["thick"], p["text_h"], p["lamp_shape"])

    def _save_scad(self, p) -> Path:
        scad = self._build_scad(p)
        name = safe_filename(f"{p['type']}-{p['text']}")
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self.export_dir / f"{name}-{stamp}.scad"
        path.write_text(scad, encoding="utf-8")
        return path

    def _log(self, msg: str):
        self.log.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}] {msg}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _gen_scad(self):
        try:
            p = self._collect_params()
            path = self._save_scad(p)
            self._log(f"✔ SCAD gerado:\n    {path}")
            self.status_bar.set(f"✔  SCAD salvo em exports/", SUCCESS)
        except Exception as e:
            self._log(f"✘ Erro: {e}")
            self.status_bar.set(f"✘  Erro ao gerar SCAD", ERROR_CLR)

    def _gen_stl(self):
        try:
            p = self._collect_params()
            scad_path = self._save_scad(p)
            self._log(f"✔ SCAD: {scad_path.name}")

            oscad = find_openscad()
            if not oscad:
                self._log("✘ OpenSCAD não encontrado. Instale em openscad.org.")
                self.status_bar.set("✘  OpenSCAD não encontrado.", ERROR_CLR)
                return

            stl_path = scad_path.with_suffix(".stl")
            self._log(f"⏳ Convertendo para STL (pode demorar)...")
            self.update_idletasks()

            result = subprocess.run(
                [oscad, "-o", str(stl_path), str(scad_path)],
                capture_output=True, text=True, timeout=120)

            if result.returncode == 0 and stl_path.exists():
                size_kb = stl_path.stat().st_size // 1024
                self._log(f"✔ STL gerado ({size_kb} KB):\n    {stl_path}")
                self.status_bar.set(f"✔  STL salvo em exports/", SUCCESS)
            else:
                self._log(f"✘ OpenSCAD falhou (código {result.returncode})")
                if result.stderr:
                    self._log(f"   {result.stderr[:300]}")
                self.status_bar.set("✘  Falha na conversão STL.", ERROR_CLR)

        except subprocess.TimeoutExpired:
            self._log("✘ Timeout: OpenSCAD demorou mais de 2 minutos.")
            self.status_bar.set("✘  Timeout na conversão.", ERROR_CLR)
        except Exception as e:
            self._log(f"✘ Erro: {e}")
            self.status_bar.set(f"✘  Erro inesperado.", ERROR_CLR)

    def _open_exports(self):
        path = str(self.export_dir)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])


if __name__ == "__main__":
    app = App()
    app.mainloop()
