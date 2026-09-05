"""Audit helper (pre-autonomy Layer B/C): for each Founder concept token, list Dart
declarations in lib/ and usage counts in lib/ vs test/.  Read-only.
Usage: python3 concept_scan.py <repo_root>
"""
import os, re, sys, collections

ROOT = sys.argv[1]
TOKENS = {
    'Concept': r'\bConcept(?!Summary|ual)\w*',
    'ConceptSummary': r'\bConceptSummary\w*',
    'SkillCase': r'\bSkillCase\w*',
    'MethodCase': r'\bMethodCase\w*',
    'Method(entity)': r'\b(?:TeachingMethod|MethodId|MethodRegistry|methodId|Method\b)',
    'CurriculumEdge/prereq': r'\b(?:CurriculumEdge|prerequisite|prereq|Prerequisite)\w*',
    'LearningActivity': r'\bLearningActivity\w*',
    'SemanticBinding': r'\bSemanticBinding\w*',
    'TutorScope': r'\bTutorScope\w*',
    'allowedMethods': r'\ballowedMethods\b',
    'PedagogyRuntime': r'\b(?:PedagogyRuntime|PedagogyEngine|PedagogyModel|Pedagogy)\w*',
    'PlannedAct': r'\bPlannedAct\w*',
    'TeachingAct': r'\bTeachingAct\w*',
    'LearningEvidence': r'\bLearningEvidence\w*',
    'EvidenceLog/append': r'\b(?:EvidenceLog|appendEvidence|evidenceLog|EvidenceStore)\w*',
    'StudentState/KnowledgeState': r'\b(?:StudentState|KnowledgeState|StudentModel|StudentKnowledge|Mastery|MasteryState)\w*',
    'NextAction': r'\b(?:NextAction|nextAction|LearningAgenda|AgendaItem|Recommendation)\w*',
    'LearningContext': r'\bLearningContext\w*',
    'LearningView': r'\bLearningView\w*',
    'TrustedLearningSource': r'\b(?:TrustedLearningSource|TrustedSource|Provenance|SourceRef|SourceAsset)\w*',
    'Learnable': r'\bLearnable\w*',
    'ActivityPattern': r'\b(?:ActivityPattern|activityPattern|patternId|PatternRegistry)\w*',
    'LessonIndex': r'\bLessonIndex\w*',
    'Surface': r'\b(?:LearningSurface|Surface|surfaceId|SurfaceKind)\w*',
    'SliceCurriculum': r'\bSliceCurriculum\w*',
    'gradable': r'\bgradable\b',
    'failClosed': r'(?:fail.?closed|failClosed|refuse|Refuse|từ chối)',
    'LearningBlueprint': r'\bLearningBlueprint\w*|BlueprintCatalogue\w*',
    'PresentationPolicy': r'\bPresentationPolicy\w*',
    'PedagogicalBoundary': r'\bPedagogicalBoundary\w*|Boundary\w*',
    'AiCurriculum': r'\bAiCurriculum\w*',
    'LearnerStore/Profile': r'\b(?:LearnerStore|LearnerProfile|learnerId|deviceId|profileId)\w*',
    'LearningSession(store)': r'\bLearningSession\w*',
    'Lineage': r'\bLineage\w*',
    'ErrorHypothesis/Diagnosis': r'\b(?:ErrorHypothesis|MultiSkillDiagnosis|Diagnosis)\w*',
    'ReviewPriority/Scheduler': r'\b(?:ReviewPriority|Scheduler|SpacedRepetition|FSRS)\w*',
    'TransferProbe': r'\bTransferProbe\w*',
    'Claim/ClaimGate': r'\b(?:Claim|claimGate|ClaimGate|Support)\w*',
}
decl = re.compile(r'^\s*(?:abstract\s+|sealed\s+|final\s+|base\s+|mixin\s+)*(class|enum|typedef|mixin|extension)\s+(\w+)')
files = {}
for sub in ('lib', 'test'):
    for dp, _, fs in os.walk(os.path.join(ROOT, sub)):
        for f in fs:
            if f.endswith('.dart'):
                p = os.path.join(dp, f)
                files[p] = open(p, encoding='utf-8').read().splitlines()
for name, pat in TOKENS.items():
    rx = re.compile(pat)
    libc = collections.Counter(); testc = collections.Counter(); decls = []
    for p, lines in files.items():
        rel = os.path.relpath(p, ROOT)
        for i, l in enumerate(lines, 1):
            if rx.search(l):
                (libc if rel.startswith('lib/') else testc)[rel] += 1
                m = decl.match(l)
                if m and rel.startswith('lib/') and rx.search(m.group(2)):
                    decls.append(f'{rel}:{i} {m.group(1)} {m.group(2)}')
    print(f'\n## {name}  lib_hits={sum(libc.values())} lib_files={len(libc)} test_hits={sum(testc.values())} test_files={len(testc)}')
    for d in decls[:25]: print('  DECL', d)
    for f, c in libc.most_common(8): print('  lib', c, f)
    for f, c in testc.most_common(6): print('  test', c, f)
