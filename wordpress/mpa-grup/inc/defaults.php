<?php
/**
 * Varsayılan içerik. Metinler MPA Grup İnşaat kurumsal kataloğundan (2026) alınmıştır;
 * hepsi Görünüm > Özelleştir > MPA Grup panelinden değiştirilebilir.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Tüm Özelleştir ayarlarının varsayılanları.
 *
 * @return array
 */
function mpa_defaults() {
	static $defaults = null;
	if ( null !== $defaults ) {
		return $defaults;
	}

	$defaults = array(
		// Genel.
		'accent_color'   => '#eb531e',
		'company_name'   => 'MPA Grup İnşaat',
		'company_short'  => 'Betonarme · Mimari İmalat · Mühendislik ve Taahhüt',
		'phone'          => '',
		'whatsapp'       => '',
		'email'          => '',
		'address'        => '',
		'hours'          => '',
		'map_embed'      => '',
		'instagram'      => '',
		'linkedin'       => '',
		'facebook'       => '',
		'youtube'        => '',

		// Giriş / inşaat animasyonu.
		'hero_eyebrow'   => 'Mühendislik ve Taahhüt Hizmetleri',
		'hero_title'     => 'Betonarme ve<br>mimari imalat.',
		'hero_text'      => 'Kamu ve özel sektör yapılarında, kaba inşaattan mimari uygulamaya uzanan süreçte planlı, denetimli ve standartlara uygun imalat.',
		'final_eyebrow'  => 'Anahtar Teslim',
		'final_title'    => 'Temelden çatıya,<br>kalıcı yapılar.',
		'final_text'     => 'Mühendislik disiplinini ticari başarıyla aynı değerde gören, planlamadan teslime kadar sürecin tamamını üstlenen güvenilir çözüm ortağı.',
		'hero_video'     => 0,
		'hero_image'     => 0,

		// Hakkımızda.
		'about_title'    => 'Mühendislik disiplinini <em>ticari başarıyla</em> aynı değerde gören, kalıcı yapılar üreten bir inşaat kuruluşu.',
		'about_text'     => "MPA Grup İnşaat; betonarme ve mimari imalat başta olmak üzere mühendislik ve taahhüt alanlarında hizmet veren bir inşaat kuruluşudur.\n\nGeleceğe yönelik, ülke menfaatlerini ön planda tutan yenilikçi bir vizyonla ilerleyen şirketimiz, her projede doğru planlama ve titiz uygulamayı esas alır.\n\nSistem çözümlerinde ürün kalitesinin tek başına yeterli olmadığının bilincindeyiz; eğitimli, deneyimli ve alanında uzman kadromuzla doğru ve kalıcı sonuçlar üretiyoruz.\n\nDünyadaki teknik gelişmeleri yakından takip etmek, ekonomiklik ve sürdürülebilirlik ilkelerini gözetmek, sektördeki tüm paydaşları bilgilendirmek temel ilkelerimiz arasındadır.",
		'about_image'    => 0,

		// Rakamlar (boş bırakılan kutu gösterilmez; hepsi boşsa bölüm gizlenir).
		'stat_1_value'   => '',
		'stat_1_label'   => '',
		'stat_2_value'   => '',
		'stat_2_label'   => '',
		'stat_3_value'   => '',
		'stat_3_label'   => '',
		'stat_4_value'   => '',
		'stat_4_label'   => '',

		// İletişim.
		'contact_title'  => 'Projenizi birlikte planlayalım.',
		'contact_text'   => 'Kamu veya özel sektör yapınız için keşif ve teklif talebinizi iletin; ekibimiz en kısa sürede size dönüş yapsın.',
		'form_recipient' => '',
		'footer_text'    => 'Kamu ve özel sektör yapılarında, kaba inşaattan mimari uygulamaya uzanan süreçte planlı, denetimli ve standartlara uygun imalat.',
	);

	foreach ( mpa_default_phases() as $i => $phase ) {
		$defaults[ 'phase_' . ( $i + 1 ) . '_title' ] = $phase[0];
		$defaults[ 'phase_' . ( $i + 1 ) . '_text' ]  = $phase[1];
	}
	foreach ( mpa_default_services() as $i => $service ) {
		$defaults[ 'service_' . ( $i + 1 ) . '_title' ] = $service[0];
		$defaults[ 'service_' . ( $i + 1 ) . '_text' ]  = $service[1];
	}
	foreach ( mpa_default_principles() as $i => $item ) {
		$defaults[ 'principle_' . ( $i + 1 ) . '_title' ] = $item[0];
		$defaults[ 'principle_' . ( $i + 1 ) . '_text' ]  = $item[1];
	}

	return $defaults;
}

