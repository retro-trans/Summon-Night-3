"""Prepare English UI targets, bound to current pointers/hashes; preview first."""
import argparse,json,struct,hashlib,textwrap,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from menu_hotfix_017 import lines_at
from inspect_categories_068 import collect,BASE
sha=lambda b:hashlib.sha256(b).hexdigest()
PROFILES={
1:"Nup's cute friend; reliable in a pinch.",
2:"An old, once widely mass-made model. Few remain.",
3:"Old but advanced. Many replicas; originals are rare.",
4:"Mass-made work bots, each with its own personality.",
5:"Fine welder: removable laser, EM shield vs. rockfalls.",
7:"Mass-made work bot; beam saw and swappable equipment.",
8:"Construction leader bot; commands even in zero G.",
9:"Demolition bot refit for war; ball hammer heats fast.",
10:"Huge medical bot; add-ons treat any illness.",
11:"Cheap, advanced bot with cartridge flamethrower.",
12:"Old wired bot: strong, short off-grid life; few made.",
13:"Newly launched top-tech bot with huge scissor blades.",
14:"Large Machine World war bot; prototype only.",
15:"Master Zel's Machine World work; merges for big hits.",
16:"Fabled bot, known only by name; said to ensure victory.",
17:"An artful transformation system; briefly warps space.",
18:'"12 million strength! Machine manganese! So strong!?"',
19:"Smiling, strong fire spirit; Belfrau's little brother.",
20:"Ninja dog trained from birth; understands human speech.",
21:"Mysterious life, said to be oni eggs; two-horn kind found.",
22:"Cucumber-loving yokai; lives by water but cannot swim.",
24:"Roaming yokai with vacuum blades; sometimes helps people.",
25:"One-eyed yokai: loves night scares, weak to sunlight.",
26:"Lucky yokai; angry if you peek inside the cloth bundle.",
27:"Young nine-tail fox borrows a priestess; loves festivals.",
28:"Huge, savage primeval oni in old texts; crushes boulders.",
29:"A sickness curse tool; intense malice gave it a soul.",
30:"Old, high-ranked ape yokai in human form; quite casual.",
31:"Ancient oni general aided humans; sword cleaves mountains.",
32:"Dark-world ninja clan; none have seen their forms.",
33:"Nature-bound Oni World dragon gods; control disasters.",
34:"Oni World guardians; six swords call mighty thunder.",
35:"Carefree, playful angel child; Alize's dear friend.",
36:"Very wise demon hermit with power over darkness.",
37:"Cute, very curious holy spirit attending angels.",
38:"Common angel-guard spirit; wields light in Spirit World.",
39:"Small apprentice angel; healing power is still weak.",
40:"Small holy fairy with healing power; not very strong.",
41:"Common, greedy Spirit World imp; excels at lightning.",
42:"A holy spirit in sheep form; brings peace of mind.",
43:"Merciful Spirit World holy mother; heals all equally.",
44:"Demon mage-warrior; ice cold enough to extinguish fire.",
45:"Dark army robs the living; abyssal aid for power seekers.",
46:"Mid-rank demon of silence and fear in Spirit World depths.",
47:"Light sage tasked to aid those who fight evil.",
48:"Great demon's corpse; emits foul miasma for centuries.",
49:"Dark angel judges sinners under white moon and red night.",
50:"Renowned sea pirate; long plagued the Imperial Navy.",
51:"Great undead king; mercilessly judges sin-laden souls.",
52:"Seven archangel souls in holy armor unite to fight demons.",
53:"Holy maiden commands holy armor; pure song cleanses evil.",
54:"Will's lively, clever friend; surprisingly dexterous.",
55:"Wise nocturnal bird uses herbs; sleepy in daylight.",
56:"Mint's loyal guard; reliable. Treasures helmet/goggles.",
57:"Feisty rascal; treasures its hat, even while asleep.",
58:"Cheery, cocky young beast; soft but proudly strong.",
59:"Forest nut spirit; repays those who cherish its forest.",
60:"Foul-breathed beast; close-knit families herd in swamps.",
61:"Shaman of an all-female aquatic tribe; likes gentle music.",
62:"Heavy, fanged beast; usually calm, wildly enraged.",
63:"Rare Maetropa beast; controls life, may read minds.",
64:"Flower fairy enslaves all with noble scent/mature beauty.",
65:"Flower fairy enslaves people; beauty/scent hard to resist.",
66:"Blazing fighting spirit; always brimming with energy.",
67:"Liquid life loves empty containers; many varieties exist.",
68:"Always runs busily; strange magic distorts sense of time.",
69:"Graceful silver wyvern; shares deep trust with Minis.",
70:"Huge, free-flying wyvern; lonely, may befriend people.",
71:"Odd life explodes if careless; surprisingly soft to touch.",
72:"Forced beast fusion; few dark summoners know how.",
73:"Fabled mountain guardian; rage raises storms, splits earth.",
74:"Beast king sealed in gold chains; fists split/ scorch all.",
75:"Paired legendary dragons; breath said to fell any foe.",
76:"Look out above! What might fall next?",
77:"A rock that's perfect as a stepping stone.",
78:"Ancient colossus's ruined fist; may make you feel strong.",
79:"Wooden garden-party table. Now taking party bookings!",
80:"Cart for carrying food. Not for carrying people!",
81:"School desk full of memories. Not for standing on!",
82:"Magic-repelling stone slab; oddly calming to stand on.",
83:"Masked statue in old ruins; eerie, unapproachable.",
85:"Weapon in order-cleaving darkness; inspires deep dread.",
86:"Crystal softens magic and ranged hits; feels powerful."
}
SUPPORT={
2:'Grants Cheer.',6:'Grants Charge.',11:'Gun cancels one enemy action.',12:'Needle stops one enemy counter.',13:'Warns of side/rear attacks.',14:'Spots weakness for a critical.',15:'Shuriken stops one enemy action.',16:'Grants DF UP possession.',17:'Nature inflicts ailment on foe.',18:'Sweet pollen puts one foe asleep.',19:'Nursing heals 50% of damage.',20:'Ranged follow-up shot.',21:'Ranged follow-up attack.',22:'Grants Charge or Cheer.',23:'Revives once per battle.',25:'Quake stops one enemy counter.',26:'Distracts to stop one foe action.',28:'Glance Charms one enemy.',33:'Evil eye Petrifies one enemy.',34:'Spear throw follow-up.',35:'Metral eye Paralyzes one enemy.',37:'Angel heals 50% of damage.',39:'Arrow stops one enemy action.',41:'Axe stops one enemy action.',43:'Summon stops one enemy counter.',44:'Glance inflicts ailment on foe.',45:'Bomb follow-up attack.',64:'Summon stops one enemy action.',69:'Talisman gives one foe ailment.',73:'Cures or inflicts an ailment.',74:'Item healing or Cheer.',76:'Revives for a fee.',78:'Glance Charms one enemy.',79:'Prayer restores all allies\' MP.',82:'Nature cures ailments/heals MP.',83:'Dismisses A-rank/lower summons.'
}
ACTIVE_NAMES={9:'Transform',10:'Transform',11:'Berserk Summon',13:'Sarutobi Art',18:'Teleport',23:'Swap Places',28:'Discharge',29:'Dragon Eye',30:'Evil Eye',31:'Metral Eye',32:'Crimson Eye',33:'Izuna Eye',34:'Alluring Gaze',35:'Healing Miracle',40:'Blessing Prayer',45:'Cheer',51:'Strla',54:'Recharge',59:'Harvest Blessing',61:'Love\'s Blessing',63:'Roar',64:'Shout',65:'Stealth',66:'Active Camo',67:'Exorcism',69:'Moonflower Smile',73:'Floral Arrow'}
ACTIVE_HELP={
9:'Switch dragon/human forms.',10:'Switch human/demon forms.',11:'Over-limit summon magic; may break the summon stone.',13:'Move regardless of height.',17:'Move regardless of height; range +1.',18:'Move regardless of height.',22:'Move regardless of height; range +1.',23:'Swap with one ally in range.',27:'Swap ally/foe in range; no leaders or unique units.',28:'Area shock Paralyzes; affects allies too.',29:'Inflicts Paralysis.',30:'Inflicts Paralysis.',31:'Inflicts Paralysis.',32:'Inflicts Petrify.',33:'Inflicts Petrify.',34:'Inflicts Charm.',35:'Heals HP and ailments; HP healed varies by level.',40:'Heals HP and ailments; HP healed varies by level.',45:'Heals HP; CR up; less physical/magic damage.',50:'Charge raises physical attack damage.',51:'Heals 40 HP.',52:'Heals 80 HP.',53:'Heals 120 HP.',54:'Machine resist >=25%: HP heal; <25%: Poison.',58:'Machine resist >=25%: HP/MP heal; <25%: Poison.',59:'Give own MP: level x50.',61:'Give own MP: level x50.',63:'Grants self Rage.',64:'All nearby face you; wakes sleeping units.',65:'No hits until action; moving OK. No ZOC while hidden.',66:'No hits until action; moving OK. No ZOC while hidden.',67:'Dispels possession.',69:'Lets an ally who has acted act again.',71:'Move 6 straight; gentle terrain: up/down 1.',72:'Move 7 straight; gentle terrain: up/down 2.',73:'Sweet scent causes Sleep; affects allies too.'}
ACTIVE_MASTER={13:'Master: move range +1',18:'Master: move range +1',23:'Master: foes, not leaders',54:'Master: also heals MP'}
PASSIVE_NAMES={2:'Cheer',6:'Courage Charge',10:'Victory Cry',11:'Warning Shot',12:'Numbing Needle',13:'Warning',14:'Analysis',15:'Shadow Pin',16:'Knight\'s Guard',17:'Nature Prayer',18:'Floralia',19:'First Aid',20:'EX Shot',21:'South Wind',22:'Encouragement',23:'Angel Light',24:'Insight',25:'Quake Fist',26:'Look!',28:'Dragon Allure',33:'Izuna Eye',34:'Spear Throw',35:'Metral Eye',37:'Quick Heal',40:'Spot Weakness',42:'Baristrla',43:'Sharp Retort',44:'Allure',45:'Special Bomb',46:'Rally',47:'Range Up',48:'Height Range Up',49:'MP Cost Down',50:'Power Up',51:'Ailment Rate Up',52:'Possess Turns Up',53:'Machine Rank Up',54:'Oni Rank Up',55:'Spirit Rank Up',56:'Beast Rank Up',61:'Dragon Cheer',62:'Pretty Cheer',63:'Brilliant Cheer',66:'Look Out Above',67:'Alarm',69:'Talisman Bind',71:'Extra Bomb',73:'Shamisen Show',74:'Rear Support',75:'See Weakness',76:'Elixir Sales',79:'Moonflower Pray',80:'Thunderous Cry',81:'Cyber Support',82:'Warrior\'s Rest',83:'Dismissal',87:'Revive',88:'Cursed Blood',89:'Bracelet Guard',90:'Resonant Awaken',95:'Summon Level Up',98:'Dismiss Units',180:'Adversity',185:'Last-Ditch Power',195:'Front Attack',200:'Back Attack',208:'Valor',209:'Mind\'s Eye',211:'Counter Seal',216:'Gun Range Up',218:'Sharpshoot',219:'Soft Body',221:'Astral Body',223:'Hard Body',225:'Ghost Body',227:'Shell Body',229:'Anti-Magic Field',234:'Ailment Resist',239:'Special Body',240:'Possess Immune',241:'Sleep Attack',246:'Seal Attack',251:'Blind Attack',256:'Poison Attack',261:'Rage Attack',266:'Charm Attack',271:'Paralyze Attack',276:'Petrify Attack',281:'Spirit Attack',282:'HP Drain Attack',287:'MP Drain Attack',292:'Teleport',293:'Float',297:'Regeneration',302:'Cursed Pulse',307:'Crimson Pulse',310:'Spirit Horn Heal',313:'Super Regen',316:'Utsusemi Art',317:'Static Camo',318:'Healing Wine',321:'Petrify Immune',322:'Paralyze Immune',323:'Poison Immune',324:'Blind Immune',325:'Charm Immune',326:'Rage Immune',327:'Sleep Immune',328:'Seal Immune',329:'Stone/Para/Charm',330:'Core Magic',331:'Hopeless Dream',332:'Warped Tombstone',333:'Lost Truth Shade',334:'Shattered Time',336:'Summon Insurance',341:'Expert Summoning',346:'Summon Fan',351:'Moonflower Hug',352:'Moonflower Boon',353:'Petrify Odds Half',354:'Paralyze Half',355:'Poison Odds Half',356:'Blind Odds Half',357:'Charm Odds Half',358:'Rage Odds Half',359:'Sleep Odds Half',360:'Seal Odds Half',361:'Ailment Odds Half'}
PASSIVE_HELP={
0:'Find ingredients nearby. At own turn start.',2:'Lively shouts grant Cheer. At own turn start.',6:'Heartfelt pep talk: Charge. At own turn start.',10:'Brave victory cry: Charge. At own turn start.',11:'Gun stops one foe action. When enemy acts.',12:'Needle stops foe counter. When enemy counters.',13:'Warn of side/rear attacks. When enemy attacks.',14:'Find weakness: always CR. When ally attacks.',15:'Shuriken stops foe action. When enemy acts.',16:'Possess to grant DF UP. At own turn start.',17:'Nature gives foe ailment. When turns switch.',18:'Sweet pollen Sleeps a foe. When turns switch.',19:'Nursing heals HP/ailments. On damage or ailment.',20:'Ranged cannon follow-up. When ally attacks.',21:'Ranged wind follow-up. When ally attacks.',22:'Cheer or Charge by shouts. At own turn start.',23:'Angel revives fallen ally. When ally is KO\'d.',25:'Quake stops foe counter. When enemy counters.',26:'Distract: stop foe action. When enemy acts.',28:'Alluring glance Charms foe. When turns switch.',33:'Izuna eye Petrifies a foe. When turns switch.',34:'Spear throw follow-up. When ally attacks.',35:'Metral eye Paralyzes foe. When turns switch.',37:'Angel heals HP/ailments. On damage or ailment.',39:'Arrow stops one foe action. When enemy acts.',41:'Axe stops one foe action. When enemy acts.',42:'Strla revives fallen ally. When ally is KO\'d.',43:'Null summon stops counter. When enemy counters.',44:'Glance gives foe ailment. When turns switch.',45:'Bomb follow-up attack. When ally attacks.',46:'Rally gives all foes Cheer.',47:'Assist: summon range +1.',48:'Assist: height range +1.',49:'Assist: summon MP cost -10%.',50:'Assist: summon power +5.',51:'Assist: ailment rate +20%.',52:'Assist: possession lasts +2 turns.',53:'Assist: Machine rank +1.',54:'Assist: Oni rank +1.',55:'Assist: Spirit rank +1.',56:'Assist: Beast rank +1.',59:'Find ingredients nearby. When turns switch.',64:'Null summon stops action. When enemy acts.',66:'Summon pot stops counter. When enemy counters.',69:'Magic talisman: foe ailment. When turns switch.',73:'Shamisen cures; song harms a foe. When turns switch.',74:'Items heal HP or grant Cheer. When turns switch.',76:'Paid elixir revives ally. When ally is KO\'d.',78:'Glance Charms, may fail. When turns switch.',79:'Prayer heals all allies\' MP. At own turn start.',81:'Battle program: all foes Cheer.',82:'Nature cures/heals MP. When turns switch.',83:'Dismiss A/lower summons; not units already summoned.',85:'C/lower magic null within 3 tiles of Gian.',86:'B/lower magic null within 3 tiles of Gian.',87:'Revive from 0 HP once per battle.',88:'Immune to all ailments.',89:'Father\'s bracelet: strange power; cannot remove it.',90:'Bracelet unsealed: Resonant power, high Beast resist.',91:'Call unit summons; higher levels allow more units.',95:'Summoned unit level rises by skill level.',98:'Dismiss own summon units within 4 tiles of Gian.',99:'Dismiss own summon units within 6 tiles of Gian.',178:'ZOC:M; off if Petrif/Para/Charm/Sleep',179:'ZOC:L; off if Petrif/Para/Charm/Sleep',180:'CR up vs. higher-level foe; level gap cap: 4.',184:'CR up vs. higher-level foe; gap <=4; less damage vs. them.',185:'Deal more damage when HP falls below set proportion.',194:'No near-death penalty.',195:'Front damage +5%/level. No effect when countering.',199:'Front damage +5%/level; no counter effect; less countered.',200:'Rear damage +4%/level.',204:'Rear damage +4%/level; less likely to be countered.',205:'Give up move: two normal attacks, no MP cost.',206:'Give up attack: move twice.',207:'Give up move/attack: use items twice.',208:'Move while ignoring ZOC.',209:'Halve damage modifier from facing.',210:'No damage modifier from facing.',211:'May prevent enemy counter when attacking.',215:'Enemy cannot counter your attacks.',216:'Gun range +skill level.',218:'Thrown weapons/guns ignore obstacles.',219:'Physical damage taken -25%/level.',229:'Magic damage -10%/level field on adjacent tiles and self.',234:'Ailment immunity 20%/level; except Charge/Cheer.',238:'All ailments blocked; except Charge/Cheer.',239:'Machine: ailment immune; Charge/Cheer work.',240:'All possession effects null.',241:'Physical hits may cause Sleep.',246:'Physical hits may cause Summon Seal.',251:'Physical hits may cause Blind.',256:'Physical hits may cause Poison.',261:'Physical hits may cause Rage.',266:'Physical hits may cause Charm.',271:'Physical hits may cause Paralysis.',276:'Physical hits may cause Petrify.',281:'Physical damage becomes MP damage.',282:'Physical damage x8%/level absorbed as HP.',287:'Physical damage x8%/level absorbed as MP.',292:'Move ignores all obstacles and height in range.',293:'Cross unwalkable tiles; cannot stop on them.',296:'Item range +skill level; adds Sharpshoot.',297:'Heal HP 4%/level each own turn.',307:'Heal HP/MP 10%/level each own turn.',316:'Avoid lethal damage once per battle.',318:'Drink wine: heals HP but always causes Sleep.',320:'Drink wine: heals HP without Sleep.',321:'Cannot be Petrified.',322:'Cannot be Paralyzed.',323:'Cannot be Poisoned.',324:'Cannot be Blinded.',325:'Cannot be Charmed.',326:'Cannot be Enraged.',327:'Cannot fall Asleep.',328:'Cannot be Summon Sealed.',329:'Immune: Petrify/Paralysis/Charm.',330:'Immune to damage until specific units fall.',331:'Regain MP every turn.',332:'Devour beasts to heal HP based on their remaining HP.',333:'Summons magical beasts.',334:'Dismiss own summon units and all ally/foe possessions.',335:'Nullifies C/lower summons targeting Fallen Dragon.',336:'Own summons deal allies -20% damage per skill level.',340:'Allies in your attack summon area are excluded.',341:'Raises summon spell power limit.',346:'Favorite summon count +skill level.',349:'Nullifies C/lower summons targeting Gian.',350:'Nullifies B/lower summons targeting Gian.',351:'Adjacent allies heal MP 3% at own turn start; not self.',352:'Adjacent allies get Charge/Cheer at turn start; not self.',353:'Halves Petrify chance.',354:'Halves Paralysis chance.',355:'Halves Poison chance.',356:'Halves Blind chance.',357:'Halves Charm chance.',358:'Halves Rage chance.',359:'Halves Sleep chance.',360:'Halves Summon Seal chance.',361:'Halves all ailment chances.'}
PASSIVE_MASTER={180:'Master: less damage vs. higher-level foes.',195:'Master: less countered',318:'Master: no Sleep'}
SHARED_HELP={0:'Equippable summon stones +skill level.',91:'Max HP +10/level.',96:'Max MP +10/level.',101:'AT +3/level.',106:'DF +2/level.',111:'MAT +3/level.',116:'MDF +2/level.',121:'TEC +3/level.',126:'LUC +5/level.',131:'STEP +1.',134:'Machine resist +3/level.',139:'Oni resist +3/level.',144:'Spirit resist +3/level.',149:'Beast resist +3/level.'}
SHARED_MASTER={26:'Master: rare CR instant KO',31:'Master: foe counters down',41:'Master: foe counters down',51:'Master: evade +15%',56:'Master: pierce 2 tiles',61:'Master: evade+15% counter+10%',66:'Master: weapon ailment rate up',71:'Master: hit height +/-1',76:'Master: Sharpshoot',81:'Master: range penalty halved',86:'Master: Sharpshoot'}
# Review changes retain mechanics and source relationships while fitting two rows.
PROFILES.update({2:'Old, once mass-made model. Few now remain.',3:'Old but advanced. Many replicas; originals rare.',18:'"12M strength! Machine manganese! Very strong!?"',19:"Smiling, strong fire spirit; Belfraw's little brother.",21:'Odd life, said to be oni eggs; two-horn kind found.',24:'Roams with vacuum blades; sometimes helps people.',27:'Young nine-tail fox in priestess; loves festivals.',28:'Huge ancient savage oni in books; crushes boulders.',31:'Old oni general aided humans; blade splits mountains.',35:"Carefree, playful angel child; Alieze's dear friend.",39:'Tiny apprentice angel; healing power still weak.',45:'Dark army robs all life; abyss aids power seekers.',46:'Mid-rank fear/silence demon in Spirit World depths.',49:'Dark angel judges sin by white moon and red night.',52:'7 archangel souls in holy armor unite vs. demons.',53:'Holy maiden rules holy armor; pure song cleanses.',61:'Shaman: women-only water tribe; likes gentle music.',64:'Enslaving flower fairy: noble scent, mature beauty.',65:'Enslaving flower fairy; scent/beauty hard to resist.',67:'Liquid life in empty containers; many kinds exist.',68:'Runs busily; strange magic distorts sense of time.',71:'Careless: it explodes! Oddly soft to touch.',73:'Remote mountain guardian; rage storms/splits earth.',74:'King in gold chains; fists split earth, scorch sky.',78:'Ruined old colossus fist; may make you feel strong.'})
SUPPORT.update({18:'Sweet pollen puts a foe asleep.',26:'Distracts: stops one foe action.'})
PROFILES.update({
5:'Welder: detachable laser; EM shield vs. falling rocks.',
7:'Work bot: beam saw, gear swapped to suit the job.',
9:'Demolition bot refit for war; hot ball hammer.',
12:'Old wired bot: strong, brief unplugged life; few made.',
16:'Fabled bot in name only; said to ensure victory.',
17:'Artful shape-shifting; briefly distorts space.',
19:"Strong, smiling fire spirit; Belfraw's little brother.",
20:'Ninja dog trained at birth; knows human speech.',
22:'Cucumber-loving water yokai; strangely cannot swim.',
26:'Lucky yokai; gets angry if you peek in its bundle.',
29:'Curse tool causes illness; malice gave it a soul.',
30:'Old ape yokai in human form; high rank, casual.',
31:'Oni ally vs. evil oni; blade said to split mountains.',
33:'Oni World dragon gods rule nature and disasters.',
35:"Playful, carefree angel; Alieze's dear friend.",
38:'Spirit World angel guard; common, wields light.',
40:'Tiny holy fairy; weak but has healing power.',
44:'Demon spell-warrior; ice can put out flames.',
51:'Great undead king; harsh judge of sin-laden souls.',
54:"Will's lively, smart friend; deft with its hands.",
56:"Mint's kind, reliable guard; loves helmet/goggles.",
59:'Tiny forest nut spirit; repays forest protectors.',
60:'Bad-breath beast; swamps, close-knit family herds.',
62:'Huge fanged beast; calm till enraged, then wild.',
63:'Rare Maetropa life-wielder; said to read minds.',
65:'Flower fairy enslaves; scent/beauty hard to resist.',
66:'Hot fighting spirit; always brimming with energy.',
67:'Liquid life in empty jars; many kinds found.',
69:'Elegant silver wyvern; Minis deeply trusts it.',
70:'Huge wyvern flies freely; lonely, may befriend humans.',
75:'Paired fabled dragons; breath said to fell any foe.',
81:'Desk full of school memories. Do not stand on it!',
85:'Order-cleaving dark weapon; its very being terrifies.',
86:'Crystal: magic/ranged hits weakened; feels strong.'
})
PASSIVE_NAMES.update({353:'Petrify Half',361:'Ailment Half'})
PASSIVE_HELP.update({184:'CR up vs. higher Lv; gap<=4; less damage from them.',199:'Front hit +5%/Lv; not counters; fewer foe counters.',229:'Adjacent/self field: magic damage -10% per level.',352:'Near allies: Charge/Cheer at own turn start; not self.'})
ACTIVE_HELP[54]='Machine res>=25%: heal HP; else Poison.'
ACTIVE_MASTER[54]='Master: MP too'
PASSIVE_HELP.update({43:'Neutral summon stops counter. When enemy counters.',64:'Neutral summon stops action. When enemy acts.',73:'Cures ailments; song inflicts them. Turn switch.',98:'Dismiss allied summon units within 4 tiles of Gian.',99:'Dismiss allied summon units within 6 tiles of Gian.',334:'Dismiss allied summons and all ally/foe possessions.',184:'CR up vs higher Lv; gap cap 4. Less damage from them.',180:'Higher-Lv foe: CR up(cap4).',195:'Front dmg+5%/Lv; not on counter.',318:'Wine heals HP; causes Sleep.',352:'Adjacent allies: Charge/Cheer at turn start; not self.'})
PASSIVE_MASTER.update({180:'Master: less damage taken',195:'Master: fewer counters'})
PROFILES.update({5:'Welder: detachable laser; EM barrier vs. rockfalls.',12:'Old, strong wired bot; brief off-grid life, few made.',19:"Smiling strong fire spirit; Belfraw's little brother.",22:'Water yokai loves cucumber; oddly cannot swim.',31:'Oni aided humans vs. evil; blade said to split mts.',54:"Will's lively clever pal; surprisingly deft.",56:"Mint's kind, trusty guard; loves its helmet/goggles.",65:'Flower fairy enslaves you; scent/beauty irresistible.',70:'Huge free-flying wyvern; lonely; may befriend humans.',75:'Paired legendary dragons; breath can fell any foe.',81:'School desk of memories. No standing on it!'})
PROFILES.update({12:'Strong old wired bot; brief off-grid life, few built.',19:"Smiling, strong fire spirit Belfraw's junior pal.",45:'Dark army robs the living; comes to power seekers.',53:'Holy angel maiden; rules armor, cleanses with song.',74:'Once gold-chained beast king Fists split earth/scorch sky',78:'Old colossus fist; standing on it feels empowering.',15:"Zel's Machine World bot; morphs/merges for big hits.",73:'Mountain guard; rage brings storms, splits earth.',70:'Huge free-flying wyvern; lonely, may befriend humans.'})
PROFILES.update({70:'Huge free-flying wyvern; lonely, befriends people.',74:'King once in gold chains; fists split earth/burn sky.'})
ACTIVE_NAMES[51]='Stora'
PASSIVE_NAMES[42]='Baristora'
ACTIVE_HELP.update({35:'Heals HP/ailments by level.',40:'Heals HP/ailments by level.'})
PASSIVE_HELP.update({91:'Unit summons; higher Lv allows more.',185:'Low HP raises attack damage.',282:'Physical dmg x8%/Lv heals HP.',336:'Summons hurt allies -20%/Lv.'})
# Already-English help must also fit when its newly translated mastery row is
# displayed. Bind these edits to current English pointers as well.
EXTRA_HELP={102:'Counter: counter dmg +5%/Lv.',107:'Cntr: phys. in range 20%/Lv first; no special.',112:'Counter: blocks normal attacks 7%/Lv.',117:'Guard: dmg reduction +5%/Lv.',122:'Guard: evade shots +5%/Lv.',127:'Guard: evade direct hits +5%/Lv.',137:'Summon dmg may hit MP; phys. dmg as Guard.',147:'Guard: phys. dmg reduction +10%/Lv.',157:'Cntr: draws attacks; dmg as Counter.',167:'Null normal phys.: 7%/Lv; else Guard dmg.',172:'Reflect 1/2 shot dmg; other phys.: Guard.'}
ACTIVE_NAMES.update({11:'Berserk Sum.',35:'Heal Miracle',40:'Bless Prayer',59:'Harvest Gift',61:"Love's Gift",69:'Moonfl. Smile'})
PASSIVE_NAMES.update({52:'Possess Time',75:'Weak Spot',336:'Sum. Cover'})
SUPPORT.update({43:'Neutral summon stops a counter.',64:'Neutral summon stops an action.'})
PROFILE_FULL={
2:'A model from several generations ago, once produced more widely than any other machine. Few remain today.',
8:'A machine that directs other construction machines as their leader. It can work even in zero gravity.',
14:'A large machine used in the Machine World War. Only prototypes were built; it was never mass-produced.',
15:'A creation of Zel, a master craftsman of the Machine World. Its transformation and combination mechanisms let it unleash powerful attacks.',
18:'"Strength: 12 million! Machine-affinity manganese! It is ever so strong...!?"',
19:"A strong fire spirit that is always smiling. It is Belfraw's junior companion.",
27:'An immature nine-tailed fox that borrows the body of the priestess it serves. It loves festivals.',
31:'An ancient oni general who fought armies of evil oni alongside humans. Its mighty sword is said to have cleaved even mountains in two.',
32:'A clan of unusual ninjas from the dark world. It is said that no one has ever seen their true forms.',
33:'Dragon gods who watch over the Oni World. They are one with nature and freely control natural disasters.',
45:'A dark army that takes everything from the living. From the abyss, it appears before those who seek power.',
46:'An embodiment of a middle-ranking demon symbolizing silence and terror. It is said to lurk in the stagnant depths of the Spirit World.',
52:'Seven archangels sealed their own souls in holy armor and united to fight mighty demons.',
53:'A holy angel maiden who commands sacred armor. Her pure voice cleanses every impurity.',
60:'A four-legged beast known for its overpowering bad breath. Its close-knit families live together in herds in swamps.',
61:'A shaman of an aquatic demi-human tribe consisting entirely of women. It likes gentle music.',
67:'A liquid creature that likes to inhabit empty containers. Many kinds with different traits have been found.',
69:'A silver-scaled wyvern that flies gracefully through the sky. It and Minis share a deep bond of trust.',
72:'Several magical beasts forcibly fused through forbidden methods. Only a few dark summoners know the technique.',
73:'A legendary great guardian said to dwell on a remote, untouched sacred mountain. Its anger brings storms and splits the earth.',
74:'A king of magical beasts once sealed in golden chains. A blow from its mighty arms can split the earth and scorch the sky.',
75:'Legendary dragons with complementary powers. Any enemy is said to crumble before their breath.',
78:'The ruined fist of an ancient colossus. Standing on it may make you feel stronger.'}
EXTRA_HELP.update({107:'Cntr: phys. 20%/Lv pre-hit; no special.',137:'Summon dmg may hit MP; phys. as Guard.',162:'Take hits for adjacent ally; dmg as Guard.'})
SHARED_MASTER.update({61:'Master: eva+15% cntr+10%',66:'Master: ailment odds up',81:'Master: half range penalty'})
PASSIVE_NAMES.update({6:'Bold Charge',12:'Numb Needle',22:'Encourage',40:'Weak Spot',48:'Height Up',51:'Ailment Up',52:'Possess Turns',53:'Mech Rank Up',66:'Look Above',73:'Shamisen',75:'See Weak Spot',79:'Moonfl. Pray',80:'Thunder Cry',89:'Bracelet',90:'Resonance',95:'Sum. Lv Up',185:'Last Stand',229:'Magic Field',240:'No Possess',271:'Paralyze Hit',282:'HP Drain Hit',287:'MP Drain Hit',310:'Horn Heal',322:'No Paralysis',329:'SPC Guard',331:'Dark Dream',332:'Warped Tomb',333:'Truth Shade',334:'Broken Time',336:'Summon Cover',341:'Sum. Mastery',351:'Moonfl. Hug',352:'Moonfl. Boon',355:'Poison Half',356:'Blind Half',357:'Charm Half',358:'Rage Half',359:'Sleep Half'})
PASSIVE_NAMES.update({52:'Possess Time',75:'Weak Spot',336:'Sum. Cover'})

