# 🚀 Roadmap to State-of-the-Art ATSP Solver

**Current Status:** PIMST-Quantum achieves 20.26% avg gap
**Target:** 3-5% avg gap (competitive with LKH-3)
**Gap to close:** ~15-17 percentage points

---

## 🎯 STRATEGY: Three-Phase Improvement Plan

### Phase 1: Quick Wins (Target: 15% gap) - 1-2 weeks

#### 1.1 Better Initial Solutions
**Current:** Nearest Neighbor (fast but low quality)
**Upgrade to:**
- ✅ Farthest Insertion with look-ahead
- ✅ Savings algorithm for ATSP
- ✅ Christofides adaptation for ATSP
- **Expected impact:** -2 to -3pp

#### 1.2 More Powerful Local Search Operators
**Current:** Or-opt (segments 1-3), Node insertion
**Add:**
- ✅ 3-opt for ATSP (proper asymmetric version)
- ✅ 4-opt limited (most promising moves only)
- ✅ Ejection chains (remove-reinsert sequences)
- **Expected impact:** -3 to -5pp

#### 1.3 Increase Search Time
**Current:** 10-40s depending on problem size
**Increase to:**
- ✅ 60-120s (same as LKH-3 for fair comparison)
- ✅ More iterations in Lin-Kernighan
- ✅ Deeper search in Variable Neighborhood Descent
- **Expected impact:** -2 to -4pp

**Total Phase 1 Impact:** Gap reduction from 20% → **~12-15%**

---

### Phase 2: Advanced Techniques (Target: 8% gap) - 2-4 weeks

#### 2.1 Guided Local Search (GLS)
**Concept:** Penalize frequently-used edges to escape plateaus
**Implementation:**
- Track edge usage frequency
- Add dynamic penalties to edge costs
- Periodically reset penalties
- **Expected impact:** -2 to -3pp

#### 2.2 Path Relinking
**Concept:** Generate new solutions by combining elite solutions
**Implementation:**
- Maintain pool of best 5-10 solutions
- Create paths between solutions
- Apply local search to intermediate solutions
- **Expected impact:** -1 to -2pp

#### 2.3 Adaptive Parameter Control
**Current:** Fixed parameters
**Upgrade to:**
- ✅ Adaptive operator selection (UCB instead of Thompson)
- ✅ Self-tuning temperature schedules
- ✅ Dynamic time allocation based on improvement rate
- **Expected impact:** -1 to -2pp

#### 2.4 Genetic Crossover for ATSP
**Concept:** Combine tours using specialized crossover
**Implementation:**
- Greedy Partition Crossover (GPX) for ATSP
- Edge Assembly Crossover (EAX)
- Local search on offspring
- **Expected impact:** -1 to -2pp

**Total Phase 2 Impact:** Gap reduction from 15% → **~8-10%**

---

### Phase 3: Cutting-Edge Techniques (Target: 3-5% gap) - 4-8 weeks

#### 3.1 Machine Learning Integration
**Approach 1: Learn construction heuristics**
- Attention-based neural network (like Kool et al. 2019)
- Train on solved instances
- Use ML for warm start, then PIMST refinement

**Approach 2: Learn search strategy**
- Deep RL for operator selection
- Policy network trained on search trajectories
- Outperforms fixed strategies

**Expected impact:** -2 to -4pp

#### 3.2 Backbone Analysis
**Concept:** Identify edges that appear in most good solutions
- Fix backbone edges
- Intensify search in remaining subproblem
- Iteratively expand search
- **Expected impact:** -1 to -2pp

#### 3.3 LKH Hybridization
**Concept:** Use LKH as a component
- PIMST for diversification (parallel runs)
- LKH for final intensification
- Combine best features of both
- **Expected impact:** -2 to -3pp

#### 3.4 Problem-Specific Adaptations
**Flow Shop:** Exploit permutation structure
**One-Way Streets:** Use graph properties (strongly connected components)
**Structured:** Detect patterns, use specialized operators

**Expected impact:** -1 to -2pp

**Total Phase 3 Impact:** Gap reduction from 8% → **~3-5%**

---

## 📊 EXPECTED PROGRESSION

