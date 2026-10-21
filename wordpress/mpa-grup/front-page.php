<?php
/**
 * Ana sayfa: inşaat videosu, ardından Kurumsal, Hizmetler ve Projeler'den kısa
 * tanıtımlar; her biri kendi sayfasına bağlanır.
 *
 * @package MPA_Grup
 */

get_header();

get_template_part( 'template-parts/build' );
get_template_part( 'template-parts/about', null, array( 'mode' => 'teaser' ) );
get_template_part( 'template-parts/services', null, array( 'mode' => 'teaser' ) );
get_template_part( 'template-parts/projects' );
get_template_part( 'template-parts/cta', null, array( 'id' => 'iletisim' ) );

get_footer();
