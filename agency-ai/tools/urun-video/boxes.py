"""Poster grafik katmaninin kaynak gorseldeki (1024x1536) konumlari."""

# Temizlenecek alanlar (genis, dikissiz doldurma icin)
INPAINT_BOXES = [
    ("kicker", 40, 34, 416, 170),
    ("title", 40, 628, 448, 842),
    ("title_rule", 40, 816, 448, 852),   # alt cizgi izi
    ("icons", 822, 658, 994, 1374),
]

# Kamera geri cekilirken sirayla geri getirilecek ogeler
REVEAL_ELEMENTS = [
    ("kicker", 40, 34, 416, 170),
    ("title", 40, 628, 448, 842),
    ("icon1", 822, 658, 994, 854),
    ("icon2", 822, 854, 994, 1014),
    ("icon3", 822, 1014, 994, 1184),
    ("icon4", 822, 1184, 994, 1374),
]
