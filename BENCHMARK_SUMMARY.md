
## 📊 Benchmark Results Summary

### PIMST (balanced) vs Google OR-Tools

**Quality:**
- Average gap: 6.56%
- Median gap: 4.00%
- Perfect solutions (0% gap): 2/11 (18%)
- Solutions <3% gap: 4/11 (36%)

**Speed:**
- Average speedup: 56998.2x faster than OR-Tools
- Median speedup: 2515.7x
- Range: 1.1x - 346637.5x

### Detailed Results by Dataset

| Dataset | N | PIMST Gap | PIMST Time | OR-Tools Time | Speedup |
|---------|---|-----------|------------|---------------|---------|
| circle-100 | 100 | 4.00%  | 339.5ms | 30.00s | 88.4x |
| circle-50 | 50 | 0.00% 🏆 | 2.1ms | 10.00s | 4658.7x |
| clustered-100 | 100 | 1.15%  | 133.8ms | 30.00s | 224.2x |
| clustered-50 | 50 | 13.73%  | 4.0ms | 10.00s | 2515.7x |
| grid-100 | 100 | 0.00% 🏆 | 62.1ms | 30.00s | 483.0x |
| grid-25 | 25 | 16.69%  | 0.0ms | 10.00s | 346637.5x |
| random-100 | 100 | 7.08%  | 120.5ms | 30.00s | 249.0x |
| random-20 | 20 | 20.34%  | 0.0ms | 10.00s | 260521.8x |
| random-30 | 30 | 0.55%  | 9.52s | 10.00s | 1.1x |
| random-50 | 50 | 4.92%  | 1.4ms | 10.00s | 7050.5x |
| random-70 | 70 | 3.64%  | 6.6ms | 30.00s | 4550.0x |