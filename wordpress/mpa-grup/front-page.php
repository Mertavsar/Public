<?php
/**
 * Ön sayfa: inşaat animasyonu + kurumsal tek sayfa.
 *
 * @package MPA_Grup
 */

get_header();

get_template_part( 'template-parts/build' );
get_template_part( 'template-parts/about' );
get_template_part( 'template-parts/services' );
get_template_part( 'template-parts/projects' );
get_template_part( 'template-parts/contact' );

get_footer();
