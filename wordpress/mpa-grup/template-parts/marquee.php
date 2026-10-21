<?php
/**
 * Kayan uzmanlık bandı.
 *
 * @package MPA_Grup
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$words = wp_list_pluck( mpa_items( 'service', 3 ), 'title' );
if ( ! $words ) {
	return;
}
$line = '';
foreach ( $words as $i => $word ) {
	$line .= '<span class="marquee__word' . ( $i % 2 ? ' is-outline' : '' ) . '">' . esc_html( $word ) . '</span><span class="marquee__star" aria-hidden="true">✦</span>';
}
?>
<div class="marquee" aria-label="<?php echo esc_attr( implode( ', ', $words ) ); ?>">
	<div class="marquee__track" aria-hidden="true">
		<div class="marquee__group"><?php echo $line . $line; // phpcs:ignore ?></div>
		<div class="marquee__group"><?php echo $line . $line; // phpcs:ignore ?></div>
	</div>
</div>
