import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams['font.family'] = 'sans-serif'

CSV = "src/python/data/results/results_2026-02-16_11-27-05.csv"
df = pd.read_csv(CSV)
df['Category'] = df['ID'].str.extract(r'test/([^/]+)/')

# Rename for display
NICE = {
    'algebra': 'Algebra',
    'intermediate_algebra': 'Intermed. Algebra',
    'prealgebra': 'Pre-Algebra',
    'precalculus': 'Pre-Calculus',
    'number_theory': 'Number Theory',
    'geometry': 'Geometry',
    'counting_and_probability': 'Counting & Prob.',
}
df['CategoryNice'] = df['Category'].map(NICE)

approaches = ['Pure LLM Correct', 'Python Answer Correct', 'Lean4 Answer Correct']
labels = ['Pure LLM', 'Python (SymPy)', 'Lean 4']
colors_main = ['#4C72B0', '#55A868', '#C44E52']

# Overall accuracy
overall = [df[a].mean() * 100 for a in approaches]

# Per-category accuracy
cats_sorted = sorted(df['Category'].unique(), key=lambda c: df[df['Category'] == c]['Pure LLM Correct'].mean(), reverse=True)
cat_labels = [NICE[c] for c in cats_sorted]
cat_counts = [len(df[df['Category'] == c]) for c in cats_sorted]


