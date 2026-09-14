'use strict';
(function(){
  if(!document.getElementById('cartPanel'))return;
  var WA=window.UHCP&&window.UHCP.WA||'923466816902';

  /* ---- Menu filter tabs ---- */
  document.querySelectorAll('.ftab').forEach(function(t){
    t.addEventListener('click',function(){
      document.querySelectorAll('.ftab').forEach(function(x){x.classList.remove('active');});
      t.classList.add('active');
      var f=t.dataset.f;
      document.querySelectorAll('.mcard').forEach(function(c){
        c.classList.toggle('hidden',f!=='all'&&c.dataset.cat!==f);
      });
    });
  });

  /* ---- Quantity buttons ---- */
  window.changeQty=function(btn,delta){
    var card=btn.closest('.mcard');
    var step=parseFloat(card.dataset.step||'1');
    var el=card.querySelector('.qval');
    var v=parseFloat(el.textContent);
    v=Math.max(step,Math.round((v+delta*step)*100)/100);
    el.textContent=v;
  };

  /* ---- Size selector ---- */
  window.selectSize=function(btn,price,label){
    var card=btn.closest('.mcard');
    card.querySelectorAll('.size-btn').forEach(function(b){b.classList.remove('active');});
    btn.classList.add('active');
    card.dataset.price=price;
    card.dataset.name=card.dataset.base+' ('+label+')';
    card.querySelector('.pr').textContent='Rs. '+price;
  };

  /* ---- Cart state ---- */
  var cart={};

  window.addToCart=function(btn){
    var card=btn.closest('.mcard');
    var name=card.dataset.name;
    var price=parseFloat(card.dataset.price);
    var unit=card.dataset.unit||'';
    var img=card.dataset.img||'';
    var qty=parseFloat(card.querySelector('.qval').textContent);
    if(cart[name]){cart[name].qty=Math.round((cart[name].qty+qty)*100)/100;}
    else{cart[name]={price:price,qty:qty,unit:unit,img:img};}
    renderCart();
    btn.textContent='Added \u2713';btn.classList.add('added');
    setTimeout(function(){btn.textContent='Add to Order';btn.classList.remove('added');},1300);
    showToast('\u2713 '+name+' added to order','success');
    bounceBadge();
  };

  window.cartQty=function(name,delta){
    if(!cart[name])return;
    var step=cart[name].unit==='kg'?0.5:1;
    cart[name].qty=Math.max(step,Math.round((cart[name].qty+delta*step)*100)/100);
    renderCart();
  };

  window.removeItem=function(name){delete cart[name];renderCart();};

  function getTotal(){return Object.values(cart).reduce(function(s,it){return s+it.price*it.qty;},0);}

  function buildWaMsg(items,total,extra){
    if(!extra)extra={};
    var name=extra.name||'';
    var lines=['\uD83C\uDF7D\uFE0F *Order \u2014 Umar Hayat Chaska Point*',''];
    items.forEach(function(it){
      var ql=it.unit?it.qty+' '+it.unit:'\u00D7'+it.qty;
      lines.push('\u2022 '+it.name+' ('+ql+') \u2014 Rs. '+Math.round(it.price*it.qty));
    });
    lines.push('','*Total: Rs. '+Math.round(total)+'*');
    if(name)lines.push('Name: '+name);
    return lines.join('\n');
  }

  function waLink(msg){return 'https://api.whatsapp.com/send?phone='+WA+'&text='+encodeURIComponent(msg);}

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
        return '<div class="citem"><div class="citem-img">'+(it.img?'<img src="'+it.img+'" alt="'+n+'" loading="lazy">':'')+'</div><div class="citem-info"><div class="citem-name">'+n+'</div><div class="citem-price">Rs. '+line+' ('+ql+')</div></div><div class="citem-right"><div class="citem-qty"><button class="cq-btn" onclick="cartQty(\''+n.replace(/'/g,"\\'")+'\',-1)" aria-label="Decrease">\u2212</button><span class="cq-val">'+it.qty+'</span><button class="cq-btn" onclick="cartQty(\''+n.replace(/'/g,"\\'")+'\',1)" aria-label="Increase">+</button></div><button class="citem-del" onclick="removeItem(\''+n.replace(/'/g,"\\'")+'\')">Remove</button></div></div>';
      }).join('');
      summaryEl.style.display='block';footerEl.style.display='block';
      document.getElementById('subtotalEl').textContent='Rs. '+total;
      document.getElementById('totalEl').textContent='Rs. '+total;
    }
    var count=names.length;
    document.getElementById('cartSubhead').textContent=count===1?'1 item':count+' items';
    document.getElementById('cartCount').textContent=count;
    document.getElementById('cartFab').classList.toggle('hidden',count===0);
    document.getElementById('mobCartItems').textContent=count===1?'1 item':count+' items';
    document.getElementById('mobCartTotal').textContent='Rs. '+total;
    document.getElementById('mobCartBar').classList.toggle('visible',count>0);
    document.getElementById('waFloat').style.bottom=count>0?'calc(76px + env(safe-area-inset-bottom))':'24px';
    var waBtn=document.getElementById('waFinalBtn');
    if(waBtn){
      var name=(document.getElementById('custName')&&document.getElementById('custName').value.trim())||'';
      var items=names.map(function(n){return{name:n,qty:cart[n].qty,unit:cart[n].unit,price:cart[n].price};});
      waBtn.href=waLink(buildWaMsg(items,total,{name:name}));
    }
  }

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

  document.getElementById('overlay').addEventListener('click',closeCart);
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){closeCart();window.closeMobNav&&closeMobNav();}});

  /* ---- Customer name re-render ---- */
  var ci=document.getElementById('custName');
  if(ci)ci.addEventListener('input',function(){renderCart();});

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
    ['cartFab','mobCartBar'].forEach(function(id){
      var el=document.getElementById(id);
      if(el&&el.animate)el.animate(kf,opt);
    });
  }
})();