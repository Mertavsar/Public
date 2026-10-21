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
			'eyebrow' => mpa_opt( 'company_name' ),
			'title'   => get_the_title(),
			'lead'    => mpa_opt( 'company_short' ),
		)
	);
	get_template_part( 'template-parts/about', null, array( 'mode' => 'full' ) );
	mpa_page_content();
	get_template_part( 'template-parts/principles' );
	get_template_part( 'template-parts/cta' );
endwhile;

get_footer();
