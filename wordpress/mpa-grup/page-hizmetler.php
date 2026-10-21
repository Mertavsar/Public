<?php
/**
 * Hizmetler sayfası (/hizmetler/).
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
			'lead'    => mpa_opt( 'hero_text' ),
			'image'   => mpa_img( 'insaat-son.jpg' ),
		)
	);
	get_template_part( 'template-parts/services', null, array( 'mode' => 'full' ) );
	mpa_page_content();
	get_template_part( 'template-parts/cta' );
endwhile;

get_footer();
