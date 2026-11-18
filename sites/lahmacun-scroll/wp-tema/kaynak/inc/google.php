<?php
/**
 * Google yorumları: işletmenin kendi Google kaydından günde bir kez çekilir (Places API, New).
 *
 * Doğru işletme: "Kuzu Lahmacun" adında başka bir işletme daha var. Gelen kaydın Google
 * Haritalar adresindeki CID panelde yazılı CID ile aynı değilse hiçbir şey kaydedilmez.
 * Çekim başarısız olursa sitede son başarılı yorumlar kalır.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function kuzu_google_yenile() {
	$a     = get_option( 'kuzu_ayarlar', array() );
	$key   = is_array( $a ) && ! empty( $a['google_anahtar'] ) ? $a['google_anahtar'] : '';
	$yer   = kuzu_ayar( 'yer_id' );
	$cid   = kuzu_ayar( 'cid' );
	$durum = function ( $mesaj, $hata ) {
		update_option( 'kuzu_google_durum', array( 'zaman' => time(), 'mesaj' => $mesaj, 'hata' => $hata ), false );
		return $mesaj;
	};

	if ( ! $key ) {
		return $durum( 'Google API anahtarı girilmemiş; temayla gelen yorumlar gösteriliyor.', true );
	}
	$r = wp_remote_get(
		'https://places.googleapis.com/v1/places/' . rawurlencode( $yer ) . '?languageCode=tr',
		array(
			'timeout' => 20,
			'headers' => array(
				'X-Goog-Api-Key'   => $key,
				'X-Goog-FieldMask' => 'id,displayName,googleMapsUri,reviews',
			),
		)
	);
	if ( is_wp_error( $r ) ) {
		return $durum( 'Google\'a bağlanılamadı: ' . $r->get_error_message(), true );
	}
	$kod = (int) wp_remote_retrieve_response_code( $r );
	$y   = json_decode( (string) wp_remote_retrieve_body( $r ), true );
	if ( 200 !== $kod || ! is_array( $y ) ) {
		$m = is_array( $y ) && isset( $y['error']['message'] ) ? $y['error']['message'] : 'bilinmeyen hata';
		return $durum( "Google hata verdi ($kod): $m", true );
	}
	if ( false === strpos( (string) ( $y['googleMapsUri'] ?? '' ), 'cid=' . $cid ) ) {
		return $durum( 'Gelen kayıt işletmenin kaydıyla eşleşmedi; yorumlar güncellenmedi.', true );
	}

	$yorumlar = array();
	foreach ( (array) ( $y['reviews'] ?? array() ) as $v ) {
		$at         = $v['authorAttribution'] ?? array();
		$metin      = $v['originalText']['text'] ?? ( $v['text']['text'] ?? '' );
		$yorumlar[] = array(
			'author' => $at['displayName'] ?? '',
			'uri'    => $at['uri'] ?? '',
			'photo'  => $at['photoUri'] ?? '',
			'rating' => (int) ( $v['rating'] ?? 0 ),
			'date'   => $v['publishTime'] ?? '',
			'text'   => $metin,
		);
	}
	if ( ! $yorumlar ) {
		return $durum( 'Google yorum döndürmedi; önceki yorumlar duruyor.', true );
	}
	update_option( 'kuzu_google', array( 'reviews' => $yorumlar, 'zaman' => time() ), false );
	$bes = count( array_filter( $yorumlar, function ( $r ) { return 5 === $r['rating']; } ) );
	return $durum( count( $yorumlar ) . " yorum alındı, $bes tanesi 5 yıldızlı (sitede bunlar görünür).", false );
}

// Günde bir kez kendiliğinden.
add_action( 'kuzu_yorum_yenile', 'kuzu_google_yenile' );
add_action(
	'init',
	function () {
		if ( ! wp_next_scheduled( 'kuzu_yorum_yenile' ) ) {
			wp_schedule_event( time() + HOUR_IN_SECONDS, 'daily', 'kuzu_yorum_yenile' );
		}
	}
);
add_action(
	'switch_theme',
	function () {
		wp_clear_scheduled_hook( 'kuzu_yorum_yenile' );
	}
);

// Paneldeki "Yorumları şimdi yenile" butonu.
add_action(
	'admin_post_kuzu_yorum_yenile',
	function () {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( 'Yetkiniz yok.' );
		}
		check_admin_referer( 'kuzu_yorum_yenile' );
		kuzu_google_yenile();
		wp_safe_redirect( admin_url( 'admin.php?page=kuzu-ayarlar&yenilendi=1#google' ) );
		exit;
	}
);
