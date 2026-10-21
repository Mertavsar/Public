<?php
/**
 * Kurumsal sayfası (/kurumsal/).
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
			'lead'    => mpa_opt( 'company_short' ),
			'image'   => mpa_img( 'projeler/anittepe-olimpik-yuzme-havuzu-01.jpg' ),
		)
	);
	get_template_part( 'template-parts/about', null, array( 'mode' => 'full' ) );
	mpa_page_content();
	get_template_part( 'template-parts/principles' );
	get_template_part( 'template-parts/cta' );
endwhile;

get_footer();
