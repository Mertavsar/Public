<?php
/**
 * Proje detayı: solda başlık ve bilgiler, sağda kapak; ardından açıklama, büyütülebilir
 * galeri ve sıradaki proje.
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
			'title'   => get_the_title(),
			'image'   => get_the_post_thumbnail_url( null, 'large' ),
			'layout'  => 'split',
			'trail'   => array( __( 'Projeler', 'mpa-grup' ) => mpa_url( 'projeler' ) ),
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
			<div class="entry__content" data-lightbox>
				<?php the_content(); ?>
			</div>
			<p class="section-more"><a class="link-arrow" href="<?php echo esc_url( mpa_url( 'projeler' ) ); ?>"><?php esc_html_e( 'Tüm projeler', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a></p>
		</div>
	</article>

	<?php
	$next = get_adjacent_post( false, '', false );
	if ( ! $next ) {
		$first = get_posts(
			array(
				'post_type'      => 'mpa_proje',
				'posts_per_page' => 1,
				'order'          => 'ASC',
				'orderby'        => 'date',
				'exclude'        => array( get_the_ID() ),
			)
		);
		$next  = $first ? $first[0] : null;
	}
	if ( $next ) :
		?>
		<a class="next-project" href="<?php echo esc_url( get_permalink( $next ) ); ?>">
			<?php if ( has_post_thumbnail( $next ) ) : ?>
				<span class="next-project__media"><?php echo get_the_post_thumbnail( $next, 'large', array( 'alt' => '' ) ); ?></span>
			<?php endif; ?>
			<span class="container next-project__inner">
				<span class="eyebrow"><?php esc_html_e( 'Sıradaki proje', 'mpa-grup' ); ?></span>
				<span class="next-project__title"><?php echo esc_html( get_the_title( $next ) ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></span>
			</span>
		</a>
		<?php
	endif;
endwhile;

get_template_part( 'template-parts/cta' );

get_footer();
