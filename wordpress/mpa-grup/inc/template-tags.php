<?php
/**
 * Şablon yardımcıları.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Başlıklarda izin verilen etiketler (<br>, <em>, <strong>).
 *
 * @param string $text Metin.
 * @return string
 */
function mpa_kses_title( $text ) {
	return wp_kses(
		$text,
		array(
			'br'     => array(),
			'em'     => array(),
			'strong' => array(),
		)
	);
}

/**
 * Logo: Özelleştir'de logo yüklendiyse o, yoksa katalogdaki MPA Grup İnşaat logosu.
 *
 * @param string $variant 'dark' (açık zemin) veya 'light' (koyu zemin).
 */
function mpa_logo( $variant = 'dark' ) {
	$name = mpa_opt( 'company_name' );
	if ( 'dark' === $variant && has_custom_logo() ) {
		$logo_id = get_theme_mod( 'custom_logo' );
		echo wp_get_attachment_image(
			$logo_id,
			'full',
			false,
			array(
				'class' => 'brand__img',
				'alt'   => $name,
			)
		);
		return;
	}
	$file = 'light' === $variant ? 'logo-light.png' : 'logo.png';
	printf(
		'<img class="brand__img" src="%1$s" alt="%2$s" width="900" height="150">',
		esc_url( MPA_URI . '/assets/img/' . $file ),
		esc_attr( $name )
	);
}

/**
 * Telefon numarasından tel: bağlantısı.
 *
 * @param string $phone Telefon.
 * @return string
 */
function mpa_tel( $phone ) {
	return 'tel:' . preg_replace( '/[^0-9+]/', '', $phone );
}

/**
 * WhatsApp bağlantısı.
 *
 * @param string $number Numara.
 * @return string
 */
function mpa_whatsapp_url( $number ) {
	$digits = preg_replace( '/\D/', '', $number );
	if ( 0 === strpos( $digits, '0' ) ) {
		$digits = '9' . $digits;
	}
	return 'https://wa.me/' . $digits;
}

/**
 * İnşaat animasyonu aşamaları ve kaydırma ilerlemesindeki başlangıç noktaları.
 *
 * @return array
 */
function mpa_phases() {
	$starts = array( 0, 0.12, 0.2, 0.3, 0.6, 0.8, 0.93 );
	$phases = array();
	foreach ( $starts as $i => $start ) {
		$phases[] = array(
			'at'    => $start,
			'title' => mpa_opt( 'phase_' . ( $i + 1 ) . '_title' ),
			'text'  => mpa_opt( 'phase_' . ( $i + 1 ) . '_text' ),
		);
	}
	return $phases;
}

/**
 * Giriş videosu kaynakları: Özelleştir'den seçilen video, yoksa tema içindeki
 * assets/video/insaat.webm ve/veya insaat.mp4.
 *
 * @return array MIME türü => adres. Boşsa fotoğraf modu kullanılır.
 */
function mpa_hero_video_sources() {
	$id = (int) mpa_opt( 'hero_video' );
	if ( $id && wp_get_attachment_url( $id ) ) {
		return array( get_post_mime_type( $id ) => wp_get_attachment_url( $id ) );
	}
	$sources = array();
	foreach ( array( 'webm' => 'video/webm', 'mp4' => 'video/mp4' ) as $ext => $mime ) {
		if ( file_exists( MPA_DIR . '/assets/video/insaat.' . $ext ) ) {
			$sources[ $mime ] = MPA_URI . '/assets/video/insaat.' . $ext;
		}
	}
	return $sources;
}

/**
 * Bitmiş yapı görseli (giriş animasyonunun son karesi).
 *
 * @return string
 */
function mpa_hero_image_url() {
	$id = (int) mpa_opt( 'hero_image' );
	if ( $id ) {
		$url = wp_get_attachment_image_url( $id, 'full' );
		if ( $url ) {
			return $url;
		}
	}
	return MPA_URI . '/assets/img/insaat-son.jpg';
}

/**
 * Teknik çizim katmanı: tema görseli için hazır çizim; özel görselde boş döner ve
 * çizim görünümü CSS filtresiyle üretilir.
 *
 * @return string
 */
function mpa_hero_sketch_url() {
	return (int) mpa_opt( 'hero_image' ) ? '' : MPA_URI . '/assets/img/insaat-cizim.jpg';
}

/**
 * Numaralı başlık/metin grupları (hizmetler, ilkeler).
 *
 * @param string $prefix Ayar öneki.
 * @param int    $count  Adet.
 * @return array
 */
function mpa_items( $prefix, $count ) {
	$items = array();
	for ( $i = 1; $i <= $count; $i++ ) {
		$title = mpa_opt( $prefix . '_' . $i . '_title' );
		if ( '' === trim( (string) $title ) ) {
			continue;
		}
		$items[] = array(
			'title' => $title,
			'text'  => mpa_opt( $prefix . '_' . $i . '_text' ),
		);
	}
	return $items;
}

/**
 * Doldurulmuş rakam kutuları.
 *
 * @return array
 */
function mpa_stats() {
	$stats = array();
	for ( $i = 1; $i <= 4; $i++ ) {
		$value = trim( (string) mpa_opt( 'stat_' . $i . '_value' ) );
		if ( '' === $value ) {
			continue;
		}
		$stats[] = array(
			'value' => $value,
			'label' => mpa_opt( 'stat_' . $i . '_label' ),
		);
	}
	return $stats;
}

/**
 * Proje kartları için ortak veri: önce "Projeler" içeriği, yoksa katalogdaki projeler.
 *
 * @param int $limit Adet.
 * @return array
 */
