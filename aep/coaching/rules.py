import rules

is_coach = rules.is_group_member('Coaches')
is_elearn = rules.is_group_member('eLearn')
is_ace = rules.is_group_member('ACE')

rules.add_rule('can_coach', is_coach)