/**
 * İnşaat animasyonunun aşamaları: başlık, açıklama.
 *
 * @return array
 */
function mpa_default_phases() {
	return array(
		array( 'Proje & Etüt', 'Her yapı doğru okunmuş bir projeyle başlar. Mimari ve statik proje, uygulamadan önce sahada netleşir.' ),
		array( 'Hafriyat & Saha', 'Saha güvenliği alınır; kazı, projede tanımlı kotlara planlı ve kontrollü şekilde indirilir.' ),
		array( 'Temel', 'Donatı yerleştirilir, kalıp kurulur, temel betonu dökülür. Yapının ömrü burada belirlenir.' ),
		array( 'Betonarme Karkas', 'Kolon, perde ve döşemeler kat kat yükselir. Kalıp, donatı ve beton işlerinde mühendislik hassasiyeti.' ),
		array( 'Cephe & Doğrama', 'Cephe ve doğrama uygulamalarıyla yapının kabuğu, projeye sadık şekilde tamamlanır.' ),
		array( 'Mimari İmalat', 'İç mekân ve ince işlerde detay odaklı uygulama; çevre düzenlemesiyle yapı kullanıma hazırlanır.' ),
		array( 'Teslim', 'Planlamadan teslime kadar sürecin tamamı tek elden, planlı ve denetimli şekilde yürütülür.' ),
	);
}

/**
 * Hizmet alanları (katalog: 01 / 02 / 03).
 *
 * @return array
 */
function mpa_default_services() {
	return array(
		array( 'Betonarme İmalat', 'Temelden çatıya taşıyıcı sistem imalatı; kalıp, donatı ve beton işlerinde mühendislik hassasiyeti.' ),
		array( 'Mimari İmalat', 'Cephe, iç mekân ve ince işlerde projeye sadık, detay odaklı uygulama.' ),
		array( 'Mühendislik & Taahhüt', 'Planlamadan teslime kadar sürecin tamamını üstlenen güvenilir çözüm ortaklığı.' ),
	);
}

/**
 * İlkeler (katalog: 01–04).
 *
 * @return array
 */
function mpa_default_principles() {
	return array(
		array( 'Mühendislik Odaklı', 'Ticari kârlılıkla eşdeğer tutulan, doğru ve bilinçli mühendislik formasyonu.' ),
		array( 'Uzman Kadro', 'Eğitimli, tecrübeli ve konusunda uzman personelle doğru sonuca ulaşma anlayışı.' ),
		array( 'Sürdürülebilirlik', 'Ekonomiklik, kullanılabilirlik ve sürekliliği gözeten teknik takip.' ),
		array( 'Müşteri Memnuniyeti', 'Projelerde daima ilk sırada yer alan güvenilir çözüm ortaklığı prensibi.' ),
	);
}

/**
 * Katalogdaki referans projeler. Tema etkinleştirildiğinde "Projeler" içeriği olarak
 * eklenir; eklenemezse ön sayfa bu listeyi doğrudan tema görselleriyle gösterir.
 *
 * Görsel etiketleri katalogdaki fotoğraf altyazılarıdır.
 *
 * @return array
 */
