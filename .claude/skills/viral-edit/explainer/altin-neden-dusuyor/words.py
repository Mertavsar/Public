import json,re
cap=json.load(open("cap_sent.json"))   # sentalign.py çıktısı (align.py uzun seste kaydı)
paras=[p.split() for p in open("script.txt").read().strip().split("\n\n")]
assert sum(map(len,paras))==len(cap),(sum(map(len,paras)),len(cap))
# konusma bicimi -> ekran bicimi (altyazida rakam)
REP=[("yirmi sekiz","28"),("yüzde üç virgül sekiz","%3,8"),("dört bin yüz yirmi iki","4.122"),
 ("otuz bir virgül bire","31,1'e"),("yüzde dört","%4"),("yüzde üç yükselsin.","%3 yükselsin."),
 ("yüzde bir virgül on iki","%1,12"),("on altı Eylül'de","16 Eylül'de"),
 ("yüzde üç virgül yetmiş beş ile dört","%3,75 ile %4"),("on Eylül'de","10 Eylül'de"),
 ("yüzde otuz yedide","%37'de"),("yüzde otuz bir virgül elli bir.","%31,51.")]
out=[];k=0
for pi,pw in enumerate(paras):
    i=0
    while i<len(pw):
        hit=None
        for a,b in REP:
            n=len(a.split())
            if [strip for strip in pw[i:i+n]]==a.split(): hit=(n,b);break
        if hit:
            n,b=hit; ws=cap[k:k+n]
            out.append({"w":b,"s":ws[0]["s"],"e":ws[-1]["e"],"p":pi,"num":1}); i+=n;k+=n
        else:
            c=cap[k]; out.append({"w":pw[i],"s":c["s"],"e":c["e"],"p":pi}); i+=1;k+=1
json.dump(out,open("words.json","w"),ensure_ascii=False)
print(len(out),[o["w"] for o in out if o.get("num")])
for pi in range(len(paras)):
    ws=[o for o in out if o["p"]==pi]; print(pi,f"{ws[0]['s']:.2f}-{ws[-1]['e']:.2f}",ws[0]["w"],ws[1]["w"])
