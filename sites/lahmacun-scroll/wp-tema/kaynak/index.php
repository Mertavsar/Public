<?php
/**
 * Ana sayfa dışındaki sayfalar (gizlilik politikası, yazılar vb.): markanın sade görünümü.
 * Ana sayfa front-page.php'dir.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b5236">
<link rel="icon" href="<?php echo esc_url( KUZU_URI . 'favicon.svg' ); ?>" type="image/svg+xml">
<?php wp_head(); ?>
</head>
<body <?php body_class( 'ic' ); ?>>
<?php wp_body_open(); ?>
<header class="topbar">
	<a class="brand" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="Kuzu Lahmacun — ana sayfa"><img src="<?php echo esc_url( KUZU_URI . 'logo-beyaz.svg' ); ?>" alt="Kuzu Lahmacun" width="105" height="40"></a>
	<nav aria-label="Bölümler">
		<a class="nav" href="<?php echo esc_url( home_url( '/#menu' ) ); ?>">Menü</a>
		<a class="btn" href="<?php echo esc_url( kuzu_harita_linki() ); ?>" target="_blank" rel="noopener">Yol tarifi</a>
	</nav>
</header>
<main class="ic-main band">
	<div class="wrap ic-wrap">
	<?php if ( have_posts() ) : ?>
		<?php while ( have_posts() ) : the_post(); ?>
			<article <?php post_class( 'ic-yazi' ); ?>>
				<h1 class="display"><?php the_title(); ?></h1>
				<div class="ic-icerik"><?php the_content(); ?></div>
			</article>
		<?php endwhile; ?>
		<?php the_posts_pagination(); ?>
	<?php else : ?>
		<h1 class="display">Sayfa bulunamadı</h1>
		<p><a class="btn" href="<?php echo esc_url( home_url( '/' ) ); ?>">Ana sayfaya dön</a></p>
	<?php endif; ?>
	</div>
</main>
<footer class="band ic-alt">
	<div class="wrap foot">
		<a class="brand" href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( KUZU_URI . 'logo-beyaz.svg' ); ?>" alt="Kuzu Lahmacun" width="147" height="56" loading="lazy"></a>
		<span>© <?php echo esc_html( wp_date( 'Y' ) ); ?> Kuzu Lahmacun &amp; Kilis Tava</span>
	</div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
