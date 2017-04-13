import os
import json

diyDict = {}


def _init_diyDict():
    for lang in ["en_US"]:
        with open(os.getcwd() + "/history/" + lang + ".json") as f:
            data = json.loads(f.read())
            diyDict[lang] = data


_init_diyDict()
print('自定义字典加载完毕')

if __name__ == "__main__":
    print(diyDict)
