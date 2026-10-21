<?php
/**
 * Hizmet alanları: fotoğraflı kartlar. Hizmetler sayfasında ayrıca çalışma süreci.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$full     = isset( $args['mode'] ) && 'full' === $args['mode'];
$services = mpa_items( 'service', 3 );
$images   = mpa_service_images();
?>
<section class="section section--white" id="hizmetler">
	<div class="container">
		<?php mpa_section_head( '', __( 'Hizmetlerimiz', 'mpa-grup' ) ); ?>

		<div class="services">
			<?php foreach ( $services as $i => $service ) : ?>
				<article class="service reveal">
					<div class="service__media reveal-img">
						<?php if ( isset( $images[ $i ] ) ) : ?>
							<img src="<?php echo esc_url( mpa_img( $images[ $i ][0] ) ); ?>" alt="<?php echo esc_attr( $images[ $i ][1] ); ?>" loading="lazy" width="800" height="1000">
						<?php endif; ?>
					</div>
					<h3 class="service__title"><?php echo esc_html( $service['title'] ); ?></h3>
					<p><?php echo esc_html( $service['text'] ); ?></p>
				</article>
			<?php endforeach; ?>
		</div>

		<?php if ( ! $full ) : ?>
			<p class="section-more"><a class="btn btn--dark" href="<?php echo esc_url( mpa_url( 'hizmetler' ) ); ?>"><?php esc_html_e( 'Hizmetlerimiz', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></a></p>
		<?php endif; ?>
	</div>
</section>

<?php if ( $full ) : ?>
	<section class="section section--paper" id="surec">
		<div class="container">
			<?php mpa_section_head( __( 'Planlamadan teslime', 'mpa-grup' ), __( 'Çalışma sürecimiz', 'mpa-grup' ) ); ?>
			<ol class="process">
				<?php foreach ( mpa_phases() as $i => $phase ) : ?>
					<li class="process__step reveal">
						<span class="process__num"><?php echo esc_html( sprintf( '%02d', $i + 1 ) ); ?></span>
						<h3 class="process__title"><?php echo esc_html( $phase['title'] ); ?></h3>
						<p><?php echo esc_html( $phase['text'] ); ?></p>
					</li>
				<?php endforeach; ?>
			</ol>
		</div>
	</section>
<?php endif; ?>
