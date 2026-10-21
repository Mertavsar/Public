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
		'lead'    => __( 'Kamu ve özel sektör yapılarında, kaba inşaattan mimari uygulamaya referans projelerimiz.', 'mpa-grup' ),
		'image'   => mpa_img( 'insaat-son.jpg' ),
	)
);
?>
<section class="section section--paper">
	<div class="container">
		<div class="project-grid">
			<?php
			$index = 0;
			while ( have_posts() ) :
				the_post();
				get_template_part(
					'template-parts/project-card',
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
get_template_part( 'template-parts/cta' );
get_footer();
