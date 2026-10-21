<?php
/**
 * İlkelerimiz (katalog 01–04).
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$principles = mpa_items( 'principle', 4 );
if ( ! $principles ) {
	return;
}
?>
<section class="section section--grid" id="ilkelerimiz">
	<div class="container">
		<?php mpa_section_head( __( 'Değerlerimiz', 'mpa-grup' ), __( 'İlkelerimiz', 'mpa-grup' ), '02' ); ?>
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
