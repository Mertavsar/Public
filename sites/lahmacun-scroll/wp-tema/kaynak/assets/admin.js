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
