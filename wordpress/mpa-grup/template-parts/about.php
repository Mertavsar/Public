<?php
/**
 * Kurumsal. Ana sayfada: kaydırdıkça kelime kelime aydınlanan kurumsal cümle, görsel
 * ve kısa metin. Kurumsal sayfasında: metnin tamamı ve rakamlar.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$image_id   = (int) mpa_opt( 'about_image' );
$full       = isset( $args['mode'] ) && 'full' === $args['mode'];
$paragraphs = array_values( array_filter( array_map( 'trim', preg_split( '/\n\s*\n/', (string) mpa_opt( 'about_text' ) ) ) ) );
$paragraphs = $full ? $paragraphs : array_slice( $paragraphs, 0, 2 );
$stats      = $full ? mpa_stats() : array();
?>
<section class="section section--paper about-section" id="hakkimizda">
	<div class="container">
		<div class="section-head__top">
			<p class="eyebrow"><?php esc_html_e( 'Kurumsal', 'mpa-grup' ); ?></p>
			<span class="section-num" aria-hidden="true">(01)</span>
		</div>
		<p class="statement" data-words><?php echo mpa_kses_title( mpa_opt( 'about_title' ) ); // phpcs:ignore ?></p>

		<div class="about">
			<figure class="about__media reveal-img">
				<?php
				if ( $image_id ) {
					echo wp_get_attachment_image( $image_id, 'large', false, array( 'class' => 'about__img' ) );
					$caption = wp_get_attachment_caption( $image_id );
				} else {
					printf(
						'<img class="about__img" src="%s" alt="%s" loading="lazy" width="1600" height="900">',
						esc_url( mpa_img( 'projeler/anittepe-olimpik-yuzme-havuzu-02.jpg' ) ),
						esc_attr__( 'Anıttepe Olimpik Yüzme Havuzu', 'mpa-grup' )
					);
					$caption = __( 'Anıttepe Olimpik Yüzme Havuzu — Ankara', 'mpa-grup' );
				}
				if ( $caption ) {
					echo '<figcaption class="about__caption">' . esc_html( $caption ) . '</figcaption>';
				}
				?>
			</figure>
			<div class="about__text reveal">
				<?php foreach ( $paragraphs as $i => $paragraph ) : ?>
					<p<?php echo 0 === $i ? ' class="about__first"' : ''; ?>><?php echo esc_html( $paragraph ); ?></p>
				<?php endforeach; ?>
				<div class="about__actions">
					<?php if ( ! $full ) : ?>
						<a class="btn btn--dark" href="<?php echo esc_url( mpa_url( 'kurumsal' ) ); ?>"><?php esc_html_e( 'Kurumsal', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a>
					<?php endif; ?>
					<a class="link-arrow" href="<?php echo esc_url( mpa_url( 'projeler' ) ); ?>"><?php esc_html_e( 'Referans projelerimiz', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a>
				</div>
			</div>
		</div>

		<?php if ( $stats ) : ?>
			<div class="stats reveal">
				<?php foreach ( $stats as $stat ) : ?>
					<div class="stat">
						<span class="stat__value"><?php echo esc_html( $stat['value'] ); ?></span>
						<span class="stat__label"><?php echo esc_html( $stat['label'] ); ?></span>
					</div>
				<?php endforeach; ?>
			</div>
		<?php endif; ?>
	</div>
</section>
