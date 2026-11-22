# source: format per ../pyrate-command-reference/references/command-list.md:13 and :15 plus
#         ../pyrate-input-file/references/preparing-input-file.md:52-54; values SYNTHETIC - every byte of the
#         body below was written for this fixture
# shows: one plausible reading of the ONE structural statement the corpus makes about a *_PyRate.py input - that
#         it "is a Python file with the fossil occurrence data (as list of Numpy arrays) and, optionally, one or
#         more continuous traits" (command-list.md:13). Shown here as: `from numpy import *`, a
#         data_N=[array([...]), ...] list holding one occurrence-age array per taxon, one such list per age
#         replicate, the accessor functions the documented flags imply (-j picks a replicate, -out tags output
#         names), and an optional trait1=array([... nan ...]) / traits=[...] block for a trait column.
# provenance caveat: this file is NOT part of the mirrored corpus and it is NOT a copy of any upstream file. The
#         corpus only ever NAMES Ursidae_PyRate.py (preparing-input-file.md:54; command-list.md:15 uses it in a
#         command example) and never prints a line of it; nothing under PyRate-doc/ contains it, and no author of
#         this suite had network access. What IS documented is much narrower than the body suggests, so keep the
#         two apart: the file is Python holding numpy arrays (command-list.md:13); several replicates go in one
#         input file and are selected with -j (command-list.md:27-29); -out tags the output names
#         (command-list.md:32-35); extract.ages(replicates=10) "generates 10 random replicates of the data set"
#         (preparing-input-file.md:36-37). NOWHERE do the docs state how many data_N objects a generated file
#         holds, how they are named, whether taxa are sorted, whether an extant taxon's array ends in a trailing
#         0, or what the accessor functions are called - each of those is a guess kept here as an illustration.
#         Note that `array(` and `data_1` occur nowhere in this corpus at all.
# note: SYNTHETIC specifics you must not quote as fact - every age, the taxa_names set, the trait vector, the nan
#         pattern, the number of array() entries, the d=/names= lists and both elision comments below. The ursid
#         names look sourced but are not: only Ursus_etruscus, Ursavus_brevirhinus, Agriotherium_insigne and
#         Agriotherium_intermedium appear anywhere in this corpus, and there as three rows of the wiki's
#         illustrative occurrence table (preparing-input-file.md:16-22), never as a species list.
#         An earlier revision of this header presented the body as an EXCERPT of upstream
#         example_files/Ursidae_PyRate.py at named line ranges, with a byte count (95,992), an md5, "75 species
#         -> 75 array() entries per replicate", "10 replicates" and a trailing-0 rule for extant taxa. None of it
#         was checkable and all of it has been removed; the same claims still stand in
#         ../pyrate-input-file/SKILL.md (its "Verified outside this corpus" section and fixture table), which
#         this file no longer supports. See ../README.md.

#!/usr/bin/env python
from numpy import * 


data_1=[array([2.657485,4.129912,4.380033,3.172819]),
array([6.50294,10.991822]),
array([5.113638,2.742798,4.502155,3.355231,2.992726]),
array([3.467839,3.427282]),
array([5.835269,6.721129,7.98197]),
array([8.1,8.4,12.689526,5.787908,10.1,6.821768,10.1,5.728776,2.945997]),
# ... elided here for brevity: a few more array() entries would sit in this same list ...
array([3.224054,2.245875,3.008434]),
array([22.469962])
]
# ... elided here for brevity: a real generated file repeats the block above once per replicate ...
d=[ data_1, data_2, data_3, data_4, data_5, data_6, data_7, data_8, data_9, data_10]
names=[  'Ursidae_1',  'Ursidae_2',  'Ursidae_3',  'Ursidae_4',  'Ursidae_5',  'Ursidae_6',  'Ursidae_7',  'Ursidae_8',  'Ursidae_9',  'Ursidae_10',]
def get_data(i): return d[i]
def get_out_name(i): return  names[i]
taxa_names=['Agriotherium_africanum','Agriotherium_inexpetans','Agriotherium_insigne','Agriotherium_intermedium','Agriotherium_roblesi','Agriotherium_schneideri','Ailurarctos_lufengensis','Ailuropoda_melanoleuca','Ailuropoda_microta','Ailuropoda_wulingshanensis','Arctodus_pristinus','Arctodus_simus','Arctotherium_brasiliensis','Ballusia_elmensis','Ballusia_hareni','Cephalogale_gracile','Dinocyon_thenardi','Helarctos_malayanus','Hemicyon_gargan','Hemicyon_goeriachensis','Hemicyon_hurzeleri','Hemicyon_mayorali','Hemicyon_sansaniensis','Hemicyon_stehlini','Indarctos_anthracitis','Indarctos_arctoides','Indarctos_atticus','Indarctos_maraghanus','Indarctos_nevadensis','Indarctos_oregonensis','Indarctos_vireti','Indarctos_zdanskyi','Kolponomos_clallamensis','Kolponomos_newportensis','Phoberocyon_akhmetievi','Phoberocyon_aurelianensis','Phoberocyon_dehmi','Phoberocyon_hispanicus','Phoberocyon_johnhenryi','Phoberocyon_youngi','Phoberogale_depereti','Phoberogale_ginesticus','Plionarctos_edensis','Plionarctos_harroldorum','Plithocyon_antunesi','Plithocyon_armagnacensis','Plithocyon_barstowensis','Plithocyon_bruneti','Plithocyon_conquense','Plithocyon_teilhardi','Plithocyon_ursinus','Tremarctos_floridanus','Ursavus_brevirhinus','Ursavus_depereti','Ursavus_intermedius','Ursavus_isorei','Ursavus_orientalis','Ursavus_pawniensis','Ursavus_primaevus','Ursavus_sylvestris','Ursus_abstrusus','Ursus_americanus','Ursus_arctos','Ursus_arvernensis','Ursus_boeckhi','Ursus_deningeri','Ursus_etruscus','Ursus_maritimus','Ursus_minimus','Ursus_ruscinensis','Ursus_spelaeus','Ursus_thibetanus','Ursus_wenzensis','Ursus_yinanensis','Zaragocyon_daamsi']
def get_taxa_names(): return taxa_names

trait1=array([ nan, nan, 285000, nan, nan, nan, nan, 117999.99, nan, nan, nan, nan, nan, 11000, 16000, nan, 410000, 57075.78, 40000, 120000, 90000, nan, 225000, 87000, nan, 160000, 351500, nan, nan, nan, 175000, nan, nan, nan, 146500, nan, nan, nan, nan, nan, nan, nan, nan, nan, 144000, 116000, nan, 37000, 82000, nan, nan, nan, 80000, 1e+05, 67000, 13000, 10000, nan, 90000, nan, nan, 110500, 196287.5, nan, nan, nan, 90000, 371703.81, 40000, nan, 3e+05, 99714.19, nan, nan, nan ])
traits=[trait1]
def get_continuous(i): return traits[i]
