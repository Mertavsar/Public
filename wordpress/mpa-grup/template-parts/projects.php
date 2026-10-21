<?php
/**
 * Ana sayfada seçili projeler; tamamı /projeler/ sayfasında.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$projects  = mpa_get_projects( 3 );
$has_posts = wp_count_posts( 'mpa_proje' )->publish > 0;
?>
<section class="section section--paper" id="projeler">
	<div class="container">
		<?php mpa_section_head( __( 'Referanslarımız', 'mpa-grup' ), __( 'Projelerimiz', 'mpa-grup' ) ); ?>

		<div class="project-grid">
			<?php
			foreach ( $projects as $i => $project ) {
				get_template_part(
					'template-parts/project-card',
					null,
					array(
						'project' => $project,
						'index'   => $i,
					)
				);
			}
			?>
		</div>

		<?php if ( $has_posts ) : ?>
			<p class="section-more"><a class="btn btn--dark" href="<?php echo esc_url( mpa_url( 'projeler' ) ); ?>"><?php esc_html_e( 'Tüm projeler', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a></p>
		<?php endif; ?>
	</div>
</section>
