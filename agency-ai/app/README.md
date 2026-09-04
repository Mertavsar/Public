# Agency AI — yerel panel

Her gün açıp içine yazacağın ekran. Tüm uzmanlar sırayla çalışır, her birinin
çıktısını ayrı ayrı görürsün, sonunda birleşik rapor müşteri klasörüne kaydedilir.

## Çalıştırma

Terminal aç, projenin içine gir ve şunu yaz:

```
python3 agency-ai/app/server.py
```

Sonra tarayıcıda: **http://127.0.0.1:7777**

Kapatmak için terminalde `Ctrl+C`.

## Gereken tek şey

**Claude Code CLI.** Panel kendi başına düşünmez; Claude Code'u motor olarak kullanır.
Bu sayede skill'ler, anayasa ve Meta bağlantısı olduğu gibi çalışır — ayrı API
anahtarı ve ayrı ücret yoktur.

Kurulu mu diye bakmak için: `claude --version`
Kurulu değilse: https://claude.com/claude-code

Python zaten macOS'ta yüklüdür. Kurulacak paket, `npm install` yok.

## Kullanım

1. **Marka** seç.
2. **Tarih aralığı** ver (varsayılan: son 7 gün).
3. **Bu hafta ne oldu / müşteri ne dedi** kutusuna yaz. Boş bırakabilirsin.
4. **Ham veri** kutusu: Meta bağlantısı çalışıyorsa boş bırak, sistem kendisi çeker.
   Çekemiyorsa panelden rakamları kopyalayıp buraya yapıştır.
5. **Analizi başlat.**

Uzmanlar sırayla çalışır. Her kutu tamamlandıkça açılır; başlığına tıklayarak
kapatıp açabilirsin.

Sonunda rapor şuraya kaydedilir:
`agency-ai/clients/<marka>/weekly-reports/<bitiş-tarihi>.md`

## Neden tek tek çağırıyor

Claude Code'da skill'ler konuya göre kendiliğinden tetiklenir ve bazen bir kısmı
tetiklenmez — rapor yarım çıkar. Panel bunu ortadan kaldırır: her skill'i **açıkça**
ve **ayrı** çağırır. Hiçbiri atlanmaz, her birinin çıktısı ayrı kutuda görünür.

## Reklam hesabı güvenliği

Panel reklam hesabında **hiçbir değişiklik yapamaz.** İki katmanlı:

1. `agency-ai/CLAUDE.md` §0 — onaysız yazma yasak.
2. `server.py` içindeki `ALLOWED_TOOLS` listesi yalnızca **okuma** araçlarını içerir.
   Kampanya açma, durdurma, bütçe değiştirme araçları listede yoktur; Claude onları
   çağıramaz.

Ayrıca sistem yalnızca `client.md`'de ID'si yazılı hesaplara bakar.

## Meta verisi gelmiyorsa

Alt süreç MCP bağlantısını görmüyor olabilir. Kontrol:

```
claude mcp list
```

Meta sunucusu listede varsa adını not al ve `server.py` içindeki `ALLOWED_TOOLS`
listesindeki `mcp__Meta_Reklam__` önekini o ada göre düzelt.

Listede yoksa Meta bağlantısı CLI'da tanımlı değil demektir. Bu durumda **Ham veri**
kutusunu kullan — sistem elle girilen veriyle de tam çalışır.

## Ayarlar

`server.py` başındaki bölümden değiştirilir:

| Ayar | Ne işe yarar |
|---|---|
| `PORT` | Panelin portu (varsayılan 7777) |
| `STEP_TIMEOUT` | Adım başına üst sınır, saniye (varsayılan 900) |
| `ALLOWED_TOOLS` | Claude'un kullanabileceği araçlar — sadece okuma |
| `STEPS` | Uzman sırası ve başlıkları |

## Sınırlar

- Aynı anda tek analiz çalışır.
- Panel açık kaldığı sürece çalışır; terminali kapatırsan durur.
- Sadece kendi bilgisayarında erişilebilir (`127.0.0.1`). Dışarı açık değildir.
- Her adım ayrı bir Claude Code oturumudur; adımlar birbirinin sohbetini görmez.
  Birleşik raporu üreten son adıma diğerlerinin çıktıları toplu olarak verilir.
