<?php
/**
 * Görünüm > Özelleştir > MPA Grup paneli.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Sadece <br>, <em>, <strong> içeren başlık temizleyicisi.
 *
 * @param string $value Değer.
 * @return string
 */
function mpa_sanitize_title_html( $value ) {
	return mpa_kses_title( $value );
}

/**
 * Harita alanı: yalnızca Google Haritalar gömme adresi kabul edilir.
 *
 * @param string $value Değer.
 * @return string
 */
function mpa_sanitize_map( $value ) {
	if ( preg_match( '/src="([^"]+)"/', $value, $m ) ) {
		$value = $m[1];
	}
	$value = esc_url_raw( trim( $value ) );
	return ( 0 === strpos( $value, 'https://www.google.com/maps/embed' ) ) ? $value : '';
}

/**
 * Özelleştir alanlarını kaydet.
 *
 * @param WP_Customize_Manager $wp_customize Yönetici.
 */
function mpa_customize_register( $wp_customize ) {
	$wp_customize->add_panel(
		'mpa_panel',
		array(
			'title'    => __( 'MPA Grup', 'mpa-grup' ),
			'priority' => 20,
		)
	);

	$sections = array(
		'mpa_general' => __( 'Firma & İletişim Bilgileri', 'mpa-grup' ),
		'mpa_hero'    => __( 'Giriş: İnşaat Animasyonu', 'mpa-grup' ),
		'mpa_about'   => __( 'Kurumsal', 'mpa-grup' ),
		'mpa_service' => __( 'Hizmetler & İlkeler', 'mpa-grup' ),
		'mpa_stats'   => __( 'Rakamlar', 'mpa-grup' ),
		'mpa_contact' => __( 'İletişim Bölümü & Alt Bilgi', 'mpa-grup' ),
	);
	foreach ( $sections as $id => $title ) {
		$wp_customize->add_section(
			$id,
			array(
				'title' => $title,
				'panel' => 'mpa_panel',
			)
		);
	}
	$wp_customize->get_section( 'mpa_stats' )->description = __( 'Rakamlar katalogda yer almadığı için varsayılan olarak boştur. Değer girdiğiniz kutular "Kurumsal" bölümünün altında görünür. Yalnızca doğrulanmış bilgileri girin.', 'mpa-grup' );

	$add = function ( $key, $section, $label, $type = 'text', $description = '' ) use ( $wp_customize ) {
		$sanitizers = array(
			'text'     => 'sanitize_text_field',
			'textarea' => 'sanitize_textarea_field',
			'html'     => 'mpa_sanitize_title_html',
			'email'    => 'sanitize_email',
			'url'      => 'esc_url_raw',
			'map'      => 'mpa_sanitize_map',
		);
		$defaults   = mpa_defaults();
		$wp_customize->add_setting(
			$key,
			array(
				'default'           => isset( $defaults[ $key ] ) ? $defaults[ $key ] : '',
				'sanitize_callback' => $sanitizers[ $type ],
			)
		);
		$control_type = in_array( $type, array( 'textarea', 'html', 'map' ), true ) ? 'textarea' : $type;
		$wp_customize->add_control(
			$key,
			array(
				'label'       => $label,
				'section'     => $section,
				'type'        => $control_type,
				'description' => $description,
			)
		);
	};

	// Firma & iletişim.
	$wp_customize->add_setting(
		'accent_color',
		array(
			'default'           => '#eb531e',
			'sanitize_callback' => 'sanitize_hex_color',
		)
	);
	$wp_customize->add_control(
		new WP_Customize_Color_Control(
			$wp_customize,
			'accent_color',
			array(
				'label'   => __( 'Vurgu rengi (logo turuncusu)', 'mpa-grup' ),
				'section' => 'mpa_general',
			)
		)
	);
	$add( 'company_name', 'mpa_general', __( 'Firma adı', 'mpa-grup' ) );
	$add( 'company_short', 'mpa_general', __( 'Kısa tanım', 'mpa-grup' ) );
	$add( 'phone', 'mpa_general', __( 'Telefon', 'mpa-grup' ), 'text', __( 'Boş bırakılırsa gösterilmez.', 'mpa-grup' ) );
	$add( 'whatsapp', 'mpa_general', __( 'WhatsApp numarası', 'mpa-grup' ), 'text', __( 'Doluysa sağ altta WhatsApp butonu çıkar. Ör. 0532 000 00 00', 'mpa-grup' ) );
	$add( 'email', 'mpa_general', __( 'E-posta', 'mpa-grup' ), 'email' );
	$add( 'address', 'mpa_general', __( 'Adres', 'mpa-grup' ), 'textarea' );
	$add( 'hours', 'mpa_general', __( 'Çalışma saatleri', 'mpa-grup' ) );
	$add( 'map_embed', 'mpa_general', __( 'Google Haritalar gömme kodu', 'mpa-grup' ), 'map', __( 'Google Haritalar > Paylaş > Harita yerleştir > HTML kopyala; kodu buraya yapıştırın.', 'mpa-grup' ) );
	$add( 'instagram', 'mpa_general', 'Instagram', 'url' );
	$add( 'linkedin', 'mpa_general', 'LinkedIn', 'url' );
	$add( 'facebook', 'mpa_general', 'Facebook', 'url' );
	$add( 'youtube', 'mpa_general', 'YouTube', 'url' );

	// Giriş.
	$add( 'hero_eyebrow', 'mpa_hero', __( 'Üst etiket', 'mpa-grup' ) );
	$add( 'hero_title', 'mpa_hero', __( 'Ana başlık', 'mpa-grup' ), 'html', __( 'Satır atlamak için <br> kullanın.', 'mpa-grup' ) );
	$add( 'hero_text', 'mpa_hero', __( 'Giriş metni', 'mpa-grup' ), 'textarea' );
	$add( 'sign_text', 'mpa_hero', __( 'Bina tepesindeki tabela', 'mpa-grup' ) );
	foreach ( mpa_default_phases() as $i => $phase ) {
		$n = $i + 1;
		/* translators: %d: aşama numarası */
		$add( "phase_{$n}_title", 'mpa_hero', sprintf( __( 'Aşama %d başlığı', 'mpa-grup' ), $n ) );
		/* translators: %d: aşama numarası */
		$add( "phase_{$n}_text", 'mpa_hero', sprintf( __( 'Aşama %d metni', 'mpa-grup' ), $n ), 'textarea' );
	}
	$add( 'final_eyebrow', 'mpa_hero', __( 'Bitiş: üst etiket', 'mpa-grup' ) );
	$add( 'final_title', 'mpa_hero', __( 'Bitiş: başlık', 'mpa-grup' ), 'html' );
	$add( 'final_text', 'mpa_hero', __( 'Bitiş: metin', 'mpa-grup' ), 'textarea' );

	// Kurumsal.
	$add( 'about_title', 'mpa_about', __( 'Başlık', 'mpa-grup' ), 'html', __( 'Turuncu vurgu için <em>…</em> kullanın.', 'mpa-grup' ) );
	$add( 'about_text', 'mpa_about', __( 'Metin (paragraflar arasında boş satır)', 'mpa-grup' ), 'textarea' );
	$wp_customize->add_setting(
		'about_image',
		array(
			'default'           => 0,
			'sanitize_callback' => 'absint',
		)
	);
	$wp_customize->add_control(
		new WP_Customize_Media_Control(
			$wp_customize,
			'about_image',
			array(
				'label'       => __( 'Kurumsal görsel', 'mpa-grup' ),
				'description' => __( 'Boşsa referans projelerden bir fotoğraf kullanılır.', 'mpa-grup' ),
				'section'     => 'mpa_about',
				'mime_type'   => 'image',
			)
		)
	);

	// Hizmetler & ilkeler.
	for ( $n = 1; $n <= 3; $n++ ) {
		/* translators: %d: hizmet numarası */
		$add( "service_{$n}_title", 'mpa_service', sprintf( __( 'Hizmet %d başlığı', 'mpa-grup' ), $n ) );
		/* translators: %d: hizmet numarası */
		$add( "service_{$n}_text", 'mpa_service', sprintf( __( 'Hizmet %d metni', 'mpa-grup' ), $n ), 'textarea' );
	}
	for ( $n = 1; $n <= 4; $n++ ) {
		/* translators: %d: ilke numarası */
		$add( "principle_{$n}_title", 'mpa_service', sprintf( __( 'İlke %d başlığı', 'mpa-grup' ), $n ) );
		/* translators: %d: ilke numarası */
		$add( "principle_{$n}_text", 'mpa_service', sprintf( __( 'İlke %d metni', 'mpa-grup' ), $n ), 'textarea' );
	}

	// Rakamlar.
	for ( $n = 1; $n <= 4; $n++ ) {
		/* translators: %d: kutu numarası */
		$add( "stat_{$n}_value", 'mpa_stats', sprintf( __( 'Rakam %d (ör. 25+)', 'mpa-grup' ), $n ) );
		/* translators: %d: kutu numarası */
		$add( "stat_{$n}_label", 'mpa_stats', sprintf( __( 'Rakam %d etiketi', 'mpa-grup' ), $n ) );
	}

	// İletişim & alt bilgi.
	$add( 'contact_title', 'mpa_contact', __( 'İletişim başlığı', 'mpa-grup' ) );
	$add( 'contact_text', 'mpa_contact', __( 'İletişim metni', 'mpa-grup' ), 'textarea' );
	$add( 'form_recipient', 'mpa_contact', __( 'Form mesajlarının gideceği e-posta', 'mpa-grup' ), 'email', __( 'Boşsa site yöneticisi e-postası kullanılır. Mesajlar ayrıca panelde "Gelen Mesajlar" altında saklanır.', 'mpa-grup' ) );
	$add( 'footer_text', 'mpa_contact', __( 'Alt bilgi metni', 'mpa-grup' ), 'textarea' );
}
add_action( 'customize_register', 'mpa_customize_register' );
