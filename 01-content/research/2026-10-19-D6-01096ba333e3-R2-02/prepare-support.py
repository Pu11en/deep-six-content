import json,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0,str(Path('tools').resolve()))
from d6_sources import fetch_page,normalized
P=Path(__file__).resolve().parent
S=json.loads((P/'live-job.json').read_text())['state']
D=json.loads(Path('01-content/harness/config.json').read_text())['support_domains']
def fact(statement,quote):return {'statement':statement,'quote':quote}
cards=[
{'url':'https://ask.ifas.ufl.edu/publication/IN319','title':'A Cockroach Egg Parasitoid, Evania appendigaster (Linnaeus) (Hymenoptera: Evaniidae)','publisher':'University of Florida IFAS Extension','date':'undated','lesson':'The female has to penetrate a tough egg case; the young wasp then develops inside and the adult cuts an exit hole. These details explain what happens to one egg case.','species':'Evania appendigaster; documented hosts include American, Oriental and Australian cockroaches','region':'Florida university profile; reports this wasp is common in much of the southern United States','limits':'Older biological observations summarized by an extension profile, not a new Texas field trial. Timing is described as usual, not an invariant rule. The larva cuts individual egg shells; the mother penetrates the outer egg case. No whole-home control rate or release recommendation is supported here. Foreign historical control rates and speculation are excluded. An exit hole is not a standalone diagnostic test.','facts':[
 fact('The female braces herself against a cockroach egg case, penetrates its tough covering with her egg-laying organ and lays one egg. The profile says inserting the organ usually takes 15 to 30 minutes.','15 to 30 minutes'),
 fact('The earliest larval stage has pointed jaws bearing small teeth that cut through the shells of individual cockroach eggs. Later larval stages have differently shaped jaws.','cut through the tough shell'),
 fact('The wasp pupates inside the cockroach egg case without a cocoon. The mature adult cuts a small round, jagged exit hole near the end of a long side of the case.','small round jagged hole'),
 fact('The profile names Oriental, American and Australian cockroaches as hosts of Evania appendigaster and describes it as common in much of the southern United States. It does not name German cockroaches as hosts.','common in much of the southern US')
]},
{'url':'https://extension.umn.edu/garden-and-home/home-maintenance/household-insects/cockroaches','title':'Cockroaches','publisher':'University of Minnesota Extension','date':'Reviewed 2024','lesson':'Cockroach species differ in egg-case handling. Inspection should account for deposited egg cases, transported belongings and the food, moisture and hiding places that support activity.','species':'American and German cockroaches for egg-case facts; household cockroaches for general inspection guidance','region':'Minnesota extension publication; use species biology and general indoor inspection, not regional prevalence or cold-weather management, for Texas','limits':'Do not claim German cockroaches are hosts of this ensign wasp. Species prevalence, winter treatments and outdoor survival in Minnesota are not transferred to Texas. No pesticide or health guidance is used. Egg cases differ by species; do not present one size or shape as universal.','facts':[
 fact('American cockroaches favor warm, moist places. Females deposit their egg cases in cracks or crevices.','deposited in a crack or crevice'),
 fact('Female German cockroaches carry their egg cases until the eggs are ready to hatch, unlike the deposited cases described for American cockroaches.','until the eggs are ready to hatch'),
 fact('Inspect bags, boxes and luggage brought indoors for cockroaches and their egg capsules. Corrugated cardboard can harbor them; removing boxes and other unnecessary clutter reduces hiding places.','Examine bags, boxes and luggage'),
 fact('Indoor cockroach prevention includes restricting food and water, repairing leaks, drying damp places and sealing cracks where roaches hide. These steps reduce resources and shelter available to them.','leaky water pipes or faucets')
]},
{'url':'https://citybugs.tamu.edu/factsheets/ipm/what-is-a-sticky-trap/','title':'What is a sticky trap?','publisher':'Texas A&M AgriLife Extension Service, Insects in the City','date':'undated','lesson':'Sticky insect traps reveal where and when crawling pests are active. Placement against edges and comparison among locations make them useful inspection tools.','species':'Cockroaches and other crawling insect pests','region':'Texas university extension guidance for buildings','limits':'Use light-duty insect monitoring cards. No rodent trapping or pesticide recommendations. Traps detect activity and changes; they are not presented as a complete control method. A wasp sighting alone does not establish an active cockroach infestation.','facts':[
 fact('Most crawling pests travel in dark areas and along edges. Place sticky insect cards directly against a wall, with open ends running parallel to it so insects can enter along that route.','travel in dark areas and along edges'),
 fact('Suggested cockroach trap sites include behind stoves and refrigerators, in cupboards and under sinks. Traps beside exterior doors or other entry points can monitor outdoor cockroaches coming in.','Behind stoves and refrigerators'),
 fact('Sticky traps detect pests when people are absent, including at night. Comparing multiple traps can help pinpoint activity and monitoring over time shows changes in abundance. Their main role is detection and monitoring, not standalone control.','detect pests, and monitor changes')
]}
]
def save(n,d):(P/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
checks=[]; actions=[]
def check(card):
 text,final=fetch_page(card['url'],D)
 source=next(s for s in S['sources'] if s['url']==card['url'])
 results=[{'quote':f['quote'],'crawler_match':f['quote'] in source['text'],'independent_match':normalized(f['quote']) in normalized(text)} for f in card['facts']]
 count=sum(len(f['quote'].split()) for f in card['facts'])
 assert count<=25 and all(x['crawler_match'] and x['independent_match'] for x in results), (card['url'],count,results)
 return {'url':card['url'],'final_url':final,'crawler_source_id':source['id'],'crawler_truncated':source['truncated'],'quote_words':count,'facts':results}
with ThreadPoolExecutor(max_workers=3) as pool: checks=list(pool.map(check,cards))
for card,check_result in zip(cards,checks):
 for f in card['facts']: actions.append({'tool':'evidence','source_id':check_result['crawler_source_id'],'claim':f['statement'],'quote':f['quote']})
save('result.json',{'cards':cards,'unresolved':[]});save('independent-check.json',checks);save('evidence-actions.json',actions)
save('scope-limits.json',{'failed_reads':[{'url':'https://ipm.ucanr.edu/home-and-landscape/cockroaches/','crawler_outcome':'redirect_limit','used_in_cards':False}], 'excluded_claims':['No household suppression percentage or guarantee.','No inference that egg-carrying behavior alone proves a species cannot be parasitized.','No claim that an ensign-wasp sighting proves or locates an active infestation.'], 'nonblocking_gaps':['The selected sources do not establish a local whole-home suppression rate. Scripts make no such claim.'], 'covered_required_scope':'Mechanism, species-specific egg-case handling, trap placement, incoming item inspection, moisture and shelter reduction.'})
print(json.dumps({'cards':len(cards),'supported_facts':len(actions),'quote_words':[x['quote_words'] for x in checks],'independent_checks':'passed'}))
