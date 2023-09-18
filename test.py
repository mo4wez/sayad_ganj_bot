import re

text = """سُند:(سُ نْ دْ) چہ پیشّ ءَ جوڑ کُرتگیں ناہ ءِ درپے کہ چہ سلامتیں دوبُن پیشّ ءَ جوڑ بیت"""

result = re.findall(r'([^:]+):', text)

print(result)
['\nسَند']

res = [item.strip() for item in result]

print(res)
