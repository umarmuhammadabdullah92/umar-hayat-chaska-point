'use strict';
(function(){
  var WA='923466816902';
  window.UHCP={WA:WA};
  var isPhone=/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)||(navigator.maxTouchPoints>0&&window.matchMedia('(pointer:coarse)').matches);

  /* ---- Theme (light / dark) ---- */
  var THEME_KEY='uhcp-theme';
  function applyTheme(t){
    document.documentElement.setAttribute('data-theme',t);
    var btn=document.getElementById('themeToggle');
    if(btn)btn.setAttribute('aria-label',t==='light'?'Switch to dark theme':'Switch to light theme');
    metaTheme();
  }
  function metaTheme(){
    var m=document.querySelector('meta[name="theme-color"]');
    if(m)m.setAttribute('content',document.documentElement.getAttribute('data-theme')==='light'?'#FFFBF3':'#0C0B0F');
  }
  function storedTheme(){
    try{return localStorage.getItem(THEME_KEY);}catch(e){return null;}
  }
  function prefersLight(){
    return window.matchMedia&&window.matchMedia('(prefers-color-scheme: light)').matches;
  }
  (function initTheme(){
    var t=storedTheme();
    applyTheme(t||(prefersLight()?'light':'dark'));
    document.addEventListener('click',function(e){
      var btn=e.target&&e.target.closest?e.target.closest('#themeToggle'):null;
      if(!btn)return;
      var cur=document.documentElement.getAttribute('data-theme')==='light'?'dark':'light';
      applyTheme(cur);
      try{localStorage.setItem(THEME_KEY,cur);}catch(e){}
    });
    var mq=window.matchMedia?window.matchMedia('(prefers-color-scheme: light)'):null;
    if(mq&&mq.addEventListener){
      mq.addEventListener('change',function(ev){
        if(!storedTheme())applyTheme(ev.matches?'light':'dark');
      });
    }
  })();

  /* ---- Mobile nav ---- */
  var ham=document.getElementById('hamBtn');
  var mob=document.getElementById('mobNav');
  var drawer=document.getElementById('drawerOverlay');
  function openMob(){mob.classList.add('open');drawer.classList.add('open');ham.classList.add('open');ham.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}
  function closeMob(){mob.classList.remove('open');drawer.classList.remove('open');ham.classList.remove('open');ham.setAttribute('aria-expanded','false');document.body.style.overflow='';}
  window.closeMobNav=closeMob;
  if(ham)ham.addEventListener('click',function(){mob.classList.contains('open')?closeMob():openMob();});
  if(drawer)drawer.addEventListener('click',closeMob);

  /* ---- Header scroll / progress bar ---- */
  var hdr=document.getElementById('siteHdr');
  var bar=document.getElementById('scrollProgress');
  var toTop=document.getElementById('toTop');
  function onScroll(){
    var y=window.scrollY;
    if(hdr)hdr.classList.toggle('scrolled',y>10);
    var max=document.documentElement.scrollHeight-window.innerHeight;
    if(bar)bar.style.width=(max>0?Math.min(100,(y/max)*100):0)+'%';
    if(toTop)toTop.classList.toggle('show',y>600);
  }
  window.addEventListener('scroll',onScroll,{passive:true});
  onScroll();
  if(toTop)toTop.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});

  /* ---- Reveal on scroll ---- */
  var revObs=new IntersectionObserver(function(entries){
    entries.forEach(function(e){if(e.isIntersecting){e.target.classList.add('visible');revObs.unobserve(e.target);}});
  },{threshold:0.07});
  document.querySelectorAll('.reveal').forEach(function(el){revObs.observe(el);});

  /* ---- FAQ accordion ---- */
  window.toggleFaq=function(item){
    var wasOpen=item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(function(el){if(el!==item)el.classList.remove('open');});
    item.classList.toggle('open',!wasOpen);
    var btn=item.querySelector('.faq-q');
    if(btn)btn.setAttribute('aria-expanded',!wasOpen);
  };

  /* ---- Highlight current page in nav ---- */
  function pageId(p){return p.replace(/\.html$/,'').replace(/\/$/,'')||'index';}
  var page=pageId(location.pathname);
  document.querySelectorAll('nav a[href]').forEach(function(a){
    var h=a.getAttribute('href');
    if(!h||h.charAt(0)==='#')return;
    var p=pageId(h);
    if(p===page)a.classList.add('active');
  });

  /* ---- Smooth scroll for hash links on same page ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click',function(e){
      var id=a.getAttribute('href');
      if(!id||id.length<2)return;
      var t=document.querySelector(id);
      if(!t)return;
      e.preventDefault();
      var h=document.getElementById('siteHdr');
      var top=t.getBoundingClientRect().top+window.pageYOffset-(h?h.offsetHeight+16:80);
      window.scrollTo({top:top,behavior:'smooth'});
      closeMob();
    });
  });

  /* ---- WhatsApp links ---- */
  var defaultMsg=encodeURIComponent("Hi! I'd like to place an order at Umar Hayat Chaska Point \uD83C\uDF7D\uFE0F\n\nCan you tell me what is available today?");
  var defaultHref='https://api.whatsapp.com/send?phone='+WA+'&text='+defaultMsg;
  var heroWa=document.getElementById('heroWaBtn');
  if(heroWa)heroWa.href=defaultHref;
  var waFloat=document.getElementById('waFloat');
  if(waFloat)waFloat.href=defaultHref;

  /* warm WhatsApp links */
  document.querySelectorAll('a[href*="api.whatsapp.com"],a[href*="wa.me"]').forEach(function(a){
    a.addEventListener('pointerenter',function(){
      if(a.dataset.warmed)return;
      a.dataset.warmed='1';
      try{fetch('https://api.whatsapp.com/send?phone='+WA,{mode:'no-cors',priority:'low'});}catch(e){}
    },{passive:true});
  });

  /* mobile WhatsApp deep-link */
  document.addEventListener('click',function(e){
    var a=e.target.closest?e.target.closest('a[href*="api.whatsapp.com"],a[href*="wa.me"]'):null;
    if(!a||!isPhone)return;
    e.preventDefault();
    var parts={},kv,qs=a.href.split('?')[1]||'';
    qs.split('&').forEach(function(pair){kv=pair.split('=');if(kv[0])parts[kv[0]]=kv.slice(1).join('=');});
    if(!parts.phone){var wm=a.href.match(/wa\.me\/(\d+)/);if(wm)parts.phone=wm[1];}
    var out=[];
    if(parts.phone)out.push('phone='+parts.phone);
    if(parts.text)out.push('text='+parts.text);
    var left=Date.now();
    location.href='whatsapp://send?'+out.join('&');
    setTimeout(function(){if(!document.hidden&&Date.now()-left<2500)location.href=a.href;},900);
  },true);

  /* ---- Home page: highlight today in hours box ---- */
  var days=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  var today=days[new Date().getDay()];
  document.querySelectorAll('.hours-row').forEach(function(r){
    if(r.dataset.day===today)r.classList.add('today');
  });

})();