<?php
/**
 * Ana sayfanın panelden düzenlenen bölümleri: kayan bant, menü, galeri, merak edilenler,
 * ziyaret bilgileri ve Google yorumları.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Paneldeki ayar; boşsa temanın varsayılanı. */
function kuzu_ayar( $k ) {
	$a = get_option( 'kuzu_ayarlar', array() );
	$v = kuzu_varsayilan();
	if ( is_array( $a ) && isset( $a[ $k ] ) && '' !== trim( (string) $a[ $k ] ) ) {
		return $a[ $k ];
	}
	return isset( $v[ $k ] ) ? $v[ $k ] : '';
}

function kuzu_satirlar( $metin ) {
	return array_values( array_filter( array_map( 'trim', preg_split( '/\R/u', (string) $metin ) ), 'strlen' ) );
}

function kuzu_harita_linki() {
	return 'https://www.google.com/maps?cid=' . rawurlencode( kuzu_ayar( 'cid' ) );
}

function kuzu_yorum_linki() {
	return 'https://search.google.com/local/writereview?placeid=' . rawurlencode( kuzu_ayar( 'yer_id' ) );
}

/** Kırmızı kayan bant: kelimeler iki kez yazılır, CSS yarıya kaydırıp başa sarar. */
function kuzu_bant() {
	$k = kuzu_satirlar( kuzu_ayar( 'bant' ) );
	$s = '';
	foreach ( $k as $w ) {
		$s .= '<span>' . esc_html( $w ) . '</span>';
	}
	echo '<div class="marquee" aria-hidden="true"><div>' . "\n    " . $s . "\n    " . $s . "\n  </div></div>";
}

/** Menü: "Kategori | Ürün | Fiyat" satırları, kategori sırası ilk geçtiği sıra. */
function kuzu_menu() {
	$gruplar = array();
	foreach ( kuzu_satirlar( kuzu_ayar( 'menu' ) ) as $satir ) {
		$p = array_map( 'trim', explode( '|', $satir ) );
		if ( count( $p ) < 2 ) {
			continue;
		}
		$kat   = $p[0];
		$urun  = count( $p ) >= 3 ? $p[1] : $p[0];
		$fiyat = count( $p ) >= 3 ? $p[2] : $p[1];
		$gruplar[ $kat ][] = array( $urun, $fiyat );
	}
	echo '<div class="cards">';
	foreach ( $gruplar as $kat => $urunler ) {
		echo "\n        " . '<article class="card"><h3 class="tag">' . esc_html( $kat ) . '</h3><ul class="prices">';
		foreach ( $urunler as $u ) {
			echo "\n          " . '<li><span>' . esc_html( $u[0] ) . '</span><i class="dots"></i><b>' . esc_html( $u[1] ) . '</b></li>';
		}
		echo '</ul></article>';
	}
	echo "\n      </div>\n";
	$not = kuzu_ayar( 'menu_notu' );
	if ( $not ) {
		echo '      <p class="menu-note">' . esc_html( $not ) . '</p>';
	}
}

/** Galeri fotoğrafları: paneldeki seçim; seçim yoksa temayla gelen fotoğraflar. */
function kuzu_galeri_fotolari() {
	$ids = array_filter( array_map( 'absint', explode( ',', (string) kuzu_ayar( 'galeri' ) ) ) );
	$out = array();
	foreach ( $ids as $id ) {
		$full = wp_get_attachment_image_url( $id, 'full' );
		if ( ! $full ) {
			continue;
		}
		$meta  = wp_get_attachment_metadata( $id );
		$baslik = get_the_title( $id );
		$alt    = trim( (string) get_post_meta( $id, '_wp_attachment_image_alt', true ) );
		$out[] = array(
			'src'    => wp_get_attachment_image_url( $id, 'large' ),
			'srcset' => (string) wp_get_attachment_image_srcset( $id, 'full' ),
			'full'   => $full,
			'w'      => isset( $meta['width'] ) ? (int) $meta['width'] : 2000,
			'h'      => isset( $meta['height'] ) ? (int) $meta['height'] : 1125,
			'baslik' => $baslik,
			'alt_yazi' => (string) wp_get_attachment_caption( $id ),
			'alt'    => $alt ? $alt : $baslik,
			'konum'  => '50% 50%',
		);
	}
	if ( $out ) {
		return $out;
	}
	foreach ( kuzu_varsayilan_galeri() as $g ) {
		list( $ad, $baslik, $alt_yazi, $alt, $konum, $h ) = $g;
		$out[] = array(
			'src'      => KUZU_URI . "foto/{$ad}-m.jpg",
			'srcset'   => KUZU_URI . "foto/{$ad}-k.jpg 720w, " . KUZU_URI . "foto/{$ad}-m.jpg 1200w, " . KUZU_URI . "foto/{$ad}.jpg 2000w",
			'full'     => KUZU_URI . "foto/{$ad}.jpg",
			'w'        => 2000,
			'h'        => $h,
			'baslik'   => $baslik,
			'alt_yazi' => $alt_yazi,
			'alt'      => $alt,
			'konum'    => $konum,
		);
	}
	return $out;
}

