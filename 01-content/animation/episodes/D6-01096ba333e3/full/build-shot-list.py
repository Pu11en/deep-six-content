"""Director step for D6-01096ba333e3: shots and beats keyed to word indices.
Writes shot-list.json with beat times copied from words.json, and refines caption groups."""
import json
from pathlib import Path

here = Path(__file__).parent
words = json.loads((here / 'words.json').read_text())
W = words['words']

# Caption groups: one idea per strip, 1 to 4 words. The sign-off uses the outro's own top caption.
GROUPS = [
    [0, 1, 2, 3], [4, 5, 6, 7], [8, 9], [10, 11],
    [12, 13, 14], [15, 16, 17, 18], [19, 20, 21, 22],
    [23, 24, 25], [26, 27, 28], [29, 30, 31], [32, 33], [34, 35], [36, 37, 38],
    [39, 40, 41, 42], [43, 44], [45, 46, 47], [48, 49, 50], [51, 52], [53, 54, 55, 56], [57, 58],
    [59, 60], [61, 62], [63, 64], [65, 66, 67], [68, 69, 70, 71],
    [72, 73, 74], [75, 76], [77, 78, 79], [80, 81], [82, 83], [84, 85, 86], [87, 88, 89],
    [90, 91], [92, 93], [94, 95, 96], [97, 98, 99],
    [100, 101, 102], [103, 104], [105, 106], [107, 108, 109], [110, 111, 112], [113], [114, 115],
    [116, 117, 118], [119, 120], [121, 122, 123, 124], [125, 126], [127, 128, 129],
]
assert [i for g in GROUPS for i in g] == list(range(130)), 'every lesson word once, in order'

