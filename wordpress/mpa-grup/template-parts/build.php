<?php
/**
 * Giriş: aşağı kaydırdıkça temelden bitmiş hale gelen yapı.
 *
 * İki mod:
 * - Video: Özelleştir'den yüklenen (ya da assets/video/insaat.webm|mp4) inşaat videosu
 *   kaydırmayla kare kare ilerler.
 * - Fotoğraf: video yoksa bitmiş yapı fotoğrafı; önce teknik çizim, sonra zeminden
 *   yükselen kaba inşaat (gri), en sonda cephe ve renkler.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$video  = mpa_hero_video_sources();
$final  = mpa_hero_image_url();
$sketch = mpa_hero_sketch_url();
$phases = mpa_phases();
$starts = implode( ',', wp_list_pluck( $phases, 'at' ) );
?>
<section class="mpa-build" id="insaat" aria-label="<?php esc_attr_e( 'İnşaat süreci', 'mpa-grup' ); ?>">
	<div class="mpa-build__stage is-intro" data-phases="<?php echo esc_attr( $starts ); ?>" data-mode="<?php echo $video ? 'video' : 'photo'; ?>">

		<div class="mpa-build__media" aria-hidden="true">
			<?php if ( $video ) : ?>
				<video class="mpa-build__video" poster="<?php echo esc_url( $final ); ?>" muted playsinline preload="auto">
					<?php foreach ( $video as $mime => $src ) : ?>
						<source src="<?php echo esc_url( $src ); ?>" type="<?php echo esc_attr( $mime ); ?>">
					<?php endforeach; ?>
				</video>
			<?php else : ?>
				<img class="mpa-build__layer mpa-build__sketch<?php echo $sketch ? '' : ' is-filtered'; ?>" src="<?php echo esc_url( $sketch ? $sketch : $final ); ?>" alt="" width="2000" height="1125" fetchpriority="high">
				<img class="mpa-build__layer mpa-build__rough" src="<?php echo esc_url( $final ); ?>" alt="" width="2000" height="1125">
				<img class="mpa-build__layer mpa-build__done" src="<?php echo esc_url( $final ); ?>" alt="" width="2000" height="1125">
				<div class="mpa-build__laser"></div>
			<?php endif; ?>
		</div>
		<div class="mpa-build__shade" aria-hidden="true"></div>

		<div class="mpa-build__copy">
			<div class="mpa-build__intro">
				<p class="eyebrow"><?php echo esc_html( mpa_opt( 'hero_eyebrow' ) ); ?></p>
				<h1 class="mpa-build__title"><?php echo mpa_kses_title( mpa_opt( 'hero_title' ) ); // phpcs:ignore ?></h1>
				<p class="mpa-build__lead"><?php echo esc_html( mpa_opt( 'hero_text' ) ); ?></p>
				<p class="mpa-build__cue"><span class="mpa-build__mouse" aria-hidden="true"></span><?php esc_html_e( 'Yapıyı inşa etmek için aşağı kaydırın', 'mpa-grup' ); ?></p>
			</div>

			<div class="mpa-build__phases" aria-live="polite">
				<div class="phase-card">
					<div class="phase-card__top">
						<span><?php esc_html_e( 'İnşaat Aşaması', 'mpa-grup' ); ?></span>
						<span class="phase-card__count"><b data-hud="phase">01</b> / <?php echo esc_html( sprintf( '%02d', count( $phases ) ) ); ?></span>
					</div>
					<ol class="phase-list">
						<?php foreach ( $phases as $i => $phase ) : ?>
							<li class="phase-item<?php echo 0 === $i ? ' is-active' : ''; ?>">
								<span class="phase-item__num"><?php echo esc_html( sprintf( '%02d', $i + 1 ) ); ?></span>
								<h2 class="phase-item__title"><?php echo esc_html( $phase['title'] ); ?></h2>
								<p class="phase-item__text"><?php echo esc_html( $phase['text'] ); ?></p>
							</li>
						<?php endforeach; ?>
					</ol>
					<div class="phase-card__bar" aria-hidden="true">
						<span class="phase-card__fill" data-hud="bar"></span>
						<?php foreach ( $phases as $phase ) : ?>
							<i style="left:<?php echo esc_attr( $phase['at'] * 100 ); ?>%"></i>
						<?php endforeach; ?>
					</div>
				</div>
			</div>

			<div class="mpa-build__final">
				<p class="eyebrow"><?php echo esc_html( mpa_opt( 'final_eyebrow' ) ); ?></p>
				<h2 class="mpa-build__title mpa-build__title--final"><?php echo mpa_kses_title( mpa_opt( 'final_title' ) ); // phpcs:ignore ?></h2>
				<p class="mpa-build__lead"><?php echo esc_html( mpa_opt( 'final_text' ) ); ?></p>
				<div class="btn-row">
					<a class="btn btn--accent" href="#projeler"><?php esc_html_e( 'Projelerimiz', 'mpa-grup' ); ?></a>
					<a class="btn btn--ghost-light" href="#iletisim"><?php esc_html_e( 'Teklif Alın', 'mpa-grup' ); ?></a>
				</div>
			</div>
		</div>

		<div class="mpa-build__hud" aria-hidden="true">
			<div class="hud-cell"><span class="hud-key"><?php esc_html_e( 'Tamamlanma', 'mpa-grup' ); ?></span><span class="hud-val">%<b data-hud="pct">0</b></span></div>
			<div class="hud-cell"><span class="hud-key"><?php esc_html_e( 'Aşama', 'mpa-grup' ); ?></span><span class="hud-val hud-val--text" data-hud="name"><?php echo esc_html( $phases[0]['title'] ); ?></span></div>
		</div>

		<a class="mpa-build__skip" href="#hakkimizda"><?php esc_html_e( 'Animasyonu geç', 'mpa-grup' ); ?> <?php echo mpa_icon( 'down' ); // phpcs:ignore ?></a>
	</div>
</section>
