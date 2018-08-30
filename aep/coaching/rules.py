import rules

is_coach = rules.is_group_member('Coaches')
is_elearn = rules.is_group_member('eLearn')
is_ace = rules.is_group_member('ACE')

rules.add_rule('can_coach', is_coach)

@rules.predicate
def active_ase181(ace_record):
	return ace_record.student.active_classes().filter(section__course__code='ASE181').count()>0

@rules.predicate
def completed_ase181(ace_record):
	return ace_record.student.completed_classes().filter(section__course__code='ASE181').count()>0

ase181 = active_ase181 | completed_ase181

@rules.predicate
def active_ase151(ace_record):
	return ace_record.student.active_classes().filter(section__course__code='ASE151').count()>0

@rules.predicate
def completed_ase151(ace_record):
	return ace_record.student.completed_classes().filter(section__course__code='ASE151').count()>0

ase151 = active_ase151 | completed_ase151

@rules.predicate
def active_ase131(ace_record):
	return ace_record.student.active_classes().filter(section__course__code='ASE131').count()>0

@rules.predicate
def completed_ase131(ace_record):
	return ace_record.student.completed_classes().filter(section__course__code='ASE131').count()>0

ase131 = active_ase131 | completed_ase131

@rules.predicate
def active_ase141(ace_record):
	return ace_record.student.active_classes().filter(section__course__code='ASE141').count()>0

@rules.predicate
def completed_ase141(ace_record):
	return ace_record.student.completed_classes().filter(section__course__code='ASE141').count()>0

ase141 = active_ase141 | completed_ase141

@rules.predicate
def active_ase142(ace_record):
	return ace_record.student.active_classes().filter(section__course__code='ASE142').count()>0

@rules.predicate
def completed_ase142(ace_record):
	return ace_record.student.completed_classes().filter(section__course__code='ASE142').count()>0

ase142 = active_ase142 | completed_ase142

@rules.predicate
def passed_math092(ace_record):
	return ace_record.math_092

rules.add_rule('can_eng062', ase181)

read072 = ase181 | ase151

rules.add_rule('can_read072', read072)

math092 = ase131 | ase141

rules.add_rule('can_math092', math092)

math098 = ase142 & passed_math092

rules.add_rule('can_math098', math098)
