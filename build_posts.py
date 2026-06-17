# Build completo dos 14 posts (ter/qui até 30/07) no padrão do feed da Juliska.
# Gera: slides 1080x1350 + caption.txt + .github/workflows/publicar-<slug>.yml
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
# ── Paleta "Geração A" — harmoniza com o feed (Moema/Brooklin/V.Mariana/Linha17) ──
CREME_TOP=(242,233,216); CREME_BOTTOM=(231,218,193)   # gradiente vertical do fundo
DOURADO=(139,111,46)        # filete, eyebrow gold, "CONTINUE"
DOURADO_FORT=(184,137,61)   # título do bairro, número, citações
ESCURO=(26,20,9)            # eyebrow ALL-CAPS
CINZA=(45,45,45)           # corpo (Georgia, legível)
CINZA_MUTED=(107,107,107)   # rodapé/créditos
F="/System/Library/Fonts/Supplemental/"
def didot(s,i=0): return ImageFont.truetype(F+"Didot.ttc",s,index=i)
def did_bd(s): return didot(s,2)
def georgia(s): return ImageFont.truetype(F+"Georgia.ttf",s)
def bask_it(s): return ImageFont.truetype(F+"Baskerville.ttc",s,index=2)
def sans(s): return ImageFont.truetype(F+"Futura.ttc",s,index=0)
def bg():
    g=Image.new("RGB",(1,H))
    for y in range(H):
        t=y/(H-1)
        g.putpixel((0,y),tuple(int(CREME_TOP[i]+(CREME_BOTTOM[i]-CREME_TOP[i])*t) for i in range(3)))
    return g.resize((W,H))
def wrap(d,t,f,mw):
    o,l=[],""
    for w in t.split():
        x=(l+" "+w).strip()
        if d.textlength(x,font=f)<=mw: l=x
        else: o.append(l); l=w
    if l: o.append(l)
    return o
