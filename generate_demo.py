"""
Génère une démo GIF du BounceEffect.jsx — mêmes formules que le script AE.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as mtransforms
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec

# ── Paramètres (identiques aux valeurs par défaut du script) ──────────────
DURATION   = 1.5    # sec
OVERSHOOT  = 0.25   # 25 %
ROT_AMP    = 15     # degrés
NUM_BOUNCES = 3
DECAY      = 5.0
FREQ       = NUM_BOUNCES * 2 * np.pi / DURATION

FPS        = 60
N_FRAMES   = int(DURATION * FPS) + 30   # +30 frames de stabilisation visible

# ── Formules (identiques aux expressions AE) ──────────────────────────────
def scale_at(t):
    if t < 0:
        return 0.0
    sv = 100 * (1 + OVERSHOOT * np.sin(FREQ * t + np.pi / 2) * np.exp(-DECAY * t))
    return max(0.0, sv)

def rotation_at(t):
    if t < 0:
        return 0.0
    return ROT_AMP * np.cos(FREQ * t) * np.exp(-DECAY * t)

times  = np.linspace(-0.05, DURATION + 0.3, N_FRAMES)
scales = [scale_at(t) for t in times]
rots   = [rotation_at(t) for t in times]

# ── Figure ────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(11, 6), facecolor="#1a1a2e")
gs  = GridSpec(2, 2, figure=fig,
               left=0.06, right=0.97, top=0.90, bottom=0.10,
               wspace=0.35, hspace=0.55)

ax_anim  = fig.add_subplot(gs[:, 0])   # animation pleine hauteur à gauche
ax_scale = fig.add_subplot(gs[0, 1])   # courbe échelle
ax_rot   = fig.add_subplot(gs[1, 1])   # courbe rotation

for ax in (ax_anim, ax_scale, ax_rot):
    ax.set_facecolor("#16213e")
    for spine in ax.spines.values():
        spine.set_edgecolor("#0f3460")

ACCENT  = "#e94560"
BLUE    = "#53d8fb"
GREEN   = "#4ecca3"
GREY    = "#888"

fig.suptitle("BounceEffect.jsx — Démonstration", color="white",
             fontsize=14, fontweight="bold", y=0.97)

# ── Panneau animation ──────────────────────────────────────────────────────
ax_anim.set_xlim(-1.6, 1.6)
ax_anim.set_ylim(-1.6, 1.6)
ax_anim.set_aspect("equal")
ax_anim.set_title("Aperçu", color="white", fontsize=10, pad=6)
ax_anim.axis("off")

# Fond : grille légère
for v in np.linspace(-1.5, 1.5, 7):
    ax_anim.axhline(v, color="#0f3460", lw=0.5, zorder=0)
    ax_anim.axvline(v, color="#0f3460", lw=0.5, zorder=0)

# Croix centrale (point d'ancrage)
ax_anim.plot(0, 0, "+", color=GREY, ms=10, mew=1.2, zorder=2)

# Rectangle (objet animé)  — taille native = 0.8 × 0.5
W, H   = 0.8, 0.5
rect   = patches.FancyBboxPatch((-W/2, -H/2), W, H,
                                 boxstyle="round,pad=0.04",
                                 linewidth=2,
                                 edgecolor=ACCENT,
                                 facecolor="#e9456044",
                                 zorder=3)
ax_anim.add_patch(rect)

# Label "100 %" et timer
scale_txt = ax_anim.text(0, -1.35, "Échelle : 0 %", color=BLUE,
                          ha="center", va="center", fontsize=9)
rot_txt   = ax_anim.text(0, -1.52, "Rotation : 0.0°", color=GREEN,
                          ha="center", va="center", fontsize=9)
time_txt  = ax_anim.text(1.55, 1.52, "t = 0.00 s", color=GREY,
                          ha="right", va="top", fontsize=7.5)

# ── Courbes ────────────────────────────────────────────────────────────────
t_full = np.linspace(-0.05, DURATION + 0.3, 500)
s_full = [scale_at(t) for t in t_full]
r_full = [rotation_at(t) for t in t_full]

# Échelle
ax_scale.plot(t_full, s_full, color=BLUE, lw=1.6)
ax_scale.axhline(100, color=GREY, lw=0.8, ls="--")
ax_scale.axvline(0,   color=ACCENT, lw=0.8, ls="--")
ax_scale.set_title("Échelle (%)", color="white", fontsize=9, pad=4)
ax_scale.tick_params(colors=GREY, labelsize=7)
ax_scale.set_xlim(t_full[0], t_full[-1])
ax_scale.set_ylim(-5, 135)
ax_scale.set_xlabel("temps (sec)", color=GREY, fontsize=7)

dot_scale, = ax_scale.plot([], [], "o", color=ACCENT, ms=6, zorder=5)
vline_scale = ax_scale.axvline(0, color=ACCENT, lw=0.8, alpha=0.4)

# Rotation
ax_rot.plot(t_full, r_full, color=GREEN, lw=1.6)
ax_rot.axhline(0,   color=GREY,   lw=0.8, ls="--")
ax_rot.axvline(0,   color=ACCENT, lw=0.8, ls="--")
ax_rot.set_title("Rotation (°)", color="white", fontsize=9, pad=4)
ax_rot.tick_params(colors=GREY, labelsize=7)
ax_rot.set_xlim(t_full[0], t_full[-1])
ax_rot.set_xlabel("temps (sec)", color=GREY, fontsize=7)

dot_rot, = ax_rot.plot([], [], "o", color=ACCENT, ms=6, zorder=5)
vline_rot = ax_rot.axvline(0, color=ACCENT, lw=0.8, alpha=0.4)

# ── Animation ─────────────────────────────────────────────────────────────
def update(frame):
    t  = times[frame]
    sc = scales[frame]
    ro = rots[frame]

    # Transform du rectangle : scale puis rotation autour du centre
    factor = (sc / 100.0)
    tr = (mtransforms.Affine2D()
          .translate(W/2, H/2)
          .scale(factor, factor)
          .rotate_deg(ro)
          .translate(-W/2 * factor, -H/2 * factor)
          + ax_anim.transData)
    rect.set_transform(tr)
    rect.set_x(-W/2)
    rect.set_y(-H/2)

    # Couleur : rouge vif quand overshoot, normal sinon
    alpha_fill = min(0.55, 0.2 + abs(sc - 100) / 200)
    rect.set_facecolor(f"#{int(233):02x}{int(69):02x}{int(96):02x}{int(alpha_fill*255):02x}")

    # Labels
    scale_txt.set_text(f"Échelle : {sc:.1f} %")
    rot_txt.set_text(f"Rotation : {ro:.1f}°")
    time_txt.set_text(f"t = {max(0, t):.2f} s")

    # Curseurs courbes
    dot_scale.set_data([t], [sc])
    dot_rot.set_data([t], [ro])
    vline_scale.set_xdata([t, t])
    vline_rot.set_xdata([t, t])

    return rect, scale_txt, rot_txt, time_txt, dot_scale, dot_rot, vline_scale, vline_rot

ani = FuncAnimation(fig, update, frames=N_FRAMES,
                    interval=1000 / FPS, blit=True)

out = "/home/user/bibliotheque/bounce_demo.gif"
ani.save(out, writer="pillow", fps=FPS, dpi=110)
print(f"GIF sauvegardé : {out}")
plt.close()
