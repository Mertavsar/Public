<?php
/**
 * İçerik türleri: Projeler ve iletişim formundan gelen Mesajlar.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * İçerik türlerini kaydet.
 */
function mpa_register_post_types() {
	register_post_type(
		'mpa_proje',
		array(
			'labels'       => array(
				'name'          => __( 'Projeler', 'mpa-grup' ),
				'singular_name' => __( 'Proje', 'mpa-grup' ),
				'add_new'       => __( 'Yeni Proje', 'mpa-grup' ),
				'add_new_item'  => __( 'Yeni Proje Ekle', 'mpa-grup' ),
				'edit_item'     => __( 'Projeyi Düzenle', 'mpa-grup' ),
				'all_items'     => __( 'Tüm Projeler', 'mpa-grup' ),
				'view_item'     => __( 'Projeyi Görüntüle', 'mpa-grup' ),
			),
			'public'       => true,
			'has_archive'  => 'projeler',
			'rewrite'      => array( 'slug' => 'projeler' ),
			'menu_icon'    => 'dashicons-building',
			'menu_position' => 5,
			'show_in_rest' => true,
			'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt', 'page-attributes' ),
		)
	);

	register_post_type(
		'mpa_mesaj',
		array(
			'labels'          => array(
				'name'          => __( 'Gelen Mesajlar', 'mpa-grup' ),
				'singular_name' => __( 'Mesaj', 'mpa-grup' ),
				'edit_item'     => __( 'Mesaj', 'mpa-grup' ),
				'all_items'     => __( 'Gelen Mesajlar', 'mpa-grup' ),
				'not_found'     => __( 'Henüz mesaj yok.', 'mpa-grup' ),
			),
			'public'          => false,
			'show_ui'         => true,
			'menu_icon'       => 'dashicons-email-alt',
			'menu_position'   => 26,
			'supports'        => array( 'title' ),
			'capability_type' => 'post',
			'capabilities'    => array( 'create_posts' => 'do_not_allow' ),
			'map_meta_cap'    => true,
		)
	);
}
add_action( 'init', 'mpa_register_post_types' );

/**
 * Proje bilgi kutusu.
 */
function mpa_project_meta_box() {
	add_meta_box( 'mpa_project_info', __( 'Proje Bilgileri', 'mpa-grup' ), 'mpa_project_meta_box_html', 'mpa_proje', 'side', 'high' );
	add_meta_box( 'mpa_message_info', __( 'Mesaj Detayı', 'mpa-grup' ), 'mpa_message_meta_box_html', 'mpa_mesaj', 'normal', 'high' );
}
add_action( 'add_meta_boxes', 'mpa_project_meta_box' );

/**
 * Proje alanları.
 *
 * @param WP_Post $post Proje.
 */
function mpa_project_meta_box_html( $post ) {
	wp_nonce_field( 'mpa_project_meta', 'mpa_project_nonce' );
	$fields = array(
		'_mpa_client'   => __( 'İşveren', 'mpa-grup' ),
		'_mpa_location' => __( 'Konum (ör. Ankara / İvedik)', 'mpa-grup' ),
		'_mpa_category' => __( 'Kategori (ör. Otel, Kamu · Araştırma)', 'mpa-grup' ),
	);
	foreach ( $fields as $key => $label ) {
		printf(
			'<p><label for="%1$s"><strong>%2$s</strong></label><br><input type="text" class="widefat" id="%1$s" name="%1$s" value="%3$s"></p>',
			esc_attr( $key ),
			esc_html( $label ),
			esc_attr( get_post_meta( $post->ID, $key, true ) )
		);
	}
	echo '<p class="description">' . esc_html__( 'Kart görseli için "Öne çıkan görsel" ekleyin. Sıralama: Sayfa Özellikleri > Sıra.', 'mpa-grup' ) . '</p>';
}

/**
 * Proje alanlarını kaydet.
 *
 * @param int $post_id Proje kimliği.
 */
function mpa_save_project_meta( $post_id ) {
	if ( ! isset( $_POST['mpa_project_nonce'] ) || ! wp_verify_nonce( sanitize_key( $_POST['mpa_project_nonce'] ), 'mpa_project_meta' ) ) {
		return;
	}
	if ( ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) || ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	foreach ( array( '_mpa_client', '_mpa_location', '_mpa_category' ) as $key ) {
		if ( isset( $_POST[ $key ] ) ) {
			update_post_meta( $post_id, $key, sanitize_text_field( wp_unslash( $_POST[ $key ] ) ) );
		}
	}
}
add_action( 'save_post_mpa_proje', 'mpa_save_project_meta' );

/**
 * Mesaj detayını salt okunur göster.
 *
 * @param WP_Post $post Mesaj.
 */
