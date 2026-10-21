<?php
/**
 * Referans projeler: katalogdaki "Projelerimiz" sayfasının satır düzeni.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$projects    = mpa_get_projects( 6 );
$archive_url = get_post_type_archive_link( 'mpa_proje' );
$has_posts   = wp_count_posts( 'mpa_proje' )->publish > 0;
?>
<section class="section section--paper" id="projeler">
	<div class="container">
		<?php mpa_section_head( __( 'Referanslarımız', 'mpa-grup' ), __( 'Projelerimiz', 'mpa-grup' ), '03' ); ?>

		<div class="project-list">
			<?php
			foreach ( $projects as $i => $project ) {
				get_template_part(
					'template-parts/project-row',
					null,
					array(
						'project' => $project,
						'index'   => $i,
					)
				);
			}
			?>
		</div>

		<?php if ( $has_posts && $archive_url ) : ?>
			<p class="project-list__more"><a class="btn btn--dark" href="<?php echo esc_url( $archive_url ); ?>"><?php esc_html_e( 'Tüm projeler', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a></p>
		<?php endif; ?>
	</div>
</section>

<section class="cta-band">
	<div class="container cta-band__inner">
		<p class="cta-band__text"><?php esc_html_e( 'Kamu ve özel sektör yapılarınızda kaba inşaattan mimari uygulamaya güvenilir çözüm ortağınız.', 'mpa-grup' ); ?></p>
		<a class="btn btn--accent" href="#iletisim"><?php esc_html_e( 'Teklif Alın', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a>
	</div>
</section>
