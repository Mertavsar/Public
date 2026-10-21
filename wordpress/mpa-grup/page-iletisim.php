<?php
/**
 * İletişim sayfası (/iletisim/).
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
			'lead'    => mpa_opt( 'contact_text' ),
			'image'   => mpa_img( 'projeler/anittepe-olimpik-yuzme-havuzu-02.jpg' ),
		)
	);
	mpa_page_content();
	get_template_part( 'template-parts/contact' );
endwhile;

get_footer();
