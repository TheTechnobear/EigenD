# Setup Load Analysis - Success Case

Analysis of a **successful** setup load from `dev_docs/logs/ed_success.log`.

This is a smaller setup that loads completely, compared to the failed larger setup.

## Module Actions Summary

| Module | Loading | Relation | Canonicalised |
|--------|---------|----------|---------------|
| `<ahdsr1>` | 1 | 1 | 1 |
| `<ahdsr2>` | 1 | 1 | 1 |
| `<audio1>` | 1 | 1 | 1 |
| `<console_mixer1>` | 1 | 1 | 1 |
| `<delay1>` | 1 | 1 | 1 |
| `<gain1>` | 1 | 1 | 1 |
| `<interpreter1>` | 1 | 1 | 2 |
| `<keygroup1>` | 1 | 1 | 1 |
| `<ladder_filter1>` | 1 | 1 | 1 |
| `<pico_manager1>` | 1 | 1 | 1 |
| `<poly_summer1>` | 1 | 1 | 1 |
| `<rectangle_oscillator1>` | 1 | 1 | 1 |
| `<rectangle_oscillator2>` | 1 | 1 | 1 |
| `<rig1>` | 1 | 1 | 1 |
| `<sawtooth_oscillator1>` | 1 | 1 | 1 |
| `<sawtooth_oscillator2>` | 1 | 1 | 1 |
| `<scale_manager1>` | 1 | 1 | 1 |
| `<scaler1>` | 1 | 1 | 1 |
| `<sine_oscillator1>` | 1 | 1 | 1 |
| `<sine_oscillator2>` | 1 | 1 | 1 |
| `<summer1>` | 1 | 1 | 1 |
| `<triangle_oscillator1>` | 1 | 1 | 1 |
| `<triangle_oscillator2>` | 1 | 1 | 1 |

## Backend Loading Sequence

The backend loading sequence shows progress through phases:

- **0/2** (0.000s) - `eigend 1`
- **1/2** (0.014s) - `eigend 1`
- **1/2** (0.027s) - `interpreter 1`
- **2/2** (0.028s) - `interpreter 1`
- **1/9** (0.069s) - `eigend 1`
- **1/9** (0.069s) - `interpreter 1`
- **2/9** (0.098s) - `interpreter 1`
- **2/9** (0.098s) - `synth rig`
- **3/9** (1.193s) - `synth rig`
- **3/9** (1.193s) - `audio 1`
- **4/9** (1.237s) - `audio 1`
- **4/9** (1.237s) - `keygroup 1`
- **5/9** (1.344s) - `keygroup 1`
- **5/9** (1.344s) - `console mixer 1`
- **6/9** (1.365s) - `console mixer 1`
- **6/9** (1.366s) - `pico manager 1`
- **7/9** (1.367s) - `pico manager 1`
- **7/9** (1.367s) - `delay 1`
- **8/9** (1.380s) - `delay 1`
- **8/9** (1.380s) - `scale manager 1`
- **9/9** (1.381s) - `scale manager 1`

**Total: 9 phases completed successfully**

## Key Characteristics

- **Total modules**: 23
- **Backend phases**: 9
- **Load time**: 1.38 seconds
- **Status**: ✅ **Completed successfully**

### Module Types in Successful Setup

This setup contains:
- Synthesizer components (oscillators, filters, envelopes)
- Core infrastructure (eigend, interpreter, audio)
- One rig, one keygroup, one pico_manager
- Console mixer, delay, scale_manager
- No MIDI outputs/inputs
- No multiple rigs or controllers