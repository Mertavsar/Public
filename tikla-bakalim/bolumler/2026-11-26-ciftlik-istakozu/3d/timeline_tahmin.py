import json, re
txt = open("/home/user/Public/tikla-bakalim/bolumler/2026-11-26-ciftlik-istakozu/seslendirme.txt").read().split("\n====\n")[1]
txt = re.sub(r"\s+", " ", txt).strip()
sents = [s.strip() for s in re.findall(r"[^.!?]+[.!?]", txt)]
ids = "hook room hot whyq step cta name live tr mother hatch tanks molt mini like rooms flow cold warm dc pipe feed kg growth plate answerq fight ninety comment comment2 loop".split()
assert len(ids) == len(sents), (len(ids), len(sents), sents)
t = .25; out = []
for i, (sid, s) in enumerate(zip(ids, sents)):
    w = s.split(); d = max(1.2, len(w) / 2.6 + .35); words = []; k = t
    for x in w:
        dw = d * (len(x) + 2) / sum(len(y) + 2 for y in w); words.append({"w": x, "s": round(k, 3), "e": round(k + dw, 3)}); k += dw
    out.append({"id": f"{sid}#{i}", "text": s, "s": round(t, 3), "e": round(t + d, 3), "words": words}); t += d + .45
json.dump({"END": round(t + .4, 2), "S": out}, open("timeline.json", "w"), ensure_ascii=False)
print(round(t, 1), len(out))
