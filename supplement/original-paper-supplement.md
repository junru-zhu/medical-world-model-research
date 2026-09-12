# Supplementary Results for the ICU Chart-Process Benchmark

## Supplementary Table S1. External 12-hour variable-level MAE

MAE is in each variable's original dataset unit. Neural values are means
across five fitted instances; parentheses are across-seed standard deviations.
These values pool observed targets within each variable and are not an
additive decomposition of the patient-macro primary outcome. No minimum
clinically important difference was prespecified.

| Variable | Unit | Targets | Ridge VAR | GRU-D-style | Masked Transformer | State-space model |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| HR | beats/min | 27,883 | 9.843 | 9.748 (0.064) | 9.648 (0.110) | 13.561 (0.355) |
| O2Sat | % | 27,226 | 2.029 | 2.012 (0.056) | 1.957 (0.037) | 2.181 (0.013) |
| Temp | degrees C | 10,813 | 0.502 | 0.511 (0.006) | 0.511 (0.011) | 0.583 (0.013) |
| SBP | mm Hg | 27,367 | 16.737 | 15.441 (0.085) | 15.277 (0.142) | 19.125 (0.601) |
| MAP | mm Hg | 27,196 | 11.379 | 10.173 (0.068) | 10.326 (0.116) | 12.427 (0.215) |
| DBP | mm Hg | 27,360 | 8.809 | 8.709 (0.061) | 8.688 (0.100) | 10.663 (0.343) |
| Resp | breaths/min | 25,030 | 3.372 | 3.323 (0.019) | 3.353 (0.075) | 3.609 (0.044) |
| BaseExcess | mmol/L | 59 | 3.680 | 4.291 (0.096) | 4.040 (0.082) | 3.824 (0.268) |
| HCO3 | mmol/L | 48 | 2.501 | 2.781 (0.130) | 2.662 (0.174) | 2.563 (0.166) |
| FiO2 | fraction | 595 | 0.159 | 0.176 (0.004) | 0.174 (0.002) | 0.185 (0.002) |
| pH | unitless | 552 | 0.057 | 0.060 (0.001) | 0.059 (0.001) | 0.063 (0.000) |
| PaCO2 | mm Hg | 552 | 6.089 | 6.678 (0.155) | 6.684 (0.094) | 6.985 (0.059) |
| SaO2 | % | 477 | 2.437 | 5.929 (0.242) | 5.983 (0.370) | 2.515 (0.303) |
| BUN | mg/dL | 1,501 | 5.707 | 5.692 (0.053) | 5.696 (0.066) | 12.613 (0.236) |
| Chloride | mmol/L | 142 | 2.841 | 3.048 (0.104) | 2.997 (0.068) | 3.519 (0.244) |
| Creatinine | mg/dL | 1,503 | 0.403 | 0.487 (0.020) | 0.442 (0.006) | 0.920 (0.016) |
| Glucose | mg/dL | 6,714 | 29.553 | 30.523 (0.064) | 30.869 (0.255) | 32.256 (0.181) |
| Magnesium | mg/dL | 1,398 | 0.227 | 0.241 (0.004) | 0.241 (0.002) | 0.270 (0.006) |
| Phosphate | mg/dL | 835 | 0.813 | 0.814 (0.014) | 0.817 (0.019) | 0.982 (0.012) |
| Potassium | mmol/L | 2,122 | 0.379 | 0.395 (0.006) | 0.404 (0.007) | 0.433 (0.005) |
| Hct | % | 1,570 | 3.096 | 3.059 (0.017) | 3.046 (0.058) | 4.889 (0.092) |
| Hgb | g/dL | 1,603 | 1.152 | 1.183 (0.031) | 1.120 (0.028) | 1.776 (0.024) |
| WBC | 10^3/uL | 1,412 | 2.578 | 2.884 (0.051) | 2.884 (0.062) | 4.335 (0.042) |
| Platelets | 10^3/uL | 1,443 | 35.507 | 34.486 (0.852) | 33.948 (1.377) | 77.234 (1.434) |

## Supplementary Table S2. Horizon-specific value-metric support

| Cohort | Horizon | Patients with scored targets | Observed targets |
| --- | ---: | ---: | ---: |
| Internal test | 1 h | 1,810 | 36,216 |
| Internal test | 3 h | 1,807 | 36,258 |
| Internal test | 6 h | 1,796 | 35,149 |
| Internal test | 12 h | 1,806 | 34,518 |
| Internal test | 24 h | 1,773 | 32,924 |
| External test | 1 h | 10,245 | 198,911 |
| External test | 3 h | 10,245 | 197,165 |
| External test | 6 h | 10,218 | 194,715 |
| External test | 12 h | 10,178 | 195,401 |
| External test | 24 h | 10,162 | 192,680 |

The anchor set is common across horizons; scored-patient and observed-target
support varies because missing targets are not included in value metrics.

## Supplementary Table S3. Implementation-seed exclusion sensitivity

After excluding seed 20260912, external 12-hour NMAE was 0.5216 for GRU-D,
0.5213 for the masked Transformer, and 0.6234 for the state-space model.
The corresponding 20-draw coverage values were 0.8435, 0.8684, and 0.5001.
The main ranking and underdispersion conclusions were unchanged.

## Supplementary Table S4. Neural implementation configuration

| Component | Frozen setting |
| --- | --- |
| Training unit | One seeded contiguous window per eligible training patient and epoch |
| Training window | Up to 72 one-step transitions (73 rows) |
| Validation windows | Exhaustive contiguous windows, stride 72 transitions; 3,127 windows |
| Checkpoint selection | Lowest mean validation total loss |
| Maximum epochs / patience | 20 / 4 epochs without improvement |
| Batch size | 64 for training and validation; 128 for rollout evaluation |
| Optimizer | AdamW, learning rate 0.0003, weight decay 0.00001 |
| Gradient clipping | Global norm 1.0 |
| Hidden / latent size | 96 / 32 |
| Transformer | 3 layers, 4 heads, dropout 0.1 |
| Objective | Observed-target Gaussian NLL + 0.25 mask BCE + 0.001 latent KL for the state-space model |
| Observation log-scale bound | Smooth sigmoid mapping to [-5, 2] |
| State-space latent log-scale bound | Smooth sigmoid mapping to [-5, 1] |
| Mask target | All valid next-step variable masks |
| Value target | Next-step values only where observed |
| Seeds | 20260912 through 20260916 |
| Accelerator | Apple MPS; patient windows and data order seeded, kernels potentially nondeterministic |
| Parameter counts | GRU-D-style 59,232; state-space 93,320; Transformer 247,848 |

All GRU-D-style and Transformer checkpoints selected epoch 20. State-space
checkpoints selected epochs 7 through 20. Ridge regularization was selected
separately by validation 12-hour patient-macro NMAE, whereas neural
checkpoints used the training objective above.