# (id, start word, set, visual, camera, [(word index, action)])
SHOTS = [
    ('H1', 0, 'macro floor', 'Close profile of the black ensign wasp walking across the cabinet floor, its small flag-shaped abdomen bobbing on a thin stalk.', 'Tracks the wasp, slow push.',
     [(0, 'Wasp mid-stride; a question mark pops above it.'), (1, 'Wasp stops; the flag-like abdomen flicks up.')]),
    ('H2', 3, 'macro floor', 'The wasp stands on top of a dark, ridged cockroach egg case.', 'Whip back from the wasp to show the case under it, then push in.',
     [(3, 'Pull back: the wasp is standing on an egg case.'), (4, 'Its abdomen tip bends down and presses on the case, wriggling.'), (6, 'A see-through circle opens on the case: one white egg pops inside.'), (7, 'The circle widens to show the egg inside among the rows of cockroach eggs.')]),
    ('H3', 8, 'macro floor', 'Paper slide to a big American cockroach (reddish brown, pale-rimmed shield, long wings and antennae) with its egg case at the tip of its abdomen.', 'Wide, then push to the egg case.',
     [(9, 'Cockroach slides in, walking, antennae sweeping.'), (10, 'Camera pushes to the egg case at its tail; lime ring.')]),
    ('H4', 11, 'macro floor', 'The egg case sits on the floor; a question mark beside it.', 'Slow push in on the case.',
     [(11, 'The case drops to the floor with a bounce; a question mark pops.')]),
    ('A1', 12, 'macro floor', 'Scale: the tiny wasp next to the egg case and the huge cockroach.', 'Starts tight on the wasp, fast pull back to the wide comparison.',
     [(13, 'Fast pull back: the wasp is tiny beside the roach.'), (14, 'Lime ring pops round the small wasp; its abdomen bobs.')]),
    ('A2', 15, 'macro floor', 'Portrait of the wasp; a purple paper pennant on a pole appears beside its abdomen and waves with it.', 'Medium, drifting to the abdomen.',
     [(15, 'Cut to the wasp portrait, antennae waving.'), (17, 'Ensign (flag) pennant pops up beside the abdomen; both wave together. Symbol for the name.'), (18, 'Pennant flips away; the abdomen bobs up and down twice.')]),
    ('A3', 19, 'macro floor', 'The wasp braces on the egg case and presses its abdomen tip into the case wall.', 'Medium on the case, push in.',
     [(19, 'Wasp presses its abdomen tip to the case, wriggling.'), (20, 'See-through circle: ONE white egg slides in; lime ring.'), (21, 'The egg glints.'), (22, 'Circle widens: the egg is inside, among cockroach eggs; the wasp walks off.')]),
    ('B1', 23, 'case cutaway', 'Inside the opened case: two rows of pale cockroach eggs and the wasp egg on top.', 'Tight on the wasp egg.',
     [(23, 'The wasp egg wobbles.'), (25, 'It splits; a tiny pale larva wriggles out.')]),
    ('B2', 26, 'case cutaway', 'The young larva close up: pale, legless, segmented, with small jaws.', 'Push in on the larva.',
     [(27, 'Larva wriggles, jaws working.'), (28, 'Lime ring round the young wasp.')]),
    ('B3', 29, 'case cutaway', 'The whole cutaway: a dozen or more cockroach eggs around the larva.', 'Pull back to the whole case.',
     [(29, 'Pull back to the whole case.'), (31, 'Eggs light up one by one, twelve of them.'), (32, 'More light up: the back row too.')]),
    ('B4', 34, 'case cutaway', 'The rows of cockroach eggs; the larva turns to the nearest egg.', 'Pans along the egg row, then to the larva.',
     [(34, 'Pan along the row of cockroach eggs.'), (35, 'All the eggs bounce.'), (37, 'Larva turns to the nearest egg and opens its jaws.'), (38, 'Chomp.')]),
    ('C1', 39, 'case cutaway', 'The larva crawls across the tops of the eggs.', 'Tracks the larva, close.',
     [(40, 'Larva wriggles forward.'), (42, 'It lifts its head toward us.')]),
    ('C2', 43, 'jaw close-up', 'Head-on close-up: two sharply pointed, sickle-shaped jaws.', 'Close, slight push.',
     [(43, 'Jaws snap open; the sharp points glint.'), (44, 'Jaws snap shut and open: a chomp with a small shake.'), (45, 'Camera slides toward one jaw.')]),
    ('C3', 46, 'jaw close-up', 'The inner edge of the jaw, lined with a row of small teeth.', 'Tight on the jaw edge.',
     [(46, 'Tight on the jaw edge.'), (47, 'The row of small teeth pops up one by one; a lime line runs along them.'), (48, 'Jaws open wide.')]),
    ('C4', 49, 'case cutaway', 'The larva bites into one cockroach egg.', 'Tight on one egg.',
     [(49, 'Jaws close on the egg shell: a cut appears.'), (50, 'The cut runs through the shell.'), (52, 'The shell collapses, empty.')]),
    ('C5', 55, 'case cutaway', 'Egg after egg around the larva is emptied.', 'Hops egg to egg, then pulls back.',
     [(55, 'Hop to the next egg: it is cut and collapses.'), (56, 'Another egg collapses.'), (57, 'Pull back: eggs around the larva empty one after another.'), (58, 'The larva wriggles in the middle.')]),
    ('D1', 59, 'case cutaway', 'The larva feeds and grows inside the case.', 'Medium on the larva.',
     [(60, 'Fast chomping; nearby eggs empty.'), (62, 'The larva swells, growing until it nearly fills the case.')]),
    ('D2', 63, 'case cutaway', 'The larva becomes a pale pupa with the adult wasp shape, legs and wings folded, no cocoon; then a black adult.', 'Close, slow push.',
     [(64, 'Squash-flip: the larva turns into a pale pupa.'), (65, 'The pupa starts to darken.'), (67, 'Pop: a black adult wasp, folded inside.')]),
    ('D3', 68, 'case cutaway', 'Pull back: the adult lies inside the same egg case, which closes up.', 'Pull back to the whole case.',
     [(68, 'Pull back: the adult inside the case.'), (70, 'The cut-open side folds shut: the same case.'), (71, 'Lime ring round the case.')]),
    ('E1', 72, 'case cutaway', 'Inside view of the adult; it stirs and its legs and antennae unfold.', 'Close.',
     [(72, 'The adult inside the case.'), (74, 'It stirs; legs and antennae unfold.'), (76, 'A shine sweeps across it: the change is complete.')]),
    ('E2', 77, 'macro floor', 'Outside of the case, close on one end of a long side.', 'Close on the hole spot.',
     [(78, 'The case trembles.'), (79, 'A chewed line starts round a small circle, crumbs flicking off.')]),
    ('E3', 80, 'macro floor', 'The chewed circle near the end of the case completes and pops out.', 'Tighter on the circle.',
     [(81, 'A small lime ring marks how small the circle is.'), (82, 'The chewed line closes into a round circle.'), (83, 'The disc pops out: a small round hole.')]),
    ('E4', 84, 'macro floor', 'The adult wasp pushes out through the hole and climbs out.', 'Pulls back as it emerges.',
     [(84, 'Head and antennae poke through the hole.'), (86, 'Pull back: the case with the wasp coming out.'), (88, 'The wasp pulls free and climbs down.'), (89, 'Outside, it lifts its flag-like abdomen and flicks its wings.')]),
    ('F1', 90, 'floor from above', 'Looking down: an American cockroach scurries across the cabinet floor.', 'Top view; punch in on the pronotum.',
     [(90, 'Cockroach scurries in from the corner.'), (91, 'Punch in: the pale-rimmed shield behind its head.')]),
    ('F2', 92, 'floor from above', 'The egg case at the tip of its abdomen is left on the floor.', 'Pans down the body to the tail.',
     [(92, 'Pan to the tail: its egg case.'), (93, 'The case is left on the floor; the roach scurries off.')]),
    ('F3', 94, 'macro floor', 'Side view: the egg case on the floor; the wasp walks up to it.', 'Medium on the case.',
     [(94, 'Cut: the case on the floor; the wasp walks in.'), (95, 'Lime ring round the case.'), (98, 'The wasp taps the case with its antennae; its abdomen bobs.')]),
    ('F4', 99, 'macro floor', 'A lime target snaps onto the egg case.', 'Push in.',
     [(99, 'Lime target snaps onto the case.')]),
    ('G1', 100, 'under the sink', 'Wide: the cabinet under a kitchen sink, with pipes, a crack in the floor and a gap under the back wall. Roaches move along the floor.', 'Wide, slow drift.',
     [(100, 'A roach scurries in along the floor.'), (101, 'A second roach peeks from the gap.'), (102, 'The first roach stops; an egg case shows at its tail.')]),
    ('G2', 104, 'under the sink', 'Close on the crack in the cabinet floor.', 'Push in to the crack.',
     [(104, 'The egg case is left at the crack and slides in.'), (106, 'Lime line traces the crack.')]),
    ('G3', 107, 'under the sink', 'The small gaps: under the back wall and around the drain pipe.', 'Whip right to the gaps.',
     [(107, 'Whip to the back wall.'), (108, 'An egg case sits in the gap under the wall.'), (109, 'Lime traces the gap; a lime ring circles the gap round the pipe.')]),
    ('G4', 110, 'under the sink', 'The hot-water line under the sink.', 'Move to the warm line.',
     [(112, 'A roach crawls toward the warm line, antennae waving.'), (113, 'Warm glow and heat ripples rise from the line.')]),
    ('G5', 114, 'under the sink', 'The dripping drain trap and the damp floor.', 'To the trap, then pull back wide.',
     [(114, 'Drops fall from the trap; a damp patch spreads.'), (115, 'Pull back: the warm, damp spot under the sink, roaches near it; a lime ring circles it.')]),
    ('I1', 116, 'under the sink', 'The cabinet goes dim; a hand shines a flashlight in.', 'Wide.',
     [(116, 'The cabinet dims.'), (118, 'A hand with a flashlight slides in; the beam clicks on.'), (119, 'The beam swings to the crack.'), (120, 'The beam sweeps the gap and the damp corner.')]),
    ('I2', 121, 'under the sink', 'The beam finds the egg cases.', 'Push toward the crack.',
     [(121, 'The beam settles on the crack.'), (123, 'The egg case in the crack glints.'), (124, 'Lime rings on the egg cases.')]),
    ('I3', 125, 'under the sink', 'The beam finds a live roach at the gap.', 'Push toward the gap.',
     [(125, 'The beam swings toward the gap.'), (128, 'A live roach steps out into the light, antennae waving.'), (129, 'Lime ring round the roach; it freezes.')]),
]
LESSON_END = 1324 / 30  # first outro frame; last lesson word ends at 44.13 s

