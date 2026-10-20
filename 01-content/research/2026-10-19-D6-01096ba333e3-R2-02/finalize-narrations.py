import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools').resolve()))
from d6_harness import Harness,ident,now
P=Path(__file__).resolve().parent
HOOK='Why would a wasp lay its egg inside a cockroach’s egg case?'
MAIN='SRC-0fa91dcbc971'; UF='SUP-d34ca591f2c4'; UMN='SUP-139443c3574f'; TRAP='SUP-b8f992d02be3'
def refs(*items):return [prefix+'-F'+str(n) for prefix,nums in items for n in nums]
bodies=[
('Getting through the egg case', '''An ensign wasp is putting her young beside its food. But getting through that case takes work.

She braces herself against it and pushes in a slender egg-laying organ. The University of Florida describes this step as usually taking 15 to 30 minutes.

She leaves one egg inside. The larva that hatches has pointed jaws with small teeth for cutting through the individual cockroach eggs.

American cockroaches, one of this wasp's hosts, leave their egg cases in cracks and crevices. During an inspection, check those gaps in warm, damp areas, including sheltered spaces under sinks.''', refs((MAIN,[1,2]),(UF,[1,2]),(UMN,[1]),(TRAP,[2]))),
('Recognizing the wasp', '''That's an ensign wasp. Her young feeds on the cockroach eggs inside.

The adult has an unusual shape: a tiny abdomen perched on a thin stalk. It flicks that part of its body up and down like a flag. That flag shape is where its name comes from.

This wasp is only about five to seven millimeters long, and it doesn't sting or bite people.

If you find one indoors, check for cockroach activity. Small insect monitoring cards under sinks or behind appliances can help you find where roaches are moving. Set them tight against a wall, along the edges the insects follow.''', refs((MAIN,[1,2,3,4]),(TRAP,[1,2,3]))),
('Checking for roaches and their eggs', '''An ensign wasp lays one egg there so her young can feed on the cockroach eggs. American cockroaches are among its hosts.

American females leave their egg cases in cracks or crevices. German females carry theirs until the eggs are ready to hatch. Different species leave different things to look for during an inspection.

When you bring bags, boxes or luggage indoors, check for both roaches and egg cases. Corrugated cardboard also provides hiding places, so remove unnecessary boxes after unpacking.''', refs((MAIN,[1,2]),(UMN,[1,2,3]))),
('Finding where roaches are active', '''An ensign wasp leaves one egg inside, where her young will feed on the cockroach eggs.

If you spot the adult indoors and want to check for roaches, start with small insect monitoring cards.

Roaches tend to follow edges. Place the cards directly against walls under sinks or behind the refrigerator, with the openings lined up along the wall.

Use several locations and compare catches. The traps work while you're asleep or away, helping show where activity is concentrated.

A card near an exterior door can also help detect outdoor cockroaches coming in. Keep checking the cards over time to see whether catches rise or fall. Use that information to guide the inspection and control work.''', refs((MAIN,[1,2]),(TRAP,[1,2,3]))),
('From egg to adult, inside the case', '''The cockroach eggs feed a young ensign wasp, but the case also holds it while it grows into an adult.

The mother places one egg inside. When it hatches, the larva uses pointed jaws with tiny teeth to cut through the individual cockroach eggs.

After feeding and growing, it becomes a pupa inside the same case. It doesn't spin a cocoon.

Then the adult has to get out. It cuts a small, round hole with a jagged edge near one end of the case and emerges through it.''', refs((MAIN,[1,2]),(UF,[2,3])))
]
scripts=[{'text':HOOK+'\n\n'+body,'fact_ids':ids} for title,body,ids in bodies]
def save(name,data):(P/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
h=Harness('.')
with h.locked():
 c=h.state['current'];assert c['run_id']=='D6-01096ba333e3' and c['status']=='waiting_narrations'
 assert c['review_id']=='review-885cb164f2fa'
 for script in scripts:
  assert script['text'].split('\n\n',1)[0]==c['selected_hook']['text']==HOOK
  assert chr(0x2014) not in script['text']
  h.clean_spoken(script['text'],'narration');h.check_facts(script['fact_ids'],h.context()['sources'][0])
 assert len({s['text'] for s in scripts})==5
 oldreview=c['review_id'];c.update(scripts=scripts,review_id=ident('review'))
 h.state['decisions'].append({'stage':'narrations','action':'editorial_revision','run_id':c['run_id'],'previous_review_id':oldreview,'review_id':c['review_id'],'note':'Removed repeated explanations, filler and detached caveat endings from the new writer batch. Kept five separate supported lessons and exact hook 4C. No narration selected.','at':now()})
 h.save()
 baseline=json.loads((P/'before-import.json').read_text())
 assert h.state['approved']==baseline['approved']
 assert h.state['next_source_id']==baseline['next_source_id']
 assert [x for x in h.state['source_queue'] if x['id']!=MAIN]==[x for x in baseline['source_queue'] if x['id']!=MAIN]
 assert hashlib.sha256(Path('BOARD.md').read_bytes()).hexdigest()==baseline['board_sha256']
 save('narration-check.json',{'run_id':c['run_id'],'review_id':c['review_id'],'status':c['status'],'choices':len(scripts),'exact_hook_in_all':True,'em_dashes':0,'fact_references_valid':True,'new_sources_accepted':3,'new_supported_facts':11,'word_counts':[len(x['text'].split()) for x in scripts],'titles':[x[0] for x in bodies],'approved_audio_and_other_queue_entries_unchanged':True,'board_unchanged':True,'editorial_check':'Every paragraph supplies mechanism, recognition, inspection or monitoring detail. No repeated no-hatch conclusion or generic useful-takeaway ending. Options are intentionally shorter than the previous padded batch.','limits':['Under-sink inspection is an application of warm, moist habitat plus extension inspection sites, not a wasp-sighting diagnosis.','Option 3 compares egg handling; it does not identify German cockroaches as this wasp\'s hosts.','Option 5 teaches natural-enemy biology and makes no whole-home treatment claim.']})
 save('final-narrations.json',{'run_id':c['run_id'],'review_id':c['review_id'],'titles':[x[0] for x in bodies],'scripts':scripts})
 checkpoint=json.loads((P/'checkpoint.json').read_text());checkpoint.update(status='imported',pending_action=None,writing_status=c['status'],review_id=c['review_id'],presentation='Full narration text in chat; no preview opened.');save('checkpoint.json',checkpoint)
 notes=Path('01-content/mp3-system/narration-options.md')
 notes.write_text('# Five new narration choices\n\nDrew requested a new batch with less repetition and useful pest-control teaching. Review '+c['review_id']+'. Read all five in chat. Nothing selected yet.\n\n'+'\n\n---\n\n'.join('## '+str(i)+'. '+bodies[i-1][0]+'\n\n'+script['text'] for i,script in enumerate(scripts,1))+'\n\nEvidence and checks: [supporting research](../research/'+P.name+'/narration-check.json).\n')
 plan=Path('01-content/mp3-system/session-plan.md');text=plan.read_text().replace('The current narration texts and review ID remain valid.','The rejected narration batch is archived; use the latest review ID below.')
 text=text.replace('Supporting facts are checked; [five complete narration choices](narration-options.md) are ready. Review `review-5c13e5e1635f` is waiting for your narration choice.','Drew rejected the first narrations for repetition, obvious conclusions and fluff. Three additional university sources now support eleven new facts. [Five new narration choices](narration-options.md) are ready and shown in chat. Review `'+c['review_id']+'` is waiting for your narration choice.')
 plan.write_text(text)
 r1=Path('01-content/research/2026-10-19-D6-e531a6490a21-R1-01')
 check=json.loads((r1/'checkpoint.json').read_text());check.update(narration_review_id=c['review_id'],supporting_research_folder=str(P.relative_to(Path.cwd())),writing_status=c['status']);(r1/'checkpoint.json').write_text(json.dumps(check,indent=2,ensure_ascii=False)+'\n')
 readme=(r1/'README.md').read_text().replace('review-5c13e5e1635f',c['review_id']).replace('2026-10-19-D6-01096ba333e3-R2-01','2026-10-19-D6-01096ba333e3-R2-02').replace('Five complete narrations are ready for his review.','Five revised narrations are ready for review in chat. The earlier batch was rejected for repetition and filler.')
 (r1/'README.md').write_text(readme)
 print(json.dumps({'status':c['status'],'review_id':c['review_id'],'scripts':len(scripts),'words':[len(x['text'].split()) for x in scripts],'exact_hook':True,'em_dashes':0,'queue_and_prior_audio':'unchanged'},ensure_ascii=False))