# ── Variation A: Simple bar chart (overall accuracy) ──────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(labels, overall, color=colors_main, width=0.55, edgecolor='white', linewidth=1.2)
for bar, val in zip(bars, overall):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.2, f'{val:.0f}%',
            ha='center', va='bottom', fontweight='bold', fontsize=14)
ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_ylim(0, 110)
ax.set_title('Overall Accuracy by Approach\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('src/python/data/results/plot_A_overall_bar.png', dpi=150)
plt.close()


# ── Variation B: Grouped bar chart (per-category) ────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(cats_sorted))
w = 0.25
for i, (app, label, col) in enumerate(zip(approaches, labels, colors_main)):
    vals = [df[df['Category'] == c][app].mean() * 100 for c in cats_sorted]
    bars = ax.bar(x + (i - 1) * w, vals, w, label=label, color=col, edgecolor='white', linewidth=0.8)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.0f}',
                ha='center', va='bottom', fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels([f'{cl}\n(n={cn})' for cl, cn in zip(cat_labels, cat_counts)], fontsize=9)
ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_ylim(0, 115)
ax.set_title('Accuracy by Math Category & Approach\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('src/python/data/results/plot_B_category_grouped.png', dpi=150)
plt.close()


# ── Variation C: Horizontal stacked bar showing correct/incorrect ────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
for ax, app, label, col in zip(axes, approaches, labels, colors_main):
    cat_acc = [(NICE[c], df[df['Category'] == c][app].mean() * 100, len(df[df['Category'] == c]))
               for c in cats_sorted]
    cat_acc.reverse()  # so highest is at top
    names = [f'{n} (n={cnt})' for n, _, cnt in cat_acc]
    correct = [v for _, v, _ in cat_acc]
    incorrect = [100 - v for _, v, _ in cat_acc]

    y = np.arange(len(names))
    ax.barh(y, correct, color=col, alpha=0.85, label='Correct')
    ax.barh(y, incorrect, left=correct, color='#DDDDDD', label='Incorrect')
    for j, (c, ic) in enumerate(zip(correct, incorrect)):
        ax.text(c / 2, j, f'{c:.0f}%', ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Accuracy (%)')
    ax.set_title(label, fontsize=12, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

fig.suptitle('Correct vs Incorrect by Category\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold', y=1.02)
fig.tight_layout()
fig.savefig('src/python/data/results/plot_C_horizontal_stacked.png', dpi=150, bbox_inches='tight')
plt.close()


# ── Variation D: Heatmap ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
data_matrix = np.array([
    [df[df['Category'] == c][app].mean() * 100 for app in approaches]
    for c in cats_sorted
])
im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=11)
ax.set_yticks(range(len(cats_sorted)))
ax.set_yticklabels([f'{NICE[c]} (n={len(df[df["Category"]==c])})' for c in cats_sorted], fontsize=10)
for i in range(len(cats_sorted)):
    for j in range(len(approaches)):
        val = data_matrix[i, j]
        ax.text(j, i, f'{val:.0f}%', ha='center', va='center',
                fontsize=11, fontweight='bold', color='black' if 30 < val < 80 else 'white')
cbar = fig.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Accuracy (%)', fontsize=11)
ax.set_title('Accuracy Heatmap by Category & Approach\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('src/python/data/results/plot_D_heatmap.png', dpi=150)
plt.close()


# ── Variation E: Radar / Spider chart ────────────────────────────────────
angles = np.linspace(0, 2 * np.pi, len(cats_sorted), endpoint=False).tolist()
angles += angles[:1]  # close the polygon

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
for app, label, col in zip(approaches, labels, colors_main):
    vals = [df[df['Category'] == c][app].mean() * 100 for c in cats_sorted]
    vals += vals[:1]
    ax.plot(angles, vals, 'o-', linewidth=2, label=label, color=col)
    ax.fill(angles, vals, alpha=0.08, color=col)

ax.set_xticks(angles[:-1])
ax.set_xticklabels([NICE[c] for c in cats_sorted], fontsize=9)
ax.set_ylim(0, 105)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=8)
ax.set_title('Accuracy Radar by Category\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold', y=1.08)
ax.legend(loc='lower right', bbox_to_anchor=(1.25, 0), fontsize=10)
fig.tight_layout()
fig.savefig('src/python/data/results/plot_E_radar.png', dpi=150, bbox_inches='tight')
plt.close()


# ── Difficulty level setup ────────────────────────────────────────────────
df['Difficulty'] = df['Difficulty'].astype(int)
diff_levels = sorted(df['Difficulty'].unique())
diff_counts = {d: len(df[df['Difficulty'] == d]) for d in diff_levels}

# ── Variation F: Grouped bar chart by difficulty level ────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(diff_levels))
w = 0.25
for i, (app, label, col) in enumerate(zip(approaches, labels, colors_main)):
    vals = [df[df['Difficulty'] == d][app].mean() * 100 for d in diff_levels]
    bars = ax.bar(x + (i - 1) * w, vals, w, label=label, color=col, edgecolor='white', linewidth=0.8)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{val:.0f}%',
                ha='center', va='bottom', fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels([f'Level {d}\n(n={diff_counts[d]})' for d in diff_levels], fontsize=10)
ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_ylim(0, 115)
ax.set_title('Accuracy by Difficulty Level\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.tight_layout()
fig.savefig('src/python/data/results/plot_F_difficulty_grouped.png', dpi=150)
plt.close()


# ── Variation G: Heatmap — difficulty x approach ──────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
data_diff = np.array([
    [df[df['Difficulty'] == d][app].mean() * 100 for app in approaches]
    for d in diff_levels
])
im = ax.imshow(data_diff, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=11)
ax.set_yticks(range(len(diff_levels)))
ax.set_yticklabels([f'Level {d} (n={diff_counts[d]})' for d in diff_levels], fontsize=10)
for i in range(len(diff_levels)):
    for j in range(len(approaches)):
        val = data_diff[i, j]
        ax.text(j, i, f'{val:.0f}%', ha='center', va='center',
                fontsize=12, fontweight='bold', color='black' if 30 < val < 80 else 'white')
cbar = fig.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Accuracy (%)', fontsize=11)
ax.set_title('Accuracy Heatmap by Difficulty & Approach\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig('src/python/data/results/plot_G_difficulty_heatmap.png', dpi=150)
plt.close()


# ── Variation H: Line chart — accuracy trend across difficulty ────────────
fig, ax = plt.subplots(figsize=(8, 5))
for app, label, col in zip(approaches, labels, colors_main):
    vals = [df[df['Difficulty'] == d][app].mean() * 100 for d in diff_levels]
    ax.plot(diff_levels, vals, 'o-', linewidth=2.5, markersize=8, label=label, color=col)
    for d, val in zip(diff_levels, vals):
        ax.annotate(f'{val:.0f}%', (d, val), textcoords='offset points',
                    xytext=(0, 10), ha='center', fontsize=9, fontweight='bold', color=col)

ax.set_xlabel('Difficulty Level', fontsize=12)
ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_xticks(diff_levels)
ax.set_xticklabels([f'Level {d}\n(n={diff_counts[d]})' for d in diff_levels])
ax.set_ylim(0, 110)
ax.set_title('Accuracy vs Difficulty Level\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
fig.savefig('src/python/data/results/plot_H_difficulty_line.png', dpi=150)
plt.close()


# ── Variation I: Heatmap — category x difficulty (Pure LLM) ──────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, app, label in zip(axes, approaches, labels):
    data_cd = np.full((len(cats_sorted), len(diff_levels)), np.nan)
    for i, c in enumerate(cats_sorted):
        for j, d in enumerate(diff_levels):
            subset = df[(df['Category'] == c) & (df['Difficulty'] == d)]
            if len(subset) > 0:
                data_cd[i, j] = subset[app].mean() * 100

    im = ax.imshow(data_cd, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
    ax.set_xticks(range(len(diff_levels)))
    ax.set_xticklabels([f'L{d}' for d in diff_levels], fontsize=10)
    ax.set_yticks(range(len(cats_sorted)))
    ax.set_yticklabels([NICE[c] for c in cats_sorted], fontsize=9)
    for i in range(len(cats_sorted)):
        for j in range(len(diff_levels)):
            val = data_cd[i, j]
            if np.isnan(val):
                ax.text(j, i, '—', ha='center', va='center', fontsize=10, color='#999999')
            else:
                n = len(df[(df['Category'] == cats_sorted[i]) & (df['Difficulty'] == diff_levels[j])])
                ax.text(j, i, f'{val:.0f}%\n({n})', ha='center', va='center',
                        fontsize=9, fontweight='bold', color='black' if 30 < val < 80 else 'white')
    ax.set_xlabel('Difficulty Level')
    ax.set_title(label, fontsize=12, fontweight='bold')

fig.suptitle('Accuracy by Category & Difficulty\n(GPT-OSS-120b, n=100)', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.subplots_adjust(right=0.92)
cbar = fig.colorbar(im, ax=axes, shrink=0.8, pad=0.02)
cbar.set_label('Accuracy (%)', fontsize=11)
fig.savefig('src/python/data/results/plot_I_category_difficulty_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()


print("All plots saved:")
print("  A - Overall bar chart")
print("  B - Grouped bar chart by category")
print("  C - Horizontal stacked bars (correct/incorrect)")
print("  D - Heatmap (category x approach)")
print("  E - Radar/spider chart")
print("  F - Grouped bar chart by difficulty level")
print("  G - Heatmap (difficulty x approach)")
print("  H - Line chart (accuracy vs difficulty)")
print("  I - Heatmap (category x difficulty, per approach)")
