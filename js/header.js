'use strict';
(function(){
  var U=window.App=window.App||{};

  /* ============================================================
     Currency — display-only conversion. The order total is always
     calculated in PKR, so the figure you receive is never affected
     by the display toggle.
     ============================================================ */
  var CFG=window.SITE||{};

  /* Show/hide a scrim by id, tolerating a missing element */
  function toggleScrim(id,on){
    var el=document.getElementById(id);
    if(el)el.classList.toggle('open',!!on);
  }

  var CUR_KEY='site-cur';
  var RATE_PKR_PER_USD=Number(CFG.ratePKRPerUSD)||278;
  var CURRENCIES={
    PKR:{code:'PKR',label:'PKR',name:'Pakistani Rupee',sym:'Rs.',rate:1},
    USD:{code:'USD',label:'USD',name:'US Dollar',sym:'$',rate:1/RATE_PKR_PER_USD}
  };
  var cur=CURRENCIES[CFG.currency]?CFG.currency:'PKR';

  function storedCur(){
    try{return localStorage.getItem(CUR_KEY);}catch(e){return null;}
  }
  function readCur(){
    var c=storedCur();
    return c&&CURRENCIES[c]?c:cur;
  }
  function group(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,',');}

  U.fmt=function(pkr){
    var v=Number(pkr)||0;
    if(cur==='PKR')return 'Rs. '+group(Math.round(v));
    return '$'+(v*CURRENCIES.USD.rate).toFixed(2);
  };

  function setCur(next,silent){
    if(!CURRENCIES[next])return;
    cur=next;
    try{localStorage.setItem(CUR_KEY,cur);}catch(e){}
    var lbl=document.getElementById('curLbl');
    if(lbl)lbl.textContent=cur;
    var btn=document.getElementById('curBtn');
    if(btn)btn.setAttribute('aria-label','Currency: '+CURRENCIES[cur].name+'. Change currency');
    document.querySelectorAll('#curMenu [role="menuitemradio"],.mn-cur [role="radio"]').forEach(function(b){
      b.setAttribute('aria-checked',b.dataset.cur===cur?'true':'false');
    });
    if(!silent){
      applyPrices();
      document.dispatchEvent(new CustomEvent('site:currency',{detail:{currency:cur}}));
    }
  }
  U.setCur=function(c){setCur(c);};

  /* Re-render every live price in the DOM. Prices are read from
     data-price / data-pkr so the rendered text is never the
     source of truth — that keeps currency switches lossless. */
  function applyPrices(){
    document.querySelectorAll('.mcard').forEach(function(card){
      var pr=card.querySelector('.pr');
      if(pr)pr.textContent=U.fmt(card.dataset.price);
      card.querySelectorAll('.size-btn').forEach(function(b){
        if(b.dataset.price)b.textContent=b.dataset.label+' · '+U.fmt(b.dataset.price);
      });
    });
    document.querySelectorAll('.bs-price[data-pkr]').forEach(function(el){
      el.textContent=U.fmt(el.dataset.pkr);
    });
    if(U.renderTotals)U.renderTotals();
  }
  U.applyPrices=applyPrices;

  cur=readCur();

  /* ============================================================
     Currency dropdown
     ============================================================ */
  var curBtn=document.getElementById('curBtn');
  var curMenu=document.getElementById('curMenu');
  function closeCur(){if(curMenu)curMenu.classList.remove('open');if(curBtn)curBtn.setAttribute('aria-expanded','false');}
  function openCur(){if(curMenu){curMenu.classList.add('open');curBtn.setAttribute('aria-expanded','true');}}
  if(curBtn&&curMenu){
    curBtn.addEventListener('click',function(e){
      e.stopPropagation();
      curMenu.classList.contains('open')?closeCur():openCur();
    });
    curMenu.querySelectorAll('[role="menuitemradio"]').forEach(function(b){
      b.addEventListener('click',function(){setCur(b.dataset.cur);closeCur();});
    });
  }

  /* ============================================================
     Search — client-side index built from the real /menu markup
     ============================================================ */
  var IDX_KEY='site-menu-idx';
  var idx=null, idxPromise=null;

  function esc(s){
    return String(s).replace(/[&<>"']/g,function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function buildIndexFrom(doc){
    return Array.prototype.map.call(doc.querySelectorAll('.mcard'),function(c){
      return {
        n:c.dataset.name||'',
        b:c.dataset.base||c.dataset.name||'',
        c:c.dataset.cat||'',
        p:parseFloat(c.dataset.price)||0,
        u:c.dataset.unit||'',
        i:c.dataset.img||'',
        d:(c.querySelector('.mcard-desc')||{}).textContent||''
      };
    });
  }

  function readCachedIdx(){
    try{var r=sessionStorage.getItem(IDX_KEY);return r?JSON.parse(r):null;}catch(e){return null;}
  }
  function writeCachedIdx(v){
    try{sessionStorage.setItem(IDX_KEY,JSON.stringify(v));}catch(e){}
  }

  function loadIndex(){
    if(idx)return Promise.resolve(idx);
    if(idxPromise)return idxPromise;
    var local=buildIndexFrom(document);
    if(local.length){
      idx=local;writeCachedIdx(local);
      return Promise.resolve(idx);
    }
    var cached=readCachedIdx();
    if(cached){idx=cached;return Promise.resolve(idx);}
    var urls=CFG.searchIndexUrl?[CFG.searchIndexUrl,CFG.searchIndexUrl.replace(/\/$/,'.html')]:['/menu','/menu.html'];
    idxPromise=urls.reduce(function(chain,url){
      return chain.catch(function(){
        return fetch(url,{credentials:'same-origin'}).then(function(r){
          if(!r.ok)throw new Error(r.status);
          return r.text();
        }).then(function(t){
          var d=new DOMParser().parseFromString(t,'text/html');
          var list=buildIndexFrom(d);
          if(!list.length)throw new Error('empty');
          idx=list;writeCachedIdx(list);idxPromise=null;
          return list;
        });
      });
    },Promise.reject()).catch(function(){
      idxPromise=null;
      return [];
    });
    return idxPromise;
  }

  function score(item,tok){
    var nb=item.b.toLowerCase(),nn=item.n.toLowerCase(),nc=item.c.toLowerCase(),nd=item.d.toLowerCase();
    var s=0;
    tok.forEach(function(t){
      var inName=nn.indexOf(t)>=0,inBase=nb.indexOf(t)>=0,inCat=nc.indexOf(t)>=0,inDesc=nd.indexOf(t)>=0;
      if(!inName&&!inBase&&!inCat&&!inDesc)return;
      s+=inName||inBase?10:0;
      s+=nc===t?9:inCat?5:0;
      s+=inDesc?1.5:0;
      if(nb.indexOf(t)===0)s+=8;
      if(nb.split(/\s+/).some(function(w){return w.indexOf(t)===0;}))s+=4;
    });
    return s;
  }

  function hl(text,tok){
    var out=esc(text);
    tok.forEach(function(t){
      if(t.length<2)return;
      var re=new RegExp('('+t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig');
      out=out.replace(re,'<mark>$1</mark>');
    });
    return out;
  }

  var spOpen=false;
  function closeSearch(){
    var p=document.getElementById('searchPanel');
    if(!p)return;
    p.classList.remove('open');
    toggleScrim('searchScrim',false);
    var b=document.getElementById('searchBtn');
    if(b)b.setAttribute('aria-expanded','false');
    document.body.style.overflow='';
    spOpen=false;
  }
  function openSearch(){
    var p=document.getElementById('searchPanel');
    if(!p)return;
    p.classList.add('open');
    toggleScrim('searchScrim',true);
    var b=document.getElementById('searchBtn');
    if(b)b.setAttribute('aria-expanded','true');
    document.body.style.overflow='hidden';
    spOpen=true;
    var i=document.getElementById('searchInput');
    if(i){i.value='';render('');i.focus();}
  }
  U.openSearch=openSearch;
  window.openSearch=openSearch;

  /* Fill the header branding from js/site-config.js.
     Any element carrying a data-site-* attribute is updated, so you can
     put the brand name anywhere on the page without touching this file. */
  function applyBranding(){
    var C=CFG;
    function setAll(sel,val,attr){
      if(val==null||val==='')return;
      Array.prototype.forEach.call(document.querySelectorAll(sel),function(el){
        if(attr)el.setAttribute(attr,val);else el.textContent=val;
        el.hidden=false;
      });
    }
    setAll('[data-site-name]',C.name);
    setAll('[data-site-tagline]',C.tagline);
    setAll('[data-site-address]',C.address);
    if(C.phone){
      var digits=C.phone.replace(/\D/g,'');
      setAll('[data-site-phone]','+'+digits);
      Array.prototype.forEach.call(document.querySelectorAll('[data-site-phone]'),function(el){
        el.href='tel:+'+digits;el.hidden=false;
      });
    }
    if(C.logo){
      var img=document.querySelector('[data-site-logo]');
      if(img){img.src=C.logo;img.hidden=false;}
    }
  }
  U.applyBranding=applyBranding;
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',applyBranding);
  }else{applyBranding();}

  function render(q){
    var body=document.getElementById('searchBody');
    if(!body)return;
    var tok=q.toLowerCase().split(/\s+/).filter(Boolean);
    if(!tok.length){
      var chips=((window.SITE||{}).searchChips)||[];
      body.innerHTML=chips.length
        ? '<div class="sp-hint">Search<br><strong>Try one of these.</strong></div>'+
          '<div class="sp-chips">'+chips.map(function(c){
            return '<button type="button" class="sp-chip">'+c+'</button>';
          }).join('')+'</div>'
        : '<div class="sp-hint">Search<br><strong>Type to find something.</strong></div>';
      return;
    }
    body.innerHTML='<div class="sp-hint">Searching…</div>';
    loadIndex().then(function(list){
      if(!list.length){
        body.innerHTML='<div class="sp-empty"><div class="sp-empty-ico"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/></svg></div>Menu search needs the menu page.<br>Open the menu to browse everything.</div>';
        return;
      }
      var hits=list.map(function(it){return {it:it,s:score(it,tok)};})
        .filter(function(x){return x.s>0;})
        .sort(function(a,b){return b.s-a.s;})
        .slice(0,8);
      if(!hits.length){
        body.innerHTML='<div class="sp-empty">No match for “'+esc(q)+'”.</div>';
        return;
      }
      body.innerHTML='<div class="sp-res">'+hits.map(function(h){
        var it=h.it;
        var meta=it.c+(it.u?' · per '+it.u:'');
        return '<a class="sp-item" href="/menu?q='+encodeURIComponent(it.b||it.n)+'">'+
          '<div class="sp-item-img">'+(it.i?'<img src="'+esc(it.i)+'" alt="" loading="lazy" decoding="async">':'')+'</div>'+
          '<div class="sp-item-txt"><div class="sp-item-nm">'+hl(it.n,tok)+'</div>'+
          '<div class="sp-item-meta">'+esc(meta)+'</div></div>'+
          '<div class="sp-item-pr" data-pkr="'+it.p+'">'+esc(U.fmt(it.p))+'</div></a>';
      }).join('')+'</div>';
    });
  }

  var sBtn=document.getElementById('searchBtn');
  if(sBtn){
    sBtn.addEventListener('click',function(e){e.stopPropagation();spOpen?closeSearch():openSearch();});
    var scrim=document.getElementById('searchScrim');
    if(scrim)scrim.addEventListener('click',closeSearch);
    var closeBtn=document.getElementById('searchClose');
    if(closeBtn)closeBtn.addEventListener('click',closeSearch);
    var input=document.getElementById('searchInput');
    var t=null;
    if(input)input.addEventListener('input',function(){
      var v=input.value;
      clearTimeout(t);
      t=setTimeout(function(){render(v);},130);
    });
    var chips=document.querySelector('.sp-chips');
    if(chips)chips.addEventListener('click',function(e){
      var b=e.target.closest('.sp-chip');
      if(!b)return;
      input.value=b.textContent;
      render(b.textContent);
      input.focus();
    });
  }
  document.addEventListener('keydown',function(e){
    if((e.key==='/'||(e.key==='k'&&(e.metaKey||e.ctrlKey)))&&!spOpen){
      var tag=(document.activeElement&&document.activeElement.tagName)||'';
      if(tag==='INPUT'||tag==='TEXTAREA')return;
      e.preventDefault();
      openSearch();
      return;
    }
    if(e.key==='Escape'){
      if(spOpen){closeSearch();return;}
      closeCur();
      closeAcct();
    }
  });
  document.addEventListener('click',function(e){
    if(curMenu&&curMenu.classList.contains('open')&&!e.target.closest('.uwrap'))closeCur();
  });

  /* ============================================================
     Account — saved details + device-local order history
     ============================================================ */
  var ACCT_KEY='site-acct', ORD_KEY='site-orders';
  function readJson(k,fb){try{var r=localStorage.getItem(k);return r?JSON.parse(r):fb;}catch(e){return fb;}}
  function writeJson(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}}

  function acct(){return readJson(ACCT_KEY,{name:'',phone:''});}
  function orders(){return readJson(ORD_KEY,[]);}
  U.orders=orders;
  U.acct=acct;

  function renderAcctOrders(){
    var box=document.getElementById('acctOrders');
    if(!box)return;
    var list=orders();
    if(!list.length){
      box.innerHTML='<div class="acct-note" style="margin-top:0">No saved orders on this device yet. Orders you send via WhatsApp are logged here so you can re-order.</div>';
      return;
    }
    box.innerHTML=list.map(function(o){
      return '<div class="acct-order"><div><div class="ao-ref">'+esc(o.ref)+'</div>'+
        '<div class="ao-items">'+o.count+' item'+(o.count===1?'':'s')+' · '+esc(o.currency)+' '+o.total.toFixed(0)+'</div></div>'+
        '<span class="ao-when">'+esc(o.when)+'</span></div>';
    }).join('')+'<button type="button" class="acct-clear" id="acctClear">Clear order history</button>';
    var cl=document.getElementById('acctClear');
    if(cl)cl.addEventListener('click',function(){
      try{localStorage.removeItem(ORD_KEY);}catch(e){}
      renderAcctOrders();
    });
  }

  function closeAcct(){
    var p=document.getElementById('acctPanel');
    if(!p)return;
    p.classList.remove('open');
    toggleScrim('acctScrim',false);
    var b=document.getElementById('acctBtn');
    if(b)b.setAttribute('aria-expanded','false');
    document.body.style.overflow='';
  }
  function openAcct(){
    var p=document.getElementById('acctPanel');
    if(!p)return;
    var a=acct();
    var n=document.getElementById('acctName'),ph=document.getElementById('acctPhone');
    if(n)n.value=a.name||'';
    if(ph)ph.value=a.phone||'';
    renderAcctOrders();
    p.classList.add('open');
    toggleScrim('acctScrim',true);
    var b=document.getElementById('acctBtn');
    if(b)b.setAttribute('aria-expanded','true');
    document.body.style.overflow='hidden';
    if(n)setTimeout(function(){n.focus();},260);
  }
  U.openAcct=openAcct;
  U.closeAcct=closeAcct;

  var aBtn=document.getElementById('acctBtn');
  if(aBtn){
    aBtn.addEventListener('click',function(e){
      e.stopPropagation();
      var p=document.getElementById('acctPanel');
      p.classList.contains('open')?closeAcct():openAcct();
    });
    var as=document.getElementById('acctScrim');
    if(as)as.addEventListener('click',closeAcct);
    var ac=document.getElementById('acctClose');
    if(ac)ac.addEventListener('click',closeAcct);
    var save=document.getElementById('acctSave');
    if(save)save.addEventListener('click',function(){
      var n=document.getElementById('acctName').value.trim();
      var ph=document.getElementById('acctPhone').value.trim();
      if(ph&&!/^[+\d][\d\s-]{6,19}$/.test(ph)){
        save.textContent='Check the phone number';
        save.classList.remove('saved');
        return;
      }
      writeJson(ACCT_KEY,{name:n,phone:ph});
      var cn=document.getElementById('custName');
      if(cn){cn.value=n;cn.dispatchEvent(new Event('input'));}
      var cp=document.getElementById('custPhone');
      if(cp){cp.value=ph;cp.dispatchEvent(new Event('input'));}
      save.textContent='Saved ✓';
      save.classList.add('saved');
      setTimeout(function(){save.textContent='Save details';save.classList.remove('saved');},1600);
    });
  }

  /* Log an order when the customer actually sends it to WhatsApp. */
  document.addEventListener('click',function(e){
    if(!e.target.closest||!e.target.closest('#waFinalBtn'))return;
    var c=acct();
    if(c.name||c.phone){
      var cn=document.getElementById('custName');
      if(cn&&!cn.value.trim())cn.value=c.name||'';
    }
    try{
      var cnt=parseInt(document.getElementById('cartCount').textContent,10)||0;
      if(!cnt)return;
      var tot=parseFloat(document.getElementById('totalEl').dataset.pkr||'0')||0;
      var list=orders();
      list.unshift({
        ref:'UHC-'+Date.now().toString(36).toUpperCase().slice(-6),
        count:cnt,total:tot,currency:cur,
        when:new Date().toLocaleDateString(undefined,{day:'numeric',month:'short'})
      });
      writeJson(ORD_KEY,list.slice(0,12));
    }catch(err){}
  });

  /* Prefill saved name into the cart panel. */
  (function(){
    var cn=document.getElementById('custName');
    if(!cn)return;
    var c=acct();
    if(c.name&&!cn.value)cn.value=c.name;
  })();

  /* Mobile drawer mirrors the desktop currency + account controls. */
  (function mobileDrawer(){
    var grp=document.querySelector('.mn-cur');
    if(grp)grp.addEventListener('click',function(e){
      var b=e.target.closest('button[data-cur]');
      if(!b)return;
      setCur(b.dataset.cur);
      if(window.closeMobNav)window.closeMobNav();
    });
    var ma=document.getElementById('mobAcctBtn');
    if(ma)ma.addEventListener('click',function(){
      if(window.closeMobNav)window.closeMobNav();
      openAcct();
    });
  })();

  /* ============================================================
     /menu?q=… deep link from a search result
     ============================================================ */
  (function applyQuery(){
    if(!document.querySelector('.mcard'))return;
    var q=new URLSearchParams(location.search).get('q');
    if(!q)return;
    var tok=q.toLowerCase().split(/\s+/).filter(Boolean);
    var shown=0;
    document.querySelectorAll('.mcard').forEach(function(card){
      var hay=[card.dataset.name,card.dataset.base,card.dataset.cat,
        (card.querySelector('.mcard-desc')||{}).textContent].join(' ').toLowerCase();
      var hit=tok.every(function(t){return hay.indexOf(t)>=0;});
      card.classList.toggle('hidden',!hit);
      if(hit)shown++;
    });
    document.querySelectorAll('.ftab').forEach(function(t){t.classList.remove('active');});
    var f=document.getElementById('filters');
    if(f)f.dataset.q=q;
  })();

  /* ============================================================
     Boot
     ============================================================ */
  setCur(cur,true);
  applyPrices();
  if(curBtn&&curMenu)closeCur();

})();
