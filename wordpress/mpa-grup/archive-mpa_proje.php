<?php
/**
 * Tüm projeler.
 *
 * @package MPA_Grup
 */

get_header();

get_template_part(
	'template-parts/page-hero',
	null,
	array(
		'eyebrow' => __( 'Referanslarımız', 'mpa-grup' ),
		'title'   => __( 'Projelerimiz', 'mpa-grup' ),
	)
);
?>
<section class="section section--paper">
	<div class="container">
		<div class="project-list">
			<?php
			$index = 0;
			while ( have_posts() ) :
				the_post();
				get_template_part(
					'template-parts/project-row',
					null,
					array(
						'project' => mpa_project_data( get_post() ),
						'index'   => $index++,
					)
				);
			endwhile;
			?>
		</div>
		<?php the_posts_pagination(); ?>
	</div>
</section>
<?php
get_footer();
