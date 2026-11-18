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
	foreach ( array( 'telefon', 'adres', 'menu_notu', 'galeri_yazi', 'yer_id', 'cid' ) as $k ) {
		$out[ $k ] = sanitize_text_field( $g[ $k ] ?? '' );
	}
	foreach ( array( 'saatler', 'menu', 'bant' ) as $k ) {
		$out[ $k ] = sanitize_textarea_field( $g[ $k ] ?? '' );
	}
	$out['sss']    = wp_kses( $g['sss'] ?? '', array( 'a' => array( 'href' => true, 'target' => true, 'rel' => true ), 'b' => array(), 'strong' => array(), 'em' => array(), 'br' => array() ) );
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