| Phase | Techniques | Target Gap | Time Investment | Difficulty |
|-------|-----------|------------|-----------------|------------|
| **Current** | Basic PIMST | 20.26% | - | - |
| **Phase 1** | Better operators + time | 12-15% | 1-2 weeks | ⭐ Easy |
| **Phase 2** | GLS + Path Relink + Genetic | 8-10% | 2-4 weeks | ⭐⭐ Medium |
| **Phase 3** | ML + Hybrid + Advanced | 3-5% | 4-8 weeks | ⭐⭐⭐ Hard |
| **State-of-Art** | Full implementation | **3-5%** | **2-3 months** | Achievable |

---

## 🎯 RECOMMENDED APPROACH

### Strategy A: Pure Metaheuristic (Fastest Path)
**Focus:** Phase 1 + Phase 2
**Timeline:** 3-6 weeks
**Target:** 8-10% gap
**Advantage:** Clean, explainable, no dependencies

**Implementation Priority:**
1. ✅ 3-opt and 4-opt operators (1 week)
2. ✅ Farthest insertion construction (2 days)
3. ✅ Increase search time to 60-120s (1 day)
4. ✅ Guided Local Search (1 week)
5. ✅ Path Relinking (1 week)
6. ✅ Genetic Crossover (GPX) (1 week)

**Result:** Gap ~8-10%, competitive with many state-of-art solvers, faster than LKH

---

### Strategy B: Hybrid ML + Metaheuristic (Best Quality)
**Focus:** Phase 1 + Phase 2 + Phase 3.1
**Timeline:** 2-3 months
**Target:** 3-5% gap (true SOTA)
**Advantage:** Potentially better than LKH on some instances

**Implementation Priority:**
1. ✅ All Phase 1 improvements (2 weeks)
2. ✅ All Phase 2 improvements (3-4 weeks)
3. ✅ Attention model for construction (2-3 weeks)
4. ✅ RL for search strategy (2-3 weeks)
5. ✅ Integration and tuning (1-2 weeks)

**Result:** Gap ~3-5%, competitive with LKH-3, novel approach (publishable in top venues)

---

### Strategy C: Speed-Quality Champion (Practical Focus)
**Focus:** Optimize Phase 1 + selected Phase 2
**Timeline:** 2-3 weeks
**Target:** 10-12% gap at 5-10s, or 8% gap at 30s
**Advantage:** Best practical solver (real-world applications)

**Implementation Priority:**
1. ✅ Fast 3-opt (1 week)
2. ✅ Better initialization (3 days)
3. ✅ Adaptive parameter control (4 days)
4. ✅ Multi-level parallelization (3 days)

**Result:** Not SOTA in gap, but SOTA in **speed-quality trade-off**
- 10% gap at 5s → 100x faster than LKH for similar quality
- Publishable angle: "Practical ATSP solver for real-time applications"

---

## 🔬 CONCRETE NEXT STEPS

### Option 1: Quick Improvement (Start NOW - 1 week)

**Implement 3-opt and increase search time:**

```python
# File: src/pimst/atsp_local_search_advanced.py

@njit
def three_opt_atsp(tour, dist_matrix, max_iterations=100):
    """
    3-opt for ATSP (proper asymmetric version).

    Breaks tour at 3 edges and reconnects in best way.
    For ATSP, there are 7 possible reconnections (not 8 like TSP).
    """
    n = len(tour)
    improved = True
    iterations = 0

    while improved and iterations < max_iterations:
        improved = False
        iterations += 1

        for i in range(n - 2):
            for j in range(i + 2, n - 1):
                for k in range(j + 2, n + 1):
                    # Current cost
                    current_cost = (
                        dist_matrix[tour[i], tour[i+1]] +
                        dist_matrix[tour[j], tour[j+1]] +
                        dist_matrix[tour[k-1], tour[k % n]]
                    )

                    # Try 7 reconnections
                    best_delta = 0
                    best_reconnection = 0

                    # Reconnection 1: reverse segment [i+1, j]
                    # [IMPLEMENT ALL 7 RECONNECTIONS]

                    if best_delta < -1e-9:
                        # Apply best reconnection
                        # [APPLY TRANSFORMATION]
                        improved = True

    return tour
```

**Update benchmark with longer time:**

