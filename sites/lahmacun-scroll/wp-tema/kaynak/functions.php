<?php
/**
 * Kuzu Lahmacun teması.
 *
 * Ana sayfa (front-page.php) kaydırmaya bağlı lezzet şovudur; menü, iletişim, merak edilenler,
 * kayan bant, galeri ve Google yorumları yönetim panelindeki "Kuzu Lahmacun" sayfasından düzenlenir.
 * Diğer sayfalar (gizlilik politikası vb.) index.php ile markanın sade görünümünde açılır.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'KUZU_SURUM', wp_get_theme( get_template() )->get( 'Version' ) );
define( 'KUZU_URI', trailingslashit( get_template_directory_uri() ) . 'assets/' );

require_once __DIR__ . '/inc/varsayilan.php';
require_once __DIR__ . '/inc/ayarlar.php';
require_once __DIR__ . '/inc/google.php';
require_once __DIR__ . '/inc/bolumler.php';
require_once __DIR__ . '/inc/ozellestir.php';

add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'title-tag' );
		add_theme_support( 'html5', array( 'script', 'style', 'gallery', 'caption', 'search-form', 'comment-form', 'comment-list' ) );
		add_theme_support( 'post-thumbnails' );
	}
);

/**
 * Kaydırma sahnesinin kareleri: temanın içinde; tema zip'i büyük geldiği için hafif sürüm
 * yüklendiyse wp-content/uploads/kuzu-sahne/ klasöründe.
 */
function kuzu_sahne_uri() {
	if ( file_exists( get_template_directory() . '/assets/sahne/frames/manifest.json' ) ) {
		return KUZU_URI . 'sahne/';
	}
	$u = wp_upload_dir( null, false );
	if ( file_exists( $u['basedir'] . '/kuzu-sahne/frames/manifest.json' ) ) {
		return trailingslashit( set_url_scheme( $u['baseurl'] ) ) . 'kuzu-sahne/';
	}
	return KUZU_URI . 'sahne/';
}

add_action(
	'wp_enqueue_scripts',
	function () {
		wp_enqueue_style( 'kuzu-fontlar', 'https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,400..900;1,62..125,400..900&family=Kaushan+Script&display=swap', array(), null );
		wp_enqueue_style( 'kuzu-site', KUZU_URI . 'site.css', array( 'kuzu-fontlar' ), KUZU_SURUM );

		if ( is_front_page() ) {
			wp_enqueue_script( 'lenis', 'https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js', array(), '1.1.13', true );
			wp_enqueue_script( 'kuzu-site', KUZU_URI . 'site.js', array( 'lenis' ), KUZU_SURUM, true );
			wp_add_inline_script( 'kuzu-site', 'window.KUZU_TEMA=' . wp_json_encode( array( 'sahne' => kuzu_sahne_uri() ) ) . ';', 'before' );
			// Ana sayfa blok düzenleyici stillerini kullanmaz; ilk açılış hafif kalsın.
			foreach ( array( 'wp-block-library', 'wp-block-library-theme', 'classic-theme-styles', 'global-styles' ) as $h ) {
				wp_dequeue_style( $h );
			}
		} else {
			wp_enqueue_style( 'kuzu-ic', KUZU_URI . 'ic.css', array( 'kuzu-site' ), KUZU_SURUM );
		}
	},
	20
);

// Emoji betiği ana sayfada gereksiz bir istek.
add_action(
	'init',
	function () {
		remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
		remove_action( 'wp_print_styles', 'print_emoji_styles' );
	}
);

/**
 * Sürüm geçişleri: tema güncellenince bir kez çalışır.
 * 1.1.0: sitede "Lahm-ı Acîn" yerine her yerde "Lahmacun" (panelde kaydedilmiş yazılar dahil).
 */
add_action(
	'init',
	function () {
		if ( get_option( 'kuzu_tema_surum' ) === KUZU_SURUM ) {
			return;
		}
		$a = get_option( 'kuzu_ayarlar' );
		if ( is_array( $a ) ) {
			foreach ( $a as $k => $v ) {
				if ( is_string( $v ) && 'google_anahtar' !== $k ) {
					$a[ $k ] = str_replace( array( 'Lahm-ı Acîn', 'LAHM-I ACÎN', 'lahm-ı acîn', 'Lahm-ı acîn' ), array( 'Lahmacun', 'LAHMACUN', 'lahmacun', 'Lahmacun' ), $v );
				}
			}
			update_option( 'kuzu_ayarlar', $a );
		}
		update_option( 'kuzu_tema_surum', KUZU_SURUM );
	}
);
