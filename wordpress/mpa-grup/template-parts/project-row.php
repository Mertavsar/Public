<?php
/**
 * Tek proje satırı.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$project = $args['project'];
$index   = isset( $args['index'] ) ? (int) $args['index'] : 0;
$meta    = array_filter( array( $project['client'], $project['location'] ) );
$tag     = $project['url'] ? 'a' : 'div';
?>
<article class="project-row reveal">
	<span class="project-row__num" aria-hidden="true"><?php echo esc_html( sprintf( '%02d', $index + 1 ) ); ?></span>
	<div class="project-row__body">
		<?php if ( $project['category'] ) : ?>
			<p class="eyebrow"><?php echo esc_html( $project['category'] ); ?></p>
		<?php endif; ?>
		<h3 class="project-row__title">
			<?php if ( $project['url'] ) : ?>
				<a href="<?php echo esc_url( $project['url'] ); ?>"><?php echo esc_html( $project['title'] ); ?></a>
			<?php else : ?>
				<?php echo esc_html( $project['title'] ); ?>
			<?php endif; ?>
		</h3>
		<?php if ( $meta ) : ?>
			<p class="project-row__meta"><?php echo esc_html( implode( ' — ', $meta ) ); ?></p>
		<?php endif; ?>
		<?php if ( $project['url'] ) : ?>
			<a class="link-arrow" href="<?php echo esc_url( $project['url'] ); ?>" aria-label="<?php echo esc_attr( $project['title'] ); ?>"><?php esc_html_e( 'Projeyi incele', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a>
		<?php endif; ?>
	</div>
	<<?php echo $tag; // phpcs:ignore ?> class="project-row__media"<?php echo $project['url'] ? ' href="' . esc_url( $project['url'] ) . '" tabindex="-1" aria-hidden="true"' : ''; ?>>
		<?php if ( $project['image'] ) : ?>
			<img src="<?php echo esc_url( $project['image'] ); ?>" alt="<?php echo esc_attr( $project['title'] ); ?>" loading="lazy" width="960" height="720">
		<?php endif; ?>
	</<?php echo $tag; // phpcs:ignore ?>>
</article>
