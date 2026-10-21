/**
 * MPA Grup — kaydırmaya bağlı inşaat animasyonu, menü ve görünür olma efektleri.
 */
(function () {
	'use strict';

	var root = document.documentElement;
	var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	function clamp(v, min, max) {
		return v < min ? min : v > max ? max : v;
	}

	function smooth(t) {
		return t * t * (3 - 2 * t);
	}

	function lerp(a, b, t) {
		return a + (b - a) * t;
	}

	/* ---------- Menü ---------- */
	var header = document.querySelector('.site-header');
	var toggle = document.querySelector('.nav-toggle');

	if (toggle) {
		toggle.addEventListener('click', function () {
			var open = toggle.getAttribute('aria-expanded') !== 'true';
			toggle.setAttribute('aria-expanded', String(open));
			document.body.classList.toggle('nav-open', open);
		});
		document.querySelectorAll('.main-nav a').forEach(function (link) {
			link.addEventListener('click', function () {
				toggle.setAttribute('aria-expanded', 'false');
				document.body.classList.remove('nav-open');
			});
		});
	}

	function onScrollHeader() {
		if (header) {
			header.classList.toggle('is-scrolled', window.scrollY > 8);
		}
	}
	window.addEventListener('scroll', onScrollHeader, { passive: true });
	onScrollHeader();

	/* ---------- Görünür olunca belirme ---------- */
	var reveals = document.querySelectorAll('.reveal');
	if ('IntersectionObserver' in window && !reduceMotion) {
		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (entry) {
				if (entry.isIntersecting) {
					entry.target.classList.add('is-in');
					io.unobserve(entry.target);
				}
			});
		}, { rootMargin: '0px 0px -8% 0px' });
		reveals.forEach(function (el) { io.observe(el); });
	} else {
		reveals.forEach(function (el) { el.classList.add('is-in'); });
	}

	/* ---------- İnşaat sahnesi ---------- */
	var build = document.querySelector('.mpa-build');
	if (!build) {
		return;
	}

	var stage = build.querySelector('.mpa-build__stage');
	var svg = build.querySelector('.mpa-build__svg');
	var GROUND = 620;
	var FLOOR_H = 32;
	var phases = stage.getAttribute('data-phases').split(',').map(Number);
	var frame = stage.getAttribute('data-frame').split(',').map(Number);
	var floors = Number(stage.getAttribute('data-floors'));

	function range(attr) {
		if (!attr) {
			return null;
		}
		var parts = attr.split(',');
		return [Number(parts[0]), Number(parts[1])];
	}

	var items = [];
	svg.querySelectorAll('[data-a],[data-o]').forEach(function (el) {
		items.push({
			el: el,
			a: range(el.getAttribute('data-a')),
			o: range(el.getAttribute('data-o')),
			ta: '',
			to: ''
		});
	});

	function local(p, r) {
		return smooth(clamp((p - r[0]) / (r[1] - r[0]), 0, 1));
	}

	// Gökyüzü: kâğıt (çizim) → sabah → gün → gün batımı → akşam.
	var SKY = [
		[0.00, [243, 242, 238], [236, 234, 228]],
		[0.10, [236, 238, 238], [234, 232, 226]],
		[0.25, [136, 178, 212], [222, 232, 238]],
		[0.55, [92, 150, 204], [208, 226, 238]],
		[0.80, [86, 110, 160], [242, 196, 150]],
		[0.92, [42, 48, 86], [220, 136, 98]],
		[1.00, [17, 21, 40], [104, 66, 82]]
	];

	function skyAt(p) {
		for (var i = 1; i < SKY.length; i++) {
			if (p <= SKY[i][0]) {
				var t = (p - SKY[i - 1][0]) / (SKY[i][0] - SKY[i - 1][0]);
				return [mix(SKY[i - 1][1], SKY[i][1], t), mix(SKY[i - 1][2], SKY[i][2], t)];
			}
		}
		return [SKY[SKY.length - 1][1], SKY[SKY.length - 1][2]];
	}

	function mix(a, b, t) {
		return 'rgb(' + Math.round(lerp(a[0], b[0], t)) + ',' + Math.round(lerp(a[1], b[1], t)) + ',' + Math.round(lerp(a[2], b[2], t)) + ')';
	}

	var sun = svg.querySelector('#mpa-sun');
	var sunDisc = sun.querySelector('.sun-disc');
	var hook = svg.querySelector('#mpa-hook');
	var rope = hook.querySelector('.hook-rope');
	var hookBody = hook.querySelector('.hook-body');
	var hookLoad = hook.querySelector('.hook-load');
	var hud = {};
	stage.querySelectorAll('[data-hud]').forEach(function (el) {
		hud[el.getAttribute('data-hud')] = el;
	});
	var phaseItems = stage.querySelectorAll('.phase-item');
	var lastPhase = -1;
	var lastMode = '';

	function setText(el, value) {
		if (el && el.textContent !== value) {
			el.textContent = value;
		}
	}

	function hookY(p) {
		var top = GROUND - floors * FLOOR_H - 46;
		if (p < 0.26) {
			return 300;
		}
		if (p < frame[0]) {
			return lerp(300, GROUND - 46, smooth((p - 0.26) / (frame[0] - 0.26)));
		}
		if (p < frame[1]) {
			return GROUND - 46 - (p - frame[0]) / (frame[1] - frame[0]) * floors * FLOOR_H;
		}
		if (p < 0.8) {
			return top;
		}
		return lerp(top, 128, smooth(clamp((p - 0.8) / 0.05, 0, 1)));
	}

	function render(p) {
		var i, item, v;
		for (i = 0; i < items.length; i++) {
			item = items[i];
			if (item.a) {
				v = local(p, item.a).toFixed(3);
				if (v !== item.ta) {
					item.el.style.setProperty('--t', v);
					item.ta = v;
				}
			}
			if (item.o) {
				v = local(p, item.o).toFixed(3);
				if (v !== item.to) {
					item.el.style.setProperty('--o', v);
					item.to = v;
				}
			}
		}

		var sky = skyAt(p);
		stage.style.setProperty('--sky-top', sky[0]);
		stage.style.setProperty('--sky-bottom', sky[1]);

		// Güneş sol üstten ufka iner.
		var s = clamp((p - 0.14) / 0.84, 0, 1);
		var sunOpacity = clamp((p - 0.14) / 0.08, 0, 1) * (1 - clamp((p - 0.95) / 0.05, 0, 1));
		sun.setAttribute('transform', 'translate(' + (430 - s * 300).toFixed(1) + ' ' + (130 + s * s * 500).toFixed(1) + ')');
		sun.setAttribute('opacity', sunOpacity.toFixed(3));
		sunDisc.setAttribute('fill', mix([255, 244, 220], [255, 128, 64], s * s));

		// Vinç kancası katla birlikte yükselir, araba bom üzerinde gezinir.
		var hy = hookY(p);
		var hx = p < 0.8 ? 760 + Math.sin(p * 38) * 90 : 760;
		hook.setAttribute('transform', 'translate(' + hx.toFixed(1) + ' 0)');
		rope.setAttribute('y2', hy.toFixed(1));
		hookBody.setAttribute('transform', 'translate(0 ' + hy.toFixed(1) + ')');
		hookLoad.style.opacity = p > 0.27 && p < frame[1] ? 1 : 0;

		// Gösterge.
		var built = Math.floor(clamp((p - frame[0]) / (frame[1] - frame[0]), 0, 1) * floors + 0.0001);
		setText(hud.pct, String(Math.round(p * 100)));
		setText(hud.floor, (built < 10 ? '0' : '') + built);
		setText(hud.level, (built * 3.2).toFixed(2));
		if (hud.bar) {
			hud.bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
		}

		var phase = 0;
		for (i = 0; i < phases.length; i++) {
			if (p >= phases[i]) {
				phase = i;
			}
		}
		if (phase !== lastPhase) {
			phaseItems.forEach(function (el, n) {
				el.classList.toggle('is-active', n === phase);
			});
			setText(hud.phase, (phase < 9 ? '0' : '') + (phase + 1));
			lastPhase = phase;
		}

		var mode = p < 0.03 ? 'intro' : p >= phases[phases.length - 1] ? 'final' : 'phase';
		if (mode !== lastMode) {
			stage.classList.remove('is-intro', 'is-phase', 'is-final');
			stage.classList.add('is-' + mode);
			lastMode = mode;
		}
		stage.classList.toggle('is-dark', p > 0.86);
	}

	// Dar ekranda sahne binaya yakınlaşır.
	function fit() {
		var ratio = stage.clientWidth / stage.clientHeight;
		var box = ratio < 0.8 ? '485 40 680 770' : ratio < 1.25 ? '330 10 860 790' : '20 30 1170 770';
		if (svg.getAttribute('viewBox') !== box) {
			svg.setAttribute('viewBox', box);
		}
	}

	if (reduceMotion) {
		fit();
		render(1);
		stage.classList.add('is-static');
		window.addEventListener('resize', fit);
		return;
	}

	var target = 0;
	var current = -1;
	var raf = 0;

	function progress() {
		var total = build.offsetHeight - window.innerHeight;
		return total > 0 ? clamp(-build.getBoundingClientRect().top / total, 0, 1) : 1;
	}

	function tick() {
		current = current < 0 ? target : current + (target - current) * 0.16;
		if (Math.abs(target - current) < 0.0004) {
			current = target;
		}
		render(current);
		raf = current !== target ? requestAnimationFrame(tick) : 0;
	}

	function onScroll() {
		target = progress();
		if (!raf) {
			raf = requestAnimationFrame(tick);
		}
	}

	fit();
	onScroll();
	window.addEventListener('scroll', onScroll, { passive: true });
	window.addEventListener('resize', function () {
		fit();
		onScroll();
	});
})();