function mpa_message_meta_box_html( $post ) {
	$rows = array(
		__( 'Ad Soyad', 'mpa-grup' )   => get_post_meta( $post->ID, '_mpa_name', true ),
		__( 'Telefon', 'mpa-grup' )    => get_post_meta( $post->ID, '_mpa_phone', true ),
		__( 'E-posta', 'mpa-grup' )    => get_post_meta( $post->ID, '_mpa_email', true ),
		__( 'Konu', 'mpa-grup' )       => get_post_meta( $post->ID, '_mpa_subject', true ),
		__( 'Tarih', 'mpa-grup' )      => get_the_date( 'd.m.Y H:i', $post ),
	);
	echo '<table class="widefat striped"><tbody>';
	foreach ( $rows as $label => $value ) {
		printf( '<tr><th style="width:140px">%1$s</th><td>%2$s</td></tr>', esc_html( $label ), esc_html( $value ) );
	}
	echo '</tbody></table>';
	echo '<h4>' . esc_html__( 'Mesaj', 'mpa-grup' ) . '</h4>';
	echo '<div style="white-space:pre-wrap;background:#f6f7f7;padding:12px;border-radius:4px">' . esc_html( get_post_meta( $post->ID, '_mpa_message', true ) ) . '</div>';
}

/**
 * Mesaj listesi sütunları.
 *
 * @param array $columns Sütunlar.
 * @return array
 */
function mpa_message_columns( $columns ) {
	return array(
		'cb'        => $columns['cb'],
		'title'     => __( 'Gönderen', 'mpa-grup' ),
		'mpa_phone' => __( 'Telefon', 'mpa-grup' ),
		'mpa_email' => __( 'E-posta', 'mpa-grup' ),
		'date'      => __( 'Tarih', 'mpa-grup' ),
	);
}
add_filter( 'manage_mpa_mesaj_posts_columns', 'mpa_message_columns' );

/**
 * Mesaj listesi hücreleri.
 *
 * @param string $column  Sütun.
 * @param int    $post_id Mesaj.
 */
function mpa_message_column_content( $column, $post_id ) {
	if ( 'mpa_phone' === $column ) {
		echo esc_html( get_post_meta( $post_id, '_mpa_phone', true ) );
	} elseif ( 'mpa_email' === $column ) {
		echo esc_html( get_post_meta( $post_id, '_mpa_email', true ) );
	}
}
add_action( 'manage_mpa_mesaj_posts_custom_column', 'mpa_message_column_content', 10, 2 );

/**
 * Projeler sayfasında sıralama ana sayfayla aynı: önce "Sıra" alanı, sonra tarih.
 *
 * @param WP_Query $query Sorgu.
 */
function mpa_project_archive_order( $query ) {
	if ( ! is_admin() && $query->is_main_query() && $query->is_post_type_archive( 'mpa_proje' ) ) {
		$query->set(
			'orderby',
			array(
				'menu_order' => 'ASC',
				'date'       => 'DESC',
			)
		);
	}
}
add_action( 'pre_get_posts', 'mpa_project_archive_order' );

/**
 * Proje içeriğindeki görsellerin adresini her gösterimde ekin güncel adresinden üretir.
 * Kurulumdan sonra alan adı ya da http/https değişse de (ör. Hostinger geçici adresinden
 * mpagrup.com'a geçiş) galeri fotoğrafları kırılmaz.
 *
 * @param string $content İçerik.
 * @return string
 */
function mpa_refresh_image_urls( $content ) {
	if ( ! is_singular( 'mpa_proje' ) && ! is_page() ) {
		return $content;
	}
	return preg_replace_callback(
		'/<img\b[^>]*>/i',
		static function ( $m ) {
			$tag = $m[0];
			if ( ! preg_match( '/wp-image-(\d+)/', $tag, $id ) ) {
				return $tag;
			}
			$url = wp_get_attachment_image_url( (int) $id[1], 'large' );
			if ( ! $url ) {
				return $tag;
			}
			$tag = preg_replace( '/\ssrcset="[^"]*"/i', '', $tag );
			$tag = preg_replace( '/\ssizes="[^"]*"/i', '', $tag );
			return preg_replace( '/\ssrc="[^"]*"/i', ' src="' . esc_url( $url ) . '"', $tag, 1 );
		},
		$content
	);
}
add_filter( 'the_content', 'mpa_refresh_image_urls', 8 );

/**
 * Kapak fotoğrafı proje kartlarında ve "Sıradaki proje" alanında kullanılır; katalogdan
 * alındığı için galerideki ilk fotoğrafla neredeyse aynıdır, galeride tekrar edilmez.
 *
 * @param string $content Yazı içeriği.
 * @return string
 */
function mpa_skip_cover_in_gallery( $content ) {
	if ( ! is_singular( 'mpa_proje' ) || ! has_post_thumbnail() ) {
		return $content;
	}
	$id = (int) get_post_thumbnail_id();
	return preg_replace(
		'#(?:<!-- wp:image \{[^}]*\} -->\s*)?<figure class="wp-block-image[^"]*">(?:(?!</figure>).)*?\bwp-image-' . $id . '\b(?:(?!</figure>).)*</figure>(?:\s*<!-- /wp:image -->)?#s',
		'',
		$content
	);
}
add_filter( 'the_content', 'mpa_skip_cover_in_gallery', 7 );
