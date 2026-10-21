<?php
/**
 * Hizmet alanları ve ilkeler.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$icons      = array( 'concrete', 'facade', 'blueprint' );
$services   = mpa_items( 'service', 3 );
$principles = mpa_items( 'principle', 4 );
?>
<section class="section section--grid" id="hizmetler">
	<div class="container">
		<?php mpa_section_head( __( 'Uzmanlık Alanlarımız', 'mpa-grup' ), __( 'Hizmetlerimiz', 'mpa-grup' ), '02' ); ?>

		<div class="services">
			<?php foreach ( $services as $i => $service ) : ?>
				<article class="service reveal">
					<div class="service__head">
						<span class="service__num">/ <?php echo esc_html( sprintf( '%02d', $i + 1 ) ); ?></span>
						<?php echo mpa_icon( isset( $icons[ $i ] ) ? $icons[ $i ] : 'concrete' ); // phpcs:ignore ?>
					</div>
					<h3 class="service__title"><?php echo esc_html( $service['title'] ); ?></h3>
					<p><?php echo esc_html( $service['text'] ); ?></p>
				</article>
			<?php endforeach; ?>
		</div>

		<div class="principles">
			<?php foreach ( $principles as $i => $item ) : ?>
				<div class="principle reveal">
					<span class="principle__num"><?php echo esc_html( sprintf( '%02d', $i + 1 ) ); ?></span>
					<div>
						<h3 class="principle__title"><?php echo esc_html( $item['title'] ); ?></h3>
						<p><?php echo esc_html( $item['text'] ); ?></p>
					</div>
				</div>
			<?php endforeach; ?>
		</div>
	</div>
</section>
