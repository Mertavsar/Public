<?php
/**
 * Genel şablon: yazılar, sayfalar, arşivler, arama.
 *
 * @package MPA_Grup
 */

get_header();

if ( is_singular() ) :
	while ( have_posts() ) :
		the_post();
		get_template_part(
			'template-parts/page-hero',
			null,
			array(
				'eyebrow' => is_page() ? mpa_opt( 'company_name' ) : get_the_date(),
				'title'   => get_the_title(),
			)
		);
		?>
		<article <?php post_class( 'section section--paper' ); ?>>
			<div class="container container--narrow entry">
				<?php if ( has_post_thumbnail() && ! is_page() ) : ?>
					<figure class="frame entry__cover"><?php the_post_thumbnail( 'large', array( 'class' => 'frame__img' ) ); ?></figure>
				<?php endif; ?>
				<div class="entry__content">
					<?php
					the_content();
					wp_link_pages();
					?>
				</div>
			</div>
		</article>
		<?php
	endwhile;
else :
	if ( is_search() ) {
		/* translators: %s: arama terimi */
		$heading = sprintf( __( 'Arama: %s', 'mpa-grup' ), get_search_query() );
	} elseif ( is_archive() ) {
		$heading = wp_strip_all_tags( get_the_archive_title() );
	} else {
		$heading = __( 'Haberler', 'mpa-grup' );
	}
	get_template_part(
		'template-parts/page-hero',
		null,
		array(
			'eyebrow' => mpa_opt( 'company_name' ),
			'title'   => $heading,
		)
	);
	?>
	<section class="section section--paper">
		<div class="container container--narrow">
			<?php if ( have_posts() ) : ?>
				<div class="post-list">
					<?php
					while ( have_posts() ) :
						the_post();
						?>
						<article <?php post_class( 'post-item' ); ?>>
							<p class="eyebrow"><?php echo esc_html( get_the_date() ); ?></p>
							<h2 class="post-item__title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
							<?php the_excerpt(); ?>
						</article>
					<?php endwhile; ?>
				</div>
				<?php the_posts_pagination(); ?>
			<?php else : ?>
				<p><?php esc_html_e( 'Burada henüz içerik yok.', 'mpa-grup' ); ?></p>
				<?php get_search_form(); ?>
			<?php endif; ?>
		</div>
	</section>
	<?php
endif;

get_footer();
