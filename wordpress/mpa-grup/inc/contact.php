<?php
/**
 * İletişim formu: eklenti gerektirmez. Mesaj panelde saklanır ve e-postayla iletilir.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Form gönderimini işle.
 */
function mpa_handle_contact() {
	// Sayfa önbelleği kullanan sitelerde nonce bayatlayabildiği için ziyaretçi formu
	// bal küpü alanı ve IP başına zaman sınırıyla korunur.
	$redirect = isset( $_POST['_mpa_redirect'] ) ? esc_url_raw( wp_unslash( $_POST['_mpa_redirect'] ) ) : '';
	$redirect = wp_validate_redirect( strtok( $redirect, '#' ), home_url( '/' ) );
	$redirect = remove_query_arg( 'mpa_form', $redirect );

	$back = static function ( $status ) use ( $redirect ) {
		wp_safe_redirect( add_query_arg( 'mpa_form', $status, $redirect ) . '#iletisim' );
		exit;
	};

	if ( ! empty( $_POST['website'] ) ) {
		$back( 'ok' );
	}

	$field   = static function ( $key, $multiline = false ) {
		if ( ! isset( $_POST[ $key ] ) ) {
			return '';
		}
		$value = wp_unslash( $_POST[ $key ] ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
		return $multiline ? sanitize_textarea_field( $value ) : sanitize_text_field( $value );
	};
	$name    = $field( 'ad_soyad' );
	$phone   = $field( 'telefon' );
	$email   = sanitize_email( $field( 'eposta' ) );
	$subject = $field( 'konu' );
	$message = $field( 'mesaj', true );

	if ( '' === $name || '' === $phone || empty( $_POST['kvkk'] ) ) {
		$back( 'eksik' );
	}

	$ip       = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '';
	$throttle = 'mpa_cf_' . md5( $ip );
	if ( get_transient( $throttle ) ) {
		$back( 'bekle' );
	}
	set_transient( $throttle, 1, MINUTE_IN_SECONDS );

	$post_id = wp_insert_post(
		array(
			'post_type'   => 'mpa_mesaj',
			'post_status' => 'private',
			'post_title'  => $name . ( $subject ? ' / ' . $subject : '' ),
		)
	);
	if ( $post_id && ! is_wp_error( $post_id ) ) {
		update_post_meta( $post_id, '_mpa_name', $name );
		update_post_meta( $post_id, '_mpa_phone', $phone );
		update_post_meta( $post_id, '_mpa_email', $email );
		update_post_meta( $post_id, '_mpa_subject', $subject );
		update_post_meta( $post_id, '_mpa_message', $message );
	}

	$to = mpa_opt( 'form_recipient' );
	if ( ! is_email( $to ) ) {
		$to = get_option( 'admin_email' );
	}
	$body = sprintf(
		"Ad Soyad: %s\nTelefon: %s\nE-posta: %s\nKonu: %s\n\n%s\n\n%s",
		$name,
		$phone,
		$email ? $email : '-',
		$subject ? $subject : '-',
		$message,
		home_url( '/' )
	);
	$headers = $email ? array( 'Reply-To: ' . $name . ' <' . $email . '>' ) : array();
	/* translators: %s: gönderen adı */
	wp_mail( $to, sprintf( __( 'Web sitesi iletişim formu: %s', 'mpa-grup' ), $name ), $body, $headers );

	$back( 'ok' );
}
add_action( 'admin_post_nopriv_mpa_contact', 'mpa_handle_contact' );
add_action( 'admin_post_mpa_contact', 'mpa_handle_contact' );

/**
 * Gönderim sonrası bildirim.
 */
function mpa_form_notice() {
	$status = isset( $_GET['mpa_form'] ) ? sanitize_key( $_GET['mpa_form'] ) : ''; // phpcs:ignore WordPress.Security.NonceVerification
	$notes  = array(
		'ok'    => array( 'success', __( 'Teşekkürler, mesajınız bize ulaştı. En kısa sürede dönüş yapacağız.', 'mpa-grup' ) ),
		'eksik' => array( 'error', __( 'Lütfen ad soyad ve telefon alanlarını doldurup aydınlatma metnini onaylayın.', 'mpa-grup' ) ),
		'bekle' => array( 'error', __( 'Kısa süre önce bir mesaj gönderdiniz. Lütfen bir dakika sonra tekrar deneyin.', 'mpa-grup' ) ),
	);
	if ( isset( $notes[ $status ] ) ) {
		printf( '<div class="form-note form-note--%1$s" role="status">%2$s</div>', esc_attr( $notes[ $status ][0] ), esc_html( $notes[ $status ][1] ) );
	}
}
