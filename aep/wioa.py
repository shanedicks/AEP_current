from people.models import WIOA
from core.utils import state_session

w = WIOA.objects.filter(student__WRU_ID=None)
s = state_session()
count = w.count()

print("Collecting WIOA records")
print("{0} unsent records collected".format(count))


print("Reporting collected records")
for i in w:
	i.send(s)
	print("{0} reported".format(i))