def manual():
 d={}
 for rec,text in PROFILES.items():d[(12,12,rec)]=text
 for rec,text in SUPPORT.items():d[(32,3,rec)]=text
 for rec,text in ACTIVE_NAMES.items():d[(28,8,rec)]=text
 for rec,text in ACTIVE_HELP.items():d[(28,9,rec)]=text
 for rec,text in ACTIVE_MASTER.items():d[(28,10,rec)]=text
 for rec,text in PASSIVE_NAMES.items():d[(31,8,rec)]=text
 for rec,text in PASSIVE_HELP.items():d[(31,9,rec)]=text
 for rec,text in PASSIVE_MASTER.items():d[(31,10,rec)]=text
 for rec,text in SHARED_HELP.items():d[(34,9,rec)]=text
 for rec,text in SHARED_MASTER.items():d[(34,10,rec)]=text
 for rec,text in EXTRA_HELP.items():d[(31,9,rec)]=text
 return d
def prepare():
 rows=collect();mapping=manual();targets=[];missing=[];over=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.67.iso') as src:
  static=src.resource('02.DAT',3);ix=parse_index(static,len(static));bytext={}
  meta=next(t for t in json.loads((ROOT/'work/translation/en/interface.index.json').read_text())['tables'] if t['resource_path']==[3,31]);b=child(static,ix,31)
  for rec in EXTRA_HELP:
   p=struct.unpack_from('<I',b,4+rec*meta['record_stride']+9*4)[0]
   if not any(r['table']==31 and r['slot']==9 and r['offset']==p for r in rows):
    refs=[i for i in range(meta['record_count']) if struct.unpack_from('<I',b,4+i*meta['record_stride']+9*4)[0]==p]
    rows.append(dict(table=31,slot=9,offset=p,records=refs,lines=[unicodedata.normalize('NFKC',x.decode('cp932')) for x in lines_at(b,p)[0]]))
  for row in rows:
   k=(row['table'],row['slot'],row['records'][0])
   if k in mapping:bytext[(row['table'],row['slot'],tuple(row['lines']))]=mapping[k]
  for row in rows:
   n=row['table'];slot=row['slot'];k=(n,slot,row['records'][0])
   if not(n in (28,31,32,34) or n==12 and slot==12):continue
   english=mapping.get(k,bytext.get((n,slot,tuple(row['lines']))))
   if not english and slot==10 and len(row['lines'])==1 and row['lines'][0].startswith('マスター効果:'):
    tail=row['lines'][0].removeprefix('マスター効果:').replace('最大','max ')
    if not any('\u3040'<=c<='\u9fff' for c in tail):english='Master: '+tail
   if not english:missing.append(dict(key=k,lines=row['lines']));continue
   lines=[english] if slot in (8,10) or n==32 else textwrap.wrap(english,27,break_long_words=False,break_on_hyphens=False)
   if n==12:
    splits=[i for i,c in enumerate(english) if c==' ' and i<=27 and len(english)-i-1<=27]
    if len(english)<=27:lines=[english]
    elif splits:
     i=min(splits,key=lambda i:abs(i-(len(english)-1)/2));lines=[english[:i],english[i+1:]]
   limit=32 if n==32 else 16 if slot==8 else 54
   if max(map(len,lines))>(limit if n==32 or slot==8 else 27) or sum(map(len,lines))>limit or len(lines)>(2 if n==12 else 3):over.append(dict(key=k,english=english,lines=lines))
   data=child(static,ix,n);offset=row['offset'];raw=lines_at(data,offset)[0];raw=raw[:1] if slot==8 else raw
   t=next(t for t in json.loads((ROOT/'work/translation/en/interface.index.json').read_text())['tables'] if t['resource_path']==[3,n])
   full=PROFILE_FULL.get(row['records'][0],english) if n==12 else english
   targets.append(dict(table=n,slot=slot,source_offset=offset,source_sha256=sha(b'\0\0'.join(raw)),records=row['records'],pointer_fields=[4+rec*t['record_stride']+slot*4 for rec in row['records']],english=lines,full_english=full))
 return targets,missing,over
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--refresh',action='store_true');p.add_argument('--missing',action='store_true');a=p.parse_args();targets,missing,over=prepare()
 print(json.dumps(dict(mode='write' if a.write else 'preview',translated=len(targets),missing=len(missing),over=over,sample=targets[:3]),indent=2))
 if a.missing:
  for x in missing:print(json.dumps(x,ensure_ascii=False))
 if a.write or a.refresh:
  assert not missing and not over
  out=ROOT/'work/translation/en/categories_0.1.68/targets.json';assert not (ROOT/'work/output/0.1.68/manifest.json').exists();assert a.refresh or not out.exists();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(version='0.1.68',entries=targets),indent=2)+'\n')
if __name__=='__main__':main()
