<?php
/**
 * Sayfa bulunamadı.
 *
 * @package MPA_Grup
 */

get_header();
get_template_part(
	'template-parts/page-hero',
	null,
	array(
		'eyebrow' => '404',
		'title'   => __( 'Bu kat henüz inşa edilmedi.', 'mpa-grup' ),
	)
);
?>
<section class="section section--paper">
	<div class="container container--narrow">
		<p><?php esc_html_e( 'Aradığınız sayfa taşınmış ya da hiç var olmamış olabilir.', 'mpa-grup' ); ?></p>
		<p><a class="btn btn--accent" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Ana sayfaya dön', 'mpa-grup' ); ?></a></p>
	</div>
</section>
<?php
get_footer();
