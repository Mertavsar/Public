<?php
/**
 * Görünüm → Özelleştir: videolar ve paket sipariş linkleri. Link yapıştırılınca sağdaki önizleme
 * yenilenir, video sitedeki yerini alır; "Yayımla" ile kaydedilir. Değerler paneldeki
 * "Kuzu Lahmacun" sayfasıyla aynı yerde (kuzu_ayarlar) tutulur; ikisinden de düzenlenebilir.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// Görünüm menüsünde ayarlar sayfasına kısayol.
add_action(
	'admin_menu',
	function () {
		add_submenu_page( 'themes.php', 'Kuzu Lahmacun ayarları', 'Kuzu Lahmacun ayarları', 'manage_options', 'admin.php?page=kuzu-ayarlar' );
	},
	20
);

add_action(
	'customize_register',
	function ( $wp_customize ) {
		$wp_customize->add_panel(
			'kuzu',
			array(
				'title'       => 'Kuzu Lahmacun',
				'priority'    => 1,
				'description' => 'Menü, SSS, galeri ve Google yorumları için sol menüdeki <b>Kuzu Lahmacun</b> sayfası.',
			)
		);
		$ayar = function ( $k, $temizle ) use ( $wp_customize ) {
			$wp_customize->add_setting(
				'kuzu_ayarlar[' . $k . ']',
				array(
					'type'              => 'option',
					'capability'        => 'manage_options',
					'default'           => kuzu_ayar( $k ),
					'sanitize_callback' => $temizle,
					'transport'         => 'refresh',
				)
			);
		};

		// Videolar
		$wp_customize->add_section( 'kuzu_videolar', array( 'title' => 'Videolar (YouTube Shorts)', 'panel' => 'kuzu', 'priority' => 10 ) );
		$ayar( 'videolar', 'sanitize_textarea_field' );
		$wp_customize->add_control(
			'kuzu_ayarlar[videolar]',
			array(
				'section'     => 'kuzu_videolar',
				'type'        => 'textarea',
				'label'       => 'Video linkleri',
				'description' => 'Her satıra bir video: <code>YouTube linki | başlık</code> (başlık isteğe bağlı). Shorts, normal video ve youtu.be linkleri olur. Satır eklediğiniz an önizlemede görünür.',
				'input_attrs' => array( 'rows' => 8, 'placeholder' => "https://youtube.com/shorts/... | Fırından yeni çıktı" ),
			)
		);
		$ayar( 'video_baslik', 'sanitize_text_field' );
		$wp_customize->add_control( 'kuzu_ayarlar[video_baslik]', array( 'section' => 'kuzu_videolar', 'type' => 'text', 'label' => 'Bölüm başlığı' ) );
		$ayar( 'video_yazi', 'sanitize_text_field' );
		$wp_customize->add_control( 'kuzu_ayarlar[video_yazi]', array( 'section' => 'kuzu_videolar', 'type' => 'text', 'label' => 'Başlığın altındaki yazı' ) );

		// Eve sipariş butonları (ikon, sıra) ayarlar sayfasındaki tabloda yönetilir.
		$wp_customize->add_section(
			'kuzu_siparis',
			array(
				'title'       => 'Eve sipariş butonları',
				'panel'       => 'kuzu',
				'priority'    => 20,
				'description' => 'Butonların adı, linki, ikonu, rengi ve sırası: <a href="' . esc_url( admin_url( 'admin.php?page=kuzu-ayarlar#siparis' ) ) . '">Kuzu Lahmacun ayarları → Eve sipariş butonları</a>.',
			)
		);
		$wp_customize->add_setting( 'kuzu_bilgi', array( 'type' => 'option', 'capability' => 'manage_options', 'sanitize_callback' => '__return_empty_string' ) );
		$wp_customize->add_control( 'kuzu_bilgi', array( 'section' => 'kuzu_siparis', 'type' => 'hidden' ) );
	}
);

// Önizleme, açık olan bölüme kendiliğinden iner: Videolar açıkken videoları, sipariş açıkken menüyü
// gösterir; link eklenince önizleme yenilense de aynı yerde kalır.
add_action(
	'customize_controls_print_footer_scripts',
	function () {
		?>
		<script>
		wp.customize.bind('ready', function () {
			var hedef = { kuzu_videolar: 'videolar', kuzu_siparis: 'menu' };
			var gonder = function () {
				Object.keys(hedef).forEach(function (s) {
					var sec = wp.customize.section(s);
					if (sec && sec.expanded()) wp.customize.previewer.send('kuzu-kaydir', hedef[s]);
				});
			};
			wp.customize.previewer.bind('ready', gonder);
			Object.keys(hedef).forEach(function (s) {
				wp.customize.section(s, function (sec) { sec.expanded.bind(function (acik) { if (acik) gonder(); }); });
			});
		});
		</script>
		<?php
	}
);

add_action(
	'customize_preview_init',
	function () {
		add_action(
			'wp_footer',
			function () {
				?>
				<script>
				wp.customize.bind('preview-ready', function () {
					wp.customize.preview.bind('kuzu-kaydir', function (id) {
						var el = document.getElementById(id) || document.getElementById('menu');
						if (!el) return;
						document.documentElement.style.scrollBehavior = 'auto';
						window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 80);
					});
				});
				</script>
				<?php
			},
			100
		);
	}
);
