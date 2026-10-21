/**
 * MPA Grup: kaydırmaya bağlı inşaat animasyonu, menü ve görünür olma efektleri.
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

	/* ---------- Giriş ekranı ---------- */
	var pre = document.querySelector('.preloader');
	var prePct = pre ? pre.querySelector('.preloader__pct') : null;
	var preShown = 0;
	var preDone = !pre || root.classList.contains('seen');

	function preloaderSet(f) {
		if (preDone || f < preShown) {
			return;
		}
		preShown = f;
		pre.style.setProperty('--load', f.toFixed(3));
		prePct.textContent = String(Math.round(f * 100));
	}

	function preloaderDone() {
		if (preDone) {
			return;
		}
		preloaderSet(1);
		preDone = true;
		setTimeout(function () {
			pre.classList.add('is-done');
		}, 300);
		try {
			sessionStorage.setItem('mpaSeen', '1');
		} catch (e) {}
	}

	if (!preDone) {
		// Gerçek ilerleme gelmezse bile çubuk yavaşça dolar; en geç 6 sn'de açılır.
		var fake = 0;
		var fakeTimer = setInterval(function () {
			fake = Math.min(0.85, fake + 0.04);
			preloaderSet(fake);
			if (preDone) {
				clearInterval(fakeTimer);
			}
		}, 120);
		setTimeout(preloaderDone, 6000);
		if (!document.querySelector('.mpa-build__video')) {
			window.addEventListener('load', preloaderDone);
		}
	}

	/* ---------- Menü ---------- */
	var header = document.querySelector('.site-header');
	var toggle = document.querySelector('.nav-toggle');
	var heroEl = document.querySelector('.mpa-build') || document.querySelector('.page-hero--image');
	var hasHero = document.body.classList.contains('has-hero') && heroEl;

	function updateHeader() {
		if (!header) {
			return;
		}
		var solid = true;
		if (hasHero) {
			solid = heroEl.getBoundingClientRect().bottom <= header.offsetHeight + 1;
		}
		header.classList.toggle('is-solid', solid || document.body.classList.contains('nav-open'));
		header.classList.toggle('is-scrolled', window.scrollY > 8);
	}

	if (toggle) {
		toggle.addEventListener('click', function () {
			var open = toggle.getAttribute('aria-expanded') !== 'true';
			toggle.setAttribute('aria-expanded', String(open));
			document.body.classList.toggle('nav-open', open);
			updateHeader();
		});
		document.querySelectorAll('.main-nav a').forEach(function (link) {
			link.addEventListener('click', function () {
				toggle.setAttribute('aria-expanded', 'false');
				document.body.classList.remove('nav-open');
				updateHeader();
			});
		});
	}
	window.addEventListener('scroll', updateHeader, { passive: true });
	window.addEventListener('resize', updateHeader);
	updateHeader();

	/* ---------- Görünür olunca belirme ---------- */
	var reveals = document.querySelectorAll('.reveal, .reveal-img');
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

	/* ---------- Kaydırdıkça kelime kelime aydınlanan cümle ---------- */
	document.querySelectorAll('[data-words]').forEach(function (el) {
		var words = [];
		(function split(node) {
			[].slice.call(node.childNodes).forEach(function (child) {
				if (child.nodeType === 3) {
					var frag = document.createDocumentFragment();
					child.textContent.split(/(\s+)/).forEach(function (part) {
						if (!part) {
							return;
						}
						if (/^\s+$/.test(part)) {
							frag.appendChild(document.createTextNode(part));
						} else {
							var span = document.createElement('span');
							span.className = 'w';
							span.textContent = part;
							frag.appendChild(span);
							words.push(span);
						}
					});
					node.replaceChild(frag, child);
				} else if (child.nodeType === 1) {
					split(child);
				}
			});
		})(el);

		if (reduceMotion) {
			words.forEach(function (w) { w.classList.add('is-lit'); });
			return;
		}
		var lit = -1;
		function light() {
			var r = el.getBoundingClientRect();
			var vh = window.innerHeight;
			var f = clamp((vh * 0.85 - r.top) / (r.height + vh * 0.35), 0, 1);
			var n = Math.round(f * words.length);
			if (n !== lit) {
				words.forEach(function (w, i) { w.classList.toggle('is-lit', i < n); });
				lit = n;
			}
		}
		window.addEventListener('scroll', light, { passive: true });
		window.addEventListener('resize', light);
		light();
	});

	/* ---------- Tam ekran galeri ---------- */
	document.querySelectorAll('[data-lightbox]').forEach(function (box) {
		var imgs = [].slice.call(box.querySelectorAll('img'));
		if (!imgs.length) {
			return;
		}
		var lb = document.createElement('div');
		lb.className = 'lightbox';
		lb.setAttribute('role', 'dialog');
		lb.setAttribute('aria-modal', 'true');
		lb.setAttribute('aria-label', 'Galeri');
		var arrow = '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
		lb.innerHTML = '<p class="lightbox__cap"></p>' +
			'<button type="button" class="lightbox__btn lightbox__close" aria-label="Kapat">&times;</button>' +
			'<button type="button" class="lightbox__btn lightbox__prev" aria-label="Önceki">' + arrow + '</button>' +
			'<button type="button" class="lightbox__btn lightbox__next" aria-label="Sonraki">' + arrow + '</button>';
		document.body.appendChild(lb);
		var big = null;
		var cap = lb.querySelector('.lightbox__cap');
		var current = 0;
		var opener = null;

		function largest(img) {
			var best = img.currentSrc || img.src;
			var max = 0;
			(img.getAttribute('srcset') || '').split(',').forEach(function (c) {
				var parts = c.trim().split(/\s+/);
				var w = parseInt(parts[1], 10) || 0;
				if (w > max) {
					max = w;
					best = parts[0];
				}
			});
			return best;
		}
		function show(i) {
			current = (i + imgs.length) % imgs.length;
			var img = imgs[current];
			var fig = img.closest('figure');
			var fc = fig ? fig.querySelector('figcaption') : null;
			if (!big) {
				big = document.createElement('img');
				big.className = 'lightbox__img';
				lb.insertBefore(big, lb.firstChild);
			}
			big.src = largest(img);
			big.alt = img.alt || '';
			cap.textContent = (fc ? fc.textContent + ' · ' : '') + (current + 1) + ' / ' + imgs.length;
		}
		function open(i) {
			opener = document.activeElement;
			show(i);
			lb.classList.add('is-open');
			document.documentElement.style.overflow = 'hidden';
			lb.querySelector('.lightbox__close').focus();
		}
		function close() {
			lb.classList.remove('is-open');
			document.documentElement.style.overflow = '';
			if (opener && opener.focus) {
				opener.focus();
			}
		}
		imgs.forEach(function (img, i) {
			img.setAttribute('tabindex', '0');
			img.setAttribute('role', 'button');
			img.addEventListener('click', function () { open(i); });
			img.addEventListener('keydown', function (e) {
				if (e.key === 'Enter' || e.key === ' ') {
					e.preventDefault();
					open(i);
				}
			});
		});
		lb.querySelector('.lightbox__close').addEventListener('click', close);
		lb.querySelector('.lightbox__prev').addEventListener('click', function () { show(current - 1); });
		lb.querySelector('.lightbox__next').addEventListener('click', function () { show(current + 1); });
		lb.addEventListener('click', function (e) {
			if (e.target === lb) {
				close();
			}
		});
		document.addEventListener('keydown', function (e) {
			if (!lb.classList.contains('is-open')) {
				return;
			}
			if (e.key === 'Escape') {
				close();
			} else if (e.key === 'ArrowLeft') {
				show(current - 1);
			} else if (e.key === 'ArrowRight') {
				show(current + 1);
			}
		});
		var startX = null;
		lb.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
		lb.addEventListener('touchend', function (e) {
			if (startX === null) {
				return;
			}
			var dx = e.changedTouches[0].clientX - startX;
			if (Math.abs(dx) > 50) {
				show(current + (dx < 0 ? 1 : -1));
			}
			startX = null;
		});
	});

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
	var steps = stage.querySelectorAll('.timeline__step');
	var lastPhase = -1;
	var lastMode = '';

	// Zaman çizelgesi (kaydırma ilerlemesi 0–1).
	var ROUGH = [0.1, 0.6];  // kaba inşaat zeminden çatıya
	var DONE = [0.6, 0.88];  // cephe ve renkler
	var VIDEO = (stage.getAttribute('data-video') || '0.06,0.92').split(',').map(Number); // video baştan sona

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
		video.addEventListener('loadeddata', preloaderDone);
		video.addEventListener('error', preloaderDone);
		if (source && window.fetch && window.URL) {
			fetch(source.src).then(function (res) {
				if (!res.ok) {
					return null;
				}
				var total = parseInt(res.headers.get('Content-Length'), 10) || 0;
				if (!total || !res.body || !res.body.getReader) {
					return res.blob();
				}
				// Giriş ekranındaki çubuk videonun gerçek indirme ilerlemesini gösterir.
				var reader = res.body.getReader();
				var chunks = [];
				var got = 0;
				return (function pump() {
					return reader.read().then(function (step) {
						if (step.done) {
							return new Blob(chunks, { type: source.type || 'video/mp4' });
						}
						chunks.push(step.value);
						got += step.value.length;
						preloaderSet(Math.min(0.98, got / total));
						return pump();
					});
				})();
			}).then(function (blob) {
				if (blob) {
					video.src = URL.createObjectURL(blob);
				} else {
					preloaderDone();
				}
			}).catch(preloaderDone);
		} else {
			preloaderDone();
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

	// Telefonda arka plandaki bulanık kopya: o anki kare küçük bir tuvale çizilir.
	var blur = build.querySelector('.mpa-build__blur');
	var blurCtx = blur && blur.getContext ? blur.getContext('2d') : null;
	function paintBlur(src) {
		if (!blurCtx || blur.offsetParent === null) {
			return;
		}
		try {
			blurCtx.drawImage(src, 0, 0, blur.width, blur.height);
		} catch (e) {}
	}
	if (blurCtx && video) {
		var poster = new Image();
		poster.onload = function () { paintBlur(poster); };
		poster.src = video.getAttribute('poster');
		video.addEventListener('seeked', function () { paintBlur(video); });
		video.addEventListener('loadeddata', function () { paintBlur(video); });
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
		setText(hud.pct, String(Math.round(p * 100)));

		var phase = 0;
		for (var i = 0; i < phases.length; i++) {
			if (p >= phases[i]) {
				phase = i;
			}
		}

		// Zaman çizgisi: noktalar eşit aralıklı; dolgu her aşamanın kendi süresi içinde ilerler.
		if (hud.bar) {
			var last = phases.length - 1;
			var within = phase < last ? clamp((p - phases[phase]) / (phases[phase + 1] - phases[phase]), 0, 1) : 0;
			hud.bar.style.transform = 'scaleX(' + ((phase + within) / last).toFixed(4) + ')';
		}

		if (phase !== lastPhase) {
			phaseItems.forEach(function (el, n) {
				el.classList.toggle('is-active', n === phase);
			});
			steps.forEach(function (el, n) {
				el.classList.toggle('is-active', n === phase);
				el.classList.toggle('is-done', n < phase);
			});
			setText(hud.phase, String(phase + 1));
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
