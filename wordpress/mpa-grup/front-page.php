<?php
/**
 * Ana sayfa: inşaat videosu, kurumsal cümle, kayan uzmanlık bandı, hizmetler,
 * seçili projeler ve teklif çağrısı. Her bölüm kendi sayfasına bağlanır.
 *
 * @package MPA_Grup
 */

get_header();

get_template_part( 'template-parts/build' );
get_template_part( 'template-parts/about', null, array( 'mode' => 'teaser' ) );
get_template_part( 'template-parts/marquee' );
get_template_part( 'template-parts/services', null, array( 'mode' => 'teaser' ) );
get_template_part( 'template-parts/projects' );
get_template_part( 'template-parts/cta', null, array( 'id' => 'iletisim' ) );

get_footer();