function mpa_get_projects( $limit = 9 ) {
	$items = array();
	$query = new WP_Query(
		array(
			'post_type'      => 'mpa_proje',
			'posts_per_page' => $limit,
			'orderby'        => array(
				'menu_order' => 'ASC',
				'date'       => 'DESC',
			),
			'no_found_rows'  => true,
		)
	);

	foreach ( $query->posts as $post ) {
		$items[] = mpa_project_data( $post );
	}
	wp_reset_postdata();

	if ( $items ) {
		return $items;
	}

	foreach ( array_slice( mpa_seed_projects(), 0, $limit ) as $seed ) {
		$items[] = array(
			'title'    => $seed['title'],
			'url'      => '',
			'image'    => MPA_URI . '/assets/img/projeler/' . $seed['images'][0][0],
			'location' => $seed['location'],
			'category' => $seed['category'],
			'client'   => $seed['client'],
			'excerpt'  => $seed['excerpt'],
		);
	}
	return $items;
}

/**
 * Bir proje yazısının kart verisi.
 *
 * @param WP_Post $post Proje.
 * @return array
 */
function mpa_project_data( $post ) {
	return array(
		'title'    => get_the_title( $post ),
		'url'      => get_permalink( $post ),
		'image'    => get_the_post_thumbnail_url( $post, 'mpa-card' ),
		'location' => get_post_meta( $post->ID, '_mpa_location', true ),
		'category' => get_post_meta( $post->ID, '_mpa_category', true ),
		'client'   => get_post_meta( $post->ID, '_mpa_client', true ),
		'excerpt'  => has_excerpt( $post ) ? get_the_excerpt( $post ) : '',
	);
}

/**
 * Menü atanmadığında tek sayfa bağlantıları.
 */
function mpa_menu_fallback() {
	$home  = home_url( '/' );
	$links = array(
		'#hakkimizda' => __( 'Kurumsal', 'mpa-grup' ),
		'#hizmetler'  => __( 'Hizmetler', 'mpa-grup' ),
		'#projeler'   => __( 'Projeler', 'mpa-grup' ),
		'#iletisim'   => __( 'İletişim', 'mpa-grup' ),
	);
	echo '<ul class="menu">';
	foreach ( $links as $anchor => $label ) {
		printf( '<li><a href="%1$s">%2$s</a></li>', esc_url( $home . $anchor ), esc_html( $label ) );
	}
	echo '</ul>';
}

/**
 * Katalogdaki pafta üslubunda bölüm başlığı: turuncu küçük etiket, büyük başlık, kontur numara.
 *
 * @param string $eyebrow Üst etiket.
 * @param string $title   Başlık.
 * @param string $num     Kontur numara (ör. 01, P02).
 * @param string $tag     Başlık etiketi.
 */
function mpa_section_head( $eyebrow, $title, $num = '', $tag = 'h2' ) {
	echo '<header class="section-head">';
	printf( '<p class="eyebrow">%s</p>', esc_html( $eyebrow ) );
	printf( '<%1$s class="section-title">%2$s</%1$s>', tag_escape( $tag ), mpa_kses_title( $title ) );
	if ( $num ) {
		printf( '<span class="section-num" aria-hidden="true">%s</span>', esc_html( $num ) );
	}
	echo '</header>';
}

/**
 * Çizgisel ikonlar.
 *
 * @param string $name İkon adı.
 * @return string
 */
function mpa_icon( $name ) {
	$paths = array(
		'phone'     => '<path d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
		'mail'      => '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
		'pin'       => '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
		'clock'     => '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
		'arrow'     => '<path d="M5 12h14M13 6l6 6-6 6"/>',
		'down'      => '<path d="M12 5v14M6 13l6 6 6-6"/>',
		'whatsapp'  => '<path d="M4 20l1.3-3.9A8 8 0 1 1 8 19z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2z"/>',
		'instagram' => '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>',
		'linkedin'  => '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/>',
		'facebook'  => '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/>',
		'youtube'   => '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="m10 9 5 3-5 3z"/>',
		'concrete'  => '<path d="M3 21h18M5 21V9h14v12M5 13h14M5 17h14M9 9v12M15 9v12M7 9l5-5 5 5"/>',
		'facade'    => '<path d="M4 21V5l8-2 8 2v16M4 21h16M8 8h3v3H8zM13 8h3v3h-3zM8 14h3v3H8zM13 14h3v3h-3z"/>',
		'blueprint' => '<path d="M3 5h18v14H3z"/><path d="M7 15V9h6v6M13 12h4M15 9v6M3 9h2M3 13h2"/>',
		'check'     => '<path d="m5 12 4 4 10-10"/>',
	);
	$path = isset( $paths[ $name ] ) ? $paths[ $name ] : '';
	return '<svg class="icon icon-' . esc_attr( $name ) . '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' . $path . '</svg>';
}

/**
 * Sosyal medya bağlantıları.
 */
function mpa_social_links() {
	$out = '';
	foreach ( array( 'instagram', 'linkedin', 'facebook', 'youtube' ) as $network ) {
		$url = mpa_opt( $network );
		if ( $url ) {
			$out .= sprintf(
				'<a href="%1$s" target="_blank" rel="noopener" aria-label="%2$s">%3$s</a>',
				esc_url( $url ),
				esc_attr( ucfirst( $network ) ),
				mpa_icon( $network ) // phpcs:ignore WordPress.Security.EscapeOutput
			);
		}
	}
	if ( $out ) {
		echo '<div class="social">' . $out . '</div>'; // phpcs:ignore WordPress.Security.EscapeOutput
	}
}