function kuzu_galeri() {
	$f = kuzu_galeri_fotolari();
	$n = count( $f );
	$iki = function ( $i ) { return str_pad( (string) $i, 2, '0', STR_PAD_LEFT ); };
	?>
  <section class="galeri" id="galeri" aria-labelledby="galTitle">
    <div class="band"><div class="wrap gal-head">
      <div class="sec-head">
        <p class="tag red">Galeri</p>
        <h2 class="display" id="galTitle">Fırının başından</h2>
        <p><?php echo esc_html( kuzu_ayar( 'galeri_yazi' ) ); ?></p>
      </div>
      <div class="gal-ctrl">
        <span class="gal-count" id="galCount" aria-live="polite">01 / <?php echo esc_html( $iki( $n ) ); ?></span>
        <button type="button" class="gal-btn" id="galPrev" aria-label="Önceki fotoğraf"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5 8 12l7 7"/></svg></button>
        <button type="button" class="gal-btn" id="galNext" aria-label="Sonraki fotoğraf"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg></button>
      </div>
    </div></div>
    <div class="slider" id="slider" tabindex="0" aria-roledescription="carousel" aria-label="Fotoğraflar">
	<?php foreach ( $f as $i => $p ) :
		$cap = $p['baslik'] . ( $p['alt_yazi'] ? ' · ' . $p['alt_yazi'] : '' );
		?>
      <figure class="slide<?php echo 0 === $i ? ' is-active' : ''; ?>" role="group" aria-roledescription="slayt" aria-label="<?php echo esc_attr( ( $i + 1 ) . ' / ' . $n . ': ' . $p['baslik'] ); ?>">
        <button type="button" class="gi" data-full="<?php echo esc_url( $p['full'] ); ?>" data-cap="<?php echo esc_attr( $cap ); ?>" aria-label="<?php echo esc_attr( $p['baslik'] . ': büyüt' ); ?>">
          <img src="<?php echo esc_url( $p['src'] ); ?>"<?php echo $p['srcset'] ? ' srcset="' . esc_attr( $p['srcset'] ) . '" sizes="(min-width: 760px) 84vw, 86vw"' : ''; ?> alt="<?php echo esc_attr( $p['alt'] ); ?>"<?php echo $i ? ' loading="lazy"' : ''; ?> decoding="async" width="<?php echo (int) $p['w']; ?>" height="<?php echo (int) $p['h']; ?>" style="object-position: <?php echo esc_attr( $p['konum'] ); ?>">
        </button>
        <figcaption><span class="script"><?php echo esc_html( $p['baslik'] ); ?></span><?php echo $p['alt_yazi'] ? '<small>' . esc_html( $p['alt_yazi'] ) . '</small>' : ''; ?></figcaption>
      </figure>
	<?php endforeach; ?>
    </div>
    <div class="band"><div class="wrap"><div class="gal-dots" id="galDots"><?php
	for ( $i = 0; $i < $n; $i++ ) {
		echo '<button type="button" aria-label="' . esc_attr( ( $i + 1 ) . '. fotoğraf' ) . '"' . ( 0 === $i ? ' class="is-active" aria-current="true"' : '' ) . '><i></i></button>';
	}
	?></div></div></div>
  </section>
	<?php
}

/** Merak edilenler: boş satırla ayrılmış bloklar; ilk satır soru, kalanı cevap. */
function kuzu_sss_listesi() {
	$bloklar = preg_split( '/\R\s*\R/u', trim( (string) kuzu_ayar( 'sss' ) ) );
	$out     = array();
	foreach ( $bloklar as $b ) {
		$sat = kuzu_satirlar( $b );
		if ( count( $sat ) < 2 ) {
			continue;
		}
		$out[] = array( array_shift( $sat ), implode( ' ', $sat ) );
	}
	return $out;
}

