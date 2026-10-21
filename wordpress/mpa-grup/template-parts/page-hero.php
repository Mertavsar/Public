<?php
/**
 * İç sayfa giriş alanı. Görsel verilirse tam genişlik fotoğraf üzerinde büyük başlık;
 * 'split' düzeninde solda başlık, sağda görsel (proje sayfaları).
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$eyebrow = isset( $args['eyebrow'] ) ? $args['eyebrow'] : '';
$title   = isset( $args['title'] ) ? $args['title'] : '';
$meta    = isset( $args['meta'] ) ? array_filter( (array) $args['meta'] ) : array();
$lead    = isset( $args['lead'] ) ? $args['lead'] : '';
$image   = isset( $args['image'] ) ? $args['image'] : '';
$layout  = isset( $args['layout'] ) ? $args['layout'] : 'cover';
$trail   = isset( $args['trail'] ) ? (array) $args['trail'] : array();
$classes = 'page-hero' . ( $image ? ' page-hero--image page-hero--' . $layout : '' );
?>
<section class="<?php echo esc_attr( $classes ); ?>">
	<?php if ( $image ) : ?>
		<div class="page-hero__media"><img src="<?php echo esc_url( $image ); ?>" alt="" fetchpriority="high"></div>
	<?php endif; ?>
	<div class="container page-hero__inner">
		<?php
		if ( $image ) {
			mpa_breadcrumb( $trail, wp_strip_all_tags( $title ) );
		}
		?>
		<?php if ( $eyebrow ) : ?>
			<p class="eyebrow"><?php echo esc_html( $eyebrow ); ?></p>
		<?php endif; ?>
		<h1 class="page-hero__title"><?php echo mpa_kses_title( $title ); // phpcs:ignore ?></h1>
		<?php if ( $lead ) : ?>
			<p class="page-hero__lead"><?php echo esc_html( $lead ); ?></p>
		<?php endif; ?>
		<?php if ( $meta ) : ?>
			<dl class="page-hero__meta">
				<?php foreach ( $meta as $label => $value ) : ?>
					<div><dt><?php echo esc_html( $label ); ?></dt><dd><?php echo esc_html( $value ); ?></dd></div>
				<?php endforeach; ?>
			</dl>
		<?php endif; ?>
	</div>
</section>
