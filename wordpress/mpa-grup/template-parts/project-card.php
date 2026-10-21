<?php
/**
 * Proje kartı: tüm kart tıklanabilir; görsel, kategori, konum, başlık.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$project = $args['project'];
$index   = isset( $args['index'] ) ? (int) $args['index'] : 0;
$tag     = $project['url'] ? 'a' : 'div';
?>
<<?php echo $tag; // phpcs:ignore ?> class="project-card reveal<?php echo 0 === $index ? ' project-card--wide' : ''; ?>"<?php echo $project['url'] ? ' href="' . esc_url( $project['url'] ) . '"' : ''; ?>>
	<div class="project-card__media reveal-img">
		<?php if ( $project['image'] ) : ?>
			<img src="<?php echo esc_url( $project['image'] ); ?>" alt="<?php echo esc_attr( $project['title'] ); ?>" loading="lazy" width="1600" height="1000">
		<?php endif; ?>
	</div>
	<div class="project-card__body">
		<div class="project-card__info">
			<p class="project-card__meta"><?php echo esc_html( implode( ' · ', array_filter( array( $project['category'], $project['location'] ) ) ) ); ?></p>
			<h3 class="project-card__title"><?php echo esc_html( $project['title'] ); ?></h3>
		</div>
	</div>
</<?php echo $tag; // phpcs:ignore ?>>
