<?php
/**
 * Üst bölüm.
 *
 * @package MPA_Grup
 */

?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#icerik"><?php esc_html_e( 'İçeriğe geç', 'mpa-grup' ); ?></a>

<?php if ( is_front_page() ) : ?>
	<div class="preloader" aria-hidden="true">
		<div class="preloader__inner">
			<?php mpa_logo( 'light' ); ?>
			<div class="preloader__bar"><span></span></div>
			<div class="preloader__meta"><span><?php esc_html_e( 'İnşa ediliyor', 'mpa-grup' ); ?></span><span class="preloader__pct">0</span></div>
		</div>
	</div>
<?php endif; ?>

<header class="site-header">
	<div class="container site-header__inner">
		<a class="brand" href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
			<?php mpa_logo( 'dark' ); ?>
			<?php mpa_logo( 'light' ); ?>
		</a>

		<nav class="main-nav" id="ana-menu" aria-label="<?php esc_attr_e( 'Ana menü', 'mpa-grup' ); ?>">
			<?php
			wp_nav_menu(
				array(
					'theme_location' => 'primary',
					'container'      => false,
					'depth'          => 1,
					'fallback_cb'    => 'mpa_menu_fallback',
				)
			);
			?>
			<a class="btn btn--accent btn--sm main-nav__cta" href="<?php echo esc_url( mpa_url( 'iletisim' ) ); ?>"><?php esc_html_e( 'Teklif Alın', 'mpa-grup' ); ?></a>
		</nav>

		<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="ana-menu">
			<span class="screen-reader-text"><?php esc_html_e( 'Menüyü aç', 'mpa-grup' ); ?></span>
			<span class="nav-toggle__bar"></span>
			<span class="nav-toggle__bar"></span>
		</button>
	</div>
</header>

<main id="icerik" class="site-main">
