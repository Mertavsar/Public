<?php
/**
 * Büyük teklif çağrısı.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$id    = isset( $args['id'] ) ? $args['id'] : '';
$phone = mpa_opt( 'phone' );
$email = mpa_opt( 'email' );
?>
<section class="cta"<?php echo $id ? ' id="' . esc_attr( $id ) . '"' : ''; ?>>
	<div class="container">
		<p class="eyebrow"><?php esc_html_e( 'Teklif & keşif', 'mpa-grup' ); ?></p>
		<h2 class="cta__title"><?php esc_html_e( 'Bir sonraki yapıyı', 'mpa-grup' ); ?><br><em><?php esc_html_e( 'birlikte inşa edelim.', 'mpa-grup' ); ?></em></h2>
		<div class="cta__row">
			<p class="cta__text"><?php echo esc_html( mpa_opt( 'contact_text' ) ); ?></p>
			<div class="btn-row">
				<a class="btn btn--accent btn--lg" href="<?php echo esc_url( mpa_url( 'iletisim' ) ); ?>"><?php esc_html_e( 'Teklif Alın', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a>
				<?php if ( $phone ) : ?>
					<a class="btn btn--ghost-light btn--lg" href="<?php echo esc_url( mpa_tel( $phone ) ); ?>"><?php echo mpa_icon( 'phone' ); // phpcs:ignore ?> <?php echo esc_html( $phone ); ?></a>
				<?php elseif ( $email ) : ?>
					<a class="btn btn--ghost-light btn--lg" href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php echo mpa_icon( 'mail' ); // phpcs:ignore ?> <?php echo esc_html( antispambot( $email ) ); ?></a>
				<?php endif; ?>
			</div>
		</div>
	</div>
</section>
