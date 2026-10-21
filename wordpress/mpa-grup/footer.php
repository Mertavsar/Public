<?php
/**
 * Alt bölüm.
 *
 * @package MPA_Grup
 */

$phone    = mpa_opt( 'phone' );
$email    = mpa_opt( 'email' );
$address  = mpa_opt( 'address' );
$whatsapp = mpa_opt( 'whatsapp' );
?>
</main>

<footer class="site-footer">
	<div class="container site-footer__grid">
		<div class="site-footer__brand">
			<a class="brand brand--light" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php mpa_logo( 'light' ); ?></a>
			<p><?php echo esc_html( mpa_opt( 'footer_text' ) ); ?></p>
			<?php mpa_social_links(); ?>
		</div>

		<div>
			<h2 class="site-footer__title"><?php esc_html_e( 'Kısayollar', 'mpa-grup' ); ?></h2>
			<nav aria-label="<?php esc_attr_e( 'Alt menü', 'mpa-grup' ); ?>">
				<?php
				wp_nav_menu(
					array(
						'theme_location' => 'footer',
						'container'      => false,
						'depth'          => 1,
						'fallback_cb'    => 'mpa_menu_fallback',
					)
				);
				?>
			</nav>
		</div>

		<div>
			<h2 class="site-footer__title"><?php esc_html_e( 'Hizmetler', 'mpa-grup' ); ?></h2>
			<ul class="menu">
				<?php foreach ( mpa_items( 'service', 3 ) as $service ) : ?>
					<li><a href="<?php echo esc_url( home_url( '/#hizmetler' ) ); ?>"><?php echo esc_html( $service['title'] ); ?></a></li>
				<?php endforeach; ?>
			</ul>
		</div>

		<div>
			<h2 class="site-footer__title"><?php esc_html_e( 'İletişim', 'mpa-grup' ); ?></h2>
			<ul class="site-footer__contact">
				<?php if ( $phone ) : ?>
					<li><?php echo mpa_icon( 'phone' ); // phpcs:ignore ?><a href="<?php echo esc_url( mpa_tel( $phone ) ); ?>"><?php echo esc_html( $phone ); ?></a></li>
				<?php endif; ?>
				<?php if ( $email ) : ?>
					<li><?php echo mpa_icon( 'mail' ); // phpcs:ignore ?><a href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php echo esc_html( antispambot( $email ) ); ?></a></li>
				<?php endif; ?>
				<?php if ( $address ) : ?>
					<li><?php echo mpa_icon( 'pin' ); // phpcs:ignore ?><span><?php echo nl2br( esc_html( $address ) ); ?></span></li>
				<?php endif; ?>
				<li><?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?><a href="<?php echo esc_url( home_url( '/#iletisim' ) ); ?>"><?php esc_html_e( 'İletişim formu', 'mpa-grup' ); ?></a></li>
			</ul>
		</div>
	</div>

	<div class="container site-footer__bottom">
		<span>&copy; <?php echo esc_html( gmdate( 'Y' ) . ' ' . mpa_opt( 'company_name' ) ); ?></span>
		<span class="site-footer__tag"><?php echo esc_html( mpa_opt( 'company_short' ) ); ?></span>
	</div>
</footer>

<?php if ( $whatsapp ) : ?>
	<a class="wa-float" href="<?php echo esc_url( mpa_whatsapp_url( $whatsapp ) ); ?>" target="_blank" rel="noopener" aria-label="<?php esc_attr_e( 'WhatsApp ile yazın', 'mpa-grup' ); ?>"><?php echo mpa_icon( 'whatsapp' ); // phpcs:ignore ?></a>
<?php endif; ?>

<?php wp_footer(); ?>
</body>
</html>
