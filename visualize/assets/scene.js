/* ==========================================================================
   scene.js — 단계(step) 기반 애니메이션 엔진
   --------------------------------------------------------------------------
   사용법 (HTML)
     <section class="scene" data-scene="이름" data-steps="4" data-speed="1800">
       <div class="stage">
         <div data-at="2">step 2에서만 보임</div>
         <div data-from="3">step 3부터 계속 보임</div>
         <div data-from="2" data-until="3">step 2~3 구간만 보임</div>
       </div>
       <div class="captions">
         <p data-cap="1"><span class="k">01</span>설명</p>
       </div>
     </section>

   - 엔진이 scene 루트에 data-step="N" 을 써주므로,
     페이지별 CSS에서 [data-step="3"] 조합으로 자유롭게 상태를 바꿀 수 있다.
   - 뷰포트에 들어오면 자동 재생, 나가면 정지한다.
   - prefers-reduced-motion 이면 자동 재생하지 않고 마지막 단계를 바로 보여준다.
   ========================================================================== */

(function () {
  'use strict';

  var reduceMotion =
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /** "2" 또는 "2,4" 형태를 숫자 배열로 */
  function parseList(v) {
    return String(v)
      .split(',')
      .map(function (s) { return parseInt(s.trim(), 10); })
      .filter(function (n) { return !isNaN(n); });
  }

  function Scene(root) {
    this.root = root;
    this.total = parseInt(root.dataset.steps || '1', 10);
    this.speed = parseInt(root.dataset.speed || '1900', 10);
    this.step = 0;
    this.timer = null;
    this.playing = false;
    this.started = false;

    this.targets = Array.prototype.slice.call(
      root.querySelectorAll('[data-at],[data-from],[data-until]')
    );
    this.caps = Array.prototype.slice.call(
      root.querySelectorAll('[data-cap]')
    );

    this.buildPlayer();
    this.render();
  }

  Scene.prototype.buildPlayer = function () {
    var self = this;
    var bar = this.root.querySelector('.player');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'player';
      this.root.appendChild(bar);
    }

    var name = this.root.dataset.scene || 'scene';

    this.btnPlay = document.createElement('button');
    this.btnPlay.type = 'button';
    this.btnPlay.className = 'primary';
    this.btnPlay.textContent = '▶ 재생';
    this.btnPlay.setAttribute('aria-label', name + ' 애니메이션 재생');

    this.btnPrev = document.createElement('button');
    this.btnPrev.type = 'button';
    this.btnPrev.textContent = '◀ 이전';
    this.btnPrev.setAttribute('aria-label', name + ' 이전 단계');

    this.btnNext = document.createElement('button');
    this.btnNext.type = 'button';
    this.btnNext.textContent = '다음 ▶';
    this.btnNext.setAttribute('aria-label', name + ' 다음 단계');

    this.dots = document.createElement('div');
    this.dots.className = 'dots';
    this.dots.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < this.total; i++) {
      this.dots.appendChild(document.createElement('i'));
    }

    this.readout = document.createElement('span');
    this.readout.className = 'stepno';
    this.readout.setAttribute('role', 'status');
    this.readout.setAttribute('aria-live', 'polite');

    bar.appendChild(this.btnPlay);
    bar.appendChild(this.btnPrev);
    bar.appendChild(this.btnNext);
    bar.appendChild(this.dots);
    bar.appendChild(this.readout);

    this.btnPlay.addEventListener('click', function () {
      self.playing ? self.pause() : self.play();
    });
    this.btnPrev.addEventListener('click', function () {
      self.pause();
      self.go(self.step - 1);
    });
    this.btnNext.addEventListener('click', function () {
      self.pause();
      self.go(self.step + 1 > self.total ? 1 : self.step + 1);
    });
  };

  Scene.prototype.render = function () {
    var s = this.step;
    this.root.dataset.step = String(s);

    this.targets.forEach(function (el) {
      var on = true;
      if (el.hasAttribute('data-at')) {
        on = parseList(el.getAttribute('data-at')).indexOf(s) !== -1;
      }
      if (on && el.hasAttribute('data-from')) {
        on = s >= parseInt(el.getAttribute('data-from'), 10);
      }
      if (on && el.hasAttribute('data-until')) {
        on = s <= parseInt(el.getAttribute('data-until'), 10);
      }
      el.classList.toggle('on', on);
    });

    this.caps.forEach(function (el) {
      el.classList.toggle('on', parseInt(el.getAttribute('data-cap'), 10) === s);
    });

    var kids = this.dots.children;
    for (var i = 0; i < kids.length; i++) {
      kids[i].className =
        i + 1 === s ? 'cur' : i + 1 < s ? 'done' : '';
    }

    this.readout.textContent = s === 0 ? '' : s + ' / ' + this.total;
    this.btnPrev.disabled = s <= 1;
  };

  Scene.prototype.go = function (n) {
    this.step = Math.max(1, Math.min(this.total, n));
    this.started = true;
    this.render();
  };

  Scene.prototype.play = function () {
    var self = this;
    this.playing = true;
    this.btnPlay.textContent = '❙❙ 정지';
    if (this.step >= this.total) this.step = 0;
    var tick = function () {
      if (self.step >= self.total) { self.pause(); return; }
      self.go(self.step + 1);
      self.timer = setTimeout(tick, self.speed);
    };
    clearTimeout(this.timer);
    tick();
  };

  Scene.prototype.pause = function () {
    this.playing = false;
    this.btnPlay.textContent = this.step >= this.total ? '↺ 다시' : '▶ 재생';
    clearTimeout(this.timer);
  };

  Scene.prototype.reset = function () {
    this.pause();
    this.step = 0;
    this.started = false;
    this.render();
  };

  /* ---------------- 초기화 ---------------- */

  document.addEventListener('DOMContentLoaded', function () {
    var scenes = Array.prototype.slice
      .call(document.querySelectorAll('[data-scene]'))
      .map(function (el) { return new Scene(el); });

    if (!scenes.length) return;

    if (reduceMotion) {
      // 모션을 줄이는 사용자에게는 최종 상태를 바로 보여준다.
      scenes.forEach(function (s) { s.go(s.total); });
    } else if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (e) {
            var sc = e.target.__scene;
            if (!sc) return;
            if (e.isIntersecting) {
              if (!sc.started) sc.play();
            } else {
              sc.pause();
            }
          });
        },
        { threshold: 0.4 }
      );
      scenes.forEach(function (s) {
        s.root.__scene = s;
        io.observe(s.root);
      });
    } else {
      scenes.forEach(function (s) { s.go(1); });
    }

    // ← → 키로 화면에 보이는 씬을 단계 이동
    document.addEventListener('keydown', function (ev) {
      if (ev.key !== 'ArrowLeft' && ev.key !== 'ArrowRight') return;
      var tag = (ev.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

      var mid = window.innerHeight / 2;
      var best = null;
      var bestD = Infinity;
      scenes.forEach(function (s) {
        var r = s.root.getBoundingClientRect();
        if (r.bottom < 0 || r.top > window.innerHeight) return;
        var d = Math.abs(r.top + r.height / 2 - mid);
        if (d < bestD) { bestD = d; best = s; }
      });
      if (!best) return;
      ev.preventDefault();
      best.pause();
      best.go(best.step + (ev.key === 'ArrowRight' ? 1 : -1));
    });

    // 상단 내비게이션 현재 위치 표시
    var links = document.querySelectorAll('.scene-nav a[href^="#"]');
    if (links.length && 'IntersectionObserver' in window) {
      var navIo = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (e) {
            if (!e.isIntersecting) return;
            links.forEach(function (a) {
              a.classList.toggle(
                'cur',
                a.getAttribute('href') === '#' + e.target.id
              );
            });
          });
        },
        { rootMargin: '-45% 0px -45% 0px' }
      );
      document.querySelectorAll('.scene[id]').forEach(function (el) {
        navIo.observe(el);
      });
    }
  });
})();
