/* Kuzu Lahmacun ayarları: galeri için Medya'dan fotoğraf seçme ve sürükleyerek sıralama. */
jQuery(function ($) {
  const $list = $("#kuzu-galeri"), $ids = $("#kuzu-galeri-ids");
  const sync = () => $ids.val($list.children("li").map((_, li) => $(li).data("id")).get().join(","));
  $list.sortable({ update: sync });

  let frame = null;
  $("#kuzu-galeri-sec").on("click", (e) => {
    e.preventDefault();
    if (!frame) {
      frame = wp.media({ title: "Galeri fotoğrafları", button: { text: "Galeriye koy" }, library: { type: "image" }, multiple: "add" });
      frame.on("open", () => {
        const sel = frame.state().get("selection");
        sel.reset();
        $list.children("li").each((_, li) => { const a = wp.media.attachment($(li).data("id")); a.fetch(); sel.add(a); });
      });
      frame.on("select", () => {
        $list.empty();
        frame.state().get("selection").each((a) => {
          const d = a.toJSON();
          const src = (d.sizes && (d.sizes.thumbnail || d.sizes.medium || d.sizes.full) || {}).url || d.url;
          $list.append($("<li>").attr("data-id", d.id).data("id", d.id)
            .append($("<img>").attr({ src, alt: "" }), $("<span>").text(d.title || "")));
        });
        sync();
      });
    }
    frame.open();
  });
  $("#kuzu-galeri-temizle").on("click", (e) => { e.preventDefault(); $list.empty(); sync(); });
});

/* Eve sipariş butonları: satır ekle/sil, sürükleyerek sırala, ikon için Medya'dan logo seç. */
jQuery(function ($) {
  const $tb = $("#kuzu-sip-satirlar");
  if (!$tb.length) return;
  $tb.sortable({ handle: ".tutamak", axis: "y" });
  const sablon = document.getElementById("kuzu-sip-sablon").innerHTML;
  $(".kuzu-sip-ekle").on("click", "button", function (e) {
    e.preventDefault();
    const id = "y" + Date.now().toString(36) + Math.floor(Math.random() * 1e4);
    const $r = $(sablon.split("__i__").join(id));
    $r.find(".sip-ad").val($(this).data("ad") || "");
    $r.find(".sip-renk").val($(this).data("renk") || "#d8342a");
    $tb.append($r);
    $r.find($(this).data("ad") ? 'input[type="url"]' : ".sip-ad").trigger("focus");
  });
  $tb.on("click", ".sip-sil", function (e) { e.preventDefault(); $(this).closest("tr").remove(); });
  $tb.on("click", ".sip-ikon-sil", function (e) {
    e.preventDefault();
    const $r = $(this).closest("tr");
    $r.find(".sip-ikon-id").val(""); $r.find(".sip-ikon-onizleme").empty();
    $r.find(".sip-ikon-sec").text("İkon seç"); $(this).prop("hidden", true);
  });
  $tb.on("click", ".sip-ikon-sec", function (e) {
    e.preventDefault();
    const $r = $(this).closest("tr");
    const f = wp.media({ title: "Buton ikonu (platform logosu)", button: { text: "İkon olarak kullan" }, library: { type: "image" }, multiple: false });
    f.on("select", () => {
      const d = f.state().get("selection").first().toJSON();
      const src = (d.sizes && (d.sizes.thumbnail || d.sizes.medium || d.sizes.full) || {}).url || d.url;
      $r.find(".sip-ikon-id").val(d.id);
      $r.find(".sip-ikon-onizleme").html($("<img>").attr({ src, alt: "" }));
      $r.find(".sip-ikon-sec").text("Değiştir"); $r.find(".sip-ikon-sil").prop("hidden", false);
    });
    f.open();
  });
});