function kuzu_sss() {
	$izin = array(
		'a'      => array( 'href' => true, 'target' => true, 'rel' => true ),
		'b'      => array(),
		'strong' => array(),
		'em'     => array(),
		'br'     => array(),
	);
	$liste = kuzu_sss_listesi();
	echo '<div class="qs">';
	foreach ( $liste as $q ) {
		echo "\n        " . '<details class="q"><summary>' . esc_html( $q[0] ) . '</summary><p>' . wp_kses( $q[1], $izin ) . '</p></details>';
	}
	echo "\n      </div>\n";
	$faq = array(
		'@context'   => 'https://schema.org',
		'@type'      => 'FAQPage',
		'mainEntity' => array_map(
			function ( $q ) {
				return array(
					'@type'          => 'Question',
					'name'           => $q[0],
					'acceptedAnswer' => array( '@type' => 'Answer', 'text' => wp_strip_all_tags( $q[1] ) ),
				);
			},
			$liste
		),
	);
	$yer = array(
		'@context'      => 'https://schema.org',
		'@type'         => 'Restaurant',
		'name'          => get_bloginfo( 'name' ) ? get_bloginfo( 'name' ) : 'Kuzu Lahmacun',
		'url'           => home_url( '/' ),
		'servesCuisine' => 'Türk mutfağı, lahmacun',
		'telephone'     => kuzu_ayar( 'telefon' ),
		'address'       => kuzu_ayar( 'adres' ),
		'hasMap'        => kuzu_harita_linki(),
	);
	echo '    <script type="application/ld+json">' . wp_json_encode( $faq, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>' . "\n";
	echo '    <script type="application/ld+json">' . wp_json_encode( $yer, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES ) . '</script>';
}

/** Finaldeki adres, telefon ve çalışma saatleri. */
function kuzu_ziyaret() {
	$satirlar = array();
	if ( kuzu_ayar( 'adres' ) ) {
		$satirlar[] = array( 'Adres', esc_html( kuzu_ayar( 'adres' ) ) );
	}
	$tel = kuzu_ayar( 'telefon' );
	if ( $tel ) {
		$satirlar[] = array( 'Telefon', '<a href="tel:' . esc_attr( preg_replace( '/[^0-9+]/', '', $tel ) ) . '">' . esc_html( $tel ) . '</a>' );
	}
	$saat = kuzu_satirlar( kuzu_ayar( 'saatler' ) );
	if ( $saat ) {
		$satirlar[] = array( 'Çalışma saatleri', implode( '<br>', array_map( 'esc_html', $saat ) ) );
	}
	echo '<dl class="visit" id="visit">';
	foreach ( $satirlar as $s ) {
		echo '<div><dt>' . esc_html( $s[0] ) . '</dt><dd>' . $s[1] . '</dd></div>'; // $s[1] yukarıda kaçırıldı
	}
	echo '</dl>';
}

/** Google yorumları sayfanın içine gömülür; site betiği yalnızca 5 yıldızlıları gösterir. */
function kuzu_google_verisi() {
	$g = get_option( 'kuzu_google' );
	if ( is_array( $g ) && ! empty( $g['reviews'] ) ) {
		return $g;
	}
	$ilk = get_template_directory() . '/assets/yorumlar-ilk.json';
	if ( file_exists( $ilk ) ) {
		$d = json_decode( (string) file_get_contents( $ilk ), true );
		if ( is_array( $d ) ) {
			foreach ( $d['reviews'] as &$r ) {
				if ( ! empty( $r['photo'] ) && 0 === strpos( $r['photo'], 'yorum/' ) ) {
					$r['photo'] = KUZU_URI . $r['photo'];
				}
			}
			unset( $r );
			return $d;
		}
	}
	return array( 'reviews' => array() );
}

function kuzu_google_json() {
	$g   = kuzu_google_verisi();
	$out = array( 'reviews' => array() );
	foreach ( (array) $g['reviews'] as $r ) {
		$out['reviews'][] = array(
			'author' => (string) ( $r['author'] ?? '' ),
			'uri'    => esc_url_raw( (string) ( $r['uri'] ?? '' ) ),
			'photo'  => esc_url_raw( (string) ( $r['photo'] ?? '' ) ),
			'rating' => (int) ( $r['rating'] ?? 0 ),
			'date'   => (string) ( $r['date'] ?? '' ),
			'text'   => (string) ( $r['text'] ?? '' ),
		);
	}
	echo '<script type="application/json" id="kuzu-google">' . wp_json_encode( $out, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP ) . '</script>' . "\n";
}

/** YouTube linkinden video kimliği: shorts/, youtu.be/, watch?v=, embed/, live/ biçimleri. */
function kuzu_youtube_id( $url ) {
	if ( preg_match( '~(?:youtube\.com/(?:shorts/|embed/|live/|watch\?(?:.*&)?v=)|youtu\.be/)([A-Za-z0-9_-]{11})~', (string) $url, $m ) ) {
		return $m[1];
	}
	return preg_match( '~^[A-Za-z0-9_-]{11}$~', trim( (string) $url ) ) ? trim( (string) $url ) : '';
}

/** Paneldeki "link | başlık" satırları. */
function kuzu_video_listesi() {
	$out = array();
	foreach ( kuzu_satirlar( kuzu_ayar( 'videolar' ) ) as $satir ) {
		$p  = array_map( 'trim', explode( '|', $satir, 2 ) );
		$id = kuzu_youtube_id( $p[0] );
		if ( $id ) {
			$out[] = array( $id, isset( $p[1] ) ? $p[1] : '' );
		}
	}
	return $out;
}

function kuzu_nav_videolar() {
	if ( kuzu_video_listesi() ) {
		echo '<a class="nav" href="#videolar">Videolar</a>';
	}
}

/** Videolar: video eklenmediyse bölüm hiç görünmez. YouTube oynatıcısı yalnızca tıklanınca yüklenir. */
function kuzu_videolar() {
	$v = kuzu_video_listesi();
	if ( ! $v ) {
		return;
	}
	$play = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>';
	?>
<section class="videolar band" id="videolar" aria-labelledby="vidTitle">
    <div class="wrap">
      <div class="rev-head">
        <div class="sec-head">
          <p class="tag red">Videolar</p>
          <h2 class="display" id="vidTitle"><?php echo esc_html( kuzu_ayar( 'video_baslik' ) ); ?></h2>
          <p><?php echo esc_html( kuzu_ayar( 'video_yazi' ) ); ?></p>
        </div>
        <div class="rev-ctrl">
          <button type="button" class="gal-btn" id="vidPrev" aria-label="Önceki videolar"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5 8 12l7 7"/></svg></button>
          <button type="button" class="gal-btn" id="vidNext" aria-label="Sonraki videolar"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg></button>
        </div>
      </div>
      <div class="vids" id="vids">
	<?php foreach ( $v as $x ) :
		list( $id, $baslik ) = $x;
		$etiket = $baslik ? $baslik : 'Kuzu Lahmacun videosu';
		?>
        <figure class="vid">
          <button type="button" class="vid-kare" data-yt="<?php echo esc_attr( $id ); ?>" aria-label="<?php echo esc_attr( 'Videoyu oynat: ' . $etiket ); ?>">
            <img src="https://i.ytimg.com/vi/<?php echo esc_attr( $id ); ?>/oardefault.jpg" data-yedek="https://i.ytimg.com/vi/<?php echo esc_attr( $id ); ?>/hqdefault.jpg" alt="" loading="lazy" decoding="async" width="405" height="720">
            <span class="vid-oyna" aria-hidden="true"><?php echo $play; // sabit SVG ?></span>
          </button>
		<?php if ( $baslik ) : ?>
          <figcaption><?php echo esc_html( $baslik ); ?></figcaption>
		<?php endif; ?>
        </figure>
	<?php endforeach; ?>
      </div>
    </div>
  </section>

	<?php
}

/** Paket sipariş linkleri: sabit platformlar + "Ad | link" satırları. */
function kuzu_siparis_listesi() {
	$sabit = array(
		'siparis_yemeksepeti' => array( 'Yemeksepeti', '#fa0050' ),
		'siparis_trendyol'    => array( 'Trendyol Yemek', '#f27a1a' ),
		'siparis_getir'       => array( 'Getir Yemek', '#5d3ebc' ),
		'siparis_migros'      => array( 'Migros Yemek', '#ff7e00' ),
	);
	$out = array();
	foreach ( $sabit as $k => $x ) {
		$u = trim( (string) kuzu_ayar( $k ) );
		if ( $u ) {
			$out[] = array( $x[0], $u, $x[1] );
		}
	}
	foreach ( kuzu_satirlar( kuzu_ayar( 'siparis_diger' ) ) as $satir ) {
		$p = array_map( 'trim', explode( '|', $satir, 2 ) );
		if ( 2 === count( $p ) && $p[0] && $p[1] ) {
			$out[] = array( $p[0], $p[1], '#d8342a' );
		}
	}
	return $out;
}

function kuzu_siparis( $yer ) {
	$l = kuzu_siparis_listesi();
	if ( ! $l ) {
		return;
	}
	$ok   = '<svg class="ok" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg>';
	$btns = '';
	foreach ( $l as $x ) {
		$btns .= "\n          " . '<a class="sip" href="' . esc_url( $x[1] ) . '" style="--marka:' . esc_attr( $x[2] ) . '" target="_blank" rel="noopener"><i></i>' . esc_html( $x[0] ) . $ok . '</a>';
	}
	if ( 'menu' === $yer ) {
		echo "\n      " . '<div class="siparis">' . "\n        " . '<p class="siparis-baslik">Eve sipariş</p>' . "\n        " . '<div class="siparis-btns">' . $btns . "\n        </div>\n      </div>";
	} else {
		echo "\n      " . '<div class="siparis-btns final-sip">' . $btns . "\n      </div>";
	}
}
