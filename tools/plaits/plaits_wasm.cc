// Plaits (Mutable Instruments, Emilie Gillet, MIT) as a WebAssembly module for Ngoma. A few voices, one patch each.
#include <string.h>
#include "plaits/dsp/voice.h"
using namespace plaits;
static const int NV = 8;
static char buf[NV][32768];
static Voice voices[NV];
static Patch patches[NV];
static Modulations mods[NV];
static float out_[NV][128], aux_[NV][128];
extern "C" {
__attribute__((export_name("pl_init"))) void pl_init(int i) {
  stmlib::BufferAllocator a(buf[i], 32768); voices[i].Init(&a);
  memset(&patches[i], 0, sizeof(Patch)); memset(&mods[i], 0, sizeof(Modulations));
  patches[i].note = 60; patches[i].harmonics = .5f; patches[i].timbre = .5f; patches[i].morph = .5f; patches[i].decay = .5f; patches[i].lpg_colour = .5f;
  mods[i].trigger_patched = true; mods[i].level_patched = false;
}
__attribute__((export_name("pl_set"))) void pl_set(int i, float note, float harm, float timbre, float morph, int engine, float decay, float colour) {
  Patch& p = patches[i]; p.note = note; p.harmonics = harm; p.timbre = timbre; p.morph = morph; p.engine = engine; p.decay = decay; p.lpg_colour = colour;
}
__attribute__((export_name("pl_mod"))) void pl_mod(int i, float fm_amt, float timbre_amt, float morph_amt) {
  Patch& p = patches[i]; p.frequency_modulation_amount = fm_amt; p.timbre_modulation_amount = timbre_amt; p.morph_modulation_amount = morph_amt;
}
__attribute__((export_name("pl_trig"))) void pl_trig(int i, float trig, int patched, float level) {
  mods[i].trigger = trig; mods[i].trigger_patched = patched != 0; mods[i].level = level; mods[i].level_patched = false;
}
__attribute__((export_name("pl_out"))) float* pl_out(int i) { return out_[i]; }
__attribute__((export_name("pl_aux"))) float* pl_aux(int i) { return aux_[i]; }
__attribute__((export_name("pl_render"))) void pl_render(int i, int n) {
  Voice::Frame fr[kBlockSize];
  for (int o = 0; o + (int)kBlockSize <= n; o += kBlockSize) {
    voices[i].Render(patches[i], mods[i], fr, kBlockSize);
    for (int k = 0; k < (int)kBlockSize; k++) { out_[i][o + k] = fr[k].out / 32768.f; aux_[i][o + k] = fr[k].aux / 32768.f; }
    mods[i].trigger = 0.f;
  }
}
}
