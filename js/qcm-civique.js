(function(){
  if(!document.getElementById("qcm-start")) return;
  var DATA = [{"q": "Un homme refuse de serrer la main d'une femme médecin lors d'une consultation médicale pour des raisons religieuses. Que dit le droit ?", "o": ["Le médecin doit respecter sa croyance et ne pas insister", "Ce n'est pas un délit mais le respect mutuel est attendu", "Le patient sera sanctionné pénalement", "Le médecin peut refuser de le soigner"], "a": 1, "e": "Si le refus de serrer la main n'est pas en soi un délit, l'égalité entre les femmes et les hommes est un principe constitutionnel. Dans le cadre républicain, le respect mutuel est attendu.", "c": "Principes et valeurs de la République"}, {"q": "En quelle année l'esclavage a-t-il été aboli définitivement en France ?", "o": ["1789", "1794", "1848", "1905"], "a": 2, "e": "L'esclavage a été définitivement aboli le 27 avril 1848 par le décret de Victor Schœlcher.", "c": "Histoire, géographie et culture"}, {"q": "Un élève de lycée public porte un tee-shirt avec un slogan politique visible. L'établissement peut-il le lui interdire ?", "o": ["Oui, tout signe politique est interdit à l'école", "Non, seuls les signes religieux ostensibles sont interdits", "Oui, si les autres élèves sont gênés", "Non, car la liberté d'expression est absolue à l'école"], "a": 1, "e": "La loi de 2004 interdit les signes religieux ostensibles dans les écoles publiques. Les signes politiques ne sont pas visés par cette loi, mais l'établissement peut intervenir si cela trouble l'ordre scolaire.", "c": "Principes et valeurs de la République"}, {"q": "En quelle année Napoléon Ier est-il devenu empereur ?", "o": ["1789", "1799", "1804", "1815"], "a": 2, "e": "Napoléon Bonaparte a été sacré empereur des Français le 2 décembre 1804, à Notre-Dame de Paris.", "c": "Histoire, géographie et culture"}, {"q": "Votre employeur dans le secteur privé vous demande de retirer un signe religieux discret. Que devez-vous savoir ?", "o": ["C'est toujours interdit dans le privé", "Oui, si le règlement intérieur le prévoit", "Seul l'État peut imposer cette règle", "Vous devez démissionner"], "a": 1, "e": "Dans le secteur privé, l'employeur peut restreindre le port de signes religieux si le règlement intérieur le prévoit et si c'est justifié par la nature de la tâche ou les nécessités de l'entreprise.", "c": "Principes et valeurs de la République"}, {"q": "De quand date l'appel à la résistance du général de Gaulle ?", "o": ["Le 14 juillet 1940", "Le 18 juin 1940", "Le 8 mai 1945", "Le 6 juin 1944"], "a": 1, "e": "Le 18 juin 1940, le général de Gaulle lance depuis Londres un appel à la résistance sur les ondes de la BBC.", "c": "Histoire, géographie et culture"}, {"q": "Un parent demande que sa fille soit dispensée de cours de sport mixtes à l'école publique pour des raisons religieuses. Quelle est la position correcte ?", "o": ["L'école doit accepter la demande", "L'école peut refuser au nom de la mixité", "Le parent peut retirer son enfant de l'école", "L'école doit proposer des cours séparés"], "a": 1, "e": "La mixité est un principe fondamental de l'école publique française. Un enfant ne peut pas être dispensé d'un enseignement obligatoire pour des raisons religieuses.", "c": "Principes et valeurs de la République"}, {"q": "Depuis quand les Français élisent-ils le président au suffrage universel direct ?", "o": ["1848", "1946", "1958", "1962"], "a": 3, "e": "Depuis la réforme constitutionnelle de 1962, le Président de la République est élu au suffrage universel direct.", "c": "Histoire, géographie et culture"}, {"q": "Votre ami, citoyen européen résidant en France, vous demande s'il peut voter aux élections municipales. Que lui répondez-vous ?", "o": ["Non, seuls les Français peuvent voter", "Oui, aux élections municipales et européennes", "Oui, il peut voter à toutes les élections", "Non, il doit d'abord être naturalisé"], "a": 1, "e": "Les citoyens de l'Union européenne résidant en France peuvent voter et se présenter aux élections municipales et européennes, mais pas aux élections nationales (présidentielle, législatives).", "c": "Système institutionnel et politique"}, {"q": "Lors d'une cérémonie publique, quelqu'un refuse de se lever pendant La Marseillaise. Que se passe-t-il ?", "o": ["Il sera arrêté immédiatement", "Un manque de respect, pas un délit", "Il recevra une amende", "Il perdra sa nationalité"], "a": 1, "e": "Ne pas se lever pendant l'hymne national est considéré comme un manque de respect envers les symboles de la République, mais ce n'est pas un délit en soi. Cependant, l'outrage au drapeau ou à l'hymne dans un contexte officiel peut être sanctionné.", "c": "Principes et valeurs de la République"}];
  var PASS=8, KEY='nffCivicDone';
  var quiz=DATA.map(function(q){return {q:q.q,e:q.e,c:q.c,opts:q.o,correct:q.a};});
  var answers=new Array(quiz.length).fill(null), idx=0;
  function $(s){return document.querySelector(s);}
  function esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
  function show(id){['qcm-start','qcm-quiz','qcm-result'].forEach(function(x){$('#'+x).style.display=(x===id?'block':'none');});}
  function start(){answers=new Array(quiz.length).fill(null);idx=0;show('qcm-quiz');render();}
  function render(){
    var q=quiz[idx];
    $('#qcm-progress').textContent='Question '+(idx+1)+' / '+quiz.length;
    $('#qcm-fill').style.width=(idx/quiz.length*100)+'%';
    $('#qcm-question').textContent=q.q;
    var ob=$('#qcm-options');ob.innerHTML='';
    q.opts.forEach(function(opt,i){
      var b=document.createElement('button');b.className='qcm-opt'+(answers[idx]===i?' selected':'');b.type='button';b.textContent=opt;
      b.onclick=function(){answers[idx]=i;render();};ob.appendChild(b);
    });
    $('#qcm-prev').disabled=idx===0;
    $('#qcm-next').style.display=idx<quiz.length-1?'inline-flex':'none';
    $('#qcm-finish').style.display=idx===quiz.length-1?'inline-flex':'none';
  }
  function finish(){
    var score=quiz.reduce(function(s,q,i){return s+(answers[i]===q.correct?1:0);},0);
    try{localStorage.setItem(KEY,JSON.stringify({answers:answers,score:score}));}catch(e){}
    renderResult(score,answers);
  }
  function renderResult(score,ans){
    show('qcm-result');
    var pass=score>=PASS;
    var sc=$('#qcm-score');sc.textContent=score+'/'+quiz.length;sc.className='qcm-score '+(pass?'pass':'fail');
    $('#qcm-verdict').textContent=pass?'Impressionnant — vous maîtrisez même les pièges.':'Ces questions sont les plus piégeuses de l’examen.';
    $('#qcm-resultsub').textContent='Vous avez répondu aux 10 questions les plus difficiles. Pour vous entraîner sur les 258 questions complètes, l’examen blanc chronométré et les corrections détaillées, continuez sur l’app.';
    var rev=$('#qcm-reviewlist');rev.innerHTML='';
    quiz.forEach(function(q,i){
      var ok=ans[i]===q.correct, ua=ans[i]==null?'(aucune réponse)':q.opts[ans[i]];
      var html='<div class="qcm-rev-q">'+(i+1)+'. '+esc(q.q)+'</div>'+
        '<div class="qcm-rev-line '+(ok?'qcm-rev-ok':'qcm-rev-ko')+'">'+(ok?'✓':'✗')+' Votre réponse : '+esc(ua)+'</div>'+
        (ok?'':'<div class="qcm-rev-line qcm-rev-ok">✓ Bonne réponse : '+esc(q.opts[q.correct])+'</div>')+
        '<div class="qcm-rev-exp">'+esc(q.e)+'</div>';
      var it=document.createElement('div');it.className='qcm-rev-item';it.innerHTML=html;rev.appendChild(it);
    });
  }
  document.addEventListener('click',function(e){
    var t=e.target;
    if(t.closest&&t.closest('#qcm-startbtn'))start();
    else if(t.id==='qcm-next'){idx=Math.min(quiz.length-1,idx+1);render();}
    else if(t.id==='qcm-prev'){idx=Math.max(0,idx-1);render();}
    else if(t.id==='qcm-finish')finish();
  });
  var saved=null;try{saved=JSON.parse(localStorage.getItem(KEY));}catch(e){}
  if(saved&&saved.answers){answers=saved.answers;renderResult(saved.score,saved.answers);}
})();
