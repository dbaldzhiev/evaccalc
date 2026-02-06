# Mathematical Model: Bulgarian Ordinance Iz-1971 (Annex 8a)

## 1. Primary Evacuation Time Formula ($\tau_{EB}$)

The total evacuation time is calculated using **Method L** (Length) or **Method Q** (Throughput), depending on the number of occupants ($N$).

### Selection Criteria
- **If $N \le 50$**: Use **Method L**.
- **If $N > 50$**: Use **Method Q**.

---

## 2. Method L (Length) for $N \le 50$

$$ \tau_{EB} = \sum \frac{L_i}{v_i} $$

Where:
- $L_i$ = Length of segment $i$ [m]
- $v_i$ = Travel speed in segment $i$ [m/min] (from **Table 11**)

**Note:** For the first segment (room of origin), $v$ is typically determined by density, but for low density ($D < 0.1$), assume $v = 100$ m/min for horizontal paths.

---

## 3. Method Q (Throughput) for $N > 50$

$$ \tau_{EB} = \frac{N}{Q_{exit}} + \tau_{delay} $$

Where:
- $N$ = Total number of occupants evacuating through the exit.
- $Q_{exit}$ = Effective throughput of the exit [people/min].
- $Q_{exit} = W_{eff} \times q_{max}$ (simplified) or determined by the limiting component in the path.
- More precisely, for a chain of segments:
  
  **Formula for a specific segment $i$:**
  $$ T_i = \frac{N}{W_i \times q_i} $$
  
  Where:
  - $W_i$ = Clear width of segment $i$ [m].
  - $q_i$ = Specific throughput at density $D$ [people / (m $\cdot$ min)] (from **Table 11**).

---

## 4. Density ($D$)

$$ D = \frac{N}{A} $$

Where:
- $N$ = Number of occupants in the room/segment.
- $A$ = Area of the room/segment [m²].

**Constraints:**
- If $D > 9.2$ people/m², clamp $D = 9.2$ and flag as critical logical error/boundary condition.

---

## 5. Flow Parameters (Table 11)

Look up $v$ (Speed) and $q$ (Specific Throughput) based on Density ($D$) and Path Type:
- **Horizontal**
- **Stair Down**
- **Stair Up**
- **Door**

**Interpolation Rules:**
- If $D$ is between table values, use the parameters for the **Next Higher Density** (conservative step function). Do NOT linearly interpolate $v$ or $q$.
- Example: If $D = 0.2$, use values for $D = 0.5$.

---

## 6. Geometry Rules

- **Stair Length ($L_{stair}$)**:
  $$ L_{stair} = \frac{H}{\sin(\alpha)} $$
  Where $H$ is height difference and $\alpha$ is the slope angle.
  *Approximation:* $L_{stair} \approx L_{plan} \times \sqrt{1 + \text{slope}^2}$ or actual walking path length.

- **Door Width ($W_{door}$)**:
  Use clear opening width.
  Length of door segment usually negligible unless wall thickness $\ge 0.7$ m.

---

## 7. Permissible Time ($t_{perm}$)

Compare calculated $\tau_{EB}$ with $t_{perm}$ from regulations logic (Building Height, Fire Resistance, etc.).
- See `regulations.json` for limits.