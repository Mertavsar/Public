<?php
/**
 * Tema etkinleştirildiğinde katalogdaki referans projeleri "Projeler" altına ekler,
 * böylece site ilk açılışta dolu görünür. Her proje yalnızca bir kez eklenir.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Tema etkinleştirme.
 */
function mpa_after_switch_theme() {
	mpa_register_post_types();
	mpa_import_seed_projects();
	mpa_create_core_pages();
	flush_rewrite_rules();
	set_transient( 'mpa_activated', 1, HOUR_IN_SECONDS );
}
add_action( 'after_switch_theme', 'mpa_after_switch_theme' );

/**
 * Referans projeleri ve görsellerini ekle.
 */
function mpa_import_seed_projects() {
	if ( get_option( 'mpa_seed_imported' ) ) {
		return;
	}

	require_once ABSPATH . 'wp-admin/includes/image.php';

	foreach ( mpa_seed_projects() as $order => $seed ) {
		$existing = get_posts(
			array(
				'post_type'   => 'mpa_proje',
				'name'        => $seed['slug'],
				'post_status' => 'any',
				'numberposts' => 1,
				'fields'      => 'ids',
			)
		);
		if ( $existing ) {
			continue;
		}

		$post_id = wp_insert_post(
			array(
				'post_type'    => 'mpa_proje',
				'post_status'  => 'publish',
				'post_title'   => $seed['title'],
				'post_name'    => $seed['slug'],
				'post_excerpt' => $seed['excerpt'],
				'menu_order'   => $order,
			)
		);
		if ( ! $post_id || is_wp_error( $post_id ) ) {
			continue;
		}

		update_post_meta( $post_id, '_mpa_client', $seed['client'] );
		update_post_meta( $post_id, '_mpa_location', $seed['location'] );
		update_post_meta( $post_id, '_mpa_category', $seed['category'] );

		$gallery = '';
		foreach ( $seed['images'] as $i => $image ) {
			$attachment_id = mpa_import_theme_image( $image[0], $image[1], $post_id );
			if ( ! $attachment_id ) {
				continue;
			}
			if ( 0 === $i ) {
				set_post_thumbnail( $post_id, $attachment_id );
			}
			$src      = wp_get_attachment_image_url( $attachment_id, 'large' );
			$gallery .= sprintf(
				'<!-- wp:image {"id":%1$d,"sizeSlug":"large","linkDestination":"none"} --><figure class="wp-block-image size-large"><img src="%2$s" alt="%3$s" class="wp-image-%1$d"/><figcaption class="wp-element-caption">%3$s</figcaption></figure><!-- /wp:image -->',
				$attachment_id,
				esc_url( $src ),
				esc_attr( $image[1] )
			);
		}

		$content = '<!-- wp:paragraph --><p>' . esc_html( $seed['content'] ) . '</p><!-- /wp:paragraph -->';
		if ( $gallery ) {
			$content .= '<!-- wp:gallery {"linkTo":"none"} --><figure class="wp-block-gallery has-nested-images columns-default is-cropped">' . $gallery . '</figure><!-- /wp:gallery -->';
		}
		wp_update_post(
			array(
				'ID'           => $post_id,
				'post_content' => $content,
			)
		);
	}

	update_option( 'mpa_seed_imported', 1 );
}

/**
 * Tema klasöründeki bir görseli ortam kütüphanesine kopyala.
 *
 * @param string $file    Dosya adı (assets/img/projeler altında).
 * @param string $title   Başlık / alternatif metin.
 * @param int    $post_id Bağlı yazı.
 * @return int Ek kimliği, başarısızsa 0.
 */
function mpa_import_theme_image( $file, $title, $post_id ) {
	$path = MPA_DIR . '/assets/img/projeler/' . $file;
	if ( ! is_readable( $path ) ) {
		return 0;
	}
	$upload = wp_upload_bits( $file, null, file_get_contents( $path ) ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	if ( ! empty( $upload['error'] ) ) {
		return 0;
	}
	$attachment_id = wp_insert_attachment(
		array(
			'post_mime_type' => 'image/jpeg',
			'post_title'     => $title,
			'post_status'    => 'inherit',
		),
		$upload['file'],
		$post_id
	);
	if ( ! $attachment_id || is_wp_error( $attachment_id ) ) {
		return 0;
	}
	wp_update_attachment_metadata( $attachment_id, wp_generate_attachment_metadata( $attachment_id, $upload['file'] ) );
	update_post_meta( $attachment_id, '_wp_attachment_image_alt', $title );
	return $attachment_id;
}

/**
 * Etkinleştirme sonrası yönlendirme notu.
 */
function mpa_activation_notice() {
	if ( ! get_transient( 'mpa_activated' ) || ! current_user_can( 'edit_theme_options' ) ) {
		return;
	}
	delete_transient( 'mpa_activated' );
	printf(
		'<div class="notice notice-success is-dismissible"><p><strong>%1$s</strong> %2$s <a href="%3$s">%4$s</a> · <a href="%5$s">%6$s</a></p></div>',
		esc_html__( 'MPA Grup teması etkin.', 'mpa-grup' ),
		esc_html__( 'Katalogdaki referans projeler eklendi. Telefon, adres ve e-postayı girmeyi unutmayın:', 'mpa-grup' ),
		esc_url( admin_url( 'customize.php?autofocus[panel]=mpa_panel' ) ),
		esc_html__( 'Özelleştir > MPA Grup', 'mpa-grup' ),
		esc_url( admin_url( 'edit.php?post_type=mpa_proje' ) ),
		esc_html__( 'Projeler', 'mpa-grup' )
	);
}
add_action( 'admin_notices', 'mpa_activation_notice' );

/**
 * Önceki sürümle eklenmiş proje içeriklerindeki " — " ayraçlarını virgüle çevirir (bir kez).
 */
function mpa_fix_seed_captions() {
	if ( get_option( 'mpa_captions_v2' ) ) {
		return;
	}
	update_option( 'mpa_captions_v2', 1 );
	$posts = get_posts(
		array(
			'post_type'   => array( 'mpa_proje', 'attachment' ),
			'post_status' => 'any',
			'numberposts' => -1,
		)
	);
	foreach ( $posts as $post ) {
		$changes = array();
		foreach ( array( 'post_content', 'post_title', 'post_excerpt' ) as $field ) {
			if ( false !== strpos( $post->$field, ' — ' ) ) {
				$changes[ $field ] = str_replace( ' — ', ', ', $post->$field );
			}
		}
		if ( $changes ) {
			$changes['ID'] = $post->ID;
			wp_update_post( $changes );
		}
		$alt = get_post_meta( $post->ID, '_wp_attachment_image_alt', true );
		if ( $alt && false !== strpos( $alt, ' — ' ) ) {
			update_post_meta( $post->ID, '_wp_attachment_image_alt', str_replace( ' — ', ', ', $alt ) );
		}
	}
}
add_action( 'admin_init', 'mpa_fix_seed_captions' );
add_action( 'after_switch_theme', 'mpa_fix_seed_captions', 20 );