def trk(d,y,t,f,fill,tr,cx=W//2):
    ws=[d.textlength(c,font=f) for c in t]; x=cx-(sum(ws)+tr*(len(t)-1))/2
    for c,w in zip(t,ws): d.text((x,y),c,font=f,fill=fill); x+=w+tr
def ctr(d,y,t,f,fill): d.text(((W-d.textlength(t,font=f))/2,y),t,font=f,fill=fill)
def seta(d,x,y,fill,w=26):
    d.line([(x,y),(x+w,y)],fill=fill,width=2)
    d.line([(x+w-8,y-6),(x+w,y),(x+w-8,y+6)],fill=fill,width=2,joint="curve")
def divisor(d,y,w=70): d.line([(W//2-w,y),(W//2+w,y)],fill=DOURADO,width=2)
def rodape(d,cont=True):
    # rodapé centralizado, igual ao feed antigo
    if cont:
        f=sans(21); txt="CONTINUE"
        wt=sum(d.textlength(c,font=f) for c in txt)+3*(len(txt)-1); total=wt+46
        x0=(W-total)/2; trk(d,H-158,txt,f,DOURADO,3,cx=x0+wt/2)
        seta(d,x0+wt+20,H-146,DOURADO)
    trk(d,H-92,"CYRELA · POR JULISKA TORDINO",sans(19),CINZA_MUTED,3)

def capa_bairro(label,nome,sub,out):
    img=bg();d=ImageDraw.Draw(img)
    trk(d,170,label.upper(),sans(25),ESCURO,8)
    n=nome.upper(); fs=118 if len(n)<=7 else (94 if len(n)<=11 else 68)
    yt=445; trk(d,yt,n,did_bd(fs),DOURADO_FORT,max(4,int(fs*0.11)))
    divisor(d,yt+fs+58); fsub=bask_it(48); y=yt+fs+118
    for ln in wrap(d,sub,fsub,W-280): ctr(d,y,ln,fsub,CINZA); y+=64
    rodape(d,True); img.save(out,quality=95)

def capa_dica(label,perg,sub,out):
    img=bg();d=ImageDraw.Draw(img)
    trk(d,170,label.upper(),sans(25),ESCURO,8)
    fp=bask_it(66); lines=wrap(d,perg,fp,W-230); y=460-len(lines)*46
    for ln in lines: ctr(d,y,ln,fp,DOURADO_FORT); y+=88
    divisor(d,y+24); y+=74; fs=bask_it(42)
    for ln in wrap(d,sub,fs,W-320): ctr(d,y,ln,fs,CINZA); y+=58
    rodape(d,True); img.save(out,quality=95)

def conteudo(header,titulo,corpo,out):
    img=bg();d=ImageDraw.Draw(img)
    trk(d,180,header.upper(),sans(24),ESCURO,7); divisor(d,242,58)
    ft=did_bd(72); y=370
    for ln in wrap(d,titulo,ft,W-220): ctr(d,y,ln,ft,DOURADO_FORT); y+=86
    divisor(d,y+24,55); y+=78; fb=georgia(37)
    for ln in wrap(d,corpo,fb,W-300): ctr(d,y,ln,fb,CINZA); y+=56
    rodape(d,True); img.save(out,quality=95)

def fecho(header,frase,out):
    img=bg();d=ImageDraw.Draw(img)
    trk(d,180,header.upper(),sans(24),ESCURO,7); divisor(d,242,58)
    fr=bask_it(50); y=415
    for ln in wrap(d,frase,fr,W-250): ctr(d,y,ln,fr,DOURADO_FORT); y+=66
    divisor(d,y+34,55); y+=92
    ctr(d,y,"Juliska Tordino",bask_it(64),DOURADO_FORT); y+=104
    trk(d,y,"CORRETORA · CYRELA · CRECI 133.239-F",sans(20),CINZA_MUTED,4); y+=46
    trk(d,y,"(11) 9.8127.6060 · @JULISKA.IMOVEIS",sans(18),CINZA_MUTED,3)
    img.save(out,quality=95)

WF='''name: Publicar {nome}

on:
  workflow_dispatch:   # disparo pelo agendador Apps Script (cron do GitHub é nao-confiavel)

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install requests
      - name: Publicar carrossel
        env:
          INSTAGRAM_BUSINESS_ID:   ${{{{ secrets.INSTAGRAM_BUSINESS_ID }}}}
          INSTAGRAM_ACCESS_TOKEN:  ${{{{ secrets.INSTAGRAM_ACCESS_TOKEN }}}}
          META_API_VERSION:        v19.0
          GITHUB_REPOSITORY:       ${{{{ github.repository }}}}
          GITHUB_REF_NAME:         ${{{{ github.ref_name }}}}
        run: python lib/publish_carousel.py --folder posts/{slug} --caption-file posts/{slug}/caption.txt
'''

def build(p):
    slug=p["slug"]; os.makedirs(f"posts/{slug}",exist_ok=True)
    if p["tipo"]=="bairro":
        capa_bairro(p["label"],p["nome"],p["sub"],f"posts/{slug}/slide_1.png")
        hdr=f"{p['nome']} · 2026"; fhdr=f"Em atendimento · {p['nome']}"
    else:
        capa_dica(p["label"],p["perg"],p["sub"],f"posts/{slug}/slide_1.png")
        hdr=p["label"]; fhdr=p["label"]
    conteudo(hdr,p["p1"][0],p["p1"][1],f"posts/{slug}/slide_2.png")
    conteudo(hdr,p["p2"][0],p["p2"][1],f"posts/{slug}/slide_3.png")
    fecho(fhdr,p["fecho"],f"posts/{slug}/slide_4.png")
    open(f"posts/{slug}/caption.txt","w").write(p["caption"].strip()+"\n")
    open(f".github/workflows/publicar-{slug}.yml","w").write(
        WF.format(nome=p["nome_wf"],slug=slug))
    print("  ✓",slug,"·",p["databr"])

# ════ CONTEÚDO DOS 14 POSTS ════
POSTS=[
{"slug":"itaim","tipo":"bairro","nome":"Itaim Bibi","nome_wf":"Itaim Bibi",
 "label":"Bairro mapeado · 03","databr":"Terca 16/06/2026","cron":"0 14 16 6 *",
 "sub":"Onde o dinheiro de São Paulo trabalha — e cada vez mais mora.",
 "p1":("O que mudou","Deixou de ser só escritório. As torres residenciais de alto padrão transformaram o Itaim em endereço de morar, não só de trabalhar."),
 "p2":("Quem procura","Executivos que cansaram do trânsito e querem morar a uma caminhada do escritório. No Itaim, o que se compra é tempo de volta no fim do dia."),
 "fecho":"Conversa antes de visitar. Eu sei o que cada empreendimento entrega de verdade.",
 "caption":'''Bairro mapeado · 03

Itaim Bibi é onde o dinheiro de São Paulo trabalha — e, cada vez mais, onde ele mora.

Por mais de 20 anos acompanhei o Itaim mudar de pele. Era o bairro do escritório, do happy hour, da Faria Lima. Hoje é também o bairro de quem decidiu apagar o trânsito da própria rotina.

As torres residenciais de alto padrão mudaram o jogo: dá pra morar a uma caminhada do trabalho, com lazer de resort dentro de casa.

Quem compra no Itaim hoje não está comprando metro quadrado. Está comprando o fim do deslocamento.

Se você está olhando a região, me chama antes de visitar plantão. Eu te conto qual empreendimento faz sentido pro seu momento.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#Itaim #ItaimBibi #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela'''},

{"slug":"dica_a_vista","tipo":"dica","nome":"Dica · A Vista","nome_wf":"Dica · A Vista",
 "label":"Antes de comprar · 01","databr":"Quinta 18/06/2026","cron":"0 14 18 6 *",
 "perg":"Por que todo anúncio diz “valor à vista”?",
 "sub":"O que esse termo realmente significa — e por que te protege.",
 "p1":("O que significa","“Valor à vista” é o preço da unidade pago sem financiamento. Não é promessa nem “a partir de” inventado: é o número de referência real de uma unidade específica."),
 "p2":("Como te protege","Eu trabalho sempre com a referência completa: qual unidade, qual torre, qual metragem e o valor à vista daquela unidade. É o que o CRECI exige — e o que te protege de surpresa na tabela."),
 "fecho":"Antes de se apaixonar por um “a partir de”, pergunte: à vista de qual unidade?",
 "caption":'''Antes de comprar · 01

“Por que todo anúncio de alto padrão diz ‘valor à vista’?”

É uma das perguntas que mais ouço — e a resposta diz muito sobre como ler um anúncio.

“Valor à vista” é o preço da unidade pago sem financiamento. Não é promessa, não é “a partir de” inventado: é o número de referência real de uma unidade específica.

Quando alguém te mostra só “a partir de R$ X” sem dizer a unidade e a forma de pagamento, você não está vendo um preço — está vendo uma isca.

Eu trabalho sempre com a referência completa: qual unidade, qual torre, qual metragem e o valor à vista daquela unidade. É o que o CRECI exige, e é o que te protege.

Antes de se apaixonar por um “a partir de”, pergunte: à vista de qual unidade?

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #ComprarImovel #SaoPaulo'''},

{"slug":"campo_belo","tipo":"bairro","nome":"Campo Belo","nome_wf":"Campo Belo",
 "label":"Bairro mapeado · 04","databr":"Terca 23/06/2026","cron":"0 14 23 6 *",
 "sub":"O bairro que São Paulo descobre por último.",
 "p1":("A identidade","Encostado em Moema, Brooklin e Vila Nova Conceição — mas com algo que nenhum deles tem: o silêncio. Ruas arborizadas, baixa circulação e comércio de bairro que sobreviveu à verticalização."),
 "p2":("Quem procura hoje","Quem quer qualidade de vida sem abrir mão de estar a dez minutos de tudo. Congonhas ao lado afasta alguns e atrai executivos que viajam toda semana."),
 "fecho":"Um bairro de quem já sabe o que quer. Não vende sonho — vende rotina boa.",
 "caption":'''Bairro mapeado · 04

Campo Belo é o bairro que os paulistanos descobrem por último — e se perguntam por que demoraram.

Fica encostado em Moema, Brooklin e Vila Nova Conceição, mas tem uma identidade que nenhum deles tem: o silêncio. Ruas arborizadas, baixa circulação e um comércio de bairro que sobreviveu à verticalização.

A procura mudou de perfil: antes era quem queria sair do Itaim por preço. Hoje é quem quer qualidade de vida sem abrir mão de estar a dez minutos de tudo.

Congonhas ao lado afasta alguns e atrai executivos que viajam toda semana.

É um bairro de quem já sabe o que quer. Não vende sonho, vende rotina boa.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#CampoBelo #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela #ZonaSul'''},

{"slug":"dica_financiamento","tipo":"dica","nome":"Dica · A Vista x Financiamento","nome_wf":"Dica · Financiamento",
 "label":"Antes de comprar · 02","databr":"Quinta 25/06/2026","cron":"0 14 25 6 *",
 "perg":"Faz sentido pagar à vista no alto padrão?",
 "sub":"Nem sempre. Depende de quanto o seu dinheiro rende fora do imóvel.",
 "p1":("O outro lado","Pagar à vista trava capital que poderia render. Em alto padrão, muita gente prefere dar entrada forte e diluir o restante — mantendo liquidez para investir."),
 "p2":("A conta que importa","A pergunta certa não é “à vista ou financiado”. É: o desconto à vista supera o que esse dinheiro renderia investido? É isso que eu ajudo a calcular antes da decisão."),
 "fecho":"À vista não é sempre o melhor negócio. É o melhor número de partida.",
 "caption":'''Antes de comprar · 02

“Se eu tenho o valor, melhor pagar à vista, né?”

Nem sempre. E essa é uma das contas que mais vejo gente errar no alto padrão.

Pagar à vista trava um capital que poderia estar rendendo. Muito cliente meu prefere dar uma entrada forte e diluir o restante — mantendo liquidez pra investir ou pra outra oportunidade.

A pergunta certa não é “à vista ou financiado”. É: o desconto à vista supera o que esse dinheiro renderia investido no mesmo período?

Às vezes sim, às vezes não. Depende do empreendimento, do desconto e do seu momento.

É exatamente esse tipo de conta que eu faço com você antes de bater o martelo.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #Financiamento #SaoPaulo'''},

{"slug":"vila_olimpia","tipo":"bairro","nome":"Vila Olímpia","nome_wf":"Vila Olimpia",
 "label":"Bairro mapeado · 05","databr":"Terca 30/06/2026","cron":"0 14 30 6 *",
 "sub":"O bairro que não dorme — e agora também acolhe.",
 "p1":("O que mudou","Era sinônimo de balada e escritório. Ganhou torres residenciais que trouxeram famílias pra um bairro que antes esvaziava à noite."),
 "p2":("O equilíbrio","Hoje é o ponto onde a vida executiva encontra a vida de bairro. Faria Lima de um lado, parques e escolas do outro — sem precisar do carro pra nada."),
 "fecho":"Conversa antes de visitar. Eu te conto o que cada torre entrega de verdade.",
 "caption":'''Bairro mapeado · 05

A Vila Olímpia era o bairro que não dormia. Hoje ela também acolhe.

Por anos foi sinônimo de balada, escritório e movimento. À noite, esvaziava. As torres residenciais mudaram isso: trouxeram famílias, rotina, vida de bairro.

Hoje é o ponto onde a vida executiva encontra a vida de bairro. Faria Lima de um lado, parques e escolas do outro — e quase tudo a pé.

Quem procura a Vila Olímpia hoje quer estar no centro de tudo sem abrir mão de voltar pra casa em cinco minutos.

Se você está olhando a região, me chama antes de visitar.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#VilaOlimpia #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela #ZonaSul'''},

{"slug":"dica_incc","tipo":"dica","nome":"Dica · INCC","nome_wf":"Dica · INCC",
 "label":"Antes de comprar · 03","databr":"Quinta 02/07/2026","cron":"0 14 2 7 *",
 "perg":"Comprou na planta? O INCC mexe no seu preço.",
 "sub":"O índice que corrige o saldo até a entrega — e ninguém te explica.",
 "p1":("O que é","INCC é o índice que corrige o saldo devedor de um imóvel na planta até a entrega. Ele acompanha o custo da construção — não a inflação geral."),
 "p2":("Por que importa","O preço que você assina hoje não é o que você paga até o fim. Eu mostro a simulação corrigida antes de você decidir, pra não ter surpresa no caminho."),
 "fecho":"Comprar na planta é ótimo. Comprar sem entender o INCC, não.",
 "caption":'''Antes de comprar · 03

Comprou na planta? Então o INCC já está mexendo no seu preço — e quase ninguém te explica isso na hora da venda.

INCC é o índice que corrige o saldo devedor de um imóvel na planta até a entrega. Ele acompanha o custo da construção (cimento, aço, mão de obra), não a inflação do supermercado.

Na prática: o preço que você assina hoje não é exatamente o que você termina de pagar. O saldo é corrigido mês a mês até as chaves.

Não é pegadinha — é como funciona todo imóvel na planta. O problema é descobrir isso depois.

Eu mostro a simulação já corrigida antes de você decidir. Sem surpresa no meio do caminho.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #ImovelNaPlanta #INCC'''},

{"slug":"jardins","tipo":"bairro","nome":"Jardins","nome_wf":"Jardins",
 "label":"Bairro mapeado · 06","databr":"Terca 07/07/2026","cron":"0 14 7 7 *",
 "sub":"O endereço que nunca precisou se reinventar.",
 "p1":("Por que resiste","Enquanto bairros sobem e descem, os Jardins se mantêm. Arborização protegida, baixa verticalização e um padrão que o tempo não desgasta."),
 "p2":("Quem procura","Quem já morou em vários lugares e voltou pra cá. Nos Jardins não se compra novidade — se compra permanência."),
 "fecho":"Alguns endereços valorizam. Outros simplesmente não desvalorizam nunca.",
 "caption":'''Bairro mapeado · 06

Os Jardins são o endereço que nunca precisou se reinventar.

Em mais de 20 anos de mercado, vi bairros inteiros subirem e descerem de patamar. Os Jardins se mantêm. Arborização protegida por lei, baixa verticalização, um padrão que o tempo não desgasta.

Quem procura os Jardins normalmente já morou em vários lugares — e voltou. Não compra novidade: compra permanência.

É o tipo de endereço que não promete valorização explosiva. Promete algo mais raro: não desvalorizar nunca.

Se você está olhando a região, vale conversar antes de visitar. Aqui, cada quadra tem um perfil.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#Jardins #JardimPaulista #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela'''},

{"slug":"dica_planta_pronto","tipo":"dica","nome":"Dica · Planta x Pronto","nome_wf":"Dica · Planta x Pronto",
 "label":"Antes de comprar · 04","databr":"Quinta 09/07/2026","cron":"0 14 9 7 *",
 "perg":"Na planta ou pronto: qual compensa mais?",
 "sub":"Os dois funcionam. O que muda é o que você está disposto a esperar.",
 "p1":("Na planta","Preço menor, condição de pagamento diluída e escolha de unidade. Em troca: tempo de espera e o saldo corrigido pelo INCC até a entrega."),
 "p2":("Pronto","Você vê o que compra e muda na hora. Em troca: preço cheio e pagamento mais concentrado. Ideal pra quem tem pressa ou quer zero incerteza."),
 "fecho":"Não existe melhor. Existe o que combina com o seu momento — e é isso que eu ajudo a enxergar.",
 "caption":'''Antes de comprar · 04

“Compro na planta ou já pronto?”

Os dois funcionam. O que muda é o que você está disposto a trocar.

Na planta: preço menor, pagamento diluído e a chance de escolher a melhor unidade. Em troca, você espera — e o saldo é corrigido pelo INCC até a entrega.

Pronto: você vê exatamente o que compra e se muda na hora. Em troca, paga o preço cheio, com pagamento mais concentrado.

Pra quem tem horizonte e quer otimizar o investimento, a planta costuma compensar. Pra quem tem pressa ou quer zero incerteza, o pronto resolve.

Não existe melhor. Existe o que combina com o seu momento — e é isso que eu ajudo a enxergar antes da decisão.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #ImovelNaPlanta #SaoPaulo'''},

{"slug":"pinheiros","tipo":"bairro","nome":"Pinheiros","nome_wf":"Pinheiros",
 "label":"Bairro mapeado · 07","databr":"Terca 14/07/2026","cron":"0 14 14 7 *",
 "sub":"Onde a cidade fica mais jovem sem ficar menos valorizada.",
 "p1":("A virada","Gastronomia, cultura e metrô transformaram Pinheiros no bairro mais desejado por quem tem 30 e poucos — e poder de compra."),
 "p2":("O que isso faz com o preço","Demanda jovem e qualificada sustenta a valorização. Comprar em Pinheiros é apostar num bairro que não vai sair de moda tão cedo."),
 "fecho":"Conversa antes de visitar. Cada rua de Pinheiros é um bairro diferente.",
 "caption":'''Bairro mapeado · 07

Pinheiros é onde São Paulo fica mais jovem sem ficar menos valorizada.

Gastronomia, cultura, metrô em duas linhas e uma vida de rua que poucos bairros têm. Pinheiros virou o endereço mais desejado por quem tem trinta e poucos anos — e poder de compra.

E isso muda o jogo do investimento: demanda jovem e qualificada é o que sustenta a valorização ao longo do tempo.

Comprar em Pinheiros é apostar num bairro que não vai sair de moda tão cedo.

Mas atenção: cada rua aqui é quase um bairro diferente. Vale conversar antes de visitar — eu te conto onde vale e onde não vale.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#Pinheiros #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela'''},

{"slug":"dica_tabela","tipo":"dica","nome":"Dica · Tabela de Vendas","nome_wf":"Dica · Tabela",
 "label":"Antes de comprar · 05","databr":"Quinta 16/07/2026","cron":"0 14 16 7 *",
 "perg":"Como ler uma tabela de vendas sem se perder?",
 "sub":"Entrada, mensais, balões e reforços — o que cada linha realmente significa.",
 "p1":("Os blocos","Toda tabela tem entrada (ato), parcelas mensais, reforços (semestrais) e balões anuais. O preço final é a soma de tudo — não só da parcela que te mostram."),
 "p2":("Onde mora o detalhe","A mesma unidade pode caber ou não no seu bolso só pela forma de pagamento. Eu monto o fluxo com você antes de assinar, pra não ter aperto lá na frente."),
 "fecho":"O preço não está na primeira linha. Está na soma honesta de todas elas.",
 "caption":'''Antes de comprar · 05

Uma tabela de vendas assusta mais do que devia — e é de propósito que ela parece complicada.

Toda tabela tem quatro blocos: a entrada (ato), as parcelas mensais, os reforços (geralmente semestrais) e os balões anuais. O preço final é a soma de tudo isso — não só da mensal que te mostram em destaque.

A mesma unidade pode caber ou não caber no seu bolso só pela forma de pagamento. Duas tabelas com o mesmo “valor” podem ter fôlegos completamente diferentes.

Por isso eu monto o fluxo de pagamento com você antes de assinar qualquer coisa. Pra você enxergar o esforço real mês a mês — e não tomar um susto lá na frente.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #ComprarImovel #SaoPaulo'''},

{"slug":"vila_nova_conceicao","tipo":"bairro","nome":"V. N. Conceição","nome_wf":"Vila Nova Conceicao",
 "label":"Bairro mapeado · 08","databr":"Terca 21/07/2026","cron":"0 14 21 7 *",
 "sub":"O metro quadrado mais caro de São Paulo tem motivo.",
 "p1":("Por que custa","Baixíssima oferta, lotes generosos, Parque Ibirapuera ao lado e uma exclusividade que não se reproduz. É escassez pura."),
 "p2":("Quem compra","Quem busca o ativo mais resiliente da cidade. Na Vila Nova Conceição, o imóvel é tão patrimônio quanto moradia."),
 "fecho":"Há bairros caros por moda. Este é caro por matemática.",
 "caption":'''Bairro mapeado · 08

A Vila Nova Conceição tem o metro quadrado mais caro de São Paulo. E não é capricho — é matemática.

Baixíssima oferta de terrenos, lotes generosos, o Parque Ibirapuera literalmente ao lado e uma exclusividade que simplesmente não se reproduz em outro lugar. Isso é escassez pura.

Quem compra na VNC não está só escolhendo onde morar. Está escolhendo o ativo mais resiliente da cidade — aquele que segura valor mesmo quando o mercado oscila.

Aqui o imóvel é tão patrimônio quanto moradia.

Se você está nesse nível de busca, a conversa é outra. Me chama — eu trabalho exatamente esse padrão.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#VilaNovaConceicao #VNC #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela'''},

{"slug":"dica_permuta","tipo":"dica","nome":"Dica · Permuta","nome_wf":"Dica · Permuta",
 "label":"Antes de comprar · 06","databr":"Quinta 23/07/2026","cron":"0 14 23 7 *",
 "perg":"Dá pra usar o apartamento atual como entrada?",
 "sub":"Na maioria dos lançamentos de alto padrão, dá. Chama-se permuta.",
 "p1":("Como funciona","A construtora aceita o seu imóvel atual como parte do pagamento do novo. Você não precisa vender primeiro nem ficar com dois financiamentos."),
 "p2":("O que avaliar","O valor que dão pelo seu imóvel e as condições do novo. Nem toda permuta é vantajosa — eu comparo com a venda direta antes de você decidir."),
 "fecho":"Trocar de imóvel pode ser mais simples do que você imagina. E mais vantajoso.",
 "caption":'''Antes de comprar · 06

“Mas eu preciso vender o meu apartamento primeiro pra comprar o novo?”

Nem sempre. Na maioria dos lançamentos de alto padrão existe uma saída que pouca gente conhece: a permuta.

Na permuta, a construtora aceita o seu imóvel atual como parte do pagamento do novo. Você não precisa vender antes, nem ficar com dois financiamentos ao mesmo tempo, nem esperar o comprador certo aparecer.

Mas atenção: nem toda permuta é vantajosa. O que importa é o valor que dão pelo seu imóvel e as condições do novo.

Por isso eu sempre comparo a permuta com a venda direta antes de você decidir. Às vezes vale muito. Às vezes não vale.

Trocar de imóvel pode ser mais simples do que você imagina.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #Permuta #SaoPaulo'''},

{"slug":"chacara_sto_antonio","tipo":"bairro","nome":"Chác. Sto. Antônio","nome_wf":"Chacara Santo Antonio",
 "label":"Bairro mapeado · 09","databr":"Terca 28/07/2026","cron":"0 14 28 7 *",
 "sub":"O bairro-surpresa de quem busca espaço sem sair da Zona Sul.",
 "p1":("O diferencial","Metragens maiores pelo mesmo investimento de bairros vizinhos. Ruas tranquilas, fácil acesso à Marginal e ao aeroporto."),
 "p2":("Quem está descobrindo","Famílias que querem mais espaço sem pagar o prêmio da Vila Nova Conceição. Aqui o seu dinheiro rende mais metro quadrado."),
 "fecho":"Conversa antes de visitar. Esse é o bairro onde mais vejo gente se surpreender.",
 "caption":'''Bairro mapeado · 09

A Chácara Santo Antônio é o bairro-surpresa de quem busca espaço sem sair da Zona Sul.

É o tipo de endereço que ninguém coloca na lista no começo da busca — e que, quando visita, repensa tudo. Metragens maiores pelo mesmo investimento de bairros vizinhos, ruas tranquilas, acesso fácil à Marginal e ao aeroporto.

A procura vem mudando: famílias que querem mais espaço sem pagar o prêmio da Vila Nova Conceição estão descobrindo que aqui o dinheiro rende mais metro quadrado.

É onde mais vejo gente se surpreender numa visita.

Se você quer espaço sem abrir mão da localização, me chama antes de fechar com outro bairro.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#ChacaraSantoAntonio #AltoPadrao #SaoPaulo #MercadoImobiliario #Cyrela #ZonaSul'''},

{"slug":"dica_alem_apartamento","tipo":"dica","nome":"Dica · Alem do Apartamento","nome_wf":"Dica · Alem da Planta",
 "label":"Antes de comprar · 07","databr":"Quinta 30/07/2026","cron":"0 14 30 7 *",
 "perg":"O que olhar além da planta do apartamento?",
 "sub":"O apartamento é metade da compra. A outra metade é tudo em volta dele.",
 "p1":("O que muda o dia a dia","Número de vagas, depósito, infraestrutura de lazer, vizinhança da torre e a construtora por trás. É o que você vive todo dia — não só a planta."),
 "p2":("O que protege o valor","Reputação da incorporadora, qualidade da entrega e o entorno do empreendimento. Isso define quanto o seu imóvel vai valer daqui a cinco anos."),
 "fecho":"A planta vende o apartamento. O entorno é que segura o seu patrimônio.",
 "caption":'''Antes de comprar · 07

A maioria das pessoas se apaixona pela planta. E é aí que mora o erro mais caro.

O apartamento é metade da compra. A outra metade é tudo em volta dele — e é essa metade que define a sua vida e o seu patrimônio.

No dia a dia, o que pesa: número de vagas, depósito, a infraestrutura de lazer que você realmente vai usar, a vizinhança da torre e a construtora por trás da obra.

No longo prazo, o que protege o valor: a reputação da incorporadora, a qualidade da entrega e o entorno do empreendimento. É isso que diz quanto seu imóvel vai valer daqui a cinco anos.

A planta vende o apartamento. O resto é que segura o seu investimento.

É por isso que eu acompanho cada empreendimento de perto — pra te contar o que a maquete não mostra.

— Juliska Tordino
Corretora · Cyrela · CRECI 133.239-F

#MercadoImobiliario #AltoPadrao #DicasImobiliarias #ComprarImovel #SaoPaulo'''},
]

os.makedirs(".github/workflows",exist_ok=True)
print(f"Gerando {len(POSTS)} posts...")
for p in POSTS: build(p)
print("PRONTO ·", len(POSTS), "posts")