function mpa_seed_projects() {
	return array(
		array(
			'slug'     => 'ivedik-otel',
			'title'    => 'İvedik Otel',
			'client'   => 'Ziver İnşaat',
			'location' => 'Ankara / İvedik',
			'category' => 'Otel',
			'excerpt'  => 'Ziver İnşaat — Ankara İvedik’te otel yapısı.',
			'content'  => 'Ziver İnşaat için Ankara İvedik’te yer alan otel projesi. Fotoğraflar hafriyat, kaba inşaat ve iç mekân taşıyıcı sistem aşamalarından.',
			'images'   => array(
				array( 'ivedik-otel-00.jpg', 'İvedik Otel — kaba inşaat' ),
				array( 'ivedik-otel-01.jpg', 'Kaba inşaat' ),
				array( 'ivedik-otel-02.jpg', 'Taşıyıcı sistem imalatı' ),
				array( 'ivedik-otel-03.jpg', 'Temel ve bodrum imalatı' ),
				array( 'ivedik-otel-04.jpg', 'İç mekân · taşıyıcı sistem' ),
				array( 'ivedik-otel-05.jpg', 'İç mekân · taşıyıcı sistem' ),
				array( 'ivedik-otel-06.jpg', 'İç mekân · taşıyıcı sistem' ),
			),
		),
		array(
			'slug'     => 'lalahan-arastirma-merkezi',
			'title'    => 'Ankara Lalahan Araştırma Merkezi',
			'client'   => '',
			'location' => 'Ankara / Lalahan',
			'category' => 'Kamu · Araştırma',
			'excerpt'  => 'Ankara Lalahan’da kamu araştırma yapısı.',
			'content'  => 'Ankara Lalahan’da yer alan kamu araştırma merkezi. Fotoğraflar tamamlanan yapıdan ve kaba inşaat sürecinden.',
			'images'   => array(
				array( 'lalahan-arastirma-merkezi-00.jpg', 'Ankara Lalahan Araştırma Merkezi' ),
				array( 'lalahan-arastirma-merkezi-01.jpg', 'Tamamlanan yapı' ),
				array( 'lalahan-arastirma-merkezi-02.jpg', 'Tamamlanan yapı' ),
				array( 'lalahan-arastirma-merkezi-03.jpg', 'Kaba inşaat süreci' ),
				array( 'lalahan-arastirma-merkezi-04.jpg', 'Kaba inşaat süreci' ),
				array( 'lalahan-arastirma-merkezi-05.jpg', 'Kaba inşaat süreci' ),
				array( 'lalahan-arastirma-merkezi-06.jpg', 'Kaba inşaat süreci' ),
			),
		),
		array(
			'slug'     => 'anittepe-olimpik-yuzme-havuzu',
			'title'    => 'Anıttepe Olimpik Yüzme Havuzu',
			'client'   => '',
			'location' => 'Ankara / Anıttepe',
			'category' => 'Spor Tesisi',
			'excerpt'  => 'Ankara Anıttepe’de olimpik yüzme havuzu yapısı.',
			'content'  => 'Ankara Anıttepe’de yer alan olimpik yüzme havuzu yapısı. Fotoğraflar cephe ve ana giriş uygulamalarından.',
			'images'   => array(
				array( 'anittepe-olimpik-yuzme-havuzu-01.jpg', 'Cephe ve ana giriş' ),
				array( 'anittepe-olimpik-yuzme-havuzu-00.jpg', 'Anıttepe Olimpik Yüzme Havuzu' ),
				array( 'anittepe-olimpik-yuzme-havuzu-02.jpg', 'Cephe uygulaması' ),
				array( 'anittepe-olimpik-yuzme-havuzu-03.jpg', 'Cephe uygulaması' ),
			),
		),
	);
}

/**
 * Ayar değeri (Özelleştir'de değiştirilmediyse varsayılan).
 *
 * @param string $key Ayar anahtarı.
 * @return mixed
 */
function mpa_opt( $key ) {
	$defaults = mpa_defaults();
	return get_theme_mod( $key, isset( $defaults[ $key ] ) ? $defaults[ $key ] : '' );
}
