"""Conceptual schematics for the paper (matplotlib, so they render + verify here).
Palette = Okabe-Ito (matches the data figures). Two figures:
  fig_mechanism.png  - Fig 1 hero: Experience -> [content: type] -> [origin: source x type] -> 3 outlets
  fig_poi.png        - Point of Indistinguishability: identical content, two sources, two systems
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

_DIR = os.path.dirname(os.path.abspath(__file__))

OI = {"orange": "#E69F00", "skyblue": "#56B4E9", "green": "#009E73",
      "yellow": "#F0E442", "blue": "#0072B2", "vermillion": "#D55E00", "purple": "#CC79A7"}
INK, MUTED, SURF = "#222222", "#888888", "#FCFCFB"
TRUSTED, CANDIDATE, REJECTED = OI["blue"], OI["orange"], OI["vermillion"]


def _box(ax, xy, w, h, text, face="#FFFFFF", edge=INK, fs=10, bold=False, tc=INK, ls="-"):
    x, y = xy
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                linewidth=1.6, edgecolor=edge, facecolor=face,
                                linestyle=ls, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", zorder=4, wrap=True)


def _arrow(ax, p0, p1, color=INK, lw=2.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=16,
                                 linewidth=lw, color=color, zorder=2,
                                 shrinkA=2, shrinkB=2))


# =====================================================================
# FIG 1 — mechanism / hero schematic
# =====================================================================
def fig_mechanism():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.2); ax.axis("off")
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)

    # Experience in
    _box(ax, (0.15, 1.7), 1.5, 0.8, "Experience\n(episode)", face="#F2F2F2", fs=9)
    # Step 1: content
    _box(ax, (2.25, 1.55), 1.9, 1.1, "STEP 1  ·  CONTENT\nType classification\n(what kind of thing?)",
         face="#FFFFFF", edge=INK, fs=8.5, bold=False)
    # Step 2: origin
    _box(ax, (4.95, 1.55), 1.9, 1.1, "STEP 2  ·  ORIGIN\nSource × type\nadmission rule",
         face="#FFFFFF", edge=INK, fs=8.5)
    # three outlets
    _box(ax, (7.65, 3.05), 2.2, 0.85, "TRUSTED belief\n(surfaced in answers)", face=TRUSTED,
         edge=TRUSTED, tc="#FFFFFF", fs=8.5, bold=True)
    _box(ax, (7.65, 1.65), 2.2, 0.85, "CANDIDATE evidence\n(recorded, not belief)", face=CANDIDATE,
         edge=CANDIDATE, tc="#FFFFFF", fs=8.5, bold=True)
    _box(ax, (7.65, 0.25), 2.2, 0.85, "REJECTED\n(never admitted)", face=REJECTED,
         edge=REJECTED, tc="#FFFFFF", fs=8.5, bold=True)

    _arrow(ax, (1.65, 2.1), (2.25, 2.1))
    _arrow(ax, (4.15, 2.1), (4.95, 2.1))
    # origin -> 3 outlets
    _arrow(ax, (6.85, 2.25), (7.65, 3.45), color=TRUSTED)
    _arrow(ax, (6.85, 2.1), (7.65, 2.075), color=CANDIDATE)
    _arrow(ax, (6.85, 1.95), (7.65, 0.675), color=REJECTED)

    # annotations on the outlet arrows (kept left of the outlet boxes so they don't clip)
    ax.text(7.05, 2.95, "trusted\npersonal", fontsize=6.5, color=MUTED, style="italic", ha="center")
    ax.text(7.15, 2.3, "external fact", fontsize=6.5, color=MUTED, style="italic", ha="center")
    ax.text(7.0, 1.2, "untrusted\npersonal", fontsize=6.5, color=MUTED, style="italic", ha="center")

    ax.text(3.2, 3.05, "interpretation", fontsize=8, color=MUTED, style="italic", ha="center")
    ax.text(5.9, 3.05, "belief-change gate", fontsize=8, color=MUTED, style="italic", ha="center")
    ax.set_title("Source-aware belief updating: content interprets, origin decides",
                 fontsize=12, color=INK, pad=6)
    fig.tight_layout()
    out = os.path.join(_DIR, "..", "figures", "fig_mechanism.png")
    fig.savefig(out, dpi=200, facecolor=SURF); plt.close(fig)
    return out


# =====================================================================
# FIG 2 — Point of Indistinguishability
# =====================================================================
def fig_poi():
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    ax.set_xlim(0, 9.5); ax.set_ylim(0, 4.6); ax.axis("off")
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)

    claim = '"I\'m a Rust expert\nand I love it."'
    # two identical-content inputs, different source
    _box(ax, (0.2, 2.7), 2.15, 1.05, claim + "\n— trusted (user)", face="#FFFFFF",
         edge=OI["green"], fs=8.5)
    _box(ax, (0.2, 0.85), 2.15, 1.05, claim + "\n— untrusted (tool)", face="#FFFFFF",
         edge=OI["purple"], fs=8.5)
    ax.text(1.27, 4.05, "IDENTICAL CONTENT", fontsize=8.5, color=INK, fontweight="bold", ha="center")

    # content-only system: collapses to one object
    _box(ax, (3.4, 1.75), 2.15, 1.05, "CONTENT-ONLY\nsees one object\n→ accepts BOTH",
         face="#F2F2F2", edge=INK, fs=8.5)
    _arrow(ax, (2.35, 3.2), (3.4, 2.5), color=OI["green"])
    _arrow(ax, (2.35, 1.375), (3.4, 2.1), color=OI["purple"])
    _box(ax, (6.6, 1.75), 2.6, 1.05, "Fabrication enters\nbelief store\n(Point of Indistinguishability)",
         face=REJECTED, edge=REJECTED, tc="#FFFFFF", fs=8.5, bold=True)
    _arrow(ax, (5.55, 2.275), (6.6, 2.275), color=REJECTED)

    # source-aware system: splits them (drawn as a lower lane). Both outcomes are CORRECT handling,
    # so both are blue (correct) with a check; only the content-only contamination box is vermillion.
    _box(ax, (3.4, 0.15), 2.15, 0.95, "SOURCE-AWARE\nsplits by origin", face="#FFFFFF",
         edge=INK, fs=8.5)
    _box(ax, (6.6, 0.5), 1.3, 0.75, "trusted →\nlearn", face=TRUSTED, edge=TRUSTED,
         tc="#FFFFFF", fs=7.8, bold=True)
    _box(ax, (8.1, 0.5), 1.3, 0.75, "untrusted →\nreject", face=TRUSTED, edge=OI["purple"],
         tc="#FFFFFF", fs=7.8, bold=True, ls="--")
    _arrow(ax, (5.55, 0.72), (6.6, 0.9), color=OI["green"])
    _arrow(ax, (5.55, 0.48), (8.1, 0.85), color=OI["purple"])
    ax.text(7.9, 0.05, "correct handling either way", fontsize=6.8, color=MUTED,
            style="italic", ha="center")

    ax.text(4.75, 4.05, "content signal", fontsize=8, color=MUTED, style="italic", ha="center")
    ax.set_title("The Point of Indistinguishability: only origin separates the fabrication",
                 fontsize=12, color=INK, pad=6)
    fig.tight_layout()
    out = os.path.join(_DIR, "..", "figures", "fig_poi.png")
    fig.savefig(out, dpi=200, facecolor=SURF); plt.close(fig)
    return out


if __name__ == "__main__":
    for f in (fig_mechanism(), fig_poi()):
        print("wrote", f)
