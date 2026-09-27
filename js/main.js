'use strict';
(function(){
  /* Business details come from js/site-config.js — edit it there. */
  var CFG=window.SITE||{};
  var WA=(CFG.phone||'').replace(/\D/g,'');
  window.App={WA:WA};
  var isPhone=/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)||(navigator.maxTouchPoints>0&&window.matchMedia('(pointer:coarse)').matches);


  /* ---- Mobile nav ---- */
  var hdr=document.getElementById('siteHdr');
  var ham=document.getElementById('hamBtn');
  var mob=document.getElementById('mobNav');
  /* the template uses the shared .hdr-scrim; #drawerOverlay is kept as a
     fallback so older markup still works */
  var mobScrim=document.getElementById('mobScrim')||document.getElementById('drawerOverlay');
  function toggleClass(el,cls,on){if(el)el.classList.toggle(cls,on);}
  function openMob(){
    toggleClass(mob,'open',true);
    toggleClass(mobScrim,'open',true);
    toggleClass(ham,'open',true);
    if(ham)ham.setAttribute('aria-expanded','true');
    document.body.style.overflow='hidden';
  }
  function closeMob(){
    toggleClass(mob,'open',false);
    toggleClass(mobScrim,'open',false);
    toggleClass(ham,'open',false);
    if(ham)ham.setAttribute('aria-expanded','false');
    document.body.style.overflow='';
  }
  function mobIsOpen(){return !!(mob&&mob.classList.contains('open'));}
  /* Anchor the drawer just below the sticky header so the hamburger stays
     visible and clickable while the drawer is open. The header can be more
     than one row tall, so measure it rather than assuming a fixed height. */
  function syncDrawerTop(){
    var h=hdr?Math.round(hdr.getBoundingClientRect().bottom):0;
    document.documentElement.style.setProperty('--drawer-top',h+'px');
  }
  syncDrawerTop();
  window.addEventListener('resize',syncDrawerTop);
  window.addEventListener('orientationchange',syncDrawerTop);
  window.closeMobNav=closeMob;
  window.openMobNav=openMob;
  if(ham)ham.addEventListener('click',function(){mobIsOpen()?closeMob():openMob();});
  if(mobScrim)mobScrim.addEventListener('click',closeMob);
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&mobIsOpen())closeMob();
  });

  /* ---- Header scroll / progress bar ---- */
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
  var orderPrompt=CFG.orderPrompt||("Hi! I'd like to place an order at "+(CFG.name||'your business')+".");
  var defaultHref=WA?'https://api.whatsapp.com/send?phone='+WA+'&text='+encodeURIComponent(orderPrompt):'';
  var heroWa=document.getElementById('heroWaBtn');
  if(heroWa&&defaultHref)heroWa.href=defaultHref;
  var waFloat=document.getElementById('waFloat');
  if(waFloat&&defaultHref)waFloat.href=defaultHref;
  /* hide order affordances until a number is configured */
  if(!WA||CFG.whatsappOrdering===false){
    document.querySelectorAll('[data-order-cta],#heroWaBtn,#waFloat').forEach(function(el){
      el.hidden=true;el.setAttribute('aria-hidden','true');
    });
  }

  /* warm WhatsApp links */
  if(WA){
    document.querySelectorAll('a[href*="api.whatsapp.com"],a[href*="wa.me"]').forEach(function(a){
      a.addEventListener('pointerenter',function(){
        if(a.dataset.warmed)return;
        a.dataset.warmed='1';
        try{fetch('https://api.whatsapp.com/send?phone='+WA,{mode:'no-cors',priority:'low'});}catch(e){}
      },{passive:true});
    });
  }

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

  /* ---- Footer year ---- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-year]'),function(el){
    el.textContent=String(new Date().getFullYear());
  });

})();