import { zColor } from "@remotion/zod-types";
import { z } from "zod";

export const introSchema = z.object({
  logoYazisi: z.string(),
  markaAdi: z.string(),
  musteriMesaji: z.string(),
  isletmeCevabi: z.string(),
  musteriSonMesaj: z.string(),
  slogan1: z.string(),
  slogan1Vurgu: z.string(),
  slogan2: z.string(),
  slogan2Vurgu: z.string(),
  ctaUstYazi: z.string(),
  telefon: z.string(),
  vurguRengi: zColor(),
  sesEfektleri: z.boolean(),
});

export type IntroProps = z.infer<typeof introSchema>;

export const defaultIntroProps: IntroProps = {
  logoYazisi: "WhatsApp",
  markaAdi: "Mağaza Adı",
  musteriMesaji: "Merhaba! Bu ürün hâlâ stokta mı? 👀",
  isletmeCevabi: "Evet, stokta! 🎉 Hemen siparişinizi oluşturalım.",
  musteriSonMesaj: "Harika, sipariş veriyorum 🙌",
  slogan1: "Sorularınız anında yanıtlanır.",
  slogan1Vurgu: "anında",
  slogan2: "Siparişiniz tek mesajda.",
  slogan2Vurgu: "tek mesajda.",
  ctaUstYazi: "Hemen WhatsApp'tan yazın",
  telefon: "+90 5XX XXX XX XX",
  vurguRengi: "#25D366",
  sesEfektleri: true,
};
