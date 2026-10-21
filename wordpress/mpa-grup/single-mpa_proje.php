<?php
/**
 * Proje detayı.
 *
 * @package MPA_Grup
 */

get_header();

while ( have_posts() ) :
	the_post();
	get_template_part(
		'template-parts/page-hero',
		null,
		array(
			'eyebrow' => __( 'Referans Proje', 'mpa-grup' ),
			'title'   => get_the_title(),
			'meta'    => array(
				__( 'İşveren', 'mpa-grup' )  => get_post_meta( get_the_ID(), '_mpa_client', true ),
				__( 'Konum', 'mpa-grup' )    => get_post_meta( get_the_ID(), '_mpa_location', true ),
				__( 'Kategori', 'mpa-grup' ) => get_post_meta( get_the_ID(), '_mpa_category', true ),
			),
		)
	);
	?>
	<article class="section section--paper">
		<div class="container container--narrow entry">
			<?php if ( has_post_thumbnail() ) : ?>
				<figure class="frame entry__cover"><?php the_post_thumbnail( 'large', array( 'class' => 'frame__img' ) ); ?></figure>
			<?php endif; ?>
			<div class="entry__content">
				<?php the_content(); ?>
			</div>
		</div>
	</article>

	<nav class="container container--narrow post-nav" aria-label="<?php esc_attr_e( 'Diğer projeler', 'mpa-grup' ); ?>">
		<?php
		previous_post_link( '<span class="post-nav__prev">%link</span>', '&larr; %title' );
		next_post_link( '<span class="post-nav__next">%link</span>', '%title &rarr;' );
		?>
	</nav>
	<?php
endwhile;

get_footer();