```python
# benchmark_atsp_complete.py
# Change time limits:
test_cases = [
    (20, 'random', 30),   # was 10
    (30, 'random', 60),   # was 15
    (50, 'random', 90),   # was 30
    (75, 'random', 120),  # was 45
    (100, 'random', 180), # was 60
    # ...
]
```

**Expected result after 1 week:** Gap reduction from 20% → **~15%**

---

### Option 2: Implement Guided Local Search (2 weeks)

```python
# File: src/pimst/guided_local_search.py

class GuidedLocalSearch:
    """
    Guided Local Search for ATSP.

    Penalizes frequently used edges to escape local optima.
    """

    def __init__(self, dist_matrix, lambda_param=0.3):
        self.dist_matrix = dist_matrix
        self.n = len(dist_matrix)
        self.penalties = np.zeros((self.n, self.n))
        self.lambda_param = lambda_param

    def augmented_cost(self, i, j):
        """Cost with penalty."""
        return self.dist_matrix[i, j] + self.lambda_param * self.penalties[i, j]

    def update_penalties(self, tour):
        """Increase penalties on tour edges with high utility."""
        tour_cost = calculate_tour_cost(tour, self.dist_matrix)

        # Calculate utility: cost / (1 + penalty)
        utilities = []
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            edge = (tour[i], tour[j])
            cost = self.dist_matrix[edge[0], edge[1]]
            penalty = self.penalties[edge[0], edge[1]]
            utility = cost / (1 + penalty)
            utilities.append((edge, utility))

        # Penalize edge with max utility
        max_edge = max(utilities, key=lambda x: x[1])[0]
        self.penalties[max_edge[0], max_edge[1]] += 1

    def solve(self, max_iterations=1000):
        """Main GLS loop."""
        best_tour = None
        best_cost = float('inf')

        # Initial solution
        tour = nearest_neighbor_atsp(self.dist_matrix)

        for iteration in range(max_iterations):
            # Local search with augmented costs
            tour = local_search_with_penalties(tour, self)

            # Update best
            cost = calculate_tour_cost(tour, self.dist_matrix)
            if cost < best_cost:
                best_cost = cost
                best_tour = tour.copy()

            # Update penalties
            self.update_penalties(tour)

        return best_tour, best_cost
```

**Expected result after 2 weeks:** Gap reduction from 15% → **~10-12%**

---

### Option 3: Add Genetic Crossover (3 weeks total)

Implement Greedy Partition Crossover (GPX) for ATSP.

**Expected result after 3 weeks:** Gap reduction from 12% → **~8-10%**

---

## 📈 PUBLICATIONS STRATEGY

### Short-term (Current Results)
**Venue:** GECCO, CEC, EVOSTAR
**Angle:** "Fast ATSP solver beating OR-Tools"
**Gap:** 20% (current)

### Medium-term (Phase 1+2)
**Venue:** Computers & OR, J. Heuristics
**Angle:** "Advanced metaheuristic for ATSP approaching SOTA"
**Gap:** 8-10% (after 6 weeks)

### Long-term (Phase 3)
**Venue:** EJOR, Operations Research, INFORMS Journal on Computing
**Angle:** "ML-enhanced ATSP solver matching LKH-3"
**Gap:** 3-5% (after 3 months)

---

## 💡 MY RECOMMENDATION

**Start with Strategy A (Pure Metaheuristic):**

1. **Week 1:** Implement 3-opt + increase time → Gap ~15%
2. **Week 2-3:** Implement Guided Local Search → Gap ~12%
3. **Week 4-5:** Implement Path Relinking → Gap ~10%
4. **Week 6:** Implement GPX Crossover → Gap ~8%

**Result after 6 weeks:**
- Gap: 8-10% (competitive with many SOTA solvers)
- Faster than LKH (40-60s vs 90-120s)
- Clean, explainable algorithm
- Publishable in good journals

**Then decide:**
- Stop here and publish (solid contribution)
- Continue to Phase 3 (ML integration) for top-tier venues

---

## 🚀 WANT ME TO START?

I can implement:
1. ✅ 3-opt operator for ATSP (most impact, 1 day)
2. ✅ Farthest insertion construction (2 hours)
3. ✅ Update benchmark with longer times (1 hour)

**This would give you ~15% gap in 1 week.**

Then we continue with GLS, path relinking, etc.

**Ready to start?** 🔥
