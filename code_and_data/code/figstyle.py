"""新稿图表统一样式与出图检查。

字体:环境里没有真正的 Times New Roman / SimSun 文件,setup_env.sh 用 fontconfig 把它们映射到
Liberation Serif(与 Times New Roman 等宽度量)和 Noto Serif CJK SC(宋体风格衬线)。matplotlib 不走
fontconfig 别名,所以这里直接点名这两个字体,并用 matplotlib(>=3.6)的逐字形回退:拉丁字母、数字
走 Liberation Serif,汉字走 Noto Serif CJK SC。共享 style_kit 的严格字体检查只认真名,在本镜像会直接
报错,故改用本文件的 check_fonts():逐字形核对 cmap(防豆腐块)并在 PDF 里核对嵌入字体(防 DejaVu 回退)。
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Text
from fontTools.ttLib import TTFont, TTCollection

PKG = Path(__file__).resolve().parents[1]           # 本包根目录(code/ 的上一级)
FIG_DIR = PKG / "figures"
DATA = PKG / "data"
DERIVED = DATA / "derived"
RESULTS = PKG / "results"
LOG_DIR = PKG / "logs"
STATS = DATA / "empirical_stats.json"
CHECKS = RESULTS / "checks"

try:  # 原工作区的共享出图检查(文字/图例重叠)不随本包分发,缺失时跳过这两项检查
    from style_kit import (
        assert_no_text_collisions,
        assert_no_legend_reference_line_collisions,
    )
except ImportError:
    def assert_no_text_collisions(fig):
        pass

    def assert_no_legend_reference_line_collisions(fig):
        pass

LATIN = "Liberation Serif"
CJK = "Noto Serif CJK SC"
FONT_FILES = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
]
CJK_TTC = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"

# Okabe–Ito / Wong 色板,按语义固定
C = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "red": "#D55E00",
    "purple": "#CC79A7",
    "grey": "#7F7F7F",
    "lightgrey": "#D9D9D9",
}
THEORY = C["blue"]      # 理论曲线 / 目标Ⅰ
EMPIRIC = C["red"]      # 经验点 / 目标Ⅱ
FLOOR = C["grey"]       # 环境底板、参照线
CROSS = C["green"]      # 交叉点 m×
ACCENT = C["orange"]
ACCENT2 = C["purple"]

WIDE = (6.5, 3.0)       # 通栏,建议 \includegraphics[width=\textwidth]
SINGLE = (5.0, 3.2)     # 单图,建议 width=0.8\textwidth


class _GlyphGuard(logging.Handler):
    """mathtext 缺字形只打日志不报警告;这里把它升级成异常。"""

    def emit(self, record):
        if "does not have a glyph" in record.getMessage():
            raise RuntimeError(record.getMessage())


def apply_style(base: float = 9.0) -> None:
    lg = logging.getLogger("matplotlib.mathtext")
    if not any(isinstance(h, _GlyphGuard) for h in lg.handlers):
        lg.addHandler(_GlyphGuard())
    plt.rcParams.update({
        # 必须直接给族名列表:写成通用族 "serif" 时 matplotlib 不做逐字形回退,汉字成豆腐块
        "font.family": [LATIN, CJK],
        "font.serif": [LATIN, CJK],
        "font.size": base,
        "axes.labelsize": base,
        "xtick.labelsize": base - 1,
        "ytick.labelsize": base - 1,
        "legend.fontsize": base - 1,
        "mathtext.fontset": "custom",
        "mathtext.rm": LATIN,
        "mathtext.it": f"{LATIN}:italic",
        "mathtext.bf": LATIN,
        "mathtext.fallback": None,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.6,
        "axes.grid": False,
        "axes.unicode_minus": True,
        "lines.linewidth": 1.4,
        "lines.markersize": 4.5,
        "legend.frameon": False,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.03,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def _cmap_union() -> set[int] | None:
    if not all(Path(f).exists() for f in [*FONT_FILES, CJK_TTC]):
        print("[figstyle] 未找到 Liberation Serif / Noto Serif CJK 字体文件,跳过逐字形检查", flush=True)
        return None
    cps: set[int] = set()
    for f in FONT_FILES:
        cps |= set(TTFont(f).getBestCmap().keys())
    coll = TTCollection(CJK_TTC)
    for font in coll.fonts:
        if "SC" in font["name"].getDebugName(1):
            cps |= set(font.getBestCmap().keys())
            break
    return cps


_CMAP: set[int] | None = None
_MATH = re.compile(r"(?<!\\)\$.*?(?<!\\)\$")


def _texts(fig):
    for t in fig.findobj(match=Text):
        if t.get_visible() and t.get_text().strip():
            yield t


def check_fonts(fig) -> None:
    """字号 >= 7 pt;非公式部分的每个字符都能在两种字体里找到字形。"""
    global _CMAP
    if _CMAP is None:
        _CMAP = _cmap_union() or set()
    fig.canvas.draw()
    for t in _texts(fig):
        s = t.get_text()
        if t.get_fontsize() < 7:
            raise RuntimeError(f"字号小于 7 pt:{s!r}")
        plain = _MATH.sub("", s).replace("\n", "")
        missing = sorted({ch for ch in plain if _CMAP and ord(ch) not in _CMAP and not ch.isspace()})
        if missing:
            raise RuntimeError(f"字体缺字形 {missing}:{s!r}")


def check_pdf_fonts(pdf: Path) -> list[str]:
    if shutil.which("pdffonts") is None:          # poppler-utils 未安装时跳过嵌入字体核对
        return []
    out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
    names = [ln.split()[0] for ln in out.splitlines()[2:] if ln.strip()]
    bad = [n for n in names if not re.search(r"LiberationSerif|NotoSerifCJK", n)]
    if bad:
        raise RuntimeError(f"{pdf.name} 嵌入了非预期字体:{bad}")
    return names


_HAN = re.compile(r"[　-鿿＀-￯]")


def fix_mixed(fig) -> None:
    """含公式的中文串走 mathtext,而 mathtext 不做逐字形回退,汉字会变成占位框。
    这类串整体改用思源宋体(公式里的字母仍走 Liberation Serif 斜体)。"""
    for t in _texts(fig):
        s = t.get_text()
        if _MATH.search(s) and _HAN.search(_MATH.sub("", s)):
            t.set_fontfamily([CJK])


def fix_cff_embedding(pdf: Path) -> int:
    """matplotlib 把 Noto Serif CJK(CFF 轮廓的 OpenType)当 CIDFontType2 塞进 FontFile2,
    pdffonts 报 "Mismatch between font type and embedded font file"。这里把这类子集字体的
    三次曲线转成二次(cu2qu),写成真正的 TrueType,字形顺序不变,CID→GID 映射照旧。"""
    from io import BytesIO

    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import newTable
    from pypdf import PdfReader, PdfWriter

    def otf_to_ttf(data: bytes) -> bytes:
        font = TTFont(BytesIO(data))
        order = font.getGlyphOrder()
        gs = font.getGlyphSet()
        glyf = newTable("glyf")
        glyf.glyphOrder = order
        glyf.glyphs = {}
        for name in order:
            pen = TTGlyphPen(gs)
            gs[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
            glyf.glyphs[name] = pen.glyph()
        font["glyf"] = glyf
        font["loca"] = newTable("loca")
        maxp = font["maxp"]
        maxp.tableVersion = 0x00010000
        for attr in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs",
                     "maxInstructionDefs", "maxStackElements", "maxSizeOfInstructions",
                     "maxComponentElements", "maxPoints", "maxContours",
                     "maxCompositePoints", "maxCompositeContours", "maxComponentDepth"):
            setattr(maxp, attr, 0)
        maxp.maxZones = 1
        font["head"].glyphDataFormat = 0
        if "post" in font:
            font["post"].formatType = 3.0
        for tag in ("CFF ", "VORG"):
            if tag in font:
                del font[tag]
        font.sfntVersion = "\x00\x01\x00\x00"
        out = BytesIO()
        font.save(out)
        return out.getvalue()

    writer = PdfWriter(clone_from=PdfReader(pdf))
    fixed = 0
    for page in writer.pages:
        for ref in page["/Resources"].get("/Font", {}).values():
            font = ref.get_object()
            for desc in font.get("/DescendantFonts", []):
                fd = desc.get_object()["/FontDescriptor"].get_object()
                if "/FontFile2" not in fd:
                    continue
                stream = fd["/FontFile2"].get_object()
                data = stream.get_data()
                if data[:4] != b"OTTO":
                    continue
                stream.set_data(otf_to_ttf(data))
                fixed += 1
    if fixed:
        with open(pdf, "wb") as fh:
            writer.write(fh)
    return fixed


def save(fig, stem: str, log=None) -> dict:
    """检查后保存 PDF+PNG,返回检查记录。"""
    fix_mixed(fig)
    try:
        check_fonts(fig)
        assert_no_text_collisions(fig)
        assert_no_legend_reference_line_collisions(fig)
    except RuntimeError as e:
        dbg = DERIVED / "debug"
        dbg.mkdir(exist_ok=True)
        fig.savefig(dbg / f"{stem}.png", dpi=150)
        raise RuntimeError(f"{stem}: {e}(调试图见 {dbg / stem}.png)") from e
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FIG_DIR / f"{stem}.pdf"
    png = FIG_DIR / f"{stem}.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=220)
    fix_cff_embedding(pdf)
    fonts = check_pdf_fonts(pdf)
    w, h = fig.get_size_inches()
    rec = {"stem": stem, "size_in": [round(w, 2), round(h, 2)], "pdf_fonts": fonts}
    if log:
        log(f"saved {stem}: size={w:.2f}x{h:.2f} in, fonts={fonts}")
    plt.close(fig)
    return rec


def logger(name: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{name}.log"
    fh = path.open("a", encoding="utf-8")

    def log(msg: str) -> None:
        fh.write(msg + "\n")
        fh.flush()
        print(msg, flush=True)

    return log


def load_stats() -> dict:
    return json.loads(STATS.read_text())


def panel_xlabel(ax, letter: str, text: str) -> None:
    ax.set_xlabel(f"({letter}) {text}")
