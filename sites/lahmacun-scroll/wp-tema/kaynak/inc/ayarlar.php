<?php
/**
 * Yönetim panelinde "Kuzu Lahmacun" sayfası: menü, iletişim, merak edilenler, kayan bant,
 * galeri ve Google yorumları. Kod bilmeden düzenlenir; Kaydet'e basınca site güncellenir.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action(
	'admin_menu',
	function () {
		add_menu_page( 'Kuzu Lahmacun', 'Kuzu Lahmacun', 'manage_options', 'kuzu-ayarlar', 'kuzu_ayarlar_sayfa', 'dashicons-store', 3 );
	}
);

add_action(
	'admin_init',
	function () {
		register_setting( 'kuzu_ayarlar_grubu', 'kuzu_ayarlar', array( 'sanitize_callback' => 'kuzu_ayarlar_temizle' ) );
	}
);

function kuzu_ayarlar_temizle( $g ) {
	$eski = get_option( 'kuzu_ayarlar', array() );
	$g    = is_array( $g ) ? wp_unslash( $g ) : array();
	$out  = array();
	foreach ( array( 'telefon', 'adres', 'menu_notu', 'galeri_yazi', 'video_baslik', 'video_yazi', 'yer_id', 'cid' ) as $k ) {
		$out[ $k ] = sanitize_text_field( $g[ $k ] ?? '' );
	}
	foreach ( array( 'saatler', 'menu', 'bant', 'videolar' ) as $k ) {
		$out[ $k ] = sanitize_textarea_field( $g[ $k ] ?? '' );
	}
	$out['sss']    = wp_kses( $g['sss'] ?? '', array( 'a' => array( 'href' => true, 'target' => true, 'rel' => true ), 'b' => array(), 'strong' => array(), 'em' => array(), 'br' => array() ) );
	// Eve sipariş butonları: satır sırası, ekrandaki (sürüklenmiş) sıradır
	$out['siparis'] = array();
	foreach ( (array) ( $g['siparis'] ?? array() ) as $r ) {
		$r    = (array) $r;
		$ad_  = sanitize_text_field( $r['ad'] ?? '' );
		$link = esc_url_raw( trim( (string) ( $r['link'] ?? '' ) ) );
		if ( '' === $ad_ || '' === $link ) {
			continue;
		}
		$renk             = sanitize_hex_color( $r['renk'] ?? '' );
		$out['siparis'][] = array( 'ad' => $ad_, 'link' => $link, 'ikon' => absint( $r['ikon'] ?? 0 ), 'renk' => $renk ? $renk : '#d8342a' );
	}
	$out['galeri'] = implode( ',', array_filter( array_map( 'absint', explode( ',', (string) ( $g['galeri'] ?? '' ) ) ) ) );
	$yeni          = trim( sanitize_text_field( $g['google_anahtar'] ?? '' ) );
	$out['google_anahtar'] = '' !== $yeni ? $yeni : ( is_array( $eski ) ? ( $eski['google_anahtar'] ?? '' ) : '' );
	if ( ! empty( $g['google_anahtar_sil'] ) ) {
		$out['google_anahtar'] = '';
	}
	return $out;
}

add_action(
	'admin_enqueue_scripts',
	function ( $hook ) {
		if ( 'toplevel_page_kuzu-ayarlar' !== $hook ) {
			return;
		}
		wp_enqueue_media();
		wp_enqueue_script( 'kuzu-admin', KUZU_URI . 'admin.js', array( 'jquery', 'jquery-ui-sortable' ), KUZU_SURUM, true );
	}
);

function kuzu_ayarlar_sayfa() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	$a      = get_option( 'kuzu_ayarlar', array() );
	$anahtar_var = is_array( $a ) && ! empty( $a['google_anahtar'] );
	$durum  = get_option( 'kuzu_google_durum' );
	$ad     = function ( $k ) { return 'kuzu_ayarlar[' . $k . ']'; };
	$ids    = array_filter( array_map( 'absint', explode( ',', (string) kuzu_ayar( 'galeri' ) ) ) );
	?>
	<div class="wrap kuzu-ayar">
		<h1>Kuzu Lahmacun <small style="font-weight:400;color:#646970">tema <?php echo esc_html( KUZU_SURUM ); ?></small></h1>
		<?php settings_errors(); ?>
		<?php if ( isset( $_GET['yenilendi'] ) && is_array( $durum ) ) : // phpcs:ignore WordPress.Security.NonceVerification ?>
			<div class="notice notice-<?php echo ! empty( $durum['hata'] ) ? 'error' : 'success'; ?> is-dismissible"><p><?php echo esc_html( $durum['mesaj'] ); ?></p></div>
		<?php endif; ?>
		<p>Buradaki her şey ana sayfada görünür. Değiştirip en alttaki <b>Değişiklikleri kaydet</b> butonuna basın.
			<a href="<?php echo esc_url( home_url( '/' ) ); ?>" target="_blank" rel="noopener">Siteyi yeni sekmede aç →</a></p>
		<style>
			.kuzu-ayar .card{max-width:900px;padding:8px 22px 18px;margin-top:18px}
			.kuzu-ayar textarea{width:100%;font-family:Consolas,Monaco,monospace;font-size:13px}
			.kuzu-ayar input.regular-text{width:100%;max-width:600px}
			.kuzu-ayar .ipucu{color:#646970;margin:4px 0 10px}
			.kuzu-galeri{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0;padding:0;list-style:none}
			.kuzu-galeri li{width:150px;cursor:move;background:#f6f7f7;border:1px solid #dcdcde;border-radius:6px;overflow:hidden}
			.kuzu-galeri img{display:block;width:150px;height:96px;object-fit:cover}
			.kuzu-galeri span{display:block;padding:4px 6px;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
			.kuzu-durum{padding:8px 12px;border-left:4px solid #00a32a;background:#f6f7f7}
			.kuzu-durum.hata{border-left-color:#d63638}
			.kuzu-sip td{vertical-align:middle}
			.kuzu-sip input[type=text],.kuzu-sip input[type=url]{width:100%}
			.kuzu-sip .tutamak{cursor:move;color:#8c8f94;font-size:16px;letter-spacing:-2px;text-align:center}
			.kuzu-sip .sip-ikon-onizleme img{width:28px;height:28px;object-fit:contain;vertical-align:middle;margin-right:6px;border-radius:4px;background:#f0f0f1}
			.kuzu-sip input[type=color]{width:44px;height:30px;padding:0;border:1px solid #8c8f94;border-radius:4px}
			.kuzu-sip-ekle .button{margin:2px 0}
		</style>

		<form method="post" action="options.php">
			<?php settings_fields( 'kuzu_ayarlar_grubu' ); ?>

			<div class="card">
				<h2>İletişim</h2>
				<p><label>Telefon<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'telefon' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'telefon' ) ); ?>"></label></p>
				<p><label>Adres<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'adres' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'adres' ) ); ?>"></label></p>
				<p><label>Çalışma saatleri <span class="ipucu">(her satır ayrı görünür)</span><br>
					<textarea rows="3" name="<?php echo esc_attr( $ad( 'saatler' ) ); ?>"><?php echo esc_textarea( kuzu_ayar( 'saatler' ) ); ?></textarea></label></p>
			</div>

			<div class="card">
				<h2>Menü</h2>
				<p class="ipucu">Her satıra bir ürün: <code>Kategori | Ürün | Fiyat</code>. Aynı kategorideki ürünler aynı kartta toplanır;
					kartlar ilk yazıldıkları sırayla dizilir. Örnek: <code>Çorbalar | Mercimek | 120 ₺</code></p>
				<textarea rows="10" name="<?php echo esc_attr( $ad( 'menu' ) ); ?>"><?php echo esc_textarea( kuzu_ayar( 'menu' ) ); ?></textarea>
				<p><label>Menünün altındaki not<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'menu_notu' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'menu_notu' ) ); ?>"></label></p>
			</div>

			<div class="card" id="videolar">
				<h2>Videolar (YouTube Shorts)</h2>
				<p class="ipucu">Her satıra bir video: <code>YouTube linki | başlık</code>. Başlık isteğe bağlı. Shorts, normal video ve youtu.be linkleri olur.
					Örnek: <code>https://youtube.com/shorts/AbCdEfGhIjK | Fırından yeni çıktı</code>. Hiç video yoksa bölüm sitede görünmez.</p>
				<textarea rows="6" name="<?php echo esc_attr( $ad( 'videolar' ) ); ?>"><?php echo esc_textarea( kuzu_ayar( 'videolar' ) ); ?></textarea>
				<?php
				$hatali = array();
				foreach ( kuzu_satirlar( kuzu_ayar( 'videolar' ) ) as $sat ) {
					if ( ! kuzu_youtube_id( trim( explode( '|', $sat )[0] ) ) ) {
						$hatali[] = $sat;
					}
				}
				if ( $hatali ) {
					echo '<p class="kuzu-durum hata">Şu satırlarda YouTube linki tanınmadı: ' . esc_html( implode( ' · ', $hatali ) ) . '</p>';
				}
				?>
				<p><label>Bölüm başlığı<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'video_baslik' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'video_baslik' ) ); ?>"></label></p>
				<p><label>Başlığın altındaki yazı<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'video_yazi' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'video_yazi' ) ); ?>"></label></p>
			</div>

			<div class="card" id="siparis">
				<h2>Eve sipariş butonları</h2>
				<p class="ipucu">Her satır bir buton: <b>ikon</b>, <b>ad</b>, <b>link</b> ve <b>renk</b>. Soldaki tutamaktan sürükleyerek sıralayın.
					İkon için Medya'dan platformun logosunu seçin (arka planı şeffaf PNG en iyisi); ikon yoksa renkli nokta görünür.
					Ad ya da linki boş olan satır kaydedilmez. Hiç buton yoksa "Eve sipariş" alanı sitede görünmez.</p>
				<table class="widefat kuzu-sip">
					<thead><tr><th style="width:28px"></th><th style="width:150px">İkon</th><th>Ad</th><th>Link</th><th style="width:70px">Renk</th><th style="width:50px"></th></tr></thead>
					<tbody id="kuzu-sip-satirlar">
					<?php foreach ( kuzu_siparis_satirlari() as $i => $r ) { kuzu_sip_satir( 's' . $i, $r ); } ?>
					</tbody>
				</table>
				<template id="kuzu-sip-sablon"><?php kuzu_sip_satir( '__i__', array() ); ?></template>
				<p class="kuzu-sip-ekle">Ekle:
					<?php
					foreach ( array( array( 'Yemeksepeti', '#fa0050' ), array( 'Trendyol Yemek', '#f27a1a' ), array( 'Getir Yemek', '#5d3ebc' ), array( 'Migros Yemek', '#ff7e00' ), array( 'WhatsApp sipariş', '#25d366' ), array( '', '#d8342a' ) ) as $h ) {
						echo '<button type="button" class="button" data-ad="' . esc_attr( $h[0] ) . '" data-renk="' . esc_attr( $h[1] ) . '">+ ' . esc_html( $h[0] ? $h[0] : 'Boş satır' ) . '</button> ';
					}
					?>
				</p>
			</div>

			<div class="card">
				<h2>Merak edilenler (SSS)</h2>
				<p class="ipucu">Her soru bir blok: <b>ilk satır soru</b>, altındaki satırlar cevap. Sorular arasında <b>bir boş satır</b> bırakın.</p>
				<textarea rows="18" name="<?php echo esc_attr( $ad( 'sss' ) ); ?>"><?php echo esc_textarea( kuzu_ayar( 'sss' ) ); ?></textarea>
			</div>

			<div class="card">
				<h2>Kırmızı kayan bant</h2>
				<p class="ipucu">Her satıra bir kelime ya da kısa söz.</p>
				<textarea rows="6" name="<?php echo esc_attr( $ad( 'bant' ) ); ?>"><?php echo esc_textarea( kuzu_ayar( 'bant' ) ); ?></textarea>
			</div>

			<div class="card" id="galeri">
				<h2>Galeri</h2>
				<p class="ipucu">Fotoğraf seçmezseniz temayla gelen dört fotoğraf görünür. Sürükleyerek sıralayın.
					Fotoğrafın üstündeki büyük yazı Medya'daki <b>Başlık</b>, altındaki küçük yazı <b>Alt yazı (Caption)</b> alanıdır.</p>
				<input type="hidden" id="kuzu-galeri-ids" name="<?php echo esc_attr( $ad( 'galeri' ) ); ?>" value="<?php echo esc_attr( implode( ',', $ids ) ); ?>">
				<ul class="kuzu-galeri" id="kuzu-galeri">
					<?php foreach ( $ids as $id ) : ?>
						<li data-id="<?php echo (int) $id; ?>"><?php echo wp_get_attachment_image( $id, 'thumbnail' ); ?><span><?php echo esc_html( get_the_title( $id ) ); ?></span></li>
					<?php endforeach; ?>
				</ul>
				<p><button type="button" class="button button-primary" id="kuzu-galeri-sec">Fotoğraf seç</button>
					<button type="button" class="button" id="kuzu-galeri-temizle">Temanın fotoğraflarına dön</button></p>
				<p><label>Galeri başlığının altındaki yazı<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'galeri_yazi' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'galeri_yazi' ) ); ?>"></label></p>
			</div>

			<div class="card" id="google">
				<h2>Google yorumları</h2>
				<p class="ipucu">Yorumlar işletmenin Google kaydından günde bir kez kendiliğinden yenilenir; sitede yalnızca 5 yıldızlılar görünür.
					Anahtar girilmezse temayla gelen yorumlar görünür.</p>
				<p><label>Google Places API anahtarı<br>
					<input class="regular-text" type="password" autocomplete="new-password" name="<?php echo esc_attr( $ad( 'google_anahtar' ) ); ?>" value=""
						placeholder="<?php echo $anahtar_var ? 'Kayıtlı. Değiştirmek için yeni anahtarı yazın.' : 'AIza… ile başlayan anahtar'; ?>"></label></p>
				<?php if ( $anahtar_var ) : ?>
					<p><label><input type="checkbox" name="<?php echo esc_attr( $ad( 'google_anahtar_sil' ) ); ?>" value="1"> Kayıtlı anahtarı sil</label></p>
				<?php endif; ?>
				<details><summary>Gelişmiş: işletmenin Google kimliği (değiştirmeyin)</summary>
					<p><label>Yer kimliği (Place ID)<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'yer_id' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'yer_id' ) ); ?>"></label></p>
					<p><label>CID (rakip işletmeyle karışmasın diye kontrol edilir)<br><input class="regular-text" name="<?php echo esc_attr( $ad( 'cid' ) ); ?>" value="<?php echo esc_attr( kuzu_ayar( 'cid' ) ); ?>"></label></p>
				</details>
			</div>

			<?php submit_button( 'Değişiklikleri kaydet' ); ?>
		</form>

		<?php kuzu_kare_kontrol_karti(); ?>

		<div class="card">
			<h2>Yorumları şimdi yenile</h2>
			<?php if ( is_array( $durum ) ) : ?>
				<p class="kuzu-durum<?php echo ! empty( $durum['hata'] ) ? ' hata' : ''; ?>">
					<?php echo esc_html( wp_date( 'j F Y H:i', (int) $durum['zaman'] ) . ' · ' . $durum['mesaj'] ); ?></p>
			<?php endif; ?>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<input type="hidden" name="action" value="kuzu_yorum_yenile">
				<?php wp_nonce_field( 'kuzu_yorum_yenile' ); ?>
				<?php submit_button( 'Yorumları şimdi yenile', 'secondary', 'submit', false ); ?>
			</form>
		</div>
	</div>
	<?php
}

/**
 * Görsel kontrolü: sitenin kendi adresinden bir kare paketi indirilir ve boyutu beklenenle
 * karşılaştırılır. Barındırma ya da CDN görselleri küçültüyor veya başka biçime çeviriyorsa
 * video sitede bulanık görünür; panel bunu söyler.
 */
