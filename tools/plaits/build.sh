#!/bin/sh
# Builds plaits.wasm from Mutable Instruments' Plaits (MIT, Emilie Gillet). Needs git and wasi-sdk 25
# (https://github.com/WebAssembly/wasi-sdk/releases). Run from tools/plaits: sh build.sh /path/to/wasi-sdk
set -e
W=${1:-$HOME/wasi-sdk-25.0-x86_64-linux}
[ -d mi ] || git clone --depth 1 https://github.com/pichenettes/eurorack.git mi
[ -f mi/stmlib/stmlib.h ] || { rm -rf mi/stmlib; git clone --depth 1 https://github.com/pichenettes/stmlib.git mi/stmlib; }
CC="algorithms additive_engine bass_drum_engine chiptune_engine chord_bank chord_engine dx_units fm_engine grain_engine hi_hat_engine lpc_speech_synth lpc_speech_synth_controller lpc_speech_synth_phonemes lpc_speech_synth_words modal_engine modal_voice naive_speech_synth noise_engine particle_engine phase_distortion_engine random resonator resources sam_speech_synth six_op_engine snare_drum_engine speech_engine string string_engine string_machine_engine string_voice swarm_engine units virtual_analog_engine virtual_analog_vcf_engine voice waveshaping_engine wavetable_engine wave_terrain_engine"
SRCS=""; for c in $CC; do SRCS="$SRCS $(find mi/plaits mi/stmlib -name "$c.cc" -not -path '*/test/*' | head -1)"; done
$W/bin/clang++ --target=wasm32-wasip1 --sysroot=$W/share/wasi-sysroot -O2 -DTEST -include stdio.h -fno-exceptions -fno-rtti -ffast-math -I mi -mexec-model=reactor -Wl,--strip-all -o plaits.wasm plaits_wasm.cc $SRCS
ls -la plaits.wasm
