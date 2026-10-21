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
	var media = build.querySelector('.mpa-build__media');
	var video = build.querySelector('.mpa-build__video');
	var phases = stage.getAttribute('data-phases').split(',').map(Number);
	var hud = {};
	stage.querySelectorAll('[data-hud]').forEach(function (el) {
		hud[el.getAttribute('data-hud')] = el;
	});
	var phaseItems = stage.querySelectorAll('.phase-item');
	var phaseNames = [].map.call(stage.querySelectorAll('.phase-item__title'), function (el) {
		return el.textContent;
	});
	var lastPhase = -1;
	var lastMode = '';

	// Zaman çizelgesi (kaydırma ilerlemesi 0–1).
	var ROUGH = [0.1, 0.6];  // kaba inşaat zeminden çatıya
	var DONE = [0.6, 0.88];  // cephe ve renkler
	var VIDEO = [0.03, 0.92]; // video baştan sona

	function span(p, r) {
		return clamp((p - r[0]) / (r[1] - r[0]), 0, 1);
	}

	function setText(el, value) {
		if (el && el.textContent !== value) {
			el.textContent = value;
		}
	}

	/* Video: kaydırmaya göre kare kare ileri/geri. Dosya belleğe alınır; böylece
	   sunucu kısmi indirmeyi desteklemese de her kareye anında gidilebilir. */
	var videoTarget = 0;
	var seeking = false;
	var seekStarted = 0;
	if (video) {
		video.pause();
		video.addEventListener('seeked', function () {
			seeking = false;
			seekVideo();
		});
		video.addEventListener('loadedmetadata', seekVideo);

		var source = [].filter.call(video.querySelectorAll('source'), function (el) {
			return video.canPlayType(el.type) !== '';
		})[0];
		if (source && window.fetch && window.URL) {
			fetch(source.src).then(function (res) {
				return res.ok ? res.blob() : null;
			}).then(function (blob) {
				if (blob) {
					video.src = URL.createObjectURL(blob);
				}
			}).catch(function () {});
		}

		// iOS Safari karelerin çizilmesi için bir kez oynatılmasını ister.
		var unlock = function () {
			var play = video.play();
			if (play && play.then) {
				play.then(function () { video.pause(); seekVideo(); }).catch(function () {});
			}
			window.removeEventListener('touchstart', unlock);
		};
		window.addEventListener('touchstart', unlock, { passive: true });
	}

	function seekVideo() {
		if (!video || !video.duration) {
			return;
		}
		if (seeking && Date.now() - seekStarted < 400) {
			return;
		}
		var time = videoTarget * (video.duration - 0.05);
		if (Math.abs(video.currentTime - time) > 0.02) {
			seeking = true;
			seekStarted = Date.now();
			video.currentTime = time;
		}
	}

	function render(p) {
		if (video) {
			videoTarget = span(p, VIDEO);
			seekVideo();
		} else {
			var rough = smooth(span(p, ROUGH));
			var done = smooth(span(p, DONE));
			stage.style.setProperty('--rough-top', ((1 - rough) * 100).toFixed(2) + '%');
			stage.style.setProperty('--done-top', ((1 - done) * 100).toFixed(2) + '%');
			var active = p < DONE[0] ? rough : done;
			var building = (p > ROUGH[0] && p < ROUGH[1]) || (p > DONE[0] && p < DONE[1]);
			stage.style.setProperty('--laser', ((1 - active) * 100).toFixed(2) + '%');
			stage.style.setProperty('--laser-o', building ? '1' : '0');
		}
		media.style.setProperty('--zoom', (1.1 - 0.1 * smooth(p)).toFixed(4));
		stage.style.setProperty('--shade', clamp((p - 0.02) / 0.06, 0, 1).toFixed(3));

		setText(hud.pct, String(Math.round(p * 100)));
		if (hud.bar) {
			hud.bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
		}

		var phase = 0;
		for (var i = 0; i < phases.length; i++) {
			if (p >= phases[i]) {
				phase = i;
			}
		}
		if (phase !== lastPhase) {
			phaseItems.forEach(function (el, n) {
				el.classList.toggle('is-active', n === phase);
			});
			setText(hud.phase, (phase < 9 ? '0' : '') + (phase + 1));
			setText(hud.name, phaseNames[phase] || '');
			lastPhase = phase;
		}

		var mode = p < 0.03 ? 'intro' : p >= phases[phases.length - 1] ? 'final' : 'phase';
		if (mode !== lastMode) {
			stage.classList.remove('is-intro', 'is-phase', 'is-final');
			stage.classList.add('is-' + mode);
			lastMode = mode;
		}
	}

	if (reduceMotion) {
		render(1);
		stage.classList.add('is-static');
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
		current = current < 0 ? target : current + (target - current) * 0.14;
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

	onScroll();
	window.addEventListener('scroll', onScroll, { passive: true });
	window.addEventListener('resize', onScroll);
})();
