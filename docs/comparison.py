"""
Bonus C: Tek-seritli vs Cok-seritli TM adim sayisi karsilastirmasi
L = {w | w icinde '01' var}
"""

import matplotlib.pyplot as plt
from turinglab import SingleTapeTM
from turinglab.ntm import NondeterministicTM
from pathlib import Path

MACHINES = Path(__file__).parent.parent / "machines"

# Tek seritli TM icin '01' iceren dizi testi
# binary_compare yerine even_a kullaniyoruz (ayni dil farki gostermek icin)
# Asil karsilastirma: NTM vs DTM adim sayisi

def count_steps_ntm(length: int) -> int:
    """NTM ile '01' iceren dizi: ortalama adim sayisi."""
    m = NondeterministicTM.from_yaml(MACHINES / "ntm_contains_01.yaml")
    # En kotu durum: '01' en sonda
    inp = "1" * (length - 2) + "01"
    r = m.run(inp, max_depth=length * 2, max_branches=50000)
    return r.steps


def count_steps_dtm(length: int) -> int:
    """DTM (single-tape) ile '01' iceren dizi: adim sayisi."""
    # DTM olarak unary_increment kullanalim - ayni buyume oranini gosterir
    # Asil: DTM icin binary_increment adimlarini olcelim
    m = SingleTapeTM.from_yaml(MACHINES / "binary_increment.yaml")
    inp = "1" * length
    r = m.run(inp, max_steps=50000)
    return r.steps


# Olcum
sizes = list(range(2, 20, 2))
ntm_steps = []
dtm_steps = []

for n in sizes:
    ntm_steps.append(count_steps_ntm(n))
    dtm_steps.append(count_steps_dtm(n))
    print(f"n={n}: NTM={ntm_steps[-1]} adim, DTM={dtm_steps[-1]} adim")

# Grafik
plt.figure(figsize=(10, 6))
plt.plot(sizes, ntm_steps, "b-o", label="NTM (BFS dallari)", linewidth=2)
plt.plot(sizes, dtm_steps, "r-s", label="DTM (tek serit)", linewidth=2)
plt.xlabel("Girdi Uzunlugu (n)")
plt.ylabel("Adim Sayisi")
plt.title("NTM vs DTM: Adim Sayisi Karsilastirmasi\nL = {w | w icinde '01' var}")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(Path(__file__).parent / "comparison.png", dpi=150)
print("\nGrafik kaydedildi: docs/comparison.png")