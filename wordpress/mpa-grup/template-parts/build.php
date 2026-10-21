<?php
/**
 * Giriş: aşağı kaydırdıkça teknik çizimden anahtar teslim binaya dönüşen yapı.
 *
 * Her hareketli öğe data-a="başla,bitir" (görünme) ve/veya data-o="başla,bitir"
 * (kaybolma) aralığı taşır; değerler 0–1 arası kaydırma ilerlemesidir. Görsel
 * dönüşümler style.css'teki a-* sınıflarıyla, zamanlama assets/js/main.js ile yapılır.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$ground  = 620;  // ±0.00 kotu.
$fh      = 32;   // Kat yüksekliği (3.20 m).
$floors  = 12;   // Kule kat sayısı.
$annex_n = 4;    // Ek blok kat sayısı.
$cols    = array( 600, 680, 760, 840, 920 );
$a_cols  = array( 920, 1010, 1100 );
$f0      = 0.30; // Karkas başlangıcı.
$f1      = 0.60; // Karkas bitişi.
$c0      = 0.58; // Cephe başlangıcı.
$c1      = 0.78; // Cephe bitişi.
$fd      = ( $f1 - $f0 ) / $floors;
$cd      = ( $c1 - $c0 ) / $floors;
$top     = $ground - $floors * $fh;
$height  = number_format( $floors * 3.2, 2, '.', '' );
$a_top   = $ground - $annex_n * $fh;

$da = static function ( $s, $e ) {
	return sprintf( ' data-a="%.4F,%.4F"', $s, $e );
};
$do = static function ( $s, $e ) {
	return sprintf( ' data-o="%.4F,%.4F"', $s, $e );
};

// Aynı çizim her yüklemede aynı görünsün.
mt_srand( 20260 );

$phases = mpa_phases();
$starts = implode( ',', wp_list_pluck( $phases, 'at' ) );
$sign   = mpa_opt( 'sign_text' );
?>
<section class="mpa-build" id="insaat" aria-label="<?php esc_attr_e( 'İnşaat süreci animasyonu', 'mpa-grup' ); ?>">
	<div class="mpa-build__stage" data-phases="<?php echo esc_attr( $starts ); ?>" data-frame="<?php echo esc_attr( $f0 . ',' . $f1 ); ?>" data-floors="<?php echo (int) $floors; ?>">

		<svg class="mpa-build__svg" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMax meet" role="img" aria-label="<?php esc_attr_e( 'Teknik çizimden başlayıp temel, karkas, cephe ve peyzajla tamamlanan bina illüstrasyonu', 'mpa-grup' ); ?>">
			<defs>
				<pattern id="mpa-grid-s" width="20" height="20" patternUnits="userSpaceOnUse">
					<path d="M20 0H0V20" fill="none" stroke="#0f161b" stroke-opacity=".06" stroke-width="1"/>
				</pattern>
				<pattern id="mpa-grid" width="100" height="100" patternUnits="userSpaceOnUse">
					<rect width="100" height="100" fill="url(#mpa-grid-s)"/>
					<path d="M100 0H0V100" fill="none" stroke="#0f161b" stroke-opacity=".1" stroke-width="1"/>
				</pattern>
				<pattern id="mpa-hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
					<path d="M0 0V10" stroke="#000" stroke-opacity=".12" stroke-width="2"/>
				</pattern>
				<linearGradient id="mpa-soil" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stop-color="#7a634d"/>
					<stop offset=".35" stop-color="#5c4a3a"/>
					<stop offset="1" stop-color="#2f2620"/>
				</linearGradient>
				<linearGradient id="mpa-glass" x1="0" y1="0" x2="1" y2="1">
					<stop offset="0" stop-color="#d7e6f0"/>
					<stop offset=".45" stop-color="#86a9c3"/>
					<stop offset="1" stop-color="#3f6280"/>
				</linearGradient>
				<linearGradient id="mpa-glass-dark" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stop-color="#3c4f5f"/>
					<stop offset="1" stop-color="#1d2a35"/>
				</linearGradient>
				<radialGradient id="mpa-sun-glow">
					<stop offset="0" stop-color="#fff3d6" stop-opacity=".9"/>
					<stop offset="1" stop-color="#fff3d6" stop-opacity="0"/>
				</radialGradient>
				<radialGradient id="mpa-lamp-glow">
					<stop offset="0" stop-color="#ffd38a" stop-opacity=".85"/>
					<stop offset="1" stop-color="#ffd38a" stop-opacity="0"/>
				</radialGradient>
				<clipPath id="mpa-above-ground">
					<rect x="-3000" y="-1000" width="7200" height="<?php echo (int) ( 1000 + $ground ); ?>"/>
				</clipPath>
			</defs>

			<!-- Gökyüzü: yıldızlar, güneş, bulutlar, uzak şehir -->
			<g class="a-fade"<?php echo $da( 0.94, 1 ); // phpcs:ignore ?>>
				<?php for ( $i = 0; $i < 46; $i++ ) : ?>
					<circle cx="<?php echo mt_rand( -400, 1600 ); ?>" cy="<?php echo mt_rand( 10, 330 ); ?>" r="<?php echo mt_rand( 6, 14 ) / 10; ?>" fill="#fff" opacity="<?php echo mt_rand( 4, 9 ) / 10; ?>"/>
				<?php endfor; ?>
			</g>

			<g id="mpa-sun" opacity="0">
				<circle r="90" fill="url(#mpa-sun-glow)"/>
				<circle r="24" class="sun-disc" fill="#fff4dc"/>
			</g>

			<g class="a-fade"<?php echo $da( 0.14, 0.26 ); // phpcs:ignore ?>>
				<g class="cloud cloud--1"><ellipse cx="140" cy="150" rx="70" ry="16"/><ellipse cx="175" cy="138" rx="40" ry="18"/></g>
				<g class="cloud cloud--2"><ellipse cx="820" cy="110" rx="90" ry="14"/><ellipse cx="860" cy="99" rx="46" ry="16"/></g>
				<g class="cloud cloud--3"><ellipse cx="420" cy="260" rx="60" ry="11"/><ellipse cx="445" cy="251" rx="30" ry="12"/></g>
				<g class="cloud cloud--1"><ellipse cx="1180" cy="200" rx="70" ry="12"/></g>
			</g>

			<g class="skyline a-fade"<?php echo $da( 0.12, 0.3 ); // phpcs:ignore ?>>
				<?php
				$x = -420;
				while ( $x < 1640 ) :
					$w = mt_rand( 40, 90 );
					$h = mt_rand( 50, 190 );
					if ( $x + $w > 560 && $x < 1130 ) {
						$h = mt_rand( 40, 110 );
					}
					?>
					<rect x="<?php echo (int) $x; ?>" y="<?php echo (int) ( $ground - $h ); ?>" width="<?php echo (int) $w; ?>" height="<?php echo (int) $h; ?>"/>
					<?php
					$x += $w + mt_rand( 4, 26 );
				endwhile;
				?>
			</g>

			<!-- Zemin ve kesit -->
			<rect x="-3000" y="<?php echo (int) $ground; ?>" width="7200" height="1400" fill="url(#mpa-soil)"/>
			<rect x="-3000" y="<?php echo (int) $ground; ?>" width="7200" height="1400" fill="url(#mpa-hatch)"/>
			<rect x="-3000" y="<?php echo (int) $ground; ?>" width="7200" height="7" fill="#8d7559"/>
			<rect class="a-fade" x="-3000" y="<?php echo (int) ( $ground - 2 ); ?>" width="7200" height="9" fill="#6f8a4f"<?php echo $da( 0.84, 0.9 ); // phpcs:ignore ?>/>
			<rect class="a-fade" x="560" y="<?php echo (int) ( $ground - 1 ); ?>" width="580" height="8" fill="#b9b3a8"<?php echo $da( 0.86, 0.9 ); // phpcs:ignore ?>/>

			<!-- Hafriyat -->
			<g class="a-dig"<?php echo $da( 0.12, 0.2 ); // phpcs:ignore ?>>
				<rect x="580" y="<?php echo (int) $ground; ?>" width="540" height="58" fill="#251c16"/>
				<path d="M580 <?php echo (int) $ground; ?>v58M1120 <?php echo (int) $ground; ?>v58" stroke="#a88d6c" stroke-width="3"/>
			</g>

			<!-- Temel: grobeton, donatı, radye -->
			<rect class="a-fade" x="584" y="670" width="532" height="7" fill="#8f8a82"<?php echo $da( 0.19, 0.21 ); // phpcs:ignore ?>/>
			<path class="a-draw" pathLength="1" d="M592 646H1108M592 655H1108M592 664H1108<?php for ( $x = 600; $x <= 1100; $x += 20 ) { echo 'M' . (int) $x . ' 642V668'; } ?>" fill="none" stroke="#b5502a" stroke-width="1.6"<?php echo $da( 0.2, 0.25 ); // phpcs:ignore ?>/>
			<rect class="a-grow concrete" x="588" y="640" width="524" height="30"<?php echo $da( 0.245, 0.3 ); // phpcs:ignore ?>/>

			<!-- Betonarme karkas -->
			<g class="frame">
				<?php
				for ( $i = 0; $i < $floors; $i++ ) :
					$yb = $ground - $i * $fh;
					$yt = $yb - $fh;
					$s  = $f0 + $i * $fd;
					foreach ( $cols as $c ) :
						$y0 = $yt + 6;
						$y1 = 0 === $i ? 640 : $yb;
						?>
						<rect class="a-grow column" x="<?php echo (int) ( $c - 5 ); ?>" y="<?php echo (int) $y0; ?>" width="10" height="<?php echo (int) ( $y1 - $y0 ); ?>"<?php echo $da( $s, $s + 0.6 * $fd ); // phpcs:ignore ?>/>
					<?php endforeach; ?>
					<rect class="a-growx slab" x="594" y="<?php echo (int) $yt; ?>" width="332" height="6"<?php echo $da( $s + 0.5 * $fd, $s + $fd ); // phpcs:ignore ?>/>
					<?php
					if ( $i < $annex_n ) :
						foreach ( array_slice( $a_cols, 1 ) as $c ) :
							$y0 = $yt + 6;
							$y1 = 0 === $i ? 640 : $yb;
							?>
							<rect class="a-grow column" x="<?php echo (int) ( $c - 5 ); ?>" y="<?php echo (int) $y0; ?>" width="10" height="<?php echo (int) ( $y1 - $y0 ); ?>"<?php echo $da( $s, $s + 0.6 * $fd ); // phpcs:ignore ?>/>
						<?php endforeach; ?>
						<rect class="a-growx slab" x="920" y="<?php echo (int) $yt; ?>" width="186" height="6"<?php echo $da( $s + 0.5 * $fd, $s + $fd ); // phpcs:ignore ?>/>
					<?php endif; ?>
				<?php endfor; ?>
			</g>

			<!-- Cephe: kule cam giydirme, ek blok taş kaplama -->
			<g class="facade">
				<?php
				for ( $i = 0; $i < $floors; $i++ ) :
					$yb = $ground - $i * $fh;
					$yt = $yb - $fh;
					$s  = $c0 + $i * $cd;
					for ( $b = 0; $b < 4; $b++ ) :
						$x  = $cols[ $b ] + 5;
						$bs = $s + $b * 0.12 * $cd;
						$lit = mt_rand( 0, 100 ) < 58;
						?>
						<g class="a-growx"<?php echo $da( $bs, $bs + 0.55 * $cd ); // phpcs:ignore ?>>
							<rect x="<?php echo (int) $x; ?>" y="<?php echo (int) ( $yt + 6 ); ?>" width="70" height="26" fill="url(#mpa-glass)"/>
							<?php if ( $lit ) : ?>
								<rect class="a-fade lit" x="<?php echo (int) $x; ?>" y="<?php echo (int) ( $yt + 6 ); ?>" width="70" height="26"<?php $l = 0.9 + mt_rand( 0, 90 ) / 1000; echo $da( $l, $l + 0.02 ); // phpcs:ignore ?>/>
							<?php endif; ?>
							<path d="M<?php echo (int) ( $x + 23 ); ?> <?php echo (int) ( $yt + 6 ); ?>v26M<?php echo (int) ( $x + 47 ); ?> <?php echo (int) ( $yt + 6 ); ?>v26" stroke="#1f272e" stroke-width="1.2"/>
						</g>
						<?php
					endfor;
					?>
					<g class="a-fade cladding"<?php echo $da( $s, $s + 0.5 * $cd ); // phpcs:ignore ?>>
						<rect x="594" y="<?php echo (int) $yt; ?>" width="332" height="6"/>
						<?php foreach ( $cols as $c ) : ?>
							<rect x="<?php echo (int) ( $c - 5 ); ?>" y="<?php echo (int) ( $yt + 6 ); ?>" width="10" height="26"/>
						<?php endforeach; ?>
					</g>
					<?php
					if ( $i < $annex_n ) :
						for ( $b = 0; $b < 2; $b++ ) :
							$x   = $a_cols[ $b ] + 5;
							$w   = $a_cols[ $b + 1 ] - $a_cols[ $b ] - 10;
							$lit = mt_rand( 0, 100 ) < 65;
							?>
							<g class="a-fade"<?php echo $da( $s + 0.1 * $cd, $s + 0.7 * $cd ); // phpcs:ignore ?>>
								<rect class="stone" x="<?php echo (int) $x; ?>" y="<?php echo (int) ( $yt + 6 ); ?>" width="<?php echo (int) $w; ?>" height="26"/>
								<rect x="<?php echo (int) ( $x + 7 ); ?>" y="<?php echo (int) ( $yt + 12 ); ?>" width="<?php echo (int) ( $w - 14 ); ?>" height="14" fill="url(#mpa-glass-dark)"/>
								<?php if ( $lit ) : ?>
									<rect class="a-fade lit" x="<?php echo (int) ( $x + 7 ); ?>" y="<?php echo (int) ( $yt + 12 ); ?>" width="<?php echo (int) ( $w - 14 ); ?>" height="14"<?php $l = 0.9 + mt_rand( 0, 90 ) / 1000; echo $da( $l, $l + 0.02 ); // phpcs:ignore ?>/>
								<?php endif; ?>
							</g>
							<?php
						endfor;
						?>
						<g class="a-fade stone"<?php echo $da( $s, $s + 0.5 * $cd ); // phpcs:ignore ?>>
							<rect x="920" y="<?php echo (int) $yt; ?>" width="186" height="6"/>
							<rect x="1005" y="<?php echo (int) ( $yt + 6 ); ?>" width="10" height="26"/>
							<rect x="1095" y="<?php echo (int) ( $yt + 6 ); ?>" width="10" height="26"/>
						</g>
					<?php endif; ?>
				<?php endfor; ?>
			</g>

			<!-- Çatı, tabela, giriş -->
			<rect class="a-grow cladding" x="640" y="<?php echo (int) ( $top - 38 ); ?>" width="100" height="24"<?php echo $da( 0.77, 0.81 ); // phpcs:ignore ?>/>
			<g class="a-fade"<?php echo $da( 0.79, 0.82 ); // phpcs:ignore ?>>
				<path d="M700 <?php echo (int) ( $top - 38 ); ?>V<?php echo (int) ( $top - 70 ); ?>" stroke="#20272d" stroke-width="2"/>
				<circle class="blink" cx="700" cy="<?php echo (int) ( $top - 71 ); ?>" r="2.6" fill="#ff3b2f"/>
			</g>
			<rect class="a-grow cladding" x="592" y="<?php echo (int) ( $top - 16 ); ?>" width="336" height="16"<?php echo $da( 0.76, 0.8 ); // phpcs:ignore ?>/>
			<text class="sign a-fade" x="760" y="<?php echo (int) ( $top - 4 ); ?>" text-anchor="middle"<?php echo $da( 0.8, 0.84 ); // phpcs:ignore ?>><?php echo esc_html( $sign ); ?></text>
			<text class="sign sign--glow a-fade" x="760" y="<?php echo (int) ( $top - 4 ); ?>" text-anchor="middle"<?php echo $da( 0.93, 0.97 ); // phpcs:ignore ?>><?php echo esc_html( $sign ); ?></text>
			<rect class="a-grow stone" x="918" y="<?php echo (int) ( $a_top - 10 ); ?>" width="190" height="10"<?php echo $da( 0.76, 0.8 ); // phpcs:ignore ?>/>
			<g class="a-fade"<?php echo $da( 0.84, 0.88 ); // phpcs:ignore ?>>
				<rect x="728" y="590" width="64" height="5" fill="#20272d"/>
				<rect x="728" y="590" width="64" height="2" class="accent-fill"/>
				<rect x="748" y="595" width="24" height="25" fill="#1d2a35"/>
			</g>

			<!-- Şantiye perdesi -->
			<g class="a-grow"<?php echo $da( 0.1, 0.15 ) . $do( 0.84, 0.88 ); // phpcs:ignore ?>>
				<rect x="556" y="598" width="588" height="22" fill="#0f161b"/>
				<rect x="556" y="598" width="588" height="3" class="accent-fill"/>
				<?php foreach ( array( 660, 850, 1040 ) as $x ) : ?>
					<text class="hoarding-text" x="<?php echo (int) $x; ?>" y="614" text-anchor="middle">MPA GRUP İNŞAAT</text>
				<?php endforeach; ?>
			</g>

			<!-- Kule vinç -->
			<g clip-path="url(#mpa-above-ground)">
				<g class="a-crane crane"<?php echo $da( 0.2, 0.29 ) . $do( 0.85, 0.91 ); // phpcs:ignore ?>>
					<path class="crane-steel" d="M522 100V<?php echo (int) $ground; ?>M538 100V<?php echo (int) $ground; ?><?php for ( $y = 100; $y < $ground; $y += 16 ) { echo 'M522 ' . (int) $y . 'L538 ' . (int) ( $y + 16 ) . 'M522 ' . (int) ( $y + 16 ) . 'H538'; } ?>"/>
					<path class="crane-steel" d="M440 100H1040M440 110H1040<?php for ( $x = 440; $x < 1040; $x += 15 ) { echo 'M' . (int) $x . ' 110L' . (int) ( $x + 7 ) . ' 100L' . (int) ( $x + 15 ) . ' 110'; } ?>"/>
					<path class="crane-steel" d="M522 100L530 56L538 100M530 56L1040 100M530 56L440 100"/>
					<rect x="444" y="110" width="38" height="24" fill="#4a5258"/>
					<rect x="539" y="110" width="20" height="17" class="accent-fill"/>
					<rect x="548" y="113" width="8" height="7" fill="#cfe0ec"/>
					<g id="mpa-hook">
						<rect x="-9" y="110" width="18" height="6" fill="#20272d"/>
						<line class="hook-rope" x1="0" y1="116" x2="0" y2="300" stroke="#20272d" stroke-width="1"/>
						<g class="hook-body" transform="translate(0 300)">
							<path d="M0 0v6a4 4 0 1 1-4 4" fill="none" stroke="#20272d" stroke-width="2"/>
							<g class="hook-load">
								<path d="M0 6L-26 16M0 6L26 16" stroke="#20272d" stroke-width=".8"/>
								<rect x="-30" y="16" width="60" height="6" fill="#8a4a2b"/>
								<path d="M-30 18H30M-30 20H30" stroke="#5c311d" stroke-width=".8"/>
							</g>
						</g>
					</g>
				</g>
			</g>

			<!-- Peyzaj -->
			<?php
			$trees = array( 70, 150, 240, 330, 410, 470, 1150, 1185 );
			foreach ( $trees as $n => $x ) :
				$size = 0.8 + mt_rand( 0, 40 ) / 100;
				$s    = 0.84 + $n * 0.009;
				?>
				<g class="a-pop tree" transform="translate(<?php echo (int) $x; ?> <?php echo (int) $ground; ?>)"<?php echo $da( $s, $s + 0.04 ); // phpcs:ignore ?>>
					<g transform="scale(<?php echo esc_attr( number_format( $size, 2, '.', '' ) ); ?>)">
						<rect x="-2" y="-26" width="4" height="26" fill="#5a4636"/>
						<circle cx="0" cy="-38" r="17" fill="#5d7b47"/>
						<circle cx="-9" cy="-30" r="11" fill="#6c8c52"/>
						<circle cx="9" cy="-31" r="12" fill="#55733f"/>
					</g>
				</g>
			<?php endforeach; ?>
			<?php foreach ( array( 960, 1000, 1045, 1080 ) as $n => $x ) : ?>
				<circle class="a-pop" cx="<?php echo (int) $x; ?>" cy="<?php echo (int) ( $a_top - 14 ); ?>" r="7" fill="#5d7b47"<?php echo $da( 0.87 + $n * 0.008, 0.9 + $n * 0.008 ); // phpcs:ignore ?>/>
			<?php endforeach; ?>
			<?php foreach ( array( 572, 1132 ) as $x ) : ?>
				<g class="a-fade"<?php echo $da( 0.86, 0.89 ); // phpcs:ignore ?>>
					<circle class="a-fade" cx="<?php echo (int) ( $x + 6 ); ?>" cy="572" r="34" fill="url(#mpa-lamp-glow)"<?php echo $da( 0.93, 0.97 ); // phpcs:ignore ?>/>
					<path d="M<?php echo (int) $x; ?> <?php echo (int) $ground; ?>V570h10" stroke="#20272d" stroke-width="2.5" fill="none"/>
					<rect x="<?php echo (int) ( $x + 4 ); ?>" y="569" width="10" height="4" fill="#20272d"/>
				</g>
			<?php endforeach; ?>

			<!-- Aplikasyon: kazıklar ve lazer hattı -->
			<g<?php echo $do( 0.12, 0.15 ); // phpcs:ignore ?>>
				<path class="a-draw" pathLength="1" d="M560 <?php echo (int) ( $ground - 3 ); ?>H1140" stroke="#eb531e" stroke-width="1.4"<?php echo $da( 0.04, 0.1 ); // phpcs:ignore ?>/>
				<?php foreach ( array( 580, 760, 940, 1120 ) as $n => $x ) : ?>
					<g class="a-pop"<?php echo $da( 0.03 + $n * 0.01, 0.05 + $n * 0.01 ); // phpcs:ignore ?>>
						<path d="M<?php echo (int) $x; ?> <?php echo (int) $ground; ?>V<?php echo (int) ( $ground - 22 ); ?>" stroke="#5a4636" stroke-width="2"/>
						<path d="M<?php echo (int) $x; ?> <?php echo (int) ( $ground - 22 ); ?>l10 4-10 4z" class="accent-fill"/>
					</g>
				<?php endforeach; ?>
			</g>

			<!-- Teknik çizim katmanı (katalog paftası) -->
			<g class="bp-paper"<?php echo $do( 0.07, 0.15 ); // phpcs:ignore ?>>
				<rect x="-3000" y="<?php echo (int) $ground; ?>" width="7200" height="1400" class="paper-fill"/>
				<rect x="-3000" y="<?php echo (int) $ground; ?>" width="7200" height="1400" fill="url(#mpa-grid)"/>
				<path d="M-3000 <?php echo (int) $ground; ?>H4200" stroke="#0f161b" stroke-width="1.4"/>
				<path d="M-3000 <?php echo (int) ( $ground + 4 ); ?>H4200" stroke="#0f161b" stroke-width="5" stroke-dasharray="1 6" stroke-opacity=".5"/>
			</g>
			<rect x="-3000" y="-1000" width="7200" height="<?php echo (int) ( 1000 + $ground ); ?>" fill="url(#mpa-grid)"<?php echo $do( 0.08, 0.3 ); // phpcs:ignore ?>/>

			<g class="bp-lines"<?php echo $do( 0.48, 0.7 ); // phpcs:ignore ?>>
				<rect x="600" y="<?php echo (int) $top; ?>" width="320" height="<?php echo (int) ( $ground - $top ); ?>"/>
				<rect x="920" y="<?php echo (int) $a_top; ?>" width="180" height="<?php echo (int) ( $ground - $a_top ); ?>"/>
				<rect x="640" y="<?php echo (int) ( $top - 38 ); ?>" width="100" height="22"/>
				<rect x="592" y="<?php echo (int) ( $top - 16 ); ?>" width="336" height="16"/>
				<path class="bp-thin" d="<?php
				for ( $i = 1; $i < $floors; $i++ ) {
					echo 'M600 ' . (int) ( $ground - $i * $fh ) . 'H920';
				}
				for ( $i = 1; $i < $annex_n; $i++ ) {
					echo 'M920 ' . (int) ( $ground - $i * $fh ) . 'H1100';
				}
				?>"/>
				<path class="bp-axis" d="<?php
				foreach ( array_merge( $cols, array_slice( $a_cols, 1 ) ) as $c ) {
					echo 'M' . (int) $c . ' ' . (int) ( $top - 56 ) . 'V' . (int) ( $ground + 70 );
				}
				?>"/>
				<?php foreach ( array_merge( $cols, array_slice( $a_cols, 1 ) ) as $n => $c ) : ?>
					<circle cx="<?php echo (int) $c; ?>" cy="<?php echo (int) ( $top - 66 ); ?>" r="10"/>
					<text class="bp-label" x="<?php echo (int) $c; ?>" y="<?php echo (int) ( $top - 62 ); ?>" text-anchor="middle"><?php echo esc_html( chr( 65 + $n ) ); ?></text>
				<?php endforeach; ?>
				<path d="M572 <?php echo (int) $top; ?>V<?php echo (int) $ground; ?>M566 <?php echo (int) $top; ?>H578M566 <?php echo (int) $ground; ?>H578"/>
				<text class="bp-label" transform="translate(566 <?php echo (int) ( ( $top + $ground ) / 2 ); ?>) rotate(-90)" text-anchor="middle"><?php echo esc_html( $height ); ?></text>
				<?php
				$levels = array(
					array( 1130, $ground, '±0.00' ),
					array( 1130, $a_top, '+' . number_format( $annex_n * 3.2, 2, '.', '' ) ),
					array( 560, $top, '+' . $height ),
				);
				foreach ( $levels as $lv ) :
					?>
					<g class="bp-level" transform="translate(<?php echo (int) $lv[0]; ?> <?php echo (int) $lv[1]; ?>)">
						<path d="M-7 -9h14l-7 9z"/>
						<path d="M-7 -9h40" class="bp-thin"/>
						<text x="10" y="-13"><?php echo esc_html( $lv[2] ); ?></text>
					</g>
				<?php endforeach; ?>
			</g>

			<g class="bp-titleblock"<?php echo $do( 0.02, 0.05 ); // phpcs:ignore ?>>
				<rect x="840" y="702" width="340" height="62"/>
				<path d="M840 724H1180M960 702V764M1080 702V764"/>
				<text class="bp-key" x="848" y="716">FİRMA</text>
				<text class="bp-val" x="848" y="748"><?php echo esc_html( mb_strtoupper( mpa_opt( 'company_name' ), 'UTF-8' ) ); ?></text>
				<text class="bp-key" x="968" y="716">PAFTA</text>
				<text class="bp-val" x="968" y="748">KESİT A-A</text>
				<text class="bp-key" x="1088" y="716">ÖLÇEK</text>
				<text class="bp-val" x="1088" y="748">ÖLÇEKSİZ</text>
			</g>
		</svg>

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
			<div class="hud-cell"><span class="hud-key"><?php esc_html_e( 'Kat', 'mpa-grup' ); ?></span><span class="hud-val"><b data-hud="floor">00</b>/<?php echo (int) $floors; ?></span></div>
			<div class="hud-cell"><span class="hud-key"><?php esc_html_e( 'Kot', 'mpa-grup' ); ?></span><span class="hud-val">+<b data-hud="level">0.00</b></span></div>
		</div>

		<a class="mpa-build__skip" href="#hakkimizda"><?php esc_html_e( 'Animasyonu geç', 'mpa-grup' ); ?> <?php echo mpa_icon( 'down' ); // phpcs:ignore ?></a>
	</div>
</section>