function kuzu_kare_kontrol_karti() {
	$m_yol = get_template_directory() . '/assets/sahne/frames/manifest.json';
	$u     = wp_upload_dir( null, false );
	if ( ! file_exists( $m_yol ) ) {
		$m_yol = $u['basedir'] . '/kuzu-sahne/frames/manifest.json';
	}
	$m = file_exists( $m_yol ) ? json_decode( (string) file_get_contents( $m_yol ), true ) : null;
	echo '<div class="card" id="kare-kontrol"><h2>Video kalitesi kontrolü</h2>';
	if ( ! is_array( $m ) || empty( $m['pack'] ) ) {
		echo '<p class="kuzu-durum hata">Kaydırma sahnesinin kareleri bulunamadı. Temayı tam zip ile yükleyin ya da kareler zip\'ini <code>wp-content/uploads/</code> içine açın.</p></div>';
		return;
	}
	$bek_w = (int) $m['pack']['w'] * (int) $m['pack']['cols'];
	$bek_h = (int) $m['pack']['h'] * (int) $m['pack']['rows'];
	$url   = kuzu_sahne_uri() . 'frames/paket-1.jpg?kontrol=' . time();
	$r     = wp_remote_get(
		$url,
		array(
			'timeout' => 15,
			'headers' => array(
				'User-Agent' => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
				'Accept'     => 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
			),
		)
	);
	if ( is_wp_error( $r ) || 200 !== (int) wp_remote_retrieve_response_code( $r ) ) {
		$neden = is_wp_error( $r ) ? $r->get_error_message() : 'HTTP ' . wp_remote_retrieve_response_code( $r );
		echo '<p class="kuzu-durum hata">Kare dosyası sitenin adresinden indirilemedi (' . esc_html( $neden ) . '). Bu kontrol yapılamadı.</p></div>';
		return;
	}
	$govde = (string) wp_remote_retrieve_body( $r );
	$boyut = @getimagesizefromstring( $govde ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
	$tip   = (string) wp_remote_retrieve_header( $r, 'content-type' );
	$kb    = round( strlen( $govde ) / 1024 );
	$yerel = (int) @filesize( str_replace( trailingslashit( get_template_directory_uri() ), trailingslashit( get_template_directory() ), strtok( $url, '?' ) ) ) / 1024; // phpcs:ignore
	if ( $boyut && (int) $boyut[0] === $bek_w && (int) $boyut[1] === $bek_h ) {
		echo '<p class="kuzu-durum">Kareler sunucudan tam boyutta geliyor (' . (int) $boyut[0] . '×' . (int) $boyut[1] . ', ' . esc_html( $tip ) . ', ' . (int) $kb . ' KB). Video, kaynağın verdiği en yüksek kalitede gösteriliyor.</p>';
	} else {
		$gelen = $boyut ? ( (int) $boyut[0] . '×' . (int) $boyut[1] ) : 'okunamadı';
		echo '<p class="kuzu-durum hata"><b>Sunucu kareleri değiştiriyor:</b> olması gereken ' . (int) $bek_w . '×' . (int) $bek_h . ', gelen ' . esc_html( $gelen ) . ' (' . esc_html( $tip ) . ', ' . (int) $kb . ' KB'
			. ( $yerel ? ', dosyanın kendisi ' . (int) $yerel . ' KB' : '' ) . '). Video bu yüzden bulanık görünür.</p>'
			. '<p>Çözüm: barındırmanın görsel optimizasyonunu (Hostinger: hPanel → Performans / CDN; LiteSpeed Cache → Görsel Optimizasyonu) kapatın ya da <code>wp-content/themes/kuzu-lahmacun/</code> klasörünü hariç tutun. Sonra CDN önbelleğini temizleyip bu sayfayı yenileyin.</p>';
	}
	echo '</div>';
}

/** Eve sipariş tablosunun bir satırı (şablon için $i = '__i__'). */
function kuzu_sip_satir( $i, $r ) {
	$n    = function ( $k ) use ( $i ) { return 'kuzu_ayarlar[siparis][' . $i . '][' . $k . ']'; };
	$ikon = (int) ( $r['ikon'] ?? 0 );
	$url  = $ikon ? wp_get_attachment_image_url( $ikon, 'thumbnail' ) : '';
	?>
	<tr class="kuzu-sip-satir">
		<td class="tutamak" title="Sürükleyerek sırala">⋮⋮</td>
		<td>
			<input type="hidden" class="sip-ikon-id" name="<?php echo esc_attr( $n( 'ikon' ) ); ?>" value="<?php echo $ikon ? (int) $ikon : ''; ?>">
			<span class="sip-ikon-onizleme"><?php echo $url ? '<img src="' . esc_url( $url ) . '" alt="">' : ''; ?></span>
			<button type="button" class="button button-small sip-ikon-sec"><?php echo $url ? 'Değiştir' : 'İkon seç'; ?></button>
			<button type="button" class="button-link sip-ikon-sil"<?php echo $url ? '' : ' hidden'; ?>>Kaldır</button>
		</td>
		<td><input type="text" class="sip-ad" name="<?php echo esc_attr( $n( 'ad' ) ); ?>" value="<?php echo esc_attr( $r['ad'] ?? '' ); ?>" placeholder="Yemeksepeti"></td>
		<td><input type="url" name="<?php echo esc_attr( $n( 'link' ) ); ?>" value="<?php echo esc_attr( $r['link'] ?? '' ); ?>" placeholder="https://"></td>
		<td><input type="color" class="sip-renk" name="<?php echo esc_attr( $n( 'renk' ) ); ?>" value="<?php echo esc_attr( ! empty( $r['renk'] ) ? $r['renk'] : '#d8342a' ); ?>"></td>
		<td><button type="button" class="button-link button-link-delete sip-sil">Sil</button></td>
	</tr>
	<?php
}
