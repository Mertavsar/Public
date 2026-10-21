<?php
/**
 * Kurumsal sayfalar: Kurumsal, Hizmetler, İletişim. Tema bunları bir kez oluşturur;
 * görünümleri page-{slug}.php şablonlarından gelir. Projeler, "Projeler" içerik
 * türünün arşivi (/projeler/) ve her projenin kendi sayfasıdır.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Tema sayfaları: kısa ad => başlık.
 *
 * @return array
 */
function mpa_core_pages() {
	return array(
		'kurumsal'  => __( 'Kurumsal', 'mpa-grup' ),
		'hizmetler' => __( 'Hizmetler', 'mpa-grup' ),
		'iletisim'  => __( 'İletişim', 'mpa-grup' ),
	);
}

/**
 * Eksik tema sayfalarını bir kez oluştur.
 */
function mpa_create_core_pages() {
	if ( get_option( 'mpa_pages_v1' ) ) {
		return;
	}
	foreach ( mpa_core_pages() as $slug => $title ) {
		if ( get_page_by_path( $slug ) ) {
			continue;
		}
		wp_insert_post(
			array(
				'post_type'    => 'page',
				'post_status'  => 'publish',
				'post_title'   => $title,
				'post_name'    => $slug,
				'post_content' => '',
			)
		);
	}
	update_option( 'mpa_pages_v1', 1 );
}
add_action( 'init', 'mpa_create_core_pages', 20 );

/**
 * Sitedeki ana bağlantılar. Sayfa silinmişse ana sayfadaki ilgili bölüme düşer.
 *
 * @param string $key kurumsal | hizmetler | projeler | iletisim.
 * @return string
 */
function mpa_url( $key ) {
	if ( 'projeler' === $key ) {
		$archive = get_post_type_archive_link( 'mpa_proje' );
		return $archive ? $archive : home_url( '/#projeler' );
	}
	$page = get_page_by_path( $key );
	if ( $page && 'publish' === $page->post_status ) {
		return get_permalink( $page );
	}
	$anchors = array(
		'kurumsal'  => 'hakkimizda',
		'hizmetler' => 'hizmetler',
		'iletisim'  => 'iletisim',
	);
	return home_url( '/#' . ( isset( $anchors[ $key ] ) ? $anchors[ $key ] : '' ) );
}

/**
 * Menüde şu an bulunulan bölüm.
 *
 * @param string $key Bağlantı anahtarı.
 * @return bool
 */
function mpa_is_current( $key ) {
	if ( 'projeler' === $key ) {
		return is_post_type_archive( 'mpa_proje' ) || is_singular( 'mpa_proje' );
	}
	return is_page( $key );
}

/**
 * Sayfa düzenleyicisine yazılan içerik varsa şablonun içinde göster.
 */
function mpa_page_content() {
	if ( '' === trim( get_the_content() ) ) {
		return;
	}
	echo '<section class="section section--white"><div class="container container--narrow entry"><div class="entry__content">';
	the_content();
	echo '</div></div></section>';
}
