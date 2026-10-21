<?php
/**
 * MPA Grup İnşaat — tema fonksiyonları.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'MPA_VERSION', '1.0.0' );
define( 'MPA_DIR', get_template_directory() );
define( 'MPA_URI', get_template_directory_uri() );

require MPA_DIR . '/inc/defaults.php';
require MPA_DIR . '/inc/template-tags.php';
require MPA_DIR . '/inc/post-types.php';
require MPA_DIR . '/inc/customizer.php';
require MPA_DIR . '/inc/contact.php';
require MPA_DIR . '/inc/setup-content.php';

/**
 * Tema destekleri ve menü konumları.
 */
function mpa_setup() {
	load_theme_textdomain( 'mpa-grup', MPA_DIR . '/languages' );

	add_theme_support( 'title-tag' );
	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script', 'navigation-widgets' ) );
	add_theme_support(
		'custom-logo',
		array(
			'height'      => 150,
			'width'       => 900,
			'flex-height' => true,
			'flex-width'  => true,
		)
	);

	register_nav_menus(
		array(
			'primary' => __( 'Ana Menü', 'mpa-grup' ),
			'footer'  => __( 'Alt Menü', 'mpa-grup' ),
		)
	);

	add_image_size( 'mpa-card', 960, 720, true );
}
add_action( 'after_setup_theme', 'mpa_setup' );

/**
 * Stil ve betikler.
 */
function mpa_assets() {
	wp_enqueue_style(
		'mpa-fonts',
		'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@300;500;600;700;800&display=swap',
		array(),
		null
	);
	wp_enqueue_style( 'mpa-style', get_stylesheet_uri(), array(), MPA_VERSION );

	$accent = sanitize_hex_color( mpa_opt( 'accent_color' ) );
	if ( $accent ) {
		wp_add_inline_style( 'mpa-style', ':root{--accent:' . $accent . ';}' );
	}

	wp_enqueue_script(
		'mpa-main',
		MPA_URI . '/assets/js/main.js',
		array(),
		MPA_VERSION,
		array(
			'in_footer' => true,
			'strategy'  => 'defer',
		)
	);
}
add_action( 'wp_enqueue_scripts', 'mpa_assets' );

/**
 * Google Fonts için ön bağlantı.
 *
 * @param array  $urls          URL listesi.
 * @param string $relation_type İlişki türü.
 * @return array
 */
function mpa_resource_hints( $urls, $relation_type ) {
	if ( 'preconnect' === $relation_type ) {
		$urls[] = 'https://fonts.googleapis.com';
		$urls[] = array(
			'href'        => 'https://fonts.gstatic.com',
			'crossorigin' => 'anonymous',
		);
	}
	return $urls;
}
add_filter( 'wp_resource_hints', 'mpa_resource_hints', 10, 2 );

/**
 * JS çalışıyorsa animasyonlar başlangıç durumundan açılır; çalışmıyorsa bitmiş bina görünür.
 */
function mpa_js_class() {
	echo "<script>document.documentElement.classList.add('js');</script>\n";
}
add_action( 'wp_head', 'mpa_js_class', 1 );

/**
 * Site simgesi tanımlı değilse logodaki MPA işaretini kullan.
 */
function mpa_fallback_favicon() {
	if ( ! has_site_icon() ) {
		echo '<link rel="icon" type="image/png" href="' . esc_url( MPA_URI . '/assets/img/mark.png' ) . '">' . "\n";
	}
	echo '<meta name="theme-color" content="#0f161b">' . "\n";
}
add_action( 'wp_head', 'mpa_fallback_favicon', 5 );

/**
 * Ön sayfa için gövde sınıfı.
 *
 * @param array $classes Sınıflar.
 * @return array
 */
function mpa_body_class( $classes ) {
	if ( is_front_page() ) {
		$classes[] = 'mpa-onepage';
	}
	return $classes;
}
add_filter( 'body_class', 'mpa_body_class' );

/**
 * Özet uzunluğu.
 *
 * @return int
 */
function mpa_excerpt_length() {
	return 26;
}
add_filter( 'excerpt_length', 'mpa_excerpt_length' );

/**
 * Tema içeriği Türkçe olduğundan sayfa dili Türkçe işaretlenir; böylece büyük harfe
 * çevrilen başlıklarda "i" doğru şekilde "İ" olur (MİMARİ İMALAT).
 *
 * @param string $output Dil öznitelikleri.
 * @return string
 */
function mpa_language_attributes( $output ) {
	if ( 0 === strpos( get_locale(), 'tr' ) ) {
		return $output;
	}
	return preg_replace( '/lang="[^"]*"/', 'lang="tr"', $output );
}
add_filter( 'language_attributes', 'mpa_language_attributes' );
