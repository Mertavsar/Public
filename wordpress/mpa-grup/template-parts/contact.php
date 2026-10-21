<?php
/**
 * İletişim bölümü ve form.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$phone   = mpa_opt( 'phone' );
$email   = mpa_opt( 'email' );
$address = mpa_opt( 'address' );
$hours   = mpa_opt( 'hours' );
$map     = mpa_opt( 'map_embed' );
$privacy = get_privacy_policy_url();
$topics  = array( 'Kamu yapısı', 'Özel sektör yapısı', 'Betonarme imalat', 'Mimari imalat', 'Diğer' );
?>
<section class="section section--white" id="iletisim">
	<div class="container">
		<?php mpa_section_head( __( 'İletişim', 'mpa-grup' ), mpa_opt( 'contact_title' ), '04' ); ?>

		<div class="contact">
			<div class="contact__info reveal">
				<p class="contact__lead"><?php echo esc_html( mpa_opt( 'contact_text' ) ); ?></p>
				<ul class="contact__list">
					<?php if ( $phone ) : ?>
						<li><?php echo mpa_icon( 'phone' ); // phpcs:ignore ?><div><span><?php esc_html_e( 'Telefon', 'mpa-grup' ); ?></span><a href="<?php echo esc_url( mpa_tel( $phone ) ); ?>"><?php echo esc_html( $phone ); ?></a></div></li>
					<?php endif; ?>
					<?php if ( $email ) : ?>
						<li><?php echo mpa_icon( 'mail' ); // phpcs:ignore ?><div><span><?php esc_html_e( 'E-posta', 'mpa-grup' ); ?></span><a href="mailto:<?php echo esc_attr( antispambot( $email ) ); ?>"><?php echo esc_html( antispambot( $email ) ); ?></a></div></li>
					<?php endif; ?>
					<?php if ( $address ) : ?>
						<li><?php echo mpa_icon( 'pin' ); // phpcs:ignore ?><div><span><?php esc_html_e( 'Adres', 'mpa-grup' ); ?></span><p><?php echo nl2br( esc_html( $address ) ); ?></p></div></li>
					<?php endif; ?>
					<?php if ( $hours ) : ?>
						<li><?php echo mpa_icon( 'clock' ); // phpcs:ignore ?><div><span><?php esc_html_e( 'Çalışma saatleri', 'mpa-grup' ); ?></span><p><?php echo esc_html( $hours ); ?></p></div></li>
					<?php endif; ?>
				</ul>
				<?php if ( ! $phone && ! $email && ! $address && current_user_can( 'edit_theme_options' ) ) : ?>
					<p class="admin-hint"><?php esc_html_e( 'Yalnızca yöneticiler görür: Telefon, e-posta ve adresi Görünüm > Özelleştir > MPA Grup > Firma & İletişim Bilgileri bölümünden ekleyin.', 'mpa-grup' ); ?></p>
				<?php endif; ?>
				<div class="contact__scope">
					<h3><?php esc_html_e( 'Hizmet alanlarımız', 'mpa-grup' ); ?></h3>
					<ul>
						<?php foreach ( mpa_items( 'service', 3 ) as $service ) : ?>
							<li><?php echo mpa_icon( 'check' ); // phpcs:ignore ?><?php echo esc_html( $service['title'] ); ?></li>
						<?php endforeach; ?>
						<li><?php echo mpa_icon( 'check' ); // phpcs:ignore ?><?php esc_html_e( 'Kamu ve özel sektör yapıları', 'mpa-grup' ); ?></li>
					</ul>
				</div>
				<?php if ( $map ) : ?>
					<div class="contact__map"><iframe src="<?php echo esc_url( $map ); ?>" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="<?php esc_attr_e( 'Konum', 'mpa-grup' ); ?>"></iframe></div>
				<?php endif; ?>
			</div>

			<form class="contact-form reveal" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" method="post">
				<?php mpa_form_notice(); ?>
				<input type="hidden" name="action" value="mpa_contact">
				<input type="hidden" name="_mpa_redirect" value="<?php echo esc_url( is_singular() ? get_permalink() : home_url( '/' ) ); ?>">
				<div class="hp" aria-hidden="true"><label>Web sitesi <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>

				<div class="field-row">
					<label class="field"><span><?php esc_html_e( 'Ad Soyad', 'mpa-grup' ); ?> *</span><input type="text" name="ad_soyad" required autocomplete="name"></label>
					<label class="field"><span><?php esc_html_e( 'Telefon', 'mpa-grup' ); ?> *</span><input type="tel" name="telefon" required autocomplete="tel"></label>
				</div>
				<div class="field-row">
					<label class="field"><span><?php esc_html_e( 'E-posta', 'mpa-grup' ); ?></span><input type="email" name="eposta" autocomplete="email"></label>
					<label class="field"><span><?php esc_html_e( 'Konu', 'mpa-grup' ); ?></span>
						<select name="konu">
							<?php foreach ( $topics as $topic ) : ?>
								<option><?php echo esc_html( $topic ); ?></option>
							<?php endforeach; ?>
						</select>
					</label>
				</div>
				<label class="field"><span><?php esc_html_e( 'Mesajınız', 'mpa-grup' ); ?></span><textarea name="mesaj" rows="5"></textarea></label>
				<label class="check">
					<input type="checkbox" name="kvkk" value="1" required>
					<span>
						<?php
						if ( $privacy ) {
							printf(
								/* translators: %s: aydınlatma metni bağlantısı */
								esc_html__( 'Kişisel verilerimin talebime dönüş yapılması amacıyla işlenmesini kabul ediyorum. %s', 'mpa-grup' ),
								'<a href="' . esc_url( $privacy ) . '" target="_blank">' . esc_html__( 'Aydınlatma metni', 'mpa-grup' ) . '</a>'
							);
						} else {
							esc_html_e( 'Kişisel verilerimin talebime dönüş yapılması amacıyla işlenmesini kabul ediyorum.', 'mpa-grup' );
						}
						?>
					</span>
				</label>
				<button class="btn btn--accent" type="submit"><?php esc_html_e( 'Gönder', 'mpa-grup' ); ?> <?php echo mpa_icon( 'arrow' ); // phpcs:ignore ?></button>
			</form>
		</div>
	</div>
</section>
