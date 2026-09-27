'use strict';
(function(){
  var U=window.App=window.App||{};
  var CFG=window.SITE||{};
  var WA=U.WA||(CFG.phone||'').replace(/\D/g,'');
  var CART_KEY='site-cart';
  var fmt=function(v){return U.fmt?U.fmt(v):'Rs. '+v;};

  /* ---- Build the order UI on any page that lacks it ---- */
  function buildUI(){
    if(!document.getElementById('cartPanel')){
      var d=document.createElement('div');
      d.innerHTML=
        '<button class="cart-fab hidden" id="cartFab" type="button">Your Order <span class="cnt" id="cartCount">0</span></button>'+
        '<div class="mob-cart-bar" id="mobCartBar">'+
          '<div class="mcb-left"><span class="mcb-items" id="mobCartItems">0 items</span><span class="mcb-total" id="mobCartTotal">Rs. 0</span></div>'+
          '<button class="mcb-btn" type="button">View Order →</button>'+
        '</div>'+
        '<div class="overlay" id="overlay"></div>'+
        '<div class="cart-panel" id="cartPanel" role="dialog" aria-label="Your order" aria-modal="true">'+
          '<div class="cart-hdr">'+
            '<div><h3>Your Order</h3><div class="item-cnt" id="cartSubhead">0 items</div></div>'+
            '<button class="close-btn" type="button" aria-label="Close order panel">✕</button>'+
          '</div>'+
          '<div class="cart-items" id="cartItemsEl"></div>'+
          '<div class="cart-summary" id="cartSummaryEl" style="display:none;">'+
            '<div class="summary-row"><span>Subtotal</span><span id="subtotalEl">Rs. 0</span></div>'+
            '<div class="summary-row total"><span>Total</span><span class="tprice" id="totalEl" data-pkr="0">Rs. 0</span></div>'+
          '</div>'+
          '<div class="cart-footer" id="cartFooterEl" style="display:none;">'+
            '<div class="order-fields">'+
              '<div class="ofield"><label for="custName">Your Name</label><input type="text" id="custName" placeholder="e.g. Ali Ahmed" autocomplete="name"></div>'+
              '<div class="ofield"><label for="custPhone">Phone (optional)</label><input type="tel" id="custPhone" placeholder="e.g. 0300 1234567" autocomplete="tel"></div>'+
            '</div>'+
            '<a href="#" id="waFinalBtn" class="wa-btn" target="_blank" rel="noopener">'+
              '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="white"><path d="M12 0C5.373 0 0 5.373 0 12c0 2.115.553 4.1 1.52 5.824L0 24l6.336-1.496A11.955 11.955 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>'+
              'Send Order on WhatsApp'+
            '</a>'+
            '<p class="cart-note" id="cartNote">We will confirm your order in a few minutes.</p>'+
          '</div>'+
        '</div>';
      while(d.firstChild)document.body.appendChild(d.firstChild);
    }
    document.getElementById('cartFab').addEventListener('click',function(){window.openCart();});
    document.querySelector('#mobCartBar .mcb-btn').addEventListener('click',function(){window.openCart();});
    document.querySelector('#cartPanel .close-btn').addEventListener('click',function(){window.closeCart();});
    document.getElementById('overlay').addEventListener('click',function(){window.closeCart();});
    /* Delegated item controls — no inline handlers with item names. */
    document.getElementById('cartItemsEl').addEventListener('click',function(e){
      var b=e.target.closest('button[data-act]');
      if(!b)return;
      if(b.dataset.act==='qty')window.cartQty(b.dataset.name,parseInt(b.dataset.delta,10));
      else window.removeItem(b.dataset.name);
    });
  }

  /* ---- Menu filter tabs ---- */
  var filters=document.getElementById('filters');
  function applyTab(f){
    var q=filters&&filters.dataset.q;
    if(q){
      delete filters.dataset.q;
      var tok=q.toLowerCase().split(/\s+/).filter(Boolean);
      document.querySelectorAll('.mcard').forEach(function(c){
        var hay=[c.dataset.name,c.dataset.base,c.dataset.cat,(c.querySelector('.mcard-desc')||{}).textContent].join(' ').toLowerCase();
        c.classList.toggle('hidden',!tok.every(function(t){return hay.indexOf(t)>=0;}));
      });
    }
    document.querySelectorAll('.mcard').forEach(function(c){
      c.classList.toggle('hidden',f!=='all'&&c.dataset.cat!==f);
    });
  }
  document.querySelectorAll('.ftab').forEach(function(t){
    t.addEventListener('click',function(){
      document.querySelectorAll('.ftab').forEach(function(x){x.classList.remove('active');});
      t.classList.add('active');
      applyTab(t.dataset.f);
    });
  });

  /* ---- Quantity / size controls ---- */
  window.changeQty=function(btn,delta){
    var card=btn.closest('.mcard');
    var step=parseFloat(card.dataset.step||'1');
    var el=card.querySelector('.qval');
    var v=parseFloat(el.textContent);
    v=Math.max(step,Math.round((v+delta*step)*100)/100);
    el.textContent=v;
  };

  window.selectSize=function(btn,price,label){
    var card=btn.closest('.mcard');
    card.querySelectorAll('.size-btn').forEach(function(b){b.classList.remove('active');});
    btn.classList.add('active');
    card.dataset.price=price;
    card.dataset.name=card.dataset.base+' ('+label+')';
    card.querySelector('.pr').textContent=fmt(price);
  };

  /* ---- Cart state (persisted across pages) ---- */
  var cart=readCart();
  function readCart(){
    try{
      var r=localStorage.getItem(CART_KEY);
      var o=r?JSON.parse(r):{};
      return o&&typeof o==='object'?o:{};
    }catch(e){return {};}
  }
  function saveCart(){
    try{localStorage.setItem(CART_KEY,JSON.stringify(cart));}catch(e){}
  }

  /* Add an item to the order.
     Two ways to call it:

       App.addToCart({name:'Coffee', price:350, qty:1, unit:'cup', img:'…'})

     or, from a button inside an element carrying data-name/data-price:

       <div data-name="Coffee" data-price="350" data-unit="cup">
         <button onclick="App.addToCart(this)">Add</button>
       </div>

     Returns false if the item is unusable, so callers can bail early. */
  window.addToCart=function(input){
    var name,price,unit,img,qty,btn=null,card=null;

    if(input&&typeof input.closest==='function'){
      btn=input;
      card=input.closest('[data-name][data-price]');
      if(!card)return false;
      name=card.dataset.name;
      price=parseFloat(card.dataset.price);
      unit=card.dataset.unit||'';
      img=card.dataset.img||'';
      var qEl=card.querySelector('[data-qty]')||card.querySelector('.qval');
      qty=qEl?parseFloat(qEl.textContent)||1:1;
    }else if(input&&typeof input==='object'){
      name=String(input.name||'').trim();
      price=Number(input.price)||0;
      unit=input.unit||'';
      img=input.img||'';
      qty=Number(input.qty)||1;
    }else{
      return false;
    }

    if(!name||!(price>0))return false;
    if(cart[name])cart[name].qty=Math.round((cart[name].qty+qty)*100)/100;
    else cart[name]={price:price,qty:qty,unit:unit,img:img};
    saveCart();
    renderCart();
    if(btn){
      btn.textContent='Added \u2713';btn.classList.add('added');
      setTimeout(function(){btn.textContent='Add to Order';btn.classList.remove('added');},1300);
    }
    showToast('\u2713 '+name+' added to order','success');
    bounceBadge();
    return true;
  };

  window.cartQty=function(name,delta){
    if(!cart[name])return;
    var step=cart[name].unit==='kg'?0.5:1;
    cart[name].qty=Math.max(step,Math.round((cart[name].qty+delta*step)*100)/100);
    saveCart();
    renderCart();
  };

  window.removeItem=function(name){delete cart[name];saveCart();renderCart();};

  function getTotal(){return Object.values(cart).reduce(function(s,it){return s+it.price*it.qty;},0);}
  /* total number of units ordered, not the number of distinct line items */
  function count(){
    var n=0;
    for(var k in cart){if(Object.prototype.hasOwnProperty.call(cart,k))n+=Number(cart[k].qty)||0;}
    return n;
  }

  /* The order total you actually bill stays in your own currency
     (PKR here), so the message sent to you is never affected by the
     display-only currency toggle. */
  function buildWaMsg(items,total,name,phone){
    var lines=['\uD83C\uDF7D\uFE0F *Order \u2014 '+(CFG.name||'New order')+'*',''];
    items.forEach(function(it){
      var ql=it.unit?it.qty+' '+it.unit:'\u00D7'+it.qty;
      lines.push('\u2022 '+it.name+' ('+ql+') \u2014 Rs. '+Math.round(it.price*it.qty));
    });
    lines.push('','*Total: Rs. '+Math.round(total)+'*');
    if(name)lines.push('Name: '+name);
    if(phone)lines.push('Phone: '+phone);
    return lines.join('\n');
  }

  function esc(s){
    return String(s).replace(/[&<>"']/g,function(c){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }

  function renderCart(){
    var names=Object.keys(cart);
    var total=getTotal();
    var el=document.getElementById('cartItemsEl');
    var summaryEl=document.getElementById('cartSummaryEl');
    var footerEl=document.getElementById('cartFooterEl');
    if(!names.length){
      el.innerHTML='<div class="empty-state"><div class="empty-ico"><svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 002-2V2"/><path d="M7 2v20"/><path d="M21 15V2a5 5 0 00-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg></div><p>Your order is empty.<br>Add some snacks from the menu!</p></div>';
      summaryEl.style.display='none';footerEl.style.display='none';
    }else{
      el.innerHTML=names.map(function(n){
        var it=cart[n];
        var line=Math.round(it.price*it.qty*100)/100;
        var ql=it.unit?it.qty+' '+it.unit:'\u00D7'+it.qty;
        return '<div class="citem"><div class="citem-img">'+(it.img?'<img src="'+esc(it.img)+'" alt="'+esc(n)+'" loading="lazy" decoding="async">':'')+'</div>'+
          '<div class="citem-info"><div class="citem-name">'+esc(n)+'</div>'+
          '<div class="citem-price">'+esc(fmt(line))+' ('+esc(ql)+')</div></div>'+
          '<div class="citem-right"><div class="citem-qty">'+
          '<button class="cq-btn" type="button" data-act="qty" data-name="'+esc(n)+'" data-delta="-1" aria-label="Decrease quantity">\u2212</button>'+
          '<span class="cq-val">'+it.qty+'</span>'+
          '<button class="cq-btn" type="button" data-act="qty" data-name="'+esc(n)+'" data-delta="1" aria-label="Increase quantity">+</button></div>'+
          '<button class="citem-del" type="button" data-act="del" data-name="'+esc(n)+'">Remove</button></div></div>';
      }).join('');
      summaryEl.style.display='block';footerEl.style.display='block';
      document.getElementById('subtotalEl').textContent=fmt(total);
      var te=document.getElementById('totalEl');
      te.textContent=fmt(total);
      te.dataset.pkr=total;
    }
    var c=count();
    document.getElementById('cartSubhead').textContent=c===1?'1 item':c+' items';
    document.getElementById('cartCount').textContent=c;
    document.getElementById('cartFab').classList.toggle('hidden',c===0);
    document.getElementById('mobCartItems').textContent=c===1?'1 item':c+' items';
    document.getElementById('mobCartTotal').textContent=fmt(total);
    document.getElementById('mobCartBar').classList.toggle('visible',c>0);
    document.body.classList.toggle('has-cart',c>0);
    var waF=document.getElementById('waFloat');
    if(waF)waF.style.bottom=c>0?'calc(76px + env(safe-area-inset-bottom))':'24px';
    var waBtn=document.getElementById('waFinalBtn');
    if(waBtn){
      var name=(document.getElementById('custName')||{}).value||'';
      var phone=(document.getElementById('custPhone')||{}).value||'';
      var items=names.map(function(n){return{name:n,qty:cart[n].qty,unit:cart[n].unit,price:cart[n].price};});
      waBtn.href='https://api.whatsapp.com/send?phone='+WA+'&text='+encodeURIComponent(buildWaMsg(items,total,name.trim(),phone.trim()));
    }
    syncBadge(c);
  }

  /* Header cart icon badge */
  function syncBadge(c){
    var b=document.getElementById('cartBadge');
    if(!b)return;
    b.textContent=c>99?'99+':c;
    b.hidden=c===0;
  }
  window.cartCount=count;

  window.openCart=function(){
    document.getElementById('cartPanel').classList.add('open');
    document.getElementById('overlay').classList.add('open');
    document.body.style.overflow='hidden';
    if(window.visualViewport){window.visualViewport.addEventListener('resize',_vvResize);window.visualViewport.addEventListener('scroll',_vvResize);}
  };

  window.closeCart=function(){
    document.getElementById('cartPanel').classList.remove('open');
    document.getElementById('overlay').classList.remove('open');
    document.body.style.overflow='';
    if(window.visualViewport){window.visualViewport.removeEventListener('resize',_vvResize);window.visualViewport.removeEventListener('scroll',_vvResize);}
    var p=document.getElementById('cartPanel');p.style.height='';p.style.maxHeight='';
  };

  function _vvResize(){
    var p=document.getElementById('cartPanel');
    if(!p.classList.contains('open'))return;
    var v=window.visualViewport;
    if(window.innerWidth<=768){p.style.height=v.height+'px';p.style.maxHeight=v.height+'px';}
    else{p.style.height='';p.style.maxHeight='';}
  }

  /* Delegated item controls are wired inside buildUI(). */

  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&window.closeCart)window.closeCart();
  });

  ['custName','custPhone'].forEach(function(id){
    var el=document.getElementById(id);
    if(el)el.addEventListener('input',function(){renderCart();});
  });

  /* ---- Toast & badge ---- */
  function showToast(msg,type){
    var wrap=document.getElementById('toastWrap');if(!wrap)return;
    var t=document.createElement('div');
    t.className='toast'+(type==='success'?' toast-success':'');
    t.textContent=msg;
    wrap.appendChild(t);
    setTimeout(function(){if(t.parentNode)t.remove();},2600);
  }

  function bounceBadge(){
    var kf=[{transform:'scale(1)'},{transform:'scale(1.12)'},{transform:'scale(1)'}];
    var opt={duration:320,easing:'cubic-bezier(.34,1.56,.64,1)'};
    ['cartFab','mobCartBar','cartBtn'].forEach(function(id){
      var el=document.getElementById(id);
      if(el&&el.animate)el.animate(kf,opt);
    });
  }

  /* ---- Header "Order Now": open the order if there is one,
         otherwise go straight to the menu ---- */
  document.addEventListener('click',function(e){
    var a=e.target.closest?e.target.closest('[data-order-cta]'):null;
    if(!a)return;
    if(count()>0){e.preventDefault();window.openCart();}
  });

  /* ---- Cross-tab sync ---- */
  window.addEventListener('storage',function(e){
    if(e.key!==CART_KEY)return;
    cart=readCart();
    renderCart();
  });

  /* ---- Boot ---- */
  buildUI();

  var cartBtn=document.getElementById('cartBtn');
  if(cartBtn)cartBtn.addEventListener('click',function(){window.openCart();});

  var acctPhone=document.getElementById('custPhone');
  if(acctPhone&&U.acct){var a=U.acct();if(a.phone)acctPhone.value=a.phone;}

  U.renderTotals=renderCart;
  renderCart();

})();
