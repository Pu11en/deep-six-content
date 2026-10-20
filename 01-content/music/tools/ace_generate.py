#!/usr/bin/env python3
"""Generate instrumental music beds locally with ACE-Step 1.5 (MIT license, free, runs on this PC's GPU).

Run with ACE-Step's own environment, from its folder:
  cd /home/drewp/tools/ACE-Step-1.5 && .venv/bin/python \
    /home/drewp/main-projects/deep-six-content/01-content/music/tools/ace_generate.py PROMPTS.json OUT_DIR

Planning model: ACE_LM env var, default acestep-5Hz-lm-1.7B (0.6B is the low-memory fallback).
Writes one WAV per prompt and seed, plus OUT_DIR/generation-log.json with every setting.
"""
import json, os, sys, time

ACE = '/home/drewp/tools/ACE-Step-1.5'
sys.path.insert(0, ACE)
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

prompts_path, out_dir = sys.argv[1], sys.argv[2]
LM = os.environ.get('ACE_LM', 'acestep-5Hz-lm-1.7B')
spec = json.load(open(prompts_path))
os.makedirs(out_dir, exist_ok=True)

dit = AceStepHandler()
msg, ok = dit.initialize_service(project_root=ACE, config_path='acestep-v15-turbo', device='auto',
                                 offload_to_cpu=True, offload_dit_to_cpu=True)
if not ok:
    sys.exit(f'DiT init failed: {msg}')
llm = LLMHandler()
msg, ok = llm.initialize(checkpoint_dir=os.path.join(ACE, 'checkpoints'), lm_model_path=LM,
                         backend='pt', device='auto', offload_to_cpu=True, dtype=None)
if not ok:
    sys.exit(f'LM init failed: {msg}')

log = []
jobs = [(p, k) for p in spec['prompts'] for k in range(spec.get('seeds_per_prompt', 1))]
if spec.get('seed_order') == 'seed-first':
    jobs.sort(key=lambda j: j[1])  # one version of every prompt first, then second versions
for p, k in jobs:
    if True:
        seed = 1000 + 17 * k + len(log)
        params = GenerationParams(task_type='text2music', thinking=True, caption=p['caption'],
                                  lyrics='[Instrumental]', instrumental=True, bpm=p.get('bpm'),
                                  keyscale=p.get('keyscale', ''), timesignature='4', vocal_language='unknown',
                                  duration=spec.get('duration', 95), inference_steps=8, guidance_scale=1.0, seed=seed)
        config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format='wav')
        t0 = time.time()
        result = generate_music(dit, llm, params=params, config=config, save_dir=out_dir)
        entry = {'name': p['name'], 'seed': seed, 'seconds_to_make': round(time.time() - t0, 1),
                 'success': result.success, 'error': result.error}
        if result.success:
            src = result.audios[0]['path']
            dst = os.path.join(out_dir, f"{p['name']}-seed{seed}.wav")
            os.replace(src, dst)
            entry['file'] = os.path.basename(dst)
        log.append({**entry, 'bpm': p.get('bpm'), 'keyscale': p.get('keyscale'), 'caption': p['caption']})
        print(json.dumps(entry), flush=True)
        json.dump({'model': f'ACE-Step 1.5 acestep-v15-turbo + {LM} (MIT)', 'prompts': prompts_path,
                   'runs': log}, open(os.path.join(out_dir, 'generation-log.json'), 'w'), indent=1)
