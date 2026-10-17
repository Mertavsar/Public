# WhatsApp Tanıtım İntrosu (Remotion)

~10.7 sn'lik, sesli, metinleri değiştirilebilir WhatsApp tanıtım introsu.

| Kompozisyon | Boyut | Kullanım |
|---|---|---|
| `WhatsAppIntro` | 1080×1920 | Reels / TikTok / Shorts / Story |
| `WhatsAppIntroYatay` | 1920×1080 | YouTube / web |

## Akış

1. **Logo** (0–2.3 sn) — balon çizilerek açılır, halkalar yayılır, "WhatsApp" yazısı harf harf gelir.
2. **Sohbet** (1.8–6.5 sn) — telefon aşağıdan girer; müşteri mesajı yazılıp gönderilir,
   tikler maviye döner, işletme "yazıyor…" der ve cevap verir, müşteri siparişi onaylar.
3. **Slogan** (6–8.3 sn) — iki satır, kelime kelime; vurgulu kelimeler yeşil + alt çizgi.
4. **Kapanış** (7.8–10.7 sn) — logo, CTA yazısı, telefon numarası butonu, dokunma efekti.

Ses efektleri (`public/*.wav`) ffmpeg ile sentezlendi; telif sorunu yoktur.
Font: Inter (OFL), `public/fonts/` altında gömülü — render internet istemez.

## Kullanım

```bash
npm install
npm run studio        # tarayıcıda önizleme + sağ panelden metinleri düzenleme
npm run render        # out/whatsapp-intro.mp4 (dikey)
npm run render:yatay  # out/whatsapp-intro-yatay.mp4
npm run still         # out/kapak.png
```

## Özelleştirme

Tüm metinler `src/schema.ts` → `defaultIntroProps` içinde. Studio'da sağ panelden
de değiştirilebilir ya da komut satırından verilebilir:

```bash
npx remotion render WhatsAppIntro out/marka.mp4 \
  --props='{"markaAdi":"Valens Collection","telefon":"+90 532 000 00 00"}'
```

| Alan | Ne |
|---|---|
| `markaAdi` | Sohbet başlığı ve kapanıştaki marka adı |
| `musteriMesaji`, `isletmeCevabi`, `musteriSonMesaj` | Sohbetteki 3 mesaj |
| `slogan1/2` + `slogan1Vurgu/2Vurgu` | Slogan satırları ve yeşil vurgulanacak kelimeler |
| `ctaUstYazi`, `telefon` | Kapanış çağrısı ve numara |
| `vurguRengi` | Ana yeşil |
| `sesEfektleri` | `false` → sessiz (kendi müziğinizi kurgu programında ekleyin) |

Sahne süreleri `src/theme.ts` → `SCENES`; sohbet içindeki zamanlama `src/scenes/ChatScene.tsx` → `T`.

Logo kendi çizimimizdir (balon + ahize). Resmi WhatsApp logosunu kullanmak isterseniz
dosyayı `public/` altına koyup `src/components/Logo.tsx` içinde `<Img src={staticFile(...)} />`
ile değiştirin; WhatsApp marka kurallarına uyun.

> Bulut ortamında (Chrome indirilemeyen yerlerde) render için:
> `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`