shots = []
for i, (sid, w0, place, visual, camera, beats) in enumerate(SHOTS):
    start = W[w0]['start'] if i else 0.0
    end = W[SHOTS[i + 1][1]]['start'] if i + 1 < len(SHOTS) else LESSON_END
    w1 = SHOTS[i + 1][1] if i + 1 < len(SHOTS) else 130
    shots.append({
        'id': sid, 'start': round(start, 3), 'end': round(end, 3), 'set': place,
        'words': ' '.join(w['text'] for w in W[w0:w1]),
        'visual': visual, 'camera': camera,
        'beats': [{'word': W[b]['text'], 'word_index': b, 'at': W[b]['start'], 'action': a} for b, a in beats],
    })
shots.append({
    'id': 'O1', 'start': round(LESSON_END, 3), 'end': 1472 / 30, 'set': 'approved outro',
    'words': 'Helping you understand pests. Deep Six Pest Control.',
    'visual': 'Approved Deep Six outro animation (outro-animation-v2.mp4) with its cream-paper wipe over the last teaching picture. Only opening scan time is shortened; jump, swing and reveal run at designed speed. Logo lands before "Deep". Top caption for the first sentence, as in the approved outro.',
    'camera': 'As supplied.',
    'beats': [{'word': W[130]['text'], 'word_index': 130, 'at': W[130]['start'], 'action': 'Top caption; the mascot scans.'},
              {'word': W[134]['text'], 'word_index': 134, 'at': W[134]['start'], 'action': 'Logo already landed and readable.'}],
})
plan = {
    'episode_id': 'D6-01096ba333e3', 'segment': 'full', 'author': 'Opus 5.5 (Claude Code), max effort',
    'pacing_rules': {'max_shot_seconds': 2.0, 'new_visual_action_every_seconds': 0.5},
    'science_guardrails': [
        'Ensign wasp: all black, small, flag-like flattened abdomen on a thin stalk set high on the thorax, long hind legs, clear wings; does not sting people.',
        'One white wasp egg per egg case; the larva feeds on the cockroach eggs inside; first-instar jaws sharply pointed with a row of small teeth.',
        'Pupa inside the case with no cocoon; the adult cuts a small round jagged hole near one end of a long side.',
        'American cockroach: reddish brown, pale-yellow band round the pronotum edge, long wings, long antennae, spiny legs. Egg case purse-shaped, dark, ridged seam, 16 eggs in two rows.',
        'Only the American cockroach is shown as a host; no claim about every species.',
        'No treatment advice: no sprays, baits or traps. The flashlight is inspection only.',
        'A wasp sighting is not shown as proof of an infestation.',
        'No on-screen text other than captions.',
    ],
    'shots': shots,
}
(here / 'shot-list.json').write_text(json.dumps(plan, indent=2) + '\n')
orig = here / 'words.aligned-groups.json'
if not orig.exists():
    orig.write_text(json.dumps({'caption_groups': words['caption_groups']}, indent=1) + '\n')
words['caption_groups'] = [{'words': g} for g in GROUPS]
(here / 'words.json').write_text(json.dumps(words, indent=1, ensure_ascii=False) + '\n')
lens = [s['end'] - s['start'] for s in shots[:-1]]
print(json.dumps({'shots': len(shots), 'beats': sum(len(s['beats']) for s in shots), 'longest_shot': round(max(lens), 2),
                  'longest_id': shots[lens.index(max(lens))]['id'], 'groups': len(GROUPS)}))
