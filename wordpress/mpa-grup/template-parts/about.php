<?php
/**
 * Kurumsal / Hakkımızda. Ana sayfada kısa tanıtım (teaser), Kurumsal sayfasında tam metin.
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
<section class="section section--paper" id="hakkimizda">
	<div class="container">
		<?php mpa_section_head( __( 'Kurumsal', 'mpa-grup' ), __( 'Hakkımızda', 'mpa-grup' ), '01' ); ?>

		<div class="about">
			<div class="about__lead reveal">
				<p class="about__statement"><?php echo mpa_kses_title( mpa_opt( 'about_title' ) ); // phpcs:ignore ?></p>
				<figure class="frame">
					<?php
					if ( $image_id ) {
						echo wp_get_attachment_image( $image_id, 'large', false, array( 'class' => 'frame__img' ) );
						$caption = wp_get_attachment_caption( $image_id );
					} else {
						printf(
							'<img class="frame__img" src="%s" alt="%s" loading="lazy" width="1600" height="1200">',
							esc_url( MPA_URI . '/assets/img/projeler/lalahan-arastirma-merkezi-01.jpg' ),
							esc_attr__( 'Ankara Lalahan Araştırma Merkezi — tamamlanan yapı', 'mpa-grup' )
						);
						$caption = __( 'Ankara Lalahan Araştırma Merkezi', 'mpa-grup' );
					}
					if ( $caption ) {
						echo '<figcaption class="frame__tag">' . esc_html( $caption ) . '</figcaption>';
					}
					?>
				</figure>
			</div>
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
