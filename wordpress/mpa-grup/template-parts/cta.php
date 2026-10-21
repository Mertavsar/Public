<?php
/**
 * Teklif çağrısı bandı.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$id = isset( $args['id'] ) ? $args['id'] : '';
?>
<section class="cta-band"<?php echo $id ? ' id="' . esc_attr( $id ) . '"' : ''; ?>>
	<div class="container cta-band__inner">
		<p class="cta-band__text"><?php esc_html_e( 'Kamu ve özel sektör yapılarınızda kaba inşaattan mimari uygulamaya güvenilir çözüm ortağınız.', 'mpa-grup' ); ?></p>
		<a class="btn btn--accent" href="<?php echo esc_url( mpa_url( 'iletisim' ) ); ?>"><?php esc_html_e( 'Teklif Alın', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a>
	</div>
</section>
